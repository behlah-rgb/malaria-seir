"""Figures for the SEIR-Vector malaria model.

Every figure carries a subtitle stating the model variant and calibration
status (ModelConfig.describe()). Climate inputs T(t) [°C] and R(t) [mm/day]
are drawn in separate small panels, never on a second y-axis.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write files only, no window needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, LogNorm

from malaria_model import params as p
from malaria_model.climate import Climate

# Colours: reference categorical palette slots 1-3 (dataviz skill palette.md)
SERIES_COLORS: list[str] = ["#2a78d6", "#eb6834", "#1baf7a"]
LINE_STYLES: list[str] = ["-", "--", ":"]  # second cue so colour is not the only identity signal
MARKERS: list[str] = ["o", "^", "s"]
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
CLIMATE_COLOR = "#52514e"
SAFE_FILL = "#e1e0d9"
# Sequential single-hue ramp (blue steps 100 -> 700) for heatmaps
SEQUENTIAL_CMAP = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
FIG_DPI = 150
LINE_WIDTH = 2.0
CONTOUR_RESOLUTION = 200  # points per axis for the Ω contour overlay


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _style_axis(ax: plt.Axes) -> None:
    """Recessive axes: hairline grid, muted ticks, no top/right spines."""
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_MUTED)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    ax.yaxis.label.set_color(INK_SECONDARY)
    ax.xaxis.label.set_color(INK_SECONDARY)


def _titles(fig: plt.Figure, title: str, subtitle: str) -> None:
    """Title (primary ink) and subtitle (secondary ink) stacked above the plot area.

    Call after tight_layout(); saving with bbox_inches="tight" keeps both in frame.
    """
    height_pts = fig.get_figheight() * 72
    sub_lines = subtitle.count("\n") + 1
    fig.text(0.01, 1.0, subtitle, ha="left", va="bottom", color=INK_SECONDARY, fontsize=9)
    title_y = 1.0 + (sub_lines * 9 * 1.4 + 4) / height_pts
    fig.text(0.01, title_y, title, ha="left", va="bottom", color=INK_PRIMARY, fontsize=12)


def _save(fig: plt.Figure, out_path: Path) -> Path:
    """Save a PNG and close the figure."""
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _plot_climate(ax_T: plt.Axes, ax_R: plt.Axes, climate: Climate) -> None:
    """Draw T(t) [°C] and R(t) [mm/day] in two small panels."""
    ax_T.plot(climate.days, climate.temperature, color=CLIMATE_COLOR, linewidth=LINE_WIDTH)
    ax_T.set_ylabel("T (°C)")
    ax_R.bar(climate.days, climate.rainfall, width=1.0, color=CLIMATE_COLOR)
    ax_R.set_ylabel("R (mm/day)")
    ax_R.set_xlabel("Day of reported year (0 = 1 Jan)")
    for ax in (ax_T, ax_R):
        _style_axis(ax)


def _uses_log_scale(values: np.ndarray) -> bool:
    """True if all values are positive and span at least LOG_SCALE_RATIO."""
    return bool((values > 0).all() and values.max() / values.min() >= p.LOG_SCALE_RATIO)


# ---------------------------------------------------------------------------
# Ward time series
# ---------------------------------------------------------------------------
def ward_figure(
    results: dict[str, pd.DataFrame], column: str, ylabel: str, title: str, subtitle: str,
    climate: Climate, out_path: Path, hline: float | None = None,
) -> Path:
    """Plot `column` vs day for every ward, with climate panels underneath.

    hline: optional horizontal reference line (e.g. R0 = 1). Saves a PNG.
    """
    fig, (ax, ax_T, ax_R) = plt.subplots(
        3, 1, figsize=(9, 7.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1, 1]}, facecolor=SURFACE,
    )
    for i, (name, df) in enumerate(results.items()):
        ax.plot(df.index, df[column], color=SERIES_COLORS[i], linestyle=LINE_STYLES[i],
                linewidth=LINE_WIDTH, label=name)
    if hline is not None:
        ax.axhline(hline, color=INK_MUTED, linewidth=1.0, linestyle="-.")
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_SECONDARY)
    _style_axis(ax)
    _plot_climate(ax_T, ax_R, climate)
    fig.tight_layout()
    _titles(fig, title, subtitle)
    return _save(fig, out_path)


# ---------------------------------------------------------------------------
# D_d x M_i heatmaps with Ω contours
# ---------------------------------------------------------------------------
def _omega_overlay(ax: plt.Axes, grid: pd.DataFrame, omega_star: float | None) -> None:
    """Draw Ω contours on a seaborn heatmap whose rows are M_i (top = largest)."""
    d_vals = grid.columns.to_numpy(dtype=float)
    m_vals = grid.index.to_numpy(dtype=float)
    step = d_vals[1] - d_vals[0]
    D = np.linspace(d_vals[0] - step / 2, d_vals[-1] + step / 2, CONTOUR_RESOLUTION)
    M = np.linspace(m_vals[0] - step / 2, m_vals[-1] + step / 2, CONTOUR_RESOLUTION)
    DD, MM = np.meshgrid(D, M)
    omega = (1.0 - MM) / (DD + p.EPSILON)
    X = (DD - d_vals[0]) / step + 0.5  # heatmap cell coordinates
    Y = (m_vals[-1] - MM) / step + 0.5
    lines = ax.contour(X, Y, omega, levels=p.OMEGA_CONTOUR_LEVELS, colors=INK_MUTED,
                       linewidths=0.8, linestyles="--")
    ax.clabel(lines, fmt=lambda v: f"Ω={v:g}", fontsize=7, colors=INK_SECONDARY)
    if omega_star is not None:
        with plt.rc_context({"hatch.color": INK_PRIMARY, "hatch.linewidth": 0.6}):
            ax.contourf(X, Y, omega, levels=[0.0, omega_star], colors="none", hatches=["///"])
        star = ax.contour(X, Y, omega, levels=[omega_star], colors=INK_PRIMARY, linewidths=2.2)
        ax.clabel(star, fmt=lambda v: f"Ω*={v:.3g} (min M_i)", fontsize=8, colors=INK_PRIMARY)


def heatmap_figure(grid: pd.DataFrame, title: str, subtitle: str, cbar_label: str,
                   out_path: Path, omega_star: float | None = None) -> Path:
    """Seaborn heatmap of a metric over D_d (x) and M_i (y), with Ω contours. Saves a PNG.

    Log colour scale when values span orders of magnitude (noted in the label).
    Hatched area: Ω < Ω* (peak R0 < 1, "safe zone"); bold line: Ω = Ω*, which is
    also the minimum M_i needed at each D_d.
    """
    import seaborn as sns

    values = grid.to_numpy(dtype=float)
    log = _uses_log_scale(values)
    norm = LogNorm(vmin=values.min(), vmax=values.max()) if log else None
    fig, ax = plt.subplots(figsize=(8.5, 7), facecolor=SURFACE)
    sns.heatmap(
        grid.iloc[::-1], ax=ax, cmap=SEQUENTIAL_CMAP, norm=norm, annot=True, fmt=".2g",
        annot_kws={"fontsize": 6.5}, linewidths=1, linecolor=SURFACE,
        cbar_kws={"label": cbar_label + (" (log scale)" if log else "")},
    )
    _omega_overlay(ax, grid, omega_star)
    ax.set_xlabel("Drainage density D_d (0 = none, 1 = dense)")
    ax.set_ylabel("Maintenance efficiency M_i (0 = blocked, 1 = clear)")
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    grid_min_omega = (1.0 - grid.index.max()) / (grid.columns.max() + p.EPSILON)
    if omega_star is None:
        safe_note = "no safe zone: peak R0 > 1 at every Ω searched"
    elif omega_star < grid_min_omega:
        safe_note = (f"safe zone Ω < Ω* = {omega_star:.3g} lies outside this grid "
                     f"(smallest Ω here = {grid_min_omega:.3g})")
    else:
        safe_note = "hatched = safe zone Ω < Ω* (peak R0 < 1)"
    fig.tight_layout()
    _titles(fig, title, f"{subtitle}\nDashed = Ω contours; {safe_note}")
    return _save(fig, out_path)


# ---------------------------------------------------------------------------
# Ω figures
# ---------------------------------------------------------------------------
def omega_scatter_figure(cells: dict[str, pd.DataFrame], omega_stars: dict[str, float | None],
                         subtitle: str, out_path: Path) -> Path:
    """Outcome vs Ω for every grid cell, one colour per variant (label -> sweep table).

    Illustration that outcomes depend on D_d and M_i only through Ω (a mathematical
    consequence of the model structure), not a validation.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=SURFACE)
    for ax, column, ylabel in zip(axes, ["attack /1000", "peak I_h"],
                                  ["Attack rate per 1,000 (year reported)", "Peak I_h (humans)"]):
        for i, (label, table) in enumerate(cells.items()):
            ax.scatter(table["Omega"], table[column], s=36, marker=MARKERS[i],
                       color=SERIES_COLORS[i], edgecolor=SURFACE, linewidth=0.8, label=label)
            star = omega_stars.get(label)
            if star is not None:
                ax.axvline(star, color=SERIES_COLORS[i], linestyle=LINE_STYLES[i], linewidth=1.2)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Clogging index Ω (log scale)")
        ax.set_ylabel(ylabel + " (log scale)")
        _style_axis(ax)
    axes[0].legend(frameon=False, fontsize=8, labelcolor=INK_SECONDARY)
    fig.tight_layout()
    _titles(fig, "Outcome vs Ω for all grid cells (vertical lines = Ω* per variant)",
            subtitle + "\nIllustration: results depend on D_d and M_i only through Ω "
            "(mathematical consequence of the model), not validation")
    return _save(fig, out_path)


def r0_vs_omega_figure(curves: dict[str, pd.DataFrame], omega_stars: dict[str, float | None],
                       persistence: dict[str, float | None], subtitle: str,
                       out_path: Path) -> Path:
    """Max and mean R0(t) vs Ω per variant; line at R0 = 1; safe zone (Ω < Ω*) shaded.

    Dotted verticals: Ω where local infections stop declining year to year (persistence).
    """
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=SURFACE)
    for i, (label, curve) in enumerate(curves.items()):
        ax.plot(curve["Omega"], curve["R0 max"], color=SERIES_COLORS[i], linewidth=LINE_WIDTH,
                label=f"{label}: peak R0(t)")
        ax.plot(curve["Omega"], curve["R0 mean"], color=SERIES_COLORS[i], linewidth=1.2,
                linestyle=":", label=f"{label}: mean R0(t)")
        star = omega_stars.get(label)
        if star is not None:
            ax.axvspan(curve["Omega"].min(), star, color=SERIES_COLORS[i], alpha=0.08)
            ax.axvline(star, color=SERIES_COLORS[i], linestyle="--", linewidth=1.2)
            ax.annotate(f"Ω* = {star:.3g}", xy=(star, p.R0_THRESHOLD), xytext=(4, 6 + 14 * i),
                        textcoords="offset points", fontsize=8, color=INK_SECONDARY)
        persist = persistence.get(label)
        if persist is not None:
            ax.axvline(persist, color=SERIES_COLORS[i], linestyle=":", linewidth=1.5)
            ax.annotate(f"persistence Ω = {persist:.3g}", xy=(persist, p.R0_THRESHOLD),
                        xytext=(4, -16 - 14 * i), textcoords="offset points", fontsize=8,
                        color=INK_SECONDARY)
    ax.axhline(p.R0_THRESHOLD, color=INK_MUTED, linewidth=1.0, linestyle="-.")
    ax.set_xscale("log")
    ax.set_xlabel("Clogging index Ω (log scale)")
    ax.set_ylabel("R0 (next-generation matrix)")
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_SECONDARY)
    _style_axis(ax)
    fig.tight_layout()
    _titles(fig, "R0 vs Ω; shaded = safe zone (peak R0 < 1); dotted = local growth factor 1",
            subtitle)
    return _save(fig, out_path)


def variant_comparison_figure(runs: dict[str, dict[str, pd.DataFrame]], subtitle: str,
                              out_path: Path) -> Path:
    """Spec vs extended: columns = wards; rows = I_h(t) (log) and mosquitoes per human.

    runs: {variant label: {ward name: reported-year DataFrame}}.
    """
    wards = list(next(iter(runs.values())).keys())
    fig, axes = plt.subplots(2, len(wards), figsize=(4.2 * len(wards), 7), sharex=True,
                             sharey="row", facecolor=SURFACE)
    for j, ward in enumerate(wards):
        for i, (label, by_ward) in enumerate(runs.items()):
            df = by_ward[ward]
            style = dict(color=SERIES_COLORS[i], linestyle=LINE_STYLES[i], linewidth=LINE_WIDTH,
                         label=label)
            axes[0, j].plot(df.index, df["I_h"].clip(lower=1e-12), **style)
            axes[1, j].plot(df.index, df["N_v"] / df["N_h"], **style)
        axes[0, j].set_title(ward, fontsize=10, color=INK_PRIMARY)
        axes[0, j].set_yscale("log")
        axes[1, j].set_xlabel("Day of reported year")
        for ax in axes[:, j]:
            _style_axis(ax)
    axes[0, 0].set_ylabel("Infectious humans I_h (log scale)")
    axes[1, 0].set_ylabel("Mosquitoes per human N_v/N_h")
    fig.tight_layout()
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=len(labels),
               frameon=False, fontsize=9, labelcolor=INK_SECONDARY)
    _titles(fig, "Spec vs extended model, reported year", subtitle)
    return _save(fig, out_path)


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------
def sensitivity_figure(table: pd.DataFrame, subtitle: str, out_path: Path) -> Path:
    """Small multiples: attack rate [per 1,000] over gamma_h x beta_hv, one panel per ward.

    Shared log colour scale across panels so wards are directly comparable.
    """
    import seaborn as sns

    wards = list(table["ward"].unique())
    positive = table["attack rate /1000"][table["attack rate /1000"] > 0]
    norm = LogNorm(vmin=positive.min(), vmax=positive.max())
    fig, axes = plt.subplots(1, len(wards), figsize=(4.2 * len(wards), 4), facecolor=SURFACE,
                             sharey=True)
    for i, (ax, ward) in enumerate(zip(axes, wards)):
        grid = table[table["ward"] == ward].pivot(
            index="beta_hv", columns="gamma_h", values="attack rate /1000").iloc[::-1]
        sns.heatmap(grid, ax=ax, cmap=SEQUENTIAL_CMAP, norm=norm, annot=True, fmt=".3g",
                    annot_kws={"fontsize": 8}, linewidths=1, linecolor=SURFACE,
                    cbar=i == len(wards) - 1,
                    cbar_kws={"label": "Attack rate per 1,000 (log scale)"})
        ax.set_title(ward, fontsize=10, color=INK_PRIMARY)
        ax.set_xlabel("gamma_h (1/day)")
        ax.set_ylabel("beta_hv" if i == 0 else "")
        ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    fig.tight_layout()
    _titles(fig, "SENSITIVITY ANALYSIS (not main results): attack rate, reported year", subtitle)
    return _save(fig, out_path)
