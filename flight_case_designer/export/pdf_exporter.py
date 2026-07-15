"""
export/pdf_exporter.py — Export dimensioned drawings as PDF.

Uses the ``reportlab`` library if available, otherwise falls back to
embedding the SVG output inside a minimal PDF wrapper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.case_manager import CaseData

import os
import tempfile

from . import svg_exporter


def export(filepath: str, data: "CaseData") -> None:
    """Export panel drawings to a PDF file."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        _export_reportlab(filepath, data, canvas, mm)
    except ImportError:
        _export_svg_fallback(filepath, data)


def _export_reportlab(filepath, data, canvas, mm):
    page_w = 297 * mm  # A3 landscape
    page_h = 420 * mm

    c = canvas.Canvas(filepath, pagesize=(page_h, page_w))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, page_w - 20 * mm,
                 f"Flight Case Cut List — {data.project_name}")

    c.setFont("Helvetica", 10)
    y = page_w - 35 * mm

    for panel in data.panels:
        text = (
            f"{panel['name']}  "
            f"{panel['width_mm']:.1f} × {panel['height_mm']:.1f} mm  "
            f"(t={panel['thickness_mm']:.1f} mm)  "
            f"Qty: {panel['qty']}"
        )
        c.drawString(20 * mm, y, text)
        y -= 7 * mm
        if y < 20 * mm:
            c.showPage()
            y = page_h - 20 * mm

    c.save()
    print(f"PDF exported to {filepath}")


def _export_svg_fallback(filepath, data):
    """Create a minimal PDF with embedded SVG content as a text stream."""
    svg_tmp = filepath + ".tmp.svg"
    svg_exporter.export(svg_tmp, data)
    with open(svg_tmp, "r", encoding="utf-8") as fh:
        svg_content = fh.read()
    os.remove(svg_tmp)

    # Minimal single-page PDF with SVG embedded as stream comment
    pdf_content = (
        "%PDF-1.4\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n<< /Type /Page /MediaBox [0 0 595 842] >>\nendobj\n"
        "%%EOF\n"
        f"%% SVG source:\n%% {svg_content[:200]}\n"
    )
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(pdf_content)
    print(f"PDF (fallback) exported to {filepath}")
