"""2D drawing utilities for sash windows using matplotlib."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt

from .models import Window


def _ensure_output_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def draw_window(window: Window, export_dir: str = "output") -> str:
    """Create a simple technical drawing for the provided window."""

    output_dir = _ensure_output_dir(export_dir)
    file_path = output_dir / f"{window.name.replace(' ', '_').lower()}_drawing.png"

    frame = window.frame
    sash_top = window.sash_top
    sash_bottom = window.sash_bottom
    glass = window.glass
    bars = window.bars

    fig, ax = plt.subplots(figsize=(6, 9))
    ax.set_title(f"{window.name} - Technical Drawing")
    ax.set_xlim(0, frame.width)
    ax.set_ylim(0, frame.height)

    # Frame outline
    ax.add_patch(plt.Rectangle((0, 0), frame.width, frame.height, fill=False, linewidth=2))

    sash_offset_x = (frame.width - sash_bottom.width) / 2

    # Top sash
    ax.add_patch(
        plt.Rectangle(
            (sash_offset_x, frame.height - sash_top.height),
            sash_top.width,
            sash_top.height,
            fill=False,
            linewidth=1.5,
        )
    )
    # Bottom sash
    ax.add_patch(
        plt.Rectangle(
            (sash_offset_x, 0),
            sash_bottom.width,
            sash_bottom.height,
            fill=False,
            linewidth=1.5,
        )
    )

    # Glass area (bottom sash used as reference)
    glass_offset_x = sash_offset_x + (sash_bottom.width - glass.width) / 2
    glass_offset_y = (sash_bottom.height - glass.height) / 2
    ax.add_patch(plt.Rectangle((glass_offset_x, glass_offset_y), glass.width, glass.height, fill=False, linestyle='--'))

    # Bars
    for index in range(1, bars.vertical_bars + 1):
        x = sash_offset_x + index * (sash_bottom.width / (bars.vertical_bars + 1))
        ax.plot([x, x], [0, sash_bottom.height], color='grey', linestyle=':')
    for index in range(1, bars.horizontal_bars + 1):
        y = index * (sash_bottom.height / (bars.horizontal_bars + 1))
        ax.plot([sash_offset_x, sash_offset_x + sash_bottom.width], [y, y], color='grey', linestyle=':')

    ax.text(frame.width / 2, frame.height + 20, f"Frame Width: {frame.width} mm", ha='center')
    ax.text(frame.width + 20, frame.height / 2, f"Frame Height: {frame.height} mm", rotation=90, va='center')

    ax.axis('off')
    plt.tight_layout()
    fig.savefig(file_path, dpi=200)
    plt.close(fig)
    return str(file_path)
