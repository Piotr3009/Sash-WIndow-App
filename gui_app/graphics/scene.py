"""Scene building for technical drawings.

This module provides the build_scene() function that converts Window data models
into a complete scene dictionary ready for export to DXF, SVG, or other formats.
"""

from __future__ import annotations

from typing import Dict, List, Any
from datetime import datetime, timezone

from ..backend.models import Window
from .geometry import CoordinateSystem, Point2D
from .layers import LayerName, get_all_layers
from .dimensioning import DimensionBuilder


def build_scene(window: Window, include_dimensions: bool = True) -> Dict[str, Any]:
    """Build a complete drawing scene from a Window object.

    This is the main entry point for converting window data into a renderable scene.
    The scene dictionary contains all geometric primitives organized by layer.

    Args:
        window: Window object from backend.models
        include_dimensions: Whether to include dimension lines

    Returns:
        Dictionary containing:
            - 'metadata': Project and window information
            - 'layers': Dictionary of layer names to geometry lists
            - 'bounds': Bounding box information
            - 'coordinate_system': CoordinateSystem object

    Example:
        >>> scene = build_scene(window)
        >>> export_dxf(scene, "output/cad/window.dxf")
        >>> export_svg(scene, "output/cad/window.svg")
    """
    # Initialize coordinate system (origin at bottom-left)
    coord_sys = CoordinateSystem(Point2D(0, 0))

    # Initialize scene structure
    scene: Dict[str, Any] = {
        'metadata': {
            'window_id': window.id,
            'window_name': window.name,
            'frame_width': window.frame.width,
            'frame_height': window.frame.height,
            'paint_color': window.paint_color,
            'hardware_finish': window.hardware_finish,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'units': 'millimeters'
        },
        'layers': {layer: [] for layer in get_all_layers()},
        'coordinate_system': coord_sys,
        'bounds': None
    }

    # Build geometry for each component
    _add_frame_geometry(scene, window, coord_sys)
    _add_sash_geometry(scene, window, coord_sys)
    _add_glass_geometry(scene, window, coord_sys)
    _add_bars_geometry(scene, window, coord_sys)
    _add_centerlines(scene, window, coord_sys)

    if include_dimensions:
        _add_dimensions(scene, window, coord_sys)

    _add_annotations(scene, window, coord_sys)

    # Calculate bounding box
    scene['bounds'] = coord_sys.calculate_bounding_box(
        window.frame.width,
        window.frame.height,
        margin=50.0
    )

    return scene


def _add_frame_geometry(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add frame geometry to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    frame_coords = coord_sys.frame_coordinates(
        window.frame.width,
        window.frame.height
    )

    # Frame rectangle
    scene['layers'][LayerName.FRAME].append({
        'type': 'polyline',
        'points': [
            frame_coords['bottom_left'],
            frame_coords['bottom_right'],
            frame_coords['top_right'],
            frame_coords['top_left'],
            frame_coords['bottom_left']  # Close the polyline
        ],
        'closed': True
    })


def _add_sash_geometry(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add sash geometry to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    # Top sash
    top_sash_coords = coord_sys.sash_coordinates(
        window.frame.width,
        window.sash_top.width,
        window.sash_top.height,
        is_top_sash=True,
        frame_height=window.frame.height
    )

    scene['layers'][LayerName.SASH_TOP].append({
        'type': 'polyline',
        'points': [
            top_sash_coords['bottom_left'],
            top_sash_coords['bottom_right'],
            top_sash_coords['top_right'],
            top_sash_coords['top_left'],
            top_sash_coords['bottom_left']
        ],
        'closed': True
    })

    # Bottom sash
    bottom_sash_coords = coord_sys.sash_coordinates(
        window.frame.width,
        window.sash_bottom.width,
        window.sash_bottom.height,
        is_top_sash=False,
        frame_height=window.frame.height
    )

    scene['layers'][LayerName.SASH_BOTTOM].append({
        'type': 'polyline',
        'points': [
            bottom_sash_coords['bottom_left'],
            bottom_sash_coords['bottom_right'],
            bottom_sash_coords['top_right'],
            bottom_sash_coords['top_left'],
            bottom_sash_coords['bottom_left']
        ],
        'closed': True
    })

    # Store sash coords for use by other functions
    scene['_sash_coords'] = {
        'top': top_sash_coords,
        'bottom': bottom_sash_coords
    }


def _add_glass_geometry(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add glass geometry to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    # Use bottom sash for glass calculation
    bottom_sash_coords = scene['_sash_coords']['bottom']

    glass_coords = coord_sys.glass_coordinates(
        bottom_sash_coords,
        window.glass.width,
        window.glass.height
    )

    scene['layers'][LayerName.GLASS].append({
        'type': 'polyline',
        'points': [
            glass_coords['bottom_left'],
            glass_coords['bottom_right'],
            glass_coords['top_right'],
            glass_coords['top_left'],
            glass_coords['bottom_left']
        ],
        'closed': True
    })

    # Store glass coords for use by bars
    scene['_glass_coords'] = glass_coords


def _add_bars_geometry(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add glazing bar geometry to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    if window.bars.vertical_bars == 0 and window.bars.horizontal_bars == 0:
        return

    glass_coords = scene['_glass_coords']
    glass_left = glass_coords['bottom_left'].x
    glass_right = glass_coords['bottom_right'].x
    glass_bottom = glass_coords['bottom_left'].y
    glass_top = glass_coords['top_left'].y
    glass_width = glass_right - glass_left
    glass_height = glass_top - glass_bottom

    # Vertical bars
    if window.bars.vertical_bars > 0:
        spacing = glass_width / (window.bars.vertical_bars + 1)
        for i in range(1, window.bars.vertical_bars + 1):
            x = glass_left + i * spacing
            scene['layers'][LayerName.BARS_V].append({
                'type': 'line',
                'start': Point2D(x, glass_bottom),
                'end': Point2D(x, glass_top)
            })

    # Horizontal bars
    if window.bars.horizontal_bars > 0:
        spacing = glass_height / (window.bars.horizontal_bars + 1)
        for i in range(1, window.bars.horizontal_bars + 1):
            y = glass_bottom + i * spacing
            scene['layers'][LayerName.BARS_H].append({
                'type': 'line',
                'start': Point2D(glass_left, y),
                'end': Point2D(glass_right, y)
            })


def _add_centerlines(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add centerlines to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    frame_w = window.frame.width
    frame_h = window.frame.height

    # Vertical centerline
    scene['layers'][LayerName.CENTERLINES].append({
        'type': 'line',
        'start': Point2D(frame_w / 2, 0),
        'end': Point2D(frame_w / 2, frame_h)
    })

    # Horizontal centerline
    scene['layers'][LayerName.CENTERLINES].append({
        'type': 'line',
        'start': Point2D(0, frame_h / 2),
        'end': Point2D(frame_w, frame_h / 2)
    })


def _add_dimensions(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add dimension lines to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    dim_builder = DimensionBuilder()

    frame_w = window.frame.width
    frame_h = window.frame.height

    # Frame width dimension (bottom)
    dim_h = dim_builder.create_horizontal_dimension(
        start_x=0,
        end_x=frame_w,
        y=0,
        offset=-15.0,  # Below frame
        precision=0
    )
    scene['layers'][LayerName.DIMENSIONS].append({
        'type': 'dimension_horizontal',
        'data': dim_h
    })

    # Frame height dimension (right side)
    dim_v = dim_builder.create_vertical_dimension(
        start_y=0,
        end_y=frame_h,
        x=frame_w,
        offset=15.0,  # To the right
        precision=0
    )
    scene['layers'][LayerName.DIMENSIONS].append({
        'type': 'dimension_vertical',
        'data': dim_v
    })

    # Glass dimensions (if needed)
    if scene.get('_glass_coords'):
        glass_coords = scene['_glass_coords']
        glass_width = glass_coords['bottom_right'].x - glass_coords['bottom_left'].x
        glass_height = glass_coords['top_left'].y - glass_coords['bottom_left'].y

        # Glass width dimension
        dim_glass_w = dim_builder.create_horizontal_dimension(
            start_x=glass_coords['bottom_left'].x,
            end_x=glass_coords['bottom_right'].x,
            y=glass_coords['bottom_left'].y,
            offset=-10.0,
            precision=0,
            text_override=f"Glass {glass_width:.0f}"
        )
        scene['layers'][LayerName.DIMENSIONS].append({
            'type': 'dimension_horizontal',
            'data': dim_glass_w
        })


def _add_annotations(
    scene: Dict[str, Any],
    window: Window,
    coord_sys: CoordinateSystem
) -> None:
    """Add text annotations to scene.

    Args:
        scene: Scene dictionary to modify
        window: Window object
        coord_sys: Coordinate system
    """
    # Title annotation
    scene['layers'][LayerName.ANNOTATIONS].append({
        'type': 'text',
        'position': Point2D(window.frame.width / 2, window.frame.height + 20),
        'text': window.name,
        'height': 5.0,
        'alignment': 'center'
    })

    # Metadata annotations
    metadata_y = window.frame.height + 10
    annotations = [
        f"Width: {window.frame.width:.0f} mm",
        f"Height: {window.frame.height:.0f} mm",
        f"Paint: {window.paint_color}",
        f"Hardware: {window.hardware_finish}"
    ]

    x_offset = 10
    for annotation in annotations:
        scene['layers'][LayerName.ANNOTATIONS].append({
            'type': 'text',
            'position': Point2D(x_offset, metadata_y),
            'text': annotation,
            'height': 3.0,
            'alignment': 'left'
        })
        metadata_y -= 5
