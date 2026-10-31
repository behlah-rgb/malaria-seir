# BUILD NOTES: Design Experience project report

Status: started in Phase 2b (2026-11-01). This file will be completed in Phase 3 with the full placeholder list, the unverified items and the status of the submission checklist (Section 7 of the guide).

## Discrepancies between sources (running list)

1. **Data Provenance Log.** The executive summary says a Data Provenance Log was built, but no such file exists: it is neither a separate file nor a sheet in either workbook. The report states that the log is planned but not yet created:
   - 1.5 item 2, 2.2.3 and 3.5 (work breakdown item 3 and milestone M2) were reworded in Phase 2b.
   - Appendix V.2 carries the placeholder “[Data Provenance Log: not yet created / attach if created]”.
2. **β_hv = 0.022 and γ_h = 0.0035.** params.py attributes both to “approx. Chitnis, Hyman & Cushing 2008 (verify)”. The Lit Matrix records the same values for Shah & Gupta 2013 (p_h, γ_h) and Osman et al. 2017. As you decided, the report cites Shah & Gupta and Osman as where the values are recorded, and Chitnis as the params.py attribution [verify]. The meaning of p_h in Shah & Gupta is also to verify.
3. **Team size.** The executive summary mentions a “two-person roadmap”, while the template has 3 rows. The report uses [N] highlighted rows.
4. **Figures in git.** The model report (Appendix B) says the figures are gitignored, but they were committed on 2026-10-16 (commit 45f2a6f). This affects nothing in the report; it is noted for accuracy.
5. **Model report date.** PROGRESS.md dates the model report to 2026-10-14; the file and figures were last committed on 2026-10-16. Milestone M7 is flagged [confirm].

## Inferred rather than found (to confirm)

- The mapping of git versions v1–v1.3 to iterations 1–4 (Section 4.4.2) was inferred from the files changed in each commit.
- The per-file test counts and descriptions (Table 4.2) were taken from the test function names (`def test_…`), not from a pytest run.
- The derivation of IEEE initials from the full author names in the Lit Matrix; the Osman name format is flagged.
- The AI-use rows 2–4 (Appendix VII): the tool and purposes come from your brief and the presence of CLAUDE.md, not from a dated log.

## Format notes for the mentor

- Code listings (Appendix III) use a monospace font. The guide says Times New Roman throughout, so this needs mentor approval.
