# -*- coding: utf-8 -*-
"""
Pregled PST-ova iz .raw datoteke: osnovni podaci transformatora i tablica korekcije
impedancije, u obliku stranice teorijske knjige (Markdown).

Pokretanje: otvoriti u IDLE-u i F5. Postavke su u bloku ispod.
Teorija: docs/teorija/prilog-pst-zapisi.md
"""
# ============================ POSTAVKE ============================
INPUT_RAW  = r""     # .raw datoteka; prazno -> dijalog za odabir
OUTPUT_MD  = r""     # prazno -> <ime ulaza>_pst.md
VERBATIM   = False   # True -> doslovni ispis svih polja zapisa umjesto pregleda
# ==================================================================

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))


def _pick_file():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Odaberi PSS/E .raw",
                                          filetypes=[("PSS/E raw", "*.raw"), ("Sve", "*.*")])
        root.destroy()
        return path
    except Exception:
        print("Dijalog se nije otvorio - upisati putanju u INPUT_RAW u bloku POSTAVKE.")
        return ""


def main():
    try:
        import pandas  # noqa: F401
    except ImportError as e:
        print("NEDOSTAJE %s u ovoj Python instalaciji:\n   %s" % (e.name, sys.executable))
        print('Instalirati s:  "%s" -m pip install %s' % (sys.executable, e.name))
        return
    from oplimits import ModelError
    from oplimits.pst_report import markdown_report, readable_report

    src = INPUT_RAW or _pick_file()
    if not src:
        print("Nije odabrana datoteka.")
        return
    out = OUTPUT_MD or os.path.splitext(src)[0] + "_pst.md"
    try:
        md, psts, tables = (markdown_report if VERBATIM else readable_report)(src)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        print("PST-ova: %d, tablica korekcije: %d" % (len(psts), len(tables)))
        print("Spremljeno:", out)
    except ModelError as e:
        print("GREŠKA:", e)
    except PermissionError as e:
        print("Ne mogu spremiti:", e.filename)


main()
