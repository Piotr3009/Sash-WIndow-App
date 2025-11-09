"""Utility helpers for API serialization."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict

from app.graphics.geometry import BoundingBox, CoordinateSystem, Point2D
from app.graphics.renderer import WindowRenderer


def serialize_point(point: Point2D | dict | Any) -> Dict[str, float] | Any:
    """Convert a :class:`Point2D` into a JSON serialisable dictionary."""

    if isinstance(point, Point2D):
        return {"x": point.x, "y": point.y}
    if is_dataclass(point):  # Fallback for dataclass-based points
        return asdict(point)
    return point


def serialize_bounds(bounds: BoundingBox | None) -> Dict[str, Any] | None:
    """Convert :class:`BoundingBox` into JSON serialisable format."""

    if bounds is None:
        return None
    return {
        "min": serialize_point(bounds.min_point),
        "max": serialize_point(bounds.max_point),
        "width": bounds.width,
        "height": bounds.height,
        "center": serialize_point(bounds.center),
    }


def serialize_coordinate_system(system: CoordinateSystem | None) -> Dict[str, Any] | None:
    """Serialize coordinate system metadata."""

    if system is None:
        return None
    return {"origin": serialize_point(system.origin)}


def normalize_scene(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert scene dictionaries to JSON serialisable objects."""

    def _convert(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: _convert(val) for key, val in value.items() if not key.startswith("_")}
        if isinstance(value, list):
            return [_convert(item) for item in value]
        if isinstance(value, Point2D):
            return serialize_point(value)
        if isinstance(value, BoundingBox):
            return serialize_bounds(value)
        if isinstance(value, CoordinateSystem):
            return serialize_coordinate_system(value)
        if is_dataclass(value):
            return _convert(asdict(value))
        return value

    converted = _convert(scene)
    converted["bounds"] = serialize_bounds(scene.get("bounds"))
    converted["coordinate_system"] = serialize_coordinate_system(scene.get("coordinate_system"))
    return converted


def serialize_renderer(renderer: WindowRenderer) -> Dict[str, Any]:
    """Convert renderer primitives into JSON serialisable payload."""

    from dataclasses import asdict as dc_asdict  # Local import to avoid circular

    renderer.generate_geometry()

    rectangles = [dc_asdict(rect) for rect in renderer.rectangles]
    lines = [dc_asdict(line) for line in renderer.lines]
    texts = [dc_asdict(text) for text in renderer.texts]
    dimensions = [dc_asdict(dimension) for dimension in renderer.dimensions]

    bounds = None
    if renderer.bounds_min and renderer.bounds_max:
        bounds = {
            "min": dc_asdict(renderer.bounds_min),
            "max": dc_asdict(renderer.bounds_max),
        }

    summary = {
        "rectangles": len(rectangles),
        "lines": len(lines),
        "texts": len(texts),
        "dimensions": len(dimensions),
        "layers": renderer.get_layers(),
        "bounds": bounds,
    }

    return {
        "rectangles": rectangles,
        "lines": lines,
        "texts": texts,
        "dimensions": dimensions,
        "summary": summary,
    }
