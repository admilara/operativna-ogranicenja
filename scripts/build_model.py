# -*- coding: utf-8 -*-
"""
Izgradnja pandapower modela iz PSS/E v35 .raw datoteke i provjera prema spremljenom
PSS/E rješenju.

Pokretanje: otvoriti u IDLE-u i F5. Postavke su u bloku ispod.
Teorija: docs/teorija/01-mrezni-model.md, docs/teorija/02-pst-korekcija-impedancije.md
"""
# ============================ POSTAVKE ============================
INPUT_RAW    = r""      # .raw datoteka; prazno -> dijalog za odabir
OUTPUT_JSON  = r""      # prazno -> <ime ulaza>_pp.json   (mreža PRIJE rješavanja)
OUTPUT_XLSX  = r""      # prazno -> <ime ulaza>_validacija.xlsx
FREQ_HZ      = 50.0
SLACK_BUS    = 60132    # referentni čvor: RHE Velebit 400 kV
# Točnije modeliranje PST-ova (opcija, v. teorija pogl. 2.8):
PST_TAP_TABLE = r""     # CSV s tablicama po položajima; prazno -> samo kutni model
PST_POSITIONS = {}      # npr. {"T1 400 KONJS": 5}; koristi se samo uz PST_TAP_TABLE
SHOW_TOP     = 15       # koliko najvećih odstupanja napona ispisati
# ==================================================================

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))


def _check_dependencies():
    missing = []
    for mod in ("numpy", "scipy", "pandas", "pandapower", "openpyxl"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print("NEDOSTAJE " + ", ".join(missing) + " u ovoj Python instalaciji:")
        print("   " + sys.executable)
        print('Instalirati s:  "%s" -m pip install %s' % (sys.executable, " ".join(missing)))
        return False
    return True


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
    if not _check_dependencies():
        return None
    import copy
    import warnings
    import pandas as pd
    import pandapower as pp
    from oplimits import ModelError
    from oplimits.psse_raw import read_raw
    from oplimits.build import build_network
    from oplimits.validate import (stored_state_mismatch, add_boundary_injections,
                                   boundary_table, compare_voltages)
    from oplimits.powerflow import run_pf_varlim, set_slack
    from oplimits.pst_tables import load_tap_tables, apply_tap_positions

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    src = INPUT_RAW or _pick_file()
    if not src:
        print("Nije odabrana datoteka.")
        return None
    base = os.path.splitext(src)[0]
    out_json = OUTPUT_JSON or base + "_pp.json"
    out_xlsx = OUTPUT_XLSX or base + "_validacija.xlsx"

    try:
        raw = read_raw(src)
        print("Pročitano: %d sabirnica, %d tereta, %d generatora, %d vodova, %d transformatora"
              % (len(raw["bus"]), len(raw["load"]), len(raw["gen"]), len(raw["branch"]), len(raw["trafo"])))
        print("PSS/E opcije rješavača:", raw["solver"])

        net, fnd, dropped = build_network(raw, FREQ_HZ)
        if PST_TAP_TABLE:
            applied = apply_tap_positions(net, load_tap_tables(PST_TAP_TABLE), PST_POSITIONS, fnd)
            print("PST po tablicama položaja:", ", ".join(applied) or "nijedan")

        mism, x_nodes = stored_state_mismatch(net, raw, dropped)
        inner = mism[~mism.x_cvoriste]
        print("\nNeusklađenost sa spremljenim naponima (unutarnje sabirnice):")
        print("   max |dP| = %.3f MW, max |dQ| = %.3f Mvar" % (inner.dP.abs().max(), inner.dQ.abs().max()))
        if inner.dP.abs().max() > 5 or inner.dQ.abs().max() > 10:
            fnd.warn("validacija", "neusklađenost iznad razine zaokruživanja - provjeriti model")

        add_boundary_injections(net, mism, x_nodes)
        p_units = set_slack(net, SLACK_BUS)
        print("Referentni čvor: %d %s (jedinice na sabirnici: %.1f MW)"
              % (SLACK_BUS, net.bus.at[SLACK_BUS, "name"], p_units))

        net_unsolved = copy.deepcopy(net)
        n_outer = run_pf_varlim(net)
        cmp_v = compare_voltages(net)
        n_lim = int(net.sgen.qlim_of.notna().sum())
        print("\nLoad flow (pandapower + VARLIM): konvergirao, %d vanjskih koraka, %d regulatora na Q granici"
              % (n_outer, n_lim))
        print("   ext_grid P = %.2f MW (očekivano ~0: PSS/E rješenje nema neravnoteže)"
              % net.res_ext_grid.p_mw.sum())
        print("   max |dVM| = %.5f p.u., max |dVA| = %.4f°" % (cmp_v.dVM.abs().max(), cmp_v.dVA.abs().max()))
        top = cmp_v.reindex(cmp_v.dVM.abs().sort_values(ascending=False).index).head(SHOW_TOP)
        print(top.to_string(float_format=lambda v: "%.5f" % v))

        pp.to_json(net_unsolved, out_json)
        with pd.ExcelWriter(out_xlsx) as xw:
            cmp_v.to_excel(xw, sheet_name="naponi_usporedba")
            mism.to_excel(xw, sheet_name="neuskladenost_S")
            boundary_table(net).to_excel(xw, sheet_name="granica_X", index=False)
            fnd.to_frame().to_excel(xw, sheet_name="nalazi", index=False)

        warn = fnd.warnings()
        print("\nNalazi: %d (od toga upozorenja: %d) - list 'nalazi'" % (len(fnd), len(warn)))
        pst = [w for w in warn if w["kategorija"] == "PST"]
        if pst:
            print("\n" + "!" * 78)
            print("UPOZORENJE: %d PST-ova modelirano SAMO KUTNO:" % len(pst))
            print("   " + ", ".join(w["element"] for w in pst))
            print("   Stvarni PST-ovi (dio njih) imaju dijagonalnu regulaciju - kut i napon dolaze")
            print("   iz istog položaja preklopke. Rezultati koji ovise o kutu PST-a su približni.")
            print("   Točnije: tablice po položajima u PST_TAP_TABLE (teorija, pogl. 2.8).")
            print("!" * 78)
        print("\nSpremljeno:\n   %s\n   %s" % (out_json, out_xlsx))
        return net
    except ModelError as e:
        print("GREŠKA:", e)
    except PermissionError as e:
        print("Ne mogu spremiti (datoteka otvorena u Excelu?):", e.filename)
    except pp.LoadflowNotConverged:
        print("GREŠKA: load flow nije konvergirao.")
    return None


NET = main()
