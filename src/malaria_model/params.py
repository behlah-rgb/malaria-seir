"""All parameter values for the SEIR-Vector malaria model.

This is the ONLY place where numbers live. Equations in the other modules
refer to these names. Units: time in days, temperature in °C, rainfall in
mm/day, populations in individuals. All rates are per day.

Each value carries a comment with its source, or the label
"PLACEHOLDER - needs literature value".
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Section 1: Urban Drainage and Clogging Index (SPEC §1)
# ---------------------------------------------------------------------------
EPSILON: float = 0.001  # smoothing constant [-]; source: docs/SPEC.md §1

# ---------------------------------------------------------------------------
# Section 2: Aquatic carrying capacity and larval mortality (SPEC §2)
# ---------------------------------------------------------------------------
K_0: float = 500.0  # mosquitoes per (mm/day); PLACEHOLDER - needs literature value
#                     (chosen so the monsoon adult-mosquito:human ratio is ~1-5)
ETA: float = 0.5  # sensitivity of K_v to clogging Omega [-]; PLACEHOLDER - needs literature value
MU_BASE: float = 0.1  # baseline larval mortality [1/day]; PLACEHOLDER - needs literature value
#                       (commonly quoted range 0.05-0.3 /day)
MU_FLUSH: float = 0.005  # flushing coefficient [(1/day)/(mm/day)]; PLACEHOLDER - needs literature value
R_FLUSH: float = 15.0  # rainfall threshold for flushing [mm/day]; PLACEHOLDER - needs literature value

# ---------------------------------------------------------------------------
# Section 3: Thermal response functions (SPEC §3)
# ---------------------------------------------------------------------------
# Brière biting rate. Source: Mordecai et al. 2013, Ecology Letters
# (Brière fit for Anopheles biting rate) - verify exact values against the paper.
C_A: float = 2.03e-4  # Brière scale constant [1/(day·°C²·√°C)]
T_0: float = 11.7  # lower thermal limit for biting [°C]
T_M: float = 42.3  # upper thermal limit for biting [°C]

# Degree-day parasite development. Source: classic Detinova / Macdonald
# P. falciparum degree-day model (EIP = 111 / (T - 16) days).
T_MIN: float = 16.0  # minimum temperature for parasite development [°C]
DD: float = 111.0  # degree-days needed to complete the EIP [°C·day]

# Adult mosquito mortality, quadratic denominator. Source: Martens (1997),
# Anopheles daily survival p(T) = exp(-1/(-4.4 + 1.31 T - 0.03 T^2)).
Q_0: float = -4.4  # [day]
Q_1: float = 1.31  # [day/°C]
Q_2: float = -0.03  # [day/°C²]

# ---------------------------------------------------------------------------
# Section 5: Vector and human parameters (SPEC §5 glossary)
# ---------------------------------------------------------------------------
PHI_V: float = 10.0  # oviposition rate [female eggs/(adult·day)]; PLACEHOLDER - needs literature value
#                      (order of magnitude: ~100 eggs per 3-4 day gonotrophic cycle, half female)
THETA_A: float = 0.1  # aquatic-to-adult maturation [1/day]; PLACEHOLDER - needs literature value
#                       (~10 days egg->adult; general range 7-14 days)
BETA_VH: float = 0.48  # human->vector transmission prob. per bite [-];
#                        approx. Chitnis, Hyman & Cushing 2008 (Bull. Math. Biol.) - verify exact value
BETA_HV: float = 0.022  # vector->human transmission prob. per bite [-];
#                         approx. Chitnis, Hyman & Cushing 2008 baseline - verify exact value.
#                         Low end of quoted values (~0.01-0.5): OPEN QUESTION FOR PROFESSOR.

N_H0: float = 10_000.0  # initial human population of a ward [humans]; PLACEHOLDER - needs ward census
MU_H: float = 1.0 / (60.0 * 365.0)  # human natural mortality [1/day]; PLACEHOLDER - needs literature value
#                                     (60-year life expectancy, country-specific)
LAMBDA_H: float = MU_H * N_H0  # human recruitment [humans/day]; derived so the
#                                disease-free population stays at N_H0
ALPHA_H: float = 1.0 / 12.0  # human incubation rate E_h->I_h [1/day]; PLACEHOLDER - needs literature value
#                              (intrinsic incubation ~10-14 days)
GAMMA_H: float = 0.0035  # human recovery rate [1/day] (~285-day untreated infection);
#                          approx. Chitnis, Hyman & Cushing 2008 baseline; NEEDS VERIFICATION.
#                          Changed 2026-10-14 from unsourced 0.01, see PROGRESS.md Decisions.
DELTA_H: float = 1e-4  # disease-induced human mortality [1/day]; PLACEHOLDER - needs literature value
RHO: float = 1.0 / 365.0  # loss of immunity R_h->S_h [1/day]; PLACEHOLDER - needs literature value

# ---------------------------------------------------------------------------
# Numerical guards (approved deviations, see docs/DEVIATIONS.md)
# ---------------------------------------------------------------------------
K_V_MIN: float = 1.0  # floor on carrying capacity [mosquitoes]; DEVIATION #1
Q_DEN_MIN: float = 1.0  # floor on mu_v denominator [day] => mu_v <= 1/day; DEVIATION #4

# ---------------------------------------------------------------------------
# Synthetic climate (SPEC §6 note 6) - all synthetic, not real data
# ---------------------------------------------------------------------------
N_DAYS: int = 365  # simulation length [days]; day 0 = 1 January
DAYS_PER_YEAR: float = 365.0  # period of the seasonal cycle [days]
T_MEAN: float = 28.0  # mean temperature [°C]; synthetic
T_AMP: float = 4.0  # temperature amplitude [°C] -> range 24-32 °C; synthetic
T_PEAK_DAY: float = 135.0  # hottest day (mid-May, pre-monsoon) [day]; synthetic
R_DRY: float = 0.2  # background rainfall [mm/day]; synthetic
R_PEAK: float = 15.0  # monsoon peak mean rainfall [mm/day]; synthetic
R_PEAK_DAY: float = 212.0  # monsoon peak (late July) [day]; synthetic
R_WIDTH: float = 30.0  # monsoon width (std. dev.) [days]; synthetic
R_NOISE_SD: float = 0.5  # log-normal daily noise std. dev. (log scale) [-]; synthetic
RANDOM_SEED: int = 42  # fixed seed so the synthetic rainfall is reproducible

# ---------------------------------------------------------------------------
# Initial conditions (SPEC §6 note 7) - see PROGRESS.md "Decisions"
# ---------------------------------------------------------------------------
I_H0: float = 10.0  # seed infectious humans [humans]
E_H0: float = 0.0  # initial exposed humans [humans]
R_H0: float = 0.0  # initial recovered humans [humans]
E_V0: float = 0.0  # initial exposed mosquitoes [mosquitoes]
I_V0: float = 0.0  # initial infectious mosquitoes [mosquitoes]
# A_v(0) and S_v(0) are computed from the dry-season equilibrium in ode.initial_state().

# ---------------------------------------------------------------------------
# Ward profiles (D_d, M_i) - illustrative, not real wards
# ---------------------------------------------------------------------------
WARDS: dict[str, tuple[float, float]] = {
    "High infra / high maintenance": (0.8, 0.9),
    "Medium infra / low maintenance": (0.5, 0.3),
    "Poor infra / neglected": (0.1, 0.1),
}

# ---------------------------------------------------------------------------
# Heatmap sweep and solver settings
# ---------------------------------------------------------------------------
GRID_MIN: float = 0.1  # lowest D_d and M_i in the sweep [-]
GRID_MAX: float = 0.9  # highest D_d and M_i in the sweep [-]
GRID_RESOLUTION: int = 9  # number of points per axis (9 x 9 = 81 runs)
ODE_HMAX: float = 1.0  # max solver step [day] so no rainy day is skipped
ODE_RTOL: float = 1e-6  # relative tolerance for odeint
ODE_ATOL: float = 1e-6  # absolute tolerance for odeint [individuals]

# ---------------------------------------------------------------------------
# Spin-up (approved 2026-10-14, DEVIATION #5)
# ---------------------------------------------------------------------------
N_YEARS_TOTAL: int = 3  # years simulated with the climate repeated each year
#                         (years 1-2 = burn-in, discarded; year 3 is reported)

# ---------------------------------------------------------------------------
# Metrics and plotting
# ---------------------------------------------------------------------------
PER_POPULATION: float = 1000.0  # attack rate is reported per this many people
R0_THRESHOLD: float = 1.0  # epidemic threshold drawn on the R0(t) figure [-]
LOG_SCALE_RATIO: float = 10.0  # heatmaps use a log colour scale if max/min >= this

# ---------------------------------------------------------------------------
# Sensitivity analysis (SEPARATE from the main results)
# ---------------------------------------------------------------------------
SENS_GAMMA_H: list[float] = [0.0035, 0.005, 0.01]  # recovery rates tested [1/day]
SENS_BETA_HV: list[float] = [0.022, 0.05, 0.1]  # vector->human probabilities tested [-]

# ===========================================================================
# EXTENDED VARIANT ONLY (approved 2026-10-14; not used by the "spec" variant)
# ===========================================================================
MODEL_VARIANT: str = "extended"  # headline variant in main.py: "spec" or "extended"

# Rainfall memory (DEVIATION #6, #7)
TAU_RAIN: float = 10.0  # breeding-water retention time [days]; PLACEHOLDER - needs literature value
#                         (order of magnitude for puddles/drains; no specific source known)
R_EFF_MIN: float = 0.01  # numerical floor on R_eff [mm/day]; PLACEHOLDER - needs literature value
#                          (deliberately tiny: a guard, not a "permanent water" parameter)
OMEGA_LENGTHENS_TAU: bool = False  # switch: clogged drains retain water longer (OFF by default)
TAU_OMEGA_SLOPE: float = 0.1  # tau(Ω) = TAU_RAIN * (1 + slope * Ω) [1/unit Ω];
#                               PLACEHOLDER - needs literature value

# Importation of infections (DEVIATION #8)
IMPORT_PER_1000_PER_YEAR: float = 1.0  # imported infections [per 1,000 people per year];
#                                        PLACEHOLDER - needs literature value

# Carrying capacity scale for the extended variant
K_0_CALIBRATED: float | None = None  # calibrated K_0 [mosquitoes/(mm/day)]; None = not yet
#                                      calibrated (extended then uses K_0 above)

# Spin-up until convergence (DEVIATION #9)
SPINUP_TOL: float = 0.01  # stop when local attack rate changes < 1% year over year [-]
SPINUP_MAX_YEARS: int = 20  # cap on spin-up years

# K_0 calibration search (medium ward reference; target supplied by the user)
CALIBRATION_WARD: str = "Medium infra / low maintenance"
CAL_K0_MIN: float = 10.0  # lowest K_0 scanned [mosquitoes/(mm/day)]
CAL_K0_MAX: float = 1.0e6  # highest K_0 scanned [mosquitoes/(mm/day)]
CAL_SCAN_POINTS: int = 9  # log-spaced scan points
CAL_RTOL: float = 1e-3  # relative tolerance on calibrated K_0 [-]
CAL_MIN_ELASTICITY: float = 0.1  # d ln(API)/d ln(K_0) below this => "poorly identified" [-]
CAL_MAX_IMPORT_FRACTION: float = 0.5  # imported share above this => "poorly identified" [-]

# Ω analysis
OMEGA_SEARCH_MIN: float = 0.0  # lower bound for critical-Ω search [-]
OMEGA_SEARCH_MAX: float = 20.0  # upper bound for critical-Ω search [-]
OMEGA_CURVE_POINTS: int = 25  # Ω values on the R0-vs-Ω curve
OMEGA_CURVE_MIN: float = 0.05  # smallest Ω on the R0-vs-Ω curve (log-spaced) [-]
VECTOR_SPINUP_YEARS: int = 2  # years to settle vector dynamics before reading R0(t)
OMEGA_CONTOUR_LEVELS: list[float] = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]  # Ω contours on heatmaps

# Importation sensitivity (separate from main results)
SENS_IMPORT: list[float] = [0.0, 0.1, 1.0, 10.0]  # imported infections per 1,000 per year

# Parallel runs
N_WORKERS: int = 8  # processes for grid sweeps
