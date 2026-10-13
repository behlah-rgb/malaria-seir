"""Sweep drainage density D_d and maintenance M_i; record outcomes per grid cell."""

from __future__ import annotations

import numpy as np
import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.config import ModelConfig
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, local_infections, peak_infectious, per_1000
from malaria_model.ode import simulate_reported_year
from malaria_model.parallel import parallel_map


def grid_values(resolution: int = p.GRID_RESOLUTION) -> np.ndarray:
    """D_d and M_i values [-] of the sweep, GRID_MIN..GRID_MAX."""
    return np.round(np.linspace(p.GRID_MIN, p.GRID_MAX, resolution), 3)


def _grid_cell(task: tuple[float, float, Climate, ModelConfig]) -> dict:
    """Outcomes for one (D_d, M_i) cell (top-level so worker processes can run it)."""
    D_d, M_i, climate, config = task
    omega = clogging_index(D_d, M_i)
    result = simulate_reported_year(omega, climate, config)
    df = result.df
    return {"D_d": D_d, "M_i": M_i, "Omega": omega,
            "peak I_h": peak_infectious(df), "attack /1000": attack_rate(df),
            "local /1000": per_1000(local_infections(df, climate), df),
            "converged": result.converged, "spin-up yrs": result.years_run}


def sweep(climate: Climate, config: ModelConfig, resolution: int = p.GRID_RESOLUTION,
          workers: int = p.N_WORKERS) -> pd.DataFrame:
    """One row per grid cell (resolution² cells) with Omega and outcomes for `config`."""
    values = grid_values(resolution)
    tasks = [(D_d, M_i, climate, config) for M_i in values for D_d in values]
    return pd.DataFrame(parallel_map(_grid_cell, tasks, workers))


def to_grid(cells: pd.DataFrame, column: str) -> pd.DataFrame:
    """Pivot a sweep result to rows = M_i, columns = D_d for one outcome column."""
    return cells.pivot(index="M_i", columns="D_d", values=column)
