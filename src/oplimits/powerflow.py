"""Power flow with PSS/E-style reactive limits (VARLIM) and slack placement.

pandapower's enforce_q_lims does not converge on these networks, so Q limits are
enforced in an outer loop. Theory: docs/teorija/01-mrezni-model.md, section 1.3
"""
import pandapower as pp

from .errors import ModelError

PF_OPTIONS = dict(calculate_voltage_angles=True, max_iteration=60, numba=False)


def reset_qlim(net):
    """Undo PV->PQ switches from a previous run_pf_varlim call."""
    if "qlim_of" not in net.sgen:
        net.sgen["qlim_of"] = float("nan")
        return
    switched = net.sgen.index[net.sgen.qlim_of.notna()]
    for k in switched:
        net.gen.at[int(net.sgen.at[k, "qlim_of"]), "in_service"] = True
    net.sgen.drop(switched, inplace=True)


def run_pf_varlim(net, max_outer=40, init="dc", verbose=False):
    """Newton-Raphson + outer loop: a regulator beyond a Q limit becomes PQ at the limit;
    it returns to PV when its bus voltage crosses the setpoint the 'wrong' way.
    Returns the number of outer iterations."""
    reset_qlim(net)
    pp.runpp(net, init=init, **PF_OPTIONS)
    gen = net.gen
    for it in range(max_outer):
        changes = 0
        q = net.res_gen.q_mvar
        act = gen.in_service
        hi = act & (q > gen.max_q_mvar + 1e-4)
        lo = act & (q < gen.min_q_mvar - 1e-4)
        for g in gen.index[hi | lo]:
            qlim = gen.at[g, "max_q_mvar"] if hi[g] else gen.at[g, "min_q_mvar"]
            gen.at[g, "in_service"] = False
            k = pp.create_sgen(net, gen.at[g, "bus"], p_mw=gen.at[g, "p_mw"], q_mvar=qlim,
                               name="Qlim_" + str(gen.at[g, "name"]))
            net.sgen.at[k, "qlim_of"] = g
            net.sgen.at[k, "unit"] = False
            changes += 1
        for k in net.sgen.index[net.sgen.qlim_of.notna() & net.sgen.in_service]:
            g = int(net.sgen.at[k, "qlim_of"])
            b = gen.at[g, "bus"]
            v, vs, qk = net.res_bus.at[b, "vm_pu"], gen.at[g, "vm_pu"], net.sgen.at[k, "q_mvar"]
            if (qk >= gen.at[g, "max_q_mvar"] - 1e-6 and v > vs + 1e-5) or \
               (qk <= gen.at[g, "min_q_mvar"] + 1e-6 and v < vs - 1e-5):
                net.sgen.drop(k, inplace=True)
                gen.at[g, "in_service"] = True
                changes += 1
        if verbose:
            print("   VARLIM korak %d: promjena %d" % (it, changes))
        if changes == 0:
            return it
        pp.runpp(net, init="results", **PF_OPTIONS)
    raise ModelError("VARLIM petlja nije se smirila u %d koraka" % max_outer)


def set_slack(net, bus):
    """ext_grid at `bus` with the stored PSS/E voltage and angle; the bus regulator is
    switched off; units keep their P, so ext_grid takes only losses and imbalance.
    Returns the P of in-service units at that bus."""
    if bus not in net.bus.index or not net.bus.at[bus, "in_service"]:
        raise ModelError("Referentna sabirnica %s ne postoji ili nije u pogonu." % bus)
    net.ext_grid.drop(net.ext_grid.index, inplace=True)
    regs = net.gen.index[(net.gen.bus == bus) & net.gen.in_service]
    net.gen.loc[regs, "in_service"] = False
    net.gen.loc[regs, "replaced_by_slack"] = True
    pp.create_ext_grid(net, bus, vm_pu=net.bus.at[bus, "psse_vm"], va_degree=net.bus.at[bus, "psse_va"],
                       name="slack_%d" % bus)
    units = net.sgen[(net.sgen.bus == bus) & net.sgen.in_service & net.sgen.unit]
    return float(units.p_mw.sum())
