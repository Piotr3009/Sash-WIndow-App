"""Dimensioning utilities for technical drawings.

This module provides functions for creating dimension lines, arrows,
and measurement labels following technical drawing standards.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

from .geometry import Point2D
from .layers import LayerName


@dataclass
class DimensionLine:
    """Represents a dimension line with measurement.

    Attributes:
        start: Start point of dimension
        end: End point of dimension
        offset: Distance from geometry being dimensioned (mm)
        measurement: Measured value in mm
        text: Optional custom text (if None, uses measurement)
        layer: Layer name for dimension
        precision: Number of decimal places for measurement
    """
    start: Point2D
    end: Point2D
    offset: float
    measurement: float
    text: Optional[str] = None
    layer: str = LayerName.DIMENSIONS
    precision: int = 1


@dataclass
class DimensionArrow:
    """Arrow head for dimension line.

    Attributes:
        tip: Arrow tip point
        angle: Arrow rotation angle in degrees
        size: Arrow size in mm
        style: Arrow style ('closed', 'open', 'dot', 'slash')
    """
    tip: Point2D
    angle: float
    size: float = 3.0
    style: str = 'closed'


@dataclass
class DimensionText:
    """Dimension text label.

    Attributes:
        position: Text position
        text: Text content
        height: Text height in mm
        rotation: Text rotation in degrees
        layer: Layer name
    """
    position: Point2D
    text: str
    height: float = 3.5
    rotation: float = 0.0
    layer: str = LayerName.DIMENSIONS


class DimensionBuilder:
    """Builder for creating dimension lines with ISO standard formatting."""

    def __init__(
        self,
        arrow_size: float = 3.0,
        text_height: float = 3.5,  # ISO standard 3.5mm
        extension_overshoot: float = 2.0,
        text_gap: float = 5.0  # ISO standard 5mm offset
    ):
        """Initialize dimension builder.

        Args:
            arrow_size: Size of arrow heads in mm
            text_height: Height of dimension text in mm
            extension_overshoot: How far extension lines extend beyond dimension line
            text_gap: Gap between dimension line and text
        """
        self.arrow_size = arrow_size
        self.text_height = text_height
        self.extension_overshoot = extension_overshoot
        self.text_gap = text_gap

    def create_horizontal_dimension(
        self,
        start_x: float,
        end_x: float,
        y: float,
        offset: float = 10.0,
        precision: int = 1,
        text_override: Optional[str] = None
    ) -> dict:
        """Create a horizontal dimension line.

        Args:
            start_x: Start X coordinate
            end_x: End X coordinate
            y: Y coordinate of dimensioned geometry
            offset: Distance above geometry
            precision: Decimal places for measurement
            text_override: Optional custom text

        Returns:
            Dictionary with dimension components
        """
        measurement = abs(end_x - start_x)
        dim_y = y + offset

        start = Point2D(start_x, y)
        end = Point2D(end_x, y)
        dim_start = Point2D(start_x, dim_y)
        dim_end = Point2D(end_x, dim_y)

        # Extension lines
        extension_lines = [
            {'start': start, 'end': Point2D(start_x, dim_y + self.extension_overshoot)},
            {'start': end, 'end': Point2D(end_x, dim_y + self.extension_overshoot)}
        ]

        # Dimension line
        dimension_line = {'start': dim_start, 'end': dim_end}

        # Arrows
        arrows = [
            DimensionArrow(dim_start, 0, self.arrow_size),  # Left arrow
            DimensionArrow(dim_end, 180, self.arrow_size)  # Right arrow
        ]

        # Text
        text_pos = Point2D((start_x + end_x) / 2, dim_y + self.text_gap + self.text_height / 2)
        text_content = text_override or f"{measurement:.{precision}f}"
        text = DimensionText(text_pos, text_content, self.text_height)

        return {
            'extension_lines': extension_lines,
            'dimension_line': dimension_line,
            'arrows': arrows,
            'text': text,
            'measurement': measurement
        }

    def create_vertical_dimension(
        self,
        start_y: float,
        end_y: float,
        x: float,
        offset: float = 10.0,
        precision: int = 1,
        text_override: Optional[str] = None
    ) -> dict:
        """Create a vertical dimension line.

        Args:
            start_y: Start Y coordinate
            end_y: End Y coordinate
            x: X coordinate of dimensioned geometry
            offset: Distance to the right of geometry
            precision: Decimal places for measurement
            text_override: Optional custom text

        Returns:
            Dictionary with dimension components
        """
        measurement = abs(end_y - start_y)
        dim_x = x + offset

        start = Point2D(x, start_y)
        end = Point2D(x, end_y)
        dim_start = Point2D(dim_x, start_y)
        dim_end = Point2D(dim_x, end_y)

        # Extension lines
        extension_lines = [
            {'start': start, 'end': Point2D(dim_x + self.extension_overshoot, start_y)},
            {'start': end, 'end': Point2D(dim_x + self.extension_overshoot, end_y)}
        ]

        # Dimension line
        dimension_line = {'start': dim_start, 'end': dim_end}

        # Arrows
        arrows = [
            DimensionArrow(dim_start, 90, self.arrow_size),  # Bottom arrow
            DimensionArrow(dim_end, 270, self.arrow_size)  # Top arrow
        ]

        # Text
        text_pos = Point2D(dim_x + self.text_gap + self.text_height, (start_y + end_y) / 2)
        text_content = text_override or f"{measurement:.{precision}f}"
        text = DimensionText(text_pos, text_content, self.text_height, rotation=90)

        return {
            'extension_lines': extension_lines,
            'dimension_line': dimension_line,
            'arrows': arrows,
            'text': text,
            'measurement': measurement
        }

    def create_aligned_dimension(
        self,
        start: Point2D,
        end: Point2D,
        offset: float = 10.0,
        precision: int = 1,
        text_override: Optional[str] = None
    ) -> dict:
        """Create an aligned dimension line (follows angle of geometry).

        Args:
            start: Start point
            end: End point
            offset: Distance perpendicular to geometry
            precision: Decimal places for measurement
            text_override: Optional custom text

        Returns:
            Dictionary with dimension components
        """
        import math

        # Calculate measurement
        dx = end.x - start.x
        dy = end.y - start.y
        measurement = math.sqrt(dx * dx + dy * dy)

        # Calculate angle
        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle)

        # Perpendicular angle for offset
        perp_angle = angle + math.pi / 2
        offset_dx = offset * math.cos(perp_angle)
        offset_dy = offset * math.sin(perp_angle)

        # Dimension line points
        dim_start = Point2D(start.x + offset_dx, start.y + offset_dy)
        dim_end = Point2D(end.x + offset_dx, end.y + offset_dy)

        # Extension lines
        extension_lines = [
            {'start': start, 'end': dim_start},
            {'start': end, 'end': dim_end}
        ]

        # Dimension line
        dimension_line = {'start': dim_start, 'end': dim_end}

        # Arrows
        arrows = [
            DimensionArrow(dim_start, angle_deg, self.arrow_size),
            DimensionArrow(dim_end, angle_deg + 180, self.arrow_size)
        ]

        # Text
        text_x = (dim_start.x + dim_end.x) / 2
        text_y = (dim_start.y + dim_end.y) / 2
        text_pos = Point2D(text_x, text_y)
        text_content = text_override or f"{measurement:.{precision}f}"
        text = DimensionText(text_pos, text_content, self.text_height, rotation=angle_deg)

        return {
            'extension_lines': extension_lines,
            'dimension_line': dimension_line,
            'arrows': arrows,
            'text': text,
            'measurement': measurement,
            'angle': angle_deg
        }

    def create_radial_dimension(
        self,
        center: Point2D,
        radius: float,
        angle: float = 45.0,
        precision: int = 1,
        prefix: str = "R"
    ) -> dict:
        """Create a radial dimension (for circles/arcs).

        Args:
            center: Center point of circle
            radius: Radius value
            angle: Angle for dimension line placement (degrees)
            precision: Decimal places for measurement
            prefix: Prefix for text (default 'R' for radius)

        Returns:
            Dictionary with dimension components
        """
        import math

        angle_rad = math.radians(angle)
        end_x = center.x + radius * math.cos(angle_rad)
        end_y = center.y + radius * math.sin(angle_rad)
        end_point = Point2D(end_x, end_y)

        # Dimension line from center to edge
        dimension_line = {'start': center, 'end': end_point}

        # Arrow at edge
        arrows = [DimensionArrow(end_point, angle + 180, self.arrow_size)]

        # Text near midpoint
        text_x = center.x + (radius * 0.6) * math.cos(angle_rad)
        text_y = center.y + (radius * 0.6) * math.sin(angle_rad)
        text_pos = Point2D(text_x, text_y)
        text_content = f"{prefix}{radius:.{precision}f}"
        text = DimensionText(text_pos, text_content, self.text_height)

        return {
            'dimension_line': dimension_line,
            'arrows': arrows,
            'text': text,
            'measurement': radius
        }


def create_arrow_polygon(
    tip: Point2D,
    angle: float,
    size: float = 3.0,
    style: str = 'closed'
) -> List[Point2D]:
    """Create arrow polygon points.

    Args:
        tip: Arrow tip point
        angle: Arrow direction angle in degrees
        size: Arrow size in mm
        style: Arrow style ('closed', 'open')

    Returns:
        List of points defining arrow polygon
    """
    import math

    angle_rad = math.radians(angle)
    arrow_angle = math.radians(20)  # Half-angle of arrow head

    # Calculate arrow points
    base_dist = size * math.cos(arrow_angle)
    base_width = size * math.sin(arrow_angle)

    # Base center point
    base_x = tip.x - base_dist * math.cos(angle_rad)
    base_y = tip.y - base_dist * math.sin(angle_rad)

    # Perpendicular direction
    perp_angle = angle_rad + math.pi / 2

    # Arrow points (tip, left wing, right wing)
    points = [
        tip,  # Tip
        Point2D(
            base_x + base_width * math.cos(perp_angle),
            base_y + base_width * math.sin(perp_angle)
        ),  # Left wing
        Point2D(
            base_x - base_width * math.cos(perp_angle),
            base_y - base_width * math.sin(perp_angle)
        ),  # Right wing
    ]

    return points


def format_dimension_text(
    value: float,
    precision: int = 1,
    units: str = "mm",
    show_units: bool = True
) -> str:
    """Format dimension text with proper precision and units.

    Args:
        value: Measurement value
        precision: Number of decimal places
        units: Unit string (default 'mm')
        show_units: Whether to show units

    Returns:
        Formatted dimension text
    """
    text = f"{value:.{precision}f}"
    if show_units:
        text += f" {units}"
    return text
