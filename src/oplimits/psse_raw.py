"""Reader for PSS/E v35 .raw files (only the sections and fields this tool needs).

The result is a plain dict of records; no pandapower objects are created here.
Theory: docs/teorija/01-mrezni-model.md
"""
import csv
import io
import re

from .errors import ModelError

UNSUPPORTED_SECTIONS = (
    "TWO-TERMINAL DC", "VSC DC LINE", "MULTI-TERMINAL DC", "FACTS DEVICE",
    "INDUCTION MACHINE", "SYSTEM SWITCHING DEVICE", "MULTI-SECTION LINE", "GNE",
)


def _rec(line):
    row = next(csv.reader(io.StringIO(line), quotechar="'", skipinitialspace=True))
    return [x.strip() for x in row]


def _f(x, default=0.0):
    try:
        return float(x)
    except (ValueError, TypeError):
        return default


def _i(x, default=0):
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return default


def _split_sections(lines):
    sections, current = {"SYSTEM": []}, "SYSTEM"
    for ln in lines:
        s = ln.strip()
        if s == "Q":
            break
        if s.startswith("0 /") or s == "0":
            m = re.search(r"BEGIN (.+?) DATA", s)
            current = m.group(1) if m else "END"
            sections[current] = []
            continue
        if not s or s.startswith("@!"):
            continue
        sections[current].append(ln)
    return sections


def _winding(r):
    return dict(windv=_f(r[0]), nomv=_f(r[1]), ang=_f(r[2]), rate1=_f(r[3]),
                cod=_i(r[15]), cont=_i(r[16]), rma=_f(r[18]), rmi=_f(r[19]),
                vma=_f(r[20]), vmi=_f(r[21]), ntp=_i(r[22]), tab=_i(r[23]))


def read_raw(path):
    """Read a PSS/E v35 .raw file into a dict of records."""
    with open(path, encoding="latin-1") as fh:
        lines = fh.read().splitlines()
    while lines and lines[0].lstrip().startswith("@!"):
        lines = lines[1:]
    if not lines:
        raise ModelError("Datoteka je prazna: %s" % path)
    hdr = _rec(lines[0].split("/")[0])
    rev = _i(hdr[2])
    if rev != 35:
        raise ModelError("Datoteka je PSS/E revizija %s; čitač podržava samo v35." % rev)
    sbase = _f(hdr[1])
    secs = _split_sections(lines[1:])

    for name in UNSUPPORTED_SECTIONS:
        if secs.get(name):
            raise ModelError("Sekcija '%s' nije prazna, a čitač je još ne podržava." % name)

    d = {"sbase": sbase, "basfrq": _f(hdr[5], 50.0), "path": str(path)}
    d["solver"] = " ".join(l.strip() for l in secs["SYSTEM"] if l.strip().startswith("SOLVER"))

    d["bus"] = {}
    for l in secs.get("BUS", []):
        r = _rec(l)
        d["bus"][_i(r[0])] = dict(name=r[1], baskv=_f(r[2]), ide=_i(r[3]), area=_i(r[4]),
                                  zone=_i(r[5]), owner=_i(r[6]), vm=_f(r[7], 1.0), va=_f(r[8]))

    d["load"] = []
    for l in secs.get("LOAD", []):
        r = _rec(l)
        d["load"].append(dict(bus=_i(r[0]), id=r[1], stat=_i(r[2]), pl=_f(r[5]), ql=_f(r[6]),
                              ip=_f(r[7]), iq=_f(r[8]), yp=_f(r[9]), yq=_f(r[10])))

    d["gen"] = []
    for l in secs.get("GENERATOR", []):
        r = _rec(l)
        d["gen"].append(dict(
            bus=_i(r[0]), id=r[1], pg=_f(r[2]), qg=_f(r[3]), qt=_f(r[4]), qb=_f(r[5]),
            vs=_f(r[6], 1.0), ireg=_i(r[7]), mbase=_f(r[9], sbase), stat=_i(r[15]),
            rmpct=_f(r[16], 100.0), pt=_f(r[17]), pb=_f(r[18]),
            o1=_i(r[20]) if len(r) > 20 else 0, o2=_i(r[22]) if len(r) > 22 else 0,
            o3=_i(r[24]) if len(r) > 24 else 0, o4=_i(r[26]) if len(r) > 26 else 0,
            wmod=_i(r[28]) if len(r) > 28 else 0, nfields=len(r)))

    d["branch"] = []
    for l in secs.get("BRANCH", []):
        r = _rec(l)
        d["branch"].append(dict(
            i=_i(r[0]), j=_i(r[1]), ckt=r[2], r=_f(r[3]), x=_f(r[4]), b=_f(r[5]),
            rate1=_f(r[7]), rate2=_f(r[8]), rate3=_f(r[9]),
            gi=_f(r[19]), bi=_f(r[20]), gj=_f(r[21]), bj=_f(r[22]),
            stat=_i(r[23]), length=_f(r[25])))

    # transformers: 4 lines (two-winding, K=0) or 5 lines (three-winding)
    tl = secs.get("TRANSFORMER", [])
    d["trafo"], k = [], 0
    while k < len(tl):
        r1 = _rec(tl[k])
        t = dict(i=_i(r1[0]), j=_i(r1[1]), k=_i(r1[2]), ckt=r1[3], cw=_i(r1[4]), cz=_i(r1[5]),
                 cm=_i(r1[6]), mag1=_f(r1[7]), mag2=_f(r1[8]), name=r1[10].strip(),
                 stat=_i(r1[11]), vecgrp=r1[20] if len(r1) > 20 else "")
        r2 = _rec(tl[k + 1])
        if t["k"] == 0:
            t.update(r12=_f(r2[0]), x12=_f(r2[1]), sb12=_f(r2[2], sbase))
            t["w1"] = _winding(_rec(tl[k + 2]))
            r4 = _rec(tl[k + 3])
            t["w2"] = dict(windv=_f(r4[0]), nomv=_f(r4[1]), ang=0.0, rate1=0.0, tab=0)
            k += 4
        else:
            t.update(r12=_f(r2[0]), x12=_f(r2[1]), sb12=_f(r2[2], sbase),
                     r23=_f(r2[3]), x23=_f(r2[4]), sb23=_f(r2[5], sbase),
                     r31=_f(r2[6]), x31=_f(r2[7]), sb31=_f(r2[8], sbase),
                     vmstar=_f(r2[9], 1.0), anstar=_f(r2[10]))
            t["w1"] = _winding(_rec(tl[k + 2]))
            t["w2"] = _winding(_rec(tl[k + 3]))
            t["w3"] = _winding(_rec(tl[k + 4]))
            k += 5
        d["trafo"].append(t)

    # impedance correction tables: id, then triplets (T, Re F, Im F); a zero triplet ends a table
    d["ztab"], buf = {}, []
    for l in secs.get("IMPEDANCE CORRECTION", []):
        buf.extend(l.replace(",", " ").split())
    pos = 0
    while pos < len(buf):
        tid = _i(buf[pos])
        pos += 1
        pts = []
        while pos + 2 < len(buf) + 1:
            angle, factor = _f(buf[pos]), _f(buf[pos + 1])
            pos += 3
            if angle == 0.0 and factor == 0.0:
                break
            pts.append((angle, factor))
        d["ztab"][tid] = sorted(pts)

    d["swshunt"] = []
    for l in secs.get("SWITCHED SHUNT", []):
        r = _rec(l)
        d["swshunt"].append(dict(bus=_i(r[0]), id=r[1], modsw=_i(r[2]), stat=_i(r[4]),
                                 vswhi=_f(r[5]), vswlo=_f(r[6]), swreg=_i(r[7]), binit=_f(r[11])))
    d["fxshunt"] = []
    for l in secs.get("FIXED SHUNT", []):
        r = _rec(l)
        d["fxshunt"].append(dict(bus=_i(r[0]), id=r[1], stat=_i(r[2]), gl=_f(r[3]), bl=_f(r[4])))
    d["area"] = [_rec(l) for l in secs.get("AREA", [])]
    return d


def impedance_factor(table, angle_deg):
    """PSS/E impedance correction: linear interpolation of F(angle), clamped at the ends."""
    if not table:
        return 1.0
    if angle_deg <= table[0][0]:
        return table[0][1]
    if angle_deg >= table[-1][0]:
        return table[-1][1]
    for (a0, f0), (a1, f1) in zip(table, table[1:]):
        if a0 <= angle_deg <= a1:
            return f0 + (f1 - f0) * (angle_deg - a0) / (a1 - a0) if a1 > a0 else f0
    return 1.0
