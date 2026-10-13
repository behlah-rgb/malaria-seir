# Deviations from docs/SPEC.md

Permanent record. Never delete or rewrite entries; reversals get a new entry.
Code markers: `# DEVIATION: ..., see DEVIATIONS.md #N`.

## #1 - Floor on carrying capacity K_v
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/drainage.py `carrying_capacity()`
- **Spec formula:** K_v = K_0 * (1 + eta * Ω) * R(t)
- **Code does:** K_v = max(K_0 * (1 + eta * Ω) * R(t), K_V_MIN), K_V_MIN = 1.0 mosquito (params.py)
- **Reason:** with R = 0 the term A_v / K_v in dA_v/dt divides by zero (SPEC §6 note 1).
  Never active with the current synthetic climate (R > 0 every day).
- **Approved by:** user

## #2 - Brière biting rate set to 0 outside its thermal limits
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/climate.py `biting_rate()`
- **Spec formula:** a(T) = c_a * T * (T - T_0) * sqrt(T_m - T)
- **Code does:** same formula for T_0 < T < T_m; a(T) = 0 otherwise
- **Reason:** formula gives NaN (T > T_m) or negative biting (T < T_0) (SPEC §6 note 2).
  Not active for the synthetic 24-32 °C climate.
- **Approved by:** user

## #3 - Parasite development rate floored at 0
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/climate.py `incubation_rate()`
- **Spec formula:** γ_m(T) = (T - T_min) / DD
- **Code does:** γ_m(T) = max(0, (T - T_min) / DD)
- **Reason:** negative development rate below T_min is not physical (SPEC §6 note 3).
  Not active for the synthetic 24-32 °C climate.
- **Approved by:** user

## #4 - Floor on the mosquito mortality denominator
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/climate.py `vector_mortality()`
- **Spec formula:** μ_v(T) = 1 / (q_0 + q_1*T + q_2*T^2)
- **Code does:** μ_v(T) = 1 / max(q_0 + q_1*T + q_2*T^2, Q_DEN_MIN), Q_DEN_MIN = 1.0 day (so μ_v <= 1/day)
- **Reason:** with the Martens coefficients the denominator is <= 0 below ~3.7 °C and above
  ~40 °C, giving infinite or negative mortality (SPEC §6 note 4). Not active for 24-32 °C.
- **Approved by:** user

## #5 - Spin-up (burn-in) before the reported 365 days
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/ode.py `simulate_with_spinup()` (used by scenarios.py,
  optimize.py, sensitivity.py)
- **Spec says:** 365-day trajectories from the chosen initial conditions (SPEC §6 note 6).
- **Code does:** simulates 3 years with the synthetic 365-day climate repeated
  (params.N_YEARS_TOTAL = 3), discards years 1-2, and reports year 3 (re-indexed to days 0-364).
  All metrics (peak I_h, attack rate, R0(t)) are computed on year 3 only. The equations are unchanged.
- **Reason:** in the first run, peak I_h always equalled the arbitrary day-0 seed (I_h = 10),
  so the result reflected the initial conditions, not the drainage. Spin-up removes most of that
  dependence. `simulate()` (single year from day 0) is still available and used in tests.
- **Approved by:** user

## #6 - Extended variant: carrying capacity driven by rainfall with memory
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/ode.py `build_forcing()`; climate.py `effective_rainfall()`
- **Spec formula:** K_v = K_0 * (1 + eta * Ω) * R(t)
- **Code does (extended only):** K_v = K_0 * (1 + eta * Ω) * max(R_eff(t), R_EFF_MIN), where
  R_eff[d] = (1 - w) R_eff[d-1] + w R[d], w = 1 - exp(-1/τ), τ = TAU_RAIN (10 days, placeholder),
  computed periodically over the repeating climate. R_EFF_MIN = 0.01 mm/day is a numerical floor.
  Larval flushing μ_A still uses same-day R(t). The spec variant is unchanged.
- **Reason:** breeding water persists for days after rain; same-day R makes habitat vanish instantly.
- **Approved by:** user

## #7 - Extended variant: optional Ω-dependent retention time (OFF by default)
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/config.py `ModelConfig.tau()`
- **Spec:** no retention time exists in SPEC.
- **Code does (extended, only if OMEGA_LENGTHENS_TAU = True):** τ(Ω) = TAU_RAIN * (1 + TAU_OMEGA_SLOPE * Ω).
- **Reason:** clogged drains plausibly retain water longer. Default OFF, so current results do not use it.
- **Approved by:** user

## #8 - Extended variant: imported infections
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/ode.py `human_rhs()`
- **Spec formulas:** dS_h/dt and dE_h/dt as in SPEC §5 (no importation term)
- **Code does (extended only):** subtracts ι·S_h from dS_h/dt and adds it to dE_h/dt, with
  ι = IMPORT_PER_1000_PER_YEAR / 1000 / 365 per day (1 per 1,000/yr, placeholder). Pure transfer:
  N_h balance unchanged (tested). In spec, import_rate = 0, so the term vanishes.
- **Reason:** urban wards receive infections from travel; without them, infection must survive the
  dry season with no outside source.
- **Approved by:** user

## #9 - Spin-up until convergence
- **Date:** 2026-10-14
- **File / function:** src/malaria_model/ode.py `simulate_converged()`, used by both variants
  in main.py (#5's fixed 3-year spin-up remains available and is kept, not replaced)
- **Spec says:** 365-day trajectories (SPEC §6 note 6).
- **Code does:** simulates year by year (climate repeating) until LOCALLY ACQUIRED infections change by
  < SPINUP_TOL = 1% year over year, cap SPINUP_MAX_YEARS = 20; reports the final year, the years run,
  whether it converged, and the local growth factor.
- **Reason:** a fixed 3 years did not reach a steady pattern; local infections are used because
  imported infections would mask whether transmission is self-sustaining.
- **Approved by:** user
