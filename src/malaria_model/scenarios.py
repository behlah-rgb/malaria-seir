"""Run the three illustrative ward profiles defined in params.WARDS."""

from __future__ import annotations

import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.config import ModelConfig
from malaria_model.drainage import clogging_index
from malaria_model.metrics import (
    annual_eir, attack_rate, day_of_peak, imported_infections, local_infections,
    peak_infectious, per_1000, vectors_per_human,
)
from malaria_model.ode import SpinupResult, simulate_reported_year
from malaria_model.r0 import r0_series


def run_wards(climate: Climate, config: ModelConfig) -> dict[str, SpinupResult]:
    """Simulate every ward in params.WARDS under `config`; return the reported year.

    climate: one year of daily T [°C] and R [mm/day].
    Each result's df holds compartments [individuals] by day, plus R0 [-].
    """
    results = {}
    for name, (D_d, M_i) in p.WARDS.items():
        result = simulate_reported_year(clogging_index(D_d, M_i), climate, config)
        result.df["R0"] = r0_series(result.df, climate)
        results[name] = result
    return results


def ward_row(name: str, result: SpinupResult, climate: Climate, config: ModelConfig) -> dict:
    """All reported quantities for one ward (units in the column names / docstrings)."""
    df = result.df
    D_d, M_i = p.WARDS[name]
    m = vectors_per_human(df)
    return {
        "scenario": name,
        "Omega": clogging_index(D_d, M_i),
        "mosq/human mean": m.mean(),
        "mosq/human peak": m.max(),
        "EIR /yr": annual_eir(df, climate),
        "attack /1000": attack_rate(df),
        "local /1000": per_1000(local_infections(df, climate), df),
        "imported /1000": per_1000(imported_infections(df, config.import_rate), df),
        "peak I_h": peak_infectious(df),
        "day of peak": day_of_peak(df),
        "growth (local)": result.growth_factor,
        "R0 max": df["R0"].max(),
        "R0 mean": df["R0"].mean(),
        "spin-up yrs": result.years_run,
        "converged": result.converged,
    }


def summary_table(results: dict[str, SpinupResult], climate: Climate,
                  config: ModelConfig) -> pd.DataFrame:
    """One row per ward; see ward_row() for the columns."""
    return pd.DataFrame([ward_row(n, r, climate, config) for n, r in results.items()])
