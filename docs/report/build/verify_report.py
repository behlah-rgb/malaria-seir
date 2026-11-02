"""Verify docs/report/build/Project_Report.docx against the MPSTME format guide (Table 1).

Run after build_report.py:  .venv/bin/python docs/report/build/verify_report.py
Writes build/verify_report.txt and prints the same text. Checks:
  page size and margins; fonts (styles, East Asian attribute, run overrides); body size and
  spacing; heading sizes/weight/colour; sections and page-number formats; header and footer;
  caption positions (figures below, tables above); TOC/list fields and update-on-open;
  equations; every figure/table cross-referenced; every reference cited; every chapter has an
  introduction and closing summary; one conclusion; appendix numbering;
  yellow-highlighted placeholders per chapter; the list of [verify] items.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches

BUILD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD_DIR))
import build_report as br  # noqa: E402

OUT_TXT = BUILD_DIR / "verify_report.txt"
W = qn("w:val")


class Report:
    def __init__(self):
        self.lines: list[str] = []
        self.fails = 0

    def check(self, ok: bool, label: str, detail: str = "") -> None:
        self.lines.append(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" -- {detail}" if detail else ""))
        self.fails += 0 if ok else 1

    def info(self, text: str) -> None:
        self.lines.append(text)


def style_fonts(style) -> dict:
    rpr = style.element.find(qn("w:rPr"))
    rf = rpr.find(qn("w:rFonts")) if rpr is not None else None
    return {} if rf is None else {k.split("}")[1]: v for k, v in rf.attrib.items()}


def para_text(p_el) -> str:
    """Paragraph text; a line break inside a heading counts as one space."""
    out = []
    for el in p_el.iter(qn("w:t"), qn("w:br")):
        out.append(" " if el.tag == qn("w:br") else (el.text or ""))
    return "".join(out)


def highlighted_groups(p_el) -> list[str]:
    """Concatenate consecutive yellow-highlighted runs of one paragraph into strings."""
    groups, cur = [], []
    for r in p_el.iter(qn("w:r")):
        hl = r.find(f"{qn('w:rPr')}/{qn('w:highlight')}")
        txt = "".join(t.text or "" for t in r.iter(qn("w:t")))
        if hl is not None and hl.get(W) == "yellow":
            cur.append(txt)
        elif txt and cur:
            groups.append("".join(cur)); cur = []
    if cur:
        groups.append("".join(cur))
    return groups


def main() -> None:
    rep = Report()
    doc = Document(br.OUT_PATH)
    body = doc.element.body

    # ---- page setup -------------------------------------------------------
    rep.info("== Page setup")
    secs = doc.sections
    for i, s in enumerate(secs, 1):
        a4 = abs(s.page_width - br.PAGE_W) < Inches(0.01) and abs(s.page_height - br.PAGE_H) < Inches(0.01)
        m = (s.left_margin == br.MARGIN_L and s.right_margin == s.top_margin == s.bottom_margin == br.MARGIN_OTHER)
        rep.check(a4 and m, f"Section {i}: A4, margins L 1.5\" / T,B,R 1\"")

    # ---- fonts and styles ----------------------------------------------------
    rep.info("== Fonts and styles")
    defaults = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    rf = defaults.find(qn("w:rFonts"))
    rep.check(all(rf.get(qn(f"w:{a}")) == br.FONT for a in ("ascii", "hAnsi", "eastAsia", "cs")),
              "Document default font Times New Roman (incl. East Asian)")
    normal = doc.styles["Normal"]
    f = style_fonts(normal)
    rep.check(f.get("ascii") == br.FONT and f.get("eastAsia") == br.FONT and normal.font.size.pt == 12
              and normal.paragraph_format.line_spacing == 1.5, "Normal: TNR 12 pt, line spacing 1.5")
    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
        st = doc.styles[name]
        f = style_fonts(st)
        col = st.element.find(f"{qn('w:rPr')}/{qn('w:color')}")
        black = col is not None and col.get(W) == "000000" and col.get(qn("w:themeColor")) is None
        rep.check(f.get("ascii") == br.FONT and f.get("eastAsia") == br.FONT and st.font.size.pt == size
                  and st.font.bold and black and not any("Theme" in k for k in f),
                  f"{name}: TNR {size} pt bold black, no theme fonts")
    cap = doc.styles["Caption Text"]
    rep.check(style_fonts(cap).get("ascii") == br.FONT and cap.font.size.pt == 10, "Caption style: TNR 10 pt")
    used = Counter()
    for r in doc.element.iter(qn("w:r")):
        rf = r.find(f"{qn('w:rPr')}/{qn('w:rFonts')}")
        if rf is not None and rf.get(qn("w:ascii")):
            used[rf.get(qn("w:ascii"))] += 1
    other = {k: v for k, v in used.items() if k not in (br.FONT, br.MONO)}
    rep.check(not other, "No run-level fonts other than TNR (and Courier New for code)", str(dict(used)))
    code_paras = sum(1 for p in doc.paragraphs if p.style.name == "Code Listing")
    rep.info(f"  Note: {code_paras} code-listing paragraph(s) in Courier New 8 pt (Appendix III) -- needs mentor approval.")

    # ---- sections, numbering, header/footer -----------------------------------
    rep.info("== Sections, page numbers, header and footer")
    rep.check(len(secs) == 3, "Three sections: cover+certificate / front matter / main body", f"found {len(secs)}")
    fmts = []
    for s in secs:
        pg = s._sectPr.find(qn("w:pgNumType"))
        fmts.append(None if pg is None else (pg.get(qn("w:fmt")), pg.get(qn("w:start"))))
    rep.check(fmts == [None, ("lowerRoman", "1"), ("decimal", "1")],
              "Cover unnumbered; front matter lower Roman from i; Chapter 1 onwards decimal from 1", str(fmts))
    cover_hdr = "".join(p.text for p in secs[0].header.paragraphs).strip()
    cover_ftr = "".join(p.text for p in secs[0].footer.paragraphs).strip()
    rep.check(not secs[0].header.is_linked_to_previous and not cover_hdr and not cover_ftr,
              "Cover/certificate: no header text, no page number")
    hdr = secs[1].header
    htxt = " | ".join(c.text for t in hdr.tables for c in t.rows[0].cells)
    rep.check(br.TITLE in htxt and "2026" in htxt, "Header: title left, academic year right", htxt[:60] + " ...")
    ftr_xml = secs[1].footer._element.xml
    right = secs[1].footer.paragraphs[0].alignment == 2
    rep.check("PAGE" in ftr_xml and right, "Footer: PAGE field, right-aligned")
    rep.check(secs[2].header.is_linked_to_previous and secs[2].footer.is_linked_to_previous,
              "Main body inherits header and footer")

    # ---- fields ----------------------------------------------------------------
    rep.info("== Fields")
    instr = [t.text.strip() for t in doc.element.iter(qn("w:instrText"))]
    rep.check(any(i.startswith('TOC \\o "1-3"') for i in instr), "Table of contents field (TOC \\o 1-3)")
    rep.check(any('\\c "Fig"' in i for i in instr), "List of figures field (TOC \\c Fig)")
    rep.check(any('\\c "Table"' in i for i in instr), "List of tables field (TOC \\c Table)")
    uf = doc.settings.element.find(qn("w:updateFields"))
    rep.check(uf is not None and uf.get(W) == "true", "Fields set to update when the document opens")
    rep.info(f"  SEQ Fig fields: {sum(i.startswith('SEQ Fig') for i in instr)}; "
             f"SEQ Table fields: {sum(i.startswith('SEQ Table') for i in instr)}")

    # ---- body walk: captions, equations, chapters, placeholders -----------------
    rep.info("== Captions, equations and chapter structure")
    elems = list(body.iterchildren())
    style_names = {st.style_id: st.name for st in doc.styles}
    fig_caps = tab_caps = fig_bad = tab_bad = 0
    eq_count = 0
    eq_numbers = []
    chapter = "Front matter"
    ph_by_chapter: "OrderedDict[str, int]" = OrderedDict()
    verify_items: list[tuple[str, str]] = []
    h1_titles = []
    after_h1 = {}
    last_h1 = None

    def count_ph(p_el):
        for g in highlighted_groups(p_el):
            items = re.findall(r"\[[^\]]*\]", g) or [g]
            ph_by_chapter[chapter] = ph_by_chapter.get(chapter, 0) + len(items)
            for it in items:
                if "verify" in it.lower():
                    verify_items.append((chapter, it))

    for idx, el in enumerate(elems):
        if el.tag == qn("w:p"):
            ps = el.find(f"{qn('w:pPr')}/{qn('w:pStyle')}")
            style_id = ps.get(W) if ps is not None else "Normal"
            text = para_text(el)
            if style_names.get(style_id) == "Heading 1":
                title = text.strip()
                h1_titles.append(title)
                chapter = title
                last_h1 = title
                after_h1[title] = None
            elif last_h1 and after_h1.get(last_h1) is None and text.strip():
                after_h1[last_h1] = style_id
            sname = style_names.get(style_id, style_id)
            if sname == "Caption Text" and text.startswith("Fig."):
                fig_caps += 1
                prev = elems[idx - 1]
                if not (prev.tag == qn("w:p") and prev.find(f".//{qn('w:drawing')}") is not None):
                    fig_bad += 1
            elif sname == "Caption Text" and text.startswith("Table"):
                tab_caps += 1
                if elems[idx + 1].tag != qn("w:tbl"):
                    tab_bad += 1
            elif sname == "Equation":
                if el.find(f".//{qn('w:drawing')}") is not None:
                    eq_count += 1
                    eq_numbers.append(text.strip())
            count_ph(el)
        elif el.tag == qn("w:tbl"):
            for p in el.iter(qn("w:p")):
                count_ph(p)
    for hdr_p in secs[1].header._element.iter(qn("w:p")):
        chapter_save = chapter
        chapter = "Page header"
        count_ph(hdr_p)
        chapter = chapter_save

    rep.check(fig_caps == 13 and fig_bad == 0, "Figure captions below figures (TNR 10)", f"{fig_caps} captions, {fig_bad} misplaced")
    rep.check(tab_bad == 0, "Table captions above tables (TNR 10)", f"{tab_caps} captions, {tab_bad} misplaced")
    rep.check(eq_count == 16, "Equations rendered as images with numbers", f"{eq_count}: {', '.join(eq_numbers)}")

    chapters = [t for t in h1_titles if t.startswith("Chapter")]
    rep.check(len(chapters) == 6, "Six chapters present", "; ".join(chapters))
    rep.check(all(after_h1[c] in ("Normal", None) or after_h1[c] not in ("Heading2",) for c in chapters),
              "Each chapter heading is followed by an introduction paragraph (not a section heading)")
    concl = [t for t in h1_titles if "Conclusion" in t]
    rep.check(len(concl) == 1 and concl[0].startswith("Chapter 6"), "Only one conclusion (Chapter 6)", str(concl))
    apps = [t for t in h1_titles if t.startswith("Appendix")]
    romans = [re.match(r"Appendix ([IVX]+)\b", a).group(1) for a in apps]
    rep.check(romans == ["I", "II", "III", "IV", "V", "VI", "VII"], "Appendices numbered I-VII in Roman capitals", str(romans))
    order_ok = (h1_titles.index("Abstract") < h1_titles.index("Table of Contents") < h1_titles.index("List of Figures")
                < h1_titles.index("List of Tables") < h1_titles.index("Abbreviations") < h1_titles.index(chapters[0])
                and h1_titles.index(chapters[-1]) < h1_titles.index("References") < h1_titles.index(apps[0]))
    rep.check(order_ok, "Order of contents as in Table 2 of the guide")

    # ---- Markdown-level checks: intro/summary, cross-references, citations --------
    rep.info("== Content checks (chapter sources)")
    texts = {f: (br.CHAPTER_DIR / f).read_text(encoding="utf-8") for f in br.FILES}
    for f in br.FILES[1:7]:
        blocks = br.parse_blocks(texts[f])
        kinds = [b[0] for b in blocks]
        h1 = kinds.index("h")
        intro_ok = kinds[h1 + 1] == "intro" and kinds[h1 + 2] == "p"
        summ_ok = "summary" in kinds and kinds[kinds.index("summary") + 1] == "p" and kinds.index("summary") >= len(kinds) - 2
        rep.check(intro_ok and summ_ok, f"{f}: introduction paragraph and closing summary lines")
    all_txt = "".join(br.strip_comments(t) for t in texts.values())
    defs = set(re.findall(r"\[\[(?:FIG|TAB):(\w+)\|", all_txt))
    refs = set(re.findall(r"\[\[REF:(\w+)\]\]", all_txt))
    rep.check(defs <= refs, "Every numbered figure and table is referred to in the text", f"unreferenced: {sorted(defs - refs)}")
    body_text = "\n".join(para_text(p) for p in body.iter(qn("w:p")))
    refs_start = body_text.find("\nReferences\n")
    cited_nums = {int(n) for n in re.findall(r"\[(\d+)\]", body_text[:refs_start])}
    nref = len(re.findall(r"^- \w+:", texts["references.md"], flags=re.M))
    rep.check(cited_nums == set(range(1, nref + 1)), "Every listed reference is cited in the text, numbered in citation order",
              f"{nref} references; cited numbers {sorted(cited_nums)}")

    # ---- placeholders and [verify] items ------------------------------------------
    rep.info("== Yellow-highlighted placeholders by chapter")
    total = 0
    for ch, n in ph_by_chapter.items():
        rep.info(f"  {n:4d}  {ch}")
        total += n
    rep.info(f"  {total:4d}  TOTAL")
    rep.info(f"== [verify] items ({len(verify_items)})")
    for ch, it in verify_items:
        rep.info(f"  - {ch}: {it}")

    rep.info(f"\nSummary: {rep.fails} check(s) failed.")
    OUT_TXT.write_text("\n".join(rep.lines) + "\n", encoding="utf-8")
    print("\n".join(rep.lines))


if __name__ == "__main__":
    main()
