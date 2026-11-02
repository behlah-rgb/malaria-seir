# Chapter 5: Individual Contribution, Teamwork and Reflection

[[INTRO]]
This chapter documents how the team worked: its structure and roles, each student's individual contribution, teamwork and leadership, each student's reflection, and the project management and AI-use disclosure. Assessment in Design Experience is individual, so each student completes their own Sections 5.2 and 5.4. This draft gives the structure and the documented facts only. All individual content is to be written by the students themselves.

## 5.1 Team structure, roles and responsibilities

The team has [[PH: N]] students under the supervision of [[PH: faculty mentor]], in the VIP vertical. Roles and responsibilities are not recorded in the project files; [[REF:roles]] is to be completed by the team.

[[TAB:roles|Team structure and roles]]

| Student | Role(s) | Main responsibilities |
|---|---|---|
| [[PH: Student 1]] | [[PH: role]] | [[PH: responsibilities]] |
| [[PH: Student 2]] | [[PH: role]] | [[PH: responsibilities]] |
| [[PH: Student N — one row per student]] | [[PH: role]] | [[PH: responsibilities]] |

The work packages that had to be covered are listed in Section 3.5:

1. scoping
2. literature review
3. data identification
4. conceptual model
5. specification
6. implementation and testing
7. simulation and analysis
8. model report
9. project report

[[PH: map each work package to the student(s) responsible]]

## 5.2 Individual contribution statement

Each student writes their own statement, and the team completes the contribution matrix in [[REF:contribmatrix]]. **No contribution has been written for any student in this draft.**

[[TAB:contribmatrix|Contribution matrix (work package × student; Evidence IDs from the IER)]]

| Work package | [[PH: Student 1]] | [[PH: Student 2]] | [[PH: Student N]] | Evidence IDs |
|---|---|---|---|---|
| Scoping and framing | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Literature review / Lit Matrix | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Data identification | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Conceptual model and specification | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Implementation and testing | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Simulation experiments and analysis | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |
| Model report and project report | [[PH: ]] | [[PH: ]] | [[PH: ]] | [[PH: ]] |

### 5.2.1 [[PH: Student 1 name]]

[[PH: To be written by the student. Prompts: Which tasks did you own? What outputs did you produce (files, tables, figures, code modules, sections of this report)? Which Evidence IDs in the IER support each output? What did you do that would not have been done without you?]]

### 5.2.2 [[PH: Student 2 name]]

[[PH: To be written by the student. Same prompts as 5.2.1.]]

### 5.2.3 [[PH: Student N name — one subsection per student]]

[[PH: To be written by the student. Same prompts as 5.2.1.]]

## 5.3 Teamwork and leadership

The project records document the following teamwork activities. Everything else is to be added by the team.

- **Recovery plan.** A one-day, two-person roadmap was drawn up to turn the scoping, literature and data work into a visible progress update for the professor (executive summary). [[PH: date, who took part, outcome]]
- **Supervisor meeting preparation.** A written model report was prepared for a supervisor meeting. It set out the model, the results, the limitations and a list of decisions requested from the professor (Section 4.4.1). [[PH: meeting date, attendees, outcome]]
- **Professor approval of the specification.** The mathematical specification is recorded as professor-approved. [[PH: date and form of approval]]

[[PH: meetings held (dates, attendance; minutes in Appendix IV)]]

[[PH: how work was coordinated (communication channels, shared repository, task tracking)]]

[[PH: conflicts or disagreements and how they were handled, or “none”]]

[[PH: stakeholder / partner interactions, or “none this semester”]]

[[PH: summary of peer feedback and mentor feedback]]

## 5.4 Reflection by each student

Each student writes their own reflection. **No reflection has been written for any student in this draft.**

### 5.4.1 [[PH: Student 1 name]]

[[PH: To be written by the student. Prompts: Which key decisions did you take or influence, and why? What was the hardest challenge and how did you deal with it? What did you learn, technically and about teamwork? What would you do differently, and what is your plan for improvement next semester?]]

### 5.4.2 [[PH: Student 2 name]]

[[PH: To be written by the student. Same prompts as 5.4.1.]]

### 5.4.3 [[PH: Student N name — one subsection per student]]

[[PH: To be written by the student. Same prompts as 5.4.1.]]

## 5.5 Project management, professional conduct and AI-use disclosure

### 5.5.1 Project management

The project records show the following management practices.

- **Version control.** The code and documents are kept in a git repository. The recorded history is:
  - 13 October 2026: project skeleton and specification
  - 14 October 2026: versions v1 to v1.3
  - 16 October 2026: model report and figures
  - 1 November 2026: report inputs
- **Progress log.** docs/PROGRESS.md records, for each task, the files changed, the reasons, the test results, unfinished items and the next step. It also keeps a list of decisions with their reasons and a list of open questions for the professor.
- **Deviation log.** docs/DEVIATIONS.md is a permanent, append-only record of every approved departure from the specification (Section 3.3.6).
- **Single source of truth.** The professor-approved specification (docs/SPEC.md) governs the mathematics. All parameter values live in one file, each with its source.

### 5.5.2 Professional conduct

- The approved equations were not changed without approval.
- Placeholder parameters and synthetic data are labelled wherever they are used.
- One parameter change (γ_h) is recorded with its reason, and the record states that it was not tuned to obtain a result.
- Results are reported as model behaviour, not as findings about a real city.

[[PH: add any other conduct points the team wishes to state]]

### 5.5.3 AI-use disclosure

[[PH: CONFIRM THIS SECTION — draft compiled from the git history, PROGRESS.md and the project files; the team must check every row]]

AI tools were used in this project as described below and in the log in Appendix VII. AI output was checked by the students before it was accepted [[PH: confirm]].

- **Tool.** [[PH: confirm]] Claude, used through Claude Code, an AI coding assistant. The repository contains a CLAUDE.md file: the working rules given to the assistant, first committed on 16 October 2026.
- **Purposes.** [[PH: confirm each]]
  - drafting and debugging the Python model code and tests
  - diagnosing the degenerate first run (Section 4.4.2). Deviation #5 (fixed 3-year spin-up) followed from this diagnosis. Deviation #9 (spin-up until convergence) followed when the 3-year spin-up did not settle. Deviations #6–#8 (rainfall memory, Ω-dependent retention time, importation) were realism changes decided by the student team.
  - drafting documentation: progress log, deviation log, model report
  - reviewing figures
  - drafting this project report from the team's records
- **Literature and data work.** [[PH: Were AI tools used to compile the Lit Matrix or the Data Identification Table? If yes, which tool, for what, and how was the output verified? To be completed by the team.]]
- **Verification.**
  - automated tests (42 passing), including hand-calculated values for every formula
  - a regression test of the spec variant
  - a rule that the AI tool may not change any equation from the approved specification without the team's approval, with every approved departure logged in DEVIATIONS.md and marked in the code
  - cross-checking every number in the model report against the model output
  - review by the faculty mentor [[PH: confirm whether and when the mentor reviewed the AI-assisted work]]

[[SUMMARY]]
In summary, this chapter set out the structure for documenting team roles, individual contributions with Evidence IDs, teamwork, and each student's reflection; the individual sections are to be completed by the students. It also recorded the documented project-management practices: version control, the progress and deviation logs, and the single specification. It gave a draft AI-use disclosure, which the team must confirm.
