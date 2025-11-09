"""PNG raster graphics export using matplotlib.

This module provides high-quality raster image export for documentation,
presentations, and preview purposes.
"""

from __future__ import annotations

from typing import Optional, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg

from .base_exporter import BaseExporter
from .renderer import WindowRenderer, ColorScheme
from app.core.models import Window, Project


class PNGExporter(BaseExporter):
    """Export window designs to PNG raster format.

    Generates high-quality PNG images with anti-aliasing, proper colors,
    and customizable resolution.
    """

    def __init__(self, output_dir: str = "output/graphics") -> None:
        """Initialize PNG exporter.

        Args:
            output_dir: Directory for output files
        """
        super().__init__(output_dir)
        self.file_extension = ".png"

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> tuple:
        """Convert hex color to RGBA tuple for matplotlib.

        Args:
            hex_color: Hex color string (e.g., '#FF0000')
            alpha: Alpha value (0.0-1.0)

        Returns:
            RGBA tuple (r, g, b, a) with values 0-1
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return rgb + (alpha,)

    def export_window(
        self,
        window: Window,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export a window to PNG format.

        Args:
            window: Window object to export
            output_path: Optional custom output path
            **options: Additional options:
                - dpi (int): Resolution in dots per inch (default 300)
                - include_dimensions (bool): Include dimension lines (default True)
                - include_bars (bool): Include glazing bars (default True)
                - background_color (str): Background color (default 'white')
                - show_grid (bool): Show background grid (default False)

        Returns:
            Path to generated PNG file
        """
        if not self.validate_window(window):
            raise ValueError("Invalid window object for export")

        # Get options
        dpi = options.get("dpi", 300)
        bg_color = options.get("background_color", "white")
        show_grid = options.get("show_grid", False)

        # Create renderer and generate geometry
        renderer = WindowRenderer(window, ColorScheme())
        renderer.generate_geometry(
            include_dimensions=options.get("include_dimensions", True),
            include_bars=options.get("include_bars", True)
        )

        # Calculate canvas size
        bounds_min, bounds_max = renderer.get_bounds()
        padding = 50.0
        canvas_width = (bounds_max.x - bounds_min.x + 2 * padding) / 25.4  # Convert mm to inches
        canvas_height = (bounds_max.y - bounds_min.y + 2 * padding) / 25.4

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(canvas_width, canvas_height), dpi=dpi)
        ax.set_xlim(bounds_min.x - padding, bounds_max.x + padding)
        ax.set_ylim(bounds_min.y - padding, bounds_max.y + padding)
        ax.set_aspect('equal')

        # Set background color
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        # Optional grid
        if show_grid:
            ax.grid(True, color=renderer.colors.grid, linestyle=':', linewidth=0.5, alpha=0.5)
        else:
            ax.grid(False)

        # Hide axis ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Render rectangles
        for rect in renderer.rectangles:
            color = self._hex_to_rgba(rect.color, rect.alpha)
            patch = patches.Rectangle(
                (rect.x, rect.y),
                rect.width,
                rect.height,
                linewidth=rect.linewidth * 3,  # Scale up for visibility
                edgecolor=self._hex_to_rgba(rect.color, 1.0),
                facecolor=color if rect.fill else 'none',
                zorder=2
            )
            ax.add_patch(patch)

        # Render lines
        for line in renderer.lines:
            color = self._hex_to_rgba(line.color, 1.0)
            linestyle_map = {
                'solid': '-',
                'dashed': '--',
                'dotted': ':'
            }
            ax.plot(
                [line.x1, line.x2],
                [line.y1, line.y2],
                color=color,
                linewidth=line.linewidth * 3,
                linestyle=linestyle_map.get(line.linestyle, '-'),
                zorder=1
            )

        # Render dimension lines
        for dim in renderer.dimensions:
            color = self._hex_to_rgba(dim.color, 1.0)
            offset_y = dim.offset if dim.y1 == dim.y2 else 0
            offset_x = dim.offset if dim.x1 == dim.x2 else 0

            if dim.y1 == dim.y2:  # Horizontal
                # Extension lines
                ax.plot([dim.x1, dim.x1], [dim.y1, dim.y1 + offset_y],
                       color=color, linewidth=0.75, zorder=3)
                ax.plot([dim.x2, dim.x2], [dim.y2, dim.y2 + offset_y],
                       color=color, linewidth=0.75, zorder=3)
                # Dimension line with arrows
                ax.annotate(
                    '',
                    xy=(dim.x2, dim.y2 + offset_y),
                    xytext=(dim.x1, dim.y1 + offset_y),
                    arrowprops=dict(
                        arrowstyle='<->',
                        color=color,
                        lw=1.0,
                        shrinkA=0,
                        shrinkB=0
                    ),
                    zorder=3
                )
            else:  # Vertical
                # Extension lines
                ax.plot([dim.x1, dim.x1 + offset_x], [dim.y1, dim.y1],
                       color=color, linewidth=0.75, zorder=3)
                ax.plot([dim.x2, dim.x2 + offset_x], [dim.y2, dim.y2],
                       color=color, linewidth=0.75, zorder=3)
                # Dimension line with arrows
                ax.annotate(
                    '',
                    xy=(dim.x2 + offset_x, dim.y2),
                    xytext=(dim.x1 + offset_x, dim.y1),
                    arrowprops=dict(
                        arrowstyle='<->',
                        color=color,
                        lw=1.0,
                        shrinkA=0,
                        shrinkB=0
                    ),
                    zorder=3
                )

        # Render text
        for text in renderer.texts:
            color = self._hex_to_rgba(text.color, 1.0)
            ha_map = {'left': 'left', 'center': 'center', 'right': 'right'}
            va_map = {'top': 'top', 'middle': 'center', 'bottom': 'bottom'}
            ax.text(
                text.x,
                text.y,
                text.text,
                fontsize=text.size * 3,  # Scale up for visibility
                color=color,
                ha=ha_map.get(text.halign, 'center'),
                va=va_map.get(text.valign, 'center'),
                rotation=text.rotation,
                zorder=4
            )

        # Add title
        title_text = f"{window.name} - {window.frame.width:.0f} × {window.frame.height:.0f} mm"
        fig.suptitle(
            title_text,
            fontsize=12,
            fontweight='bold',
            y=0.98
        )

        # Tight layout
        plt.tight_layout()

        # Determine output path
        output_dir = self._ensure_output_dir()
        if output_path:
            file_path = output_path
        else:
            file_path = self._generate_filename(window.name, "preview")

        # Save PNG with high quality
        fig.savefig(
            file_path,
            dpi=dpi,
            bbox_inches='tight',
            facecolor=bg_color,
            edgecolor='none',
            pad_inches=0.2
        )
        plt.close(fig)

        return str(file_path)

    def export_project(
        self,
        project: Project,
        output_path: Optional[str] = None,
        **options: Any
    ) -> str:
        """Export all windows in a project to separate PNG files.

        Args:
            project: Project containing multiple windows
            output_path: Optional custom output directory
            **options: Export options passed to export_window

        Returns:
            Path to output directory containing all PNG files
        """
        self._add_metadata(
            project_name=project.name,
            client_name=project.client_name
        )

        output_dir = self._ensure_output_dir()
        exported_files = []

        for idx, window in enumerate(project.windows, start=1):
            filename = self._generate_filename(
                f"{project.name}_{window.name}",
                f"w{idx:02d}"
            )
            file_path = self.export_window(window, str(filename), **options)
            exported_files.append(file_path)

        return str(output_dir)
