# Chapter 2: Background Study

[[INTRO]]
This chapter reviews the background needed to design the model. It first gives an overview of compartmental malaria modelling and of how climate is put into such models. It then describes the literature search strategy and reviews the eight papers logged in the team's Literature Matrix (Lit Matrix), with a comparison table. It also summarises the data identification work, which asked which papers use real data and where real data for this project could come from. The chapter ends with the research gap that defines the problem. Every paper detail in this chapter is taken from the Lit Matrix and the Data Identification Table. These entries have not yet been re-checked against the original papers ([[PH: verified against paper: yes/no, to be completed per paper in Table 2.1]]).

## 2.1 Overview of the domain and its context

### 2.1.1 Compartmental host–vector models

The standard mathematical description of malaria transmission couples two populations:

- **Humans**, usually divided into susceptible (S_h), exposed (E_h), infectious (I_h) and recovered (R_h) classes, an SEIR structure.
- **Adult mosquitoes**, divided into susceptible (S_v), exposed (E_v) and infectious (I_v) classes, an SEI structure. Infected mosquitoes are usually assumed to stay infectious until they die.

The two populations are linked by biting. A susceptible human can be infected by the bite of an infectious mosquito, and a susceptible mosquito can be infected by biting an infectious human. The basic reproduction number R0 summarises whether an infection introduced into a fully susceptible population will spread (R0 > 1) or die out (R0 < 1) [[CITE:osman2017,shah2013]].

Some models also represent the mosquito's aquatic life stages (eggs, larvae, pupae). This is the natural place where breeding habitat, and therefore rainfall and drainage, enters the model [[CITE:turner2015,padder2025]].

### 2.1.2 Climate forcing

Temperature affects three key quantities:

- the mosquito biting rate
- the parasite's extrinsic incubation period (EIP) inside the mosquito
- mosquito survival

Rainfall affects the aquatic stages, mainly through the carrying capacity of breeding sites, and very heavy rain can flush larvae away. Models put these effects in either as mechanistic thermal-response functions or as statistical relationships fitted to case data. The choice between the two has a large effect on the predicted seasonal pattern [[CITE:madito2026]].

### 2.1.3 Urban context

Urban malaria differs from rural malaria in its breeding sites, population density and socio-economic structure. The single Indian urban study in the Lit Matrix (Ahmedabad) found that population density, climate and poverty together structure ward-level risk [[CITE:santosvega2016]].

## 2.2 Review of relevant sources

### 2.2.1 Search strategy

Search terms were organised into six keyword clusters:

1. model structure
2. vector biology
3. climate coupling
4. urban context
5. parameter estimation
6. regional grounding

[[PH: list the actual search keywords used in each cluster and the databases searched; only the cluster names are recorded]]

Candidate papers were sourced across the clusters. Eight have been read and logged in the Lit Matrix, which records for each paper:

- the model type and the human and vector compartments
- the climate variables, study region and data sources
- the key parameter values and the R0 or key result
- the limitations, a relevance score from 1 to 5, and notes

Eight papers is a small base for a literature review. The target is 15–25 papers after triage, and expanding the matrix is part of the future work (Chapter 6).

### 2.2.2 Review of the logged papers

**Baseline SEIR–SEI models.**

- *Shah and Gupta* [[CITE:shah2013]] present a deterministic SEIR–SEI model for malaria with parameters interpreted in an Indian context, simulated in MATLAB. They derive an R0 threshold: the disease-free equilibrium is stable for R0 < 1 and unstable for R0 > 1. Their sensitivity analysis identifies the mosquito biting rate and mosquito death rate as the most influential parameters. The model has no temperature, rainfall or other environmental forcing.
- *Osman, Adu and Yang* [[CITE:osman2017]] give a similar human SEIR + mosquito SEI model with an analytically derived R0 and the same stability result. It has no climate dependence and no mosquito life stages, and many parameters are assumed.

Together, these two papers give the basic structure and the analysis tools (R0, sensitivity) on which this project builds. They also record the transmission and recovery values used as placeholders in this project (Section 3.3.4).

**Models with mosquito life stages.**

- *Turner et al.* [[CITE:turner2015]] combine a human SEIR model, a mosquito SEI model and a four-stage mosquito life cycle (egg, larva, pupa, adult), with climate effects and competition among mosquitoes. The population is hypothetical (560 humans, 2,500 mosquitoes) and is not calibrated to any location. The model is available as an open BioModels record, which makes it useful for checking an implementation, though not for calibration.
- *Padder et al.* [[CITE:padder2025]] extend the SEIR–SEI structure with immature and adult mosquito stages and control functions for a generic vector-borne disease. With their parameter set R0 ≈ 0.742, and controls reduce infected humans and adult mosquitoes. Temperature and rainfall are discussed but not coupled into the equations.

**Climate–parasite and climate–vector experiments.**

- *Paaijmans et al.* [[CITE:paaijmans2012]] infected *An. stephensi* with the rodent parasite *P. yoelii* at 20–26 °C. Higher temperature sped up parasite development but reduced the fraction of mosquitoes surviving to become infectious, so transmission is not monotonic in temperature.
- *Waite et al.* [[CITE:waite2019]] measured *P. falciparum* development at 17–20 °C and found it faster than the conventional degree-day model predicts, especially under realistic daily temperature fluctuation.

Both are laboratory studies. They are sources of temperature-response parameters, not field data.

**Climate-forced malaria model.** *Madito, Brooke and Silal* [[CITE:madito2026]] compare three formulations of temperature and rainfall effects in one vector–host compartmental model across African climatic regions. The formulations include temperature-dependent biting, mortality and EIP, and a rainfall-dependent carrying capacity. The three give substantially different predictions: stable seasonal transmission, extended peaks, or irregular rainfall-driven peaks. The model is driven by World Bank Climate Change Knowledge Portal data. It is the closest methodological reference for the climate coupling in this project.

**Urban India.** *Santos-Vega et al.* [[CITE:santosvega2016]] model monthly ward-level *P. vivax* and *P. falciparum* cases in Ahmedabad (2002–2014) with phenomenological and statistical models (Markov-chain and negative-binomial GLM/GLMM). Their best models combine seasonality, temperature, two socio-economic risk regions and neighbouring wards. The study is the closest match to this project's setting, but it is not a mechanistic SEIR–SEI model.

[[TAB:litcompare|Comparison of the eight papers logged in the Literature Matrix]]

| Ref. | Model type | Compartments (human / vector) | Climate variables | Key parameters (abridged) | Limitations noted | Verified against paper |
|---|---|---|---|---|---|---|
| [[CITE:waite2019]] | Lab study of parasite development; not a transmission model | — / *An. stephensi*, *An. gambiae* (experimental) | Temperature; daily fluctuation | EIP measured at 17–20 °C | Narrow temperature range; lab only; no rainfall or human epidemiology | [[PH: yes/no]] |
| [[CITE:turner2015]] | SEIR–SEI + egg/larva/pupa life cycle | S_h, E_h, I_h, R_h / S_v, E_v, I_v + egg, larva, pupa | Rainfall / geo-climate effects | Carrying capacity 2×10⁴; transmission probabilities 0.02 and 0.8333; mosquito mortality 0.1429 | Generic parameters; hypothetical population; not calibrated | [[PH: yes/no]] |
| [[CITE:osman2017]] | Human SEIR + mosquito SEI ODE | S_h, E_h, I_h, R_h / S_v, E_v, I_v | None | Recovery 0.0035; mosquito→human probability 0.022; immunity loss 0.00017 | No climate forcing; many assumed parameters; no life stages | [[PH: yes/no]] |
| [[CITE:paaijmans2012]] | Lab vectorial-capacity study + simple model | — / *An. stephensi* with *P. yoelii* | Temperature (humidity fixed 90 ± 5%) | 4 temperatures (20–26 °C); 25 mosquitoes per sample | Rodent parasite; lab only; narrow range | [[PH: yes/no]] |
| [[CITE:madito2026]] | Vector–host compartmental model, 3 climate formulations | S, E, A, I_u, I_s, T_u, T_s, R / E_a, L_a, P_a, S_m, E_m, I_m | Temperature + rainfall | a(T), μ(T), development rates (T), K_m(R), γ_m(T); control coverage 25–90% | Formulations disagree; no mobility or socio-economic factors; no local case calibration | [[PH: yes/no]] |
| [[CITE:santosvega2016]] | Phenomenological model + Markov chain + GLM/GLMM | Not compartmental / vector implicit | Temperature, rainfall, relative humidity | Temperature lag 1 month, RH lag 2 months; up to 78 parameters | Ahmedabad-specific; statistical, not mechanistic | [[PH: yes/no]] |
| [[CITE:shah2013]] | SEIR–SEI deterministic ODE | S_h, E_h, I_h, R_h / S_v, E_v, I_v | None | p_h = 0.022, γ_h = 0.0035, μ_v = 0.0165 | No environmental forcing; homogeneous population | [[PH: yes/no]] |
| [[CITE:padder2025]] | Extended SEIR–SEI + immature/adult mosquitoes + controls | S_h, E_h, I_h, R_h / S_v, E_v, I_v, L, A | None in equations | R0 ≈ 0.742; controls u₁ = 0.46, u₂ = u₃ = 0.99 | No climate forcing; generic disease; larva and pupa combined | [[PH: yes/no]] |

### 2.2.3 Data identification

A separate Data Identification Table maps each logged paper to the datasets it used, their characteristics, format and availability. A Data Provenance Log to track candidate data sources is planned but has not yet been created [[PH: Data Provenance Log: not yet created / attach if created]]. The main findings are listed below and summarised in [[REF:dataid]].

- **Only 2 of the 8 papers use real, named datasets** (Madito et al. and Santos-Vega et al.). Two are laboratory studies that supply parameter values (Waite et al., Paaijmans et al.). The other four are theoretical models with literature-derived or assumed parameters.
- **Climate data.** The World Bank Climate Change Knowledge Portal (CCKP) [[CITE:cckp]] is recorded as public and open. It provides monthly temperature and precipitation for 1950–2022 on a grid of about 0.5°, downloadable through the web interface, an API or a public cloud bucket. It is the primary candidate source of climate data for any Indian target city.
- **Malaria case data is the bottleneck.** The closest comparable study obtained ward-level case data for Ahmedabad through direct collaboration with the municipal corporation's malaria division [[CITE:santosvega2016]]. Such data is not openly downloadable. A formal request to the relevant municipal or state health department will be needed.
- **Demographic data.** Census of India data [[CITE:census]] is public and can supply the population layer.
- **Laboratory papers as a parameter bank.** The temperature-response results of the two laboratory studies are best kept as a “literature parameter bank” that feeds the model directly, separate from the data-cleaning pipeline.

[[TAB:dataid|Summary of the data identification findings]]

| Ref. | Dataset(s) named in the paper | Data type | Availability |
|---|---|---|---|
| [[CITE:waite2019]] | None (original laboratory experiment) | Experimental counts | Not published as a dataset; parameter source |
| [[CITE:turner2015]] | BioModels record MODEL1805220001 (model file) | Simulation model (SBML) | Public (model, not field data) |
| [[CITE:osman2017]] | None | — | Not applicable (theoretical) |
| [[CITE:paaijmans2012]] | None (original laboratory experiment) | Experimental | Not published as a dataset; parameter source |
| [[CITE:madito2026]] | World Bank CCKP monthly temperature and precipitation, 1950–2022 | Gridded climate | Public, open access |
| [[CITE:santosvega2016]] | AMC malaria surveillance; meteorological station data (IIT Gandhinagar); Census of India; ward maps | Case counts, time series, census tables, GIS | AMC and station data: on request only. Census: public |
| [[CITE:shah2013]] | None | — | Not applicable (theoretical) |
| [[CITE:padder2025]] | None | — | Not applicable (theoretical) |

## 2.3 Gap or need identified

Across the eight papers reviewed, three patterns stand out:

- **Little coupling of climate into SEIR–SEI models.** The mechanistic models either have no climate forcing [[CITE:osman2017,shah2013,padder2025]] or have climate forcing that is generic and uncalibrated [[CITE:turner2015]]. Only one paper couples temperature and rainfall into the equations in several alternative ways [[CITE:madito2026]].
- **No mechanistic model of the urban setting.** The only urban Indian study is statistical, not mechanistic [[CITE:santosvega2016]].
- **No drainage variable.** None of the eight papers represents the condition of urban drainage, meaning the density of drains and how well they are maintained, as a variable that controls mosquito breeding habitat.

**Gap statement.** Within the literature reviewed so far, there is no mechanistic, climate-forced SEIR–SEI malaria model in which urban drainage condition controls larval carrying capacity and larval flushing. There is also no tool that can compare drainage-maintenance scenarios in terms of malaria risk. The project's proposed contribution, the Clogging Index Ω coupled to the aquatic stage of the mosquito model, addresses this gap. [[PH: confirm with literature — the novelty claim rests on 8 papers only and must be re-checked after the Lit Matrix is expanded to 15–25 papers]]

**Data need.** The data identification shows a second gap, a practical one. Climate data for an Indian city is openly available, but ward-level malaria case data is not. The model must therefore be built and tested on synthetic inputs first, with a data request to the health department running in parallel. This sequence shapes the design in Chapter 3.

[[SUMMARY]]
In summary, this chapter reviewed compartmental host–vector modelling, climate forcing and the urban context. It compared the eight logged papers in [[REF:litcompare]], and the data identification showed that only two of them use real, named datasets. It identified the World Bank CCKP as the climate-data source and municipal malaria case data as the main bottleneck. It stated the gap: no reviewed model links urban drainage condition to mosquito breeding habitat. This claim is to be confirmed once the literature base is expanded.
