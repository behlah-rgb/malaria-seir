# Progress

## Current status
Two model variants run with `python main.py` (~130 s): "spec" (literal SPEC + guards #1-#4) and
"extended" (rainfall memory #6, importation #8). Both use spin-up to convergence (#9). 42/42 tests
pass. K_0 is NOT calibrated (no target given yet). Synthetic climate; most parameters are placeholders.
Key result: peak-R0 threshold Ω* ≈ 0.04-0.08 (outside the grid), but local infections only persist
above Ω ≈ 8.7, so only the poor ward (Ω 8.9) sustains transmission in either variant.

## Change log
### 2026-10-14 - Spec/extended variants, convergence spin-up, Ω analysis, calibration code
- New: config.py (ModelConfig, variant switch), calibrate.py (K_0 only; built, not run),
  omega_analysis.py (R0 vs Ω, Ω*, persistence Ω, min M_i), parallel.py (process pool),
  tests/test_extended.py, tests/test_omega.py.
- Changed: params.py (extended-only block), climate.py (effective_rainfall), drainage.py (k0 arg),
  ode.py (Forcing, importation, simulate_converged), metrics.py (local/imported infections, EIR,
  mosquitoes per human), scenarios.py, optimize.py (parallel sweep), sensitivity.py (+importation),
  plotting.py (subtitles with variant/calibration, Ω contours, Ω figures), main.py (--calibrate).
- Deviations #6-#9 logged.
- Tests: 42 passed (regression: spec + fixed 3-yr spin-up reproduces the previous numbers; spec
  output unchanged when extended-only params change).
- Results, low / medium / high Ω ward:
  - spec: attack /1000 5.7e-10 / 3.1e-8 / 1.81; local growth 0.36 / 0.43 / 1.02 per year; NO ward
    converged in 20 yr (two dying out, poor ward still growing ~2%/yr); 0/81 grid cells converged.
  - extended: attack /1000 1.27 / 1.52 / 21.3, of which local 0.28 / 0.53 / 20.4 and imported
    ~1.0 each; EIR 0.013 / 0.024 / 0.96 per person per yr; mosquitoes per human (mean) 0.17 /
    0.27 / 0.87; poor ward not converged (growth 1.03/yr); 79/81 grid cells converged.
  - In the low and medium wards most extended infections are IMPORTED (78% / 65%).
  - Ω* (peak R0 = 1): spec 0.0437, extended 0.0825, both below the smallest grid Ω (0.111), so
    min M_i for "R0 < 1 all year" is 0.93-0.996. Persistence Ω (local growth = 1, import off):
    spec 8.67, extended 8.76, so only D_d = 0.1 needs M_i >= ~0.12.
  - Rainfall memory barely changes mosquito numbers (smoother, slightly lower peaks); the large
    spec-vs-extended difference in infections is driven by importation.
  - Sensitivity: ward ranking by Ω holds in all 9 γ_h × β_hv runs and all 4 importation rates,
    for total and for local attack rate.

### 2026-10-14 - Diagnosis of the flat first run + spin-up, new metric, R0, sensitivity
- Diagnosis (read-only): the main cause was weak transmission (annual-mean R0 < 1 in every ward;
  weakest link K_hv = 0.068 humans infected per infectious mosquito). Dry-season start played a
  minor part; adding infectious mosquitoes made no difference.
- ode.py: `simulate_with_spinup()` (DEVIATION #5); climate.py: `Climate.repeat()`.
- New: metrics.py (peak I_h, day of peak, new infections = ∫α_h E_h dt, attack rate per 1,000),
  r0.py (next-generation-matrix R0(t)), sensitivity.py (γ_h × β_hv, separate output).
- scenarios.py / optimize.py now use year 3; two heatmaps (peak I_h primary, attack rate
  supplementary, log scale when values span ≥10×); new ward_R0.png; sensitivity figure in
  results/figures/sensitivity/.
- params.py: GAMMA_H 0.01 → 0.0035; new spin-up/metric/sensitivity constants.
- Tests: `pytest` → 26 passed (6 new in tests/test_metrics.py).
- Results (year 3), low / medium / high Ω: peak I_h 1.30 / 1.86 / 12.4 (days 0 / 0 / 301);
  attack rate per 1,000: 0.0198 / 0.0491 / 1.21; max R0(t) 1.08 / 1.42 / 2.56;
  days with R0 > 1: 15 / 65 / 113. Heatmaps: both metrics rise monotonically as D_d and M_i fall.
  In the low and medium wards the peak is on day 0 (infection still declining from the year before).
- Sensitivity: all 9 (γ_h, β_hv) combinations keep the ranking high Ω > medium > low;
  magnitudes range from 5e-5 to 593 per 1,000.

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
- 2026-10-14 Two variants selected by params.MODEL_VARIANT (default "extended" for the ward figures);
  heatmaps, Ω analysis and comparison always run both.
- 2026-10-14 Calibration: K_0 only, medium ward, extended variant, converged spin-up; target is TOTAL
  reported API (imported + local) per 1,000/yr, as the user specified. β_hv, β_vh, γ_h untouched. The
  scan also prints local incidence and imported fraction; "poorly identified" is flagged if the
  elasticity d ln(API)/d ln(K_0) < 0.1, the imported share > 0.5, or the scan is not monotonic.
  NOT yet run: awaiting the target. Result is never written to params.py automatically.
- 2026-10-14 Growth factor and convergence use LOCALLY acquired infections (imports would mask
  persistence). The persistence threshold is computed with importation off.
- 2026-10-14 Added the persistence threshold (local growth = 1) next to Ω* (peak R0 = 1), because
  peak R0 > 1 for a few days does not make infection persist; the two differ by ~100×.
- 2026-10-14 The 81-cell Ω scatter is an illustration that outcomes depend on D_d, M_i only through Ω
  (a mathematical consequence of the model), not a validation.
- 2026-10-14 Local vs imported infections are counted on entry to E_h; the reported total is
  ∫α_h E_h dt (exit from E_h). They agree within 5% (tested).
- 2026-10-14 Spin-up: 3 years with repeating climate, report year 3 (also DEVIATIONS #5).
  Reason: remove the dependence on the arbitrary day-0 seed.
- 2026-10-14 γ_h changed 0.01 → 0.0035/day ("approx. Chitnis, Hyman & Cushing 2008 baseline;
  NEEDS VERIFICATION"). Reason: the original value was unsourced. It was replaced with a
  literature-anchored value after the first run, NOT to produce a target result. β_hv deliberately
  left at 0.022.
- 2026-10-14 Metrics: peak I_h (SPEC §6 note 8) stays primary, now on year 3. Attack rate per 1,000
  (∫α_h E_h dt / N_h(day 0 of year 3) × 1000) is supplementary. Computed from daily output, so
  no new ODE state.
- 2026-10-14 R0(t) uses the next-generation matrix with the simulated N_v(t)/N_h(t), convention
  R0 = √(K_hv·K_vh) (formula in src/malaria_model/r0.py).
- 2026-10-14 Option (b), infectious mosquitoes in the initial conditions: rejected by the user
  (no effect in the diagnostic run).
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

## Open questions for professor
- β_hv = 0.022 is at the low end of quoted values (~0.01–0.5); which source and value should we use?
- γ_h = 0.0035: verify against Chitnis et al. 2008 or another source.
- Should treatment be modelled? Treated infections recover in weeks, not months; this
  changes results hugely (see the sensitivity analysis).
- Which heatmap metric is preferred: peak I_h (spec) or attack rate per 1,000?

## Open questions
- Calibration target (annual parasite incidence per 1,000) and its source: needed before calibrating K_0.
- New PLACEHOLDERS (extended variant): TAU_RAIN = 10 d, R_EFF_MIN = 0.01 mm/day, TAU_OMEGA_SLOPE = 0.1
  (switch OFF), IMPORT_PER_1000_PER_YEAR = 1.0; calibration search settings CAL_K0_MIN = 10,
  CAL_K0_MAX = 1e6, CAL_SCAN_POINTS = 9, CAL_RTOL = 1e-3, CAL_MIN_ELASTICITY = 0.1,
  CAL_MAX_IMPORT_FRACTION = 0.5; SPINUP_TOL = 1%, SPINUP_MAX_YEARS = 20.
- Importation dominates low-Ω wards at 1 per 1,000/yr; its real value matters a lot.
- Poor ward still growing after 20 years in both variants (not converged): longer cap, or accept?
- Which "safe" threshold should the Ω analysis emphasise: peak R0 < 1 or local growth < 1?
- Verify cited values: Mordecai 2013 (c_a, T_0, T_m), Chitnis et al. 2008 (β_vh).
- K_0, eta, μ_flush, R_flush, φ_v, θ_A, μ_base are still placeholders.

## Next step
User supplies the calibration target → run `python main.py --calibrate TARGET`, review
identifiability, then (if approved) enter K_0_CALIBRATED in params.py.
