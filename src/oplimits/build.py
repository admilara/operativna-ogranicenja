"""Build a pandapower network from records read by psse_raw.read_raw.

The goal is a 1:1 reproduction of the PSS/E model; every convention here was checked
against the stored PSS/E solution (see validate.py).
Theory: docs/teorija/01-mrezni-model.md, docs/teorija/02-pst-korekcija-impedancije.md
"""
import math

import pandapower as pp

from .errors import ModelError
from .findings import Findings
from .psse_raw import impedance_factor

PST_DIAGONAL_WARNING = (
    "PST modeliran SAMO KUTNO (kut + tablica korekcije impedancije, omjer iz modela). "
    "Stvarni PST može imati dijagonalnu regulaciju (kut i napon iz istog položaja preklopke) - "
    "model nije točan i treba ga revidirati s tablicama po položajima (v. teorija, pogl. 2)."
)


# ----------------------------------------------------------------------------------------
# impedance helpers
# ----------------------------------------------------------------------------------------
def _r_z_on_pair_base(cz, r, x, s_pair, sbase):
    """Return (R, |Z|) in p.u. on the pair's own MVA base, from PSS/E CZ coding."""
    if cz == 1:      # p.u. on system base
        rr, xx = r * s_pair / sbase, x * s_pair / sbase
        return rr, math.hypot(rr, xx)
    if cz == 2:      # p.u. on winding-pair base
        return r, math.hypot(r, x)
    if cz == 3:      # R = load loss in W, X = |Z| in p.u. on pair base
        return r / (s_pair * 1e6), x
    raise ModelError("Nepoznat CZ=%s" % cz)


def _z_system(cz, r, x, s_pair, sbase):
    """Complex pair impedance in p.u. on the system base."""
    rr, zz = _r_z_on_pair_base(cz, r, x, s_pair, sbase)
    return complex(rr, math.sqrt(max(zz * zz - rr * rr, 0.0))) * sbase / s_pair


def trafo3w_pair_percent(z12, z23, z31, factor, sn_hv, sn_mv, sn_lv, sbase):
    """pandapower vk/vkr [%] for the three pairs.

    The impedance correction factor applies to winding 1 of the PSS/E star:
    Z1 = (Z12 + Z31 - Z23)/2, Z12' = Z12 + (F-1) Z1, Z31' = Z31 + (F-1) Z1, Z23' = Z23.
    pandapower references each pair's vk to the smaller rated power of the two windings.
    """
    z1 = (z12 + z31 - z23) / 2.0
    pairs = {
        "hv": (z12 + (factor - 1.0) * z1, min(sn_hv, sn_mv)),
        "mv": (z23, min(sn_mv, sn_lv)),
        "lv": (z31 + (factor - 1.0) * z1, min(sn_hv, sn_lv)),
    }
    return {p: (100.0 * abs(z) * sref / sbase, 100.0 * z.real * sref / sbase)
            for p, (z, sref) in pairs.items()}


# ----------------------------------------------------------------------------------------
# network
# ----------------------------------------------------------------------------------------
def build_network(raw, f_hz=50.0):
    """Return (net, findings, dropped_branches).

    dropped_branches: branch records with an end bus missing from the file (tie lines
    cut at the model boundary); validate.py turns them into boundary injections.
    """
    sb = raw["sbase"]
    bus = raw["bus"]
    fnd = Findings()
    net = pp.create_empty_network(name="PSS/E: %s" % raw.get("path", ""), f_hz=f_hz, sn_mva=sb)
    net["ztab"] = {str(k): v for k, v in raw["ztab"].items()}   # kept for set_pst_angle

    for b, r in bus.items():
        pp.create_bus(net, vn_kv=r["baskv"], name=r["name"].strip(), index=b,
                      in_service=(r["ide"] != 4), zone=str(r["zone"]))
    net.bus["psse_area"] = [bus[b]["area"] for b in net.bus.index]
    net.bus["psse_ide"] = [bus[b]["ide"] for b in net.bus.index]
    net.bus["psse_vm"] = [bus[b]["vm"] for b in net.bus.index]
    net.bus["psse_va"] = [bus[b]["va"] for b in net.bus.index]
    if not any(r["ide"] == 3 for r in bus.values()):
        fnd.warn("model", "u .raw-u nema sabirnice tipa 3 (swing) - referentni čvor zadaje korisnik")

    _add_loads(net, raw, fnd)
    _add_generators(net, raw, fnd)
    dropped = _add_lines(net, raw, fnd, f_hz)
    _add_transformers(net, raw, fnd)
    _add_shunts(net, raw)
    return net, fnd, dropped


def _add_loads(net, raw, fnd):
    for ld in raw["load"]:
        if abs(ld["ip"]) + abs(ld["iq"]) + abs(ld["yp"]) + abs(ld["yq"]) > 0:
            fnd.info("teret", "ima I/Y komponentu - modelirano kao stalna snaga",
                     "%d '%s'" % (ld["bus"], ld["id"]))
        pp.create_load(net, ld["bus"], p_mw=ld["pl"], q_mvar=ld["ql"],
                       name="%d_%s" % (ld["bus"], ld["id"]), in_service=bool(ld["stat"]))
    net.load["boundary"] = False


def _add_generators(net, raw, fnd):
    """Each unit -> sgen (own P and owner fields); each PV bus -> one gen 'Vreg_<bus>'."""
    bus = raw["bus"]
    by_bus = {}
    for g in raw["gen"]:
        by_bus.setdefault(g["bus"], []).append(g)

    for b, units in by_bus.items():
        if b not in bus:
            fnd.warn("generator", "sabirnica ne postoji", b)
            continue
        active = [g for g in units if g["stat"] == 1]
        # remote regulation of a bus that already has local regulation -> PQ at stored QG
        remote = [g for g in active if g["ireg"] not in (0, b)
                  and bus.get(g["ireg"], {}).get("ide") == 2
                  and any(x["stat"] == 1 for x in by_bus.get(g["ireg"], []))]
        for g in remote:
            fnd.info("generator", "regulira sabirnicu %d koja ima vlastitu regulaciju -> PQ na QG=%.2f Mvar"
                     % (g["ireg"], g["qg"]), "%d '%s'" % (b, g["id"]))
        regulating = [g for g in active if g not in remote]
        q_range = sum(g["qt"] - g["qb"] for g in regulating)
        is_pv = bus[b]["ide"] == 2 and bool(regulating) and q_range > 1e-6
        setpoints = {round(g["vs"], 5) for g in regulating if g["qt"] - g["qb"] > 1e-6}
        if is_pv and len(setpoints) > 1:
            fnd.warn("generator", "različite zadane vrijednosti napona %s - uzeta prva" % sorted(setpoints), b)

        for g in units:
            unit = "%d '%s'" % (b, g["id"])
            if g["ireg"] not in (0, b) and g not in remote and g["stat"] == 1:
                fnd.info("generator", "regulira udaljenu sabirnicu %d - modelirano kao lokalna regulacija"
                         % g["ireg"], unit)
            if g["nfields"] < 29:
                fnd.info("generator", "skraćeni zapis (%d polja) - vlasnici/WMOD nepotpuni" % g["nfields"], unit)
            if g["qt"] < g["qb"]:
                fnd.warn("generator", "QT < QB (%.1f < %.1f)" % (g["qt"], g["qb"]), unit)
            on = g["stat"] == 1 and bus[b]["ide"] != 4
            on_reg = is_pv and g in regulating
            idx = pp.create_sgen(net, b, p_mw=g["pg"], q_mvar=0.0 if on_reg else g["qg"],
                                 sn_mva=g["mbase"], max_p_mw=g["pt"], min_p_mw=g["pb"],
                                 name="%d_%s" % (b, g["id"]), in_service=on)
            for col, val in (("psse_id", g["id"]), ("psse_o1", g["o1"]), ("psse_o2", g["o2"]),
                             ("psse_o3", g["o3"]), ("psse_o4", g["o4"]), ("psse_stat", g["stat"]),
                             ("psse_qg", g["qg"] if on else 0.0), ("psse_qt", g["qt"]),
                             ("psse_qb", g["qb"]), ("unit", True), ("on_pv_bus", bool(on_reg))):
                net.sgen.loc[idx, col] = val

        if is_pv:
            first = [g for g in regulating if g["qt"] - g["qb"] > 1e-6][0]
            idx = pp.create_gen(net, b, p_mw=0.0, vm_pu=first["vs"],
                                min_q_mvar=sum(g["qb"] for g in regulating),
                                max_q_mvar=sum(g["qt"] for g in regulating),
                                name="Vreg_%d" % b, in_service=bus[b]["ide"] != 4)
            net.gen.loc[idx, "psse_qg_sum"] = sum(g["qg"] for g in regulating)
            net.gen.loc[idx, "psse_qg"] = 0.0
    net.sgen["unit"] = net.sgen["unit"].eq(True)


def _add_lines(net, raw, fnd, f_hz):
    sb, bus = raw["sbase"], raw["bus"]
    dropped = []
    for br in raw["branch"]:
        i, j = br["i"], br["j"]
        tag = "%d-%d '%s'" % (i, j, br["ckt"])
        if i not in bus or j not in bus:
            dropped.append(br)
            fnd.info("granica", "vod ide na sabirnicu izvan .raw-a - izostavljen", tag)
            continue
        vi, vj = bus[i]["baskv"], bus[j]["baskv"]
        if abs(vi - vj) > 1e-3:
            fnd.warn("vod", "spaja različite bazne napone %.0f/%.0f kV" % (vi, vj), tag)
        if abs(br["gi"]) + abs(br["bi"]) + abs(br["gj"]) + abs(br["bj"]) > 0:
            fnd.warn("vod", "ima poprečne admitancije na krajevima - nisu modelirane", tag)
        zb = vi ** 2 / sb
        rate = br["rate1"] if br["rate1"] > 0 else 9999.0
        idx = pp.create_line_from_parameters(
            net, i, j, length_km=1.0, r_ohm_per_km=br["r"] * zb, x_ohm_per_km=max(br["x"] * zb, 1e-6),
            c_nf_per_km=br["b"] / zb / (2 * math.pi * f_hz) * 1e9,
            max_i_ka=rate / (math.sqrt(3) * vi), name="%d-%d_%s" % (i, j, br["ckt"]),
            in_service=bool(br["stat"]))
        for col, val in (("psse_ckt", br["ckt"]), ("rate1_mva", br["rate1"]),
                         ("rate2_mva", br["rate2"]), ("rate3_mva", br["rate3"]),
                         ("psse_len_km", br["length"])):
            net.line.loc[idx, col] = val
    return dropped


def _winding_kv(raw, t, w, b):
    wv = t[w]["windv"]
    if t["cw"] == 2:
        return wv
    nomv = t[w]["nomv"] if t[w]["nomv"] > 0 else raw["bus"][b]["baskv"]
    return wv * nomv      # CW=1: p.u. of the winding nominal (or bus base) voltage


def _pst_checks(t, fnd):
    w1 = t["w1"]
    if abs(w1.get("cod", 0)) != 3 and not w1.get("tab"):
        return False
    tag = t["name"] or "%d-%d" % (t["i"], t["j"])
    fnd.warn("PST", PST_DIAGONAL_WARNING, tag)
    if abs(w1.get("rma", 0)) > 90 or abs(w1.get("rmi", 0)) > 90:
        fnd.info("PST", "RMA/RMI = %.3f / %.3f (kV), VMA/VMI = %.3f / %.3f: polja kodirana za naponsku "
                 "regulaciju (dijagonalna regulacija); kut se ne ograničava iz zapisa nego iz Tablice 3 smjernica"
                 % (w1["rma"], w1["rmi"], w1["vma"], w1["vmi"]), tag)
    return True


def _add_transformers(net, raw, fnd):
    sb, bus = raw["sbase"], raw["bus"]
    for t in raw["trafo"]:
        if t["cw"] == 3:
            raise ModelError("Transformator %d-%d: CW=3 još nije podržan." % (t["i"], t["j"]))
        on = bool(t["stat"])
        is_pst = _pst_checks(t, fnd)
        if t["k"] == 0:
            _add_trafo2w(net, raw, t, on, is_pst, fnd)
        else:
            _add_trafo3w(net, raw, t, on, is_pst, fnd)


def _add_trafo2w(net, raw, t, on, is_pst, fnd):
    sb, bus = raw["sbase"], raw["bus"]
    i, j, w1 = t["i"], t["j"], t["w1"]
    angle = w1["ang"]
    factor = impedance_factor(raw["ztab"].get(w1["tab"]), angle) if w1["tab"] else 1.0
    rr, zz = _r_z_on_pair_base(t["cz"], t["r12"], t["x12"], t["sb12"], sb)
    v1, v2 = _winding_kv(raw, t, "w1", i), _winding_kv(raw, t, "w2", j)
    if t["cm"] == 1:
        pfe_kw = t["mag1"] * sb * 1e3
        i0 = 100.0 * math.hypot(t["mag1"], t["mag2"]) * sb / t["sb12"]
    else:
        pfe_kw = t["mag1"] / 1e3
        i0 = 100.0 * t["mag2"]
    w1_is_hv = bus[i]["baskv"] >= bus[j]["baskv"]
    hv, lv, vhv, vlv, shift = (i, j, v1, v2, angle) if w1_is_hv else (j, i, v2, v1, -angle)
    idx = pp.create_transformer_from_parameters(
        net, hv, lv, sn_mva=t["sb12"], vn_hv_kv=vhv, vn_lv_kv=vlv,
        vk_percent=max(100.0 * zz * factor, 1e-4), vkr_percent=100.0 * rr * factor,
        pfe_kw=pfe_kw, i0_percent=max(i0, pfe_kw / (t["sb12"] * 10.0)), shift_degree=shift,
        name=t["name"] or "%d-%d_%s" % (i, j, t["ckt"]), in_service=on)
    for col, val in (("psse_i", i), ("psse_j", j), ("psse_ckt", t["ckt"]),
                     ("rate1_mva", w1["rate1"]), ("psse_cod1", w1["cod"]), ("psse_cont1", w1["cont"]),
                     ("psse_tab1", w1["tab"]), ("psse_ang1", angle), ("psse_zfactor", factor),
                     ("psse_rma1", w1["rma"]), ("psse_rmi1", w1["rmi"]),
                     ("psse_vk_nom", 100.0 * zz), ("psse_vkr_nom", 100.0 * rr),
                     ("psse_w1_is_hv", w1_is_hv), ("pst", is_pst), ("pst_model", "kutni" if is_pst else "")):
        net.trafo.loc[idx, col] = val


def _add_trafo3w(net, raw, t, on, is_pst, fnd):
    sb = raw["sbase"]
    i, j, k = t["i"], t["j"], t["k"]
    for w in ("w2", "w3"):
        if t[w]["tab"]:
            fnd.warn("trafo3w", "tablica korekcije na namotu %s - zanemarena" % w[1], t["name"])
    factor = impedance_factor(raw["ztab"].get(t["w1"]["tab"]), t["w1"]["ang"]) if t["w1"]["tab"] else 1.0
    z12 = _z_system(t["cz"], t["r12"], t["x12"], t["sb12"], sb)
    z23 = _z_system(t["cz"], t["r23"], t["x23"], t["sb23"], sb)
    z31 = _z_system(t["cz"], t["r31"], t["x31"], t["sb31"], sb)
    sn_hv = sn_mv = t["sb12"]
    sn_lv = t["sb23"]
    pc = trafo3w_pair_percent(z12, z23, z31, factor, sn_hv, sn_mv, sn_lv, sb)
    if t["mag1"] or t["mag2"]:
        fnd.warn("trafo3w", "MAG1/MAG2 != 0 - nije modelirano", t["name"])
    idx = pp.create_transformer3w_from_parameters(
        net, i, j, k,
        vn_hv_kv=_winding_kv(raw, t, "w1", i), vn_mv_kv=_winding_kv(raw, t, "w2", j),
        vn_lv_kv=_winding_kv(raw, t, "w3", k),
        sn_hv_mva=sn_hv, sn_mv_mva=sn_mv, sn_lv_mva=sn_lv,
        vk_hv_percent=pc["hv"][0], vk_mv_percent=pc["mv"][0], vk_lv_percent=pc["lv"][0],
        vkr_hv_percent=pc["hv"][1], vkr_mv_percent=pc["mv"][1], vkr_lv_percent=pc["lv"][1],
        pfe_kw=0.0, i0_percent=0.0,
        # +ANG1 verified against the stored PSS/E solution; -ANG1 gives GW-level mismatch
        shift_mv_degree=t["w1"]["ang"] - t["w2"]["ang"],
        shift_lv_degree=t["w1"]["ang"] - t["w3"]["ang"],
        name=t["name"], in_service=on)
    for col, val in (("psse_ckt", t["ckt"]), ("rate1_hv_mva", t["w1"]["rate1"]),
                     ("rate1_mv_mva", t["w2"]["rate1"]), ("rate1_lv_mva", t["w3"]["rate1"]),
                     ("psse_sb12", t["sb12"]), ("psse_cod1", t["w1"]["cod"]), ("psse_cont1", t["w1"]["cont"]),
                     ("psse_tab1", t["w1"]["tab"]), ("psse_ang1", t["w1"]["ang"]), ("psse_zfactor", factor),
                     ("psse_rma1", t["w1"]["rma"]), ("psse_rmi1", t["w1"]["rmi"]),
                     ("psse_vmstar", t["vmstar"]), ("psse_anstar", t["anstar"]),
                     ("z12_re", z12.real), ("z12_im", z12.imag), ("z23_re", z23.real),
                     ("z23_im", z23.imag), ("z31_re", z31.real), ("z31_im", z31.imag),
                     ("pst", is_pst), ("pst_model", "kutni" if is_pst else "")):
        net.trafo3w.loc[idx, col] = val


def _add_shunts(net, raw):
    for s in raw["fxshunt"]:
        pp.create_shunt(net, s["bus"], q_mvar=-s["bl"], p_mw=s["gl"],
                        name="fx_%d_%s" % (s["bus"], s["id"]), in_service=bool(s["stat"]))
    for s in raw["swshunt"]:
        pp.create_shunt(net, s["bus"], q_mvar=-s["binit"], p_mw=0.0,
                        name="sw_%d_%s" % (s["bus"], s["id"]), in_service=bool(s["stat"]))


# ----------------------------------------------------------------------------------------
# PST angle (angle-only model)
# ----------------------------------------------------------------------------------------
def set_pst_angle(net, element, idx, angle_deg):
    """Set a PST angle and recompute its impedance from the correction table.

    Angle-only model: the winding ratio is left unchanged (see PST_DIAGONAL_WARNING).
    element: "trafo" or "trafo3w".
    """
    tab = net["ztab"].get(str(int(net[element].at[idx, "psse_tab1"])))
    factor = impedance_factor(tab, angle_deg) if tab else 1.0
    if element == "trafo":
        tr = net.trafo
        tr.at[idx, "vk_percent"] = max(tr.at[idx, "psse_vk_nom"] * factor, 1e-4)
        tr.at[idx, "vkr_percent"] = tr.at[idx, "psse_vkr_nom"] * factor
        tr.at[idx, "shift_degree"] = angle_deg if tr.at[idx, "psse_w1_is_hv"] else -angle_deg
    elif element == "trafo3w":
        t3 = net.trafo3w
        z = {p: complex(t3.at[idx, p + "_re"], t3.at[idx, p + "_im"]) for p in ("z12", "z23", "z31")}
        pc = trafo3w_pair_percent(z["z12"], z["z23"], z["z31"], factor, t3.at[idx, "sn_hv_mva"],
                                  t3.at[idx, "sn_mv_mva"], t3.at[idx, "sn_lv_mva"], net.sn_mva)
        for p in ("hv", "mv", "lv"):
            t3.at[idx, "vk_%s_percent" % p], t3.at[idx, "vkr_%s_percent" % p] = pc[p]
        t3.at[idx, "shift_mv_degree"] = angle_deg
        t3.at[idx, "shift_lv_degree"] = angle_deg
    else:
        raise ValueError(element)
    net[element].at[idx, "psse_ang1"] = angle_deg
    net[element].at[idx, "psse_zfactor"] = factor
