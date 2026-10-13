"""Figures: ward time series with the climate inputs shown underneath.

Each figure has one main panel plus two small panels for T(t) [°C] and
R(t) [mm/day]. They use separate panels (not a second y-axis) because the
quantities have different units.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write files only, no window needed
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, LogNorm

from malaria_model import params as p
from malaria_model.climate import Climate

# Colours: reference categorical palette slots 1-3 (dataviz skill palette.md)
SERIES_COLORS: list[str] = ["#2a78d6", "#eb6834", "#1baf7a"]
LINE_STYLES: list[str] = ["-", "--", ":"]  # second cue so colour is not the only identity signal
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
CLIMATE_COLOR = "#52514e"
# Sequential single-hue ramp (blue steps 100 -> 700) for the heatmap
SEQUENTIAL_CMAP = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
FIG_DPI = 150
LINE_WIDTH = 2.0


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


def _plot_climate(ax_T: plt.Axes, ax_R: plt.Axes, climate: Climate) -> None:
    """Draw T(t) [°C] and R(t) [mm/day] in two small panels."""
    ax_T.plot(climate.days, climate.temperature, color=CLIMATE_COLOR, linewidth=LINE_WIDTH)
    ax_T.set_ylabel("T (°C)")
    ax_R.bar(climate.days, climate.rainfall, width=1.0, color=CLIMATE_COLOR)
    ax_R.set_ylabel("R (mm/day)")
    ax_R.set_xlabel("Day of year (0 = 1 Jan)")
    for ax in (ax_T, ax_R):
        _style_axis(ax)


def ward_figure(
    results: dict[str, pd.DataFrame], column: str, ylabel: str, title: str,
    climate: Climate, out_path: Path, hline: float | None = None,
) -> Path:
    """Plot `column` vs day for every ward, with climate panels underneath.

    hline: optional horizontal reference line (e.g. R0 = 1).
    Saves a PNG to out_path and returns the path.
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
    ax.set_title(title, loc="left", color=INK_PRIMARY, fontsize=12)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_SECONDARY)
    _style_axis(ax)
    _plot_climate(ax_T, ax_R, climate)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _uses_log_scale(grid: pd.DataFrame) -> bool:
    """True if positive values span at least LOG_SCALE_RATIO (orders of magnitude)."""
    values = grid.to_numpy()
    return bool((values > 0).all() and values.max() / values.min() >= p.LOG_SCALE_RATIO)


def heatmap_figure(grid: pd.DataFrame, title: str, cbar_label: str, out_path: Path) -> Path:
    """Seaborn heatmap of a metric over D_d (x) and M_i (y); saves a PNG.

    Uses a log colour scale when values span orders of magnitude (noted in the label).
    Every cell is annotated with its value so the numbers are readable either way.
    """
    import seaborn as sns

    log = _uses_log_scale(grid)
    norm = LogNorm(vmin=grid.to_numpy().min(), vmax=grid.to_numpy().max()) if log else None
    fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=SURFACE)
    sns.heatmap(
        grid.iloc[::-1], ax=ax, cmap=SEQUENTIAL_CMAP, norm=norm, annot=True, fmt=".3g",
        annot_kws={"fontsize": 7}, linewidths=1, linecolor=SURFACE,
        cbar_kws={"label": cbar_label + (" (log scale)" if log else "")},
    )
    ax.set_xlabel("Drainage density D_d (0 = none, 1 = dense)")
    ax.set_ylabel("Maintenance efficiency M_i (0 = blocked, 1 = clear)")
    ax.set_title(title, loc="left", color=INK_PRIMARY, fontsize=11)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path


def sensitivity_figure(table: pd.DataFrame, out_path: Path) -> Path:
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
    fig.suptitle("SENSITIVITY ANALYSIS (not main results): attack rate in year 3",
                 x=0.01, ha="left", color=INK_PRIMARY, fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path
