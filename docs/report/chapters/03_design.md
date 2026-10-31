# Chapter 3: Design and Development Process

[[INTRO]]
This chapter explains how the model was designed. It turns the problem from Chapter 2 into requirements and sets out the design alternatives found in the project records, with the decisions taken and their reasons. It then presents the selected design: the system architecture, the Clogging Index, the climate functions, the eight-compartment ODE system, the inputs and the two model variants. It also covers standards, constraints and ethical considerations, and ends with the project plan. All equations are copied from the professor-approved specification (docs/SPEC.md), which is the source of truth for the mathematics.

## 3.1 Stakeholder / user needs and specifications

No stakeholder has yet been consulted directly ([[PH: record any stakeholder input]]). The requirements in [[REF:reqs]] come from three sources:

- the problem statement (Section 1.3)
- the approved specification
- the project's working rules, which were set at the start of implementation

[[TAB:reqs|Requirements for the model and software]]

| ID | Requirement | Type | Source |
|---|---|---|---|
| R1 | Represent humans (S_h, E_h, I_h, R_h) and mosquitoes (A_v, S_v, E_v, I_v) in 8 compartments | Functional | Specification §4 |
| R2 | Biting rate, parasite incubation and mosquito mortality depend on temperature T (°C) | Functional | Specification §3 |
| R3 | Larval carrying capacity and flushing depend on rainfall R (mm/day) and on the Clogging Index Ω | Functional | Specification §1–2 |
| R4 | Compare wards with different drainage density D_d and maintenance M_i, and sweep a grid of drainage scenarios | Functional | Research question |
| R5 | Report peak infectious humans (max over t of I_h) as the heatmap metric unless the professor specifies otherwise | Functional | Specification §6 note 8 |
| R6 | Solve with scipy.integrate.odeint; time in days, rates per day | Implementation | Project rules |
| R7 | Every parameter value in one file, each with its literature source or the label “PLACEHOLDER – needs literature value” | Traceability | Specification §6 note 5; project rules |
| R8 | No change to any approved equation without approval; every approved departure marked in code and logged | Traceability | Project rules |
| R9 | Automated tests run after every change | Verification | Project rules |
| R10 | Modular code with type hints and documented units; no hard-coded numbers inside equations | Maintainability | Project rules |
| R11 | Reproducible results (fixed random seed, pinned package versions) | Reproducibility | Model report §7 |

## 3.2 Design alternatives considered and the decision

### 3.2.1 Model structure

The literature review (Chapter 2) offered four types of model structure. [[REF:dmatrix]] compares them against criteria that follow from the requirements. **The scores and weights are not recorded in the project files and must be filled in by the team.**

[[TAB:dmatrix|Decision matrix for the model structure (scores 1–5; weights and scores to be confirmed by the team)]]

| Criterion (weight) | A. Simple SEIR–SEI [[CITE:osman2017,shah2013]] | B. SEIR–SEI + egg/larva/pupa stages [[CITE:turner2015]] | C. SEIR–SEI + one aquatic stage (selected) | D. Statistical / phenomenological [[CITE:santosvega2016]] |
|---|---|---|---|---|
| Has an entry point for breeding habitat and drainage (R3) ([[PH: w]]) | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Mechanistic climate coupling (R2) ([[PH: w]]) | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Parameters obtainable without local field data ([[PH: w]]) | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Analytical tools available (R0, sensitivity) ([[PH: w]]) | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Implementation and testing effort ([[PH: w]]) | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| **Weighted total** | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |

**Reasons recorded for the choice.**

- Option A has no place for breeding water, so drainage cannot enter.
- Option D needs ward-level case data, which is not yet available, and it does not describe mechanisms.
- Option B represents the aquatic stages in more detail than the available parameters support.
- Option C keeps the well-studied SEIR–SEI core of A and adds one aquatic compartment A_v. That compartment is the point where rainfall and Ω enter. This is the structure in the professor-approved specification. [[PH: confirm the reasons and who made the decision, and when]]

### 3.2.2 Other design decisions

[[REF:decisions]] lists the other alternatives that appear in the project records, the option taken and the reason recorded at the time. Sources are the specification, the deviation log (DEVIATIONS.md) and the decision log (PROGRESS.md).

[[TAB:decisions|Further design decisions recorded during development]]

| Decision | Alternatives in the records | Chosen | Reason recorded |
|---|---|---|---|
| Programming environment | MATLAB or Python | Python with scipy.integrate.odeint | Required by the project rules [[PH: add the team’s reason for choosing Python over MATLAB]] |
| Climate input | Real CCKP data or synthetic series | Synthetic for now | Lets the model be built and tested before the target city and real data are chosen |
| Climate formulation | Several approaches exist [[CITE:madito2026]] | Thermal-response functions for T and a rainfall-proportional carrying capacity, as in the specification | Specification §2–3 |
| Model variant | Specification only, or specification plus realism changes | Both kept: “spec” and “extended” | Extended adds rainfall memory (breeding water persists after rain) and imported infections (urban wards receive travel-related cases). Which to use in the thesis is an open question for the professor. |
| Start-up of simulations | Report year 1; fixed 3-year spin-up; spin-up until convergence | Spin-up until local infections change by < 1% per year (maximum 20 years) | In the first run the peak equalled the arbitrary day-0 seed; 3 years did not reach a steady pattern |
| Heatmap metric | Peak I_h (specification) or attack rate per 1,000 | Peak I_h primary, attack rate supplementary | Specification §6 note 8; open question for the professor |
| “Safe” threshold | Peak R0(t) < 1 or local growth < 1 (persistence) | Both reported | They differ by about 100–200×; open question |
| Initial infectious mosquitoes | Seed infectious mosquitoes or not | Not seeded (option rejected) | Made no difference in a diagnostic run |
| Recovery rate γ_h | Original 0.01/day (unsourced) or 0.0035/day | 0.0035/day | Replaced the unsourced value with a literature-anchored one. Not tuned to obtain a result. |
| Calibration | Calibrate several parameters or only K_0 | K_0 only, to total annual parasite incidence | Built and tested but **not run**: no calibration target yet |
| Water retention grows with Ω | Include or not | Implemented, switched OFF | Plausible mechanism, not part of the specification; current results do not use it |

## 3.3 Selected design

### 3.3.1 Architecture and workflow

[[REF:workflow]] shows the software architecture. The architecture follows the chain from inputs to model to outputs:

1. Parameters and climate inputs are read.
2. The Clogging Index Ω is computed for each ward.
3. The ODE system is solved over repeated years until the spin-up converges.
4. Metrics are computed on the final year.
5. The same chain is run for three illustrative wards, an 81-cell drainage grid, a threshold analysis and sensitivity runs.
6. Figures are produced.

The Python modules that implement each step are listed in Chapter 4.

[[FIG:workflow|system_workflow.png|System workflow of the simulation tool, from inputs to figures]]

[[REF:compartments]] shows the conceptual model. The human compartments follow S_h → E_h → I_h → R_h, with births, waning immunity, natural death and death from malaria. The mosquito compartments follow A_v → S_v → E_v → I_v, with egg-laying limited by the carrying capacity. The two populations are coupled through biting. Temperature and rainfall enter at the points marked.

[[FIG:compartments|model_diagram.png|Eight-compartment SEIR–vector model with climate and drainage entry points]]

### 3.3.2 Urban drainage and the Clogging Index Ω

A ward is described by two numbers between 0 and 1:

- **D_d, drainage density:** how much drainage infrastructure exists.
- **M_i, maintenance efficiency:** how clear the drains are kept, where 0 is fully blocked and 1 is perfectly clear.

The specification combines them into the Clogging Index Ω (also written D_m), where ε = 0.001 is a smoothing constant that prevents division by zero:

[[EQ:omega|Ω = D_m = (1 - M_i) / (D_d + epsilon)]]

Ω is large when drains are both blocked and sparse, and falls when either improves. Ω enters the mosquito model in two ways that reinforce each other. First, it raises the aquatic carrying capacity, which is proportional to daily rainfall R(t) in mm/day:

[[EQ:kv|K_v(R, Ω) = K_0 * (1 + eta * Ω) * R(t)]]

Second, it weakens the flushing of larvae by heavy rain:

[[EQ:mua|μ_A(R(t)) = μ_base + μ_flush * max(0, (R(t) - R_flush) / (Ω + epsilon))]]

So a clogged ward has more breeding habitat for the same rain and loses fewer larvae on heavy-rain days. [[REF:wards]] gives the three illustrative ward profiles used in the experiments. The profiles were chosen by the team and do not describe real wards.

[[TAB:wards|Illustrative ward profiles and their Clogging Index]]

| Ward profile | D_d | M_i | Ω | Habitat multiplier 1 + ηΩ (η = 0.5) |
|---|---|---|---|---|
| High infrastructure / high maintenance | 0.8 | 0.9 | 0.1248 | 1.062 |
| Medium infrastructure / low maintenance | 0.5 | 0.3 | 1.3972 | 1.699 |
| Poor infrastructure / neglected | 0.1 | 0.1 | 8.9109 | 5.455 |

The 9 × 9 grid of D_d and M_i values from 0.1 to 0.9 covers Ω from 0.1110 to 8.9109.

### 3.3.3 Climate-dependent thermal response functions

Temperature T (°C) sets three mosquito and parasite rates. The biting rate follows a Brière function:

[[EQ:biting|a(T) = c_a * T * (T - T_0) * sqrt(T_m - T)]]

The parasite incubation rate in the mosquito follows a degree-day model:

[[EQ:gammam|γ_m(T) = (T - T_min) / DD]]

Adult mosquito mortality follows a quadratic curve:

[[EQ:muv|μ_v(T) = 1 / (q_0 + q_1*T + q_2*T^2)]]

The parameter values come from the sources named in the parameter file, all marked for verification:

- **Brière constants** c_a, T_0, T_m: Mordecai et al. [[CITE:mordecai2013]] [[PH: verify]].
- **Degree-day constants** T_min = 16 °C and DD = 111 °C·day: the classic Detinova/Macdonald *P. falciparum* model [[PH: verify source; no reference number assigned until the source is confirmed]].
- **Mortality coefficients** q_0, q_1, q_2: Martens [[CITE:martens1997]] [[PH: verify]].

Waite et al. found that the degree-day model underestimates development at cool temperatures [[CITE:waite2019]]. This matters less for the 24–32 °C synthetic climate used here, but should be revisited for real data.

### 3.3.4 State variables and the ODE system

The human population is N_h, and the adult mosquito population is N_v. The aquatic stage A_v is not part of N_v.

[[EQ:nh|N_h = S_h + E_h + I_h + R_h]]

[[EQ:nv|N_v = S_v + E_v + I_v]]

The vector equations are:

[[EQ:dAv|dA_v/dt = φ_v * (1 - A_v / K_v(R, Ω)) * (S_v + E_v + I_v) - (θ_A + μ_A(R)) * A_v]]

[[EQ:dSv|dS_v/dt = θ_A * A_v - a(T) * β_vh * (I_h / N_h) * S_v - μ_v(T) * S_v]]

[[EQ:dEv|dE_v/dt = a(T) * β_vh * (I_h / N_h) * S_v - (γ_m(T) + μ_v(T)) * E_v]]

[[EQ:dIv|dI_v/dt = γ_m(T) * E_v - μ_v(T) * I_v]]

The human equations are:

[[EQ:dSh|dS_h/dt = Λ_h - a(T) * β_hv * (I_v / N_h) * S_h - μ_h * S_h + ρ * R_h]]

[[EQ:dEh|dE_h/dt = a(T) * β_hv * (I_v / N_h) * S_h - (α_h + μ_h) * E_h]]

[[EQ:dIh|dI_h/dt = α_h * E_h - (γ_h + μ_h + δ_h) * I_h]]

[[EQ:dRh|dR_h/dt = γ_h * I_h - (ρ + μ_h) * R_h]]

**How to read the coupling terms.** The infection of mosquitoes in [[EQREF:dSv]]–[[EQREF:dEv]] depends on three factors:

- the biting rate a(T)
- the probability β_vh that a bite on an infectious human infects the mosquito
- the fraction of humans who are infectious, I_h/N_h

The infection of humans in [[EQREF:dSh]]–[[EQREF:dEh]] depends on the same biting rate, the probability β_hv that an infectious bite infects a human, and the number of infectious mosquitoes per human, I_v/N_h. These two terms are the forces of infection. Through a(T) they are where temperature enters the host–vector coupling.

**Parameters.** Appendix II gives the full parameter table with values, units and sources. In summary:

- **Sourced, to verify against the papers:**
  - the Brière, degree-day and mortality constants above
  - β_vh = 0.48, attributed in the parameter file to Chitnis et al. [[CITE:chitnis2008]] [[PH: verify]]
  - β_hv = 0.022 and γ_h = 0.0035/day. These exact values are recorded in the Lit Matrix for Shah and Gupta [[CITE:shah2013]] (p_h = 0.022, γ_h = 0.0035) and for Osman et al. [[CITE:osman2017]] (mosquito-to-human probability 0.022, recovery 0.0035). The parameter file attributes both to Chitnis et al. [[CITE:chitnis2008]] [[PH: verify the attribution, and the meaning of p_h in Shah and Gupta]]. The value β_hv = 0.022 is at the low end of quoted values and is an open question for the professor.
- **Placeholders awaiting literature values:** K_0 (500, uncalibrated), η, μ_base, μ_flush, R_flush, φ_v, θ_A, μ_h, α_h, δ_h and ρ.
- **Derived:** Λ_h = μ_h × N_h(0), so that the disease-free population stays constant.

### 3.3.5 Inputs, initial conditions and outputs

**Synthetic climate.** Real climate data has not yet been loaded, so the model uses a synthetic year designed to resemble a monsoon city (day 0 = 1 January). It is not data from any real place.

- **Temperature:** a smooth cosine between 24 and 32 °C (mean 28 °C), hottest on day 135.
- **Rainfall:**
  - a dry-season background of 0.2 mm/day plus a bell-shaped monsoon centred on day 212 (mean peak 15 mm/day, width 30 days)
  - multiplied by log-normal day-to-day noise with a fixed seed (42)
  - about 1,357 mm per year, 92% of it from June to September
  - rainfall is above zero on every day

**Initial conditions.** The specification does not give initial conditions. The following were chosen and documented:

- Humans: N_h = 10,000, with 10 infectious people; all other infected classes start at 0.
- Larvae start at the day-0 carrying capacity.
- Adults start at the level that larval maturation supports.
- No mosquito starts infected.

**Outputs.**

- peak I_h and its day (the specification's metric)
- attack rate: new infections per 1,000 people per year
- local and imported infections
- entomological inoculation rate (EIR)
- the time-varying reproduction number R0(t), from the next-generation matrix as R0 = √(K_hv·K_vh)
- two Ω thresholds:
  - Ω\*, where the yearly peak of R0(t) equals 1
  - the persistence threshold, where local infections neither grow nor shrink from year to year

### 3.3.6 Model variants, spin-up and logged deviations

The tool has two variants:

- **“spec”** implements the equations above exactly, plus four numerical guards against impossible values. The guards are never active with the synthetic climate.
- **“extended”** adds rainfall memory and imported infections.

Both variants simulate repeated years of the same climate until the result settles (spin-up) and report only the final year.

Every departure from the specification follows the same process:

1. It is proposed and explained before any code is written.
2. It is implemented only after approval.
3. It is marked in the code with a `# DEVIATION:` comment.
4. It is entered in a permanent deviation log.

All nine deviations were approved by the student team during development. Mentor review is [[PH: pending — confirm whether and when the professor reviewed deviations #1–#9]]. [[REF:deviations]] summarises them.

[[TAB:deviations|Logged deviations from the approved specification]]

| # | Change | Reason | Variant | Active in current results |
|---|---|---|---|---|
| 1 | K_v floored at 1 mosquito | Avoid division by zero in A_v/K_v on rain-free days | Both | No (rain > 0 every day) |
| 2 | a(T) = 0 outside T_0 < T < T_m | Formula gives an undefined or negative value outside the range | Both | No (24–32 °C) |
| 3 | γ_m(T) floored at 0 below T_min | Negative development is not physical | Both | No |
| 4 | Denominator of μ_v(T) floored at 1 day | Denominator ≤ 0 below about 3.7 °C and above about 40 °C | Both | No |
| 5 | Fixed 3-year spin-up, report year 3 | Remove dependence on the arbitrary day-0 seed | Both | Kept for the regression test and threshold calculations |
| 6 | K_v driven by rainfall with memory (retention time τ = 10 days) | Breeding water persists after rain | Extended | Yes |
| 7 | Retention time grows with Ω | Clogged drains may hold water longer | Extended | No (switched off) |
| 8 | Imported infections, 1 per 1,000 people per year (S_h → E_h) | Urban wards receive travel-related infections | Extended | Yes |
| 9 | Spin-up until local infections change by < 1% per year (maximum 20 years) | 3 years did not reach a steady pattern | Both | Yes |

## 3.4 Standards, constraints, safety, ethical, societal and environmental considerations

**Standards.**

- References follow the IEEE numbered style required by the report format.
- No formal engineering or software standard has been adopted for the model [[PH: list any standard followed, or confirm “none”]].
- The software follows documented good practice:
  - version control with git
  - pinned package versions
  - automated tests
  - a fixed random seed
  - units documented in every function
  - a single parameter file with a source for every value

**Constraints.**

- **Data:** the target city is not yet confirmed (Ahmedabad is the strongest candidate), and malaria case data has not been obtained.
- **Parameters:** most parameter values are still placeholders.
- **Calibration:** none is possible until a calibration target is chosen.
- **Model structure:**
  - The model is deterministic, so infections can shrink towards zero but never reach it.
  - Its parameters are generic *P. falciparum* / *Anopheles* values. Urban India often involves *P. vivax* and *An. stephensi*, which are not represented.
- **Computing:** a full run takes about two minutes on the development machine.

**Ethical considerations.**

- **Confidentiality of health data.** Ward-level surveillance data is held by municipal health departments and is released only on request [[CITE:santosvega2016]]. Any data obtained must be used only for the agreed purpose, stored securely, and reported only at the agreed level of aggregation. It must not be published without the data owner's permission. [[PH: confirm whether institutional ethics approval or a data-use agreement is required before the data request]]
- **Honest reporting.** The synthetic climate, placeholder parameters and uncalibrated K_0 are stated wherever results appear. Model behaviour is not presented as evidence about a real city.
- **Integrity of the specification.** The approved equations are not changed silently. Every departure is logged and traceable.
- **AI use** is disclosed in Section 5.5 and Appendix VII.
- **Intellectual property.** Under the IPR Policy of SVKM's NMIMS, approval is needed before any public disclosure of potentially patentable work.

**Societal and environmental considerations.** If confirmed with real data, results of this kind could support decisions on drain construction and maintenance as part of vector control. Because current results depend on placeholder parameters, no policy recommendation is made (Section 4.5).

## 3.5 Project plan

**Work breakdown.**

1. Scoping and framing
2. Literature review and Lit Matrix
3. Data identification (a Data Provenance Log is planned)
4. Conceptual model
5. Mathematical specification and professor approval
6. Implementation and testing
7. Simulation experiments and analysis
8. Model report for the supervisor meeting
9. Project report and portfolio

[[REF:milestones]] gives the milestones. Dates are filled in only where the git history records them. All other dates are placeholders.

[[TAB:milestones|Project milestones]]

| # | Milestone | Planned date | Completed | Evidence |
|---|---|---|---|---|
| M1 | Project scoping and research workflow | [[PH: date]] | [[PH: date]] | Executive summary |
| M2 | Lit Matrix (8 papers) set up; Data Provenance Log [[PH: not yet created]] | [[PH: date]] | [[PH: date]] | Lit Matrix workbook |
| M3 | Data Identification Table | [[PH: date]] | [[PH: date]] | Data Identification workbook |
| M4 | Conceptual model diagram finalised | [[PH: date]] | [[PH: date]] | Executive summary |
| M5 | Project skeleton and specification committed | [[PH: date]] | 13 Oct 2026 | git history |
| M6 | First complete model build and subsequent versions v1–v1.3 | [[PH: date]] | 14 Oct 2026 | git history; progress log |
| M7 | Model report for the supervisor meeting | [[PH: date]] | 14 Oct 2026 (progress log) [[PH: confirm; file last updated 16 Oct 2026]] | docs/MODEL_REPORT.md |
| M8 | Supervisor meeting and feedback | [[PH: date]] | [[PH: date]] | [[PH: minutes]] |
| M9 | Project report draft | [[PH: date]] | [[PH: in progress]] | This report |
| M10 | Portfolio Review (Week 13) | [[PH: date]] | — | — |
| M11 | Final Evaluation / TEE (Week 15) | [[PH: date]] | — | — |

**Gantt chart.** [[PH: insert Gantt chart once the planned dates for M1–M11 are confirmed]]

**Task allocation.** [[PH: task allocation per student — not recorded in the project files; see also Section 5.1]]

[[SUMMARY]]
In summary, this chapter set eleven requirements and compared four model structures in a decision matrix whose scores are to be confirmed. It recorded the further design decisions with their reasons. It presented the selected design: an eight-compartment SEIR–vector ODE model with temperature-dependent rates and a Clogging Index Ω that raises breeding habitat and weakens larval flushing, run in a “spec” and an “extended” variant with spin-up and nine logged deviations. It also covered the constraints and ethical considerations and the project plan.
