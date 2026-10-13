"""SENSITIVITY ANALYSIS - kept separate from the main results.

Re-runs the three wards with gamma_h and beta_hv set to each combination of
params.SENS_GAMMA_H x params.SENS_BETA_HV, then restores the original values.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, peak_infectious
from malaria_model.ode import simulate_with_spinup


@contextmanager
def override_params(**values: float) -> Iterator[None]:
    """Temporarily set params.NAME = value for each keyword; always restore afterwards."""
    original = {name: getattr(p, name) for name in values}
    try:
        for name, value in values.items():
            setattr(p, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(p, name, value)


def run_sensitivity(climate: Climate) -> pd.DataFrame:
    """One row per (gamma_h [1/day], beta_hv [-], ward): peak I_h [humans] (year 3),
    attack rate [per 1,000] and the ward's rank by attack rate (1 = most infections)."""
    rows = []
    for gamma_h in p.SENS_GAMMA_H:
        for beta_hv in p.SENS_BETA_HV:
            with override_params(GAMMA_H=gamma_h, BETA_HV=beta_hv):
                for name, (D_d, M_i) in p.WARDS.items():
                    df = simulate_with_spinup(clogging_index(D_d, M_i), climate)
                    rows.append({"gamma_h": gamma_h, "beta_hv": beta_hv, "ward": name,
                                 "Omega": clogging_index(D_d, M_i),
                                 "peak I_h": peak_infectious(df),
                                 "attack rate /1000": attack_rate(df)})
    table = pd.DataFrame(rows)
    table["rank"] = (table.groupby(["gamma_h", "beta_hv"])["attack rate /1000"]
                     .rank(ascending=False).astype(int))
    return table


def ranking_follows_omega(table: pd.DataFrame) -> pd.DataFrame:
    """Per (gamma_h, beta_hv): True if higher Omega always gives a higher attack rate."""
    def ordered(group: pd.DataFrame) -> bool:
        return bool(group.sort_values("Omega")["attack rate /1000"].is_monotonic_increasing)

    return (table.groupby(["gamma_h", "beta_hv"])[["Omega", "attack rate /1000"]]
            .apply(ordered).rename("high Omega = more infections").reset_index())
