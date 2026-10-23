"""Thermal model: reproduces the ACCC datasheet and the guidelines' Table 4."""
import csv
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from oplimits.thermal import accc_datasheet_check, calibrate_table4, htls_ratings  # noqa: E402


def test_model_reproduces_accc_datasheet():
    for name, pairs in accc_datasheet_check().items():
        for model, sheet in pairs:
            assert model == pytest.approx(sheet, rel=0.005), name


def test_calibration_reproduces_table4():
    wind, solar, rms, mx = calibrate_table4(80.0)
    assert rms < 0.005 and mx < 0.01


def test_htls_csv_is_up_to_date():
    rows, _ = htls_ratings()
    with open(os.path.join(ROOT, "config", "htls_ratings.csv"), encoding="utf-8") as fh:
        saved = list(csv.DictReader(fh))
    assert len(saved) == len(rows)
    for s, r in zip(saved, rows):
        assert int(s["htls_a"]) == r["htls_a"]
        assert s["htls_conductor"] == r["htls_conductor"]
