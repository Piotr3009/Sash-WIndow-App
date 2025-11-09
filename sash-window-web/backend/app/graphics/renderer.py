"""Core rendering engine for window geometry and visualization.

This module provides the WindowRenderer class that converts window data models
into geometric primitives (rectangles, lines, text) for rendering and export.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

from app.core.models import Window, Frame, Sash, Glass, Bars


# Color scheme for professional CAD rendering
@dataclass
class ColorScheme:
    """Professional color scheme for window components."""
    frame: str = "#444444"  # Dark gray
    sash: str = "#4A90E2"  # Professional blue
    glass: str = "#A0C4FF"  # Light blue
    glass_alpha: float = 0.4  # Glass transparency
    bars: str = "#AAAAAA"  # Medium gray
    dimensions: str = "#FF6B6B"  # Red for dimension lines
    grid: str = "#E0E0E0"  # Light gray for background grid
    text: str = "#333333"  # Dark gray for text


@dataclass
class Point:
    """2D point in millimeters."""
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple format."""
        return (self.x, self.y)


@dataclass
class Rectangle:
    """Rectangle primitive with position, dimensions, and style."""
    x: float
    y: float
    width: float
    height: float
    color: str
    fill: bool = False
    alpha: float = 1.0
    linewidth: float = 0.25  # mm
    layer: str = "DEFAULT"

    def get_corners(self) -> List[Point]:
        """Get four corner points of the rectangle."""
        return [
            Point(self.x, self.y),
            Point(self.x + self.width, self.y),
            Point(self.x + self.width, self.y + self.height),
            Point(self.x, self.y + self.height),
        ]

    def get_center(self) -> Point:
        """Get center point of the rectangle."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)


@dataclass
class Line:
    """Line primitive with start and end points."""
    x1: float
    y1: float
    x2: float
    y2: float
    color: str
    linewidth: float = 0.25  # mm
    linestyle: str = "solid"  # solid, dashed, dotted
    layer: str = "DEFAULT"

    def get_points(self) -> Tuple[Point, Point]:
        """Get start and end points."""
        return Point(self.x1, self.y1), Point(self.x2, self.y2)

    def length(self) -> float:
        """Calculate line length."""
        return ((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2) ** 0.5


@dataclass
class Text:
    """Text annotation with position and styling."""
    x: float
    y: float
    text: str
    size: float = 3.0  # mm
    color: str = "#333333"
    halign: str = "center"  # left, center, right
    valign: str = "middle"  # top, middle, bottom
    rotation: float = 0.0  # degrees
    layer: str = "TEXT"


@dataclass
class DimensionLine:
    """Dimension line with arrows and measurement label."""
    x1: float
    y1: float
    x2: float
    y2: float
    offset: float = 10.0  # mm offset from geometry
    color: str = "#FF6B6B"
    layer: str = "DIMENSIONS"

    def get_measurement(self) -> float:
        """Calculate the measurement value."""
        return ((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2) ** 0.5


class WindowRenderer:
    """Converts Window data models into geometric primitives for rendering.

    This class is the core of the graphics system, generating all geometry,
    colors, layers, and annotations from the backend window calculations.
    """

    def __init__(
        self,
        window: Window,
        color_scheme: Optional[ColorScheme] = None,
        scale: float = 1.0
    ) -> None:
        """Initialize the renderer.

        Args:
            window: Window object to render
            color_scheme: Optional custom color scheme
            scale: Scale factor for rendering (1.0 = actual size in mm)
        """
        self.window = window
        self.colors = color_scheme or ColorScheme()
        self.scale = scale

        # Geometry collections
        self.rectangles: List[Rectangle] = []
        self.lines: List[Line] = []
        self.texts: List[Text] = []
        self.dimensions: List[DimensionLine] = []

        # Rendering bounds (auto-calculated)
        self.bounds_min: Optional[Point] = None
        self.bounds_max: Optional[Point] = None

    def generate_geometry(
        self,
        include_dimensions: bool = True,
        include_bars: bool = True
    ) -> None:
        """Generate all geometric primitives from the window data.

        Args:
            include_dimensions: Whether to include dimension lines
            include_bars: Whether to include glazing bars
        """
        self.rectangles.clear()
        self.lines.clear()
        self.texts.clear()
        self.dimensions.clear()

        self._generate_frame()
        self._generate_sashes()
        self._generate_glass()

        if include_bars and self.window.bars.vertical_bars + self.window.bars.horizontal_bars > 0:
            self._generate_bars()

        if include_dimensions:
            self._generate_dimensions()

        self._calculate_bounds()

    def _generate_frame(self) -> None:
        """Generate frame geometry."""
        frame = self.window.frame

        # Outer frame rectangle
        self.rectangles.append(
            Rectangle(
                x=0,
                y=0,
                width=frame.width * self.scale,
                height=frame.height * self.scale,
                color=self.colors.frame,
                fill=False,
                linewidth=0.5,
                layer="FRAME"
            )
        )

    def _generate_sashes(self) -> None:
        """Generate top and bottom sash geometry."""
        frame = self.window.frame
        sash_top = self.window.sash_top
        sash_bottom = self.window.sash_bottom

        # Calculate sash offset (centered in frame)
        sash_offset_x = (frame.width - sash_bottom.width) / 2

        # Bottom sash
        self.rectangles.append(
            Rectangle(
                x=sash_offset_x * self.scale,
                y=0,
                width=sash_bottom.width * self.scale,
                height=sash_bottom.height * self.scale,
                color=self.colors.sash,
                fill=False,
                linewidth=0.35,
                layer="SASH_BOTTOM"
            )
        )

        # Top sash
        top_sash_y = frame.height - sash_top.height
        self.rectangles.append(
            Rectangle(
                x=sash_offset_x * self.scale,
                y=top_sash_y * self.scale,
                width=sash_top.width * self.scale,
                height=sash_top.height * self.scale,
                color=self.colors.sash,
                fill=False,
                linewidth=0.35,
                layer="SASH_TOP"
            )
        )

        # Meeting rails (horizontal line between sashes)
        self.lines.append(
            Line(
                x1=sash_offset_x * self.scale,
                y1=sash_bottom.height * self.scale,
                x2=(sash_offset_x + sash_bottom.width) * self.scale,
                y2=sash_bottom.height * self.scale,
                color=self.colors.sash,
                linewidth=0.5,
                layer="SASH_BOTTOM"
            )
        )

    def _generate_glass(self) -> None:
        """Generate glass panel geometry."""
        frame = self.window.frame
        sash_bottom = self.window.sash_bottom
        glass = self.window.glass

        # Glass is offset within the sash
        sash_offset_x = (frame.width - sash_bottom.width) / 2
        glass_offset_x = sash_offset_x + (sash_bottom.width - glass.width) / 2
        glass_offset_y = (sash_bottom.height - glass.height) / 2

        # Glass rectangle with transparency
        self.rectangles.append(
            Rectangle(
                x=glass_offset_x * self.scale,
                y=glass_offset_y * self.scale,
                width=glass.width * self.scale,
                height=glass.height * self.scale,
                color=self.colors.glass,
                fill=True,
                alpha=self.colors.glass_alpha,
                linewidth=0.15,
                layer="GLASS"
            )
        )

    def _generate_bars(self) -> None:
        """Generate glazing bar geometry."""
        frame = self.window.frame
        sash_bottom = self.window.sash_bottom
        bars = self.window.bars

        sash_offset_x = (frame.width - sash_bottom.width) / 2

        # Vertical bars
        for i in range(1, bars.vertical_bars + 1):
            x = sash_offset_x + i * (sash_bottom.width / (bars.vertical_bars + 1))
            self.lines.append(
                Line(
                    x1=x * self.scale,
                    y1=0,
                    x2=x * self.scale,
                    y2=sash_bottom.height * self.scale,
                    color=self.colors.bars,
                    linewidth=0.2,
                    linestyle="dotted",
                    layer="BARS"
                )
            )

        # Horizontal bars
        for i in range(1, bars.horizontal_bars + 1):
            y = i * (sash_bottom.height / (bars.horizontal_bars + 1))
            self.lines.append(
                Line(
                    x1=sash_offset_x * self.scale,
                    y1=y * self.scale,
                    x2=(sash_offset_x + sash_bottom.width) * self.scale,
                    y2=y * self.scale,
                    color=self.colors.bars,
                    linewidth=0.2,
                    linestyle="dotted",
                    layer="BARS"
                )
            )

    def _generate_dimensions(self) -> None:
        """Generate dimension lines and labels."""
        frame = self.window.frame

        # Horizontal dimension (width)
        self.dimensions.append(
            DimensionLine(
                x1=0,
                y1=frame.height * self.scale,
                x2=frame.width * self.scale,
                y2=frame.height * self.scale,
                offset=20.0 * self.scale,
                layer="DIMENSIONS"
            )
        )

        # Vertical dimension (height)
        self.dimensions.append(
            DimensionLine(
                x1=frame.width * self.scale,
                y1=0,
                x2=frame.width * self.scale,
                y2=frame.height * self.scale,
                offset=20.0 * self.scale,
                layer="DIMENSIONS"
            )
        )

        # Dimension labels
        self.texts.append(
            Text(
                x=(frame.width / 2) * self.scale,
                y=(frame.height + 30) * self.scale,
                text=f"{frame.width:.0f} mm",
                color=self.colors.dimensions,
                layer="DIMENSIONS"
            )
        )

        self.texts.append(
            Text(
                x=(frame.width + 30) * self.scale,
                y=(frame.height / 2) * self.scale,
                text=f"{frame.height:.0f} mm",
                rotation=90,
                color=self.colors.dimensions,
                layer="DIMENSIONS"
            )
        )

    def _calculate_bounds(self) -> None:
        """Calculate the bounding box of all geometry."""
        all_x = []
        all_y = []

        # Collect all coordinates
        for rect in self.rectangles:
            all_x.extend([rect.x, rect.x + rect.width])
            all_y.extend([rect.y, rect.y + rect.height])

        for line in self.lines:
            all_x.extend([line.x1, line.x2])
            all_y.extend([line.y1, line.y2])

        for dim in self.dimensions:
            all_x.extend([dim.x1, dim.x2])
            all_y.extend([dim.y1, dim.y2])
            # Add offset for dimension lines
            offset = dim.offset
            all_y.append(max(dim.y1, dim.y2) + offset)

        for text in self.texts:
            all_x.append(text.x)
            all_y.append(text.y)

        if all_x and all_y:
            self.bounds_min = Point(min(all_x), min(all_y))
            self.bounds_max = Point(max(all_x), max(all_y))

    def get_bounds(self) -> Tuple[Point, Point]:
        """Get the bounding box of all geometry.

        Returns:
            Tuple of (min_point, max_point)
        """
        if self.bounds_min is None or self.bounds_max is None:
            self._calculate_bounds()
        return self.bounds_min, self.bounds_max

    def get_layers(self) -> List[str]:
        """Get all unique layer names used in the geometry.

        Returns:
            Sorted list of layer names
        """
        layers = set()
        for rect in self.rectangles:
            layers.add(rect.layer)
        for line in self.lines:
            layers.add(line.layer)
        for text in self.texts:
            layers.add(text.layer)
        for dim in self.dimensions:
            layers.add(dim.layer)
        return sorted(list(layers))

    def get_geometry_summary(self) -> dict:
        """Get a summary of generated geometry.

        Returns:
            Dictionary with geometry counts
        """
        return {
            "rectangles": len(self.rectangles),
            "lines": len(self.lines),
            "texts": len(self.texts),
            "dimensions": len(self.dimensions),
            "layers": self.get_layers(),
            "bounds": self.get_bounds() if self.bounds_min else None
        }
