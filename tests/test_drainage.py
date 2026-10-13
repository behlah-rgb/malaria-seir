"""Tests for drainage.py (SPEC §1-2) and DEVIATION #1."""

import pytest

from malaria_model import params as p
from malaria_model.drainage import carrying_capacity, clogging_index, larval_mortality


def test_clogging_index_hand_values():
    # Omega = (1 - M_i) / (D_d + 0.001)
    assert clogging_index(0.8, 0.9) == pytest.approx(0.1 / 0.801)
    assert clogging_index(0.1, 0.1) == pytest.approx(0.9 / 0.101)
    assert clogging_index(0.5, 1.0) == 0.0  # perfect maintenance -> no clogging


def test_clogging_increases_when_maintenance_or_drainage_drops():
    assert clogging_index(0.5, 0.2) > clogging_index(0.5, 0.8)
    assert clogging_index(0.2, 0.5) > clogging_index(0.8, 0.5)


def test_carrying_capacity_hand_value():
    # K_0 * (1 + eta * Omega) * R = 500 * 1.5 * 10
    assert carrying_capacity(10.0, 1.0) == pytest.approx(p.K_0 * (1 + p.ETA * 1.0) * 10.0)
    assert carrying_capacity(10.0, 1.0) == pytest.approx(7500.0)


def test_carrying_capacity_floor_on_dry_day():
    # DEVIATION #1: R = 0 would give K_v = 0; floored at K_V_MIN
    assert carrying_capacity(0.0, 5.0) == p.K_V_MIN


def test_larval_mortality_below_threshold_is_baseline():
    assert larval_mortality(p.R_FLUSH - 1.0, 1.0) == pytest.approx(p.MU_BASE)


def test_larval_mortality_flushing_above_threshold():
    R, omega = p.R_FLUSH + 10.0, 1.0
    expected = p.MU_BASE + p.MU_FLUSH * 10.0 / (omega + p.EPSILON)
    assert larval_mortality(R, omega) == pytest.approx(expected)
    # clogged drains (higher Omega) flush less
    assert larval_mortality(R, 8.0) < larval_mortality(R, 0.1)
