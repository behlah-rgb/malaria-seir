<!-- SECTION: cover (no page number) — Template T1, wording as in the format guide -->

::: center
[[LOGO]]

**A Compartmental SEIR-Vector Model for Malaria Transmission Dynamics under Climate Variability in Urban Environments**

**Design Experience [[PH: I / II / III]] Project Report**

submitted in partial fulfilment of the requirements of

**[[PH: Name of the Programme]]**

in

**[[PH: Name of the Stream / Department]]**

Vertical: VIP

by

[[PH: Name 1 (Roll No. / SAP ID)]]

[[PH: Name 2 (Roll No. / SAP ID)]]

[[PH: Name N (Roll No. / SAP ID) — one line per student; team size N to be confirmed]]

Under the supervision of

**[[PH: Name of Faculty Mentor]]**

[[PH: Designation, Department, MPSTME]]

**MPSTME, SVKM’s NMIMS (Deemed-to-be University), Mumbai**

**[[PH: 2026–27 — confirm academic year]]**
:::

[[PAGEBREAK]]

<!-- Template T2: Certificate (no page number) -->

::: center
**SVKM’s NMIMS University**

(Deemed-to-be University)

[[LOGO]]

**MUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING (MPSTME)**

**Vile Parle (W), Mumbai-56**

**[[PH: 2026–27 — confirm academic year]]**

**CERTIFICATE**
:::

This is to certify that the Design Experience [[PH: I / II / III]] project entitled “A Compartmental SEIR-Vector Model for Malaria Transmission Dynamics under Climate Variability in Urban Environments” has been carried out by [[PH: Names with Roll No.]] under my guidance and supervision, and has been submitted in partial fulfilment of the requirements of [[PH: Name of the Programme]] in [[PH: Name of the Stream]] of MPSTME, SVKM’s NMIMS (Deemed-to-be University), Mumbai, India.

[[SIGNATURES: Project mentor (name and signature) (Internal Guide) | Vertical SPOC (name and signature) | HoD (name and signature)]]

**Date:**

**Place: Mumbai**

<!-- SECTION: front matter (lower-case Roman page numbers start here) -->

# *ACKNOWLEDGEMENT

[[PH: Thank the faculty mentor, vertical SPOC, industry / community / competition partners, funding or resource providers and peers. Mention the specific help received.]]

| Name | Roll No. | SAP ID |
|---|---|---|
| [[PH: Student 1]] | [[PH: ]] | [[PH: ]] |
| [[PH: Student 2]] | [[PH: ]] | [[PH: ]] |
| [[PH: Student N — one row per student]] | [[PH: ]] | [[PH: ]] |

# *DECLARATION

We declare that this report is our original work and reflects our own contribution in the semester of registration. We have acknowledged all contributors and cited all sources. The use of AI tools, if any, is disclosed in Section 5.5 and Appendix VII, and AI-generated content has been verified by us.

Signatures of students: ____________ ____________ ____________ [[PH: one line per student]]  Date: ____________

[[PAGEBREAK]]

# *Abstract

Malaria transmission depends on mosquitoes, and mosquito numbers depend on climate and on the water available for breeding. In cities, blocked or sparse drains leave standing water after rain, but most transmission models describe climate and ignore the condition of urban drainage. This project asks whether the build quality and maintenance of urban drainage change modelled malaria outcomes in a city ward, and how much maintenance is “enough” for a given drainage network.

During this semester the team scoped the problem, organised a literature search into six keyword clusters and logged eight papers in a structured Literature Matrix. The team also identified data sources for each paper: the World Bank Climate Change Knowledge Portal is the primary candidate for climate data, while ward-level malaria case data must be requested from a municipal health department. The team then built a conceptual model and implemented the professor-approved mathematical specification in Python. It is an eight-compartment ordinary differential equation model that couples a human SEIR system to a mosquito system with an aquatic stage. Temperature enters through the biting rate, the parasite incubation rate and mosquito mortality. Rainfall enters through the larval carrying capacity and larval flushing. A Clogging Index Ω, built from drainage density and maintenance efficiency, links drainage condition to breeding habitat.

The main technical contribution is a tested, documented simulation tool with two variants. The “spec” variant implements the approved equations exactly. The “extended” variant adds rainfall memory and imported infections. The tool also includes a 9 × 9 drainage-scenario sweep, threshold analysis of Ω and sensitivity analysis, 42 passing automated tests, and a logged record of every departure from the specification.

With synthetic climate, mostly placeholder parameters and an uncalibrated habitat scale, worse drainage gave more malaria in every run. Only the worst illustrative ward sustained local transmission, above Ω ≈ 8.7. The Ω at which the reproduction number never exceeds 1 was about 100 to 200 times smaller. These results describe model behaviour, not any real city. The next steps are to lock the target city, obtain real climate and case data, source the placeholder parameters and calibrate the model.

[[PAGEBREAK]]

# *Table of Contents

[[TOC]]

[[PAGEBREAK]]

# *List of Figures

[[LOF]]

[[PAGEBREAK]]

# *List of Tables

[[LOT]]

[[PAGEBREAK]]

# *Abbreviations

| Abbreviation | Full form |
|---|---|
| AMC | Ahmedabad Municipal Corporation |
| API | Annual parasite incidence |
| CCKP | Climate Change Knowledge Portal (World Bank) |
| DFE | Disease-free equilibrium |
| EIP | Extrinsic incubation period |
| EIR | Entomological inoculation rate |
| ELP | Egg, larva, pupa (mosquito aquatic stages) |
| GLM / GLMM | Generalised linear (mixed) model |
| HoD | Head of Department |
| IEEE | Institute of Electrical and Electronics Engineers |
| IER | [[PH: full form of IER as used by the Design Experience office]] |
| MPSTME | Mukesh Patel School of Technology Management & Engineering |
| ODE | Ordinary differential equation |
| R0 | Basic reproduction number |
| SEI | Susceptible–Exposed–Infectious |
| SEIR | Susceptible–Exposed–Infectious–Recovered |
| SPOC | Single point of contact |
| VIP | Vertically Integrated Projects [[PH: confirm full form used by MPSTME]] |
