"""Background workers for CAD export operations.

This module provides QRunnable workers for threaded CAD exports, allowing
the GUI to remain responsive during export operations.
"""

from __future__ import annotations

from typing import Any, Optional, Callable
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    """Signals for export worker communication.

    Attributes:
        started: Emitted when export starts
        progress: Emitted with progress value (0-100)
        finished: Emitted with result path when export completes
        error: Emitted with error message if export fails
    """
    started = pyqtSignal()
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)  # file path
    error = pyqtSignal(str)  # error message


class ExportWorker(QRunnable):
    """Background worker for CAD file exports.

    This worker runs export operations in a background thread to keep
    the GUI responsive. Supports DXF, SVG, and preview rendering.

    Usage:
        worker = ExportWorker(exporter, scene, output_path)
        worker.signals.finished.connect(on_export_complete)
        worker.signals.error.connect(on_export_error)
        QThreadPool.globalInstance().start(worker)
    """

    def __init__(
        self,
        export_func: Callable,
        scene: dict,
        output_path: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize export worker.

        Args:
            export_func: Export function to call (e.g., exporter.export_from_scene)
            scene: Scene dictionary from build_scene()
            output_path: Optional output path
            **kwargs: Additional arguments for export function
        """
        super().__init__()
        self.export_func = export_func
        self.scene = scene
        self.output_path = output_path
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Allow worker to be auto-deleted after run
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self) -> None:
        """Run the export operation in background thread."""
        try:
            # Emit started signal
            self.signals.started.emit()

            # Emit initial progress
            self.signals.progress.emit(0)

            # Run the export function
            result_path = self.export_func(
                self.scene,
                self.output_path,
                **self.kwargs
            )

            # Emit completion progress
            self.signals.progress.emit(100)

            # Emit success signal with result path
            self.signals.finished.emit(str(result_path))

        except Exception as e:
            # Emit error signal with error message
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.signals.error.emit(error_msg)


class PreviewWorker(QRunnable):
    """Background worker for SVG preview rendering.

    Renders SVG files to PNG format for preview display in the GUI.
    """

    def __init__(
        self,
        svg_path: str,
        png_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        dpi: int = 96
    ):
        """Initialize preview worker.

        Args:
            svg_path: Path to SVG file
            png_path: Path for output PNG file
            width: Optional width in pixels
            height: Optional height in pixels
            dpi: DPI for rendering (default 96)
        """
        super().__init__()
        self.svg_path = svg_path
        self.png_path = png_path
        self.width = width
        self.height = height
        self.dpi = dpi
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self) -> None:
        """Run the preview rendering in background thread."""
        try:
            from .preview import render_preview_svg, is_preview_available

            # Emit started signal
            self.signals.started.emit()
            self.signals.progress.emit(0)

            # Check if preview is available
            if not is_preview_available():
                raise RuntimeError(
                    "cairosvg is not installed. "
                    "Install it with: pip install cairosvg"
                )

            # Render preview
            result_path = render_preview_svg(
                self.svg_path,
                self.png_path,
                width=self.width,
                height=self.height,
                dpi=self.dpi
            )

            self.signals.progress.emit(100)

            if result_path:
                self.signals.finished.emit(str(result_path))
            else:
                self.signals.error.emit("Preview rendering failed")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.signals.error.emit(error_msg)


class BatchExportWorker(QRunnable):
    """Background worker for batch export operations.

    Exports multiple windows or multiple formats in a single operation.
    """

    def __init__(
        self,
        scenes: list[dict],
        export_functions: list[Callable],
        output_paths: Optional[list[str]] = None
    ):
        """Initialize batch export worker.

        Args:
            scenes: List of scene dictionaries
            export_functions: List of export functions to call
            output_paths: Optional list of output paths
        """
        super().__init__()
        self.scenes = scenes
        self.export_functions = export_functions
        self.output_paths = output_paths or [None] * len(scenes)
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self) -> None:
        """Run batch export in background thread."""
        try:
            self.signals.started.emit()

            total_items = len(self.scenes) * len(self.export_functions)
            completed = 0
            result_paths = []

            for scene, output_path in zip(self.scenes, self.output_paths):
                for export_func in self.export_functions:
                    try:
                        result_path = export_func(scene, output_path)
                        result_paths.append(str(result_path))

                        completed += 1
                        progress = int((completed / total_items) * 100)
                        self.signals.progress.emit(progress)

                    except Exception as e:
                        # Log error but continue with other exports
                        error_msg = f"Export failed: {type(e).__name__}: {str(e)}"
                        self.signals.error.emit(error_msg)

            # Emit finished with comma-separated paths
            self.signals.finished.emit(", ".join(result_paths))

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.signals.error.emit(error_msg)
