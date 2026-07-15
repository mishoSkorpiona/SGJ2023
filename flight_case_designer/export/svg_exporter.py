"""
export/svg_exporter.py — Export panel cut shapes as SVG.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def export(filepath: str, data: "CaseData") -> None:
    """Export panel outlines to an SVG file."""
    x_cursor = 0.0
    gap = 10.0
    margin = 20.0
    max_h = max((p["height_mm"] for p in data.panels), default=100.0)
    total_w = sum(p["width_mm"] + gap for p in data.panels) + margin * 2

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_w}mm" height="{max_h + margin * 2}mm" '
        f'viewBox="0 0 {total_w} {max_h + margin * 2}">',
        '<g transform="translate(20,20)" stroke="black" stroke-width="0.5" fill="none">',
    ]

    for panel in data.panels:
        w = panel["width_mm"]
        h = panel["height_mm"]
        lines.append(
            f'<rect x="{x_cursor:.2f}" y="0" width="{w:.2f}" height="{h:.2f}"/>'
        )
        lines.append(
            f'<text x="{x_cursor + 2:.2f}" y="{h + 8:.2f}" '
            f'font-size="4" fill="black">{panel["name"]}</text>'
        )
        x_cursor += w + gap

    lines += ["</g>", "</svg>"]

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"SVG exported to {filepath}")
