"""Steady-state conductor ampacity (IEEE 738 heat balance) and HTLS ratings.

The guidelines give ratings of existing Al/Fe conductors (Table 4) but not of HTLS
conductors. HTLS ratings are therefore computed:

1. the heat-balance model is checked against the ACCC datasheet (IEEE 738-2006 conditions);
2. the unknown weather assumptions behind Table 4 (wind speed, solar heat, max conductor
   temperature of Al/Fe) are calibrated so that the model reproduces Table 4;
3. ACCC conductors of the same diameter are rated at 180 C under the calibrated assumptions.

Theory: docs/teorija/07-mjere.md, section 7.2 (HTLS)
"""
import math

import numpy as np
from scipy.optimize import least_squares

# Guidelines, Table 4: permissible current [A] of Al/Fe conductors vs ambient temperature [C]
TABLE4_AMBIENT_C = [0, 5, 10, 15, 20, 25, 30, 35, 40]
TABLE4_A = {
    "150/25": [613, 595, 576, 555, 534, 512, 489, 465, 439],
    "240/40": [843, 817, 791, 764, 735, 705, 673, 640, 605],
    "360/57": [1084, 1054, 1020, 985, 948, 910, 869, 826, 780],
    "490/65": [1322, 1282, 1241, 1198, 1154, 1107, 1058, 1006, 951],
}

# Al/Fe conductors (EN 50182 / DIN 48204 nominal values): diameter [mm], DC resistance at 20 C [ohm/km]
ACSR = {
    "150/25": (17.1, 0.1939),
    "240/40": (21.9, 0.1188),
    "360/57": (26.6, 0.0797),
    "490/65": (30.6, 0.0590),
}
ALUMINIUM_ALPHA = 0.00403   # 1/K

# ACCC datasheet (CTC Global, "ACCC Conductor: International sizes (metric units)"):
# diameter [mm], R_AC at 25 C and 200 C [ohm/km], ampacity at 75/180/200 C [A] under
# IEEE 738-2006: 25 C ambient, 0.61 m/s wind, 1033 W/m2, absorptivity = emissivity = 0.5
ACCC = {
    "ZADAR":        (17.10, 0.1611, 0.2720, (533, 895, 942)),
    "ROVINJ":       (17.10, 0.1520, 0.2566, (548, 922, 970)),
    "LISBON":       (21.79, 0.0910, 0.1532, (755, 1285, 1353)),
    "STOCKHOLM 2L": (26.40, 0.0625, 0.1047, (960, 1650, 1740)),
    "STOCKHOLM 3L": (26.40, 0.0637, 0.1068, (950, 1633, 1723)),
    "VIENNA":       (30.42, 0.0466, 0.0773, (1156, 2007, 2120)),
}
DATASHEET_CONDITIONS = dict(ambient_c=25.0, wind_ms=0.61, solar_wm2=1033.0, alpha=0.5, eps=0.5)
ACCC_CONTINUOUS_C = 180.0

# Same-diameter replacement for each existing conductor (110 kV and 220 kV; no HTLS at 400 kV)
REPLACEMENT = {"150/25": "ROVINJ", "240/40": "LISBON", "360/57": "STOCKHOLM 2L"}
VOLTAGE_KV = {"150/25": 110, "240/40": 110, "360/57": 220}


def _air(t_film, elevation_m=0.0):
    mu = 1.458e-6 * (t_film + 273.0) ** 1.5 / (t_film + 383.4)
    rho = (1.293 - 1.525e-4 * elevation_m + 6.379e-9 * elevation_m ** 2) / (1.0 + 0.00367 * t_film)
    k = 2.424e-2 + 7.477e-5 * t_film - 4.407e-9 * t_film ** 2
    return mu, rho, k


def heat_loss_w_per_m(d_m, t_cond, t_amb, wind_ms, eps):
    """Convective (forced/natural, wind perpendicular) + radiative cooling, IEEE 738 SI form."""
    mu, rho, k = _air((t_cond + t_amb) / 2.0)
    re = d_m * rho * wind_ms / mu
    dt = max(t_cond - t_amb, 0.0)
    qc = max((1.01 + 1.35 * re ** 0.52) * k * dt, 0.754 * re ** 0.6 * k * dt,
             3.645 * rho ** 0.5 * d_m ** 0.75 * dt ** 1.25)
    qr = 17.8 * d_m * eps * (((t_cond + 273.0) / 100.0) ** 4 - ((t_amb + 273.0) / 100.0) ** 4)
    return qc + qr


def ampacity_a(d_mm, r_ohm_km, t_cond, t_amb, wind_ms, solar_wm2, alpha=0.5, eps=0.5):
    """Steady-state current [A]; r_ohm_km is a function of conductor temperature."""
    d = d_mm / 1000.0
    q = heat_loss_w_per_m(d, t_cond, t_amb, wind_ms, eps) - alpha * solar_wm2 * d
    return math.sqrt(max(q, 0.0) / (r_ohm_km(t_cond) / 1000.0))


def r_linear(r1, t1, r2, t2):
    return lambda t: r1 + (r2 - r1) * (t - t1) / (t2 - t1)


def r_acsr(r20):
    return lambda t: r20 * (1.0 + ALUMINIUM_ALPHA * (t - 20.0))


def accc_datasheet_check():
    """Model vs datasheet at 75/180/200 C. Returns {name: [(model, datasheet), ...]}."""
    c = DATASHEET_CONDITIONS
    out = {}
    for name, (d, r25, r200, amps) in ACCC.items():
        r = r_linear(r25, 25.0, r200, 200.0)
        out[name] = [(ampacity_a(d, r, t, c["ambient_c"], c["wind_ms"], c["solar_wm2"], c["alpha"], c["eps"]), a)
                     for t, a in zip((75.0, 180.0, 200.0), amps)]
    return out


def calibrate_table4(t_max_acsr):
    """Fit wind speed and solar heat so the model reproduces Table 4 for all four Al/Fe
    conductors at a given max conductor temperature. Returns (wind, solar, rms_rel, max_rel)."""
    def residuals(p):
        wind, solar = p
        res = []
        for cond, amps in TABLE4_A.items():
            d, r20 = ACSR[cond]
            for ta, a in zip(TABLE4_AMBIENT_C, amps):
                res.append(ampacity_a(d, r_acsr(r20), t_max_acsr, ta, wind, solar) / a - 1.0)
        return np.array(res)
    fit = least_squares(residuals, [0.6, 600.0], bounds=([0.05, 0.0], [5.0, 1500.0]))
    r = residuals(fit.x)
    return float(fit.x[0]), float(fit.x[1]), float(np.sqrt(np.mean(r ** 2))), float(np.abs(r).max())


def htls_ratings(calibrations=(80.0, 85.0, 90.0)):
    """HTLS rating per existing conductor and ambient temperature: the lowest value over the
    calibrations that reproduce Table 4 (conservative). Returns a list of dict rows."""
    fits = {t: calibrate_table4(t) for t in calibrations}
    rows = []
    for cond, htls in REPLACEMENT.items():
        d, r25, r200, _ = ACCC[htls]
        r = r_linear(r25, 25.0, r200, 200.0)
        u = VOLTAGE_KV[cond]
        for i, ta in enumerate(TABLE4_AMBIENT_C):
            per_cal = {t: ampacity_a(d, r, ACCC_CONTINUOUS_C, ta, f[0], f[1]) for t, f in fits.items()}
            amps = min(per_cal.values())
            rows.append(dict(voltage_kv=u, existing_conductor=cond, htls_conductor="ACCC " + htls,
                             ambient_c=ta, existing_a=TABLE4_A[cond][i], htls_a=round(amps),
                             htls_mva=round(math.sqrt(3) * u * amps / 1000.0, 1),
                             spread_pct=round(100.0 * (max(per_cal.values()) / amps - 1.0), 1)))
    return rows, fits
