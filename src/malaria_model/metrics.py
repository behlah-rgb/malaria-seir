"""Outcome metrics computed from a simulated trajectory (no new ODE states)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import trapezoid

from malaria_model import params as p
from malaria_model.climate import Climate, biting_rate


def peak_infectious(df: pd.DataFrame) -> float:
    """Primary metric (SPEC §6 note 8): max over t of I_h(t) [humans]."""
    return float(df["I_h"].max())


def day_of_peak(df: pd.DataFrame) -> int:
    """Day [day of reported year] on which I_h is largest."""
    return int(df["I_h"].idxmax())


def new_infections(df: pd.DataFrame) -> float:
    """Cumulative new human infections [humans]: integral of alpha_h * E_h dt.

    This is the reported total (imported + local), counted as people becoming
    infectious. local_infections() + imported_infections() count the same people
    when they enter E_h; the two agree up to the change in E_h over the period.

    alpha_h * E_h is the daily flow from E_h into I_h [humans/day]; the integral
    over the trajectory's days (trapezoid rule on daily output) gives the count.
    """
    return float(trapezoid(p.ALPHA_H * df["E_h"].to_numpy(), df.index.to_numpy()))


def attack_rate(df: pd.DataFrame) -> float:
    """Supplementary metric: new infections per PER_POPULATION people [per 1,000].

    Denominator is the human population N_h on the first day of the trajectory.
    """
    return p.PER_POPULATION * new_infections(df) / float(df["N_h"].iloc[0])


def _integrate_daily(values: np.ndarray, df: pd.DataFrame) -> float:
    """Trapezoid integral of a daily series over the trajectory's days [value·day]."""
    return float(trapezoid(values, df.index.to_numpy()))


def _daily_biting_rate(df: pd.DataFrame, climate: Climate) -> np.ndarray:
    """a(T(t)) [bites/mosquito/day] on each output day of df."""
    return np.array([biting_rate(climate.T_at(t)) for t in df.index])


def local_infections(df: pd.DataFrame, climate: Climate) -> float:
    """Locally acquired human infections [humans]: integral of a(T)·beta_hv·(I_v/N_h)·S_h dt."""
    force = _daily_biting_rate(df, climate) * p.BETA_HV * df["I_v"] / df["N_h"]
    return _integrate_daily((force * df["S_h"]).to_numpy(), df)


def imported_infections(df: pd.DataFrame, import_rate: float) -> float:
    """Imported human infections [humans]: integral of import_rate·S_h dt (import_rate [1/day])."""
    return _integrate_daily(import_rate * df["S_h"].to_numpy(), df)


def per_1000(count: float, df: pd.DataFrame) -> float:
    """Convert a count [humans] to a rate per PER_POPULATION people (N_h on day 0)."""
    return p.PER_POPULATION * count / float(df["N_h"].iloc[0])


def annual_eir(df: pd.DataFrame, climate: Climate) -> float:
    """Entomological inoculation rate [infectious bites per person per year].

    Integral over the year of a(T)·I_v/N_h dt (= 365 × the mean daily EIR).
    """
    return _integrate_daily((_daily_biting_rate(df, climate) * df["I_v"] / df["N_h"]).to_numpy(), df)


def vectors_per_human(df: pd.DataFrame) -> pd.Series:
    """Adult mosquitoes per human N_v/N_h [-] on each day."""
    return df["N_v"] / df["N_h"]
