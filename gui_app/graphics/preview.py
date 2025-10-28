"""SVG preview rendering using cairosvg.

This module provides optional SVG→PNG conversion for preview purposes.
Falls back gracefully if cairosvg is not installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import warnings


# Try to import cairosvg
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    cairosvg = None


def is_preview_available() -> bool:
    """Check if SVG preview rendering is available.

    Returns:
        True if cairosvg is installed and preview is available
    """
    return CAIROSVG_AVAILABLE


def render_preview_svg(
    svg_path: str,
    png_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    dpi: int = 96
) -> Optional[str]:
    """Render SVG file to PNG preview image.

    Args:
        svg_path: Path to input SVG file
        png_path: Path to output PNG file
        width: Output width in pixels (None = auto from SVG)
        height: Output height in pixels (None = auto from SVG)
        dpi: DPI for rendering (default 96)

    Returns:
        Path to generated PNG file, or None if cairosvg not available

    Raises:
        FileNotFoundError: If SVG file doesn't exist
        RuntimeError: If rendering fails
    """
    if not CAIROSVG_AVAILABLE:
        warnings.warn(
            "cairosvg is not installed. SVG preview rendering is disabled. "
            "Install with: pip install cairosvg",
            UserWarning
        )
        return None

    svg_file = Path(svg_path)
    if not svg_file.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    png_file = Path(png_path)
    png_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Convert SVG to PNG
        cairosvg.svg2png(
            url=str(svg_file),
            write_to=str(png_file),
            output_width=width,
            output_height=height,
            dpi=dpi
        )
        return str(png_file)
    except Exception as exc:
        raise RuntimeError(f"Failed to render SVG preview: {exc}") from exc


def render_preview_from_data(
    svg_data: str,
    png_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    dpi: int = 96
) -> Optional[str]:
    """Render SVG data to PNG preview image.

    Args:
        svg_data: SVG content as string
        png_path: Path to output PNG file
        width: Output width in pixels (None = auto from SVG)
        height: Output height in pixels (None = auto from SVG)
        dpi: DPI for rendering (default 96)

    Returns:
        Path to generated PNG file, or None if cairosvg not available

    Raises:
        RuntimeError: If rendering fails
    """
    if not CAIROSVG_AVAILABLE:
        warnings.warn(
            "cairosvg is not installed. SVG preview rendering is disabled.",
            UserWarning
        )
        return None

    png_file = Path(png_path)
    png_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Convert SVG data to PNG
        cairosvg.svg2png(
            bytestring=svg_data.encode('utf-8'),
            write_to=str(png_file),
            output_width=width,
            output_height=height,
            dpi=dpi
        )
        return str(png_file)
    except Exception as exc:
        raise RuntimeError(f"Failed to render SVG preview: {exc}") from exc


def get_preview_size_from_svg(svg_path: str) -> tuple[Optional[float], Optional[float]]:
    """Extract width and height from SVG file.

    Args:
        svg_path: Path to SVG file

    Returns:
        Tuple of (width, height) in pixels, or (None, None) if not found
    """
    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Try to get width and height attributes
        width_str = root.get('width', '')
        height_str = root.get('height', '')

        # Remove units and convert to float
        width = float(width_str.rstrip('mmpxpt')) if width_str else None
        height = float(height_str.rstrip('mmpxpt')) if height_str else None

        return width, height
    except Exception:
        return None, None


def create_thumbnail(
    svg_path: str,
    thumbnail_path: str,
    max_size: int = 200
) -> Optional[str]:
    """Create a thumbnail preview of SVG file.

    Args:
        svg_path: Path to input SVG file
        thumbnail_path: Path to output thumbnail PNG
        max_size: Maximum dimension (width or height) in pixels

    Returns:
        Path to generated thumbnail, or None if preview not available
    """
    if not CAIROSVG_AVAILABLE:
        return None

    # Get original size
    orig_width, orig_height = get_preview_size_from_svg(svg_path)

    if orig_width and orig_height:
        # Calculate thumbnail size maintaining aspect ratio
        if orig_width > orig_height:
            width = max_size
            height = int(max_size * orig_height / orig_width)
        else:
            height = max_size
            width = int(max_size * orig_width / orig_height)
    else:
        # Use square if size unknown
        width = height = max_size

    return render_preview_svg(svg_path, thumbnail_path, width, height)


def batch_render_previews(
    svg_files: list[str],
    output_dir: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    dpi: int = 96
) -> dict[str, Optional[str]]:
    """Render multiple SVG files to PNG previews.

    Args:
        svg_files: List of SVG file paths
        output_dir: Output directory for PNG files
        width: Output width in pixels
        height: Output height in pixels
        dpi: DPI for rendering

    Returns:
        Dictionary mapping SVG paths to PNG paths (or None if failed)
    """
    if not CAIROSVG_AVAILABLE:
        warnings.warn("cairosvg not available, skipping preview generation")
        return {svg: None for svg in svg_files}

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}
    for svg_path in svg_files:
        try:
            svg_file = Path(svg_path)
            png_file = output_path / f"{svg_file.stem}.png"
            result = render_preview_svg(
                svg_path,
                str(png_file),
                width,
                height,
                dpi
            )
            results[svg_path] = result
        except Exception as exc:
            warnings.warn(f"Failed to render {svg_path}: {exc}")
            results[svg_path] = None

    return results


def get_installation_message() -> str:
    """Get message about installing cairosvg.

    Returns:
        Installation instruction message
    """
    return (
        "SVG preview rendering requires cairosvg.\n\n"
        "Install with:\n"
        "  pip install cairosvg\n\n"
        "Note: cairosvg requires Cairo library:\n"
        "  Ubuntu/Debian: sudo apt-get install libcairo2\n"
        "  macOS: brew install cairo\n"
        "  Windows: Download from https://www.cairographics.org/"
    )
