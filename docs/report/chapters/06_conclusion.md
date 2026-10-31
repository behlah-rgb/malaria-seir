# Chapter 6: Conclusion and Future Scope

[[INTRO]]
This chapter brings the report together. It summarises the work carried out this semester and the conclusions that can be drawn from the analysis in Chapter 4, within the limits set by synthetic climate, placeholder parameters and an uncalibrated K_0. It then sets out the future scope and hand-over notes so that the project can continue in the next semester.

## 6.1 Work carried out and conclusions

**Work carried out.** This semester the team carried out six pieces of work:

1. Scoped the project.
2. Reviewed and logged eight papers in a structured Literature Matrix.
3. Identified data sources for each paper and for the project.
4. Developed a conceptual model.
5. Implemented the professor-approved eight-compartment SEIR–vector specification in Python, with a Clogging Index Ω linking urban drainage condition to mosquito breeding habitat and larval flushing. The implementation has two variants (spec and extended), a 42-test suite and a logged record of nine approved deviations.
6. Ran simulations for three illustrative wards, an 81-cell drainage grid, two threshold analyses and sensitivity analyses.

**Conclusions.** These follow from Chapter 4 and describe the behaviour of the model under synthetic climate, mostly placeholder parameters and an uncalibrated K_0. They are not findings about any real city.

1. **The specification can be implemented faithfully and verifiably.** The spec variant reproduces the approved equations. Its numerical guards are inactive for the inputs used, and all 42 tests pass, including a regression test.
2. **In the model, worse drainage always means more malaria.** Higher Ω gave more mosquitoes and more infections in every run. This held in both variants, all 9 combinations of γ_h and β_hv, and all 4 importation rates. The direction of the effect is robust, but its size is not: the poor ward's attack rate ranged from 1.65 to 404 per 1,000 across the sensitivity runs.
3. **Only the most neglected illustrative ward sustains local transmission.** With imports off, local infection grows from year to year only above Ω ≈ 8.7 (8.673 spec, 8.761 extended). Only the poor ward (Ω = 8.911) is above this threshold, and it had not reached a steady state within 20 years.
4. **The definition of “safe” drainage matters more than any single number.** The Ω below which R0(t) never exceeds 1 (0.044 spec, 0.083 extended) is about 100–200 times smaller than the persistence threshold. Keeping R0 below 1 all year would need maintenance of 0.93–0.996 at every drainage density, whereas preventing persistence needs maintenance only at the lowest density (M_i ≥ about 0.12 at D_d = 0.1).
5. **In the extended variant, importation dominates the better wards.** At the placeholder rate of 1 per 1,000 per year, about 78% and 65% of their infections are imported, so the importation rate is a key unknown.
6. **D_d and M_i act only through Ω.** This follows from the structure of the specification. As a result, the model cannot separate building drains from maintaining them.

Regarding the gap identified in Chapter 2: the project has produced a working mechanistic model in which drainage condition controls breeding habitat. Within the eight papers reviewed, no such model was found. This statement must be re-checked against a larger literature base [[PH: confirm with literature]].

[[PH: professor / mentor feedback on these conclusions, to be added after the supervisor meeting]]

## 6.2 Future scope and hand-over notes

### 6.2.1 Future work, in order of priority

1. **Lock the target city.** Ahmedabad is the strongest candidate but is not confirmed.
2. **Request malaria case data.** Draft and send a formal request to the relevant municipal or state health department for ward-level case data. Agree the terms of use and confidentiality (Section 3.4).
3. **Calibration target and calibration.** Choose a target for annual parasite incidence per 1,000 people for a reference ward, and its source. Then run `main.py --calibrate TARGET` and check whether K_0 is well identified; the tool reports this.
4. **Real climate data.** Download temperature and rainfall for the target city from the World Bank CCKP and replace the synthetic series. The CCKP data is monthly, so the method for getting daily values must be decided and documented.
5. **Climate scenarios.** Once real data is in place, test how the drainage thresholds shift under warmer or wetter conditions.
6. **Source the placeholder parameters.**
   - Find literature values for β_hv and γ_h and verify their attribution (Section 3.3.4).
   - Verify the Brière, degree-day and mortality constants against the papers.
   - Replace the remaining placeholders: K_0, η, μ_base, μ_flush, R_flush, φ_v, θ_A, μ_h, α_h, δ_h, ρ, the rainfall retention time and the importation rate.
7. **Species for Indian cities.** Consider adapting the model to *P. vivax* (including relapse) and *An. stephensi* (including container breeding).
8. **Treatment.** Decide whether to model treatment. Treated infections recover in weeks rather than months, which would change the results substantially (Section 4.3.7).
9. **Expand the Lit Matrix** from 8 to 15–25 papers. Record the search keywords for each cluster, and create the Data Provenance Log.
10. **Model questions for the professor:**
    - the preferred threshold
    - the preferred heatmap metric
    - whether the extended changes are accepted
    - whether D_d and M_i should act only through Ω
    - a longer spin-up for wards near the threshold
11. **Validation** against local surveillance data once it is obtained.

### 6.2.2 Hand-over notes

- **Where things are.**
  - `docs/SPEC.md`: the approved mathematics, the source of truth
  - `docs/DEVIATIONS.md`: every approved departure, append-only
  - `docs/PROGRESS.md`: status, decisions, open questions and next step
  - `docs/MODEL_REPORT.md`: full results and explanations
  - `src/malaria_model/params.py`: all parameter values with their sources
  - `results/figures/`: the figures
- **Rules to keep.**
  - Do not change any equation without approval.
  - Log every deviation in the code and in DEVIATIONS.md.
  - Label every parameter with its source or as a PLACEHOLDER.
  - Run the tests after every change.
- **Open questions.** These are listed in PROGRESS.md and in Section 4.4.1. [[PH: update with the professor’s answers]]

### 6.2.3 How to run the project

From the project folder, with the virtual environment `.venv` set up from `requirements.txt` (Python 3.14):

- `.venv/bin/python -m pytest` runs the 42 automated tests.
- `.venv/bin/python main.py` runs all experiments and writes the figures to `results/figures/`. This takes about two minutes.
- `.venv/bin/python main.py --calibrate X` calibrates K_0 to a target of X infections per 1,000 per year (not yet run).

[[SUMMARY]]
In summary, the project has turned a professor-approved specification into a tested and documented simulation tool. Under synthetic inputs, the tool shows that worse urban drainage consistently increases modelled malaria, and that the choice of “safe” threshold changes the answer by two orders of magnitude. The next semester should obtain real climate and case data, source the placeholder parameters and calibrate the model, so that these behaviours can be tested against a real city.
