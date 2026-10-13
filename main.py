"""Run the whole SEIR-Vector malaria demo: 3 wards, figures, heatmap, summary.

Usage:  python main.py
Figures are written to results/figures/.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))  # lets `python main.py` find the package without installing it

import pandas as pd  # noqa: E402

from malaria_model.climate import make_synthetic_climate  # noqa: E402
from malaria_model.optimize import run_sweep  # noqa: E402
from malaria_model.plotting import ward_figure  # noqa: E402
from malaria_model.scenarios import run_wards, summary_table  # noqa: E402

FIGURE_DIR = ROOT / "results" / "figures"


def main() -> None:
    """Run all scenarios, save figures, print the summary table."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    climate = make_synthetic_climate()

    results = run_wards(climate)
    ward_figure(results, "I_h", "Infectious humans I_h",
                "Infectious humans by ward (synthetic climate)",
                climate, FIGURE_DIR / "ward_infections.png")
    ward_figure(results, "N_v", "Adult mosquitoes S_v + E_v + I_v",
                "Adult mosquito density by ward (synthetic climate)",
                climate, FIGURE_DIR / "ward_vectors.png")

    start = time.perf_counter()
    run_sweep(climate, FIGURE_DIR / "heatmap_peak_Ih.png")
    sweep_seconds = time.perf_counter() - start

    pd.set_option("display.width", 120)
    table = summary_table(results)
    print("\nSummary (peak I_h = max over 365 days of infectious humans)")
    print(table.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print(f"\nHeatmap sweep took {sweep_seconds:.1f} s")
    print(f"Figures saved to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
