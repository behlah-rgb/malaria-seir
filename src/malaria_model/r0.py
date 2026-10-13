"""Basic reproduction number from the next-generation matrix (NGM).

For this model the NGM has two non-zero entries:
  K_hv = humans infected by one infectious mosquito over its life
       = a(T) * beta_hv / mu_v(T) * alpha_h / (alpha_h + mu_h)
  K_vh = mosquitoes infected by one infectious human over their infectious period
       = a(T) * beta_vh * (N_v / N_h) / (gamma_h + mu_h + delta_h)
         * gamma_m(T) / (gamma_m(T) + mu_v(T))
and R0 = sqrt(K_hv * K_vh) (spectral radius). Some texts report R0^2 instead.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate, biting_rate, incubation_rate, vector_mortality


def ngm_r0(T: float, vectors_per_human: float) -> float:
    """R0 [-] at temperature T [°C] and mosquito:human ratio N_v/N_h [-]."""
    a = biting_rate(T)
    mu_v = vector_mortality(T)
    gamma_m = incubation_rate(T)
    K_hv = a * p.BETA_HV / mu_v * p.ALPHA_H / (p.ALPHA_H + p.MU_H)
    K_vh = (a * p.BETA_VH * vectors_per_human / (p.GAMMA_H + p.MU_H + p.DELTA_H)
            * gamma_m / (gamma_m + mu_v))
    return float(np.sqrt(K_hv * K_vh))


def r0_series(df: pd.DataFrame, climate: Climate) -> pd.Series:
    """R0(t) [-] for each day, using T(t) [°C] and the simulated N_v(t)/N_h(t)."""
    values = [ngm_r0(climate.T_at(t), df.loc[t, "N_v"] / df.loc[t, "N_h"]) for t in df.index]
    return pd.Series(values, index=df.index, name="R0")
