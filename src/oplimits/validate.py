"""Check the pandapower model against the solution stored in the .raw file, and derive
boundary (X-node) injections from it.
Theory: docs/teorija/01-mrezni-model.md, sections 1.5 and 1.6
"""
import copy

import numpy as np
import pandas as pd
import pandapower as pp
import scipy.sparse as sp
from pandapower.pypower.makeYbus import makeYbus
from scipy.sparse.linalg import spsolve

from .errors import ModelError


def _full_ybus(net):
    """Ybus of the whole network at ppc level (incl. 3W star buses), without solving."""
    net2 = copy.deepcopy(net)
    net2.ext_grid.drop(net2.ext_grid.index, inplace=True)
    net2.gen["in_service"] = False      # avoids setpoint conflicts; Ybus does not depend on gens
    pp.create_ext_grid(net2, net2.bus.index[net2.bus.in_service][0])
    pp.runpp(net2, tolerance_mva=1e12, init="flat", calculate_voltage_angles=True, numba=False)
    ppc = net2._ppc
    Y, _, _ = makeYbus(ppc["baseMVA"], ppc["bus"], ppc["branch"])
    lookup = net2._pd2ppc_lookups["bus"]
    aux3w = net2._pd2ppc_lookups.get("aux", {}).get("trafo3w")
    return sp.csr_matrix(Y), lookup, aux3w


def stored_state_mismatch(net, raw, dropped):
    """Power mismatch at every in-service bus with the stored PSS/E voltages.

    Returns (DataFrame indexed by bus, list of X-node buses). At X-nodes the mismatch is the
    exchange over the dropped part of the tie line."""
    Y, lookup, aux3w = _full_ybus(net)
    buses = [b for b in net.bus.index if net.bus.at[b, "in_service"]]
    n = Y.shape[0]
    V = np.ones(n, dtype=complex)
    for b in buses:
        V[lookup[b]] = net.bus.at[b, "psse_vm"] * np.exp(1j * np.deg2rad(net.bus.at[b, "psse_va"]))

    # 3W star points: not VMSTAR/ANSTAR (pandapower puts the phase shift on the other side
    # of the star point than PSS/E) but zero injection: V_s = -Yss^-1 Ysk V_k
    if aux3w is not None and len(aux3w):
        s_all = np.array([lookup[a] for a in aux3w])
        on = (net.trafo3w.in_service.values
              & net.bus.loc[net.trafo3w.hv_bus, "in_service"].values
              & net.bus.loc[net.trafo3w.mv_bus, "in_service"].values
              & net.bus.loc[net.trafo3w.lv_bus, "in_service"].values)
        s_idx = s_all[on]
        V[s_all[~on]] = 0.0
        k_idx = np.setdiff1d(np.arange(n), s_idx)
        V[s_idx] = spsolve(Y[s_idx][:, s_idx].tocsc(), -(Y[s_idx][:, k_idx] @ V[k_idx]))

    s_net = V * np.conj(Y @ V) * net.sn_mva
    spec = {b: 0j for b in buses}
    for tab in ("gen", "sgen"):
        df = net[tab]
        for _, g in df[df.in_service].iterrows():
            spec[g.bus] += complex(g.p_mw, g.get("psse_qg", 0.0) or 0.0)
    for _, ld in net.load[net.load.in_service].iterrows():
        spec[ld.bus] -= complex(ld.p_mw, ld.q_mvar)

    x_nodes = sorted({br["i"] if br["i"] in raw["bus"] else br["j"] for br in dropped})
    rows = []
    for b in buses:
        sc, ss = s_net[lookup[b]], spec[b]
        rows.append(dict(sabirnica=b, ime=net.bus.at[b, "name"], vn_kv=net.bus.at[b, "vn_kv"],
                         x_cvoriste=b in x_nodes, P_mreza=sc.real, Q_mreza=sc.imag,
                         P_zadano=ss.real, Q_zadano=ss.imag, dP=sc.real - ss.real, dQ=sc.imag - ss.imag))
    out = pd.DataFrame(rows).set_index("sabirnica")
    if out[["dP", "dQ"]].isna().any().any():
        raise ModelError("Neusklađenost sadrži NaN na sabirnicama: %s"
                         % out.index[out.dP.isna()].tolist()[:10])
    return out, x_nodes


def add_boundary_injections(net, mismatch, x_nodes):
    """Fixed PQ at each X-node = exchange over the dropped tie-line half
    (load > 0 means export from the modelled system)."""
    for b in x_nodes:
        if not net.bus.at[b, "in_service"]:
            continue
        idx = pp.create_load(net, b, p_mw=-mismatch.at[b, "dP"], q_mvar=-mismatch.at[b, "dQ"],
                             name="granica_%d" % b)
        net.load.at[idx, "boundary"] = True
    net.load["boundary"] = net.load["boundary"].eq(True)


def boundary_table(net):
    ld = net.load[net.load.boundary]
    return pd.DataFrame({"sabirnica": ld.bus.values, "ime": net.bus.loc[ld.bus, "name"].values,
                         "vn_kv": net.bus.loc[ld.bus, "vn_kv"].values,
                         "P_izvoz_MW": ld.p_mw.values, "Q_izvoz_Mvar": ld.q_mvar.values})


def compare_voltages(net):
    rb = net.res_bus[net.bus.in_service]
    return pd.DataFrame({
        "ime": net.bus.loc[rb.index, "name"], "vn_kv": net.bus.loc[rb.index, "vn_kv"],
        "vm_psse": net.bus.loc[rb.index, "psse_vm"], "vm_pp": rb.vm_pu,
        "dVM": rb.vm_pu - net.bus.loc[rb.index, "psse_vm"],
        "va_psse": net.bus.loc[rb.index, "psse_va"], "va_pp": rb.va_degree,
        "dVA": rb.va_degree - net.bus.loc[rb.index, "psse_va"]})
