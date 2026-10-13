"""Outcome metrics computed from a simulated trajectory (no new ODE states)."""

from __future__ import annotations

import pandas as pd
from scipy.integrate import trapezoid

from malaria_model import params as p


def peak_infectious(df: pd.DataFrame) -> float:
    """Primary metric (SPEC §6 note 8): max over t of I_h(t) [humans]."""
    return float(df["I_h"].max())


def day_of_peak(df: pd.DataFrame) -> int:
    """Day [day of reported year] on which I_h is largest."""
    return int(df["I_h"].idxmax())


def new_infections(df: pd.DataFrame) -> float:
    """Cumulative new human infections [humans]: integral of alpha_h * E_h dt.

    alpha_h * E_h is the daily flow from E_h into I_h [humans/day]; the integral
    over the trajectory's days (trapezoid rule on daily output) gives the count.
    """
    return float(trapezoid(p.ALPHA_H * df["E_h"].to_numpy(), df.index.to_numpy()))


def attack_rate(df: pd.DataFrame) -> float:
    """Supplementary metric: new infections per PER_POPULATION people [per 1,000].

    Denominator is the human population N_h on the first day of the trajectory.
    """
    return p.PER_POPULATION * new_infections(df) / float(df["N_h"].iloc[0])
