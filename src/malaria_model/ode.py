"""The 8-compartment SEIR-Vector ODE system (docs/SPEC.md §5).

State order: [A_v, S_v, E_v, I_v, S_h, E_h, I_h, R_h], all in individuals.
Time t in days. The right-hand side returns derivatives in individuals/day.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import odeint

from malaria_model import params as p
from malaria_model.climate import Climate, biting_rate, incubation_rate, vector_mortality
from malaria_model.drainage import carrying_capacity, larval_mortality

STATE_NAMES: list[str] = ["A_v", "S_v", "E_v", "I_v", "S_h", "E_h", "I_h", "R_h"]


def vector_rhs(
    A_v: float, S_v: float, E_v: float, I_v: float, I_h: float, N_h: float,
    T: float, R: float, omega: float,
) -> tuple[float, float, float, float]:
    """Derivatives of the vector compartments [mosquitoes/day].

    Inputs: populations [individuals], T [°C], R [mm/day], omega [-].
    Returns (dA_v/dt, dS_v/dt, dE_v/dt, dI_v/dt).
    """
    a = biting_rate(T)
    mu_v = vector_mortality(T)
    gamma_m = incubation_rate(T)
    K_v = carrying_capacity(R, omega)
    mu_A = larval_mortality(R, omega)
    N_v = S_v + E_v + I_v
    infection = a * p.BETA_VH * (I_h / N_h) * S_v  # new vector infections [mosquitoes/day]

    dA_v = p.PHI_V * (1.0 - A_v / K_v) * N_v - (p.THETA_A + mu_A) * A_v
    dS_v = p.THETA_A * A_v - infection - mu_v * S_v
    dE_v = infection - (gamma_m + mu_v) * E_v
    dI_v = gamma_m * E_v - mu_v * I_v
    return dA_v, dS_v, dE_v, dI_v


def human_rhs(
    S_h: float, E_h: float, I_h: float, R_h: float, I_v: float, T: float,
) -> tuple[float, float, float, float]:
    """Derivatives of the human compartments [humans/day].

    Inputs: populations [individuals], T [°C].
    Returns (dS_h/dt, dE_h/dt, dI_h/dt, dR_h/dt).
    """
    N_h = S_h + E_h + I_h + R_h
    infection = biting_rate(T) * p.BETA_HV * (I_v / N_h) * S_h  # new human infections [humans/day]

    dS_h = p.LAMBDA_H - infection - p.MU_H * S_h + p.RHO * R_h
    dE_h = infection - (p.ALPHA_H + p.MU_H) * E_h
    dI_h = p.ALPHA_H * E_h - (p.GAMMA_H + p.MU_H + p.DELTA_H) * I_h
    dR_h = p.GAMMA_H * I_h - (p.RHO + p.MU_H) * R_h
    return dS_h, dE_h, dI_h, dR_h


def rhs(y: np.ndarray, t: float, omega: float, climate: Climate) -> list[float]:
    """Full right-hand side for scipy.integrate.odeint.

    y: state [individuals] in STATE_NAMES order; t: time [days];
    omega: clogging index [-]; climate: supplies T(t) [°C] and R(t) [mm/day].
    Returns the 8 derivatives [individuals/day].
    """
    A_v, S_v, E_v, I_v, S_h, E_h, I_h, R_h = y
    T = climate.T_at(t)
    R = climate.R_at(t)
    N_h = S_h + E_h + I_h + R_h
    vector = vector_rhs(A_v, S_v, E_v, I_v, I_h, N_h, T, R, omega)
    human = human_rhs(S_h, E_h, I_h, R_h, I_v, T)
    return [*vector, *human]


def initial_state(omega: float, climate: Climate) -> np.ndarray:
    """Initial state [individuals] for a ward with clogging index omega [-].

    Larvae start at the day-0 carrying capacity; adults start at the level
    that larval maturation alone would sustain (theta_A * A_v / mu_v).
    """
    A_v0 = carrying_capacity(climate.R_at(0.0), omega)
    S_v0 = p.THETA_A * A_v0 / vector_mortality(climate.T_at(0.0))
    S_h0 = p.N_H0 - p.E_H0 - p.I_H0 - p.R_H0
    return np.array([A_v0, S_v0, p.E_V0, p.I_V0, S_h0, p.E_H0, p.I_H0, p.R_H0])


def simulate(omega: float, climate: Climate, y0: np.ndarray | None = None) -> pd.DataFrame:
    """Integrate the model over the climate's length with odeint.

    omega: clogging index [-]; climate: daily T [°C] and R [mm/day];
    y0: optional initial state [individuals] (default: initial_state()).
    Returns a DataFrame indexed by day [days] with one column per compartment,
    plus N_v (adult mosquitoes) and N_h (humans).
    """
    if y0 is None:
        y0 = initial_state(omega, climate)
    t = climate.days
    sol = odeint(
        rhs, y0, t, args=(omega, climate),
        hmax=p.ODE_HMAX, rtol=p.ODE_RTOL, atol=p.ODE_ATOL,
    )
    df = pd.DataFrame(sol, columns=STATE_NAMES, index=pd.Index(t, name="day"))
    df["N_v"] = df["S_v"] + df["E_v"] + df["I_v"]
    df["N_h"] = df["S_h"] + df["E_h"] + df["I_h"] + df["R_h"]
    return df
