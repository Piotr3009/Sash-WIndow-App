"""Tests for the graphics renderer module."""

import pytest
from gui_app.backend.models import Window, Frame, Sash, Glass, Bars
from gui_app.graphics.renderer import WindowRenderer, ColorScheme, Point


def create_test_window() -> Window:
    """Create a test window fixture."""
    frame = Frame(
        width=1200.0,
        height=1600.0,
        jambs_length=1494.0,
        head_length=1200.0,
        cill_length=1200.0,
        ext_head_liner=996.0,
        int_head_liner=1030.0
    )

    sash_top = Sash(
        width=1022.0,
        height=780.0,
        height_with_horn=850.0,
        stiles_length=780.0,
        top_rail_length=1022.0,
        bottom_rail_length=1022.0,
        meet_rail_length=1022.0
    )

    sash_bottom = Sash(
        width=1022.0,
        height=780.0,
        height_with_horn=780.0,
        stiles_length=780.0,
        top_rail_length=1022.0,
        bottom_rail_length=1022.0,
        meet_rail_length=1022.0
    )

    glass = Glass(
        width=932.0,
        height=704.0,
        type="24mm TGH/ARG/TGH",
        frosted=False,
        toughened=True,
        spacer_color="Black",
        pcs=2
    )

    bars = Bars(
        layout_type="3x3",
        vertical_bars=3,
        horizontal_bars=3,
        spacing_vertical=[255.5, 255.5, 255.5],
        spacing_horizontal=[195.0, 195.0, 195.0]
    )

    window = Window(
        id="test-window-1",
        name="Test Window",
        frame=frame,
        sash_top=sash_top,
        sash_bottom=sash_bottom,
        glass=glass,
        bars=bars,
        paint_color="White",
        hardware_finish="Brass",
        trickle_vent="Concealed",
        sash_catches="PAS24",
        cill_extension=60
    )

    return window


def test_renderer_initialization():
    """Test renderer initialization."""
    window = create_test_window()
    renderer = WindowRenderer(window)

    assert renderer.window == window
    assert isinstance(renderer.colors, ColorScheme)
    assert renderer.scale == 1.0
    assert len(renderer.rectangles) == 0
    assert len(renderer.lines) == 0


def test_geometry_generation():
    """Test geometry generation."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry()

    # Should have rectangles for frame, sashes, and glass
    assert len(renderer.rectangles) > 0
    # Should have lines for bars and meeting rails
    assert len(renderer.lines) > 0
    # Should have dimension texts
    assert len(renderer.texts) > 0
    # Should have dimension lines
    assert len(renderer.dimensions) > 0


def test_geometry_layers():
    """Test that geometry is properly layered."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry()

    layers = renderer.get_layers()
    expected_layers = ["FRAME", "SASH_TOP", "SASH_BOTTOM", "GLASS", "BARS", "DIMENSIONS", "TEXT"]

    for layer in expected_layers:
        assert layer in layers, f"Expected layer {layer} not found"


def test_bounds_calculation():
    """Test bounding box calculation."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry()

    bounds_min, bounds_max = renderer.get_bounds()

    assert isinstance(bounds_min, Point)
    assert isinstance(bounds_max, Point)
    assert bounds_max.x > bounds_min.x
    assert bounds_max.y > bounds_min.y


def test_geometry_without_bars():
    """Test geometry generation without bars."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry(include_bars=False)

    # Should have no bar geometry
    bar_lines = [line for line in renderer.lines if line.layer == "BARS"]
    assert len(bar_lines) == 0


def test_geometry_without_dimensions():
    """Test geometry generation without dimensions."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry(include_dimensions=False)

    # Should have no dimension geometry
    assert len(renderer.dimensions) == 0


def test_custom_color_scheme():
    """Test renderer with custom color scheme."""
    window = create_test_window()
    custom_colors = ColorScheme(
        frame="#FF0000",
        sash="#00FF00",
        glass="#0000FF"
    )
    renderer = WindowRenderer(window, custom_colors)

    assert renderer.colors.frame == "#FF0000"
    assert renderer.colors.sash == "#00FF00"
    assert renderer.colors.glass == "#0000FF"


def test_geometry_summary():
    """Test geometry summary generation."""
    window = create_test_window()
    renderer = WindowRenderer(window)
    renderer.generate_geometry()

    summary = renderer.get_geometry_summary()

    assert "rectangles" in summary
    assert "lines" in summary
    assert "texts" in summary
    assert "dimensions" in summary
    assert "layers" in summary
    assert summary["rectangles"] > 0
