"""Geometric calculations for sash window components."""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .models import Bars, Frame, Glass, Project, Sash, Window

# Constants based on manufacturing standards (in millimetres)
HORN_ALLOWANCE = 70
SASH_WIDTH_DEDUCTION = 178
JAMBS_DEDUCTION = 106
EXT_HEAD_LINER_DEDUCTION = 204
INT_HEAD_LINER_DEDUCTION = 170
GLASS_WIDTH_DEDUCTION = 90
GLASS_HEIGHT_DEDUCTION = 76


def calculate_frame(width: float, height: float) -> Frame:
    """Calculate the primary frame dimensions."""

    jambs_length = height - JAMBS_DEDUCTION
    head_length = width
    cill_length = width
    ext_head_liner = width - EXT_HEAD_LINER_DEDUCTION
    int_head_liner = width - INT_HEAD_LINER_DEDUCTION

    return Frame(
        width=width,
        height=height,
        jambs_length=jambs_length,
        head_length=head_length,
        cill_length=cill_length,
        ext_head_liner=ext_head_liner,
        int_head_liner=int_head_liner,
    )


def calculate_sash(frame_width: float, sash_height: float, include_horn: bool = False) -> Sash:
    """Calculate sash dimensions derived from the frame size."""

    sash_width = frame_width - SASH_WIDTH_DEDUCTION
    stiles_length = sash_height
    top_rail_length = sash_width
    bottom_rail_length = sash_width
    meet_rail_length = sash_width
    height_with_horn = sash_height + (HORN_ALLOWANCE if include_horn else 0)

    return Sash(
        width=sash_width,
        height=sash_height,
        height_with_horn=height_with_horn,
        stiles_length=stiles_length,
        top_rail_length=top_rail_length,
        bottom_rail_length=bottom_rail_length,
        meet_rail_length=meet_rail_length,
    )


def calculate_glass(sash: Sash, glass_type: str, frosted: bool, toughened: bool,
                    spacer_color: str, pcs: int) -> Glass:
    """Calculate glass panel dimensions relative to the sash."""

    glass_width = sash.width - GLASS_WIDTH_DEDUCTION
    glass_height = sash.height - GLASS_HEIGHT_DEDUCTION

    return Glass(
        width=glass_width,
        height=glass_height,
        type=glass_type,
        frosted=frosted,
        toughened=toughened,
        spacer_color=spacer_color,
        pcs=pcs,
    )


def calculate_bars(sash: Sash, layout_type: str, vertical_bars: int, horizontal_bars: int) -> Bars:
    """Calculate the spacing between glazing bars."""

    spacing_vertical: List[float] = []
    spacing_horizontal: List[float] = []

    if vertical_bars > 0:
        spacing = sash.width / (vertical_bars + 1)
        spacing_vertical = [round(spacing, 2)] * vertical_bars

    if horizontal_bars > 0:
        spacing = sash.height / (horizontal_bars + 1)
        spacing_horizontal = [round(spacing, 2)] * horizontal_bars

    return Bars(
        layout_type=layout_type,
        vertical_bars=vertical_bars,
        horizontal_bars=horizontal_bars,
        spacing_vertical=spacing_vertical,
        spacing_horizontal=spacing_horizontal,
    )


def assemble_window(
    window_id: str,
    name: str,
    frame_width: float,
    frame_height: float,
    top_sash_height: float,
    bottom_sash_height: float,
    paint_color: str,
    hardware_finish: str,
    trickle_vent: str,
    sash_catches: str,
    cill_extension: int,
    glass_type: str,
    glass_frosted: bool,
    glass_toughened: bool,
    spacer_color: str,
    glass_pcs: int,
    bars_layout: str,
    bars_vertical: int,
    bars_horizontal: int,
) -> Window:
    """Generate a :class:`Window` with all calculated elements."""

    frame = calculate_frame(frame_width, frame_height)
    sash_top = calculate_sash(frame_width, top_sash_height, include_horn=True)
    sash_bottom = calculate_sash(frame_width, bottom_sash_height, include_horn=False)

    glass = calculate_glass(sash_bottom, glass_type, glass_frosted, glass_toughened, spacer_color, glass_pcs)
    bars = calculate_bars(sash_bottom, bars_layout, bars_vertical, bars_horizontal)

    return Window(
        id=window_id,
        name=name,
        frame=frame,
        sash_top=sash_top,
        sash_bottom=sash_bottom,
        glass=glass,
        bars=bars,
        paint_color=paint_color,
        hardware_finish=hardware_finish,
        trickle_vent=trickle_vent,
        sash_catches=sash_catches,
        cill_extension=cill_extension,
    )


def window_to_dict(window: Window) -> Dict[str, Dict]:
    """Serialize a :class:`Window` into nested dictionaries for export."""

    return {
        "id": window.id,
        "name": window.name,
        "paint_color": window.paint_color,
        "hardware_finish": window.hardware_finish,
        "trickle_vent": window.trickle_vent,
        "sash_catches": window.sash_catches,
        "cill_extension": window.cill_extension,
        "frame": asdict(window.frame),
        "sash_top": asdict(window.sash_top),
        "sash_bottom": asdict(window.sash_bottom),
        "glass": asdict(window.glass),
        "bars": asdict(window.bars),
    }


def calculate_materials(window: Window, wood_type: str = "Sapele") -> List[Dict[str, object]]:
    """Generate a cutting list for the provided window."""

    frame = window.frame
    sash_top = window.sash_top
    sash_bottom = window.sash_bottom

    materials = [
        {"material_type": "Frame", "section": "Jamb", "length": round(frame.jambs_length, 2), "qty": 2, "wood_type": wood_type},
        {"material_type": "Frame", "section": "Head", "length": round(frame.head_length, 2), "qty": 1, "wood_type": wood_type},
        {"material_type": "Frame", "section": "Cill", "length": round(frame.cill_length, 2), "qty": 1, "wood_type": wood_type},
        {"material_type": "Top Sash", "section": "Stile", "length": round(sash_top.stiles_length, 2), "qty": 2, "wood_type": wood_type},
        {"material_type": "Top Sash", "section": "Top Rail", "length": round(sash_top.top_rail_length, 2), "qty": 1, "wood_type": wood_type},
        {"material_type": "Top Sash", "section": "Bottom Rail", "length": round(sash_top.bottom_rail_length, 2), "qty": 1, "wood_type": wood_type},
        {"material_type": "Bottom Sash", "section": "Stile", "length": round(sash_bottom.stiles_length, 2), "qty": 2, "wood_type": wood_type},
        {"material_type": "Bottom Sash", "section": "Top Rail", "length": round(sash_bottom.top_rail_length, 2), "qty": 1, "wood_type": wood_type},
        {"material_type": "Bottom Sash", "section": "Bottom Rail", "length": round(sash_bottom.bottom_rail_length, 2), "qty": 1, "wood_type": wood_type},
    ]

    return materials


def prepare_window_export(window: Window) -> Dict[str, object]:
    """Prepare a dictionary containing window data, materials and hardware summary."""

    materials = calculate_materials(window)
    total_timber = sum(item["length"] * item["qty"] for item in materials)

    return {
        "window": window_to_dict(window),
        "materials": materials,
        "glass": asdict(window.glass),
        "bars": asdict(window.bars),
        "hardware": {
            "paint_color": window.paint_color,
            "hardware_finish": window.hardware_finish,
            "trickle_vent": window.trickle_vent,
            "sash_catches": window.sash_catches,
        },
        "totals": {
            "timber_length": round(total_timber, 2),
            "glass_area": round(window.glass.width * window.glass.height * window.glass.pcs / 1_000_000, 3),
        },
    }


def prepare_project_export(project: Project) -> Dict[str, object]:
    """Prepare full project export data for downstream modules."""

    windows_data = [prepare_window_export(window) for window in project.windows]

    summary = {
        "total_timber": round(sum(item["totals"]["timber_length"] for item in windows_data), 2),
        "total_glass_area": round(sum(item["totals"]["glass_area"] for item in windows_data), 3),
        "window_count": len(project.windows),
    }

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "client_name": project.client_name,
            "created_at": project.created_at,
        },
        "windows": windows_data,
        "summary": summary,
    }
