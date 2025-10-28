"""
Technical drawing generation using matplotlib
Creates 2D window diagrams as PNG files
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from models import Window


def draw_window(window: Window, output_path: str = None) -> str:
    """
    Generate technical drawing of a window

    Args:
        window: Window object to draw
        output_path: Optional output path (default: output/{window_name}_drawing.png)

    Returns:
        Path to created PNG file
    """
    if output_path is None:
        output_path = f"output/{window.name}_drawing.png"

    # Create figure with appropriate aspect ratio
    fig, ax = plt.subplots(figsize=(8, 12))

    # Frame dimensions (scaled for display)
    frame_width = window.frame.width
    frame_height = window.frame.height

    # Scale factor for display (normalize to typical size)
    scale = 1000 / max(frame_width, frame_height)
    display_width = frame_width * scale / 100
    display_height = frame_height * scale / 100

    # Set up the plot
    ax.set_xlim(0, display_width * 1.2)
    ax.set_ylim(0, display_height * 1.2)
    ax.set_aspect('equal')

    # Offset for centering
    offset_x = display_width * 0.1
    offset_y = display_height * 0.1

    # Draw outer frame
    frame_rect = patches.Rectangle(
        (offset_x, offset_y),
        display_width,
        display_height,
        linewidth=3,
        edgecolor='black',
        facecolor='wheat',
        label='Frame'
    )
    ax.add_patch(frame_rect)

    # Frame thickness (approximate)
    frame_thickness = 0.5

    # Calculate sash positions
    sash_width = window.sash_top.width * scale / 100
    sash_top_height = window.sash_top.height * scale / 100
    sash_bottom_height = window.sash_bottom.height * scale / 100

    # Position sashes (with frame gap)
    sash_x = offset_x + frame_thickness
    sash_bottom_y = offset_y + frame_thickness
    sash_top_y = sash_bottom_y + sash_bottom_height

    # Draw bottom sash
    bottom_sash_rect = patches.Rectangle(
        (sash_x, sash_bottom_y),
        sash_width,
        sash_bottom_height,
        linewidth=2,
        edgecolor='darkblue',
        facecolor='lightblue',
        alpha=0.7,
        label='Bottom Sash'
    )
    ax.add_patch(bottom_sash_rect)

    # Draw top sash
    top_sash_rect = patches.Rectangle(
        (sash_x, sash_top_y),
        sash_width,
        sash_top_height,
        linewidth=2,
        edgecolor='darkgreen',
        facecolor='lightgreen',
        alpha=0.7,
        label='Top Sash'
    )
    ax.add_patch(top_sash_rect)

    # Draw glass areas
    glass_margin = 0.3

    # Bottom glass
    bottom_glass_x = sash_x + glass_margin
    bottom_glass_y = sash_bottom_y + glass_margin
    bottom_glass_width = sash_width - 2 * glass_margin
    bottom_glass_height = sash_bottom_height - 2 * glass_margin

    bottom_glass = patches.Rectangle(
        (bottom_glass_x, bottom_glass_y),
        bottom_glass_width,
        bottom_glass_height,
        linewidth=1,
        edgecolor='gray',
        facecolor='lightcyan',
        alpha=0.5
    )
    ax.add_patch(bottom_glass)

    # Top glass
    top_glass_x = sash_x + glass_margin
    top_glass_y = sash_top_y + glass_margin
    top_glass_width = sash_width - 2 * glass_margin
    top_glass_height = sash_top_height - 2 * glass_margin

    top_glass = patches.Rectangle(
        (top_glass_x, top_glass_y),
        top_glass_width,
        top_glass_height,
        linewidth=1,
        edgecolor='gray',
        facecolor='lightcyan',
        alpha=0.5
    )
    ax.add_patch(top_glass)

    # Draw glazing bars if present
    if window.bars_top.layout_type != "None" and window.bars_top.vertical_bars > 0:
        draw_glazing_bars(
            ax,
            top_glass_x,
            top_glass_y,
            top_glass_width,
            top_glass_height,
            window.bars_top.vertical_bars,
            window.bars_top.horizontal_bars
        )

    if window.bars_bottom.layout_type != "None" and window.bars_bottom.vertical_bars > 0:
        draw_glazing_bars(
            ax,
            bottom_glass_x,
            bottom_glass_y,
            bottom_glass_width,
            bottom_glass_height,
            window.bars_bottom.vertical_bars,
            window.bars_bottom.horizontal_bars
        )

    # Add dimension annotations
    # Frame width annotation
    ax.annotate('',
                xy=(offset_x + display_width, offset_y - 0.5),
                xytext=(offset_x, offset_y - 0.5),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax.text(offset_x + display_width / 2, offset_y - 0.8,
            f'Frame Width: {window.frame.width:.0f} mm',
            ha='center', fontsize=10, color='red', weight='bold')

    # Frame height annotation
    ax.annotate('',
                xy=(offset_x - 0.5, offset_y + display_height),
                xytext=(offset_x - 0.5, offset_y),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax.text(offset_x - 1.5, offset_y + display_height / 2,
            f'Frame Height:\n{window.frame.height:.0f} mm',
            ha='center', va='center', fontsize=10, color='red', weight='bold', rotation=90)

    # Title
    ax.text(offset_x + display_width / 2, offset_y + display_height + 1,
            f'{window.name} - Technical Drawing',
            ha='center', fontsize=14, weight='bold')

    # Specifications text
    specs_y = offset_y + display_height + 1.8
    specs_text = f"""
Paint: {window.paint_color} | Hardware: {window.hardware_finish}
Glass: {window.glass_top.type} | Bars: {window.bars_top.layout_type}
Trickle Vent: {window.trickle_vent} | Cill Extension: {window.cill_extension}mm
    """.strip()

    ax.text(offset_x + display_width / 2, specs_y,
            specs_text,
            ha='center', fontsize=8, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    # Legend
    ax.legend(loc='upper right', fontsize=8)

    # Remove axes
    ax.axis('off')

    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Drawing created: {output_path}")
    return output_path


def draw_glazing_bars(ax, x, y, width, height, vertical_bars, horizontal_bars):
    """
    Draw glazing bars on glass area

    Args:
        ax: Matplotlib axes
        x, y: Bottom-left corner of glass area
        width, height: Glass area dimensions
        vertical_bars: Number of vertical bars
        horizontal_bars: Number of horizontal bars
    """
    bar_color = 'darkgray'
    bar_width = 0.08

    # Vertical bars
    if vertical_bars > 0:
        spacing = width / (vertical_bars + 1)
        for i in range(1, vertical_bars + 1):
            bar_x = x + i * spacing - bar_width / 2
            bar = patches.Rectangle(
                (bar_x, y),
                bar_width,
                height,
                linewidth=0,
                facecolor=bar_color,
                alpha=0.8
            )
            ax.add_patch(bar)

    # Horizontal bars
    if horizontal_bars > 0:
        spacing = height / (horizontal_bars + 1)
        for i in range(1, horizontal_bars + 1):
            bar_y = y + i * spacing - bar_width / 2
            bar = patches.Rectangle(
                (x, bar_y),
                width,
                bar_width,
                linewidth=0,
                facecolor=bar_color,
                alpha=0.8
            )
            ax.add_patch(bar)


def draw_all_windows(project, output_dir: str = "output") -> list:
    """
    Draw all windows in a project

    Args:
        project: Project object
        output_dir: Output directory for drawings

    Returns:
        List of paths to created drawings
    """
    paths = []
    for window in project.windows:
        path = f"{output_dir}/{window.name}_drawing.png"
        draw_window(window, path)
        paths.append(path)

    return paths
