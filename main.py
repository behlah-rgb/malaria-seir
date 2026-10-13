"""Run the whole SEIR-Vector malaria demo: 3 wards, figures, heatmaps, summary,
then a separate sensitivity analysis.

Usage:  python main.py
Main figures go to results/figures/, sensitivity figures to results/figures/sensitivity/.
All results are for year 3 of a 3-year run (years 1-2 are burn-in, DEVIATIONS.md #5).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))  # lets `python main.py` find the package without installing it

from malaria_model import params as p  # noqa: E402
from malaria_model.climate import Climate, make_synthetic_climate  # noqa: E402
from malaria_model.optimize import run_sweep  # noqa: E402
from malaria_model.plotting import sensitivity_figure, ward_figure  # noqa: E402
from malaria_model.scenarios import run_wards, summary_table  # noqa: E402
from malaria_model.sensitivity import ranking_follows_omega, run_sensitivity  # noqa: E402

FIGURE_DIR = ROOT / "results" / "figures"
SENSITIVITY_DIR = FIGURE_DIR / "sensitivity"


def _fmt(x: float) -> str:
    """Format a table number: 3 significant figures, thousands separators."""
    return f"{x:,.3g}" if abs(x) < 1000 else f"{x:,.0f}"


def run_main_results(climate: Climate) -> None:
    """Ward figures, R0(t) figure, both heatmaps, and the summary table."""
    results = run_wards(climate)
    ward_figure(results, "I_h", "Infectious humans I_h",
                "Infectious humans by ward (year 3, synthetic climate)",
                climate, FIGURE_DIR / "ward_infections.png")
    ward_figure(results, "N_v", "Adult mosquitoes S_v + E_v + I_v",
                "Adult mosquito density by ward (year 3, synthetic climate)",
                climate, FIGURE_DIR / "ward_vectors.png")
    ward_figure(results, "R0", "R0(t), next-generation matrix",
                "Reproduction number R0(t) by ward (year 3); above 1 = transmission can grow",
                climate, FIGURE_DIR / "ward_R0.png", hline=p.R0_THRESHOLD)

    start = time.perf_counter()
    run_sweep(climate, FIGURE_DIR)
    sweep_seconds = time.perf_counter() - start

    print("\nMAIN RESULTS (year 3 after 2 burn-in years)")
    print(summary_table(results).to_string(index=False, float_format=_fmt))
    print(f"\nHeatmap sweep ({p.GRID_RESOLUTION}x{p.GRID_RESOLUTION}) took {sweep_seconds:.1f} s")


def run_sensitivity_analysis(climate: Climate) -> None:
    """Separate sensitivity analysis on gamma_h and beta_hv: table + figure."""
    SENSITIVITY_DIR.mkdir(parents=True, exist_ok=True)
    table = run_sensitivity(climate)
    sensitivity_figure(table, SENSITIVITY_DIR / "sensitivity_attack_rate.png")
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS (not main results): gamma_h x beta_hv, year 3")
    print("=" * 70)
    print(table.drop(columns="Omega").to_string(index=False, float_format=_fmt))
    print("\nDoes higher Omega always give more infections?")
    print(ranking_follows_omega(table).to_string(index=False))


def main() -> None:
    """Run main results, then the sensitivity analysis; save all figures."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    climate = make_synthetic_climate()
    run_main_results(climate)
    run_sensitivity_analysis(climate)
    print(f"\nFigures saved to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
