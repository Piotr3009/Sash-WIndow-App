"""Smoke tests for graphics module.

This module tests the basic functionality of the CAD export system,
ensuring that scenes can be built and exported to DXF and SVG formats.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from gui_app.backend.calculations import assemble_window
from gui_app.graphics.scene import build_scene
from gui_app.graphics.export_dxf import DXFExporter
from gui_app.graphics.export_svg import SVGExporter
from gui_app.graphics.geometry import Point2D, BoundingBox, CoordinateSystem
from gui_app.graphics.layers import get_all_layers, get_dxf_color, get_svg_stroke_width


@pytest.fixture
def sample_window():
    """Create a sample window for testing."""
    window = assemble_window(
        window_id="test_001",
        name="Test Window",
        frame_width=1200.0,
        frame_height=1600.0,
        vertical_bars=2,
        horizontal_bars=2,
        paint_color="White",
        hardware_finish="Chrome"
    )
    return window


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestGeometry:
    """Test geometry primitives."""

    def test_point2d_creation(self):
        """Test Point2D creation and properties."""
        point = Point2D(10.0, 20.0)
        assert point.x == 10.0
        assert point.y == 20.0
        assert point.to_tuple() == (10.0, 20.0)

    def test_point2d_distance(self):
        """Test distance calculation between points."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        assert p1.distance_to(p2) == 5.0

    def test_bounding_box(self):
        """Test BoundingBox creation and properties."""
        bbox = BoundingBox(
            min_point=Point2D(0.0, 0.0),
            max_point=Point2D(100.0, 200.0)
        )
        assert bbox.width == 100.0
        assert bbox.height == 200.0
        assert bbox.center.x == 50.0
        assert bbox.center.y == 100.0

    def test_coordinate_system(self):
        """Test CoordinateSystem basic operations."""
        coord_sys = CoordinateSystem(Point2D(0.0, 0.0))
        frame_coords = coord_sys.frame_coordinates(1200.0, 1600.0)

        assert 'bottom_left' in frame_coords
        assert 'top_right' in frame_coords
        assert frame_coords['bottom_left'] == Point2D(0.0, 0.0)
        assert frame_coords['top_right'] == Point2D(1200.0, 1600.0)


class TestLayers:
    """Test layer system."""

    def test_all_layers_defined(self):
        """Test that all 9 layers are defined."""
        layers = get_all_layers()
        assert len(layers) == 9
        expected_layers = [
            'FRAME', 'SASH_TOP', 'SASH_BOTTOM', 'GLASS',
            'BARS_V', 'BARS_H', 'DIMENSIONS', 'CENTERLINES', 'ANNOTATIONS'
        ]
        for layer in expected_layers:
            assert layer in layers

    def test_dxf_colors(self):
        """Test that DXF colors are assigned correctly."""
        # Test exact color codes per user specification
        assert get_dxf_color('FRAME') == 7
        assert get_dxf_color('SASH_TOP') == 3
        assert get_dxf_color('SASH_BOTTOM') == 5
        assert get_dxf_color('GLASS') == 4
        assert get_dxf_color('BARS_V') == 1
        assert get_dxf_color('BARS_H') == 2
        assert get_dxf_color('DIMENSIONS') == 8
        assert get_dxf_color('CENTERLINES') == 9
        assert get_dxf_color('ANNOTATIONS') == 6

    def test_svg_stroke_widths(self):
        """Test that SVG stroke widths are defined."""
        assert get_svg_stroke_width('FRAME') == 0.50
        assert get_svg_stroke_width('DIMENSIONS') == 0.18


class TestSceneBuilder:
    """Test scene building functionality."""

    def test_build_scene_basic(self, sample_window):
        """Test basic scene building."""
        scene = build_scene(sample_window, include_dimensions=True)

        # Check scene structure
        assert 'metadata' in scene
        assert 'layers' in scene
        assert 'bounds' in scene
        assert 'coordinate_system' in scene

        # Check metadata
        metadata = scene['metadata']
        assert metadata['window_id'] == 'test_001'
        assert metadata['window_name'] == 'Test Window'
        assert metadata['frame_width'] == 1200.0
        assert metadata['frame_height'] == 1600.0
        assert metadata['units'] == 'millimeters'

        # Check layers
        assert len(scene['layers']) == 9
        for layer in get_all_layers():
            assert layer in scene['layers']

    def test_build_scene_frame_geometry(self, sample_window):
        """Test that frame geometry is created."""
        scene = build_scene(sample_window, include_dimensions=False)

        frame_layer = scene['layers']['FRAME']
        assert len(frame_layer) > 0

        # Check first geometry is a polyline
        frame_geom = frame_layer[0]
        assert frame_geom['type'] == 'polyline'
        assert len(frame_geom['points']) == 5  # Rectangle with closed path

    def test_build_scene_with_bars(self, sample_window):
        """Test that glazing bars are created."""
        scene = build_scene(sample_window, include_dimensions=False)

        # Check vertical bars (should have 2)
        bars_v = scene['layers']['BARS_V']
        assert len(bars_v) == 2

        # Check horizontal bars (should have 2)
        bars_h = scene['layers']['BARS_H']
        assert len(bars_h) == 2

    def test_build_scene_with_dimensions(self, sample_window):
        """Test that dimensions are created."""
        scene = build_scene(sample_window, include_dimensions=True)

        dimensions_layer = scene['layers']['DIMENSIONS']
        assert len(dimensions_layer) > 0

        # Should have at least frame dimensions and glass dimensions
        assert len(dimensions_layer) >= 4  # H+V frame, H+V glass

    def test_build_scene_centerlines(self, sample_window):
        """Test that centerlines are created."""
        scene = build_scene(sample_window, include_dimensions=False)

        centerlines = scene['layers']['CENTERLINES']
        assert len(centerlines) == 2  # Vertical and horizontal

        # Both should be lines
        for line in centerlines:
            assert line['type'] == 'line'

    def test_build_scene_annotations(self, sample_window):
        """Test that annotations are created."""
        scene = build_scene(sample_window, include_dimensions=False)

        annotations = scene['layers']['ANNOTATIONS']
        assert len(annotations) > 0

        # At least title and metadata
        text_items = [a for a in annotations if a['type'] == 'text']
        assert len(text_items) >= 1


class TestDXFExport:
    """Test DXF export functionality."""

    def test_dxf_exporter_creation(self, temp_output_dir):
        """Test DXF exporter can be created."""
        exporter = DXFExporter(output_dir=temp_output_dir)
        assert exporter is not None
        assert exporter.file_extension == ".dxf"

    def test_dxf_export_from_scene(self, sample_window, temp_output_dir):
        """Test DXF export from scene - smoke test."""
        scene = build_scene(sample_window, include_dimensions=True)
        exporter = DXFExporter(output_dir=temp_output_dir)

        # Export scene
        dxf_path = exporter.export_from_scene(scene)

        # Verify file exists
        assert Path(dxf_path).exists()

        # Verify file size > 1 KB (per user requirement)
        file_size = Path(dxf_path).stat().st_size
        assert file_size > 1024, f"DXF file too small: {file_size} bytes"

        # Verify it's a valid DXF by checking header
        with open(dxf_path, 'r') as f:
            content = f.read(100)
            assert '0' in content  # DXF files start with section markers
            assert 'SECTION' in content


class TestSVGExport:
    """Test SVG export functionality."""

    def test_svg_exporter_creation(self, temp_output_dir):
        """Test SVG exporter can be created."""
        exporter = SVGExporter(output_dir=temp_output_dir)
        assert exporter is not None
        assert exporter.file_extension == ".svg"

    def test_svg_export_from_scene(self, sample_window, temp_output_dir):
        """Test SVG export from scene - smoke test."""
        scene = build_scene(sample_window, include_dimensions=True)
        exporter = SVGExporter(output_dir=temp_output_dir)

        # Export scene
        svg_path = exporter.export_from_scene(scene)

        # Verify file exists
        assert Path(svg_path).exists()

        # Verify file size > 1 KB (per user requirement)
        file_size = Path(svg_path).stat().st_size
        assert file_size > 1024, f"SVG file too small: {file_size} bytes"

        # Verify it's a valid SVG by checking header
        with open(svg_path, 'r') as f:
            content = f.read(200)
            assert '<?xml' in content
            assert '<svg' in content
            assert 'xmlns' in content

    def test_svg_contains_layers(self, sample_window, temp_output_dir):
        """Test that SVG contains layer groups."""
        scene = build_scene(sample_window, include_dimensions=True)
        exporter = SVGExporter(output_dir=temp_output_dir)
        svg_path = exporter.export_from_scene(scene)

        with open(svg_path, 'r') as f:
            content = f.read()

            # Check for layer groups
            assert 'layer-frame' in content.lower()
            assert 'layer-dimensions' in content.lower()


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow_dxf_and_svg(self, sample_window, temp_output_dir):
        """Test complete workflow: build scene → export DXF + SVG."""
        # Build scene
        scene = build_scene(sample_window, include_dimensions=True)
        assert scene is not None

        # Export DXF
        dxf_exporter = DXFExporter(output_dir=temp_output_dir)
        dxf_path = dxf_exporter.export_from_scene(scene)
        assert Path(dxf_path).exists()

        # Export SVG
        svg_exporter = SVGExporter(output_dir=temp_output_dir)
        svg_path = svg_exporter.export_from_scene(scene)
        assert Path(svg_path).exists()

        # Both files should be valid and > 1 KB
        assert Path(dxf_path).stat().st_size > 1024
        assert Path(svg_path).stat().st_size > 1024

    def test_multiple_windows_export(self, temp_output_dir):
        """Test exporting multiple windows."""
        windows = [
            assemble_window(
                window_id=f"test_{i:03d}",
                name=f"Window {i}",
                frame_width=1000.0 + i * 100,
                frame_height=1400.0 + i * 100,
                vertical_bars=i % 3,
                horizontal_bars=i % 3,
                paint_color="White",
                hardware_finish="Chrome"
            )
            for i in range(3)
        ]

        exporter = DXFExporter(output_dir=temp_output_dir)

        for window in windows:
            scene = build_scene(window)
            dxf_path = exporter.export_from_scene(scene)
            assert Path(dxf_path).exists()
            assert Path(dxf_path).stat().st_size > 1024
