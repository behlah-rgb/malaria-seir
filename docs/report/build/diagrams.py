"""Block diagrams for the project report (drawn with matplotlib, no data involved).

Writes to docs/report/figures/:
  - model_diagram.png    eight-compartment SEIR-vector model with climate/drainage entry points
  - system_workflow.png  software workflow from inputs to figures

Content follows docs/SPEC.md (compartments and flows) and docs/MODEL_REPORT.md (module map).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "figures"
DPI = 300

INK = "#1a1a1a"
VECTOR_FILL = "#dbe8f5"
HUMAN_FILL = "#f6e3d3"
INPUT_FILL = "#eeeeee"
MODULE_FILL = "#f4f4f4"


def _setup_fonts() -> None:
    """Use Times-like STIX fonts so the diagrams match the report text."""
    matplotlib.rcParams["mathtext.fontset"] = "stix"
    matplotlib.rcParams["font.family"] = "STIXGeneral"


def _box(ax, x: float, y: float, w: float, h: float, text: str, fill: str,
         size: float = 13, style: str = "round,pad=0.02,rounding_size=0.08") -> tuple[float, float, float, float]:
    """Draw a labelled box centred at (x, y); return its (left, right, bottom, top)."""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=style,
                                facecolor=fill, edgecolor=INK, linewidth=1.1))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=INK)
    return x - w / 2, x + w / 2, y - h / 2, y + h / 2


def _arrow(ax, start, end, label: str = "", dashed: bool = False, rad: float = 0.0,
           label_offset=(0.0, 0.12), size: float = 10.5) -> None:
    """Draw an arrow from start to end with an optional label near its midpoint."""
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                                 linewidth=1.1, color=INK, linestyle=(0, (4, 3)) if dashed else "-",
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=size, color=INK)


def model_diagram(path: Path) -> Path:
    """Eight-compartment SEIR-vector model (SPEC §4-5) with entry points of T, R and Ω."""
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.35, 7.3)
    ax.axis("off")

    w, h = 1.25, 0.7
    xs = [1.2, 3.75, 6.3, 8.85]
    yv, yh = 4.6, 1.9

    vec = [_box(ax, x, yv, w, h, f"${n}$", VECTOR_FILL, 15) for x, n in zip(xs, ["A_v", "S_v", "E_v", "I_v"])]
    hum = [_box(ax, x, yh, w, h, f"${n}$", HUMAN_FILL, 15) for x, n in zip(xs, ["S_h", "E_h", "I_h", "R_h"])]
    ax.text(0.15, yv - 0.75, "Mosquitoes (aquatic stage + adults)", fontsize=11.5, color=INK, style="italic")
    ax.text(0.15, yh + 0.55, "Humans", fontsize=11.5, color=INK, style="italic")

    # Vector flows
    _arrow(ax, (vec[0][1], yv), (vec[1][0], yv), r"$\theta_A$")
    _arrow(ax, (vec[1][1], yv), (vec[2][0], yv), r"$a(T)\,\beta_{vh}\,I_h/N_h$")
    _arrow(ax, (vec[2][1], yv), (vec[3][0], yv), r"$\gamma_m(T)$")
    # Egg-laying by all adults (S_v + E_v + I_v) into the aquatic stage
    _arrow(ax, (xs[1] - 0.2, vec[1][3]), (xs[0] + 0.2, vec[0][3]), rad=0.55, label="")
    ax.text((xs[0] + xs[1]) / 2, yv + 1.05, r"egg-laying by all adults: $\varphi_v\,(1 - A_v/K_v)\,N_v$",
            ha="center", fontsize=10.5, color=INK)
    # Human flows
    _arrow(ax, (hum[0][1], yh), (hum[1][0], yh), r"$a(T)\,\beta_{hv}\,I_v/N_h$", label_offset=(0.0, -0.17))
    _arrow(ax, (hum[1][1], yh), (hum[2][0], yh), r"$\alpha_h$")
    _arrow(ax, (hum[2][1], yh), (hum[3][0], yh), r"$\gamma_h$")
    _arrow(ax, (xs[3], hum[3][2]), (xs[0], hum[0][2]), rad=-0.2)
    ax.text(5.0, 0.45, r"loss of immunity $\rho$", ha="center", fontsize=10.5, color=INK)
    _arrow(ax, (-0.05, yh), (hum[0][0], yh), r"$\Lambda_h$", label_offset=(0.0, 0.14))

    # Host-vector coupling (dashed = influence, not movement)
    _arrow(ax, (xs[2] - 0.2, hum[2][3]), ((xs[1] + xs[2]) / 2 + 0.05, yv - 0.05), dashed=True)
    ax.text(5.35, 3.35, "infectious humans\ninfect biting mosquitoes", fontsize=9.5, color=INK, ha="right")
    _arrow(ax, (xs[3] - 0.15, vec[3][2]), ((xs[0] + xs[1]) / 2 + 0.1, yh + 0.05), dashed=True)
    ax.text(7.7, 3.45, "infectious bites\ninfect humans", fontsize=9.5, color=INK, ha="left")

    # Deaths (listed as text to keep the diagram readable)
    ax.text(5.0, -0.25,
            r"Deaths: larvae $\mu_A(R)$; adult mosquitoes $\mu_v(T)$; humans $\mu_h$ (all classes), "
            r"$\delta_h$ (malaria, from $I_h$)", ha="center", fontsize=10, color=INK)

    # Climate and drainage inputs
    _box(ax, 1.2, 6.75, 2.3, 0.75, "Rainfall $R(t)$, Clogging index $\\Omega$\n"
         r"$\rightarrow K_v(R,\Omega)$, $\mu_A(R)$", INPUT_FILL, 10, style="square,pad=0.02")
    _arrow(ax, (0.75, 6.37), (0.75, vec[0][3] + 0.02), dashed=True)
    _box(ax, 6.3, 6.75, 2.6, 0.75, "Temperature $T(t)$\n"
         r"$\rightarrow a(T)$, $\gamma_m(T)$, $\mu_v(T)$", INPUT_FILL, 10, style="square,pad=0.02")
    _arrow(ax, (6.3, 6.37), (6.3, vec[2][3] + 0.02), dashed=True)

    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def system_workflow(path: Path) -> Path:
    """Software workflow: inputs -> drainage/climate -> ODE + spin-up -> metrics -> experiments -> figures."""
    fig, ax = plt.subplots(figsize=(10, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    bw, bh = 2.75, 0.95
    col = [1.6, 5.0, 8.4]

    _box(ax, col[0], 5.2, bw, bh, "params.py\nall values + sources\nconfig.py: spec / extended", MODULE_FILL, 10.5)
    _box(ax, col[1], 5.2, bw, bh, "climate.py\n$T(t)$, $R(t)$; $a$, $\\gamma_m$, $\\mu_v$", MODULE_FILL, 10.5)
    _box(ax, col[2], 5.2, bw, bh, "drainage.py\n$\\Omega$, $K_v$, $\\mu_A$", MODULE_FILL, 10.5)

    _box(ax, col[1], 3.55, 4.6, bh, "ode.py\n8 ODEs solved with odeint; spin-up until\nlocal infections change < 1 % per year",
         MODULE_FILL, 10.5)
    for x in col:
        _arrow(ax, (x, 5.2 - bh / 2), (col[1] + (x - col[1]) * 0.45, 3.55 + bh / 2))

    _box(ax, col[1], 2.0, 4.6, 0.8, "metrics.py, r0.py\npeak $I_h$, attack rate, EIR, local / imported, $R_0(t)$",
         MODULE_FILL, 10.5)
    _arrow(ax, (col[1], 3.55 - bh / 2), (col[1], 2.0 + 0.4))

    exps = ["scenarios.py\n3 wards", "optimize.py\n81-cell sweep", "omega_analysis.py\nthresholds",
            "sensitivity.py", "calibrate.py\n(not run)"]
    ex_x = [1.0, 3.0, 5.0, 7.0, 9.0]
    for x, t in zip(ex_x, exps):
        _box(ax, x, 0.65, 1.75, 0.75, t, MODULE_FILL, 9.5)
        _arrow(ax, (col[1] + (x - col[1]) * 0.35, 2.0 - 0.4), (x, 0.65 + 0.375))

    ax.text(0.05, 2.0, "main.py runs\nall steps;\nplotting.py\nwrites figures", fontsize=10, color=INK, va="center")
    ax.text(9.95, 2.0, "parallel.py\nruns sweep cells\nin parallel", fontsize=10, color=INK, va="center", ha="right")

    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def render_all(out_dir: Path = OUT_DIR) -> list[Path]:
    """Render both diagrams; return their paths."""
    _setup_fonts()
    out_dir.mkdir(parents=True, exist_ok=True)
    return [model_diagram(out_dir / "model_diagram.png"), system_workflow(out_dir / "system_workflow.png")]


if __name__ == "__main__":
    for p in render_all():
        print(p)
