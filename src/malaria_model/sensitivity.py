"""SENSITIVITY ANALYSES - kept separate from the main results.

1. gamma_h x beta_hv (params.SENS_GAMMA_H x params.SENS_BETA_HV).
2. Importation rate (params.SENS_IMPORT): imported vs local attack rate.
Both report whether the ward ranking by Ω holds.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace

import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.config import ModelConfig
from malaria_model.drainage import clogging_index
from malaria_model.metrics import (
    attack_rate, imported_infections, local_infections, peak_infectious, per_1000,
)
from malaria_model.ode import simulate_reported_year


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


def _ward_rows(climate: Climate, config: ModelConfig, **labels: float) -> list[dict]:
    """Outcomes for every ward under config (serial: runtime param overrides apply)."""
    rows = []
    for name, (D_d, M_i) in p.WARDS.items():
        df = simulate_reported_year(clogging_index(D_d, M_i), climate, config).df
        rows.append({**labels, "ward": name, "Omega": clogging_index(D_d, M_i),
                     "peak I_h": peak_infectious(df), "attack rate /1000": attack_rate(df),
                     "local /1000": per_1000(local_infections(df, climate), df),
                     "imported /1000": per_1000(imported_infections(df, config.import_rate), df)})
    return rows


def run_sensitivity(climate: Climate, config: ModelConfig) -> pd.DataFrame:
    """One row per (gamma_h [1/day], beta_hv [-], ward): peak I_h [humans], attack rate
    [per 1,000] and the ward's rank by attack rate (1 = most infections)."""
    rows = []
    for gamma_h in p.SENS_GAMMA_H:
        for beta_hv in p.SENS_BETA_HV:
            with override_params(GAMMA_H=gamma_h, BETA_HV=beta_hv):
                rows += _ward_rows(climate, config, gamma_h=gamma_h, beta_hv=beta_hv)
    table = pd.DataFrame(rows)
    table["rank"] = (table.groupby(["gamma_h", "beta_hv"])["attack rate /1000"]
                     .rank(ascending=False).astype(int))
    return table


def run_import_sensitivity(climate: Climate, config: ModelConfig) -> pd.DataFrame:
    """One row per (import rate [per 1,000/yr], ward): total, local and imported attack rate."""
    rows = []
    for rate in p.SENS_IMPORT:
        rows += _ward_rows(climate, replace(config, import_per_1000_per_year=rate),
                           import_per_1000=rate)
    return pd.DataFrame(rows)


def ranking_follows_omega(table: pd.DataFrame, by: list[str],
                          column: str = "attack rate /1000") -> pd.DataFrame:
    """Per group in `by`: True if higher Omega always gives a higher `column`."""
    def ordered(group: pd.DataFrame) -> bool:
        return bool(group.sort_values("Omega")[column].is_monotonic_increasing)

    return (table.groupby(by)[["Omega", column]].apply(ordered)
            .rename(f"higher Omega => higher {column}").reset_index())
