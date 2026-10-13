"""Run the three illustrative ward profiles defined in params.WARDS."""

from __future__ import annotations

import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.drainage import clogging_index
from malaria_model.ode import simulate


def run_wards(climate: Climate) -> dict[str, pd.DataFrame]:
    """Simulate every ward in params.WARDS for the length of `climate` [days].

    Returns {ward name: DataFrame of compartments [individuals] by day}.
    """
    return {
        name: simulate(clogging_index(D_d, M_i), climate)
        for name, (D_d, M_i) in p.WARDS.items()
    }


def summary_table(results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summary per ward: D_d [-], M_i [-], Omega [-], peak I_h [humans], day of peak [day]."""
    rows = []
    for name, df in results.items():
        D_d, M_i = p.WARDS[name]
        rows.append({
            "scenario": name,
            "D_d": D_d,
            "M_i": M_i,
            "Omega": clogging_index(D_d, M_i),
            "peak I_h": df["I_h"].max(),
            "day of peak": int(df["I_h"].idxmax()),
            "peak adult mosquitoes": df["N_v"].max(),
        })
    return pd.DataFrame(rows)
