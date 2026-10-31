# Markup used in the chapter files (parsed by build/build_report.py)

This file is not part of the report. It explains the tags used in 00_front_matter.md ... appendices.md.

| Tag | Meaning in the Word file |
|---|---|
| `[[PH: text]]` | Yellow-highlighted placeholder, printed as `[text]`. Every one is listed in BUILD_NOTES.md. |
| `[[CITE:key]]` / `[[CITE:key1,key2]]` | IEEE citation `[n]`; numbers are assigned in order of first citation (keys defined in references.md). |
| `[[FIG:id\|file.png\|caption]]` | Figure from docs/report/figures/, caption BELOW, "Fig. c.n:". |
| `[[TAB:id\|caption]]` | Caption ABOVE the pipe table that follows, "Table c.n:". |
| `[[REF:id]]` | Cross-reference to a figure or table number, e.g. "Fig. 3.1" / "Table 2.1". |
| `[[EQ:label\|plain-text form]]` | Numbered equation image (c.n), from build/equations.py. The plain text is for review only and is copied from docs/SPEC.md. |
| `[[EQREF:label]]` | Equation number in parentheses, e.g. (3.1). |
| `[[INTRO]]` / `[[SUMMARY]]` | Marks the chapter introduction / closing summary paragraph (used by the checker; not printed). |
| `[[PAGEBREAK]]`, `[[TOC]]`, `[[LOF]]`, `[[LOT]]` | Page break and Word fields for contents, list of figures, list of tables. |
| `::: center` ... `:::` | Block of centred paragraphs (cover, certificate). |
| `[[LOGO]]` | inputs/logo_nmims.png if present, else a highlighted `[insert NMIMS logo]` box. |
| `[[SIGNATURES: a \| b \| c]]` | Row of signature lines with the given labels underneath. |
| `<!-- SECTION: ... -->` | Section break (page-numbering change). Other HTML comments are ignored. |
| `# Chapter N: Title` | Heading 1 (chapter). `##` = Heading 2 (section), `###` = Heading 3 (subsection). |
| `# *Title` | Unnumbered front-matter heading (still appears in the TOC where the guide's T4 lists it). |
