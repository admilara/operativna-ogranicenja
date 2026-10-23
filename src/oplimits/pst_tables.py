"""Optional, more accurate PST model: per-position tap tables.

For PSTs with diagonal regulation one tap position fixes the winding-1 voltage, the angle
and the impedance together. When a table is supplied for a transformer, the selected
position overrides the angle-only model from build.py.

CSV format (config/pst_tap_tables.csv):

    transformer,step,u_w1_kv,angle_deg,z_factor
    T1 400 KONJS,-12,...,...,...

transformer = transformer name as in the .raw file; u_w1_kv = winding-1 voltage in the
position; z_factor = impedance factor relative to the nominal (.raw) impedance.
Theory: docs/teorija/02-pst-korekcija-impedancije.md, section 2.8
"""
import pandas as pd

from .build import trafo3w_pair_percent
from .errors import ModelError

COLUMNS = ["transformer", "step", "u_w1_kv", "angle_deg", "z_factor"]


def load_tap_tables(path):
    df = pd.read_csv(path, comment="#")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ModelError("U %s nedostaju stupci: %s" % (path, ", ".join(missing)))
    df["transformer"] = df["transformer"].astype(str).str.strip()
    return {name: g.set_index("step").sort_index() for name, g in df.groupby("transformer")}


def apply_tap_positions(net, tables, positions, findings):
    """positions: {transformer name: step}. Returns names that were applied."""
    applied = []
    for name, step in positions.items():
        if name not in tables:
            raise ModelError("Za transformator '%s' nema tablice po položajima." % name)
        tab = tables[name]
        if step not in tab.index:
            raise ModelError("'%s': položaj %s nije u tablici (%s … %s)."
                             % (name, step, tab.index.min(), tab.index.max()))
        row = tab.loc[step]
        hit2 = net.trafo.index[net.trafo.name == name]
        hit3 = net.trafo3w.index[net.trafo3w.name == name]
        if len(hit2) + len(hit3) != 1:
            raise ModelError("Transformator '%s' nije jednoznačno pronađen u mreži." % name)
        if len(hit3):
            i = hit3[0]
            t3 = net.trafo3w
            z = {p: complex(t3.at[i, p + "_re"], t3.at[i, p + "_im"]) for p in ("z12", "z23", "z31")}
            pc = trafo3w_pair_percent(z["z12"], z["z23"], z["z31"], float(row.z_factor),
                                      t3.at[i, "sn_hv_mva"], t3.at[i, "sn_mv_mva"], t3.at[i, "sn_lv_mva"],
                                      net.sn_mva)
            for p in ("hv", "mv", "lv"):
                t3.at[i, "vk_%s_percent" % p], t3.at[i, "vkr_%s_percent" % p] = pc[p]
            t3.at[i, "vn_hv_kv"] = float(row.u_w1_kv)
            t3.at[i, "shift_mv_degree"] = t3.at[i, "shift_lv_degree"] = float(row.angle_deg)
            el = "trafo3w"
        else:
            i = hit2[0]
            tr = net.trafo
            tr.at[i, "vk_percent"] = max(tr.at[i, "psse_vk_nom"] * float(row.z_factor), 1e-4)
            tr.at[i, "vkr_percent"] = tr.at[i, "psse_vkr_nom"] * float(row.z_factor)
            w1_hv = bool(tr.at[i, "psse_w1_is_hv"])
            tr.at[i, "vn_hv_kv" if w1_hv else "vn_lv_kv"] = float(row.u_w1_kv)
            tr.at[i, "shift_degree"] = float(row.angle_deg) if w1_hv else -float(row.angle_deg)
            el = "trafo"
        net[el].at[i, "pst_model"] = "tablica po položajima"
        net[el].at[i, "pst_step"] = step
        net[el].at[i, "psse_ang1"] = float(row.angle_deg)
        findings.info("PST", "modeliran tablicom po položajima, položaj %s (%.3f kV, %.2f°, F=%.4f)"
                      % (step, row.u_w1_kv, row.angle_deg, row.z_factor), name)
        applied.append(name)
    # the angle-only warning stays for PSTs without a table
    findings.rows = [r for r in findings.rows
                     if not (r["kategorija"] == "PST" and r["element"] in applied and r["razina"] == "UPOZORENJE")]
    return applied
