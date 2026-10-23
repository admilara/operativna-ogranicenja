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
