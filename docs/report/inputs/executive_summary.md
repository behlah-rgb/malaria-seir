Executive summary: Group 1 malaria SEIR-Vector project
Project: A compartmental SEIR-Vector model for malaria transmission dynamics under climate variability in urban environments.
Completed so far
1. Scoping and framing. The title is broken into its components: compartmental modelling, a human SEIR system coupled to a mosquito SEI system, climate-dependent parameters, and an urban setting. A research workflow was set out for the literature review and data acquisition phases.
2. Literature review infrastructure. A structured Lit Matrix (Excel) and a Data Provenance Log were built. Search buzzwords were organised into six clusters: model structure, vector biology, climate coupling, urban context, parameter estimation, and regional grounding. Candidate papers were sourced across the clusters, and 8 are logged in the matrix with model type, compartments, climate variables, parameters and limitations.
3. Data identification. A Data Identification Table maps each logged paper to its datasets, characteristics, format and availability. Findings:
Only 2 of the 8 papers use real, named datasets. The other 6 are lab studies that supply parameter values, or purely theoretical models.
The World Bank Climate Change Knowledge Portal is confirmed public and usable for temperature and rainfall (monthly, 1950-2022, ~0.5° grid). It is the primary climate-data source.
Malaria case data is the bottleneck. The closest comparable study (Ahmedabad, Santos-Vega et al.) got ward-level data through direct collaboration with the municipal corporation, so it is not openly downloadable. Census of India data for the demographic layer is public.
4. Conceptual model structure. The model diagram was finalised in three parts:
Human compartments Sₕ → Eₕ → Iₕ → Rₕ, with births, waning immunity (ρ), and natural and disease-induced death.
Vector compartments Aᵥ → Sᵥ → Eᵥ → Iᵥ, with oviposition feedback limited by carrying capacity.
Host-vector coupling through the biting rate a(T) and the transmission probabilities β_hv and β_vh.
The temperature-dependent terms are the climate entry points: the biting rate a(T), the extrinsic incubation rate γ_m(T), mosquito mortality μᵥ(T), and the infection forces λ_hv(T) and λ_vh(T).
5. Recovery plan. A one-day, two-person roadmap was drawn up to turn the above into a visible progress update for the professor.
Still open
Target city is not yet confirmed as locked. Ahmedabad is the strongest candidate.
Malaria case data has not been obtained. A formal request to the relevant municipal or state health department still needs to be drafted and sent.
Lit Matrix stands at 8 papers, against a target of 15-25 after triage.
Mathematical formulation: the compartment flows are diagrammed, but the full ODE system and the functional forms for the temperature-dependent terms are not yet written out or implemented.
Baseline simulation: no working Python or MATLAB model exists yet.
Suggested next steps
Lock the target city and send the data request.
Write out the full ODE system from the diagrams.
Implement a non-climate baseline simulation, then add the temperature forcing.
