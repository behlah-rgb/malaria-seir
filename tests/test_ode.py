"""Tests for the ODE system (SPEC §5): validity and human population balance."""

import numpy as np
import pytest
from scipy.integrate import trapezoid

from malaria_model import params as p
from malaria_model.climate import make_synthetic_climate
from malaria_model.drainage import clogging_index
from malaria_model.ode import STATE_NAMES, human_rhs, initial_state, simulate

OMEGAS = [clogging_index(D_d, M_i) for D_d, M_i in p.WARDS.values()]


@pytest.fixture(scope="module")
def climate():
    return make_synthetic_climate()


@pytest.fixture(scope="module")
def runs(climate):
    return [simulate(omega, climate) for omega in OMEGAS]


def test_no_nan_or_inf(runs):
    for df in runs:
        assert np.isfinite(df.to_numpy()).all()


def test_compartments_non_negative(runs):
    # small tolerance for solver round-off; states are NOT clipped in the model
    for df in runs:
        assert df[STATE_NAMES].to_numpy().min() >= -1e-6


def test_disease_free_stays_disease_free(climate):
    y0 = initial_state(OMEGAS[-1], climate)
    y0[STATE_NAMES.index("S_h")] += y0[STATE_NAMES.index("I_h")]
    y0[STATE_NAMES.index("I_h")] = 0.0
    df = simulate(OMEGAS[-1], climate, y0)
    for col in ["E_v", "I_v", "E_h", "I_h", "R_h"]:
        assert np.abs(df[col]).max() < 1e-6


def test_human_derivatives_sum_to_births_minus_deaths():
    S_h, E_h, I_h, R_h = 9000.0, 300.0, 500.0, 200.0
    total = sum(human_rhs(S_h, E_h, I_h, R_h, I_v=50.0, T=28.0))
    N_h = S_h + E_h + I_h + R_h
    assert total == pytest.approx(p.LAMBDA_H - p.MU_H * N_h - p.DELTA_H * I_h)


def test_human_population_balance_over_time(runs):
    # N_h(t) - N_h(0) must equal the integral of (Lambda_h - mu_h N_h - delta_h I_h)
    for df in runs:
        t = df.index.to_numpy()
        net_flow = p.LAMBDA_H - p.MU_H * df["N_h"] - p.DELTA_H * df["I_h"]
        expected = df["N_h"].iloc[0] + trapezoid(net_flow, t)
        assert df["N_h"].iloc[-1] == pytest.approx(expected, abs=1e-2)


def test_population_constant_without_disease_deaths(climate, monkeypatch):
    monkeypatch.setattr(p, "DELTA_H", 0.0)
    df = simulate(OMEGAS[-1], climate)
    assert np.allclose(df["N_h"], p.N_H0, atol=1e-3)
