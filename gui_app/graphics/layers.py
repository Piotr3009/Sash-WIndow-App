"""Layer definitions for CAD drawings.

This module defines standard layer names, colors, and line weights for
technical drawings following CAD conventions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class LayerName(str, Enum):
    """Standard layer names for window drawings."""
    FRAME = "FRAME"
    SASH_TOP = "SASH_TOP"
    SASH_BOTTOM = "SASH_BOTTOM"
    GLASS = "GLASS"
    BARS_V = "BARS_V"  # Vertical bars
    BARS_H = "BARS_H"  # Horizontal bars
    DIMENSIONS = "DIMENSIONS"
    CENTERLINES = "CENTERLINES"
    ANNOTATIONS = "ANNOTATIONS"


@dataclass
class LayerProperties:
    """Properties for a drawing layer."""
    name: str
    color: str  # Hex color code
    lineweight: float  # Line weight in mm
    linetype: str = "CONTINUOUS"  # CONTINUOUS, DASHED, DOTTED, etc.
    description: str = ""


# Standard layer definitions
LAYER_DEFINITIONS: Dict[str, LayerProperties] = {
    LayerName.FRAME: LayerProperties(
        name=LayerName.FRAME,
        color="#2C2C2C",  # Dark gray
        lineweight=0.50,  # Thick line
        linetype="CONTINUOUS",
        description="Window frame outline"
    ),
    LayerName.SASH_TOP: LayerProperties(
        name=LayerName.SASH_TOP,
        color="#4A90E2",  # Blue
        lineweight=0.35,
        linetype="CONTINUOUS",
        description="Top sash outline"
    ),
    LayerName.SASH_BOTTOM: LayerProperties(
        name=LayerName.SASH_BOTTOM,
        color="#4A90E2",  # Blue
        lineweight=0.35,
        linetype="CONTINUOUS",
        description="Bottom sash outline"
    ),
    LayerName.GLASS: LayerProperties(
        name=LayerName.GLASS,
        color="#A0C4FF",  # Light blue
        lineweight=0.18,
        linetype="CONTINUOUS",
        description="Glass panel outline"
    ),
    LayerName.BARS_V: LayerProperties(
        name=LayerName.BARS_V,
        color="#888888",  # Medium gray
        lineweight=0.25,
        linetype="DASHED",
        description="Vertical glazing bars"
    ),
    LayerName.BARS_H: LayerProperties(
        name=LayerName.BARS_H,
        color="#888888",  # Medium gray
        lineweight=0.25,
        linetype="DASHED",
        description="Horizontal glazing bars"
    ),
    LayerName.DIMENSIONS: LayerProperties(
        name=LayerName.DIMENSIONS,
        color="#FF0000",  # Red
        lineweight=0.18,  # Thin line
        linetype="CONTINUOUS",
        description="Dimension lines and text"
    ),
    LayerName.CENTERLINES: LayerProperties(
        name=LayerName.CENTERLINES,
        color="#00FF00",  # Green
        lineweight=0.18,
        linetype="DASHDOT",
        description="Center lines"
    ),
    LayerName.ANNOTATIONS: LayerProperties(
        name=LayerName.ANNOTATIONS,
        color="#000000",  # Black
        lineweight=0.25,
        linetype="CONTINUOUS",
        description="Text annotations and labels"
    ),
}


# DXF color indices (AutoCAD Color Index)
DXF_COLORS: Dict[str, int] = {
    LayerName.FRAME: 8,  # Dark gray
    LayerName.SASH_TOP: 5,  # Blue
    LayerName.SASH_BOTTOM: 5,  # Blue
    LayerName.GLASS: 4,  # Cyan
    LayerName.BARS_V: 9,  # Light gray
    LayerName.BARS_H: 9,  # Light gray
    LayerName.DIMENSIONS: 1,  # Red
    LayerName.CENTERLINES: 3,  # Green
    LayerName.ANNOTATIONS: 7,  # Black/White
}


# DXF lineweight (in hundredths of mm)
DXF_LINEWEIGHTS: Dict[str, int] = {
    LayerName.FRAME: 50,  # 0.50mm
    LayerName.SASH_TOP: 35,  # 0.35mm
    LayerName.SASH_BOTTOM: 35,  # 0.35mm
    LayerName.GLASS: 18,  # 0.18mm
    LayerName.BARS_V: 25,  # 0.25mm
    LayerName.BARS_H: 25,  # 0.25mm
    LayerName.DIMENSIONS: 18,  # 0.18mm
    LayerName.CENTERLINES: 18,  # 0.18mm
    LayerName.ANNOTATIONS: 25,  # 0.25mm
}


# SVG stroke widths (in mm, will be converted to pixels)
SVG_STROKE_WIDTHS: Dict[str, float] = {
    LayerName.FRAME: 0.50,
    LayerName.SASH_TOP: 0.35,
    LayerName.SASH_BOTTOM: 0.35,
    LayerName.GLASS: 0.18,
    LayerName.BARS_V: 0.25,
    LayerName.BARS_H: 0.25,
    LayerName.DIMENSIONS: 0.18,
    LayerName.CENTERLINES: 0.18,
    LayerName.ANNOTATIONS: 0.25,
}


# SVG stroke dash patterns
SVG_DASH_PATTERNS: Dict[str, str] = {
    "CONTINUOUS": "none",
    "DASHED": "5,3",
    "DOTTED": "1,2",
    "DASHDOT": "8,3,1,3",
    "CENTER": "12,2,2,2",
}


def get_layer_properties(layer_name: str) -> LayerProperties:
    """Get properties for a layer by name.

    Args:
        layer_name: Name of the layer

    Returns:
        LayerProperties object

    Raises:
        KeyError: If layer name not found
    """
    return LAYER_DEFINITIONS[layer_name]


def get_dxf_color(layer_name: str) -> int:
    """Get DXF color index for a layer.

    Args:
        layer_name: Name of the layer

    Returns:
        DXF color index (AutoCAD Color Index)
    """
    return DXF_COLORS.get(layer_name, 7)  # Default to white/black


def get_dxf_lineweight(layer_name: str) -> int:
    """Get DXF lineweight for a layer.

    Args:
        layer_name: Name of the layer

    Returns:
        Lineweight in hundredths of mm
    """
    return DXF_LINEWEIGHTS.get(layer_name, 25)  # Default to 0.25mm


def get_svg_stroke_width(layer_name: str) -> float:
    """Get SVG stroke width for a layer.

    Args:
        layer_name: Name of the layer

    Returns:
        Stroke width in mm
    """
    return SVG_STROKE_WIDTHS.get(layer_name, 0.25)


def get_svg_dash_pattern(linetype: str) -> str:
    """Get SVG dash pattern for a linetype.

    Args:
        linetype: Line type name (CONTINUOUS, DASHED, etc.)

    Returns:
        SVG dash pattern string
    """
    return SVG_DASH_PATTERNS.get(linetype, "none")


def get_all_layers() -> list[str]:
    """Get list of all layer names.

    Returns:
        List of layer name strings
    """
    return [layer.value for layer in LayerName]


def create_layer_legend() -> Dict[str, Dict[str, any]]:
    """Create a legend mapping for all layers.

    Returns:
        Dictionary mapping layer names to their properties
    """
    return {
        name: {
            "color": props.color,
            "lineweight": props.lineweight,
            "linetype": props.linetype,
            "description": props.description
        }
        for name, props in LAYER_DEFINITIONS.items()
    }
