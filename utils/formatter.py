"""
Formatting utilities for LegalEase.
Converts sanitised document text into TXT, DOCX, and PDF byte buffers
ready for download or storage.
"""
import io
import re
from typing import Optional

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

from utils.sanitizer import sanitize_text


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

def format_txt(text: str) -> bytes:
    """
    Return the document text as UTF-8 encoded bytes suitable for a .txt file.

    Args:
        text: Raw document text.

    Returns:
        UTF-8 encoded bytes.
    """
    clean = sanitize_text(text)
    return clean.encode("utf-8")


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def _is_numbered_heading(line: str) -> bool:
    """Return True if the line starts with a numeric clause identifier."""
    return bool(re.match(r"^\d+(\.\d+)*[\.\)]\s+\S", line))


def format_docx(text: str, title: Optional[str] = "Legal Document") -> bytes:
    """
    Convert document text into a professionally formatted DOCX file.

    Heuristics:
      - First non-empty line -> document title (centred, bold, large font).
      - Lines that look like numbered headings (e.g. "1." or "1.1") -> Heading 2.
      - All-uppercase short lines -> Heading 3 (section labels).
      - Everything else -> Body text paragraph.

    Args:
        text: The sanitised document text.
        title: Fallback document title if the first line is empty.

    Returns:
        DOCX file contents as bytes.
    """
    clean = sanitize_text(text)
    lines = clean.splitlines()

    doc = Document()

    # ---- Page margins ----
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.25)

    # ---- Default paragraph style ----
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(11)

    first_line_used = False

    for line in lines:
        stripped = line.strip()

        # Skip completely blank lines — add spacing instead
        if not stripped:
            doc.add_paragraph("")
            continue

        # First non-blank line -> Title
        if not first_line_used:
            heading = doc.add_heading(stripped, level=0)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if heading.runs:
                run = heading.runs[0]
            else:
                run = heading.add_run(stripped)
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x5E)  # dark navy
            first_line_used = True
            continue

        # Numbered clause heading: starts with digit(s) followed by dot
        if _is_numbered_heading(stripped):
            h = doc.add_heading(stripped, level=2)
            if h.runs:
                h.runs[0].font.size = Pt(12)
                h.runs[0].font.bold = True
            continue

        # All-caps section label (short line, <= 60 chars)
        if stripped.isupper() and len(stripped) <= 60:
            h = doc.add_heading(stripped, level=3)
            if h.runs:
                h.runs[0].font.size = Pt(11)
            continue

        # Bullet-style lines
        if stripped.startswith(("*", "-")) and len(stripped) > 2:
            p = doc.add_paragraph(stripped[1:].strip(), style="List Bullet")
            if p.runs:
                p.runs[0].font.size = Pt(11)
            continue

        # Default body paragraph
        p = doc.add_paragraph(stripped)
        p.paragraph_format.space_after = Pt(4)
        if p.runs:
            p.runs[0].font.size = Pt(11)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

class _LegalPDF(FPDF):
    """Custom FPDF subclass with header and footer."""

    def __init__(self, doc_title: str = "Legal Document", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = doc_title

    def header(self) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, self.doc_title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Page {self.page_no()} | Confidential", align="C")


def format_pdf(text: str, title: Optional[str] = "Legal Document") -> bytes:
    """
    Convert document text into a PDF file using FPDF2.

    Args:
        text: The sanitised document text.
        title: Document title shown in the PDF header.

    Returns:
        PDF file contents as bytes.
    """
    clean = sanitize_text(text)
    lines = clean.splitlines()

    pdf = _LegalPDF(doc_title=title or "Legal Document")
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    first_line_used = False

    for line in lines:
        stripped = line.strip()

        # Blank line -> small vertical gap
        if not stripped:
            pdf.ln(3)
            continue

        # First non-blank line -> Title
        if not first_line_used:
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(26, 26, 94)  # dark navy
            pdf.multi_cell(0, 10, stripped, align="C")
            pdf.ln(4)
            pdf.set_text_color(0, 0, 0)
            first_line_used = True
            continue

        # Numbered clause heading
        if _is_numbered_heading(stripped):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, stripped, align="L")
            pdf.ln(1)
            pdf.set_font("Helvetica", "", 10)
            continue

        # ALL-CAPS section label
        if stripped.isupper() and len(stripped) <= 60:
            pdf.set_font("Helvetica", "BI", 10)
            pdf.multi_cell(0, 7, stripped, align="L")
            pdf.ln(1)
            pdf.set_font("Helvetica", "", 10)
            continue

        # Bullet items
        if stripped.startswith(("*", "-")) and len(stripped) > 2:
            bullet_text = "  " + stripped[1:].strip()
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, bullet_text, align="L")
            pdf.ln(1)
            continue

        # Body text
        pdf.set_font("Helvetica", "", 10)
        # Encode to latin-1 safe string to avoid FPDF encoding issues
        safe = stripped.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe, align="J")
        pdf.ln(1)

    return bytes(pdf.output())
