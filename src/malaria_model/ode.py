"""The 8-compartment SEIR-Vector ODE system (docs/SPEC.md §5).

State order: [A_v, S_v, E_v, I_v, S_h, E_h, I_h, R_h], all in individuals.
Time t in days. The right-hand side returns derivatives in individuals/day.

Two variants (see config.py):
  spec     - equations exactly as in SPEC (plus the approved guards #1-#4);
  extended - K_v driven by rainfall with memory R_eff (#6), and imported
             infections S_h -> E_h (#8).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.integrate import odeint

from malaria_model import params as p
from malaria_model.climate import (
    Climate, biting_rate, effective_rainfall, incubation_rate, vector_mortality,
)
from malaria_model.config import ModelConfig, spec_config
from malaria_model.drainage import carrying_capacity, larval_mortality
from malaria_model.metrics import local_infections

STATE_NAMES: list[str] = ["A_v", "S_v", "E_v", "I_v", "S_h", "E_h", "I_h", "R_h"]


# ---------------------------------------------------------------------------
# Climate forcing seen by the equations
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Forcing:
    """Daily inputs to the ODE, repeating with period len(temperature) [days].

    temperature [°C]; rain_for_K [mm/day] drives K_v; rain_for_flush [mm/day]
    drives larval flushing. In the spec variant both rain series are R(t).
    """

    temperature: np.ndarray
    rain_for_K: np.ndarray
    rain_for_flush: np.ndarray

    def at(self, t: float) -> tuple[float, float, float]:
        """(T [°C], R for K_v [mm/day], R for flushing [mm/day]) at time t [days].

        Linear interpolation between days; after the last day the series wraps
        to day 0, so the climate repeats every period.
        """
        n = len(self.temperature)
        tm = t % n
        i = int(tm)
        j = (i + 1) % n
        f = tm - i
        return (
            self.temperature[i] + f * (self.temperature[j] - self.temperature[i]),
            self.rain_for_K[i] + f * (self.rain_for_K[j] - self.rain_for_K[i]),
            self.rain_for_flush[i] + f * (self.rain_for_flush[j] - self.rain_for_flush[i]),
        )


def build_forcing(climate: Climate, omega: float, config: ModelConfig) -> Forcing:
    """Daily forcing for a ward with clogging index omega [-] under `config`."""
    rain = climate.rainfall
    if not config.is_extended:
        return Forcing(climate.temperature, rain, rain)
    # DEVIATION: K_v uses rainfall with memory R_eff (floored at R_EFF_MIN), see DEVIATIONS.md #6
    r_eff = np.maximum(effective_rainfall(rain, config.tau(omega)), p.R_EFF_MIN)
    return Forcing(climate.temperature, r_eff, rain)


# ---------------------------------------------------------------------------
# Right-hand side
# ---------------------------------------------------------------------------
def vector_rhs(
    A_v: float, S_v: float, E_v: float, I_v: float, I_h: float, N_h: float,
    T: float, R_K: float, R_flush: float, omega: float, k0: float | None = None,
) -> tuple[float, float, float, float]:
    """Derivatives of the vector compartments [mosquitoes/day].

    Inputs: populations [individuals], T [°C], R_K = rain driving K_v [mm/day],
    R_flush = rain driving flushing [mm/day], omega [-], k0 = K_0 [mosquitoes/(mm/day)].
    Returns (dA_v/dt, dS_v/dt, dE_v/dt, dI_v/dt).
    """
    a = biting_rate(T)
    mu_v = vector_mortality(T)
    gamma_m = incubation_rate(T)
    K_v = carrying_capacity(R_K, omega, k0)
    mu_A = larval_mortality(R_flush, omega)
    N_v = S_v + E_v + I_v
    infection = a * p.BETA_VH * (I_h / N_h) * S_v  # new vector infections [mosquitoes/day]

    dA_v = p.PHI_V * (1.0 - A_v / K_v) * N_v - (p.THETA_A + mu_A) * A_v
    dS_v = p.THETA_A * A_v - infection - mu_v * S_v
    dE_v = infection - (gamma_m + mu_v) * E_v
    dI_v = gamma_m * E_v - mu_v * I_v
    return dA_v, dS_v, dE_v, dI_v


def human_rhs(
    S_h: float, E_h: float, I_h: float, R_h: float, I_v: float, T: float,
    import_rate: float = 0.0,
) -> tuple[float, float, float, float]:
    """Derivatives of the human compartments [humans/day].

    Inputs: populations [individuals], T [°C], import_rate [1/day] (0 in spec).
    Returns (dS_h/dt, dE_h/dt, dI_h/dt, dR_h/dt).
    """
    N_h = S_h + E_h + I_h + R_h
    infection = biting_rate(T) * p.BETA_HV * (I_v / N_h) * S_h  # new human infections [humans/day]
    # DEVIATION: imported infections move S_h -> E_h (0 in spec), see DEVIATIONS.md #8
    imported = import_rate * S_h  # [humans/day]

    dS_h = p.LAMBDA_H - infection - imported - p.MU_H * S_h + p.RHO * R_h
    dE_h = infection + imported - (p.ALPHA_H + p.MU_H) * E_h
    dI_h = p.ALPHA_H * E_h - (p.GAMMA_H + p.MU_H + p.DELTA_H) * I_h
    dR_h = p.GAMMA_H * I_h - (p.RHO + p.MU_H) * R_h
    return dS_h, dE_h, dI_h, dR_h


def rhs(y: np.ndarray, t: float, omega: float, forcing: Forcing,
        k0: float, import_rate: float) -> list[float]:
    """Full right-hand side for scipy.integrate.odeint.

    y: state [individuals] in STATE_NAMES order; t: time [days]; omega [-];
    forcing: daily T [°C] and rain [mm/day]; k0 [mosquitoes/(mm/day)];
    import_rate [1/day]. Returns the 8 derivatives [individuals/day].
    """
    A_v, S_v, E_v, I_v, S_h, E_h, I_h, R_h = y
    T, R_K, R_flush = forcing.at(t)
    N_h = S_h + E_h + I_h + R_h
    vector = vector_rhs(A_v, S_v, E_v, I_v, I_h, N_h, T, R_K, R_flush, omega, k0)
    human = human_rhs(S_h, E_h, I_h, R_h, I_v, T, import_rate)
    return [*vector, *human]


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def initial_state(omega: float, climate: Climate, config: ModelConfig | None = None) -> np.ndarray:
    """Initial state [individuals] for a ward with clogging index omega [-].

    Larvae start at the day-0 carrying capacity; adults start at the level
    that larval maturation alone would sustain (theta_A * A_v / mu_v).
    """
    config = config or spec_config()
    forcing = build_forcing(climate, omega, config)
    A_v0 = carrying_capacity(forcing.rain_for_K[0], omega, config.k0)
    S_v0 = p.THETA_A * A_v0 / vector_mortality(forcing.temperature[0])
    S_h0 = p.N_H0 - p.E_H0 - p.I_H0 - p.R_H0
    return np.array([A_v0, S_v0, p.E_V0, p.I_V0, S_h0, p.E_H0, p.I_H0, p.R_H0])


def simulate(omega: float, climate: Climate, y0: np.ndarray | None = None,
             config: ModelConfig | None = None, include_end: bool = False) -> pd.DataFrame:
    """Integrate the model over the climate's length with odeint.

    omega: clogging index [-]; climate: daily T [°C] and R [mm/day];
    y0: optional initial state [individuals]; config: variant (default spec);
    include_end: also output day len(climate) (the first day of the next period).
    Returns a DataFrame indexed by day [days] with one column per compartment,
    plus N_v (adult mosquitoes) and N_h (humans).
    """
    config = config or spec_config()
    if y0 is None:
        y0 = initial_state(omega, climate, config)
    n = len(climate.temperature)
    t = np.arange(n + 1 if include_end else n, dtype=float)
    forcing = build_forcing(climate, omega, config)
    sol = odeint(
        rhs, y0, t, args=(omega, forcing, config.k0, config.import_rate),
        hmax=p.ODE_HMAX, rtol=p.ODE_RTOL, atol=p.ODE_ATOL,
    )
    df = pd.DataFrame(sol, columns=STATE_NAMES, index=pd.Index(t, name="day"))
    df["N_v"] = df["S_v"] + df["E_v"] + df["I_v"]
    df["N_h"] = df["S_h"] + df["E_h"] + df["I_h"] + df["R_h"]
    return df


def simulate_with_spinup(omega: float, climate: Climate, n_years: int = p.N_YEARS_TOTAL,
                         config: ModelConfig | None = None) -> pd.DataFrame:
    """Simulate n_years with the one-year climate repeated; return only the last year.

    omega: clogging index [-]; climate: one year of daily T [°C] and R [mm/day].
    The returned DataFrame is re-indexed to days 0..len(climate)-1 of the reported year,
    so it has the same shape as simulate(omega, climate).
    """
    # DEVIATION: burn-in years run and discarded before the reported 365 days, see DEVIATIONS.md #5
    return _split_years(_simulate_tiled(omega, climate, n_years, config), climate)[-1]


def _simulate_tiled(omega: float, climate: Climate, n_years: int,
                    config: ModelConfig | None) -> pd.DataFrame:
    """One continuous odeint run over n_years of repeated climate [days 0..n_years*365-1]."""
    return simulate(omega, climate.repeat(n_years), initial_state(omega, climate, config), config)


def _split_years(full: pd.DataFrame, climate: Climate) -> list[pd.DataFrame]:
    """Cut a multi-year run into per-year DataFrames re-indexed to days 0..364."""
    n = len(climate.temperature)
    years = []
    for k in range(len(full) // n):
        year = full.iloc[k * n:(k + 1) * n].copy()
        year.index = pd.Index(climate.days, name="day")
        years.append(year)
    return years


@dataclass
class SpinupResult:
    """Reported year plus spin-up diagnostics.

    df: reported year, days 0..364; years_run: total years simulated;
    converged: local attack rate changed < SPINUP_TOL in the last year;
    growth_factor: local new infections, reported year / previous year [-].
    """

    df: pd.DataFrame
    years_run: int
    converged: bool
    growth_factor: float


def _growth(current: float, previous: float) -> float:
    """Year-over-year ratio of local infections [-]; 1.0 if both are zero."""
    if previous <= 0.0:
        return 1.0 if current <= 0.0 else float("inf")
    return current / previous


def simulate_converged(omega: float, climate: Climate, config: ModelConfig) -> SpinupResult:
    """Simulate year by year until LOCAL infections change < SPINUP_TOL (cap SPINUP_MAX_YEARS).

    Each year starts from the previous year's end state; the climate repeats.
    """
    # DEVIATION: spin-up repeated until local incidence converges (cap 20 yr), see DEVIATIONS.md #9
    y = initial_state(omega, climate, config)
    previous_local = None
    growth = float("nan")
    for year in range(1, p.SPINUP_MAX_YEARS + 1):
        full = simulate(omega, climate, y, config, include_end=True)
        y = full[STATE_NAMES].iloc[-1].to_numpy()
        df = full.iloc[:-1]
        local = local_infections(df, climate)
        if previous_local is not None:
            growth = _growth(local, previous_local)
            if abs(growth - 1.0) < p.SPINUP_TOL:
                return SpinupResult(df, year, True, growth)
        previous_local = local
    return SpinupResult(df, p.SPINUP_MAX_YEARS, False, growth)


def simulate_reported_year(omega: float, climate: Climate, config: ModelConfig) -> SpinupResult:
    """Run the spin-up chosen in config ("fixed" #5 or "converge" #9); return the reported year."""
    if config.spinup == "converge":
        return simulate_converged(omega, climate, config)
    years = _split_years(_simulate_tiled(omega, climate, p.N_YEARS_TOTAL, config), climate)
    growth = _growth(local_infections(years[-1], climate), local_infections(years[-2], climate))
    return SpinupResult(years[-1], p.N_YEARS_TOTAL, abs(growth - 1.0) < p.SPINUP_TOL, growth)
