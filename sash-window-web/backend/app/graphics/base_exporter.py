"""Abstract base class for all graphics exporters.

This module provides the foundational interface that all export formats
must implement, ensuring consistency across DXF, SVG, PNG, PDF, and future formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.models import Window, Project


class BaseExporter(ABC):
    """Abstract base class for graphics and CAD exporters.

    All export implementations (DXF, SVG, PNG, etc.) should inherit from this
    class and implement the required methods.

    Attributes:
        output_dir: Directory where export files will be saved
        file_extension: File extension for this exporter (e.g., '.dxf', '.svg')
        metadata: Additional metadata to include in exports
    """

    def __init__(self, output_dir: str = "output/graphics") -> None:
        """Initialize the exporter.

        Args:
            output_dir: Directory path for output files
        """
        self.output_dir = Path(output_dir)
        self.file_extension: str = ""
        self.metadata: Dict[str, Any] = {}

    def _ensure_output_dir(self) -> Path:
        """Create output directory if it doesn't exist.

        Returns:
            Path object for the output directory
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def _generate_filename(self, base_name: str, suffix: str = "") -> Path:
        """Generate a standardized filename for exports.

        Args:
            base_name: Base name for the file (typically window or project name)
            suffix: Optional suffix to add before extension

        Returns:
            Full path to the output file
        """
        clean_name = base_name.replace(" ", "_").lower()
        if suffix:
            filename = f"{clean_name}_{suffix}{self.file_extension}"
        else:
            filename = f"{clean_name}{self.file_extension}"
        return self.output_dir / filename

    def _add_metadata(
        self,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Add metadata to be included in the export.

        Args:
            project_name: Name of the project
            client_name: Name of the client
            **kwargs: Additional metadata key-value pairs
        """
        self.metadata = {
            "generator": "Skylon Elements - Sash Window Designer",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_name": project_name,
            "client_name": client_name,
            **kwargs
        }

    @abstractmethod
    def export_window(
        self,
        window: Window,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export a single window to the target format.

        Args:
            window: Window object to export
            output_path: Optional custom output path
            **options: Format-specific export options

        Returns:
            Path to the generated file

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement export_window()")

    @abstractmethod
    def export_project(
        self,
        project: Project,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export an entire project with multiple windows.

        Args:
            project: Project object containing multiple windows
            output_path: Optional custom output path
            **options: Format-specific export options

        Returns:
            Path to the generated file or directory

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement export_project()")

    def validate_window(self, window: Window) -> bool:
        """Validate that a window has all required data for export.

        Args:
            window: Window object to validate

        Returns:
            True if window is valid for export
        """
        required_attrs = ['id', 'name', 'frame', 'sash_top', 'sash_bottom', 'glass']
        return all(hasattr(window, attr) for attr in required_attrs)

    def get_export_info(self) -> Dict[str, Any]:
        """Get information about this exporter.

        Returns:
            Dictionary containing exporter information
        """
        return {
            "format": self.__class__.__name__.replace("Exporter", ""),
            "extension": self.file_extension,
            "output_dir": str(self.output_dir),
            "metadata": self.metadata
        }


class AsyncExporter(BaseExporter):
    """Base class for exporters that support asynchronous operation.

    Future enhancement for handling large file exports without blocking the GUI.
    """

    def __init__(self, output_dir: str = "output/graphics") -> None:
        super().__init__(output_dir)
        self.progress_callback: Optional[callable] = None

    def set_progress_callback(self, callback: callable) -> None:
        """Set a callback function for progress updates.

        Args:
            callback: Function that takes progress percentage (0-100) as argument
        """
        self.progress_callback = callback

    def _update_progress(self, progress: float) -> None:
        """Update progress if callback is set.

        Args:
            progress: Progress percentage (0-100)
        """
        if self.progress_callback:
            self.progress_callback(progress)


class BatchExporter:
    """Utility class for exporting to multiple formats simultaneously.

    This class coordinates multiple exporters to generate a complete
    package of all available formats.
    """

    def __init__(self, exporters: list[BaseExporter]) -> None:
        """Initialize batch exporter with multiple format exporters.

        Args:
            exporters: List of exporter instances
        """
        self.exporters = exporters

    def export_all(
        self,
        window: Window,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Export a window to all registered formats.

        Args:
            window: Window object to export
            output_dir: Optional custom output directory

        Returns:
            Dictionary mapping format names to output file paths
        """
        results = {}
        for exporter in self.exporters:
            if output_dir:
                exporter.output_dir = Path(output_dir)
            try:
                file_path = exporter.export_window(window)
                format_name = exporter.get_export_info()["format"]
                results[format_name] = file_path
            except Exception as exc:
                results[exporter.__class__.__name__] = f"Error: {exc}"
        return results

    def create_package(
        self,
        project: Project,
        package_name: Optional[str] = None
    ) -> str:
        """Create a ZIP package with all export formats.

        Args:
            project: Project to export
            package_name: Optional custom package name

        Returns:
            Path to the generated ZIP file

        Note:
            Implementation deferred to future version
        """
        # TODO: Implement ZIP packaging with all formats
        raise NotImplementedError("Package creation coming in future version")
