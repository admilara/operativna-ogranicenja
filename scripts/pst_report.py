# -*- coding: utf-8 -*-
"""
Doslovni ispis svih podataka koje .raw datoteka sadrži za svaki PST
(transformator s kontrolom kuta, tablicom korekcije impedancije ili kutom različitim od nule).

Pokretanje: otvoriti u IDLE-u i F5. Postavke su u bloku ispod.
Teorija: docs/teorija/prilog-pst-zapisi.md
"""
# ============================ POSTAVKE ============================
INPUT_RAW   = r""   # .raw datoteka; prazno -> dijalog za odabir
OUTPUT_MD   = r""   # prazno -> <ime ulaza>_pst.md
OUTPUT_XLSX = r""   # prazno -> <ime ulaza>_pst.xlsx
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
        import pandas as pd
        import openpyxl  # noqa: F401
    except ImportError as e:
        print("NEDOSTAJE %s u ovoj Python instalaciji:\n   %s" % (e.name, sys.executable))
        print('Instalirati s:  "%s" -m pip install %s' % (sys.executable, e.name))
        return
    from oplimits import ModelError
    from oplimits.pst_report import markdown_report, frames

    src = INPUT_RAW or _pick_file()
    if not src:
        print("Nije odabrana datoteka.")
        return
    base = os.path.splitext(src)[0]
    out_md = OUTPUT_MD or base + "_pst.md"
    out_xlsx = OUTPUT_XLSX or base + "_pst.xlsx"
    try:
        md, psts, tables = markdown_report(src)
        with open(out_md, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        with pd.ExcelWriter(out_xlsx) as xw:
            for name, df in frames(src).items():
                df.to_excel(xw, sheet_name=name, index=False)
        print("PST-ova: %d, tablica korekcije: %d" % (len(psts), len(tables)))
        print("Spremljeno:\n   %s\n   %s" % (out_md, out_xlsx))
    except ModelError as e:
        print("GREŠKA:", e)
    except PermissionError as e:
        print("Ne mogu spremiti (datoteka otvorena u Excelu?):", e.filename)


main()
