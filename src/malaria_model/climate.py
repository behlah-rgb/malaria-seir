"""Climate inputs: thermal response functions and synthetic T(t), R(t).

Temperature T in °C, rainfall R in mm/day, time t in days (day 0 = 1 Jan).
Formulas for a(T), gamma_m(T), mu_v(T) follow docs/SPEC.md §3.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from malaria_model import params as p


# ---------------------------------------------------------------------------
# Thermal response functions (SPEC §3)
# ---------------------------------------------------------------------------
def biting_rate(T: float) -> float:
    """Brière biting rate a(T) [bites per mosquito per day].

    a(T) = c_a * T * (T - T_0) * sqrt(T_m - T), with T in °C.
    """
    # DEVIATION: a(T) = 0 outside (T_0, T_m) to avoid NaN/negative, see DEVIATIONS.md #2
    if T <= p.T_0 or T >= p.T_M:
        return 0.0
    return p.C_A * T * (T - p.T_0) * np.sqrt(p.T_M - T)


def incubation_rate(T: float) -> float:
    """Parasite (sporogonic) development rate gamma_m(T) [1/day].

    gamma_m(T) = (T - T_min) / DD, with T in °C and DD in °C·day.
    """
    # DEVIATION: gamma_m floored at 0 below T_min, see DEVIATIONS.md #3
    return max(0.0, (T - p.T_MIN) / p.DD)


def vector_mortality(T: float) -> float:
    """Adult mosquito mortality mu_v(T) [1/day].

    mu_v(T) = 1 / (q_0 + q_1*T + q_2*T^2), with T in °C.
    """
    denominator = p.Q_0 + p.Q_1 * T + p.Q_2 * T**2  # [day]
    # DEVIATION: denominator floored at Q_DEN_MIN so mu_v <= 1/day, see DEVIATIONS.md #4
    return 1.0 / max(denominator, p.Q_DEN_MIN)


# ---------------------------------------------------------------------------
# Synthetic climate (SPEC §6 note 6)
# ---------------------------------------------------------------------------
def synthetic_temperature(n_days: int = p.N_DAYS) -> np.ndarray:
    """Daily temperature [°C] for days 0..n_days-1 (smooth seasonal cosine).

    T(t) = T_mean + T_amp * cos(2*pi*(t - T_peak_day) / 365).
    """
    t = np.arange(n_days, dtype=float)
    return p.T_MEAN + p.T_AMP * np.cos(2 * np.pi * (t - p.T_PEAK_DAY) / p.DAYS_PER_YEAR)


def synthetic_rainfall(n_days: int = p.N_DAYS, seed: int = p.RANDOM_SEED) -> np.ndarray:
    """Daily monsoonal rainfall [mm/day] for days 0..n_days-1.

    A dry-season background plus a Gaussian monsoon bump centred on
    R_peak_day, multiplied by log-normal daily noise (always > 0).
    """
    t = np.arange(n_days, dtype=float)
    mean_rain = p.R_DRY + p.R_PEAK * np.exp(-0.5 * ((t - p.R_PEAK_DAY) / p.R_WIDTH) ** 2)
    rng = np.random.default_rng(seed)
    noise = rng.lognormal(mean=0.0, sigma=p.R_NOISE_SD, size=n_days)
    return mean_rain * noise


@dataclass(frozen=True)
class Climate:
    """Daily climate series with lookup at any (fractional) day.

    Attributes:
        temperature: daily temperature [°C], index = day.
        rainfall: daily rainfall [mm/day], index = day.
    """

    temperature: np.ndarray
    rainfall: np.ndarray

    @property
    def days(self) -> np.ndarray:
        """Day index array [days]."""
        return np.arange(len(self.temperature), dtype=float)

    def T_at(self, t: float) -> float:
        """Temperature [°C] at time t [days], linearly interpolated between days."""
        return float(np.interp(t, self.days, self.temperature))

    def R_at(self, t: float) -> float:
        """Rainfall [mm/day] at time t [days], linearly interpolated between days."""
        return float(np.interp(t, self.days, self.rainfall))


def make_synthetic_climate(n_days: int = p.N_DAYS, seed: int = p.RANDOM_SEED) -> Climate:
    """Build the synthetic 365-day Climate (T in °C, R in mm/day)."""
    return Climate(synthetic_temperature(n_days), synthetic_rainfall(n_days, seed))
