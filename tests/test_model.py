"""Tests. Unit tests use synthetic numbers; integration tests run only when the model
data/modeli/ScA_2029.raw is present locally (it is never committed)."""
import copy
import math
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from oplimits.psse_raw import impedance_factor           # noqa: E402
from oplimits.build import trafo3w_pair_percent         # noqa: E402

RAW = os.path.join(ROOT, "data", "modeli", "ScA_2029.raw")
TAB4 = [(4.91, 0.7944), (5.70, 0.7889)]


def test_impedance_factor_interpolation_and_clamp():
    assert impedance_factor(TAB4, 5.5) == pytest.approx(0.79029, abs=1e-5)
    assert impedance_factor(TAB4, 0.0) == 0.7944      # clamped below
    assert impedance_factor(TAB4, 10.0) == 0.7889     # clamped above
    assert impedance_factor([], 3.0) == 1.0


def test_trafo3w_star_correction_example():
    """Worked example from theory, chapter 2.4 (400/220/30 kV, 400 MVA)."""
    z12, z23, z31 = complex(0.00036, 0.02917), complex(0.00234, 0.03993), complex(0.00237, 0.13348)
    f = 0.79029
    pc = trafo3w_pair_percent(z12, z23, z31, f, 400, 400, 100, 100)
    z1 = (z12 + z31 - z23) / 2
    assert z1.imag == pytest.approx(0.06136, abs=1e-5)
    # Z12' = Z12 + (F-1) Z1  -> |Z12'| = 0.01631 p.u. on 100 MVA, pandapower vk on 400 MVA
    assert pc["hv"][0] == pytest.approx(100 * abs(z12 + (f - 1) * z1) * 400 / 100, rel=1e-9)
    assert abs(z12 + (f - 1) * z1) == pytest.approx(0.01631, abs=1e-5)
    # Z23 unchanged; referenced to min(400, 100) MVA
    assert pc["mv"][0] == pytest.approx(100 * abs(z23) * 100 / 100, rel=1e-9)
    # F = 1 leaves all pairs at nominal values
    pc1 = trafo3w_pair_percent(z12, z23, z31, 1.0, 400, 400, 100, 100)
    assert pc1["hv"][0] == pytest.approx(100 * abs(z12) * 4, rel=1e-9)


needs_data = pytest.mark.skipif(not os.path.exists(RAW), reason="model data not present")


@pytest.fixture(scope="module")
def model():
    from oplimits.psse_raw import read_raw
    from oplimits.build import build_network
    from oplimits.validate import stored_state_mismatch, add_boundary_injections
    from oplimits.powerflow import set_slack
    raw = read_raw(RAW)
    net, fnd, dropped = build_network(raw)
    mism, x_nodes = stored_state_mismatch(net, raw, dropped)
    add_boundary_injections(net, mism, x_nodes)
    set_slack(net, 60132)
    return raw, net, fnd, dropped, mism


@needs_data
def test_stored_state_mismatch_at_rounding_level(model):
    _, _, _, _, mism = model
    inner = mism[~mism.x_cvoriste]
    assert inner.dP.abs().max() < 1.0
    assert inner.dQ.abs().max() < 3.0


@needs_data
def test_loadflow_reproduces_psse(model):
    from oplimits.powerflow import run_pf_varlim
    from oplimits.validate import compare_voltages
    net = copy.deepcopy(model[1])
    run_pf_varlim(net)
    cmp_v = compare_voltages(net)
    assert cmp_v.dVM.abs().max() < 5e-4
    assert cmp_v.dVA.abs().max() < 0.05
    assert abs(net.res_ext_grid.p_mw.sum()) < 0.5


@needs_data
def test_set_pst_angle_is_idempotent(model):
    from oplimits.build import set_pst_angle
    net = copy.deepcopy(model[1])
    for el in ("trafo", "trafo3w"):
        df = net[el]
        for idx in df.index[df.pst.astype(bool)]:
            before = df.loc[idx].copy()
            set_pst_angle(net, el, idx, float(before.psse_ang1))
            cols = (["vk_percent", "vkr_percent", "shift_degree"] if el == "trafo" else
                    ["vk_hv_percent", "vk_mv_percent", "vk_lv_percent", "vkr_hv_percent",
                     "shift_mv_degree", "shift_lv_degree"])
            for c in cols:
                assert df.at[idx, c] == pytest.approx(before[c], rel=1e-9, abs=1e-12), (el, idx, c)


@needs_data
def test_tap_table_equal_to_angle_model_changes_nothing(model, tmp_path):
    """A position table that encodes the angle-only state must give identical parameters."""
    from oplimits.pst_tables import load_tap_tables, apply_tap_positions
    net = copy.deepcopy(model[1])
    i = net.trafo3w.index[net.trafo3w.name == "T1 400 KONJS"][0]
    t3 = net.trafo3w.loc[i].copy()
    csv = tmp_path / "pst.csv"
    csv.write_text("transformer,step,u_w1_kv,angle_deg,z_factor\nT1 400 KONJS,7,%r,%r,%r\n"
                   % (float(t3.vn_hv_kv), float(t3.psse_ang1), float(t3.psse_zfactor)))
    apply_tap_positions(net, load_tap_tables(csv), {"T1 400 KONJS": 7}, model[2].__class__())
    for c in ("vk_hv_percent", "vk_lv_percent", "vn_hv_kv", "shift_mv_degree"):
        assert net.trafo3w.at[i, c] == pytest.approx(t3[c], rel=1e-12)
    assert net.trafo3w.at[i, "pst_model"] == "tablica po položajima"


@needs_data
def test_json_roundtrip_keeps_ztab(model, tmp_path):
    import pandapower as pp
    from oplimits.build import set_pst_angle
    p = tmp_path / "net.json"
    pp.to_json(model[1], str(p))
    net = pp.from_json(str(p))
    assert "4" in net["ztab"]
    i = net.trafo3w.index[net.trafo3w.name == "T1 400 KONJS"][0]
    set_pst_angle(net, "trafo3w", i, 5.5)
    assert net.trafo3w.at[i, "psse_zfactor"] == pytest.approx(0.79029, abs=1e-5)
    assert not math.isnan(net.trafo3w.at[i, "vk_hv_percent"])

