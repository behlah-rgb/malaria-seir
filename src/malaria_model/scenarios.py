"""Run the three illustrative ward profiles defined in params.WARDS."""

from __future__ import annotations

import pandas as pd

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, day_of_peak, peak_infectious
from malaria_model.ode import simulate_with_spinup
from malaria_model.r0 import r0_series


def run_wards(climate: Climate) -> dict[str, pd.DataFrame]:
    """Simulate every ward in params.WARDS with spin-up; return the reported year.

    climate: one year of daily T [°C] and R [mm/day].
    Returns {ward name: DataFrame of compartments [individuals] by day, plus R0 [-]}.
    """
    results = {}
    for name, (D_d, M_i) in p.WARDS.items():
        df = simulate_with_spinup(clogging_index(D_d, M_i), climate)
        df["R0"] = r0_series(df, climate)
        results[name] = df
    return results


def summary_table(results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """One row per ward with Omega [-], peak I_h [humans], day of peak, attack rate
    [per 1,000], max R0(t) [-], days with R0 > 1 and peak adult mosquitoes."""
    rows = []
    for name, df in results.items():
        D_d, M_i = p.WARDS[name]
        rows.append({
            "scenario": name,
            "Omega": clogging_index(D_d, M_i),
            "peak I_h": peak_infectious(df),
            "day of peak": day_of_peak(df),
            "attack rate /1000": attack_rate(df),
            "max R0(t)": df["R0"].max(),
            "days R0>1": int((df["R0"] > p.R0_THRESHOLD).sum()),
            "peak adult mosq.": df["N_v"].max(),
        })
    return pd.DataFrame(rows)
