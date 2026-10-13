"""Tests for the thermal response functions (SPEC §3) and DEVIATIONS #2-#4."""

import math

import pytest

from malaria_model import params as p
from malaria_model.climate import (
    biting_rate, incubation_rate, make_synthetic_climate, vector_mortality,
)


def test_biting_rate_hand_value_25C():
    # 2.03e-4 * 25 * (25 - 11.7) * sqrt(42.3 - 25)
    assert biting_rate(25.0) == pytest.approx(2.03e-4 * 25 * 13.3 * math.sqrt(17.3))


def test_biting_rate_zero_outside_limits():
    # DEVIATION #2
    assert biting_rate(p.T_0 - 1.0) == 0.0
    assert biting_rate(p.T_M + 1.0) == 0.0
    assert biting_rate(p.T_M) == 0.0


def test_incubation_rate_hand_value_27C():
    assert incubation_rate(27.0) == pytest.approx((27.0 - 16.0) / 111.0)


def test_incubation_rate_zero_below_T_min():
    # DEVIATION #3
    assert incubation_rate(p.T_MIN - 5.0) == 0.0


def test_vector_mortality_hand_value_25C():
    # 1 / (-4.4 + 1.31*25 - 0.03*625) = 1 / 9.6
    assert vector_mortality(25.0) == pytest.approx(1.0 / 9.6)


def test_vector_mortality_capped_where_denominator_negative():
    # DEVIATION #4: at 45 °C the denominator is -6.2 days
    assert vector_mortality(45.0) == pytest.approx(1.0 / p.Q_DEN_MIN)
    assert vector_mortality(0.0) == pytest.approx(1.0 / p.Q_DEN_MIN)


def test_synthetic_climate_ranges():
    c = make_synthetic_climate()
    assert len(c.temperature) == p.N_DAYS
    assert c.temperature.min() >= p.T_MEAN - p.T_AMP - 1e-9
    assert c.temperature.max() <= p.T_MEAN + p.T_AMP + 1e-9
    assert (c.rainfall > 0).all()
    # monsoon (Jun-Sep, days 151-272) much wetter than Jan-Mar (days 0-89)
    assert c.rainfall[151:273].mean() > 10 * c.rainfall[0:90].mean()


def test_climate_interpolation_between_days():
    c = make_synthetic_climate()
    assert c.T_at(10.5) == pytest.approx(0.5 * (c.temperature[10] + c.temperature[11]))
