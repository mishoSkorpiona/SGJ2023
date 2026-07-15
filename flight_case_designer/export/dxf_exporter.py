"""
export/dxf_exporter.py — Export case panels and profiles as DXF drawings.

Requires ``ezdxf`` to be installed in Blender's Python environment.
Each panel is exported as a flat rectangle in model space.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def export(filepath: str, data: "CaseData") -> None:
    """Export panel cut shapes to a DXF file at *filepath*."""
    try:
        import ezdxf
    except ImportError:
        raise ImportError(
            "ezdxf is required for DXF export. "
            "Install it via: pip install ezdxf"
        )

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Lay panels out in a row with 10 mm gaps
    x_cursor = 0.0
    gap = 10.0

    for panel in data.panels:
        w = panel["width_mm"]
        h = panel["height_mm"]
        # Rectangle
        msp.add_lwpolyline(
            [(x_cursor, 0), (x_cursor + w, 0),
             (x_cursor + w, h), (x_cursor, h)],
            close=True,
        )
        # Label
        msp.add_text(
            panel["name"],
            dxfattribs={"height": 5, "insert": (x_cursor + 2, h + 5)},
        )
        x_cursor += w + gap

    doc.saveas(filepath)
    print(f"DXF exported to {filepath}")
