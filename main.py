"""Run the SEIR-Vector malaria demo for both model variants ("spec" and "extended").

Usage:
    python main.py                     # everything except calibration
    python main.py --calibrate TARGET  # calibrate K_0 to TARGET API per 1,000/yr, then stop

Main figures go to results/figures/, sensitivity figures to results/figures/sensitivity/.
Reported results are the final year of a spin-up (DEVIATIONS.md #5, #9).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))  # lets `python main.py` find the package without installing it

import pandas as pd  # noqa: E402

from malaria_model import params as p  # noqa: E402
from malaria_model.calibrate import calibrate_k0  # noqa: E402
from malaria_model.climate import Climate, make_synthetic_climate  # noqa: E402
from malaria_model.config import (  # noqa: E402
    ModelConfig, extended_config, headline_config, spec_config,
)
from malaria_model.omega_analysis import (  # noqa: E402
    CriticalOmega, critical_omega, min_maintenance, persistence_omega, r0_curve,
)
from malaria_model.optimize import grid_values, sweep, to_grid  # noqa: E402
from malaria_model.plotting import (  # noqa: E402
    heatmap_figure, omega_scatter_figure, r0_vs_omega_figure, sensitivity_figure,
    variant_comparison_figure, ward_figure,
)
from malaria_model.scenarios import run_wards, summary_table  # noqa: E402
from malaria_model.sensitivity import (  # noqa: E402
    ranking_follows_omega, run_import_sensitivity, run_sensitivity,
)

FIGURE_DIR = ROOT / "results" / "figures"
SENSITIVITY_DIR = FIGURE_DIR / "sensitivity"


def _fmt(x: float) -> str:
    """Format a table number: 3 significant figures, thousands separators."""
    return f"{x:,.3g}" if abs(x) < 1000 else f"{x:,.0f}"


def _banner(text: str) -> None:
    """Print a section heading."""
    print("\n" + "=" * 78 + f"\n{text}\n" + "=" * 78)


def _print_table(table: pd.DataFrame) -> None:
    """Print a DataFrame with compact number formatting."""
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(table.to_string(index=False, float_format=_fmt))


def run_ward_results(climate: Climate, variants: dict[str, ModelConfig]) -> dict:
    """Per-ward summary for every variant; ward figures for the headline variant."""
    runs = {}
    for label, config in variants.items():
        results = run_wards(climate, config)
        runs[label] = {name: r.df for name, r in results.items()}
        _banner(f"WARD RESULTS - {config.describe()}")
        _print_table(summary_table(results, climate, config))

    headline = headline_config()
    frames = runs[headline.variant]
    sub = headline.describe()
    ward_figure(frames, "I_h", "Infectious humans I_h", "Infectious humans by ward", sub,
                climate, FIGURE_DIR / "ward_infections.png")
    ward_figure(frames, "N_v", "Adult mosquitoes S_v + E_v + I_v", "Adult mosquitoes by ward",
                sub, climate, FIGURE_DIR / "ward_vectors.png")
    ward_figure(frames, "R0", "R0(t), next-generation matrix",
                "R0(t) by ward; above 1 = transmission can grow", sub, climate,
                FIGURE_DIR / "ward_R0.png", hline=p.R0_THRESHOLD)
    return runs


def run_omega_results(climate: Climate, variants: dict[str, ModelConfig]) -> None:
    """Critical Ω*, minimum maintenance, D_d x M_i heatmaps, Ω scatter, R0-vs-Ω curve."""
    stars: dict[str, CriticalOmega] = {}
    persist: dict[str, CriticalOmega] = {}
    cells: dict[str, pd.DataFrame] = {}
    curves: dict[str, pd.DataFrame] = {}
    for label, config in variants.items():
        stars[label] = critical_omega(climate, config)
        persist[label] = persistence_omega(climate, config)
        curves[label] = r0_curve(climate, config)
        cells[label] = sweep(climate, config)
        star = stars[label].value
        for column, name, cbar in [("peak I_h", "peak_Ih", "Peak I_h (humans)"),
                                   ("attack /1000", "attack_rate", "Attack rate per 1,000")]:
            heatmap_figure(to_grid(cells[label], column), f"{cbar} over D_d x M_i ({label})",
                           config.describe(), cbar,
                           FIGURE_DIR / f"heatmap_{label}_{name}.png", star)

    _banner("CRITICAL CLOGGING INDEX Ω* (peak R0(t) = 1) AND MINIMUM MAINTENANCE")
    d_vals = grid_values()
    for label, star in stars.items():
        print(f"{label:9s}: Ω* = {star.value:.4g}" if star.value is not None
              else f"{label:9s}: no Ω* in [{p.OMEGA_SEARCH_MIN}, {p.OMEGA_SEARCH_MAX}] "
                   f"({star.status})")
    print("\nStricter threshold: Ω where LOCAL infections persist (growth factor = 1, import off)")
    for label, star in persist.items():
        print(f"{label:9s}: Ω_persist = {star.value:.4g}" if star.value is not None
              else f"{label:9s}: none in search range ({star.status})")
    rows = {"D_d": d_vals}
    for label, star in stars.items():
        if star.value is not None:
            rows[f"min M_i, R0<1 ({label})"] = min_maintenance(star.value, d_vals)
    for label, star in persist.items():
        if star.value is not None:
            rows[f"min M_i, no growth ({label})"] = min_maintenance(star.value, d_vals)
    _print_table(pd.DataFrame(rows))

    _banner("GRID SWEEP: spin-up convergence per variant")
    for label, table in cells.items():
        print(f"{label:9s}: {int(table['converged'].sum())}/{len(table)} cells converged; "
              f"spin-up years min {table['spin-up yrs'].min()}, max {table['spin-up yrs'].max()}")

    subtitle = " | ".join(c.describe() for c in variants.values())
    omega_values = {label: s.value for label, s in stars.items()}
    omega_scatter_figure(cells, omega_values, subtitle, FIGURE_DIR / "omega_scatter.png")
    persist_values = {label: s.value for label, s in persist.items()}
    r0_vs_omega_figure(curves, omega_values, persist_values, subtitle,
                       FIGURE_DIR / "r0_vs_omega.png")


def run_comparison(climate: Climate, runs: dict) -> None:
    """Spec vs extended (and extended-calibrated, once K_0_CALIBRATED exists) figure."""
    labels = {"spec": spec_config().describe(),
              "extended": extended_config(calibrated=False).describe()}
    figure_runs = {labels["spec"]: runs["spec"], labels["extended"]: runs["extended"]}
    if p.K_0_CALIBRATED is not None:
        calibrated = extended_config(calibrated=True)
        figure_runs[calibrated.describe()] = {
            name: r.df for name, r in run_wards(climate, calibrated).items()}
    variant_comparison_figure(figure_runs, "Placeholder parameters; synthetic climate",
                              FIGURE_DIR / "variant_comparison.png")


def run_sensitivity_analyses(climate: Climate) -> None:
    """Separate sensitivity analyses (headline variant): gamma_h x beta_hv, and importation."""
    SENSITIVITY_DIR.mkdir(parents=True, exist_ok=True)
    config = headline_config()
    table = run_sensitivity(climate, config)
    sensitivity_figure(table, config.describe(), SENSITIVITY_DIR / "sensitivity_attack_rate.png")
    _banner(f"SENSITIVITY ANALYSIS (not main results): gamma_h x beta_hv - {config.describe()}")
    _print_table(table.drop(columns="Omega"))
    _print_table(ranking_follows_omega(table, ["gamma_h", "beta_hv"]))

    if config.is_extended:
        imports = run_import_sensitivity(climate, config)
        _banner("SENSITIVITY ANALYSIS (not main results): importation rate per 1,000/yr")
        _print_table(imports.drop(columns="Omega"))
        _print_table(ranking_follows_omega(imports, ["import_per_1000"]).merge(
            ranking_follows_omega(imports, ["import_per_1000"], "local /1000")))


def run_calibration(climate: Climate, target: float) -> None:
    """Calibrate K_0 to `target` total API [per 1,000/yr]; print, never write params."""
    _banner(f"CALIBRATION of K_0: target total API = {target} per 1,000/yr "
            f"(ward: {p.CALIBRATION_WARD}, extended variant)")
    result = calibrate_k0(target, climate)
    _print_table(result.scan)
    if result.k0 is None:
        print(f"\nStatus: {result.status} - target outside the scanned range "
              f"(K_0 {p.CAL_K0_MIN:g}-{p.CAL_K0_MAX:g}). params.py unchanged.")
        return
    print(f"\nCalibrated K_0 = {result.k0:.5g} mosquitoes/(mm/day)")
    print(f"Elasticity d ln(API)/d ln(K_0) near solution = {result.elasticity:.3g}")
    print(f"Imported share of API at solution = {result.import_fraction:.3g}")
    print("WARNING: K_0 is POORLY IDENTIFIED by this target." if result.poorly_identified
          else "K_0 appears identifiable from this target.")
    print("params.py was NOT changed. Approve the value before it is entered as K_0_CALIBRATED.")


def main() -> None:
    """Parse arguments and run the requested analyses."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--calibrate", type=float, metavar="TARGET",
                        help="calibrate K_0 to this total API per 1,000/yr, then stop")
    args = parser.parse_args()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    climate = make_synthetic_climate()
    start = time.perf_counter()
    if args.calibrate is not None:
        run_calibration(climate, args.calibrate)
    else:
        variants = {"spec": spec_config(), "extended": extended_config()}
        runs = run_ward_results(climate, variants)
        run_omega_results(climate, variants)
        run_comparison(climate, runs)
        run_sensitivity_analyses(climate)
        print(f"\nFigures saved to {FIGURE_DIR}")
    print(f"Total runtime {time.perf_counter() - start:.0f} s")


if __name__ == "__main__":  # required: worker processes re-import this file on macOS
    main()
