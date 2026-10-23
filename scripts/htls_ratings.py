# -*- coding: utf-8 -*-
"""
Nazivne vrijednosti vodova nakon zamjene HTLS (ACCC) vodičem, u obliku Tablice 4 smjernica.

1. provjera toplinskog modela (IEEE 738) prema katalogu ACCC vodiča,
2. kalibracija nepoznatih uvjeta Tablice 4 (vjetar, Sunce, najviša temperatura Al/Fe vodiča),
3. ACCC vodič istog promjera na 180 °C uz kalibrirane uvjete -> config/htls_ratings.csv

Pokretanje: otvoriti u IDLE-u i F5.
Teorija: docs/teorija/07-mjere.md, §7.2
"""
# ============================ POSTAVKE ============================
OUTPUT_CSV = r""    # prazno -> config/htls_ratings.csv u repozitoriju
# ==================================================================

import csv
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))


def main():
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
    except ImportError as e:
        print("NEDOSTAJE %s u ovoj Python instalaciji:\n   %s" % (e.name, sys.executable))
        print('Instalirati s:  "%s" -m pip install %s' % (sys.executable, e.name))
        return
    from oplimits.thermal import accc_datasheet_check, htls_ratings

    print("1. Model prema katalogu ACCC (25 °C, 0,61 m/s, 1033 W/m²):")
    for name, pairs in accc_datasheet_check().items():
        print("   %-13s " % name + "  ".join("%5.0f/%5d A (%+.1f %%)" % (m, a, 100 * (m / a - 1)) for m, a in pairs))

    rows, fits = htls_ratings()
    print("\n2. Kalibracija na Tablicu 4 (sva četiri Al/Fe vodiča, 0-40 °C):")
    for t, (wind, solar, rms, mx) in fits.items():
        print("   T_max Al/Fe = %.0f °C: vjetar %.3f m/s, Sunce %.0f W/m², odstupanje RMS %.2f %%, najveće %.2f %%"
              % (t, wind, solar, 100 * rms, 100 * mx))

    out = OUTPUT_CSV or os.path.join(_REPO, "config", "htls_ratings.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("\n3. HTLS na 180 °C (najniža vrijednost preko kalibracija):")
    for r in rows:
        if r["ambient_c"] in (15, 25, 40):
            print("   %s kV %-6s -> %-17s %2d °C: %4d A (%5.1f MVA), postojeći %4d A, raspon kalibracija %.1f %%"
                  % (r["voltage_kv"], r["existing_conductor"], r["htls_conductor"], r["ambient_c"],
                     r["htls_a"], r["htls_mva"], r["existing_a"], r["spread_pct"]))
    print("\nSpremljeno:", out)


main()
