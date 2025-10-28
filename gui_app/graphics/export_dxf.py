"""DXF CAD file export using ezdxf library.

This module provides professional-grade DXF export functionality with proper
layering, line weights, colors, and metadata for CAD applications.
"""

from __future__ import annotations

from typing import Optional, Any

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

from .base_exporter import BaseExporter
from .renderer import WindowRenderer, ColorScheme, Line
from ..backend.models import Window, Project


class DXFExporter(BaseExporter):
    """Export window designs to DXF CAD format.

    Generates professional DXF files compatible with AutoCAD, LibreCAD,
    and other CAD software. Uses R2018 DXF version with proper layering,
    line weights, and metadata.
    """

    def __init__(self, output_dir: str = "output/graphics") -> None:
        """Initialize DXF exporter.

        Args:
            output_dir: Directory for output files

        Raises:
            RuntimeError: If ezdxf library is not installed
        """
        super().__init__(output_dir)
        self.file_extension = ".dxf"

        if not EZDXF_AVAILABLE:
            raise RuntimeError(
                "ezdxf library is required for DXF export. "
                "Install it with: pip install ezdxf"
            )

        # DXF-specific settings
        self.dxf_version = "R2018"
        self.units = 4  # 4 = millimeters
        self.default_lineweight = 25  # 0.25mm in DXF units (hundredths of mm)

    def _setup_layers(self, doc: ezdxf.document.Drawing) -> None:
        """Setup DXF layers with appropriate colors and line weights.

        Args:
            doc: ezdxf document object
        """
        layers_config = [
            ("FRAME", 250, 50),  # color 250 (gray), lineweight 0.50mm
            ("SASH_TOP", 140, 35),  # color 140 (blue), lineweight 0.35mm
            ("SASH_BOTTOM", 140, 35),  # color 140 (blue), lineweight 0.35mm
            ("GLASS", 151, 15),  # color 151 (light blue), lineweight 0.15mm
            ("BARS", 252, 20),  # color 252 (light gray), lineweight 0.20mm
            ("DIMENSIONS", 1, 25),  # color 1 (red), lineweight 0.25mm
            ("TEXT", 7, 25),  # color 7 (white/black), lineweight 0.25mm
        ]

        for layer_name, color, lineweight in layers_config:
            layer = doc.layers.add(layer_name)
            layer.color = color
            layer.lineweight = lineweight

    def _add_metadata_block(
        self,
        doc: ezdxf.document.Drawing,
        window: Window
    ) -> None:
        """Add metadata block to DXF file.

        Args:
            doc: ezdxf document object
            window: Window object being exported
        """
        msp = doc.modelspace()

        # Create title block in upper right corner
        frame = window.frame
        x_offset = frame.width + 100
        y_offset = frame.height - 100

        # Add metadata text
        metadata_lines = [
            f"PROJECT: {self.metadata.get('project_name', 'N/A')}",
            f"WINDOW: {window.name}",
            f"CLIENT: {self.metadata.get('client_name', 'N/A')}",
            f"DIMENSIONS: {frame.width:.0f} x {frame.height:.0f} mm",
            f"PAINT: {window.paint_color}",
            f"HARDWARE: {window.hardware_finish}",
            f"GENERATED: {self.metadata.get('timestamp', 'N/A')[:10]}",
            f"BY: Skylon Elements v{self.metadata.get('version', '1.0')}",
        ]

        for i, line in enumerate(metadata_lines):
            msp.add_text(
                line,
                dxfattribs={
                    "layer": "TEXT",
                    "height": 3.0,
                }
            ).set_placement(
                (x_offset, y_offset - i * 5),
                align=TextEntityAlignment.LEFT
            )

    def export_window(
        self,
        window: Window,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export a window to DXF format.

        Args:
            window: Window object to export
            output_path: Optional custom output path
            **options: Additional options:
                - include_dimensions (bool): Include dimension lines (default True)
                - include_metadata (bool): Include metadata block (default True)
                - include_bars (bool): Include glazing bars (default True)

        Returns:
            Path to generated DXF file
        """
        if not self.validate_window(window):
            raise ValueError("Invalid window object for export")

        # Create renderer and generate geometry
        renderer = WindowRenderer(window, ColorScheme())
        renderer.generate_geometry(
            include_dimensions=options.get("include_dimensions", True),
            include_bars=options.get("include_bars", True)
        )

        # Create DXF document
        doc = ezdxf.new(self.dxf_version, units=self.units)
        self._setup_layers(doc)
        msp = doc.modelspace()

        # Export rectangles
        for rect in renderer.rectangles:
            # DXF doesn't have transparency, so we skip filled glass
            if rect.fill and rect.alpha < 1.0:
                # Just draw outline for transparent glass
                points = [
                    (rect.x, rect.y),
                    (rect.x + rect.width, rect.y),
                    (rect.x + rect.width, rect.y + rect.height),
                    (rect.x, rect.y + rect.height),
                    (rect.x, rect.y),  # Close the polyline
                ]
                msp.add_lwpolyline(
                    points,
                    dxfattribs={
                        "layer": rect.layer,
                    }
                )
            else:
                # Regular rectangle outline
                points = [
                    (rect.x, rect.y),
                    (rect.x + rect.width, rect.y),
                    (rect.x + rect.width, rect.y + rect.height),
                    (rect.x, rect.y + rect.height),
                    (rect.x, rect.y),  # Close the polyline
                ]
                msp.add_lwpolyline(
                    points,
                    dxfattribs={
                        "layer": rect.layer,
                    }
                )

        # Export lines
        for line in renderer.lines:
            msp.add_line(
                (line.x1, line.y1),
                (line.x2, line.y2),
                dxfattribs={
                    "layer": line.layer,
                    "linetype": self._get_dxf_linetype(line.linestyle),
                }
            )

        # Export dimension lines
        for dim in renderer.dimensions:
            # Main dimension line
            offset_y = dim.offset if dim.y1 == dim.y2 else 0
            offset_x = dim.offset if dim.x1 == dim.x2 else 0

            # Extension lines
            if dim.y1 == dim.y2:  # Horizontal dimension
                msp.add_line(
                    (dim.x1, dim.y1),
                    (dim.x1, dim.y1 + offset_y),
                    dxfattribs={"layer": dim.layer}
                )
                msp.add_line(
                    (dim.x2, dim.y2),
                    (dim.x2, dim.y2 + offset_y),
                    dxfattribs={"layer": dim.layer}
                )
                # Dimension line
                msp.add_line(
                    (dim.x1, dim.y1 + offset_y),
                    (dim.x2, dim.y2 + offset_y),
                    dxfattribs={"layer": dim.layer}
                )
            else:  # Vertical dimension
                msp.add_line(
                    (dim.x1, dim.y1),
                    (dim.x1 + offset_x, dim.y1),
                    dxfattribs={"layer": dim.layer}
                )
                msp.add_line(
                    (dim.x2, dim.y2),
                    (dim.x2 + offset_x, dim.y2),
                    dxfattribs={"layer": dim.layer}
                )
                # Dimension line
                msp.add_line(
                    (dim.x1 + offset_x, dim.y1),
                    (dim.x2 + offset_x, dim.y2),
                    dxfattribs={"layer": dim.layer}
                )

        # Export text
        for text in renderer.texts:
            msp.add_text(
                text.text,
                dxfattribs={
                    "layer": text.layer,
                    "height": text.size,
                }
            ).set_placement(
                (text.x, text.y),
                align=self._get_text_alignment(text.halign, text.valign)
            ).set_rotation(text.rotation)

        # Add metadata block if requested
        if options.get("include_metadata", True):
            self._add_metadata_block(doc, window)

        # Determine output path
        output_dir = self._ensure_output_dir()
        if output_path:
            file_path = output_path
        else:
            file_path = self._generate_filename(window.name, "cad")

        # Save DXF file
        doc.saveas(file_path)
        return str(file_path)

    def export_project(
        self,
        project: Project,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export all windows in a project to separate DXF files.

        Args:
            project: Project containing multiple windows
            output_path: Optional custom output directory
            **options: Export options passed to export_window

        Returns:
            Path to output directory containing all DXF files
        """
        self._add_metadata(
            project_name=project.name,
            client_name=project.client_name
        )

        output_dir = self._ensure_output_dir()
        exported_files = []

        for idx, window in enumerate(project.windows, start=1):
            filename = self._generate_filename(
                f"{project.name}_{window.name}",
                f"w{idx:02d}"
            )
            file_path = self.export_window(window, str(filename), **options)
            exported_files.append(file_path)

        return str(output_dir)

    def _get_dxf_linetype(self, linestyle: str) -> str:
        """Convert linestyle to DXF linetype.

        Args:
            linestyle: Linestyle string (solid, dashed, dotted)

        Returns:
            DXF linetype name
        """
        mapping = {
            "solid": "CONTINUOUS",
            "dashed": "DASHED",
            "dotted": "DOTTED",
        }
        return mapping.get(linestyle.lower(), "CONTINUOUS")

    def _get_text_alignment(self, halign: str, valign: str) -> TextEntityAlignment:
        """Convert alignment strings to ezdxf alignment enum.

        Args:
            halign: Horizontal alignment (left, center, right)
            valign: Vertical alignment (top, middle, bottom)

        Returns:
            ezdxf TextEntityAlignment value
        """
        alignment_map = {
            ("left", "top"): TextEntityAlignment.TOP_LEFT,
            ("center", "top"): TextEntityAlignment.TOP_CENTER,
            ("right", "top"): TextEntityAlignment.TOP_RIGHT,
            ("left", "middle"): TextEntityAlignment.MIDDLE_LEFT,
            ("center", "middle"): TextEntityAlignment.MIDDLE_CENTER,
            ("right", "middle"): TextEntityAlignment.MIDDLE_RIGHT,
            ("left", "bottom"): TextEntityAlignment.BOTTOM_LEFT,
            ("center", "bottom"): TextEntityAlignment.BOTTOM_CENTER,
            ("right", "bottom"): TextEntityAlignment.BOTTOM_RIGHT,
        }
        return alignment_map.get((halign.lower(), valign.lower()), TextEntityAlignment.MIDDLE_CENTER)
