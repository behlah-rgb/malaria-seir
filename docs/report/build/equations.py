"""Equation mapping and renderer for the project report.

Each entry maps a label (used as [[EQ:label|...]] in the chapter Markdown) to
  - "spec":  the equation exactly as written in docs/SPEC.md (used to check the chapters), and
  - "latex": the matplotlib mathtext string that is rendered to a PNG.
Edit the "latex" strings to change how an equation looks. Do NOT change the mathematics:
the "spec" strings must stay identical to docs/SPEC.md (check_against_spec() enforces this).

Images are written to docs/report/figures/equations/<label>.png at 300 dpi, using the STIX
fonts so that the symbols match Times New Roman.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPORT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = REPORT_DIR.parents[1]
SPEC_PATH = REPO_DIR / "docs" / "SPEC.md"
OUT_DIR = REPORT_DIR / "figures" / "equations"

DPI = 300
FONT_SIZE_PT = 12  # rendered at body-text size; inserted at native size so 12 pt stays 12 pt

EQUATIONS: dict[str, dict[str, str]] = {
    "omega": {
        "spec": "Ω = D_m = (1 - M_i) / (D_d + epsilon)",
        "latex": r"\Omega = D_m = \dfrac{1 - M_i}{D_d + \varepsilon}",
    },
    "kv": {
        "spec": "K_v(R, Ω) = K_0 * (1 + eta * Ω) * R(t)",
        "latex": r"K_v(R, \Omega) = K_0 \cdot (1 + \eta \cdot \Omega) \cdot R(t)",
    },
    "mua": {
        "spec": "μ_A(R(t)) = μ_base + μ_flush * max(0, (R(t) - R_flush) / (Ω + epsilon))",
        "latex": r"\mu_A(R(t)) = \mu_{\mathrm{base}} + \mu_{\mathrm{flush}} \cdot "
        r"\max\left(0,\ \dfrac{R(t) - R_{\mathrm{flush}}}{\Omega + \varepsilon}\right)",
    },
    "biting": {
        "spec": "a(T) = c_a * T * (T - T_0) * sqrt(T_m - T)",
        "latex": r"a(T) = c_a \cdot T \cdot (T - T_0) \cdot \sqrt{T_m - T}",
    },
    "gammam": {
        "spec": "γ_m(T) = (T - T_min) / DD",
        "latex": r"\gamma_m(T) = \dfrac{T - T_{\mathrm{min}}}{DD}",
    },
    "muv": {
        "spec": "μ_v(T) = 1 / (q_0 + q_1*T + q_2*T^2)",
        "latex": r"\mu_v(T) = \dfrac{1}{q_0 + q_1 \cdot T + q_2 \cdot T^2}",
    },
    "nh": {
        "spec": "N_h = S_h + E_h + I_h + R_h",
        "latex": r"N_h = S_h + E_h + I_h + R_h",
    },
    "nv": {
        "spec": "N_v = S_v + E_v + I_v",
        "latex": r"N_v = S_v + E_v + I_v",
    },
    "dAv": {
        "spec": "dA_v/dt = φ_v * (1 - A_v / K_v(R, Ω)) * (S_v + E_v + I_v) - (θ_A + μ_A(R)) * A_v",
        "latex": r"\dfrac{dA_v}{dt} = \varphi_v \cdot \left(1 - \dfrac{A_v}{K_v(R, \Omega)}\right) "
        r"\cdot (S_v + E_v + I_v) - (\theta_A + \mu_A(R)) \cdot A_v",
    },
    "dSv": {
        "spec": "dS_v/dt = θ_A * A_v - a(T) * β_vh * (I_h / N_h) * S_v - μ_v(T) * S_v",
        "latex": r"\dfrac{dS_v}{dt} = \theta_A \cdot A_v - a(T) \cdot \beta_{vh} \cdot "
        r"\dfrac{I_h}{N_h} \cdot S_v - \mu_v(T) \cdot S_v",
    },
    "dEv": {
        "spec": "dE_v/dt = a(T) * β_vh * (I_h / N_h) * S_v - (γ_m(T) + μ_v(T)) * E_v",
        "latex": r"\dfrac{dE_v}{dt} = a(T) \cdot \beta_{vh} \cdot \dfrac{I_h}{N_h} \cdot S_v "
        r"- (\gamma_m(T) + \mu_v(T)) \cdot E_v",
    },
    "dIv": {
        "spec": "dI_v/dt = γ_m(T) * E_v - μ_v(T) * I_v",
        "latex": r"\dfrac{dI_v}{dt} = \gamma_m(T) \cdot E_v - \mu_v(T) \cdot I_v",
    },
    "dSh": {
        "spec": "dS_h/dt = Λ_h - a(T) * β_hv * (I_v / N_h) * S_h - μ_h * S_h + ρ * R_h",
        "latex": r"\dfrac{dS_h}{dt} = \Lambda_h - a(T) \cdot \beta_{hv} \cdot \dfrac{I_v}{N_h} \cdot S_h "
        r"- \mu_h \cdot S_h + \rho \cdot R_h",
    },
    "dEh": {
        "spec": "dE_h/dt = a(T) * β_hv * (I_v / N_h) * S_h - (α_h + μ_h) * E_h",
        "latex": r"\dfrac{dE_h}{dt} = a(T) \cdot \beta_{hv} \cdot \dfrac{I_v}{N_h} \cdot S_h "
        r"- (\alpha_h + \mu_h) \cdot E_h",
    },
    "dIh": {
        "spec": "dI_h/dt = α_h * E_h - (γ_h + μ_h + δ_h) * I_h",
        "latex": r"\dfrac{dI_h}{dt} = \alpha_h \cdot E_h - (\gamma_h + \mu_h + \delta_h) \cdot I_h",
    },
    "dRh": {
        "spec": "dR_h/dt = γ_h * I_h - (ρ + μ_h) * R_h",
        "latex": r"\dfrac{dR_h}{dt} = \gamma_h \cdot I_h - (\rho + \mu_h) \cdot R_h",
    },
}


def check_against_spec() -> list[str]:
    """Return the labels whose "spec" string does not appear verbatim in docs/SPEC.md."""
    spec_text = SPEC_PATH.read_text(encoding="utf-8")
    return [label for label, eq in EQUATIONS.items() if eq["spec"] not in spec_text]


def render_all(out_dir: Path = OUT_DIR) -> dict[str, Path]:
    """Render every equation to a tightly cropped 300 dpi PNG; return {label: path}."""
    matplotlib.rcParams["mathtext.fontset"] = "stix"
    matplotlib.rcParams["font.family"] = "STIXGeneral"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for label, eq in EQUATIONS.items():
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${eq['latex']}$", fontsize=FONT_SIZE_PT, color="black")
        path = out_dir / f"{label}.png"
        fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.02, transparent=False,
                    facecolor="white")
        plt.close(fig)
        paths[label] = path
    return paths


if __name__ == "__main__":
    bad = check_against_spec()
    if bad:
        raise SystemExit(f"Equations not found verbatim in SPEC.md: {bad}")
    for label, path in render_all().items():
        print(label, path)
