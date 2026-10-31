<!-- SECTION: main body (decimal page numbers restart at 1) -->

# Chapter 1: Introduction

[[INTRO]]
This chapter introduces the project topic: how climate and the condition of urban drainage together shape malaria transmission in a city. It explains why the topic was chosen and what this report covers. It then states the problem, names the stakeholders, and lists the objectives and expected outcomes. It also separates the work done this semester from any earlier background. The chapter ends with an outline of the rest of the report.

## 1.1 Background of the project topic

### 1.1.1 Malaria as a vector-borne disease

Malaria is caused by *Plasmodium* parasites and is spread between people by the bites of infected female *Anopheles* mosquitoes. The parasite has to develop inside the mosquito before the mosquito can infect a person, and inside a person before that person can infect a mosquito. Transmission therefore depends on three groups of factors: how many mosquitoes there are, how often they bite, and how long they survive compared with the time the parasite needs to develop. Compartmental models describe this cycle by dividing the human and mosquito populations into states such as susceptible, exposed, infectious and recovered. Ordinary differential equations (ODEs) then track how individuals move between the states over time [[CITE:osman2017,shah2013]].

### 1.1.2 Climate and malaria

Temperature affects almost every step of the mosquito and parasite life cycle. Laboratory work shows that parasite development inside the mosquito speeds up with temperature, while mosquito survival and vector competence can fall at warmer temperatures. Transmission therefore does not simply rise with temperature [[CITE:paaijmans2012]]. At the cool end, parasite development has been observed to be faster than the classic degree-day formula predicts [[CITE:waite2019]]. Rainfall mainly controls the amount of water available for mosquito larvae. A recent comparison found that three different ways of linking temperature and rainfall to a malaria model gave substantially different predictions [[CITE:madito2026]]. How climate is put into a model is therefore itself a design decision.

### 1.1.3 Urban malaria and drainage

Malaria is not only a rural problem. In the Indian city of Ahmedabad, ward-level malaria risk was shown to be structured jointly by population density, climate variables and poverty [[CITE:santosvega2016]]. In a city, much of the standing water in which mosquitoes breed is linked to the drainage network. When drains are sparse, or are present but blocked, water remains after rain and creates breeding habitat. When drains are clear, heavy rain can flush larvae away. [[PH: supporting reference needed for the drainage–standing water–breeding link; not yet in the Lit Matrix]] This project expresses the drainage condition of a ward as a single Clogging Index, Ω, built from drainage density and maintenance efficiency, and feeds it into the mosquito part of a malaria transmission model (Chapter 3).

## 1.2 Motivation and scope of the report

The motivation is practical. If drainage condition measurably changes malaria risk, then drain construction and drain maintenance become malaria-control tools as well as civic services. The model can then ask how much maintenance is “enough” for a given drainage network.

This report covers the work done in the semester of registration ([[PH: confirm semester and dates]]):

- scoping of the project title
- a structured literature review and data identification
- the conceptual model
- implementation of the professor-approved mathematical specification as a tested Python model
- simulation experiments on illustrative wards and drainage scenarios

The report does **not** present findings about any real city, for four reasons:

- The climate inputs used so far are synthetic.
- Most parameter values are placeholders awaiting literature sources.
- The habitat scale K_0 is uncalibrated.
- No malaria case data has yet been obtained.

The results therefore show how the model behaves. They are not predictions.

## 1.3 Problem statement / need, and stakeholders or users

**Problem statement.** Existing compartmental malaria models include climate through temperature and rainfall, but none of the models reviewed in this project represents the condition of urban drainage as a driver of mosquito breeding habitat (Section 2.3). Planners and health departments therefore have no mechanistic way to compare drainage scenarios, such as building more drains or maintaining existing ones better, in terms of malaria risk.

**Need.** A transparent, reproducible model is needed. It should couple human and mosquito infection dynamics to temperature, rainfall and a drainage index. It should be able to rank drainage scenarios and find threshold drainage conditions. It should also state clearly which of its inputs are measured and which are assumed.

**Stakeholders and potential users.** The following groups are identified from the project records as potential users of the model or providers of its data. No interaction with them has taken place yet.

- **Municipal or state health departments and vector-control units.** They hold ward-level malaria surveillance data. In the closest comparable study, the Ahmedabad Municipal Corporation provided such data through institutional collaboration [[CITE:santosvega2016]].
- **Urban planners and municipal drainage and maintenance departments.** They decide on drain construction and cleaning.
- **Researchers in climate–health modelling.**
- **The faculty mentor and the VIP vertical** as academic stakeholders.

[[PH: record any stakeholder or partner interactions that took place; none are documented]]

## 1.4 Objectives and expected outcomes

The objectives, derived from the project title and the research question in the model report, are:

1. To build a compartmental SEIR (human) – SEI with aquatic stage (mosquito) model of malaria transmission, with temperature- and rainfall-dependent parameters.
2. To represent urban drainage condition through a Clogging Index Ω and link it to larval carrying capacity and larval flushing.
3. To implement the model reproducibly in Python. Every parameter is recorded with its source or flagged as a placeholder, every departure from the approved specification is logged, and automated tests check the implementation.
4. To simulate illustrative wards and a grid of drainage scenarios, and to find threshold values of Ω and the minimum maintenance level needed for a given drainage density.
5. To identify the real climate, demographic and malaria data needed to apply the model to a target Indian city.

**Expected outcomes for this semester:**

- a structured literature and data review
- an approved model specification
- a working, tested simulation tool with documented results on synthetic inputs
- a clear list of the data and parameter sources needed before the model can be applied to a real city

## 1.5 Project context and continuity

**Vertical and partner.** The project is carried out under the VIP vertical. No industry or community partner is recorded [[PH: confirm: no partner]].

**Work of this semester.** Based on the project records, the following work was carried out this semester [[PH: confirm that the scoping, Lit Matrix and Data Identification work belongs to this semester]]:

1. **Scoping and framing.** The title was broken into its components: compartmental modelling, a human SEIR system coupled to a mosquito SEI system, climate-dependent parameters, and the urban setting. A research workflow was set out for the literature review and data acquisition phases.
2. **Literature review infrastructure.** A Literature Matrix was set up; a Data Provenance Log is planned but has not yet been created. Search terms were organised into six clusters, and eight papers were logged (Chapter 2).
3. **Data identification.** Each logged paper was mapped to its datasets, data characteristics, format and availability (Section 2.2.3).
4. **Conceptual model.** A three-part model diagram was finalised: human compartments, vector compartments, and host–vector coupling through the biting rate.
5. **Mathematical specification.** The equations were written up and approved by the professor in a specification document (docs/SPEC.md).
6. **Implementation and experiments.** The project skeleton was created on 13 October 2026, and the model went through versions v1 to v1.3 on 14 October 2026 (git history). The work produced a written model report for a supervisor meeting.

**Earlier work.** [[PH: describe any work done before this semester (earlier team or semester), or state “None — the project started this semester”]]

**Continuity.** Chapter 6 lists the items that remain open and hand-over notes so that the project can continue in the next semester.

## 1.6 Organization of the report

- **Chapter 2** reviews the domain and the eight logged papers, summarises the data identification findings and states the research gap.
- **Chapter 3** sets out the requirements, the design alternatives and decisions, the selected model design with its equations, the relevant standards and ethical considerations, and the project plan.
- **Chapter 4** describes the implementation, testing, results and their analysis, the iterations made and the limitations.
- **Chapter 5** documents team structure, individual contributions, teamwork, reflection and the AI-use disclosure.
- **Chapter 6** gives the conclusions and future scope.
- The references and Appendices I–VII follow.

[[SUMMARY]]
In summary, this chapter introduced malaria as a climate-sensitive, vector-borne disease. It explained why the condition of urban drainage may matter for mosquito breeding and stated the problem: models do not yet link drainage condition to malaria transmission. The chapter set five objectives, listed the work done this semester, and noted that all results in this report come from synthetic inputs and placeholder parameters.
