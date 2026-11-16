"""
pdf_utils.py - export a generated research proposal to a formatted PDF (fpdf2, pure Python).
"""
from __future__ import annotations

from fpdf import FPDF

NAVY = (10, 14, 39)
PURPLE = (124, 92, 255)
BLUE = (0, 180, 255)
INK = (35, 40, 70)
MUTED = (120, 125, 155)

SECTION_TITLES = {
    "titles": "Research Title Options",
    "abstract": "Abstract",
    "keywords": "Keywords",
    "objectives": "Research Objectives",
    "future_enhancements": "Future Enhancements",
}

_REPLACE = {
    "‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
    "…": "...", "•": "-", " ": " ", "→": "->", "≥": ">=", "≤": "<=",
}


def _s(text) -> str:
    """fpdf core fonts are latin-1 only; make text safe."""
    text = str(text)
    for k, v in _REPLACE.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


class _PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "ResearchMate AI - Research Proposal", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _heading(pdf: _PDF, number: int, text: str):
    if pdf.get_y() > 255:
        pdf.add_page()
    pdf.ln(4)
    y = pdf.get_y()
    pdf.set_fill_color(*PURPLE)
    pdf.rect(pdf.l_margin, y, 1.6, 8, style="F")
    pdf.set_xy(pdf.l_margin + 4, y)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, _s(f"{number}. {text}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _body(pdf: _PDF, text: str, indent: float = 0):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(*INK)
    pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(0, 6, _s(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(entry: dict) -> bytes:
    """entry = {idea, domain, level, tech, created, result:{...}}"""
    res = entry["result"]
    pdf = _PDF(format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(True, margin=18)
    pdf.set_title(_s(res["titles"][0]))
    pdf.set_author("ResearchMate AI")
    pdf.add_page()

    # Banner
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 44, style="F")
    pdf.set_fill_color(*PURPLE)
    pdf.rect(0, 44, 140, 1.6, style="F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(140, 44, 70, 1.6, style="F")
    pdf.set_xy(20, 14)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "ResearchMate AI", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(20)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(190, 200, 255)
    pdf.cell(0, 7, "AI-generated research proposal", new_x="LMARGIN", new_y="NEXT")

    # Meta
    pdf.set_xy(20, 54)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*MUTED)
    meta = f"Domain: {entry.get('domain', '-')}   |   Level: {entry.get('level', '-')}   |   Generated: {entry.get('created', '-')}"
    pdf.cell(0, 6, _s(meta), new_x="LMARGIN", new_y="NEXT")
    if entry.get("tech"):
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, _s(f"Technology preferences: {entry['tech']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, _s(f"Project idea: {entry.get('idea', '')}"), new_x="LMARGIN", new_y="NEXT")

    # Sections
    _heading(pdf, 1, SECTION_TITLES["titles"])
    for i, t in enumerate(res["titles"], 1):
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*INK)
        pdf.multi_cell(0, 6, _s(f"Option {i}: {t}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    _heading(pdf, 2, SECTION_TITLES["abstract"])
    _body(pdf, res["abstract"])

    _heading(pdf, 3, SECTION_TITLES["keywords"])
    _body(pdf, "  |  ".join(res["keywords"]))

    _heading(pdf, 4, SECTION_TITLES["objectives"])
    for i, o in enumerate(res["objectives"], 1):
        _body(pdf, f"{i}. {o}")
        pdf.ln(1)

    _heading(pdf, 5, SECTION_TITLES["future_enhancements"])
    for i, e in enumerate(res["future_enhancements"], 1):
        _body(pdf, f"{i}. {e}")
        pdf.ln(1)

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(
        0, 5,
        "Generated locally with Ollama (Llama 3.2). Methods and outcomes are proposed, not completed results. "
        "Review and verify all content before academic use.",
        new_x="LMARGIN", new_y="NEXT",
    )
    return bytes(pdf.output())
