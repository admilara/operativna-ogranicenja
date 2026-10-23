"""Verbatim report of everything a PSS/E v35 .raw file contains for each PST.

Values are copied as strings exactly as written in the file (no conversion, no rounding);
field names come from the file's own '@!' header lines. Output: Markdown (theory book) and
a dict of DataFrames (Excel).
"""
import csv
import io
import re

import pandas as pd

from .errors import ModelError


def _rec(line):
    return [x.strip() for x in next(csv.reader(io.StringIO(line), quotechar="'", skipinitialspace=True))]


def _section(lines, name):
    start = next((i for i, l in enumerate(lines) if "BEGIN %s DATA" % name in l), None)
    if start is None:
        raise ModelError("Sekcija %s nije pronađena." % name)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip().startswith("0 /") or lines[i].strip() == "Q")
    headers = [_rec(l.lstrip()[2:]) for l in lines[start + 1:end] if l.lstrip().startswith("@!")]
    body = [l for l in lines[start + 1:end] if not l.lstrip().startswith("@!") and l.strip()]
    return headers, body


def _is_pst(rec):
    windings = rec["windings"]
    for w in windings:
        if abs(int(float(w.get("COD", "0") or 0))) == 3:
            return True
        if int(float(w.get("TAB", "0") or 0)) != 0:
            return True
        if abs(float(w.get("ANG", "0") or 0)) > 0:
            return True
    return False


def read_pst_records(path):
    with open(path, encoding="latin-1") as fh:
        lines = fh.read().splitlines()
    hdr, body = _section(lines, "TRANSFORMER")
    if len(hdr) < 5:
        raise ModelError("Zaglavlje sekcije transformatora nema 5 redaka '@!'.")
    h1, h2, hw1, hw2, hw3 = ([x.strip() for x in h] for h in hdr[:5])
    recs, k = [], 0
    while k < len(body):
        r1 = _rec(body[k])
        three = int(r1[2]) != 0
        n = 5 if three else 4
        rows = [_rec(x) for x in body[k:k + n]]
        k += n
        line1 = dict(zip(h1, r1 + [None] * (len(h1) - len(r1))))
        line2 = dict(zip(h2, rows[1] + [None] * (len(h2) - len(rows[1]))))
        if three:
            line2_used = h2
        else:
            line2_used = h2[:3]
        wh = [hw1, hw2, hw3] if three else [hw1, hw2[:2]]
        windings = []
        for wi, (h, r) in enumerate(zip(wh, rows[2:])):
            vals = dict(zip(h, r + [None] * (len(h) - len(r))))
            # generic keys without the winding number, e.g. 'WINDV1' -> 'WINDV'
            generic = {re.sub(r"^RATE%d-" % (wi + 1), "RATE-", key) if key.startswith("RATE")
                       else re.sub(r"%d$" % (wi + 1), "", key): val for key, val in vals.items()}
            windings.append(dict(raw=vals, header=h, generic=generic, nfields=len(r)))
        recs.append(dict(line1=line1, line1_header=h1, line1_nfields=len(r1),
                         line2=line2, line2_header=line2_used, line2_nfields=len(rows[1]),
                         windings=[w["generic"] for w in windings], windings_full=windings,
                         three=three))
    psts = [r for r in recs if _is_pst(r)]

    zhdr, zbody = _section(lines, "IMPEDANCE CORRECTION")
    buf = []
    for l in zbody:
        buf.extend(l.replace(",", " ").split())
    tables, pos = {}, 0
    while pos < len(buf):
        tid = buf[pos]
        pos += 1
        pts = []
        while pos + 2 < len(buf) + 1:
            t, re_f, im_f = buf[pos], buf[pos + 1], buf[pos + 2]
            pos += 3
            if float(t) == 0.0 and float(re_f) == 0.0 and float(im_f) == 0.0:
                break
            pts.append((t, re_f, im_f))
        tables[tid] = pts

    bhdr, bbody = _section(lines, "BUS")
    bh = [x.strip() for x in bhdr[0]]
    buses = {}
    for l in bbody:
        r = _rec(l)
        buses[r[0]] = dict(zip(bh, r))
    return psts, tables, buses, bh


# ----------------------------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------------------------
def _label(rec):
    return rec["line1"].get("'N A M E'", rec["line1"].get("N A M E", "")) or "%s-%s" % (rec["line1"]["I"], rec["line1"]["J"])


def _name(rec):
    for k, v in rec["line1"].items():
        if "N A M E" in k:
            return v
    return "%s-%s" % (rec["line1"]["I"], rec["line1"]["J"])


def _fmt(v):
    if v is None:
        return "*(nema u zapisu)*"
    return "`%s`" % v if v != "" else "*(prazno)*"


def _transposed(recs, getter, fields, collapse_rates=True):
    """Rows = fields, columns = transformers. RATEx-2..RATEx-12 collapsed if all zero."""
    cols = [_name(r) for r in recs]
    out = ["| Polje | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    rate_tail = [f for f in fields if f.startswith("RATE") and not f.endswith("-1")]
    for f in fields:
        if collapse_rates and f in rate_tail:
            continue
        out.append("| %s | " % f + " | ".join(_fmt(getter(r, f)) for r in recs) + " |")
        if collapse_rates and f.startswith("RATE") and f.endswith("-1") and rate_tail:
            vals = [[getter(r, x) for x in rate_tail] for r in recs]
            cells = []
            for v in vals:
                nz = [x for x in v if x not in (None, "") and float(x) != 0.0]
                cells.append("svi `0.00`" if not nz else ", ".join("`%s`" % x for x in v))
            out.append("| %s … %s | " % (rate_tail[0], rate_tail[-1]) + " | ".join(cells) + " |")
    return "\n".join(out)


def markdown_report(path, title_suffix=""):
    psts, tables, buses, bus_header = read_pst_records(path)
    two = [r for r in psts if not r["three"]]
    three = [r for r in psts if r["three"]]
    md = []
    md.append("Izvor: `%s`. Vrijednosti su prepisane **doslovno** iz datoteke (bez pretvorbe i zaokruživanja); "
              "nazivi polja su iz zaglavlja `@!` same datoteke. Polja koja u zapisu nedostaju označena su "
              "*(nema u zapisu)*." % path.replace("\\", "/").split("/")[-1])

    # overview
    md.append("\n### Pregled\n")
    md.append("| Transformator | Vrsta | I | J | K | STAT | COD1 | CONT1 | ANG1 | WINDV1 | NTP1 | TAB1 | RMA1 / RMI1 | VMA1 / VMI1 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in psts:
        l1, w = r["line1"], r["windings"][0]
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s / %s |" % (
            _name(r), "3W" if r["three"] else "2W", l1["I"], l1["J"], l1["K"], l1["STAT"], w["COD"], w["CONT"],
            w["ANG"], w["WINDV"], w["NTP"], w["TAB"], w["RMA"], w["RMI"], w["VMA"], w["VMI"]))

    def l1get(r, f):
        return r["line1"].get(f)

    def l2get(r, f):
        return r["line2"].get(f) if f in r["line2_header"] else None

    def wget(i):
        def g(r, f):
            if i >= len(r["windings_full"]):
                return None
            raw = r["windings_full"][i]["raw"]
            return raw.get(f)
        return g

    for group, label in ((two, "Dvonamotni PST-ovi"), (three, "Tronamotni PST-ovi (autotransformatori)")):
        if not group:
            continue
        md.append("\n### %s\n" % label)
        h1 = group[0]["line1_header"]
        md.append("**Redak 1 — opći podaci**\n")
        md.append(_transposed(group, l1get, h1))
        md.append("\n**Redak 2 — impedancije i zvjezdište**\n")
        md.append(_transposed(group, l2get, group[0]["line2_header"] if group[0]["three"] else group[0]["line2_header"]))
        nw = 3 if group[0]["three"] else 2
        for i in range(nw):
            hdr = group[0]["windings_full"][i]["header"]
            md.append("\n**Redak %d — namot %d**\n" % (i + 3, i + 1))
            md.append(_transposed(group, wget(i), hdr))

    # buses
    md.append("\n### Sabirnice priključka (zapisi iz sekcije BUS)\n")
    used = []
    for r in psts:
        for key in ("I", "J", "K"):
            b = r["line1"][key]
            if b and b != "0" and b not in used:
                used.append(b)
    md.append("| " + " | ".join(bus_header) + " |")
    md.append("|" + "---|" * len(bus_header))
    for b in used:
        rec = buses.get(b)
        if rec is None:
            md.append("| %s | *(sabirnica ne postoji)* |" % b + " |" * (len(bus_header) - 2))
        else:
            md.append("| " + " | ".join("`%s`" % rec.get(h, "") for h in bus_header) + " |")

    # impedance tables
    md.append("\n### Tablice korekcije impedancije\n")
    used_tabs = sorted({r["windings"][i]["TAB"] for r in psts for i in range(len(r["windings"]))
                        if r["windings"][i].get("TAB") not in (None, "0")}, key=lambda x: int(x))
    allzero_im = all(float(p[2]) == 0.0 for t in tables.values() for p in t)
    md.append("Tablice u datoteci: %s; korištene: %s. Imaginarni dio faktora je %s." % (
        ", ".join(sorted(tables, key=int)), ", ".join(used_tabs),
        "`0.00000` u svim točkama svih tablica" if allzero_im else "**različit od nule u nekim točkama**"))
    users = {t: [_name(r) for r in psts if r["windings"][0].get("TAB") == t] for t in tables}
    ids = sorted(tables, key=int)
    n = max(len(tables[t]) for t in ids)
    md.append("\n| Točka | " + " | ".join("Tab. %s: T [°] | Tab. %s: Re F" % (t, t) for t in ids) + " |")
    md.append("|---|" + "---|---|" * len(ids))
    for i in range(n):
        cells = []
        for t in ids:
            if i < len(tables[t]):
                cells += ["`%s`" % tables[t][i][0], "`%s`" % tables[t][i][1]]
            else:
                cells += ["", ""]
        md.append("| %d | " % (i + 1) + " | ".join(cells) + " |")
    md.append("| **Broj točaka** | " + " | ".join("**%d** | " % len(tables[t]) for t in ids) + "")
    md.append("\n| Tablica | Broj točaka | Koriste je |")
    md.append("|---|---|---|")
    for t in ids:
        md.append("| %s | %d | %s |" % (t, len(tables[t]), ", ".join(users[t]) or "—"))
    return "\n".join(md), psts, tables


def frames(path):
    psts, tables, buses, _ = read_pst_records(path)
    rows = []
    for r in psts:
        for part, d in [("redak 1", r["line1"]), ("redak 2", {k: r["line2"].get(k) for k in r["line2_header"]})] + \
                [("namot %d" % (i + 1), w["raw"]) for i, w in enumerate(r["windings_full"])]:
            for f, v in d.items():
                rows.append(dict(transformator=_name(r), dio=part, polje=f, vrijednost=v))
    zt = [dict(tablica=t, tocka=i + 1, T=p[0], ReF=p[1], ImF=p[2]) for t, pts in tables.items() for i, p in enumerate(pts)]
    return {"pst_zapisi": pd.DataFrame(rows), "tablice_korekcije": pd.DataFrame(zt)}


# ----------------------------------------------------------------------------------------
# Readable page: basic data per station + impedance table per correction table
# ----------------------------------------------------------------------------------------
STATIONS = {"GRACAC": "Gračac", "KONJS": "Konjsko", "MELIN": "Melina", "HE SE": "Senj", "ZERJA": "Žerjavinec"}
# guidelines, Table 3
TABLE3_RANGE = {"Gračac": "±30°", "Senj": "−6,3° do +10,54°", "Žerjavinec": "−4,48° do +6,76°",
                "Konjsko": "−5,4° do +9°", "Melina": "−5,4° do +9°"}


def _station(name):
    for key, label in STATIONS.items():
        if key in name.upper():
            return label
    return name


def _unit(name):
    if "VP " in name.upper():
        return "VP " + name.upper().split("VP ", 1)[1].strip().title()
    return name.split()[0]


def _n(x, dec=None):
    """Croatian number formatting."""
    v = float(x)
    if dec is None:
        s = ("%.5f" % v).rstrip("0").rstrip(".")
    else:
        s = "%.*f" % (dec, v)
    return s.replace("-", "−").replace(".", ",")


def _interp(points, angle):
    pts = [(float(t), float(f)) for t, f, _ in points]
    if angle <= pts[0][0]:
        return pts[0][1]
    if angle >= pts[-1][0]:
        return pts[-1][1]
    for (a0, f0), (a1, f1) in zip(pts, pts[1:]):
        if a0 <= angle <= a1:
            return f0 + (f1 - f0) * (angle - a0) / (a1 - a0)
    return 1.0


def _z_sys(r_w, x_pu, s_pair, sbase=100.0):
    rr = float(r_w) / (float(s_pair) * 1e6)
    xx = float(x_pu)
    return complex(rr, (max(xx * xx - rr * rr, 0.0)) ** 0.5) * sbase / float(s_pair)


def _uk12_eff(rec, factor):
    """Effective |Z12| [%] on SBASE1-2 for a given impedance factor (CZ=3 records)."""
    l2 = rec["line2"]
    s12 = float(l2["SBASE1-2"])
    z12 = _z_sys(l2["R1-2"], l2["X1-2"], s12)
    if not rec["three"]:
        return 100.0 * abs(z12) * factor * s12 / 100.0
    z23 = _z_sys(l2["R2-3"], l2["X2-3"], l2["SBASE2-3"])
    z31 = _z_sys(l2["R3-1"], l2["X3-1"], l2["SBASE3-1"])
    z1 = (z12 + z31 - z23) / 2.0
    return 100.0 * abs(z12 + (factor - 1.0) * z1) * s12 / 100.0


def _bus(buses, b):
    rec = buses.get(b, {})
    return "%s %s (%s kV)" % (b, rec.get("'NAME'", rec.get("NAME", "")).strip("' "),
                              _n(rec.get("BASKV", "0")))


def _station_table(recs, buses, tables):
    units = [_unit(_name(r)) for r in recs]
    rows = []

    def row(label, fn):
        vals = [fn(r) for r in recs]
        rows.append("| %s | %s |" % (label, " | ".join(vals)))

    three = recs[0]["three"]
    w = lambda r, i, k: r["windings_full"][i]["raw"].get(k + str(i + 1)) if i < len(r["windings_full"]) else None
    row("Priključak (namot 1 → namot 2)", lambda r: "%s → %s" % (_bus(buses, r["line1"]["I"]), _bus(buses, r["line1"]["J"])))
    if three:
        row("Tercijar (namot 3)", lambda r: _bus(buses, r["line1"]["K"]))
    row("U pogonu", lambda r: "da" if r["line1"]["STAT"] == "1" else "**ne**")
    nw = 3 if three else 2
    row("Nazivni naponi namota NOMV [kV]", lambda r: " / ".join(
        (_n(w(r, i, "NOMV")) if float(w(r, i, "NOMV") or 0) else "**0** (= bazni napon)") for i in range(nw)))
    row("Namotni naponi WINDV [kV]", lambda r: " / ".join(_n(w(r, i, "WINDV")) for i in range(nw)))
    if three:
        row("Nazivne snage parova 1-2 / 2-3 / 3-1 [MVA]", lambda r: " / ".join(
            _n(r["line2"][k]) for k in ("SBASE1-2", "SBASE2-3", "SBASE3-1")))
        def rate(r, i):
            v = r["windings_full"][i]["raw"].get("RATE%d-1" % (i + 1))
            return "**0**" if float(v or 0) == 0 else _n(v)
        row("RATE namota 1 / 2 / 3 [MVA]", lambda r: " / ".join(rate(r, i) for i in range(3)))
        row("u<sub>k</sub> parova 1-2 / 2-3 / 3-1 [%] (na snazi para)", lambda r: " / ".join(
            _n(100 * float(r["line2"][k]), 2) for k in ("X1-2", "X2-3", "X3-1")))
        row("Gubici u bakru parova 1-2 / 2-3 / 3-1 [kW]", lambda r: " / ".join(
            _n(float(r["line2"][k]) / 1000, 1) for k in ("R1-2", "R2-3", "R3-1")))
    else:
        row("Nazivna snaga [MVA]", lambda r: _n(r["line2"]["SBASE1-2"]))
        row("RATE [MVA]", lambda r: _n(r["windings_full"][0]["raw"]["RATE1-1"]))
        row("u<sub>k</sub> [%]", lambda r: _n(100 * float(r["line2"]["X1-2"]), 3))
        row("Gubici u bakru [kW]", lambda r: _n(float(r["line2"]["R1-2"]) / 1000, 1))
        row("Gubici u željezu [kW] (MAG1 · S<sub>B</sub>)", lambda r: _n(float(r["line1"]["MAG1"]) * 100e3, 1))
    row("Kut u modelu ANG1 [°]", lambda r: "**%s**" % _n(w(r, 0, "ANG")))
    row("Faktor F pri tom kutu *(izračunato)*", lambda r: _n(_interp(tables[w(r, 0, "TAB")], float(w(r, 0, "ANG"))), 4))
    row("u<sub>k12</sub> pri tom kutu [%] *(izračunato)*", lambda r: _n(
        _uk12_eff(r, _interp(tables[w(r, 0, "TAB")], float(w(r, 0, "ANG")))), 2))
    row("Raspon kuta prema Tablici 3 smjernica", lambda r: TABLE3_RANGE.get(_station(_name(r)), "—"))
    row("Tablica korekcije / broj točaka / raspon", lambda r: "%s / %d / %s° … %s°" % (
        w(r, 0, "TAB"), len(tables[w(r, 0, "TAB")]), _n(tables[w(r, 0, "TAB")][0][0]), _n(tables[w(r, 0, "TAB")][-1][0])))
    row("Broj položaja preklopke NTP1", lambda r: w(r, 0, "NTP"))

    def reg(r):
        rma, rmi, vma, vmi = (float(w(r, 0, k)) for k in ("RMA", "RMI", "VMA", "VMI"))
        if abs(rma) > 90 or abs(rmi) > 90:
            return "granice **napona** %s–%s kV, pojas %s–%s p.u." % (_n(rmi), _n(rma), _n(vmi), _n(vma))
        return "granice **kuta** %s° … %s°, pojas toka %s … %s MW" % (_n(rmi), _n(rma), _n(vmi), _n(vma))
    row("Granice u zapisu (RMA/RMI, VMA/VMI)", reg)
    row("Regulacija (COD1 / regulirana sabirnica)", lambda r: "%s (kut, isključena) / %s" % (
        w(r, 0, "COD").replace("-", "−"), w(r, 0, "CONT")))
    if three:
        row("Grupa spoja", lambda r: r["line1"].get("VECGRP") or "—")
        row("Zvjezdište u rješenju (VMSTAR / ANSTAR)", lambda r: "%s p.u. / %s°" % (
            _n(r["line2"]["VMSTAR"], 5), _n(r["line2"]["ANSTAR"], 4)))
    head = "| | " + " | ".join(units) + " |\n|---|" + "---|" * len(units)
    return head + "\n" + "\n".join(rows)


def _impedance_table(tab_id, points, users):
    """users: list of (station, rec). Rows = table points; model angles inserted as rows."""
    stations = []
    for st, r in users:
        if st not in [s for s, _ in stations]:
            stations.append((st, r))
    has_uk = True
    grouped = {}
    for st, r in users:
        a = float(r["windings_full"][0]["raw"]["ANG1"])
        unit = _unit(_name(r)) + ("" if r["line1"]["STAT"] == "1" else " (izvan pogona)")
        grouped.setdefault(a, {}).setdefault(st, []).append(unit)
    marks = {a: ["%s %s" % (st, ", ".join(u)) for st, u in sts.items()] for a, sts in grouped.items()}
    # same impedance data for all stations in this table?
    uks = {st: r for st, r in stations}
    same = len({tuple(r["line2"].get(k) for k in ("R1-2", "X1-2", "SBASE1-2", "R2-3", "X2-3", "SBASE2-3",
                                                     "R3-1", "X3-1", "SBASE3-1")) for _, r in stations}) == 1
    uk_cols = [stations[0]] if same else stations
    head = "| Točka | Kut [°] | F | " + " | ".join(
        "u<sub>k12</sub> [%]" + ("" if same else " " + st) for st, _ in uk_cols) + " | U modelu |"
    out = [head, "|---|---|---|" + "---|" * len(uk_cols) + "---|"]
    angles = [float(p[0]) for p in points]
    extra = [a for a in marks if a not in angles]
    rows = [(float(t), float(f), i + 1) for i, (t, f, _) in enumerate(points)]
    rows += [(a, _interp(points, a), None) for a in extra]
    rows.sort(key=lambda x: (x[0], x[2] is None))
    for a, f, idx in rows:
        uk = " | ".join(_n(_uk12_eff(r, f), 2) for _, r in uk_cols)
        mark = ", ".join(marks.get(a, []))
        if idx is None:
            out.append("| *—* | ***%s*** | ***%s*** | *%s* | **%s** *(interpolirano)* |" % (_n(a), _n(f, 4), uk, mark))
        else:
            cell = "| %d | %s | %s | %s | %s |" % (idx, _n(a, 2), _n(f, 5), uk, ("**%s**" % mark) if mark else "")
            out.append(cell)
    return "\n".join(out), same


def readable_report(path):
    psts, tables, buses, _ = read_pst_records(path)
    by_tab = {}
    for r in psts:
        by_tab.setdefault(r["windings_full"][0]["raw"]["TAB1"], []).append(r)
    md = []
    order = sorted(by_tab, key=lambda t: (not by_tab[t][0]["three"], -len(by_tab[t]), int(t)))
    for t in order:
        recs = by_tab[t]
        stations = []
        for r in recs:
            st = _station(_name(r))
            if st not in stations:
                stations.append(st)
        kind = "autotransformator" if recs[0]["three"] else "dvonamotni PST"
        l1, l2 = recs[0]["line1"], recs[0]["line2"]
        md.append("## %s — tablica korekcije %s\n" % (" i ".join(stations), t))
        for st in stations:
            srecs = [r for r in recs if _station(_name(r)) == st]
            md.append("### %s (%s)\n" % (st, kind))
            md.append(_station_table(srecs, buses, tables) + "\n")
        users = [(_station(_name(r)), r) for r in recs]
        tab_md, same = _impedance_table(t, tables[t], users)
        md.append("### Tablica korekcije impedancije %s\n" % t)
        note = ("u<sub>k12</sub> je izračunata efektivna impedancija para 1-2 na nazivnoj snazi para "
                "za faktor F")
        if recs[0]["three"]:
            note += " (F se primjenjuje na Z<sub>1</sub> zvijezde, pogl. 2, §2.4)"
        if same and len(stations) > 1:
            note += "; %s imaju jednake podatke o impedancijama, pa je stupac zajednički" % " i ".join(stations)
        md.append(note + ".\n")
        md.append(tab_md + "\n")
    return "\n".join(md), psts, tables
