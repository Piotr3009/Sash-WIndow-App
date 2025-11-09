"""Graphics and CAD visualization system for Sash Window Designer.

This package provides advanced graphics rendering, interactive visualization,
and CAD file export capabilities.

Modules:
    base_exporter: Abstract base class for all exporters
    renderer: Core geometry and rendering logic
    viewer: PyQt6 interactive graphics viewer widget
    export_dxf: DXF CAD file export
    export_svg: SVG vector graphics export
    export_png: PNG raster graphics export
    export_3d: 3D model export (STL/OBJ) - future feature
    export_gcode: CNC G-code generation - future feature
    nesting: Material optimization and nesting - future feature
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "BaseExporter",
    "WindowRenderer",
    "GraphicsViewer",
    "DXFExporter",
    "SVGExporter",
    "PNGExporter",
]
