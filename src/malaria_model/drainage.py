"""Urban drainage: clogging index, carrying capacity, larval mortality.

Formulas follow docs/SPEC.md §1-2. Rainfall R in mm/day.
"""

from __future__ import annotations

from malaria_model import params as p


def clogging_index(D_d: float, M_i: float) -> float:
    """Clogging index Omega [-] from drainage density D_d [-] and maintenance M_i [-].

    Omega = (1 - M_i) / (D_d + epsilon).
    """
    return (1.0 - M_i) / (D_d + p.EPSILON)


def carrying_capacity(R: float, omega: float, k0: float | None = None) -> float:
    """Aquatic carrying capacity K_v [mosquito larvae] for rainfall R [mm/day].

    K_v = K_0 * (1 + eta * Omega) * R. k0 overrides params.K_0
    [mosquitoes/(mm/day)] (used by the extended variant and calibration).
    """
    K_0 = p.K_0 if k0 is None else k0
    K_v = K_0 * (1.0 + p.ETA * omega) * R
    # DEVIATION: K_v floored at K_V_MIN to avoid division by zero on dry days, see DEVIATIONS.md #1
    return max(K_v, p.K_V_MIN)


def larval_mortality(R: float, omega: float) -> float:
    """Larval mortality mu_A [1/day] including rainfall flushing.

    mu_A = mu_base + mu_flush * max(0, (R - R_flush) / (Omega + epsilon)).
    """
    return p.MU_BASE + p.MU_FLUSH * max(0.0, (R - p.R_FLUSH) / (omega + p.EPSILON))
