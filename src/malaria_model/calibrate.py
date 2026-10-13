"""Calibrate K_0 ONLY, against a user-supplied annual parasite incidence (API).

Reference: params.CALIBRATION_WARD, extended variant, converged spin-up.
Target: TOTAL reported incidence per 1,000 per year (imported + local).
The result is printed for review; it is never written to params.py automatically.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from malaria_model import params as p
from malaria_model.climate import Climate
from malaria_model.config import ModelConfig, extended_config, with_k0
from malaria_model.drainage import clogging_index
from malaria_model.metrics import attack_rate, imported_infections, local_infections, per_1000
from malaria_model.ode import simulate_reported_year
from malaria_model.parallel import parallel_map


def _evaluate(task: tuple[float, Climate, ModelConfig]) -> dict:
    """Incidence [per 1,000/yr] in the reference ward at one K_0 (top-level for workers)."""
    k0, climate, config = task
    cfg = with_k0(config, k0)
    result = simulate_reported_year(clogging_index(*p.WARDS[p.CALIBRATION_WARD]), climate, cfg)
    df = result.df
    total = attack_rate(df)
    imported = per_1000(imported_infections(df, cfg.import_rate), df)
    return {"K_0": k0, "total /1000": total,
            "local /1000": per_1000(local_infections(df, climate), df),
            "imported fraction": imported / total if total > 0 else float("nan"),
            "converged": result.converged, "spin-up yrs": result.years_run}


@dataclass
class CalibrationResult:
    """Outcome of calibrate_k0.

    k0: calibrated K_0 [mosquitoes/(mm/day)] or None; status: "found" or "unreachable";
    scan: table of the log-spaced K_0 scan; elasticity: d ln(API)/d ln(K_0) near the
    solution [-]; import_fraction: imported share of the API at the solution [-];
    poorly_identified: True if elasticity or import share fail the CAL_* thresholds,
    or the scan is not monotonic in K_0.
    """

    k0: float | None
    status: str
    scan: pd.DataFrame
    elasticity: float = float("nan")
    import_fraction: float = float("nan")
    poorly_identified: bool = True


def calibrate_k0(target_per_1000: float, climate: Climate, config: ModelConfig | None = None,
                 workers: int = p.N_WORKERS) -> CalibrationResult:
    """Find K_0 so the reference ward's total API equals target_per_1000 [per 1,000/yr].

    1. Scan K_0 log-spaced over [CAL_K0_MIN, CAL_K0_MAX]; check the target is bracketed.
    2. brentq on ln K_0 to tolerance CAL_RTOL.
    3. Report elasticity and imported share to judge whether K_0 is well identified.
    """
    config = config or extended_config(calibrated=False)
    k0s = np.geomspace(p.CAL_K0_MIN, p.CAL_K0_MAX, p.CAL_SCAN_POINTS)
    scan = pd.DataFrame(parallel_map(_evaluate, [(k, climate, config) for k in k0s], workers))
    totals = scan["total /1000"].to_numpy()
    above = np.nonzero(totals >= target_per_1000)[0]
    if totals[0] >= target_per_1000 or len(above) == 0:
        return CalibrationResult(None, "unreachable", scan)
    hi = above[0]
    lo = hi - 1

    def excess(log_k0: float) -> float:
        return _evaluate((float(np.exp(log_k0)), climate, config))["total /1000"] - target_per_1000

    k0 = float(np.exp(brentq(excess, np.log(k0s[lo]), np.log(k0s[hi]), xtol=p.CAL_RTOL)))
    elasticity = float(np.log(totals[hi] / totals[lo]) / np.log(k0s[hi] / k0s[lo]))
    import_fraction = _evaluate((k0, climate, config))["imported fraction"]
    monotonic = bool(np.all(np.diff(totals) > 0))
    poorly = (elasticity < p.CAL_MIN_ELASTICITY or import_fraction > p.CAL_MAX_IMPORT_FRACTION
              or not monotonic)
    return CalibrationResult(k0, "found", scan, elasticity, import_fraction, poorly)
