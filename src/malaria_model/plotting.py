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
from matplotlib.colors import LinearSegmentedColormap

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
    climate: Climate, out_path: Path,
) -> Path:
    """Plot `column` [individuals] vs day for every ward, with climate panels.

    Saves a PNG to out_path and returns the path.
    """
    fig, (ax, ax_T, ax_R) = plt.subplots(
        3, 1, figsize=(9, 7.5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1, 1]}, facecolor=SURFACE,
    )
    for i, (name, df) in enumerate(results.items()):
        ax.plot(df.index, df[column], color=SERIES_COLORS[i], linestyle=LINE_STYLES[i],
                linewidth=LINE_WIDTH, label=name)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", color=INK_PRIMARY, fontsize=12)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_SECONDARY)
    _style_axis(ax)
    _plot_climate(ax_T, ax_R, climate)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path


def heatmap_figure(grid: pd.DataFrame, out_path: Path) -> Path:
    """Seaborn heatmap of peak I_h [humans] over D_d (x) and M_i (y). Saves a PNG."""
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=SURFACE)
    sns.heatmap(
        grid.iloc[::-1], ax=ax, cmap=SEQUENTIAL_CMAP, annot=True, fmt=".1f",
        annot_kws={"fontsize": 7}, linewidths=1, linecolor=SURFACE,
        cbar_kws={"label": "Peak infectious humans, max I_h(t)"},
    )
    ax.set_xlabel("Drainage density D_d (0 = none, 1 = dense)")
    ax.set_ylabel("Maintenance efficiency M_i (0 = blocked, 1 = clear)")
    ax.set_title("Peak I_h over one year by drainage and maintenance", loc="left",
                 color=INK_PRIMARY, fontsize=12)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return out_path
