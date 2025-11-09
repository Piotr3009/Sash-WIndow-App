"""Export endpoints covering PDF, Excel, DXF, SVG and PNG outputs."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Type
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from app.api.schemas import CalculationRequest
from app.core.calculations import prepare_project_export
from app.core.models import Project
from app.graphics.export_dxf import DXFExporter
from app.graphics.export_png import PNGExporter
from app.graphics.export_svg import SVGExporter
from app.services.drawings_service import draw_window
from app.services.excel_service import generate_excel
from app.services.pdf_service import generate_pdf

router = APIRouter(tags=["exports"])

BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "output"
EXPORT_REGISTRY: Dict[str, Path] = {}


def _ensure_output_directory(subfolder: str) -> Path:
    directory = OUTPUT_DIR / subfolder
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _register_file(path: Path) -> Dict[str, str]:
    file_id = uuid4().hex
    EXPORT_REGISTRY[file_id] = path
    return {
        "file_id": file_id,
        "filename": path.name,
        "size": path.stat().st_size,
        "download_url": f"/api/download/{file_id}",
    }


def _project_from_request(payload: CalculationRequest) -> Project:
    try:
        return payload.to_project()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _build_export_metadata(project: Project) -> Dict[str, Any]:
    return {
        "project_name": project.name,
        "client_name": project.client_name,
    }


@router.post("/export/pdf", summary="Generate PDF report")
def export_pdf(payload: CalculationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    project = _project_from_request(payload)
    export_data = prepare_project_export(project)

    drawings: Dict[str, str] = {}
    drawings_dir = _ensure_output_directory("drawings")
    for window in project.windows:
        drawing_path = draw_window(window, export_dir=str(drawings_dir))
        drawings[window.id] = drawing_path

    reports_dir = _ensure_output_directory("reports")
    background_tasks.add_task(_cleanup_missing_files)
    pdf_path = Path(generate_pdf(export_data, drawings, export_dir=str(reports_dir)))
    return _register_file(pdf_path)


@router.post("/export/excel", summary="Generate Excel workbook")
def export_excel(payload: CalculationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    project = _project_from_request(payload)
    export_data = prepare_project_export(project)
    reports_dir = _ensure_output_directory("reports")
    background_tasks.add_task(_cleanup_missing_files)
    excel_path = Path(generate_excel(export_data, export_dir=str(reports_dir)))
    return _register_file(excel_path)


def _export_with_graphics(
    payload: CalculationRequest,
    exporter_cls: Type,
    subdir: str,
    *,
    include_dimensions: bool = True,
    include_bars: bool = True,
) -> Path:
    project = _project_from_request(payload)
    export_metadata = _build_export_metadata(project)

    root_dir = _ensure_output_directory("graphics") / subdir
    root_dir.mkdir(parents=True, exist_ok=True)
    export_dir = root_dir / uuid4().hex
    export_dir.mkdir(parents=True, exist_ok=True)

    try:
        exporter = exporter_cls(output_dir=str(export_dir))
    except RuntimeError as exc:  # Missing optional dependency
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    exporter.metadata.update(export_metadata)

    exporter.export_project(
        project,
        output_path=str(export_dir),
        include_dimensions=include_dimensions,
        include_bars=include_bars,
    )

    archive_path = shutil.make_archive(str(export_dir), "zip", root_dir=export_dir)
    shutil.rmtree(export_dir, ignore_errors=True)
    return Path(archive_path)


@router.post("/export/dxf", summary="Generate DXF package")
def export_dxf(payload: CalculationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    background_tasks.add_task(_cleanup_missing_files)
    path = _export_with_graphics(payload, DXFExporter, "dxf")
    return _register_file(path)


@router.post("/export/svg", summary="Generate SVG package")
def export_svg(payload: CalculationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    background_tasks.add_task(_cleanup_missing_files)
    path = _export_with_graphics(payload, SVGExporter, "svg")
    return _register_file(path)


@router.post("/export/png", summary="Generate PNG package")
def export_png(payload: CalculationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    background_tasks.add_task(_cleanup_missing_files)
    path = _export_with_graphics(payload, PNGExporter, "png", include_dimensions=True)
    return _register_file(path)


@router.get("/download/{file_id}", summary="Download a generated export")
def download_export(file_id: str) -> FileResponse:
    path = EXPORT_REGISTRY.get(file_id)
    if not path or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return FileResponse(path, filename=path.name)


def _cleanup_missing_files() -> None:
    stale = [key for key, path in EXPORT_REGISTRY.items() if not path.exists()]
    for key in stale:
        EXPORT_REGISTRY.pop(key, None)
