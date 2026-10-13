"""Model variant selection: "spec" (literal SPEC + approved guards) vs "extended".

A ModelConfig is passed to the simulation functions. All numeric values still
live in params.py; this file only decides which of them are used.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from malaria_model import params as p

Variant = Literal["spec", "extended"]
Spinup = Literal["fixed", "converge"]


@dataclass(frozen=True)
class ModelConfig:
    """Switches for one model run.

    variant: "spec" or "extended".
    k0: carrying-capacity scale K_0 [mosquitoes/(mm/day)].
    import_per_1000_per_year: imported infections [per 1,000 per year] (0 in spec).
    omega_lengthens_tau: extended only; if True, tau grows with Ω.
    spinup: "fixed" (N_YEARS_TOTAL years, DEVIATION #5) or "converge" (DEVIATION #9).
    calibrated: whether k0 came from calibration (used in figure subtitles).
    """

    variant: Variant
    k0: float
    import_per_1000_per_year: float = 0.0
    omega_lengthens_tau: bool = False
    spinup: Spinup = "converge"
    calibrated: bool = False

    @property
    def is_extended(self) -> bool:
        """True for the extended variant."""
        return self.variant == "extended"

    @property
    def import_rate(self) -> float:
        """Per-capita importation rate on susceptibles [1/day]."""
        return self.import_per_1000_per_year / p.PER_POPULATION / p.DAYS_PER_YEAR

    def tau(self, omega: float) -> float:
        """Rainfall retention time [days] for clogging index omega [-] (extended only)."""
        if self.omega_lengthens_tau:
            # DEVIATION: tau lengthened by Ω when the switch is on, see DEVIATIONS.md #7
            return p.TAU_RAIN * (1.0 + p.TAU_OMEGA_SLOPE * omega)
        return p.TAU_RAIN

    def describe(self) -> str:
        """Short label for figure subtitles, e.g. 'extended, uncalibrated (K_0 = 500), ...'."""
        status = "calibrated" if self.calibrated else "uncalibrated"
        return f"{self.variant}, {status} (K_0 = {self.k0:,.4g}), placeholder parameters"


def spec_config(spinup: Spinup = "converge") -> ModelConfig:
    """Literal SPEC model with only the approved numerical guards (#1-#4)."""
    return ModelConfig(variant="spec", k0=p.K_0, spinup=spinup)


def extended_config(spinup: Spinup = "converge", calibrated: bool | None = None) -> ModelConfig:
    """Extended model. Uses K_0_CALIBRATED if it exists (and calibrated is not False)."""
    use_calibrated = p.K_0_CALIBRATED is not None if calibrated is None else calibrated
    k0 = p.K_0_CALIBRATED if use_calibrated and p.K_0_CALIBRATED is not None else p.K_0
    return ModelConfig(
        variant="extended", k0=k0, import_per_1000_per_year=p.IMPORT_PER_1000_PER_YEAR,
        omega_lengthens_tau=p.OMEGA_LENGTHENS_TAU, spinup=spinup,
        calibrated=use_calibrated and p.K_0_CALIBRATED is not None,
    )


def headline_config() -> ModelConfig:
    """The variant selected by params.MODEL_VARIANT."""
    return extended_config() if p.MODEL_VARIANT == "extended" else spec_config()


def with_k0(config: ModelConfig, k0: float) -> ModelConfig:
    """Copy of config with a different K_0 (used by calibration)."""
    return replace(config, k0=k0)
