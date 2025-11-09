"""Calculation endpoints for the sash window web backend."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import CalculationRequest
from app.api.utils import normalize_scene, serialize_renderer
from app.core.calculations import calculate_materials, prepare_project_export
from app.core.models import Project
from app.graphics.renderer import WindowRenderer
from app.graphics.scene import build_scene

router = APIRouter(tags=["calculations"])


@router.post("/calculate", summary="Calculate sash window dimensions and materials")
def calculate_windows(payload: CalculationRequest) -> Dict[str, Any]:
    """Run full calculation workflow and return render-ready data."""

    try:
        project: Project = payload.to_project()
    except ValueError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    export_data = prepare_project_export(project)

    response_windows: List[Dict[str, Any]] = []
    for window_config, window, window_payload in zip(payload.windows, project.windows, export_data["windows"]):
        if window_config.wood_type:
            materials = calculate_materials(window, wood_type=window_config.wood_type)
            window_payload["materials"] = materials
            window_payload["totals"]["timber_length"] = round(
                sum(item["length"] * item["qty"] for item in materials),
                2,
            )
        scene = build_scene(window)
        renderer = WindowRenderer(window)
        renderer_payload = serialize_renderer(renderer)
        response_windows.append(
            {
                "id": window.id,
                "name": window.name,
                "wood_type": window_config.wood_type,
                "export": window_payload,
                "scene": normalize_scene(scene),
                "renderer": renderer_payload,
            }
        )

    return {
        "project": export_data["project"],
        "summary": export_data["summary"],
        "windows": response_windows,
    }
