"""Ω-focused analysis: R0 versus Ω, critical Ω*, persistence threshold, minimum maintenance."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.config import ModelConfig
from malaria_model.ode import simulate_reported_year, simulate_with_spinup
from malaria_model.parallel import parallel_map
from malaria_model.r0 import r0_series


def r0_stats(omega: float, climate: Climate, config: ModelConfig) -> tuple[float, float]:
    """(max, mean) of R0(t) [-] over a year once vector dynamics have settled.

    Vector numbers do not depend on infection, so VECTOR_SPINUP_YEARS of
    burn-in is enough; the year after that is used.
    """
    df = simulate_with_spinup(omega, climate, p.VECTOR_SPINUP_YEARS + 1, config)
    r0 = r0_series(df, climate)
    return float(r0.max()), float(r0.mean())


def _r0_task(task: tuple[float, Climate, ModelConfig]) -> tuple[float, float, float]:
    """(omega, max R0, mean R0) for one Ω (top-level for worker processes)."""
    omega, climate, config = task
    return (omega, *r0_stats(omega, climate, config))


def r0_curve(climate: Climate, config: ModelConfig, workers: int = p.N_WORKERS) -> pd.DataFrame:
    """Max and mean R0(t) [-] over log-spaced Ω from OMEGA_CURVE_MIN to OMEGA_SEARCH_MAX."""
    omegas = np.geomspace(p.OMEGA_CURVE_MIN, p.OMEGA_SEARCH_MAX, p.OMEGA_CURVE_POINTS)
    rows = parallel_map(_r0_task, [(o, climate, config) for o in omegas], workers)
    return pd.DataFrame(rows, columns=["Omega", "R0 max", "R0 mean"])


@dataclass
class CriticalOmega:
    """Critical clogging index Ω* where max_t R0(t) = 1.

    value: Ω* [-] or None; status: "found", "none safe" (R0 > 1 even at the lowest Ω)
    or "all safe" (R0 < 1 even at the highest Ω searched).
    """

    value: float | None
    status: str


def critical_omega(climate: Climate, config: ModelConfig) -> CriticalOmega:
    """Find Ω* in [OMEGA_SEARCH_MIN, OMEGA_SEARCH_MAX] with max_t R0(t; Ω*) = R0_THRESHOLD."""
    def excess(omega: float) -> float:
        return r0_stats(omega, climate, config)[0] - p.R0_THRESHOLD

    low, high = excess(p.OMEGA_SEARCH_MIN), excess(p.OMEGA_SEARCH_MAX)
    if low >= 0:
        return CriticalOmega(None, "none safe")
    if high <= 0:
        return CriticalOmega(None, "all safe")
    return CriticalOmega(brentq(excess, p.OMEGA_SEARCH_MIN, p.OMEGA_SEARCH_MAX, xtol=1e-3), "found")


def min_maintenance(omega_star: float, D_d: np.ndarray | float) -> np.ndarray | float:
    """Smallest M_i [-] keeping Ω <= Ω* at drainage density D_d [-].

    From Ω = (1 - M_i)/(D_d + ε) <= Ω*  =>  M_i >= 1 - Ω*·(D_d + ε), clipped to [0, 1].
    """
    return np.clip(1.0 - omega_star * (np.asarray(D_d) + p.EPSILON), 0.0, 1.0)


def local_growth(omega: float, climate: Climate, config: ModelConfig) -> float:
    """Year-over-year growth factor [-] of LOCAL infections with importation switched off.

    Uses the fixed spin-up (years N_YEARS_TOTAL-1 -> N_YEARS_TOTAL); the ratio settles
    within a few years because it is set by the linearised yearly cycle.
    """
    no_import = replace(config, import_per_1000_per_year=0.0, spinup="fixed")
    return simulate_reported_year(omega, climate, no_import).growth_factor


def persistence_omega(climate: Climate, config: ModelConfig) -> CriticalOmega:
    """Ω where local infections neither grow nor shrink year to year (growth factor = 1).

    Stricter than Ω*: peak R0(t) > 1 for a few days is not enough for infection to persist.
    """
    def excess(omega: float) -> float:
        return local_growth(omega, climate, config) - 1.0

    low, high = excess(p.OMEGA_SEARCH_MIN), excess(p.OMEGA_SEARCH_MAX)
    if low >= 0:
        return CriticalOmega(None, "none safe")
    if high <= 0:
        return CriticalOmega(None, "all safe")
    return CriticalOmega(brentq(excess, p.OMEGA_SEARCH_MIN, p.OMEGA_SEARCH_MAX, xtol=1e-3), "found")
