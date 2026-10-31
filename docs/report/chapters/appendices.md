# Appendix I: Summary of the IER and Evidence Register

[[PH: Insert the summary of the IER / Design Experience Portfolio and the Evidence Register. Evidence IDs are not recorded in the project files.]] [[REF:ier]] gives the layout.

[[TAB:ier|Evidence Register summary]]

| Evidence ID | Description | Location | Student(s) |
|---|---|---|---|
| [[PH: ]] | [[PH: e.g. Lit Matrix workbook]] | [[PH: e.g. docs/report/inputs/]] | [[PH: ]] |
| [[PH: ]] | [[PH: e.g. Data Identification Table]] | [[PH: ]] | [[PH: ]] |
| [[PH: ]] | [[PH: e.g. approved specification (docs/SPEC.md)]] | [[PH: ]] | [[PH: ]] |
| [[PH: ]] | [[PH: e.g. model code and tests (git versions v1–v1.3)]] | [[PH: ]] | [[PH: ]] |
| [[PH: ]] | [[PH: e.g. model report for the supervisor meeting]] | [[PH: ]] | [[PH: ]] |

# Appendix II: Model Specifications

## II.1 Parameter table

All rates are per day. “Lit.” means a value with a named source that has **not yet been verified** against the paper. PLACEHOLDER means that no literature value has yet been sourced. [[REF:params]] lists every parameter. Source: params.py and the model report.

[[TAB:params|Model parameters, values and sources]]

| Symbol | Meaning | Value | Units | Source / status |
|---|---|---|---|---|
| ε | Smoothing constant | 0.001 | – | Specification §1 |
| K_0 | Carrying-capacity scale | 500 | mosquitoes per (mm/day) | PLACEHOLDER, uncalibrated |
| η | Sensitivity of K_v to Ω | 0.5 | – | PLACEHOLDER |
| μ_base | Baseline larval mortality | 0.1 | 1/day | PLACEHOLDER |
| μ_flush | Flushing coefficient | 0.005 | (1/day)/(mm/day) | PLACEHOLDER |
| R_flush | Rain threshold for flushing | 15 | mm/day | PLACEHOLDER |
| c_a, T_0, T_m | Brière biting-rate constants | 2.03×10⁻⁴, 11.7, 42.3 | –, °C, °C | Lit.: Mordecai et al. [[CITE:mordecai2013]] [[PH: verify]] |
| T_min, DD | Degree-day parasite development | 16, 111 | °C, °C·day | Lit.: classic Detinova/Macdonald *P. falciparum* model [[PH: verify source]] |
| q_0, q_1, q_2 | Mosquito mortality quadratic | −4.4, 1.31, −0.03 | day, day/°C, day/°C² | Lit.: Martens [[CITE:martens1997]] [[PH: verify]] |
| φ_v | Egg-laying (oviposition) rate | 10 | female eggs/adult/day | PLACEHOLDER |
| θ_A | Aquatic → adult maturation | 0.1 | 1/day | PLACEHOLDER |
| β_vh | Human → mosquito transmission probability per bite | 0.48 | – | Attributed in params.py to Chitnis et al. [[CITE:chitnis2008]] [[PH: verify]] |
| β_hv | Mosquito → human transmission probability per bite | 0.022 | – | Value recorded in [[CITE:shah2013,osman2017]]; attributed in params.py to Chitnis et al. [[CITE:chitnis2008]] [[PH: verify]]; low end of quoted range, open question |
| Λ_h | Human births/immigration | 0.4566 | humans/day | Derived: μ_h × 10,000 |
| μ_h | Human natural death rate | 4.566×10⁻⁵ (= 1/(60·365)) | 1/day | PLACEHOLDER (60-year life expectancy) |
| α_h | Human incubation rate E_h → I_h | 0.0833 (= 1/12) | 1/day | PLACEHOLDER |
| γ_h | Human recovery rate | 0.0035 | 1/day | Value recorded in [[CITE:shah2013,osman2017]]; attributed in params.py to Chitnis et al. [[CITE:chitnis2008]] [[PH: verify]]; changed from an unsourced 0.01 |
| δ_h | Malaria death rate | 1×10⁻⁴ | 1/day | PLACEHOLDER |
| ρ | Loss of immunity R_h → S_h | 0.00274 (= 1/365) | 1/day | PLACEHOLDER |

**Numerical settings.**

- K_V_MIN = 1 mosquito and Q_DEN_MIN = 1 day (guards #1 and #4).
- odeint maximum step 1 day; relative and absolute tolerance 10⁻⁶.
- Spin-up tolerance 1% per year, maximum 20 years.

**Extended variant only (all PLACEHOLDER).**

- Rainfall retention time τ = 10 days, with a numerical floor R_EFF_MIN = 0.01 mm/day.
- Imported infections: 1 per 1,000 people per year.
- Ω-dependent retention time: switched off (slope 0.1 if switched on).

## II.2 Equations

The approved equations are given in Section 3.3 as Equations [[EQREF:omega]] to [[EQREF:dRh]], copied from docs/SPEC.md. The deviations add the following formulas (docs/DEVIATIONS.md). They are not part of the approved specification:

- **#1:** K_v = max(K_0 (1 + η Ω) R(t), K_V_MIN).
- **#2:** a(T) = 0 outside T_0 < T < T_m.
- **#3:** γ_m(T) = max(0, (T − T_min)/DD).
- **#4:** μ_v(T) = 1 / max(q_0 + q_1 T + q_2 T², Q_DEN_MIN).
- **#6 (extended):** K_v = K_0 (1 + η Ω) max(R_eff(t), R_EFF_MIN), where
  - R_eff[d] = (1 − w) R_eff[d−1] + w R[d]
  - w = 1 − exp(−1/τ)
- **#7 (extended, off):** τ(Ω) = τ (1 + slope × Ω).
- **#8 (extended):** a transfer ι S_h from S_h to E_h, with ι = imports per 1,000 per year / 1000 / 365 per day.

## II.3 Module and function map

[[REF:funcmap]] shows where each deviation is implemented in the code.

[[TAB:funcmap|Location of the deviations in the code]]

| Deviation | File | Function |
|---|---|---|
| #1 | drainage.py | carrying_capacity() |
| #2 | climate.py | biting_rate() |
| #3 | climate.py | incubation_rate() |
| #4 | climate.py | vector_mortality() |
| #5 | ode.py | simulate_with_spinup() |
| #6 | ode.py; climate.py | build_forcing(); effective_rainfall() |
| #7 | config.py | ModelConfig.tau() |
| #8 | ode.py | human_rhs() |
| #9 | ode.py | simulate_converged() |

The module map is given in [[REF:modules]] and the system workflow in [[REF:workflow]].

# Appendix III: Source Code and Result Tables

## III.1 Key source code

The listings below are copied unchanged from the repository at the time of the build. The full code is in `src/malaria_model/`.

### III.1.1 params.py

[[CODE:src/malaria_model/params.py]]

### III.1.2 climate.py

[[CODE:src/malaria_model/climate.py]]

### III.1.3 drainage.py

[[CODE:src/malaria_model/drainage.py]]

### III.1.4 ode.py

[[CODE:src/malaria_model/ode.py]]

## III.2 Result tables

[[REF:climstats]] summarises the synthetic climate, and [[REF:wardderived]] gives the derived drainage quantities for the three wards.

[[TAB:climstats|Statistics of the synthetic climate (not real weather data)]]

| Quantity | Value |
|---|---|
| Temperature | T(t) = 28 + 4·cos(2π(t − 135)/365); range 24.00–32.00 °C; mean 28.00 °C |
| Hottest / coolest day | Day 135 (mid-May) / day 317 |
| Annual rainfall | 1,357 mm, of which 1,246 mm (92%) falls in June–September (days 151–272) |
| Daily rainfall range | 0.064 to 48.07 mm/day (maximum on day 226) |
| Days above the flushing threshold (15 mm/day) | 27 |
| Rainfall with memory (extended, τ = 10 days) | Mean 3.72 mm/day; range 0.174–19.57 mm/day |

[[TAB:wardderived|Derived drainage quantities for the three illustrative wards]]

| Ward profile | Ω | Habitat multiplier 1 + ηΩ | Flushing divisor Ω + ε |
|---|---|---|---|
| High infrastructure / high maintenance | 0.1248 | 1.062 | 0.1258 |
| Medium infrastructure / low maintenance | 1.3972 | 1.699 | 1.3982 |
| Poor infrastructure / neglected | 8.9109 | 5.455 | 8.9119 |

The ward summaries, thresholds, minimum-maintenance table and importation sensitivity table are given in Section 4.3.

# Appendix IV: Meeting Minutes, Peer Feedback and Mentor Feedback

[[PH: Insert minutes of team meetings and supervisor meetings (date, attendees, points discussed, decisions, actions). No minutes are recorded in the project files.]]

[[PH: Insert peer feedback forms.]]

[[PH: Insert mentor feedback, including the outcome of the supervisor meeting for which the model report was prepared.]]

# Appendix V: VIP Evidence

## V.1 Literature Matrix summary

The Lit Matrix has 8 logged papers, against a target of 15–25 after triage. All eight are marked “Read”. [[REF:litsummary]] lists them. The relevance scores are the team's own ratings (1–5).

[[TAB:litsummary|Literature Matrix: status and relevance of the logged papers]]

| ID | Reference | Study region | Relevance (1–5) | Status |
|---|---|---|---|---|
| 1 | Waite et al. 2019 [[CITE:waite2019]] | Laboratory | 4 | Read |
| 2 | Turner et al. 2015 [[CITE:turner2015]] | Generic / hypothetical | 5 | Read |
| 3 | Osman, Adu and Yang 2017 [[CITE:osman2017]] | Generic parameters | 4 | Read |
| 4 | Paaijmans et al. 2012 [[CITE:paaijmans2012]] | Laboratory | 5 | Read |
| 5 | Madito, Brooke and Silal 2026 [[CITE:madito2026]] | Semi-arid, tropical and sub-tropical Africa | 5 | Read |
| 6 | Santos-Vega et al. 2016 [[CITE:santosvega2016]] | Ahmedabad, Gujarat, India | 5 | Read |
| 7 | Shah and Gupta 2013 [[CITE:shah2013]] | India (parameters interpreted in an Indian context) | 5 | Read |
| 8 | Padder et al. 2025 [[CITE:padder2025]] | Generic vector-borne disease | 4 | Read |

## V.2 Data Provenance Log

[[PH: Data Provenance Log: not yet created / attach if created]]

## V.3 Data Identification Table

The full Data Identification Table is summarised in [[REF:dataid]]. The table's own summary sheet makes six recommendations:

1. Only 2 of the 8 papers reference a real, named, acquirable dataset (papers 5 and 6).
2. The World Bank CCKP is public and directly usable, and is the likely primary climate-data source for any Indian target city.
3. The Ahmedabad case data used in paper 6 is not openly downloadable. An equivalent request must be made to the target city's municipal health or vector-borne-disease-control department.
4. Census of India data is public and can supply the demographic layer.
5. The Data Provenance Log should record CCKP as an “Obtained / In use” candidate, and the municipal surveillance data as “To verify” or “Requested”.
6. The laboratory papers (1 and 4) should be kept as a literature parameter bank, separate from the data pipeline.

## V.4 Draft paper status

[[PH: status of any draft research paper (none / in preparation / submitted), target venue]]

# Appendix VI: Publications, Certificates and IP

[[PH: list papers presented or published, competition certificates and patent / IP filings, or state “None this semester”]]

# Appendix VII: AI-Tool Use Disclosure Log

[[PH: CONFIRM THIS LOG — draft compiled from the git history, PROGRESS.md and the project files; every row must be checked by the team]]

[[REF:ailog]] lists each use of an AI tool, its purpose and how the output was verified.

[[TAB:ailog|AI-tool use log]]

| # | Date / period | Tool | Purpose | How the output was verified |
|---|---|---|---|---|
| 1 | [[PH: dates]] | [[PH: tool, if any]] | [[PH: Was an AI tool used to compile the Lit Matrix and/or the Data Identification Table? To be completed by the team.]] | [[PH: ]] |
| 2 | 13–14 Oct 2026 (git history) [[PH: confirm]] | Claude (Claude Code) [[PH: confirm]] | Drafting and debugging the model code and tests from the approved specification | 42 automated tests with hand-calculated values; regression test; no equation changed without approval; deviations logged in DEVIATIONS.md and marked in the code [[PH: confirm]] |
| 3 | 14 Oct 2026 (progress log) [[PH: confirm]] | Claude (Claude Code) [[PH: confirm]] | Diagnosing the degenerate first run and proposing fixes (spin-up, new metrics) | Read-only diagnosis; fixes implemented only after approval and logged as deviations #5–#9 [[PH: confirm]] |
| 4 | 14–16 Oct 2026 [[PH: confirm]] | Claude (Claude Code) [[PH: confirm]] | Drafting documentation: progress log, deviation log, model report; reviewing figures | Every number cross-checked against the model output and params.py (model report §13) [[PH: confirm]] |
| 5 | From 1 Nov 2026 | Claude (Claude Code) | Drafting this project report from the team's records (chapters, figures, Word build) | Review and editing by the team; placeholders for every unrecorded fact; mentor review [[PH: confirm]] |
| 6 | [[PH: ]] | [[PH: ]] | [[PH: any other AI use (grammar, brainstorming, visualisation, literature search)]] | [[PH: ]] |
