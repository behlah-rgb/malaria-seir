"""Sweep drainage density D_d and maintenance M_i; record peak I_h."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.drainage import clogging_index
from malaria_model.ode import simulate
from malaria_model.plotting import heatmap_figure


def peak_ih_grid(climate: Climate, resolution: int = p.GRID_RESOLUTION) -> pd.DataFrame:
    """Peak infectious humans max_t I_h(t) [humans] over a D_d x M_i grid.

    D_d and M_i [-] each run from GRID_MIN to GRID_MAX with `resolution` points.
    Returns a DataFrame: rows = M_i, columns = D_d, values = peak I_h.
    """
    values = np.round(np.linspace(p.GRID_MIN, p.GRID_MAX, resolution), 3)
    grid = pd.DataFrame(index=pd.Index(values, name="M_i"),
                        columns=pd.Index(values, name="D_d"), dtype=float)
    for M_i in values:
        for D_d in values:
            df = simulate(clogging_index(D_d, M_i), climate)
            grid.loc[M_i, D_d] = df["I_h"].max()
    return grid


def run_sweep(climate: Climate, out_path: Path,
              resolution: int = p.GRID_RESOLUTION) -> pd.DataFrame:
    """Compute the peak-I_h grid and save its Seaborn heatmap to out_path (PNG).

    Returns the grid (rows = M_i [-], columns = D_d [-], values = peak I_h [humans]).
    """
    grid = peak_ih_grid(climate, resolution)
    heatmap_figure(grid, out_path)
    return grid
