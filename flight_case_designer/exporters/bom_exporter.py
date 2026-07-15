# SPDX-License-Identifier: GPL-3.0-or-later
"""
Bill of Materials and cut-list exporter.

Exports the following files:
    <name>_cut_list.csv    – all plywood panels (W × D × thickness, label, qty)
    <name>_profile_list.csv– all aluminium extrusion cuts (type, length)
    <name>_hardware_bom.csv– all hardware items (name, part number, qty, weight)
    <name>_bom_summary.csv – combined BOM with material areas, weights and
                             optional cost estimate

All dimensions in the CSV files are in millimetres.
"""

from __future__ import annotations

import csv
import math
import os
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

if TYPE_CHECKING:
    from ..generators.case_builder import CaseDimensions
    from ..properties import FCD_SceneProperties


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _m2mm(metres: float) -> float:
    return round(metres * 1000.0, 2)


def _mm2(w_m: float, d_m: float) -> float:
    """Return area in mm²."""
    return round(w_m * 1000.0 * d_m * 1000.0, 2)


def _safe_path(base_dir: str, filename: str) -> str:
    """Resolve Blender-relative path and join filename."""
    import bpy
    abs_dir = bpy.path.abspath(base_dir)
    os.makedirs(abs_dir, exist_ok=True)
    return os.path.join(abs_dir, filename)


# ---------------------------------------------------------------------------
# Panel cut list
# ---------------------------------------------------------------------------

def _collect_panels(dims: "CaseDimensions") -> List[Dict[str, Any]]:
    """Return a list of panel dicts for the cut list."""
    t   = dims.ply_t
    w   = dims.ext_w
    d   = dims.ext_d
    h   = dims.ext_h
    bh  = dims.body_h
    lh  = dims.lid_h
    has_lid = dims.case_type not in ("CUSTOM_BOX",)
    fb_h_body = bh - t
    fb_h_lid  = lh - t
    side_w    = d - 2 * t

    panels = [
        {"label": "Bottom Panel",      "width": w,       "depth": d,       "thickness": t, "qty": 1},
        {"label": "Top Panel",         "width": w,       "depth": d,       "thickness": t, "qty": 1},
    ]

    if has_lid:
        panels += [
            {"label": "Body Front Panel", "width": w,       "depth": t,       "thickness": fb_h_body, "qty": 1},
            {"label": "Body Back Panel",  "width": w,       "depth": t,       "thickness": fb_h_body, "qty": 1},
            {"label": "Body Side Panel",  "width": t,       "depth": side_w,  "thickness": fb_h_body, "qty": 2},
            {"label": "Lid Front Panel",  "width": w,       "depth": t,       "thickness": fb_h_lid,  "qty": 1},
            {"label": "Lid Back Panel",   "width": w,       "depth": t,       "thickness": fb_h_lid,  "qty": 1},
            {"label": "Lid Side Panel",   "width": t,       "depth": side_w,  "thickness": fb_h_lid,  "qty": 2},
        ]
    else:
        fb_h = h - 2 * t
        panels += [
            {"label": "Front Panel",  "width": w,      "depth": t,      "thickness": fb_h, "qty": 1},
            {"label": "Back Panel",   "width": w,      "depth": t,      "thickness": fb_h, "qty": 1},
            {"label": "Side Panel",   "width": t,      "depth": side_w, "thickness": fb_h, "qty": 2},
        ]

    # convert metres to mm
    for p in panels:
        p["width_mm"]     = _m2mm(p.pop("width"))
        p["depth_mm"]     = _m2mm(p.pop("depth"))
        p["thickness_mm"] = _m2mm(p.pop("thickness"))
        p["area_mm2"]     = round(p["width_mm"] * p["depth_mm"], 2)

    return panels


# ---------------------------------------------------------------------------
# Profile cut list
# ---------------------------------------------------------------------------

def _collect_profiles(dims: "CaseDimensions") -> List[Dict[str, Any]]:
    """Return a list of profile cut dicts."""
    w, d, h = dims.ext_w, dims.ext_d, dims.ext_h
    sz      = dims.split_z
    ti      = dims.prof_t   # inset

    has_seam = dims.case_type not in ("CUSTOM_BOX",)

    horizontal_lengths = {
        "Front / Back edge":  w - 2 * ti,
        "Left / Right edge":  d - 2 * ti,
    }
    vertical_body_h = dims.body_h if has_seam else h
    vertical_lid_h  = dims.lid_h  if has_seam else 0.0

    profiles: List[Dict[str, Any]] = []

    def add(label, length_m, qty):
        profiles.append({
            "label":      label,
            "length_mm":  _m2mm(length_m),
            "qty":        qty,
            "profile":    dims.profile_type,
        })

    # Bottom ring
    add("Bottom Front/Back Extrusion", w - 2 * ti, 2)
    add("Bottom Left/Right Extrusion", d - 2 * ti, 2)
    # Top ring
    add("Top Front/Back Extrusion",    w - 2 * ti, 2)
    add("Top Left/Right Extrusion",    d - 2 * ti, 2)
    # Vertical – body
    add("Vertical Body Extrusion",     vertical_body_h, 4)
    if has_seam and vertical_lid_h > 0:
        add("Vertical Lid Extrusion",  vertical_lid_h,  4)
        # Seam ring
        add("Seam Front/Back Extrusion", w - 2 * ti, 2)
        add("Seam Left/Right Extrusion", d - 2 * ti, 2)

    return profiles


# ---------------------------------------------------------------------------
# Hardware BOM
# ---------------------------------------------------------------------------

def _collect_hardware(props: "FCD_SceneProperties", dims: "CaseDimensions") -> List[Dict[str, Any]]:
    """Return the hardware item list."""
    from ..libraries.hardware_data import get_hardware_def

    hdw = props.hardware
    case = props.case
    items: List[Dict[str, Any]] = []

    has_lid  = case.case_type not in ("CUSTOM_BOX",)
    hinged   = case.case_type == "HINGED_LID"
    is_rack  = case.case_type == "RACK_CASE"

    def add_item(hw_id: str, qty: int) -> None:
        defn = get_hardware_def(hw_id)
        if defn and qty > 0:
            items.append({
                "name":         defn["name"],
                "manufacturer": defn["manufacturer"],
                "part_number":  defn["part_number"],
                "qty":          qty,
                "unit_weight_g":defn["weight_g"],
                "total_weight_g":defn["weight_g"] * qty,
                "notes":        defn["notes"],
            })
        elif defn is None and qty > 0:
            items.append({
                "name":         hw_id,
                "manufacturer": "–",
                "part_number":  "–",
                "qty":          qty,
                "unit_weight_g": 0,
                "total_weight_g": 0,
                "notes":        "",
            })

    # Latches
    if hdw.latch_type == "BUTTERFLY":
        n = hdw.latch_count or dims.auto_latch_count()
        add_item("butterfly_medium", n)
    elif hdw.latch_type == "DRAW":
        n = hdw.latch_count or dims.auto_latch_count()
        add_item("draw_latch", n)

    # Handles
    if hdw.handle_type == "SPRING":
        nc = hdw.handle_count or dims.auto_handle_count()
        add_item("spring_handle_small", nc * 2)  # × 2 sides
    elif hdw.handle_type == "SIDE":
        nc = hdw.handle_count or dims.auto_handle_count()
        add_item("side_handle", nc * 2)

    # Corners
    if case.corner_type == "BALL":
        add_item("ball_corner", 8)
    elif case.corner_type == "CAST":
        add_item("cast_corner", 8)

    # Feet / casters
    if hdw.feet_type == "RUBBER":
        add_item("rubber_foot", 4)
    elif hdw.feet_type == "CASTERS":
        add_item("caster_50mm", 4)

    # Hinges
    if hinged:
        add_item("lid_hinge", hdw.hinge_count)

    # Stacking cups
    if hdw.stacking_cups:
        add_item("stacking_cup", 4)

    # Label holder
    if hdw.label_holder:
        add_item("label_holder", 1)

    # Rack rails
    if is_rack:
        add_item("rack_rail_4u", 2)

    return items


# ---------------------------------------------------------------------------
# Cost estimate helpers
# ---------------------------------------------------------------------------

def _panel_area_sqm(panels: List[Dict[str, Any]]) -> float:
    total = 0.0
    for p in panels:
        total += p["area_mm2"] * p["qty"] / 1_000_000.0
    return total


def _profile_total_m(profiles: List[Dict[str, Any]]) -> float:
    total = 0.0
    for p in profiles:
        total += p["length_mm"] * p["qty"] / 1000.0
    return total


# ---------------------------------------------------------------------------
# Public exporter
# ---------------------------------------------------------------------------

def export_manufacturing_files(
    props: "FCD_SceneProperties",
    dims:  "CaseDimensions",
) -> List[str]:
    """
    Write all manufacturing output CSV files.

    Returns a list of absolute file paths that were written.
    """
    mfg      = props.manufacturing
    base_dir = mfg.export_path
    name     = props.case.case_name.replace(" ", "_")

    written: List[str] = []

    panels   = _collect_panels(dims)
    profiles = _collect_profiles(dims)
    hardware = _collect_hardware(props, dims)

    # ------------------------------------------------------------------
    # 1. Panel cut list
    # ------------------------------------------------------------------
    path = _safe_path(base_dir, f"{name}_cut_list.csv")
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["label", "width_mm", "depth_mm", "thickness_mm", "area_mm2", "qty"],
        )
        writer.writeheader()
        writer.writerows(panels)
    written.append(path)

    # ------------------------------------------------------------------
    # 2. Profile cut list
    # ------------------------------------------------------------------
    path = _safe_path(base_dir, f"{name}_profile_list.csv")
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["label", "profile", "length_mm", "qty"])
        writer.writeheader()
        writer.writerows(profiles)
    written.append(path)

    # ------------------------------------------------------------------
    # 3. Hardware BOM
    # ------------------------------------------------------------------
    path = _safe_path(base_dir, f"{name}_hardware_bom.csv")
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "name", "manufacturer", "part_number",
                "qty", "unit_weight_g", "total_weight_g", "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(hardware)
    written.append(path)

    # ------------------------------------------------------------------
    # 4. Summary BOM
    # ------------------------------------------------------------------
    path = _safe_path(base_dir, f"{name}_bom_summary.csv")
    panel_area     = _panel_area_sqm(panels)
    profile_metres = _profile_total_m(profiles)
    hw_weight_kg   = sum(h["total_weight_g"] for h in hardware) / 1000.0
    ply_weight_kg  = dims.ply_weight
    total_weight   = dims.total_weight()

    summary_rows = [
        {"item": "Plywood",        "quantity": f"{panel_area:.3f} m²",  "weight_kg": f"{ply_weight_kg:.2f}",   "cost": ""},
        {"item": "Al Profiles",    "quantity": f"{profile_metres:.2f} m","weight_kg": "–",                      "cost": ""},
        {"item": "Hardware",       "quantity": f"{len(hardware)} types", "weight_kg": f"{hw_weight_kg:.2f}",    "cost": ""},
        {"item": "Equipment",      "quantity": "1",                      "weight_kg": f"{dims.eq_weight:.1f}",  "cost": ""},
        {"item": "TOTAL",          "quantity": "–",                      "weight_kg": f"{total_weight:.2f}",    "cost": ""},
    ]

    if mfg.include_cost_estimate:
        costs = {
            "Plywood":   panel_area     * mfg.ply_cost_per_sqm,
            "Al Profiles": profile_metres * mfg.profile_cost_per_m,
            "Hardware":  hw_weight_kg   * 30.0 * (1 + mfg.hardware_markup / 100.0),  # rough
            "Equipment": 0.0,
        }
        total_cost = sum(costs.values())
        for row in summary_rows:
            item = row["item"]
            row["cost"] = f"£{costs.get(item, 0.0):.2f}" if item in costs else f"£{total_cost:.2f}"

    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["item", "quantity", "weight_kg", "cost"])
        writer.writeheader()
        writer.writerows(summary_rows)
    written.append(path)

    return written
