# Chapter 4: Implementation, Results and Analysis

[[INTRO]]
This chapter describes how the design of Chapter 3 was implemented and tested, and what the simulations show. It covers the software structure and how to run it, the testing and verification process, the results for three illustrative wards and an 81-cell drainage grid, two threshold analyses and the sensitivity runs. It also describes the iterations made after the first run and closes with the advantages, limitations and possible applications of the model. **Three conditions apply to every result in this chapter:**

- The climate is synthetic: invented temperature and rainfall series, not observations.
- Most parameter values are placeholders without a confirmed literature source.
- The habitat scale K_0 is uncalibrated.

The results therefore show how the model behaves. They are not findings about any real city. All result numbers are taken from the project's model report (docs/MODEL_REPORT.md), which was produced from a full run of the model with all 42 tests passing.

## 4.1 Implementation

### 4.1.1 Software structure

The model is implemented in Python as a package, `src/malaria_model/`, with one module per responsibility ([[REF:modules]]). A single entry script, `main.py`, runs all experiments and writes the figures. The ODE system is solved with `scipy.integrate.odeint`:

- time step at most 1 day
- relative and absolute tolerance 10⁻⁶
- daily temperature and rainfall linearly interpolated between days

[[TAB:modules|Module map of the simulation package]]

| Module | Role |
|---|---|
| params.py | Every parameter value, each with its source or a PLACEHOLDER label |
| config.py | Chooses the variant (spec / extended) and the spin-up mode |
| climate.py | Thermal functions a(T), γ_m(T), μ_v(T); synthetic T(t) and R(t); rainfall with memory |
| drainage.py | Clogging Index Ω, carrying capacity K_v, larval mortality μ_A |
| ode.py | The 8 equations; simulation; spin-up |
| metrics.py | Peak I_h, attack rate, local vs imported infections, EIR |
| r0.py | R0(t) from the next-generation matrix |
| scenarios.py | Runs the three wards and builds the summary table |
| optimize.py | The 81-cell D_d × M_i sweep (run in parallel) |
| omega_analysis.py | R0 vs Ω, Ω\*, persistence threshold, minimum M_i |
| sensitivity.py | γ_h × β_hv and importation sensitivity runs |
| calibrate.py | K_0 calibration (built and tested; not run, no target yet) |
| plotting.py | All figures |
| parallel.py | Runs grid cells in parallel processes |

### 4.1.2 Environment and how to run

The project runs in a Python 3.14 virtual environment with package versions pinned in `requirements.txt`. The random seed for the synthetic rainfall is fixed (42), so every run is identical. From the project folder:

- `.venv/bin/python -m pytest` runs the 42 automated tests.
- `.venv/bin/python main.py` runs all experiments and writes the figures to `results/figures/`. The recorded run took 127 s.
- `.venv/bin/python main.py --calibrate X` calibrates K_0 to a target of X infections per 1,000 per year. This has not been run.

The model was developed in versions recorded in git: v1 to v1.3 on 14 October 2026, after the project skeleton and specification were committed on 13 October 2026. Section 4.4 describes the development steps.

[[PH: name the student(s) who implemented each module — not recorded in the project files]]

## 4.2 Testing, validation and verification

### 4.2.1 Test plan

Verification is by automated tests, written with pytest and run after every change. The suite has 42 tests in six files ([[REF:tests]]). The number of tests per file and the descriptions below were taken from the test function names in each file.

[[TAB:tests|Automated test suite]]

| Test file | Tests | What is checked |
|---|---|---|
| test_drainage.py | 6 | Ω, K_v and μ_A against hand-calculated values; Ω rises when maintenance or drainage falls; K_v floor on a dry day; flushing only above R_flush |
| test_thermal.py | 8 | a(T), γ_m(T) and μ_v(T) against hand-calculated values; guards outside the valid range; synthetic climate ranges; interpolation between days |
| test_ode.py | 6 | No NaN or infinite values; no negative compartments; a disease-free start stays disease-free; human population balance |
| test_metrics.py | 6 | Climate repetition and spin-up; attack rate, peak and day of peak against hand values; R0 from the next-generation matrix against a hand value |
| test_extended.py | 12 | Regression of the spec variant; spec unaffected by extended-only parameters; no NaN or negative values; importation keeps the population total unchanged; local/imported split; rainfall-memory properties; retention-time switch; spin-up convergence and cap; calibration round-trip |
| test_omega.py | 4 | Minimum maintenance against hand values; Ω\* and the persistence threshold are roots and correctly ordered |
| **Total** | **42** | **All passing in the recorded run** |

Two tests protect the approved specification:

- **Regression test.** The spec variant with the fixed 3-year spin-up reproduces the numbers of the earlier run exactly.
- **Spec-isolation test.** Changing extended-only parameters does not change the spec output.

### 4.2.2 Specification compliance

Section 3.3.6 describes the process for departures from the specification. The project rules require that, before any task is finished, every `# DEVIATION:` marker in the source code is checked against the deviation log. When this report was drafted there were nine markers in the code and nine log entries (#1 to #9) [[PH: confirm the marker-to-entry match by reviewing each marker]].

### 4.2.3 Validation

**The model has not been validated against real data.** No malaria case data or real climate data has been used yet, and K_0 has not been calibrated. The checks above verify that the code implements the specification correctly. They do not show that the model describes a real city.

## 4.3 Results and analysis

**How to read the numbers:**

- **Attack rate:** new infections per 1,000 people during the reported year.
- **EIR:** infectious bites per person per year.
- **Peak I_h:** the largest number of people infectious at the same time, out of 10,000.
- **Local growth:** locally acquired infections this year divided by last year. Below 1 means dying out; above 1 means growing.
- **R0(t):** how many new infections one case would cause at day t's temperature and mosquito density.

### 4.3.1 Ward summaries

[[PH: name the student(s) who produced this analysis]]

[[REF:wardspec]] and [[REF:wardext]] summarise the final reported year for each illustrative ward in the spec and extended variants.

[[TAB:wardspec|Per-ward summary, spec variant (final reported year; uncalibrated K_0 = 500; placeholder parameters)]]

| Ward (Ω) | Mosquitoes per human (mean / peak) | EIR per year | Attack per 1,000 | Peak I_h (day) | Local growth | R0 max / mean | Spin-up | Converged |
|---|---|---|---|---|---|---|---|---|
| High infra (0.125) | 0.157 / 0.783 | 2.6×10⁻¹¹ | 5.74×10⁻¹⁰ | 3.76×10⁻⁸ (day 0) | 0.36 | 1.08 / 0.357 | 20 yr | No |
| Medium (1.4) | 0.257 / 1.35 | 1.4×10⁻⁹ | 3.09×10⁻⁸ | 1.17×10⁻⁶ (day 0) | 0.432 | 1.42 / 0.455 | 20 yr | No |
| Poor (8.91) | 0.826 / 4.39 | 0.0826 | 1.81 | 18.5 (day 301) | 1.02 | 2.56 / 0.817 | 20 yr | No |

[[TAB:wardext|Per-ward summary, extended variant (final reported year; uncalibrated K_0 = 500; placeholder parameters; 1 imported infection per 1,000 per year)]]

| Ward (Ω) | Mosquitoes per human (mean / peak) | EIR per year | Attack per 1,000 (local + imported) | Peak I_h (day) | Local growth | R0 max / mean | Spin-up | Converged |
|---|---|---|---|---|---|---|---|---|
| High infra (0.125) | 0.166 / 0.715 | 0.0127 | 1.27 (0.28 + 0.995) | 10.4 (day 304) | 1 | 1.02 / 0.364 | 3 yr | Yes |
| Medium (1.4) | 0.268 / 1.16 | 0.0242 | 1.52 (0.531 + 0.995) | 12.9 (day 305) | 1.01 | 1.3 / 0.461 | 5 yr | Yes |
| Poor (8.91) | 0.866 / 3.77 | 0.961 | 21.3 (20.4 + 0.962) | 212 (day 310) | 1.03 | 2.34 / 0.829 | 20 yr | No |

**What the tables show.**

- In both variants, every column rises with Ω.
- In the spec variant the two better wards are effectively extinct, with about 10⁻⁸ and 10⁻⁶ infectious people, and are shrinking each year (growth 0.36 and 0.432).
- In the extended variant, imported infections keep the better wards at a low, steady level, and most of their infections are imported: about 78% in the best ward and 65% in the medium ward. In the poor ward only about 4.5% is imported.

**What not to conclude.**

- The absolute numbers are not predictions, because K_0 and most parameters are placeholders.
- The peak in late October to early November (days 301–310) reflects the timing of the synthetic monsoon, not any real season.
- The poor ward did not converge within the 20-year spin-up in either variant, so its values are not a steady state.

### 4.3.2 Ward time series (extended variant)

[[PH: name the student(s) who produced this analysis]]

[[REF:wardinf]], [[REF:wardvec]] and [[REF:wardr0]] follow the three wards through the reported year in the extended variant.

[[FIG:wardinf|ward_infections.png|Infectious humans I_h by ward through the reported year, with temperature and rainfall (extended variant)]]

- **What it shows:** infectious humans through the reported year in each ward, with T(t) and R(t) in the lower panels.
- **Key observation:** the poor ward's I_h rises after the monsoon and peaks around day 310, while the other two wards stay low and flat.
- **What not to conclude:** that the seasonal timing matches any real city. The climate is synthetic.

[[FIG:wardvec|ward_vectors.png|Adult mosquitoes N_v by ward (extended variant)]]

- **What it shows:** adult mosquito numbers follow the monsoon.
- **Key observation:** the poor ward's peak is about 5 times the best ward's (3.77 vs 0.715 peak mosquitoes per human), which is the direct effect of Ω on the carrying capacity.
- **What not to conclude:** real mosquito densities. They scale directly with the uncalibrated K_0.

[[FIG:wardr0|ward_R0.png|Time-varying reproduction number R0(t) by ward, with the line R0 = 1 (extended variant)]]

- **What it shows:** R0(t), computed from the next-generation matrix as R0 = √(K_hv·K_vh). K_hv is the number of humans infected per infectious mosquito, and K_vh the number of mosquitoes infected per infectious human.
- **Key observation:** R0(t) exceeds 1 only during the monsoon. The peaks are 1.02 (best), 1.3 (medium) and 2.34 (poor), while the year-round means are all below 1 (0.364, 0.461 and 0.829).
- **What not to conclude:** that R0(t) > 1 means an outbreak. The best ward briefly exceeds 1, yet its local infections do not grow (Section 4.3.4).

### 4.3.3 Drainage-scenario heatmaps

[[PH: name the student(s) who produced this analysis]]

[[REF:hmspecpeak]] and [[REF:hmspecatt]] show the 81-cell drainage grid for the spec variant, and [[REF:hmextpeak]] and [[REF:hmextatt]] for the extended variant.

[[FIG:hmspecpeak|heatmap_spec_peak_Ih.png|Peak I_h over drainage density D_d × maintenance M_i, spec variant (log colour scale; dashed lines are contours of equal Ω)]]

[[FIG:hmspecatt|heatmap_spec_attack_rate.png|Attack rate per 1,000 over D_d × M_i, spec variant]]

[[FIG:hmextpeak|heatmap_extended_peak_Ih.png|Peak I_h over D_d × M_i, extended variant]]

[[FIG:hmextatt|heatmap_extended_attack_rate.png|Attack rate per 1,000 over D_d × M_i, extended variant]]

- **What they show:** each of the 81 cells is one (D_d, M_i) combination, coloured by the outcome in the reported year. The colour scale is logarithmic because values span many orders of magnitude. In the spec variant the attack rate runs from 5.4×10⁻¹⁰ in the smallest cell (read from the figure) up to 1.8 per 1,000.
- **Key observations:**
  - The worst cell is always bottom-left (D_d = 0.1, M_i = 0.1).
  - Outcomes change along the contours of equal Ω, not along rows or columns separately.
  - In the extended variant most cells sit near 1.3–1.5 per 1,000, close to the importation level.
- **What not to conclude:** that the cells are independent evidence. They are 81 points on one curve (Section 4.3.5). The “safe” region below Ω\* lies outside this grid for both variants.

### 4.3.4 Two thresholds: peak R0 = 1 vs persistence

[[PH: name the student(s) who produced this analysis]]

[[REF:r0omega]] plots the yearly peak and mean of R0(t) against Ω for both variants, with Ω\* and the persistence thresholds marked; [[REF:thresholds]] lists the threshold values.

[[FIG:r0omega|r0_vs_omega.png|Peak and mean R0(t) against Ω for both variants, with Ω* (shaded safe zone) and the persistence thresholds marked]]

[[TAB:thresholds|Threshold values of the Clogging Index Ω]]

| Threshold | Meaning | Spec | Extended |
|---|---|---|---|
| Ω\* (peak R0(t) = 1) | Below this, R0 never exceeds 1 at any time of year | 0.04367 | 0.08253 |
| Persistence Ω (local growth = 1, imports off) | Below this, local infections shrink year to year | 8.673 | 8.761 |
| Ratio | | ≈ 199× | ≈ 106× |

From Ω ≤ threshold, the minimum maintenance needed at each drainage density is M_i ≥ 1 − threshold × (D_d + ε) ([[REF:minmi]]).

[[TAB:minmi|Minimum maintenance M_i needed at each drainage density D_d]]

| D_d | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|
| Min M_i for peak R0 < 1 (spec) | 0.996 | 0.991 | 0.987 | 0.982 | 0.978 | 0.974 | 0.969 | 0.965 | 0.961 |
| Min M_i for peak R0 < 1 (extended) | 0.992 | 0.983 | 0.975 | 0.967 | 0.959 | 0.95 | 0.942 | 0.934 | 0.926 |
| Min M_i for no growth (spec) | 0.124 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Min M_i for no growth (extended) | 0.115 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

- **What it shows:** two different definitions of a “safe” drainage condition. R0(t) is a snapshot. Exceeding 1 briefly during the monsoon peak lets infections grow for a few weeks, but they shrink for the rest of the year, when R0(t) is well below 1 (yearly means 0.36–0.83). Persistence depends on the balance over the whole year. The peak criterion is therefore very cautious, and the persistence criterion much less so.
- **Key observation:** only drainage density D_d = 0.1 needs any maintenance (about M_i ≥ 0.12) to stop local persistence. Keeping peak R0 below 1 all year needs M_i between 0.93 and 0.996.
- **What not to conclude:** a policy recommendation. Both thresholds depend on placeholder parameters, and which threshold counts as “safe” is an open question for the professor.

### 4.3.5 Dependence on Ω only

[[PH: name the student(s) who produced this analysis]]

[[REF:omegascatter]] plots the outcome of every grid cell against its value of Ω.

[[FIG:omegascatter|omega_scatter.png|Outcome of all 81 grid cells plotted against Ω]]

- **What it shows:** all 81 cells fall on a single curve per variant when plotted against Ω.
- **Why:** in the equations, D_d and M_i appear only inside Ω, in K_v and μ_A. Two wards with the same Ω therefore have identical simulations.
- **What not to conclude:** that this validates the model. It is a mathematical consequence of the model structure. It also means the model cannot separate “build more drains” from “maintain existing drains better” except through their combined effect on Ω.

### 4.3.6 Spec vs extended variant

[[PH: name the student(s) who produced this analysis]]

[[REF:variants]] compares the two variants ward by ward.

[[FIG:variants|variant_comparison.png|Spec vs extended variant by ward: I_h on a log scale (top) and mosquitoes per human (bottom)]]

- **What it shows:** the mosquito curves of the two variants are almost identical. Rainfall memory only smooths and slightly delays them: the peaks are 0.715 vs 0.783 mosquitoes per human for the best ward and 3.77 vs 4.39 for the poor ward.
- **Key observation:** the large difference in I_h comes from importation, not from rainfall memory. With imports set to 0, the extended best ward falls to an attack rate of 5.68×10⁻¹⁰ per 1,000, the same order as the spec variant (5.74×10⁻¹⁰).
- **What not to conclude:** that rainfall memory is unimportant in general. Its retention time (10 days) is a placeholder, and the synthetic rainfall is positive every day.

### 4.3.7 Sensitivity analyses

[[PH: name the student(s) who produced this analysis]]

[[REF:sens]] shows how the attack rate responds to the two most uncertain transmission parameters.

[[FIG:sens|sensitivity_attack_rate.png|Sensitivity of the attack rate to the recovery rate γ_h and the vector-to-human transmission probability β_hv (extended variant)]]

**Recovery rate × transmission probability.** Each of γ_h ∈ {0.0035, 0.005, 0.01} per day and β_hv ∈ {0.022, 0.05, 0.1} was tested in all 9 combinations.

- **What it shows:** the ward ranking (higher Ω gives a higher attack rate) held in all 9 combinations.
- **Key observation:** the magnitudes vary enormously. The poor ward's attack rate ranges from 1.65 per 1,000 (γ_h = 0.01, β_hv = 0.022) to 404 per 1,000 (γ_h = 0.0035, β_hv = 0.1), and the best ward's from 1.08 to 8.61.
- **What not to conclude:** any particular attack rate. The direction of the effect is robust to these two parameters; its size is not.

**Importation rate** ([[REF:importsens]]).

[[TAB:importsens|Attack rate per 1,000 for different importation rates, extended variant: total (local)]]

| Imports per 1,000 per year | Best ward | Medium ward | Poor ward | Ranking holds (total / local) |
|---|---|---|---|---|
| 0 | 5.68×10⁻¹⁰ (5.65×10⁻¹⁰) | 2.69×10⁻⁸ (2.68×10⁻⁸) | 1.47 (1.47) | Yes / yes |
| 0.1 | 0.128 (0.0283) | 0.154 (0.054) | 4.3 (4.21) | Yes / yes |
| 1 | 1.27 (0.28) | 1.52 (0.531) | 21.3 (20.4) | Yes / yes |
| 10 | 12.4 (2.65) | 14.6 (4.93) | 68.4 (59.7) | Yes / yes |

- For the better wards the total attack rate is roughly proportional to the import rate, so their outcome is set mainly by importation, which is a placeholder.
- For the poor ward, imports seed local transmission: local cases rise from 1.47 to 59.7 per 1,000 as imports rise from 0 to 10.

### 4.3.8 Overall analysis

Four findings hold across both variants, all 9 sensitivity combinations and all 4 importation rates:

1. Worse drainage (higher Ω) gives more mosquitoes and more infections in every run.
2. With imports switched off, only the worst illustrative ward (Ω = 8.911) sustains local transmission. The persistence threshold is about Ω = 8.7.
3. The two “safe” thresholds differ by about 100–200 times, so the choice of threshold changes the message completely.
4. In the extended variant, imported infections dominate the better wards.

**Why the absolute numbers are small.** The model sits in a low-transmission regime because of its placeholder values. With β_hv = 0.022 at 28 °C, a = 0.350 and μ_v = 0.1142 per day, so one infectious mosquito infects about a·β_hv/μ_v ≈ 0.067 people in its lifetime. Only comparisons between wards are meaningful.

## 4.4 Feedback received and iterations made

### 4.4.1 Feedback received

[[PH: professor / mentor feedback from the supervisor meeting — date, attendees and feedback to be added. Do not fill in until the minutes are available.]]

[[PH: peer feedback, if any]]

The model report prepared for the supervisor meeting listed the decisions requested from the professor:

- a calibration target and its source
- whether rainfall memory and importation are acceptable additions to the specification
- which threshold to treat as “safe”
- literature values for β_hv and γ_h
- whether to model treatment
- which heatmap metric to use
- whether it is acceptable that D_d and M_i act only through Ω
- a review of deviations #1–#9
- whether to adapt the model to *P. vivax* and *An. stephensi*

[[PH: record the professor’s answers to these questions]]

### 4.4.2 Iterations

The model went through four documented iterations, all on 14 October 2026 according to the progress log. The numbers in this subsection come from **earlier runs** recorded in the progress log (docs/PROGRESS.md). They are not the final results of Section 4.3. The match between iterations and the git versions v1–v1.3 is [[PH: confirm; inferred from the files changed in each commit]].

**Iteration 1: first complete build (earlier run).**

- The spec equations, synthetic climate, three wards and the 81-cell sweep were implemented, with 20 tests passing.
- The first heatmap was degenerate: peak I_h was 10.0 on day 0 for all three wards and all 81 cells. The peak was simply the arbitrary seed of 10 infectious people at the start of the simulation, so the heatmap showed the initial conditions, not the effect of drainage.
- Mosquito numbers did differ by ward (peak adult mosquitoes 7,831 / 13,549 / 43,836 for low / medium / high Ω). [[PH: insert the original first heatmap image if a copy exists; it was overwritten by later runs]]

**Diagnosis (read-only investigation).**

- The main cause was weak transmission: the annual-mean R0 was below 1 in every ward, and the weakest link was K_hv = 0.068 humans infected per infectious mosquito.
- Starting the simulation in the dry season played a minor part.
- Seeding infectious mosquitoes made no difference, so that option was rejected.

**Iteration 2: spin-up and new metrics (earlier run).**

- A fixed 3-year spin-up was added (deviation #5), reporting year 3.
- The attack rate and R0(t) metrics and the first sensitivity analysis were added.
- The unsourced recovery rate γ_h = 0.01 was replaced with the literature-anchored 0.0035 per day. The aim was to source the value, not to obtain a result.
- Results for low / medium / high Ω:
  - peak I_h: 1.30 / 1.86 / 12.4
  - attack rate per 1,000: 0.0198 / 0.0491 / 1.21
  - days with R0 > 1: 15 / 65 / 113
- Both metrics now rose with Ω. However, in the low and medium wards the peak was still on day 0, because infection was still declining from the year before. Tests: 26 passing.

**Iteration 3: two variants and spin-up until convergence.**

- 3 years did not reach a steady pattern, so spin-up until local infections change by less than 1% per year was added (deviation #9).
- The extended variant was added: rainfall memory (#6) and importation (#8), with the Ω-dependent retention time (#7) switched off.
- The Ω threshold analysis and calibration code were also added.
- Tests: 42 passing, including the regression test that reproduces iteration 2.
- This iteration produced the results in Section 4.3.

**Iteration 4: documentation.** The model report for the supervisor meeting was written from a fresh full run, with every number cross-checked against the output.

[[PH: name the student(s) responsible for each iteration]]

## 4.5 Advantages, limitations and applications

**Advantages.**

- **Traceable to the approved specification.** The spec variant implements the equations exactly, and every departure is logged, marked in the code and covered by tests.
- **Transparent about uncertainty.** Every parameter has a source or a PLACEHOLDER label in one file.
- **Verified.** 42 automated tests cover hand-calculated formulas, conservation, regression and the thresholds.
- **Fast and reproducible.** A full run takes about two minutes, with a fixed seed and pinned packages.
- **Ready for the next step.** Calibration of K_0 and the threshold tools are already built.

**Limitations** (from the model report).

1. **Synthetic climate:** T(t) and R(t) are invented shapes, not observations.
2. **Placeholder parameters:** most drainage, larval and human rates are unsourced, and the sourced ones still need checking against the papers. β_hv = 0.022 is at the low end of literature values.
3. **Uncalibrated K_0:** absolute mosquito numbers, EIR and case numbers are arbitrary in scale.
4. **Importation dominates the better wards** in the extended variant, and its rate is a placeholder.
5. **The poor ward is near the threshold and has not converged:** it is still growing after the 20-year spin-up cap (growth 1.02 and 1.03 per year).
6. **The two “safe” thresholds differ by about 100–200 times.**
7. **The model is deterministic:** populations shrink towards zero but never reach it, so values such as 3.76×10⁻⁸ infectious people mean “effectively extinct”.
8. **The species parameters do not fit an Indian city:** they are generic *P. falciparum* / *Anopheles* values. Indian urban malaria often involves *P. vivax*, which can relapse, and *An. stephensi*, which also breeds in containers and tanks.
9. **The ward profiles are illustrative,** chosen by the team.
10. **Ω is the only drainage pathway,** so infrastructure and maintenance cannot be separated.

**Applications and possible impact.** Once real climate data, sourced parameters and a calibration target are in place, the tool could:

- rank wards of a target city by drainage-related malaria risk
- estimate how much drain maintenance is needed at a given drainage density
- test climate scenarios

It can also serve as a documented, tested starting point for later teams. No policy use is proposed at this stage.

[[SUMMARY]]
In summary, this chapter described a modular Python implementation of the approved model, verified by 42 passing tests and a strict deviation-logging process. With synthetic climate, placeholder parameters and uncalibrated K_0, worse drainage gave more malaria in every run. Only the worst illustrative ward sustained local transmission (persistence threshold Ω ≈ 8.7), and the peak-R0 threshold was about 100–200 times smaller. The chapter traced how the first degenerate heatmap led to spin-up, new metrics and the extended variant, and it listed the limitations that keep these results at the level of model behaviour.
