"""
export/csv_exporter.py — Export BOM and cut list as CSV.
"""

from __future__ import annotations

import csv
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.case_manager import CaseData


def export(filepath: str, data: "CaseData") -> None:
    """
    Export to *filepath*.
    Three CSV files are written:
      {base}_panels.csv
      {base}_hardware.csv
      {base}_profiles.csv
    """
    base, _ = os.path.splitext(filepath)

    # Panels
    with open(f"{base}_panels.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "width_mm", "height_mm", "thickness_mm",
                            "material", "qty"]
        )
        writer.writeheader()
        writer.writerows(data.panels)

    # Hardware
    with open(f"{base}_hardware.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "count", "part_number", "manufacturer"]
        )
        writer.writeheader()
        writer.writerows(data.hardware_items)

    # Profiles
    with open(f"{base}_profiles.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "profile_type", "length_mm", "qty"]
        )
        writer.writeheader()
        writer.writerows(data.profile_cuts)

    print(f"CSV files exported to {base}_*.csv")
