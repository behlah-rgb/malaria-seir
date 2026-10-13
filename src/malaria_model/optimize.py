"""Sweep drainage density D_d and maintenance M_i; record peak I_h and attack rate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, peak_infectious
from malaria_model.ode import simulate_with_spinup
from malaria_model.plotting import heatmap_figure


def metric_grids(climate: Climate,
                 resolution: int = p.GRID_RESOLUTION) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Peak I_h [humans] and attack rate [per 1,000] over a D_d x M_i grid (reported year).

    D_d and M_i [-] each run from GRID_MIN to GRID_MAX with `resolution` points.
    Returns (peak grid, attack-rate grid); rows = M_i, columns = D_d.
    """
    values = np.round(np.linspace(p.GRID_MIN, p.GRID_MAX, resolution), 3)
    index = pd.Index(values, name="M_i")
    columns = pd.Index(values, name="D_d")
    peak = pd.DataFrame(index=index, columns=columns, dtype=float)
    attack = pd.DataFrame(index=index, columns=columns, dtype=float)
    for M_i in values:
        for D_d in values:
            df = simulate_with_spinup(clogging_index(D_d, M_i), climate)
            peak.loc[M_i, D_d] = peak_infectious(df)
            attack.loc[M_i, D_d] = attack_rate(df)
    return peak, attack


def run_sweep(climate: Climate, out_dir: Path,
              resolution: int = p.GRID_RESOLUTION) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute both grids and save one Seaborn heatmap per metric into out_dir (PNG)."""
    peak, attack = metric_grids(climate, resolution)
    heatmap_figure(peak, "Peak infectious humans, max I_h(t) (primary metric, year 3)",
                   "Peak I_h (humans)", out_dir / "heatmap_peak_Ih.png")
    heatmap_figure(attack, "New infections per 1,000 people in year 3 (supplementary metric)",
                   "Attack rate per 1,000", out_dir / "heatmap_attack_rate.png")
    return peak, attack
