"""Demonstration entry point for the Skylon Elements backend."""
from __future__ import annotations

import sys
import uuid

from .calculations import assemble_window, prepare_project_export
from .database import save_project, save_window
from .drawings import draw_window
from .export_excel import generate_excel
from .export_pdf import generate_pdf
from .models import Project


def main() -> None:
    project_id = str(uuid.uuid4())
    window_id = str(uuid.uuid4())

    # Example inputs - in production these would come from a GUI or API request
    frame_width = 1200.0
    frame_height = 1600.0
    top_sash_height = 780.0
    bottom_sash_height = 780.0

    window = assemble_window(
        window_id=window_id,
        name="Living Room",
        frame_width=frame_width,
        frame_height=frame_height,
        top_sash_height=top_sash_height,
        bottom_sash_height=bottom_sash_height,
        paint_color="White",
        hardware_finish="Satin Chrome",
        trickle_vent="Concealed",
        sash_catches="Polished Brass",
        cill_extension=60,
        glass_type="24mm TGH/ARG/TGH",
        glass_frosted=False,
        glass_toughened=True,
        spacer_color="Black",
        glass_pcs=2,
        bars_layout="3x3",
        bars_vertical=3,
        bars_horizontal=3,
    )

    project = Project(
        id=project_id,
        name="Sample Residence",
        client_name="Jane Doe",
        windows=[window],
    )

    export_data = prepare_project_export(project)

    # Persist to Supabase if configured
    try:
        save_project(project)
        window_export = export_data["windows"][0]
        save_window(project.id, window, window_export["materials"], window_export["glass"])
        print(f"Project saved: {project.name}")
    except Exception as exc:
        print("Supabase persistence skipped:", exc)

    drawing_path = draw_window(window)
    drawings = {window.id: drawing_path}

    excel_path = generate_excel(export_data)
    pdf_path = generate_pdf(export_data, drawings)

    print(f"PDF: {pdf_path}")
    print(f"Excel: {excel_path}")
    print(f"Drawing: {drawing_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - entry point error handling
        print("An error occurred:", exc)
        sys.exit(1)
