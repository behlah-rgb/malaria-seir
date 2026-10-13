# Progress

## Current status
Full model runs end to end with `python main.py` on SYNTHETIC climate (2026-10-14).
20/20 tests pass. Most parameter values are placeholders (see src/malaria_model/params.py).
**Key finding:** with current parameters no ward has an outbreak; peak I_h = 10 (the seed,
day 0) everywhere, so the heatmap is flat. Not tuned, awaiting decision (see Open questions).

## Change log
### 2026-10-14 - First complete build
- Added src/malaria_model/: params.py, climate.py, drainage.py, ode.py, scenarios.py,
  optimize.py, plotting.py; main.py; pyproject.toml (pytest path only); tests/ (3 files).
- Why: runnable demo of docs/SPEC.md for the professor.
- Deviations #1-#4 approved and logged in docs/DEVIATIONS.md (guards that are never
  active with the synthetic climate).
- Tests: `pytest` -> 20 passed. `python main.py` -> 3 figures in results/figures/, sweep ~12-16 s.
- Results: peak I_h = 10.0 on day 0 for all 3 wards and all 81 heatmap cells.
  Peak adult mosquitoes: 7,831 (low Ω) / 13,549 (medium) / 43,836 (high Ω).
  Poor ward I_h shows a monsoon bump (~2.1 around day 270) and ends the year at 1.15 vs 0.36 (low Ω).
  Diagnostic R0 (not in code): max 0.65 / 0.85 / 1.53; only the poor ward has R0 > 1 (75 days).

## Decisions
- Initial conditions: N_h = 10,000, I_h = 10, others 0; A_v(0) = K_v(R(0), Ω),
  S_v(0) = θ_A·A_v(0)/μ_v(T(0)). Reason: seed an outbreak; avoid an artificial day-1 jump in vectors.
- Λ_h = μ_h·N_h0 so the disease-free population is stable.
- Synthetic climate: T cosine 24-32 °C peaking day 135; R = dry 0.2 + Gaussian monsoon
  (peak 15 mm/day, day 212, width 30 d) × log-normal noise (sd 0.5, seed 42); ~1,357 mm/yr.
  Reason: user's request; R > 0 every day.
- T(t), R(t) linearly interpolated between days; odeint hmax = 1 day, rtol = atol = 1e-6.
  Numerical choices, not spec changes.
- Ward profiles (D_d, M_i): (0.8, 0.9) Ω=0.125; (0.5, 0.3) Ω=1.397; (0.1, 0.1) Ω=8.911.
- States are not clipped to >= 0 (tests allow -1e-6 round-off; none observed).

## Open questions
- Peak-I_h metric is degenerate (always the day-0 seed). Options for user/professor:
  measure peak after a burn-in year, use max over the monsoon only, use cumulative
  incidence, or review placeholder values (γ_h, β, K_0, eta) against literature. Not tuned.
- Verify cited values: Mordecai 2013 (c_a, T_0, T_m), Chitnis et al. 2008 (β_hv, β_vh).

## Next step
Decide how to handle the flat peak-I_h result (see Open questions), then source literature values.


- [14th Oct, 2026] CONFIRMED: Ω affects larvae in two reinforcing ways, raising K_v via (1 + eta*Ω) and reducing flushing via division by (Ω + epsilon). This is intended. Do not treat as a bug.