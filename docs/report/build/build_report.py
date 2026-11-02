"""Build docs/report/build/Project_Report.docx from the Markdown chapters.

Re-runnable:  .venv/bin/python docs/report/build/build_report.py
(from the project folder). It
  1. checks every [[EQ:...]] against docs/SPEC.md (via equations.py) and every citation key
     against chapters/references.md, and stops with an error on any mismatch;
  2. renders the equation images and block diagrams (equations.py, diagrams.py);
  3. writes the Word file with the MPSTME format: A4, Times New Roman, 12 pt / 1.5 spacing,
     margins L 1.5", T/B/R 1", header (title | academic year), page number bottom right,
     unnumbered cover/certificate, Roman front matter, decimal numbering from Chapter 1,
     Heading 1/2/3 (18/14/12 pt bold, black), captions in TNR 10 (figures below, tables above),
     Word fields for the contents and the lists of figures and tables;
  4. writes build/manifest.json (numbering of figures, tables, equations and references).

Markup is documented in docs/report/chapters/_MARKUP.md. It reads only docs/report/ and the
four source files listed in Appendix III; it never modifies anything outside docs/report/.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

BUILD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD_DIR))
import diagrams  # noqa: E402
import equations  # noqa: E402

REPORT_DIR = BUILD_DIR.parent
REPO_DIR = REPORT_DIR.parents[1]
CHAPTER_DIR = REPORT_DIR / "chapters"
FIG_DIR = REPORT_DIR / "figures"
LOGO_PATH = REPORT_DIR / "inputs" / "logo_nmims.png"
OUT_PATH = BUILD_DIR / "Project_Report.docx"
MANIFEST_PATH = BUILD_DIR / "manifest.json"

FILES = ["00_front_matter.md", "01_introduction.md", "02_background.md", "03_design.md",
         "04_results.md", "05_contribution.md", "06_conclusion.md", "references.md", "appendices.md"]

TITLE = ("A Compartmental SEIR-Vector Model for Malaria Transmission Dynamics under Climate "
         "Variability in Urban Environments")
YEAR_PLACEHOLDER = "2026–27 — confirm academic year"

FONT = "Times New Roman"
MONO = "Courier New"
BLACK = RGBColor(0, 0, 0)
PAGE_W, PAGE_H = Inches(8.27), Inches(11.69)  # A4
MARGIN_L, MARGIN_OTHER = Inches(1.5), Inches(1.0)
TEXT_W_IN = 8.27 - 1.5 - 1.0  # 5.77 in
FRONT_TITLES = {"ACKNOWLEDGEMENT", "DECLARATION"}  # bold centred titles, not in the TOC (template T3)

# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"^\[\[(PAGEBREAK|TOC|LOF|LOT|INTRO|SUMMARY|LOGO|SECTION)\]\]$")
FIG_RE = re.compile(r"^\[\[FIG:(\w+)\|([^|\]]+)\|(.+)\]\]$")
TAB_RE = re.compile(r"^\[\[TAB:(\w+)\|(.+)\]\]$")
EQ_RE = re.compile(r"^\[\[EQ:(\w+)\|(.+)\]\]$")
CODE_RE = re.compile(r"^\[\[CODE:([^\]]+)\]\]$")
SIG_RE = re.compile(r"^\[\[SIGNATURES:(.+)\]\]$")
LIST_RE = re.compile(r"^(\s*)(-|\d+\.)\s+(.*)$")
REF_LINE_RE = re.compile(r"^- (\w+):\s*(.+)$")
CITE_RE = re.compile(r"\[\[CITE:([\w,]+)\]\]")


def strip_comments(text: str) -> str:
    """Turn SECTION comments into [[SECTION]] tokens and drop all other HTML comments."""
    text = re.sub(r"<!--\s*SECTION:.*?-->", "\n[[SECTION]]\n", text, flags=re.S)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def parse_blocks(text: str) -> list[tuple]:
    """Split one chapter file into blocks: ('p', text, centred), ('h', level, text), ('li', ...), ..."""
    lines = strip_comments(text).split("\n")
    blocks: list[tuple] = []
    para: list[str] = []
    centred = False

    def flush() -> None:
        if para:
            blocks.append(("p", " ".join(para), centred))
            para.clear()

    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        i += 1
        if s == "::: center":
            flush(); centred = True; continue
        if s == ":::":
            flush(); centred = False; continue
        if not s:
            flush(); continue
        if m := TOKEN_RE.match(s):
            flush(); blocks.append((m.group(1).lower(),)); continue
        if m := FIG_RE.match(s):
            flush(); blocks.append(("fig", m.group(1), m.group(2), m.group(3))); continue
        if m := TAB_RE.match(s):
            flush(); blocks.append(("tabcap", m.group(1), m.group(2))); continue
        if m := EQ_RE.match(s):
            flush(); blocks.append(("eq", m.group(1), m.group(2))); continue
        if m := CODE_RE.match(s):
            flush(); blocks.append(("code", m.group(1))); continue
        if m := SIG_RE.match(s):
            flush(); blocks.append(("sig", [x.strip() for x in m.group(1).split("|")])); continue
        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            blocks.append(("h", level, s[level:].strip()))
            continue
        if s.startswith("|"):
            flush()
            rows = [s]
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip()); i += 1
            blocks.append(("table", parse_table(rows)))
            continue
        if m := LIST_RE.match(raw):
            flush()
            indent = len(m.group(1).replace("\t", "    "))
            item = [m.group(3).strip()]
            while (i < len(lines) and lines[i].strip() and lines[i].startswith(" ")
                   and not LIST_RE.match(lines[i])):
                item.append(lines[i].strip()); i += 1
            marker = m.group(2)
            blocks.append(("li", 0 if indent < 2 else 1, marker != "-", marker, " ".join(item)))
            continue
        para.append(s)
    flush()
    return blocks


def parse_table(rows: list[str]) -> list[list[str]]:
    """Parse pipe-table rows into a list of cell lists, dropping the |---| separator row."""
    out = []
    for r in rows:
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", r.strip().strip("|"))]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        out.append([c.replace("\\|", "|") for c in cells])
    return out


def chapter_key(h1_text: str) -> str | None:
    """'Chapter 3: ...' -> '3'; 'Appendix II: ...' -> 'II'; front/back matter -> None."""
    if m := re.match(r"Chapter (\d+):", h1_text):
        return m.group(1)
    if m := re.match(r"Appendix ([IVX]+):", h1_text):
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Pass 1: numbering of figures, tables, equations and references
# ---------------------------------------------------------------------------
@dataclass
class Numbering:
    figs: dict[str, str] = field(default_factory=dict)
    tabs: dict[str, str] = field(default_factory=dict)
    eqs: dict[str, str] = field(default_factory=dict)
    first_in_chapter: set[str] = field(default_factory=set)  # "fig:id"/"tab:id" that reset the SEQ
    captions: dict[str, str] = field(default_factory=dict)
    refs: dict[str, int] = field(default_factory=dict)
    ref_text: dict[str, str] = field(default_factory=dict)


def number_everything(parsed: dict[str, list[tuple]], texts: dict[str, str]) -> Numbering:
    """Assign chapter-based numbers (3.1, II.1) and IEEE reference numbers by first citation."""
    num = Numbering()
    for fname in FILES:
        if fname == "references.md":
            continue
        key = None
        counters = {"fig": 0, "tab": 0, "eq": 0}
        for b in parsed[fname]:
            if b[0] == "h" and b[1] == 1:
                key = chapter_key(b[2])
                counters = {"fig": 0, "tab": 0, "eq": 0}
            elif b[0] in ("fig", "tabcap", "eq"):
                kind = {"fig": "fig", "tabcap": "tab", "eq": "eq"}[b[0]]
                if key is None:
                    raise SystemExit(f"{fname}: {kind} '{b[1]}' outside a numbered chapter/appendix")
                counters[kind] += 1
                label = f"{key}.{counters[kind]}"
                target = {"fig": num.figs, "tab": num.tabs, "eq": num.eqs}[kind]
                if b[1] in target:
                    raise SystemExit(f"duplicate id {kind}:{b[1]}")
                target[b[1]] = label
                if counters[kind] == 1 and kind != "eq":
                    num.first_in_chapter.add(f"{kind}:{b[1]}")
                if kind == "fig":
                    num.captions[f"fig:{b[1]}"] = b[3]
                elif kind == "tab":
                    num.captions[f"tab:{b[1]}"] = b[2]

    order: list[str] = []
    for fname in FILES:
        if fname == "references.md":
            continue
        for group in CITE_RE.findall(strip_comments(texts[fname])):
            for k in group.split(","):
                if k not in order:
                    order.append(k)
    listed = {}
    for line in strip_comments(texts["references.md"]).split("\n"):
        if m := REF_LINE_RE.match(line.strip()):
            listed[m.group(1)] = m.group(2)
    missing, uncited = set(order) - set(listed), set(listed) - set(order)
    if missing or uncited:
        raise SystemExit(f"Reference mismatch. Cited but not listed: {missing}; listed but not cited: {uncited}")
    num.refs = {k: i + 1 for i, k in enumerate(order)}
    num.ref_text = listed
    return num


# ---------------------------------------------------------------------------
# Low-level docx helpers
# ---------------------------------------------------------------------------
def set_rfonts(rpr, name: str) -> None:
    """Set ascii/hAnsi/eastAsia/cs fonts on an rPr element and remove theme-font overrides."""
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rf.attrib.pop(qn(a), None)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)


def style_font(st, size: float | None = None, bold: bool | None = None, italic: bool | None = False,
               name: str = FONT) -> None:
    """Force a style to the given font (all scripts), black colour, size and weight."""
    st.font.name = name
    rpr = st.element.get_or_add_rPr()
    set_rfonts(rpr, name)
    col = rpr.find(qn("w:color"))
    if col is not None:
        rpr.remove(col)
    st.font.color.rgb = BLACK
    if size is not None:
        st.font.size = Pt(size)
    if bold is not None:
        st.font.bold = bold
    if italic is not None:
        st.font.italic = italic


def add_field(par, instr: str, result: str = "") -> None:
    """Insert a complex Word field {instr} with a cached result."""
    def fld(kind: str):
        r = par.add_run()
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        r._r.append(el)
    fld("begin")
    r = par.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r._r.append(it)
    fld("separate")
    par.add_run(result)
    fld("end")


def insert_in_order(parent, child, successors: list[str]) -> None:
    """Insert child before the first existing successor tag (keeps OOXML schema order)."""
    for el in parent:
        if el.tag in [qn(s) for s in successors]:
            el.addprevious(child)
            return
    parent.append(child)


def set_page_numbering(section, fmt: str, start: int = 1) -> None:
    """Set w:pgNumType (lowerRoman / decimal) with a restart value on a section."""
    sp = section._sectPr
    old = sp.find(qn("w:pgNumType"))
    if old is not None:
        sp.remove(old)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    pg.set(qn("w:start"), str(start))
    insert_in_order(sp, pg, ["w:cols", "w:formProt", "w:vAlign", "w:noEndnote", "w:titlePg",
                             "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid",
                             "w:printerSettings", "w:sectPrChange"])


def set_update_fields_on_open(doc) -> None:
    """Ask Word to update all fields (TOC, lists, SEQ) when the file is opened."""
    st = doc.settings.element
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    insert_in_order(st, uf, ["w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat",
                             "w:docVars", "w:rsids", "m:mathPr", "w:attachedSchema",
                             "w:themeFontLang", "w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
                             "w:doNotAutoCompressPictures", "w:forceUpgrade", "w:captions",
                             "w:readModeInkLockDown", "w:smartTagType", "w:shapeDefaults",
                             "w:doNotEmbedSmartTags", "w:decimalSymbol", "w:listSeparator"])


def shade_cell(cell, fill: str) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def repeat_header(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def no_borders(table) -> None:
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "nil")
        borders.append(e)
    tblpr.append(borders)


# ---------------------------------------------------------------------------
# Inline text: placeholders, citations, cross-references, emphasis, subscripts
# ---------------------------------------------------------------------------
ESC = "\x01"
INLINE_RE = re.compile(
    r"\[\[PH:(?P<ph>.*?)\]\]|\[\[CITE:(?P<cite>[\w,]+)\]\]|\[\[REF:(?P<ref>\w+)\]\]"
    r"|\[\[EQREF:(?P<eqref>\w+)\]\]|\*\*(?P<bold>.+?)\*\*"
    r"|(?<![\w*])\*(?=\S)(?P<ital>.+?)(?<=\S)\*(?![\w*])|`(?P<code>[^`]+)`")
PLAIN_RE = re.compile(
    r"\[\[PH:(?P<ph>.*?)\]\]|\[\[CITE:(?P<cite>[\w,]+)\]\]|\[\[REF:(?P<ref>\w+)\]\]"
    r"|\[\[EQREF:(?P<eqref>\w+)\]\]")
# Subscripts only for the model's own symbols, so file and function names stay intact.
SUB_RE = re.compile(
    r"(?<![\w.])([SEIRNAKTDMLPqcpμβγαδΛφθ])_(base|flush|min|eff|vh|hv|[hvmidAsauu0-2])(?![\w])")


class Inline:
    """Writes Markdown-ish inline text into a python-docx paragraph."""

    def __init__(self, num: Numbering):
        self.num = num
        self.placeholders = 0

    def _run(self, par, text: str, size=None, bold=False, italic=False, mono=False,
             highlight=False, subscript=False):
        r = par.add_run(text.replace(ESC, "*"))
        if size:
            r.font.size = Pt(size)
        if bold:
            r.bold = True
        if italic:
            r.italic = True
        if subscript:
            r.font.subscript = True
        if mono:
            r.font.name = MONO
            set_rfonts(r._r.get_or_add_rPr(), MONO)
        if highlight:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        return r

    def plain(self, par, text: str, **kw) -> None:
        """Plain text with model-symbol subscripts (S_h -> S with subscript h)."""
        pos = 0
        for m in SUB_RE.finditer(text):
            if m.start() > pos:
                self._run(par, text[pos:m.start()], **kw)
            self._run(par, m.group(1), **kw)
            self._run(par, m.group(2), subscript=True, **kw)
            pos = m.end()
        if pos < len(text):
            self._run(par, text[pos:], **kw)

    def write(self, par, text: str, size=None, bold=False, italic=False, emphasis=True) -> None:
        text = text.replace("\\*", ESC)
        rx = INLINE_RE if emphasis else PLAIN_RE
        pos = 0
        kw = dict(size=size, bold=bold, italic=italic)
        for m in rx.finditer(text):
            if m.start() > pos:
                self.plain(par, text[pos:m.start()], **kw)
            g = m.groupdict()
            if g.get("ph") is not None:
                inner = g["ph"].strip()
                self.placeholders += 1
                self.plain(par, f"[{inner}]" if inner else "[ ]", highlight=True, **kw)
            elif g.get("cite"):
                nums = [self.num.refs[k] for k in g["cite"].split(",")]
                self._run(par, ", ".join(f"[{n}]" for n in nums), size=size, bold=bold, italic=italic)
            elif g.get("ref"):
                rid = g["ref"]
                if rid in self.num.figs:
                    self._run(par, f"Fig. {self.num.figs[rid]}", **kw)
                elif rid in self.num.tabs:
                    self._run(par, f"Table {self.num.tabs[rid]}", **kw)
                else:
                    raise SystemExit(f"[[REF:{rid}]] has no figure or table")
            elif g.get("eqref"):
                self._run(par, f"({self.num.eqs[g['eqref']]})", **kw)
            elif g.get("bold") is not None:
                self.write(par, g["bold"].replace(ESC, "\\*"), size=size, bold=True, italic=italic)
            elif g.get("ital") is not None:
                self.write(par, g["ital"].replace(ESC, "\\*"), size=size, bold=bold, italic=True)
            elif g.get("code") is not None:
                self._run(par, g["code"], size=(size or 12) - 1, mono=True)
            pos = m.end()
        if pos < len(text):
            self.plain(par, text[pos:], **kw)


# ---------------------------------------------------------------------------
# Document builder
# ---------------------------------------------------------------------------
class ReportBuilder:
    def __init__(self, num: Numbering):
        self.num = num
        self.doc = Document()
        self.inline = Inline(num)
        self.pending_break = False
        self.after_section_break = False
        self.pending_table_caption: tuple[str, str] | None = None
        self.center_first_done = False
        self.sections_seen = 0
        self.eq_paths = {}
        self._setup_styles()

    # ---- styles -----------------------------------------------------------
    def _setup_styles(self) -> None:
        styles = self.doc.styles
        # Document defaults: Times New Roman for every script
        defaults = styles.element.find(qn("w:docDefaults"))
        rpr = defaults.find(qn("w:rPrDefault")).find(qn("w:rPr"))
        set_rfonts(rpr, FONT)

        normal = styles["Normal"]
        style_font(normal, 12, False)
        pf = normal.paragraph_format
        pf.line_spacing = 1.5
        pf.space_before = Pt(0)
        pf.space_after = Pt(6)

        for name, size, before, after in (("Heading 1", 18, 0, 18), ("Heading 2", 14, 12, 6),
                                          ("Heading 3", 12, 10, 4)):
            st = styles[name]
            style_font(st, size, True, False)
            st.paragraph_format.space_before = Pt(before)
            st.paragraph_format.space_after = Pt(after)
            st.paragraph_format.line_spacing = 1.5
            st.paragraph_format.keep_with_next = True
            if name == "Heading 1":
                st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                st.paragraph_format.page_break_before = True

        for name in ("List Bullet", "List Bullet 2"):
            st = styles[name]
            style_font(st, 12)
            st.paragraph_format.space_after = Pt(3)
            st.paragraph_format.line_spacing = 1.5

        def new_par_style(name: str, size: float, font: str = FONT, align=None, spacing=1.0,
                          after: float = 0, bold=False):
            st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = normal
            style_font(st, size, bold, False, font)
            st.paragraph_format.line_spacing = spacing
            st.paragraph_format.space_before = Pt(0)
            st.paragraph_format.space_after = Pt(after)
            if align is not None:
                st.paragraph_format.alignment = align
            return st

        new_par_style("Caption Text", 10, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)
        new_par_style("Table Text", 10)
        new_par_style("Code Listing", 8, font=MONO)
        new_par_style("Front Title", 16, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.5, after=12, bold=True)
        new_par_style("Header Text", 9)
        eq = new_par_style("Equation", 12, spacing=1.0, after=8)
        eq.paragraph_format.space_before = Pt(8)
        eq.paragraph_format.tab_stops.add_tab_stop(Inches(TEXT_W_IN / 2), WD_TAB_ALIGNMENT.CENTER)
        eq.paragraph_format.tab_stops.add_tab_stop(Inches(TEXT_W_IN), WD_TAB_ALIGNMENT.RIGHT)

    # ---- paragraphs ---------------------------------------------------------
    def para(self, style: str | None = None, align=None):
        p = self.doc.add_paragraph(style=style)
        if align is not None:
            p.paragraph_format.alignment = align
        if self.pending_break:
            p.paragraph_format.page_break_before = True
            self.pending_break = False
        if self.after_section_break:
            # The section break already starts a new page; avoid an extra blank page.
            p.paragraph_format.page_break_before = False
            self.after_section_break = False
        return p

    # ---- block renderers -----------------------------------------------------
    def heading(self, level: int, text: str) -> None:
        if level == 1 and text.startswith("*"):
            title = text[1:].strip()
            if title in FRONT_TITLES:
                p = self.para("Front Title")
                self.inline.write(p, title)
                return
            p = self.para("Heading 1")
            self.inline.write(p, title)
            return
        if level == 1:
            m = re.match(r"(Chapter \d+|Appendix [IVX]+):\s*(.+)", text)
            p = self.para("Heading 1")
            if m:
                p.add_run(m.group(1)).add_break(WD_BREAK.LINE)
                self.inline.write(p, m.group(2))
            else:
                self.inline.write(p, text)
            return
        p = self.para(f"Heading {min(level, 3)}")
        self.inline.write(p, text)

    def paragraph(self, text: str, centred: bool) -> None:
        if centred:
            p = self.para(align=WD_ALIGN_PARAGRAPH.CENTER)
            size = None
            if not self.center_first_done:
                size, self.center_first_done = 20, True  # cover title
            elif text == "**CERTIFICATE**":
                size = 16
            self.inline.write(p, text, size=size)
        else:
            p = self.para(align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            self.inline.write(p, text)

    def list_item(self, level: int, ordered: bool, marker: str, text: str) -> None:
        if ordered:
            p = self.para(align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            indent = 0.35 + 0.35 * level
            pf = p.paragraph_format
            pf.left_indent = Inches(indent)
            pf.first_line_indent = Inches(-0.3)
            pf.space_after = Pt(3)
            pf.tab_stops.add_tab_stop(Inches(indent))
            p.add_run(f"{marker}\t")
        else:
            p = self.para("List Bullet" if level == 0 else "List Bullet 2", align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        self.inline.write(p, text)

    def table(self, rows: list[list[str]]) -> None:
        ncols = max(len(r) for r in rows)
        size = 10 if ncols <= 6 else (9 if ncols <= 8 else 8)
        cap = self.pending_table_caption
        self.pending_table_caption = None
        if cap:
            tid, text = cap
            p = self.para("Caption Text")
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_after = Pt(4)
            self.caption_runs(p, "Table", self.num.tabs[tid], f"tab:{tid}", text)
        t = self.doc.add_table(rows=len(rows), cols=ncols)
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ri, row in enumerate(rows):
            for ci in range(ncols):
                cell = t.cell(ri, ci)
                p = cell.paragraphs[0]
                p.style = self.doc.styles["Table Text"]
                self.inline.write(p, row[ci] if ci < len(row) else "", size=size, bold=(ri == 0))
                if ri == 0:
                    shade_cell(cell, "D9D9D9")
        repeat_header(t.rows[0])
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)  # spacing after the table

    def caption_runs(self, p, label: str, number: str, key: str, text: str) -> None:
        """'Fig. 3.1: text' -- chapter prefix as text, running number as a SEQ field."""
        prefix, running = number.rsplit(".", 1)
        p.add_run(f"{'Fig.' if label == 'Fig' else 'Table'} {prefix}.")
        seq = f"SEQ {label} \\* ARABIC" + (" \\r 1" if key in self.num.first_in_chapter else "")
        add_field(p, seq, running)
        p.add_run(": ")
        self.inline.write(p, text, emphasis=False)

    def figure(self, fid: str, fname: str, caption: str) -> None:
        path = FIG_DIR / fname
        if not path.exists():
            raise SystemExit(f"Figure file missing: {path}")
        with Image.open(path) as im:
            w_px, h_px = im.size
        width = TEXT_W_IN * 0.98
        if width * h_px / w_px > 7.2:
            width = 7.2 * w_px / h_px
        p = self.para(align=WD_ALIGN_PARAGRAPH.CENTER)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(6)
        p.add_run().add_picture(str(path), width=Inches(width))
        c = self.para("Caption Text")
        self.caption_runs(c, "Fig", self.num.figs[fid], f"fig:{fid}", caption)

    def equation(self, label: str, plain: str) -> None:
        spec = equations.EQUATIONS.get(label, {}).get("spec")
        if spec != plain:
            raise SystemExit(f"[[EQ:{label}]] text differs from equations.py/SPEC: {plain!r} vs {spec!r}")
        path = self.eq_paths[label]
        with Image.open(path) as im:
            w_px, _ = im.size
        width = min(w_px / equations.DPI, TEXT_W_IN - 0.8)
        p = self.para("Equation")
        p.add_run("\t")
        p.add_run().add_picture(str(path), width=Inches(width))
        p.add_run(f"\t({self.num.eqs[label]})")

    def code(self, rel_path: str) -> None:
        src = (REPO_DIR / rel_path).read_text(encoding="utf-8").expandtabs(4).rstrip("\n").split("\n")
        p = self.para("Code Listing")
        for k, line in enumerate(src):
            r = p.add_run(line)
            if k < len(src) - 1:
                r.add_break(WD_BREAK.LINE)

    def logo(self) -> None:
        p = self.para(align=WD_ALIGN_PARAGRAPH.CENTER)
        if LOGO_PATH.exists():
            p.add_run().add_picture(str(LOGO_PATH), width=Inches(1.6))
        else:
            self.inline.write(p, "[[PH: insert NMIMS logo]]")

    def signatures(self, labels: list[str]) -> None:
        t = self.doc.add_table(rows=1, cols=len(labels))
        no_borders(t)
        for cell, label in zip(t.rows[0].cells, labels):
            parts = [x.strip() for x in re.split(r"(?=\()", label) if x.strip()]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(36)
            p.add_run("____________________")
            for part in parts:
                q = cell.add_paragraph()
                q.paragraph_format.space_after = Pt(0)
                q.paragraph_format.line_spacing = 1.0
                q.add_run(part).font.size = Pt(11)
        self.doc.add_paragraph()

    def toc_field(self, instr: str, hint: str) -> None:
        p = self.para()
        add_field(p, instr, hint)

    def section_break(self) -> None:
        self.sections_seen += 1
        if self.sections_seen == 1:
            return  # the cover is the first section; nothing to break
        self.doc.add_section(WD_SECTION.NEW_PAGE)
        self.after_section_break = True
        self.pending_break = False

    def references(self) -> None:
        p = self.para("Heading 1")
        p.add_run("References")
        for key, n in sorted(self.num.refs.items(), key=lambda kv: kv[1]):
            q = self.para(align=WD_ALIGN_PARAGRAPH.LEFT)
            pf = q.paragraph_format
            pf.left_indent = Inches(0.5)
            pf.first_line_indent = Inches(-0.5)
            pf.tab_stops.add_tab_stop(Inches(0.5))
            q.add_run(f"[{n}]\t")
            self.inline.write(q, self.num.ref_text[key])

    # ---- page setup, header, footer ------------------------------------------
    def finish_sections(self) -> None:
        secs = self.doc.sections
        for s in secs:
            s.page_width, s.page_height = PAGE_W, PAGE_H
            s.left_margin = MARGIN_L
            s.right_margin = s.top_margin = s.bottom_margin = MARGIN_OTHER
            s.header_distance = s.footer_distance = Inches(0.5)
        if len(secs) != 3:
            raise SystemExit(f"Expected 3 sections (cover, front matter, main), found {len(secs)}")
        cover, front, main = secs
        # Cover/certificate: no header, no page number (first section has its own empty parts).
        cover.header.is_linked_to_previous = False
        cover.footer.is_linked_to_previous = False
        # Front matter: header + footer defined here; the main body inherits them.
        front.header.is_linked_to_previous = False
        front.footer.is_linked_to_previous = False
        self._header(front.header)
        self._footer(front.footer)
        main.header.is_linked_to_previous = True
        main.footer.is_linked_to_previous = True
        set_page_numbering(front, "lowerRoman", 1)
        set_page_numbering(main, "decimal", 1)

    def _header(self, header) -> None:
        for p in header.paragraphs:
            p.text = ""
        t = header.add_table(rows=1, cols=2, width=Inches(TEXT_W_IN))
        no_borders(t)
        left, right = t.rows[0].cells
        left.width, right.width = Inches(TEXT_W_IN - 1.6), Inches(1.6)
        lp = left.paragraphs[0]
        lp.style = self.doc.styles["Header Text"]
        lp.add_run(TITLE)
        rp = right.paragraphs[0]
        rp.style = self.doc.styles["Header Text"]
        rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        self.inline.write(rp, f"[[PH: {YEAR_PLACEHOLDER}]]", size=9)

    def _footer(self, footer) -> None:
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_field(p, "PAGE", "1")

    # ---- driver ---------------------------------------------------------------
    def render(self, parsed: dict[str, list[tuple]]) -> None:
        self.eq_paths = equations.render_all()
        for fname in FILES:
            if fname == "references.md":
                self.references()
                continue
            for b in parsed[fname]:
                kind = b[0]
                if kind == "section":
                    self.section_break()
                elif kind == "pagebreak":
                    self.pending_break = True
                elif kind in ("intro", "summary"):
                    continue
                elif kind == "h":
                    self.heading(b[1], b[2])
                elif kind == "p":
                    self.paragraph(b[1], b[2])
                elif kind == "li":
                    self.list_item(b[1], b[2], b[3], b[4])
                elif kind == "tabcap":
                    self.pending_table_caption = (b[1], b[2])
                elif kind == "table":
                    self.table(b[1])
                elif kind == "fig":
                    self.figure(b[1], b[2], b[3])
                elif kind == "eq":
                    self.equation(b[1], b[2])
                elif kind == "code":
                    self.code(b[1])
                elif kind == "logo":
                    self.logo()
                elif kind == "sig":
                    self.signatures(b[1])
                elif kind == "toc":
                    self.toc_field('TOC \\o "1-3" \\h \\z \\u',
                                   "Right-click here and choose Update Field to build the table of contents.")
                elif kind == "lof":
                    self.toc_field('TOC \\h \\z \\c "Fig"',
                                   "Right-click here and choose Update Field to build the list of figures.")
                elif kind == "lot":
                    self.toc_field('TOC \\h \\z \\c "Table"',
                                   "Right-click here and choose Update Field to build the list of tables.")
                else:
                    raise SystemExit(f"Unknown block {kind} in {fname}")
            if self.pending_table_caption:
                raise SystemExit(f"{fname}: table caption without a table")
        self.finish_sections()
        set_update_fields_on_open(self.doc)


def main() -> None:
    bad = equations.check_against_spec()
    if bad:
        raise SystemExit(f"Equations not verbatim in docs/SPEC.md: {bad}")
    texts = {f: (CHAPTER_DIR / f).read_text(encoding="utf-8") for f in FILES}
    parsed = {f: parse_blocks(t) for f, t in texts.items() if f != "references.md"}
    num = number_everything(parsed, texts)
    diagrams.render_all()
    builder = ReportBuilder(num)
    builder.render(parsed)
    builder.doc.save(OUT_PATH)
    manifest = {
        "figures": {k: {"number": v, "caption": num.captions[f"fig:{k}"]} for k, v in num.figs.items()},
        "tables": {k: {"number": v, "caption": num.captions[f"tab:{k}"]} for k, v in num.tabs.items()},
        "equations": num.eqs,
        "references": num.refs,
        "placeholders_written": builder.inline.placeholders,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(num.figs)} figures, {len(num.tabs)} tables, {len(num.eqs)} equations, "
          f"{len(num.refs)} references, {builder.inline.placeholders} placeholders)")


if __name__ == "__main__":
    main()
