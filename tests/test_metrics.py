"""Tests for spin-up, metrics, R0 and the sensitivity helper."""

import math

import numpy as np
import pandas as pd
import pytest

from malaria_model import params as p
from malaria_model.climate import biting_rate, incubation_rate, make_synthetic_climate, vector_mortality
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, day_of_peak, new_infections, peak_infectious
from malaria_model.ode import initial_state, simulate, simulate_with_spinup
from malaria_model.r0 import ngm_r0
from malaria_model.sensitivity import override_params

OMEGA_POOR = clogging_index(*p.WARDS["Poor infra / neglected"])


@pytest.fixture(scope="module")
def climate():
    return make_synthetic_climate()


def test_climate_repeat(climate):
    c3 = climate.repeat(3)
    assert len(c3.temperature) == 3 * p.N_DAYS
    assert c3.R_at(2 * p.N_DAYS + 100) == pytest.approx(climate.R_at(100))


def test_spinup_returns_last_year_of_full_run(climate):
    df = simulate_with_spinup(OMEGA_POOR, climate)
    assert len(df) == p.N_DAYS
    assert df.index[0] == 0 and df.index[-1] == p.N_DAYS - 1
    full = simulate(OMEGA_POOR, climate.repeat(p.N_YEARS_TOTAL), initial_state(OMEGA_POOR, climate))
    assert np.allclose(df["I_h"].to_numpy(), full["I_h"].iloc[-p.N_DAYS:].to_numpy())
    assert np.isfinite(df.to_numpy()).all()


def _toy_trajectory(E_h: np.ndarray, I_h: np.ndarray, N_h: float = 10_000.0) -> pd.DataFrame:
    days = np.arange(len(E_h), dtype=float)
    return pd.DataFrame({"E_h": E_h, "I_h": I_h, "N_h": N_h}, index=pd.Index(days, name="day"))


def test_new_infections_and_attack_rate_hand_value():
    # constant E_h = 12 over days 0..10: integral of alpha_h * 12 dt = alpha_h * 12 * 10
    df = _toy_trajectory(np.full(11, 12.0), np.zeros(11))
    assert new_infections(df) == pytest.approx(p.ALPHA_H * 12.0 * 10.0)
    assert attack_rate(df) == pytest.approx(1000.0 * p.ALPHA_H * 12.0 * 10.0 / 10_000.0)


def test_peak_and_day_of_peak():
    df = _toy_trajectory(np.zeros(5), np.array([1.0, 3.0, 7.0, 2.0, 0.5]))
    assert peak_infectious(df) == 7.0
    assert day_of_peak(df) == 2


def test_ngm_r0_hand_value_and_zero_vectors():
    T, m = 28.0, 2.0
    a, mu_v, g = biting_rate(T), vector_mortality(T), incubation_rate(T)
    K_hv = a * p.BETA_HV / mu_v * p.ALPHA_H / (p.ALPHA_H + p.MU_H)
    K_vh = a * p.BETA_VH * m / (p.GAMMA_H + p.MU_H + p.DELTA_H) * g / (g + mu_v)
    assert ngm_r0(T, m) == pytest.approx(math.sqrt(K_hv * K_vh))
    assert ngm_r0(T, 0.0) == 0.0
    assert ngm_r0(T, 4.0) == pytest.approx(2.0 * ngm_r0(T, 1.0))  # R0 scales with sqrt(m)


def test_override_params_restores_values():
    before = p.GAMMA_H
    with override_params(GAMMA_H=0.5):
        assert p.GAMMA_H == 0.5
    assert p.GAMMA_H == before
