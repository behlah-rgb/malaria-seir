"""Tests for the variant switch, the extended model, convergence spin-up and calibration."""

from dataclasses import replace

import numpy as np
import pytest

from malaria_model import params as p
from malaria_model.calibrate import calibrate_k0
from malaria_model.climate import effective_rainfall, make_synthetic_climate
from malaria_model.config import extended_config, spec_config
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, imported_infections, local_infections, per_1000
from malaria_model.ode import (
    STATE_NAMES, human_rhs, simulate, simulate_converged, simulate_reported_year,
    simulate_with_spinup,
)

OMEGAS = {name: clogging_index(D_d, M_i) for name, (D_d, M_i) in p.WARDS.items()}
# Spec variant, fixed 3-year spin-up, recorded 2026-10-14 before the extended variant existed
PREVIOUS_SPEC = {
    "High infra / high maintenance": (1.2951039393653068, 0.019770685104217738),
    "Medium infra / low maintenance": (1.8569203635346663, 0.04907525154046512),
    "Poor infra / neglected": (12.417963850843535, 1.213366051530695),
}


@pytest.fixture(scope="module")
def climate():
    return make_synthetic_climate()


@pytest.fixture(scope="module")
def extended_runs(climate):
    return {n: simulate_reported_year(o, climate, extended_config(spinup="fixed")).df
            for n, o in OMEGAS.items()}


# --- spec variant -----------------------------------------------------------
def test_spec_reproduces_previous_results(climate):
    for name, (peak, attack) in PREVIOUS_SPEC.items():
        df = simulate_with_spinup(OMEGAS[name], climate, config=spec_config())
        assert df["I_h"].max() == pytest.approx(peak, rel=1e-3)
        assert attack_rate(df) == pytest.approx(attack, rel=1e-3)


def test_spec_unchanged_when_extended_params_change(climate, monkeypatch):
    omega = OMEGAS["Poor infra / neglected"]
    before = simulate(omega, climate, config=spec_config())
    for name, value in [("TAU_RAIN", 99.0), ("R_EFF_MIN", 5.0), ("OMEGA_LENGTHENS_TAU", True),
                        ("TAU_OMEGA_SLOPE", 3.0), ("IMPORT_PER_1000_PER_YEAR", 50.0),
                        ("K_0_CALIBRATED", 12345.0)]:
        monkeypatch.setattr(p, name, value)
    after = simulate(omega, climate, config=spec_config())
    assert np.array_equal(before.to_numpy(), after.to_numpy())


# --- extended variant --------------------------------------------------------
def test_extended_no_nan_and_non_negative(extended_runs):
    for df in extended_runs.values():
        assert np.isfinite(df.to_numpy()).all()
        assert df[STATE_NAMES].to_numpy().min() >= -1e-6


def test_importation_conserves_humans():
    S_h, E_h, I_h, R_h = 9000.0, 300.0, 500.0, 200.0
    total = sum(human_rhs(S_h, E_h, I_h, R_h, I_v=50.0, T=28.0, import_rate=0.01))
    N_h = S_h + E_h + I_h + R_h
    assert total == pytest.approx(p.LAMBDA_H - p.MU_H * N_h - p.DELTA_H * I_h)


def test_extended_population_constant_without_disease_deaths(climate, monkeypatch):
    monkeypatch.setattr(p, "DELTA_H", 0.0)
    df = simulate(OMEGAS["Poor infra / neglected"], climate, config=extended_config())
    assert np.allclose(df["N_h"], p.N_H0, atol=1e-3)


def test_import_split_matches_total(extended_runs, climate):
    # local + imported counted on entry to E_h ~ total counted on exit (alpha_h E_h)
    config = extended_config()
    for df in extended_runs.values():
        split = local_infections(df, climate) + imported_infections(df, config.import_rate)
        assert per_1000(split, df) == pytest.approx(attack_rate(df), rel=0.05)


# --- rainfall memory ----------------------------------------------------------
def test_effective_rainfall_properties(climate):
    rain = climate.rainfall
    r_eff = effective_rainfall(rain, p.TAU_RAIN)
    assert (r_eff >= 0).all()
    assert r_eff.mean() == pytest.approx(rain.mean(), rel=0.01)
    assert np.allclose(effective_rainfall(np.full(30, 4.0), 10.0), 4.0)
    assert np.allclose(effective_rainfall(rain, 1e-3), rain)


def test_tau_switch(monkeypatch):
    assert extended_config().tau(0.1) == extended_config().tau(8.0) == p.TAU_RAIN
    monkeypatch.setattr(p, "OMEGA_LENGTHENS_TAU", True)
    config = extended_config()
    assert config.tau(8.0) == pytest.approx(p.TAU_RAIN * (1 + p.TAU_OMEGA_SLOPE * 8.0))


# --- convergence spin-up ------------------------------------------------------
def test_declining_case_hits_cap_unconverged(climate):
    result = simulate_converged(OMEGAS["High infra / high maintenance"], climate, spec_config())
    assert not result.converged
    assert result.years_run == p.SPINUP_MAX_YEARS
    assert result.growth_factor < 1.0


def test_case_with_importation_converges(climate):
    result = simulate_converged(OMEGAS["High infra / high maintenance"], climate, extended_config())
    assert result.converged
    assert abs(result.growth_factor - 1.0) < p.SPINUP_TOL
    assert len(result.df) == p.N_DAYS


# --- calibration ----------------------------------------------------------------
def test_calibration_round_trip(climate):
    config = extended_config(spinup="fixed", calibrated=False)
    true_k0 = 2000.0
    df = simulate_reported_year(OMEGAS[p.CALIBRATION_WARD], climate,
                                replace(config, k0=true_k0)).df
    result = calibrate_k0(attack_rate(df), climate, config, workers=1)
    assert result.status == "found"
    assert result.k0 == pytest.approx(true_k0, rel=0.02)
    assert len(result.scan) == p.CAL_SCAN_POINTS


def test_calibration_unreachable_below_import_floor(climate):
    config = extended_config(spinup="fixed", calibrated=False)
    result = calibrate_k0(1e-6, climate, config, workers=1)
    assert result.status == "unreachable" and result.k0 is None
