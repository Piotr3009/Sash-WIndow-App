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
from .layers import get_dxf_color, get_dxf_lineweight, get_all_layers, LayerName
from .geometry import Point2D
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

    def export_from_scene(
        self,
        scene: dict,
        output_path: Optional[str] = None
    ) -> str:
        """Export a window from a pre-built scene dictionary.

        This is the recommended method for CAD export using the scene-based
        architecture. Supports all scene geometry types and proper layering.

        Args:
            scene: Scene dictionary from build_scene()
            output_path: Optional custom output path

        Returns:
            Path to generated DXF file
        """
        # Create DXF document - R2018, Modelspace only
        doc = ezdxf.new(self.dxf_version, units=self.units)

        # Setup layers with exact color codes
        self._setup_scene_layers(doc)

        msp = doc.modelspace()

        # Process each layer from the scene
        for layer_name, geometries in scene['layers'].items():
            for geom in geometries:
                geom_type = geom.get('type')

                if geom_type == 'polyline':
                    # Convert Point2D objects to tuples
                    points = [(p.x, p.y) if isinstance(p, Point2D) else p
                             for p in geom['points']]
                    msp.add_lwpolyline(
                        points,
                        dxfattribs={"layer": layer_name}
                    )

                elif geom_type == 'line':
                    start = geom['start']
                    end = geom['end']
                    msp.add_line(
                        (start.x, start.y),
                        (end.x, end.y),
                        dxfattribs={"layer": layer_name}
                    )

                elif geom_type == 'text':
                    pos = geom['position']
                    rotation = geom.get('rotation', 0)
                    msp.add_text(
                        geom['text'],
                        dxfattribs={
                            "layer": layer_name,
                            "height": geom['height'],
                        }
                    ).set_placement(
                        (pos.x, pos.y),
                        align=self._get_alignment_from_string(geom.get('alignment', 'left'))
                    ).set_rotation(rotation)

                elif geom_type in ('dimension_horizontal', 'dimension_vertical'):
                    # Add dimension components
                    dim_data = geom['data']

                    # Extension lines
                    for ext_line in dim_data['extension_lines']:
                        start = ext_line['start']
                        end = ext_line['end']
                        msp.add_line(
                            (start.x, start.y),
                            (end.x, end.y),
                            dxfattribs={"layer": layer_name}
                        )

                    # Dimension line
                    dim_line = dim_data['dimension_line']
                    start = dim_line['start']
                    end = dim_line['end']
                    msp.add_line(
                        (start.x, start.y),
                        (end.x, end.y),
                        dxfattribs={"layer": layer_name}
                    )

                    # Arrows (simplified as small triangles)
                    for arrow in dim_data['arrows']:
                        from .dimensioning import create_arrow_polygon
                        arrow_points = create_arrow_polygon(
                            arrow.tip,
                            arrow.angle,
                            arrow.size
                        )
                        points = [(p.x, p.y) for p in arrow_points]
                        points.append(points[0])  # Close polygon
                        msp.add_lwpolyline(
                            points,
                            dxfattribs={"layer": layer_name}
                        )

                    # Dimension text
                    text = dim_data['text']
                    msp.add_text(
                        text.text,
                        dxfattribs={
                            "layer": layer_name,
                            "height": text.height,
                        }
                    ).set_placement(
                        (text.position.x, text.position.y),
                        align=TextEntityAlignment.MIDDLE_CENTER
                    ).set_rotation(text.rotation)

        # Add metadata from scene
        self._add_scene_metadata(doc, scene)

        # Determine output path
        if output_path:
            file_path = output_path
        else:
            window_name = scene['metadata'].get('window_name', 'window')
            output_dir = self._ensure_output_dir()
            file_path = output_dir / f"{window_name}_cad.dxf"

        # Save DXF file
        doc.saveas(str(file_path))
        return str(file_path)

    def _setup_scene_layers(self, doc: ezdxf.document.Drawing) -> None:
        """Setup DXF layers using exact specifications from layers.py.

        Args:
            doc: ezdxf document object
        """
        for layer_name in get_all_layers():
            layer = doc.layers.add(layer_name)
            layer.color = get_dxf_color(layer_name)
            layer.lineweight = get_dxf_lineweight(layer_name)

    def _add_scene_metadata(
        self,
        doc: ezdxf.document.Drawing,
        scene: dict
    ) -> None:
        """Add metadata from scene to ANNOTATIONS layer.

        Args:
            doc: ezdxf document object
            scene: Scene dictionary
        """
        msp = doc.modelspace()
        metadata = scene['metadata']

        # Get bounds for positioning
        bounds = scene.get('bounds')
        if bounds:
            x_offset = bounds.max_point.x + 20
            y_offset = bounds.max_point.y - 10
        else:
            x_offset = metadata['frame_width'] + 20
            y_offset = metadata['frame_height'] - 10

        # Metadata lines per user specification
        metadata_lines = [
            f"PROJECT: {self.metadata.get('project_name', 'N/A')}",
            f"WINDOW: {metadata['window_name']}",
            f"CLIENT: {self.metadata.get('client_name', 'N/A')}",
            f"DATE: {metadata['generated_at'][:10]}",
            f"WINDOW ID: {metadata['window_id']}",
            f"DIMENSIONS: {metadata['frame_width']:.0f} x {metadata['frame_height']:.0f} mm",
            f"PAINT: {metadata['paint_color']}",
            f"HARDWARE: {metadata['hardware_finish']}",
        ]

        for i, line in enumerate(metadata_lines):
            msp.add_text(
                line,
                dxfattribs={
                    "layer": LayerName.ANNOTATIONS,
                    "height": 3.0,
                }
            ).set_placement(
                (x_offset, y_offset - i * 5),
                align=TextEntityAlignment.LEFT
            )

    def _get_alignment_from_string(self, alignment: str) -> TextEntityAlignment:
        """Convert alignment string to ezdxf TextEntityAlignment.

        Args:
            alignment: Alignment string (left, center, right)

        Returns:
            ezdxf TextEntityAlignment value
        """
        alignment_map = {
            'left': TextEntityAlignment.LEFT,
            'center': TextEntityAlignment.CENTER,
            'right': TextEntityAlignment.RIGHT,
        }
        return alignment_map.get(alignment.lower(), TextEntityAlignment.LEFT)

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
