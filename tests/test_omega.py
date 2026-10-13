"""Tests for the Ω analysis: minimum maintenance and critical Ω*."""

import numpy as np
import pytest

from malaria_model import params as p
from malaria_model.climate import make_synthetic_climate
from malaria_model.config import extended_config
from malaria_model.drainage import clogging_index
from malaria_model.omega_analysis import critical_omega, min_maintenance, r0_stats


def test_min_maintenance_hand_values():
    # M_i >= 1 - Ω*(D_d + ε)
    assert min_maintenance(1.0, 0.5) == pytest.approx(1 - 0.501)
    assert min_maintenance(0.1, 0.9) == pytest.approx(1 - 0.1 * 0.901)
    assert min_maintenance(10.0, 0.9) == 0.0  # clipped: any maintenance is enough
    assert min_maintenance(0.0, 0.5) == 1.0


def test_min_maintenance_lies_on_omega_star():
    D_d = np.array([0.2, 0.5, 0.8])
    M_i = min_maintenance(0.6, D_d)
    assert np.allclose([clogging_index(d, m) for d, m in zip(D_d, M_i)], 0.6)


def test_critical_omega_is_root():
    climate = make_synthetic_climate()
    config = extended_config(calibrated=False)
    star = critical_omega(climate, config)
    if star.value is None:
        pytest.skip(f"no root in search range ({star.status})")
    assert r0_stats(star.value, climate, config)[0] == pytest.approx(p.R0_THRESHOLD, abs=0.01)


def test_persistence_threshold_is_root_and_above_omega_star():
    from malaria_model.omega_analysis import local_growth, persistence_omega

    climate = make_synthetic_climate()
    config = extended_config(calibrated=False)
    persist = persistence_omega(climate, config)
    if persist.value is None:
        pytest.skip(f"no root in search range ({persist.status})")
    assert local_growth(persist.value, climate, config) == pytest.approx(1.0, abs=0.01)
    star = critical_omega(climate, config)
    if star.value is not None:
        assert persist.value > star.value  # persistence is the stricter (larger-Ω) threshold
