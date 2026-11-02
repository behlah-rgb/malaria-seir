# BUILD NOTES: Design Experience project report

Draft built on 2026-11-01. The output is `docs/report/build/Project_Report.docx`, built from the Markdown in `docs/report/chapters/`.

## How to rebuild and re-check

From the project folder:

```bash
.venv/bin/python docs/report/build/build_report.py    # renders equations + diagrams, writes the .docx and manifest.json
.venv/bin/python docs/report/build/verify_report.py   # format and content checks -> build/verify_report.txt
```

- `build/equations.py` holds the LaTeX for every equation. Each entry also stores the equation exactly as written in docs/SPEC.md, and the build stops if a SPEC string or a chapter's `[[EQ:…]]` text differs.
- `build/diagrams.py` draws the two block diagrams.
- The build reads only `docs/report/` plus the four source files shown in Appendix III. It does not run `main.py` or `pytest`.

## Build and verification result

- **Contents:** 13 figures, 24 numbered tables, 16 equations (3.1–3.16), 13 references and 272 highlighted placeholders.
- **Automated checks:** `verify_report.py` passes all 36 checks; the full output is in `build/verify_report.txt`. The checks cover:
  - A4 page size and margins, in all three sections
  - Times New Roman for the document defaults, Normal and Heading 1–3, including the East Asian font attribute and with no theme fonts
  - 12 pt body text with 1.5 line spacing; headings 18/14/12 pt, bold and black
  - an unnumbered cover and certificate, lower-case Roman numerals for the front matter, and decimal numbers from Chapter 1 restarting at 1
  - the header (title on the left, year on the right) and the right-aligned page number in the footer
  - figure captions below their figures and table captions above their tables, both TNR 10 pt
  - the contents, list-of-figures and list-of-tables fields, and update-fields-on-open
  - an introduction and closing summary in every chapter; only one conclusion
  - appendices numbered I–VII
  - every figure and table referred to in the text; all 13 references cited, numbered in order of first citation
- **Visual check: NOT done.** LibreOffice is not installed (nor pandoc or pdftoppm), and nothing was installed. The built-in macOS Quick Look produced a preview of the start of the document. It confirmed the font and the centred T1/T2 layout, but it ignores page breaks and highlighting, so pagination and the final page look must be checked in Word.

## Figures checked against MODEL_REPORT.md

All 11 copied figures were opened, and every value printed on them was compared with MODEL_REPORT.md. **No mismatches** were found at the rounding shown on the figures:

- ward_infections: poor-ward peak ≈ 212 around day 310; other wards ≈ 10 and 13.
- ward_vectors: peaks ≈ 37,500 and ≈ 7,150 adults, which with N_h = 10,000 matches 3.77 and 0.715 per human.
- ward_R0: peaks ≈ 1.02, 1.3 and 2.34.
- Spec heatmaps: worst cell 19 (vs 18.5) and 1.8; ward cells 3.8e-8, 1.2e-6, 5.7e-10 and 3.1e-8; smallest cell 5.4e-10.
- Extended heatmaps: 2.1e2, 10 and 13; 21, 1.3 and 1.5.
- r0_vs_omega: Ω\* = 0.0437 and 0.0825; persistence thresholds 8.67 and 8.76.
- variant_comparison: mosquito peaks ≈ 0.78 / 0.715 and 4.39 / 3.77 per human.
- sensitivity: ranges 1.65–404 (poor ward) and 1.08–8.61 (best ward).

Captions corrected to match what each image actually shows:

- r0_vs_omega plots peak and mean R0(t). It does **not** plot local growth.
- ward_vectors shows absolute adult numbers, not mosquitoes per human.
- ward_R0 also has temperature and rainfall panels.
- The two extended heatmaps draw the minimum-M_i line for Ω\*.
- omega_scatter has two panels (attack rate and peak I_h).
- The sensitivity caption now lists the 3 × 3 grid.

## Format decisions the mentor should confirm

1. **Code listings** (Appendix III) are in Courier New 8 pt with single spacing. The guide says Times New Roman throughout, so this needs mentor approval.
2. **Table text** is 10 pt, or 9 pt for tables with 7–8 columns and 8 pt for 9–10 columns, so that wide tables fit the page. The guide gives no size for table text. The page header is 9 pt.
3. **Caption numbering.** The chapter prefix (for example "3.") is typed text. Only the running number is a Word SEQ field, which restarts in each chapter, so the lists of figures and tables still work. Chapter-numbered STYLEREF captions were not used, because the chapter headings are typed text and not Word auto-numbering.
4. **Cross-references** in the text ("Fig. 4.1", "Table 2.1", "(3.5)") are written as plain text computed by the build script, not as Word REF fields. Change figures or tables in the Markdown and rebuild; do not renumber in Word.
5. **Equations** are 300 dpi images, rendered in STIX fonts to match Times New Roman, with the numbers right-aligned. They are not editable Word equations.
6. **Chapter titles** are written as "Chapter N", a line break, then the title, as in template T5. Word normally turns a line break into a space in the table of contents. If it does not, edit the TOC entry or remove the break.
7. The list of figures and the list of tables are Word TOC fields. Their layout is Word's: caption text, dotted leader, page number. This is close to, but not exactly, the three-column layout described under T4.
8. The team table in T3 and the abbreviations table have no caption, following the template.
9. The NMIMS logo is a highlighted placeholder. Put the file at `docs/report/inputs/logo_nmims.png` and rebuild; it will then appear on the cover and the certificate.

## Discrepancies between sources

1. **Data Provenance Log.** The executive summary says a Data Provenance Log was built, but no such file exists: it is neither a separate file nor a sheet in either workbook. The report says the log is planned but not yet created:
   - Section 1.5 (item 2), Section 2.2.3 and Section 3.5 (work-breakdown item 3 and milestone M2) were reworded in Phase 2b.
   - Appendix V.2 carries "[Data Provenance Log: not yet created / attach if created]".
2. **β_hv = 0.022 and γ_h = 0.0035.** params.py attributes both to "approx. Chitnis, Hyman & Cushing 2008 (verify)". The Lit Matrix records the same values for Shah & Gupta 2013 (p_h, γ_h) and Osman et al. 2017. As you decided, the report cites Shah & Gupta and Osman as where the values are recorded, and Chitnis as the params.py attribution [verify]. The meaning of p_h in Shah & Gupta is also to be verified.
3. **Team size.** The executive summary mentions a "two-person roadmap", while the template has 3 rows. The report uses [N] highlighted rows.
4. **Figures in git.** MODEL_REPORT.md Appendix B says the figures are gitignored, but they were committed on 2026-10-16 (commit 45f2a6f). This does not affect the report.
5. **Model report date.** PROGRESS.md dates the model report to 2026-10-14, but the file and figures were last committed on 2026-10-16. Milestone M7 is flagged [confirm].
6. **Executive summary "Still open" list.** It says no ODE system or Python model exists yet; the repository shows both now exist. The report follows the repository, as you instructed. The target city and real malaria case data remain open.

## Inferred rather than found (to confirm)

- How git versions v1–v1.3 map to iterations 1–4 (Section 4.4.2). This was inferred from the files changed in each commit.
- The per-file test counts in Table 4.2 were confirmed with `pytest --collect-only` (42 collected; no tests were run). The descriptions are taken from the test function names.
- IEEE initials were derived from the full author names in the Lit Matrix; the format of Osman's name is flagged.
- Appendix VII rows 2–4 and Section 5.5.3: the tool and purposes come from your brief and the presence of CLAUDE.md, not from a dated log. Row 5 (this report being drafted with Claude Code from 1 Nov 2026) is first-hand.
- The block diagrams (Fig. 3.1, Fig. 3.2) were drawn from SPEC.md and the module map. They are not a copy of the team's own conceptual diagram, which was not available.

## Unverified items

- **Every Lit Matrix entry.** None has been checked against its paper. Table 2.1 has a highlighted "Verified against paper: yes/no" column for you to fill in.
- **References.** There are 20 highlighted [verify] fields in the reference list:
  - month of publication (missing for all 10 journal and conference references)
  - volume, issue and pages for Waite 2019, Mordecai 2013 and Chitnis 2008
  - the full conference name and pages for Turner 2015
  - the issuing body of the Census of India
  - initials and titles for Mordecai, Martens and Chitnis
  - Osman's name format
- **Data sources.** The access dates for CCKP and the Census of India are placeholders.
- **Parameter sources** (Section 3.3 and Appendix II):
  - Brière constants: Mordecai et al. 2013
  - degree-day constants: the "classic Detinova/Macdonald" model. It has no reference number until a source is confirmed.
  - mortality coefficients: Martens 1997
  - β_vh, β_hv and γ_h: Chitnis et al. 2008
- **Novelty claim.** The gap statement in Section 2.3 and the closing statement in Section 6.1 carry [confirm with literature]; they rest on 8 papers only.
- **Supporting reference.** The link from drainage to standing water to breeding (Section 1.1.3) has no source yet.
- The full list of [verify] items in the document (31) is at the end of `build/verify_report.txt`.

## Submission checklist (Section 7 of the guide): status of this draft

| Item | Status |
|---|---|
| Cover page, certificate, acknowledgement / team details and declaration completed | **Not yet.** Templates T1–T3 are reproduced, but names, programme, mentor, SPOC, HoD, year, logo and acknowledgement are placeholders, and signatures are needed. |
| Abstract is about one page; contents, lists of figures, tables and abbreviations included | **Done.** The abstract is 352 words, about one page. The lists are Word fields and must be updated in Word (see below). The full forms of IER and VIP need confirming. |
| Font, spacing, margins, headers, footers, caption positions and page numbering as per Table 1 | **Done in the file** (automated checks pass). **Visual check in Word still needed.** Code listings in Courier New need mentor approval. |
| All six chapters present; each has an introduction and summary lines; one conclusion at the end | **Done.** |
| Chapter 5 has the individual contribution and reflection of every team member, with Evidence IDs | **Not yet.** Only stubs with prompts; each student must write their own Sections 5.2 and 5.4. |
| References numbered, cited in the text and in IEEE style; standards followed are mentioned | **Partly.** References are numbered and all cited, but [verify] fields remain. The standards statement in Section 3.4 is a placeholder. |
| Appendices I to VII included as applicable; AI-use disclosure completed | **Partly.** All seven are present. I, IV, V.2, V.4 and VI are placeholders. The AI disclosure (Section 5.5.3 and Appendix VII) is a draft marked [confirm]. |
| Similarity (plagiarism / AI) check done as per University practice | **Not done.** For the team to do. |
| Report verified and signed by the faculty mentor before the Portfolio Review / Final Evaluation | **Not done.** |

## Placeholders by chapter

All placeholders are yellow-highlighted and in square brackets. The counts come from the built .docx.

| Part | Count |
|---|---|
| Front matter (cover, certificate, T3) | 27 |
| Abbreviations | 2 |
| Chapter 1 | 6 |
| Chapter 2 | 12 |
| Chapter 3 | 62 |
| Chapter 4 | 15 |
| Chapter 5 | 70 |
| Chapter 6 | 3 |
| References | 22 |
| Appendix I | 21 |
| Appendix II | 6 |
| Appendix III | 0 |
| Appendix IV | 3 |
| Appendix V | 2 |
| Appendix VI | 1 |
| Appendix VII | 19 |
| Page header (academic year) | 1 |
| **Total** | **272** |

## Full placeholder list

Identical placeholders in the same part are merged and shown with a count (×n).

### Front matter (27)

- [insert NMIMS logo] (×2)
- [I / II / III] (×2)
- [Name of the Programme] (×2)
- [Name of the Stream / Department]
- [Name 1 (Roll No. / SAP ID)]
- [Name 2 (Roll No. / SAP ID)]
- [Name N (Roll No. / SAP ID) — one line per student; team size N to be confirmed]
- [Name of Faculty Mentor]
- [Designation, Department, MPSTME]
- [2026–27 — confirm academic year] (×2)
- [Names with Roll No.]
- [Name of the Stream]
- [Thank the faculty mentor, vertical SPOC, industry / community / competition partners, funding or resource providers and peers. Mention the specific help received.]
- [Student 1]
- [ ] (×6)
- [Student 2]
- [Student N — one row per student]
- [one line per student]

### Abbreviations (2)

- [full form of IER as used by the Design Experience office]
- [confirm full form used by MPSTME]

### Chapter 1 Introduction (6)

- [supporting reference needed for the drainage–standing water–breeding link; not yet in the Lit Matrix]
- [confirm semester and dates]
- [record any stakeholder or partner interactions that took place; none are documented]
- [confirm: no partner]
- [confirm that the scoping, Lit Matrix and Data Identification work belongs to this semester]
- [describe any work done before this semester (earlier team or semester), or state “None — the project started this semester”]

### Chapter 2 Background Study (12)

- [verified against paper: yes/no, to be completed per paper in Table 2.1]
- [list the actual search keywords used in each cluster and the databases searched; only the cluster names are recorded]
- [yes/no] (×8)
- [Data Provenance Log: not yet created / attach if created]
- [confirm with literature — the novelty claim rests on 8 papers only and must be re-checked after the Lit Matrix is expanded to 15–25 papers]

### Chapter 3 Design and Development Process (62)

- [record any stakeholder input]
- [w] (×5)
- [ ] (×24)
- [confirm the reasons and who made the decision, and when]
- [add the team’s reason for choosing Python over MATLAB]
- [verify] (×3)
- [verify source; no reference number assigned until the source is confirmed]
- [verify the attribution, and the meaning of ph in Shah and Gupta]
- [pending — confirm whether and when the professor reviewed deviations #1–#9]
- [list any standard followed, or confirm “none”]
- [confirm whether institutional ethics approval or a data-use agreement is required before the data request]
- [date] (×16)
- [not yet created]
- [confirm; file last updated 16 Oct 2026]
- [minutes]
- [in progress]
- [insert Gantt chart once the planned dates for M1–M11 are confirmed]
- [task allocation per student — not recorded in the project files; see also Section 5.1]

### Chapter 4 Implementation, Results and Analysis (15)

- [name the student(s) who implemented each module — not recorded in the project files]
- [confirm the marker-to-entry match by reviewing each marker]
- [name the student(s) who produced this analysis] (×7)
- [professor / mentor feedback from the supervisor meeting — date, attendees and feedback to be added. Do not fill in until the minutes are available.]
- [peer feedback, if any]
- [record the professor’s answers to these questions]
- [confirm; inferred from the files changed in each commit]
- [insert the original first heatmap image if a copy exists; it was overwritten by later runs]
- [name the student(s) responsible for each iteration]

### Chapter 5 Individual Contribution, Teamwork and Reflection (70)

- [N]
- [faculty mentor]
- [Student 1] (×2)
- [role] (×3)
- [responsibilities] (×3)
- [Student 2] (×2)
- [Student N — one row per student]
- [map each work package to the student(s) responsible]
- [Student N]
- [ ] (×28)
- [Student 1 name] (×2)
- [To be written by the student. Prompts: Which tasks did you own? What outputs did you produce (files, tables, figures, code modules, sections of this report)? Which Evidence IDs in the IER support each output? What did you do that would not have been done without you?]
- [Student 2 name] (×2)
- [To be written by the student. Same prompts as 5.2.1.] (×2)
- [Student N name — one subsection per student] (×2)
- [date, who took part, outcome]
- [meeting date, attendees, outcome]
- [date and form of approval]
- [meetings held (dates, attendance; minutes in Appendix IV)]
- [how work was coordinated (communication channels, shared repository, task tracking)]
- [conflicts or disagreements and how they were handled, or “none”]
- [stakeholder / partner interactions, or “none this semester”]
- [summary of peer feedback and mentor feedback]
- [To be written by the student. Prompts: Which key decisions did you take or influence, and why? What was the hardest challenge and how did you deal with it? What did you learn, technically and about teamwork? What would you do differently, and what is your plan for improvement next semester?]
- [To be written by the student. Same prompts as 5.4.1.] (×2)
- [add any other conduct points the team wishes to state]
- [CONFIRM THIS SECTION — draft compiled from the git history, PROGRESS.md and the project files; the team must check every row]
- [confirm] (×2)
- [confirm each]
- [Were AI tools used to compile the Lit Matrix or the Data Identification Table? If yes, which tool, for what, and how was the output verified? To be completed by the team.]
- [confirm whether and when the mentor reviewed the AI-assisted work]

### Chapter 6 Conclusion and Future Scope (3)

- [confirm with literature]
- [professor / mentor feedback on these conclusions, to be added after the supervisor meeting]
- [update with the professor’s answers]

### References (22)

- [verify month] (×6)
- [verify author-name format; recorded as “Mojeeb Al-Rahman El-Nor Osman”]
- [verify vol., no., pp., month] (×3)
- [verify full conference name, pp., month]
- [date accessed] (×2)
- [verify issuing body]
- [verify initials] (×5)
- [verify title] (×2)
- [verify title and source]

### Appendix I Summary of the IER and Evidence Register (21)

- [Insert the summary of the IER / Design Experience Portfolio and the Evidence Register. Evidence IDs are not recorded in the project files.]
- [ ] (×14)
- [e.g. Lit Matrix workbook]
- [e.g. docs/report/inputs/]
- [e.g. Data Identification Table]
- [e.g. approved specification (docs/SPEC.md)]
- [e.g. model code and tests (git versions v1–v1.3)]
- [e.g. model report for the supervisor meeting]

### Appendix II Model Specifications (6)

- [verify] (×5)
- [verify source]

### Appendix IV Meeting Minutes, Peer Feedback and Mentor Feedback (3)

- [Insert minutes of team meetings and supervisor meetings (date, attendees, points discussed, decisions, actions). No minutes are recorded in the project files.]
- [Insert peer feedback forms.]
- [Insert mentor feedback, including the outcome of the supervisor meeting for which the model report was prepared.]

### Appendix V VIP Evidence (2)

- [Data Provenance Log: not yet created / attach if created]
- [status of any draft research paper (none / in preparation / submitted), target venue]

### Appendix VI Publications, Certificates and IP (1)

- [list papers presented or published, competition certificates and patent / IP filings, or state “None this semester”]

### Appendix VII AI-Tool Use Disclosure Log (19)

- [CONFIRM THIS LOG — draft compiled from the git history, PROGRESS.md and the project files; every row must be checked by the team]
- [dates]
- [tool, if any]
- [Was an AI tool used to compile the Lit Matrix and/or the Data Identification Table? To be completed by the team.]
- [ ] (×4)
- [confirm] (×10)
- [any other AI use (grammar, brainstorming, visualisation, literature search)]

### Page header (1)

- [2026–27 — confirm academic year]
