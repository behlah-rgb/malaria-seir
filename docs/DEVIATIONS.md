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
