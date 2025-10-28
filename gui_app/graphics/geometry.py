"""Coordinate system, offsets, and unit conversion utilities.

This module provides coordinate transformation utilities for technical drawing
generation, ensuring consistent placement and scaling across all export formats.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


# Unit conversion constants
MM_TO_INCHES = 0.0393701
INCHES_TO_MM = 25.4
MM_TO_POINTS = 2.83465  # PostScript points (1/72 inch)


@dataclass
class Point2D:
    """2D point in millimeters."""
    x: float
    y: float

    def __add__(self, other: Point2D) -> Point2D:
        """Add two points (vector addition)."""
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        """Subtract two points (vector subtraction)."""
        return Point2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point2D:
        """Multiply point by scalar."""
        return Point2D(self.x * scalar, self.y * scalar)

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple format."""
        return (self.x, self.y)

    def to_inches(self) -> Tuple[float, float]:
        """Convert to inches."""
        return (self.x * MM_TO_INCHES, self.y * MM_TO_INCHES)


@dataclass
class BoundingBox:
    """Bounding box in 2D space."""
    min_point: Point2D
    max_point: Point2D

    @property
    def width(self) -> float:
        """Get width of bounding box."""
        return self.max_point.x - self.min_point.x

    @property
    def height(self) -> float:
        """Get height of bounding box."""
        return self.max_point.y - self.min_point.y

    @property
    def center(self) -> Point2D:
        """Get center point of bounding box."""
        return Point2D(
            (self.min_point.x + self.max_point.x) / 2,
            (self.min_point.y + self.max_point.y) / 2
        )

    def expand(self, margin: float) -> BoundingBox:
        """Expand bounding box by margin on all sides."""
        return BoundingBox(
            Point2D(self.min_point.x - margin, self.min_point.y - margin),
            Point2D(self.max_point.x + margin, self.max_point.y + margin)
        )


class CoordinateSystem:
    """Manages coordinate transformations for technical drawings.

    Uses bottom-left corner as origin (0, 0) with:
    - +X axis pointing right
    - +Y axis pointing up

    This matches standard CAD conventions.
    """

    def __init__(self, origin: Point2D = Point2D(0, 0)):
        """Initialize coordinate system.

        Args:
            origin: Origin point (default: 0, 0)
        """
        self.origin = origin

    def to_global(self, local: Point2D) -> Point2D:
        """Convert local coordinates to global coordinates.

        Args:
            local: Point in local coordinate system

        Returns:
            Point in global coordinate system
        """
        return Point2D(
            self.origin.x + local.x,
            self.origin.y + local.y
        )

    def to_local(self, global_point: Point2D) -> Point2D:
        """Convert global coordinates to local coordinates.

        Args:
            global_point: Point in global coordinate system

        Returns:
            Point in local coordinate system
        """
        return Point2D(
            global_point.x - self.origin.x,
            global_point.y - self.origin.y
        )

    def frame_coordinates(self, frame_width: float, frame_height: float) -> dict:
        """Calculate standard frame coordinates.

        Args:
            frame_width: Width of frame in mm
            frame_height: Height of frame in mm

        Returns:
            Dictionary with corner points
        """
        return {
            'bottom_left': self.origin,
            'bottom_right': Point2D(self.origin.x + frame_width, self.origin.y),
            'top_right': Point2D(self.origin.x + frame_width, self.origin.y + frame_height),
            'top_left': Point2D(self.origin.x, self.origin.y + frame_height)
        }

    def sash_coordinates(
        self,
        frame_width: float,
        sash_width: float,
        sash_height: float,
        is_top_sash: bool,
        frame_height: float
    ) -> dict:
        """Calculate sash coordinates within frame.

        Args:
            frame_width: Width of frame
            sash_width: Width of sash
            sash_height: Height of sash
            is_top_sash: True if top sash, False if bottom
            frame_height: Total frame height

        Returns:
            Dictionary with sash corner points
        """
        # Center sash horizontally in frame
        x_offset = (frame_width - sash_width) / 2

        if is_top_sash:
            # Top sash positioned at top of frame
            y_offset = frame_height - sash_height
        else:
            # Bottom sash positioned at bottom
            y_offset = 0

        origin = Point2D(x_offset, y_offset)

        return {
            'bottom_left': origin,
            'bottom_right': Point2D(origin.x + sash_width, origin.y),
            'top_right': Point2D(origin.x + sash_width, origin.y + sash_height),
            'top_left': Point2D(origin.x, origin.y + sash_height),
            'origin': origin
        }

    def glass_coordinates(
        self,
        sash_coords: dict,
        glass_width: float,
        glass_height: float
    ) -> dict:
        """Calculate glass coordinates within sash.

        Args:
            sash_coords: Sash coordinates from sash_coordinates()
            glass_width: Width of glass panel
            glass_height: Height of glass panel

        Returns:
            Dictionary with glass corner points
        """
        sash_origin = sash_coords['origin']
        sash_width = sash_coords['top_right'].x - sash_coords['bottom_left'].x
        sash_height = sash_coords['top_right'].y - sash_coords['bottom_left'].y

        # Center glass in sash
        x_offset = (sash_width - glass_width) / 2
        y_offset = (sash_height - glass_height) / 2

        origin = Point2D(
            sash_origin.x + x_offset,
            sash_origin.y + y_offset
        )

        return {
            'bottom_left': origin,
            'bottom_right': Point2D(origin.x + glass_width, origin.y),
            'top_right': Point2D(origin.x + glass_width, origin.y + glass_height),
            'top_left': Point2D(origin.x, origin.y + glass_height),
            'origin': origin
        }

    def calculate_bounding_box(
        self,
        frame_width: float,
        frame_height: float,
        margin: float = 50.0
    ) -> BoundingBox:
        """Calculate bounding box for entire drawing.

        Args:
            frame_width: Frame width in mm
            frame_height: Frame height in mm
            margin: Margin around frame in mm

        Returns:
            BoundingBox object
        """
        return BoundingBox(
            Point2D(self.origin.x - margin, self.origin.y - margin),
            Point2D(
                self.origin.x + frame_width + margin,
                self.origin.y + frame_height + margin
            )
        )


def mm_to_inches(mm: float) -> float:
    """Convert millimeters to inches.

    Args:
        mm: Value in millimeters

    Returns:
        Value in inches
    """
    return mm * MM_TO_INCHES


def inches_to_mm(inches: float) -> float:
    """Convert inches to millimeters.

    Args:
        inches: Value in inches

    Returns:
        Value in millimeters
    """
    return inches * INCHES_TO_MM


def mm_to_points(mm: float) -> float:
    """Convert millimeters to PostScript points.

    Args:
        mm: Value in millimeters

    Returns:
        Value in points
    """
    return mm * MM_TO_POINTS


def points_to_mm(points: float) -> float:
    """Convert PostScript points to millimeters.

    Args:
        points: Value in points

    Returns:
        Value in millimeters
    """
    return points / MM_TO_POINTS
