"""Interactive Qt graphics viewer widget.

This module provides a PyQt6 widget for real-time visualization of window
designs with pan, zoom, and interactive features.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush, QWheelEvent, QMouseEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem

from .renderer import WindowRenderer, ColorScheme, Rectangle, Line, Text, DimensionLine
from app.core.models import Window


class GraphicsViewer(QGraphicsView):
    """Interactive graphics viewer for window designs.

    Provides real-time visualization with pan, zoom, and fit-to-window capabilities.
    Uses QGraphicsView for hardware-accelerated rendering.
    """

    def __init__(self, parent=None) -> None:
        """Initialize the graphics viewer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Rendering settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # View settings
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Background
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))

        # Current window and renderer
        self._window: Optional[Window] = None
        self._renderer: Optional[WindowRenderer] = None
        self._color_scheme = ColorScheme()

        # Zoom limits
        self._min_zoom = 0.1
        self._max_zoom = 10.0

    def set_window(self, window: Window) -> None:
        """Set the window to display.

        Args:
            window: Window object to visualize
        """
        self._window = window
        self.render_window()

    def render_window(
        self,
        include_dimensions: bool = True,
        include_bars: bool = True
    ) -> None:
        """Render the current window to the scene.

        Args:
            include_dimensions: Whether to show dimension lines
            include_bars: Whether to show glazing bars
        """
        if not self._window:
            return

        # Clear scene
        self.scene.clear()

        # Create renderer and generate geometry
        self._renderer = WindowRenderer(self._window, self._color_scheme)
        self._renderer.generate_geometry(
            include_dimensions=include_dimensions,
            include_bars=include_bars
        )

        # Render all geometry
        self._render_rectangles()
        self._render_lines()
        self._render_dimensions()
        self._render_texts()

        # Fit view to content
        self.fit_to_window()

    def _render_rectangles(self) -> None:
        """Render rectangle primitives."""
        if not self._renderer:
            return

        for rect in self._renderer.rectangles:
            color = QColor(rect.color)
            pen = QPen(color, rect.linewidth)
            pen.setCosmetic(True)  # Width doesn't scale with zoom

            if rect.fill:
                color.setAlphaF(rect.alpha)
                brush = QBrush(color)
            else:
                brush = Qt.BrushStyle.NoBrush

            self.scene.addRect(
                rect.x, rect.y, rect.width, rect.height,
                pen=pen,
                brush=brush
            )

    def _render_lines(self) -> None:
        """Render line primitives."""
        if not self._renderer:
            return

        for line in self._renderer.lines:
            color = QColor(line.color)
            pen = QPen(color, line.linewidth)
            pen.setCosmetic(True)

            # Set line style
            if line.linestyle == 'dashed':
                pen.setStyle(Qt.PenStyle.DashLine)
            elif line.linestyle == 'dotted':
                pen.setStyle(Qt.PenStyle.DotLine)
            else:
                pen.setStyle(Qt.PenStyle.SolidLine)

            self.scene.addLine(
                line.x1, line.y1, line.x2, line.y2,
                pen=pen
            )

    def _render_dimensions(self) -> None:
        """Render dimension lines with arrows."""
        if not self._renderer:
            return

        for dim in self._renderer.dimensions:
            color = QColor(dim.color)
            pen = QPen(color, 0.5)
            pen.setCosmetic(True)

            offset_y = dim.offset if dim.y1 == dim.y2 else 0
            offset_x = dim.offset if dim.x1 == dim.x2 else 0

            if dim.y1 == dim.y2:  # Horizontal dimension
                # Extension lines
                self.scene.addLine(dim.x1, dim.y1, dim.x1, dim.y1 + offset_y, pen=pen)
                self.scene.addLine(dim.x2, dim.y2, dim.x2, dim.y2 + offset_y, pen=pen)

                # Dimension line
                dim_pen = QPen(color, 0.75)
                dim_pen.setCosmetic(True)
                self.scene.addLine(
                    dim.x1, dim.y1 + offset_y,
                    dim.x2, dim.y2 + offset_y,
                    pen=dim_pen
                )

                # Arrows
                self._draw_arrow(dim.x1, dim.y1 + offset_y, 0, color)
                self._draw_arrow(dim.x2, dim.y2 + offset_y, 180, color)

            else:  # Vertical dimension
                # Extension lines
                self.scene.addLine(dim.x1, dim.y1, dim.x1 + offset_x, dim.y1, pen=pen)
                self.scene.addLine(dim.x2, dim.y2, dim.x2 + offset_x, dim.y2, pen=pen)

                # Dimension line
                dim_pen = QPen(color, 0.75)
                dim_pen.setCosmetic(True)
                self.scene.addLine(
                    dim.x1 + offset_x, dim.y1,
                    dim.x2 + offset_x, dim.y2,
                    pen=dim_pen
                )

                # Arrows
                self._draw_arrow(dim.x1 + offset_x, dim.y1, 90, color)
                self._draw_arrow(dim.x2 + offset_x, dim.y2, 270, color)

    def _draw_arrow(self, x: float, y: float, angle: float, color: QColor) -> None:
        """Draw an arrow head.

        Args:
            x: X coordinate
            y: Y coordinate
            angle: Rotation angle in degrees
            color: Arrow color
        """
        arrow_size = 5.0
        pen = QPen(color, 0.5)
        pen.setCosmetic(True)
        brush = QBrush(color)

        # Create arrow polygon
        from PyQt6.QtGui import QPolygonF
        arrow = QPolygonF([
            QPointF(0, 0),
            QPointF(-arrow_size, arrow_size / 2),
            QPointF(-arrow_size, -arrow_size / 2)
        ])

        item = self.scene.addPolygon(arrow, pen=pen, brush=brush)
        item.setPos(x, y)
        item.setRotation(angle)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    def _render_texts(self) -> None:
        """Render text annotations."""
        if not self._renderer:
            return

        for text in self._renderer.texts:
            color = QColor(text.color)
            font = QFont("Arial", int(text.size))

            text_item = self.scene.addText(text.text, font)
            text_item.setDefaultTextColor(color)

            # Set position (accounting for text alignment)
            text_item.setPos(text.x, text.y)

            # Set rotation
            if text.rotation != 0:
                text_item.setRotation(text.rotation)

            # Make text not scale with zoom for readability
            text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    def fit_to_window(self) -> None:
        """Fit the entire scene in the view."""
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            # Add some padding
            self.scale(0.9, 0.9)

    def zoom_in(self) -> None:
        """Zoom in by 20%."""
        factor = 1.2
        current_scale = self.transform().m11()
        if current_scale * factor < self._max_zoom:
            self.scale(factor, factor)

    def zoom_out(self) -> None:
        """Zoom out by 20%."""
        factor = 0.8
        current_scale = self.transform().m11()
        if current_scale * factor > self._min_zoom:
            self.scale(factor, factor)

    def reset_zoom(self) -> None:
        """Reset zoom to fit window."""
        self.resetTransform()
        self.fit_to_window()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events for zooming.

        Args:
            event: Wheel event
        """
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def set_background_color(self, color: str) -> None:
        """Set the background color.

        Args:
            color: Color as hex string or color name
        """
        self.setBackgroundBrush(QBrush(QColor(color)))

    def set_color_scheme(self, color_scheme: ColorScheme) -> None:
        """Set the color scheme for rendering.

        Args:
            color_scheme: ColorScheme object
        """
        self._color_scheme = color_scheme
        if self._window:
            self.render_window()

    def export_scene_image(self, file_path: str, width: int = 1920, height: int = 1080) -> None:
        """Export the current scene as an image.

        Args:
            file_path: Output file path
            width: Image width in pixels
            height: Image height in pixels
        """
        from PyQt6.QtGui import QImage, QPainter

        # Create image
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)

        # Render scene to image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene.render(painter)
        painter.end()

        # Save image
        image.save(file_path)

    def clear(self) -> None:
        """Clear the viewer."""
        self.scene.clear()
        self._window = None
        self._renderer = None
