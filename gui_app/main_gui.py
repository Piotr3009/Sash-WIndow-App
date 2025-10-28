"""PyQt6 interface for the Skylon Elements Sash Window Designer with Graphics."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Dict, Tuple

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .backend import calculations, database, drawings, export_excel, export_pdf
from .backend.models import Project, Window

# Graphics imports
try:
    from .graphics.viewer import GraphicsViewer
    from .graphics.export_dxf import DXFExporter
    from .graphics.export_svg import SVGExporter
    from .graphics.export_png import PNGExporter
    from .graphics.scene import build_scene
    from .graphics.workers import ExportWorker, PreviewWorker
    from .graphics.preview import is_preview_available
    GRAPHICS_AVAILABLE = True
except ImportError:
    GRAPHICS_AVAILABLE = False


class MainWindow(QMainWindow):
    """Main application window encapsulating the designer workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Skylon Elements – Sash Window Designer")
        self.resize(1400, 900)

        self._project: Project | None = None
        self._window_data: Dict[str, object] | None = None
        self._export_payload: Dict[str, object] | None = None
        self._drawings: Dict[str, str] = {}
        self._current_window: Window | None = None

        # Graphics exporters
        if GRAPHICS_AVAILABLE:
            self._dxf_exporter = DXFExporter(output_dir="output/cad")
            self._svg_exporter = SVGExporter(output_dir="output/cad")
            self._png_exporter = PNGExporter()
            self._thread_pool = QThreadPool.globalInstance()
            self._thread_pool.setMaxThreadCount(4)  # Allow up to 4 concurrent exports
        else:
            self._dxf_exporter = None
            self._svg_exporter = None
            self._png_exporter = None
            self._thread_pool = None

        self._build_ui()
        self._apply_stylesheet()

    # ------------------------------------------------------------------
    # UI construction helpers
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left configuration panel
        self.configuration_group = QGroupBox("Window Configuration")
        config_layout = QFormLayout()
        self.configuration_group.setLayout(config_layout)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("e.g. Apartment A")
        self.client_name_edit = QLineEdit()
        self.client_name_edit.setPlaceholderText("Client name")

        self.frame_width_spin = QDoubleSpinBox()
        self.frame_width_spin.setRange(400.0, 4000.0)
        self.frame_width_spin.setSingleStep(10.0)
        self.frame_width_spin.setValue(1200.0)

        self.frame_height_spin = QDoubleSpinBox()
        self.frame_height_spin.setRange(400.0, 4000.0)
        self.frame_height_spin.setSingleStep(10.0)
        self.frame_height_spin.setValue(1600.0)

        self.paint_color_combo = QComboBox()
        self.paint_color_combo.addItems(["White", "Grey", "Custom"])

        self.hardware_finish_combo = QComboBox()
        self.hardware_finish_combo.addItems(["Brass", "Chrome", "Satin", "Black"])

        self.trickle_vent_combo = QComboBox()
        self.trickle_vent_combo.addItems(["None", "Standard", "Concealed"])

        self.sash_catches_combo = QComboBox()
        self.sash_catches_combo.addItems(["PAS24", "Non-PAS24"])

        self.cill_extension_combo = QComboBox()
        self.cill_extension_combo.addItems(["35", "60", "85", "110"])
        self.cill_extension_combo.setCurrentText("60")

        self.bars_layout_combo = QComboBox()
        self.bars_layout_combo.addItems(["None", "2x2", "3x3", "4x4"])

        config_layout.addRow("Project Name", self.project_name_edit)
        config_layout.addRow("Client Name", self.client_name_edit)
        config_layout.addRow("Frame Width (mm)", self.frame_width_spin)
        config_layout.addRow("Frame Height (mm)", self.frame_height_spin)
        config_layout.addRow("Paint Color", self.paint_color_combo)
        config_layout.addRow("Hardware Finish", self.hardware_finish_combo)
        config_layout.addRow("Trickle Vent", self.trickle_vent_combo)
        config_layout.addRow("Sash Catches", self.sash_catches_combo)
        config_layout.addRow("Cill Extension", self.cill_extension_combo)
        config_layout.addRow("Bars Layout", self.bars_layout_combo)

        button_layout = QVBoxLayout()
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.on_calculate)

        self.pdf_button = QPushButton("Generate PDF")
        self.pdf_button.clicked.connect(self.on_generate_pdf)
        self.pdf_button.setEnabled(False)

        self.excel_button = QPushButton("Export Excel")
        self.excel_button.clicked.connect(self.on_export_excel)
        self.excel_button.setEnabled(False)

        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.pdf_button)
        button_layout.addWidget(self.excel_button)
        button_layout.addStretch(1)

        config_container = QVBoxLayout()
        config_container.addWidget(self.configuration_group)
        config_container.addLayout(button_layout)
        config_container.addStretch(1)

        left_panel = QWidget()
        left_panel.setLayout(config_container)
        main_layout.addWidget(left_panel, 1)

        # Create tabs for Graphics and Results
        self.tabs = QTabWidget()

        if GRAPHICS_AVAILABLE:
            self._build_graphics_tab()

        self._build_results_tab()

        main_layout.addWidget(self.tabs, 2)

    def _build_graphics_tab(self) -> None:
        """Build the Graphics visualization tab."""
        graphics_tab = QWidget()
        graphics_layout = QVBoxLayout()
        graphics_tab.setLayout(graphics_layout)

        # Toolbar for graphics actions
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar buttons
        self.refresh_graphics_button = QPushButton("🔄 Refresh")
        self.refresh_graphics_button.setToolTip("Refresh graphics view")
        self.refresh_graphics_button.clicked.connect(self.on_refresh_graphics)
        self.refresh_graphics_button.setEnabled(False)

        self.zoom_fit_button = QPushButton("🔍 Fit")
        self.zoom_fit_button.setToolTip("Fit to window")
        self.zoom_fit_button.clicked.connect(self.on_zoom_fit)
        self.zoom_fit_button.setEnabled(False)

        self.zoom_in_button = QPushButton("➕ Zoom In")
        self.zoom_in_button.setToolTip("Zoom in")
        self.zoom_in_button.clicked.connect(self.on_zoom_in)
        self.zoom_in_button.setEnabled(False)

        self.zoom_out_button = QPushButton("➖ Zoom Out")
        self.zoom_out_button.setToolTip("Zoom out")
        self.zoom_out_button.clicked.connect(self.on_zoom_out)
        self.zoom_out_button.setEnabled(False)

        self.export_dxf_button = QPushButton("💾 Export DXF")
        self.export_dxf_button.setToolTip("Export to DXF CAD format")
        self.export_dxf_button.clicked.connect(self.on_export_dxf)
        self.export_dxf_button.setEnabled(False)

        self.export_svg_button = QPushButton("🖼 Export SVG")
        self.export_svg_button.setToolTip("Export to SVG vector format")
        self.export_svg_button.clicked.connect(self.on_export_svg)
        self.export_svg_button.setEnabled(False)

        self.export_png_graphics_button = QPushButton("📷 Export PNG")
        self.export_png_graphics_button.setToolTip("Export to PNG image format")
        self.export_png_graphics_button.clicked.connect(self.on_export_png_graphics)
        self.export_png_graphics_button.setEnabled(False)

        toolbar_layout.addWidget(self.refresh_graphics_button)
        toolbar_layout.addWidget(self.zoom_fit_button)
        toolbar_layout.addWidget(self.zoom_in_button)
        toolbar_layout.addWidget(self.zoom_out_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.export_dxf_button)
        toolbar_layout.addWidget(self.export_svg_button)
        toolbar_layout.addWidget(self.export_png_graphics_button)

        graphics_layout.addWidget(toolbar_widget)

        # Graphics viewer
        self.graphics_viewer = GraphicsViewer()
        graphics_layout.addWidget(self.graphics_viewer, 1)

        # Graphics status label
        self.graphics_status_label = QLabel("Configure window and click Calculate to view graphics")
        graphics_layout.addWidget(self.graphics_status_label)

        self.tabs.addTab(graphics_tab, "Graphics")

    def _build_results_tab(self) -> None:
        """Build the Results & Preview tab."""
        results_tab = QWidget()
        results_layout = QVBoxLayout()
        results_tab.setLayout(results_layout)

        right_panel = QGroupBox("Results & Preview")
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.results_label = QLabel("Fill out the form and press Calculate.")
        self.results_label.setWordWrap(True)
        right_layout.addWidget(self.results_label)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(420, 520)
        right_layout.addWidget(self.preview_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        right_layout.addWidget(self.log_text, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Waiting for calculation…")
        right_layout.addWidget(self.status_label)

        results_layout.addWidget(right_panel)
        self.tabs.addTab(results_tab, "Results")

    def _apply_stylesheet(self) -> None:
        style_path = Path(__file__).resolve().parent / "resources" / "style.qss"
        if style_path.exists():
            with style_path.open("r", encoding="utf-8") as fh:
                self.setStyleSheet(fh.read())

        logo_path = Path(__file__).resolve().parent / "resources" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def append_log(self, message: str) -> None:
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

    def _bars_mapping(self, layout: str) -> Tuple[int, int]:
        match layout:
            case "2x2":
                return 2, 2
            case "3x3":
                return 3, 3
            case "4x4":
                return 4, 4
            case _:
                return 0, 0

    def _calculate_sash_heights(self, frame_height: float) -> Tuple[float, float]:
        """Split the frame height into top and bottom sash heights."""
        sash_height = frame_height / 2
        return sash_height, sash_height

    def _update_results_label(self, window_export: Dict[str, object]) -> None:
        frame_data = window_export["window"]["frame"]
        sash_data = window_export["window"]["sash_bottom"]
        glass_data = window_export["glass"]
        text = (
            f"<b>Sash Width:</b> {sash_data['width']:.2f} mm\n"
            f"<b>Glass Height:</b> {glass_data['height']:.2f} mm\n"
            f"<b>Jamb Length:</b> {frame_data['jambs_length']:.2f} mm"
        )
        self.results_label.setText(text)

    def _update_preview(self) -> None:
        if not self._window_data:
            self.preview_label.clear()
            return

        drawing_path = self._drawings.get(self._window_data["window"]["id"])
        if drawing_path and Path(drawing_path).exists():
            pixmap = QPixmap(drawing_path).scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.clear()

    def _set_export_buttons_enabled(self, enabled: bool) -> None:
        self.pdf_button.setEnabled(enabled)
        self.excel_button.setEnabled(enabled)

    def _set_graphics_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable graphics buttons."""
        if not GRAPHICS_AVAILABLE:
            return
        self.refresh_graphics_button.setEnabled(enabled)
        self.zoom_fit_button.setEnabled(enabled)
        self.zoom_in_button.setEnabled(enabled)
        self.zoom_out_button.setEnabled(enabled)
        self.export_dxf_button.setEnabled(enabled)
        self.export_svg_button.setEnabled(enabled)
        self.export_png_graphics_button.setEnabled(enabled)

    def _toggle_progress(self, show: bool) -> None:
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def on_calculate(self) -> None:
        self._set_export_buttons_enabled(False)
        self._set_graphics_buttons_enabled(False)
        self.status_label.setText("Calculating…")
        try:
            project_name = self.project_name_edit.text().strip() or "Untitled Project"
            client_name = self.client_name_edit.text().strip() or "Unknown Client"
            frame_width = float(self.frame_width_spin.value())
            frame_height = float(self.frame_height_spin.value())
            paint_color = self.paint_color_combo.currentText()
            hardware_finish = self.hardware_finish_combo.currentText()
            trickle_vent = self.trickle_vent_combo.currentText()
            sash_catches = self.sash_catches_combo.currentText()
            cill_extension = int(self.cill_extension_combo.currentText())
            bars_layout = self.bars_layout_combo.currentText()
            bars_vertical, bars_horizontal = self._bars_mapping(bars_layout)

            top_sash_height, bottom_sash_height = self._calculate_sash_heights(frame_height)

            window_id = str(uuid.uuid4())
            window = calculations.assemble_window(
                window_id=window_id,
                name="Primary Window",
                frame_width=frame_width,
                frame_height=frame_height,
                top_sash_height=top_sash_height,
                bottom_sash_height=bottom_sash_height,
                paint_color=paint_color,
                hardware_finish=hardware_finish,
                trickle_vent=trickle_vent,
                sash_catches=sash_catches,
                cill_extension=cill_extension,
                glass_type="24mm TGH/ARG/TGH",
                glass_frosted=False,
                glass_toughened=True,
                spacer_color="Black",
                glass_pcs=2,
                bars_layout=bars_layout,
                bars_vertical=bars_vertical,
                bars_horizontal=bars_horizontal,
            )

            project = Project(
                id=str(uuid.uuid4()),
                name=project_name,
                client_name=client_name,
                windows=[window],
            )

            export_payload = calculations.prepare_project_export(project)
            window_export = export_payload["windows"][0]

            drawing_path = drawings.draw_window(window)
            self._drawings = {window.id: drawing_path}

            self._project = project
            self._current_window = window
            self._window_data = window_export
            self._export_payload = export_payload

            self._update_results_label(window_export)
            self._update_preview()

            # Update graphics viewer
            if GRAPHICS_AVAILABLE:
                self.graphics_viewer.set_window(window)
                self.graphics_status_label.setText("✅ Graphics rendered successfully")
                self._set_graphics_buttons_enabled(True)

            self.append_log("✅ Calculations complete.")

            try:
                project_response = database.save_project(project)
                materials = window_export["materials"]
                glass = window_export["glass"]
                window_response = database.save_window(project.id, window, materials, glass)
                self.append_log(f"✅ Data Saved to Supabase (project_id: {project.id})")
                self.append_log(str(project_response))
                self.append_log(str(window_response))
                self.status_label.setText(f"✅ Saved to Supabase (project_id: {project.id})")
            except Exception as exc:  # noqa: BLE001 - surface to UI
                self.append_log(f"⚠️ Supabase save skipped: {exc}")
                self.status_label.setText("⚠️ Supabase save skipped – check configuration.")

            self._set_export_buttons_enabled(True)
        except Exception as exc:  # noqa: BLE001 - provide message to user
            self.append_log(f"❌ Calculation failed: {exc}")
            self.status_label.setText("❌ Calculation failed")
            QMessageBox.critical(self, "Calculation Error", str(exc))
            self._project = None
            self._current_window = None
            self._window_data = None
            self._export_payload = None
            self._drawings = {}
            self._set_export_buttons_enabled(False)
            self._set_graphics_buttons_enabled(False)
            self.preview_label.clear()
            self.results_label.setText("Calculation failed. Check inputs and retry.")
            if GRAPHICS_AVAILABLE:
                self.graphics_viewer.clear()
                self.graphics_status_label.setText("No graphics to display")

    def on_generate_pdf(self) -> None:
        if not self._export_payload or not self._window_data:
            QMessageBox.warning(self, "No Data", "Please run a calculation first.")
            return

        self._toggle_progress(True)
        self.status_label.setText("Generating PDF…")
        QApplication.processEvents()
        try:
            pdf_path = export_pdf.generate_pdf(self._export_payload, self._drawings)
            self.append_log(f"✅ PDF Generated: {pdf_path}")
            self.status_label.setText(f"✅ PDF Generated: {pdf_path}")
        except Exception as exc:  # noqa: BLE001 - show to user
            self.append_log(f"❌ PDF generation failed: {exc}")
            self.status_label.setText("❌ PDF generation failed")
            QMessageBox.critical(self, "PDF Error", str(exc))
        finally:
            self._toggle_progress(False)

    def on_export_excel(self) -> None:
        if not self._export_payload or not self._window_data:
            QMessageBox.warning(self, "No Data", "Please run a calculation first.")
            return

        self._toggle_progress(True)
        self.status_label.setText("Exporting Excel…")
        QApplication.processEvents()
        try:
            excel_path = export_excel.generate_excel(self._export_payload)
            self.append_log(f"✅ Excel Exported: {excel_path}")
            self.status_label.setText(f"✅ Excel Exported: {excel_path}")
        except Exception as exc:  # noqa: BLE001
            self.append_log(f"❌ Excel export failed: {exc}")
            self.status_label.setText("❌ Excel export failed")
            QMessageBox.critical(self, "Excel Error", str(exc))
        finally:
            self._toggle_progress(False)

    # ------------------------------------------------------------------
    # Graphics event handlers
    # ------------------------------------------------------------------
    def on_refresh_graphics(self) -> None:
        """Refresh the graphics view."""
        if not self._current_window or not GRAPHICS_AVAILABLE:
            return
        self.graphics_viewer.set_window(self._current_window)
        self.graphics_status_label.setText("✅ Graphics refreshed")
        self.append_log("Graphics view refreshed")

    def on_zoom_fit(self) -> None:
        """Fit graphics to window."""
        if GRAPHICS_AVAILABLE:
            self.graphics_viewer.fit_to_window()

    def on_zoom_in(self) -> None:
        """Zoom in graphics."""
        if GRAPHICS_AVAILABLE:
            self.graphics_viewer.zoom_in()

    def on_zoom_out(self) -> None:
        """Zoom out graphics."""
        if GRAPHICS_AVAILABLE:
            self.graphics_viewer.zoom_out()

    def on_export_dxf(self) -> None:
        """Export to DXF format using threaded worker."""
        if not self._current_window or not self._dxf_exporter:
            QMessageBox.warning(self, "No Data", "Please run a calculation first.")
            return

        # Build scene from current window
        try:
            scene = build_scene(self._current_window, include_dimensions=True)
        except Exception as exc:
            self.append_log(f"❌ Scene building failed: {exc}")
            QMessageBox.critical(self, "Scene Error", str(exc))
            return

        # Add metadata to exporter
        self._dxf_exporter._add_metadata(
            project_name=self._project.name if self._project else "N/A",
            client_name=self._project.client_name if self._project else "N/A"
        )

        # Create and configure worker
        worker = ExportWorker(
            self._dxf_exporter.export_from_scene,
            scene,
            output_path=None
        )
        worker.signals.started.connect(lambda: self._on_export_started("DXF"))
        worker.signals.progress.connect(self._on_export_progress)
        worker.signals.finished.connect(self._on_dxf_export_finished)
        worker.signals.error.connect(self._on_export_error)

        # Start worker in thread pool
        self._thread_pool.start(worker)
        self._toggle_progress(True)
        self.graphics_status_label.setText("Exporting DXF in background…")
        self.append_log("DXF export started…")

    def on_export_svg(self) -> None:
        """Export to SVG format using threaded worker."""
        if not self._current_window or not self._svg_exporter:
            QMessageBox.warning(self, "No Data", "Please run a calculation first.")
            return

        # Build scene from current window
        try:
            scene = build_scene(self._current_window, include_dimensions=True)
        except Exception as exc:
            self.append_log(f"❌ Scene building failed: {exc}")
            QMessageBox.critical(self, "Scene Error", str(exc))
            return

        # Add metadata to exporter
        self._svg_exporter._add_metadata(
            project_name=self._project.name if self._project else "N/A",
            client_name=self._project.client_name if self._project else "N/A"
        )

        # Create and configure worker
        worker = ExportWorker(
            self._svg_exporter.export_from_scene,
            scene,
            output_path=None
        )
        worker.signals.started.connect(lambda: self._on_export_started("SVG"))
        worker.signals.progress.connect(self._on_export_progress)
        worker.signals.finished.connect(self._on_svg_export_finished)
        worker.signals.error.connect(self._on_export_error)

        # Start worker in thread pool
        self._thread_pool.start(worker)
        self._toggle_progress(True)
        self.graphics_status_label.setText("Exporting SVG in background…")
        self.append_log("SVG export started…")

    def on_export_png_graphics(self) -> None:
        """Export to PNG format."""
        if not self._current_window or not self._png_exporter:
            QMessageBox.warning(self, "No Data", "Please run a calculation first.")
            return

        self._toggle_progress(True)
        self.graphics_status_label.setText("Exporting PNG…")
        QApplication.processEvents()
        try:
            self._png_exporter._add_metadata(
                project_name=self._project.name if self._project else "N/A",
                client_name=self._project.client_name if self._project else "N/A"
            )
            png_path = self._png_exporter.export_window(self._current_window, dpi=300)
            self.append_log(f"✅ PNG Exported: {png_path}")
            self.graphics_status_label.setText(f"✅ PNG: {png_path}")
        except Exception as exc:
            self.append_log(f"❌ PNG export failed: {exc}")
            self.graphics_status_label.setText("❌ PNG export failed")
            QMessageBox.critical(self, "PNG Error", str(exc))
        finally:
            self._toggle_progress(False)

    # ------------------------------------------------------------------
    # Threaded export callbacks
    # ------------------------------------------------------------------
    def _on_export_started(self, export_type: str) -> None:
        """Called when export worker starts.

        Args:
            export_type: Type of export (DXF, SVG, etc.)
        """
        self.append_log(f"{export_type} export worker started")

    def _on_export_progress(self, value: int) -> None:
        """Called when export worker reports progress.

        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)
        self.progress_bar.setRange(0, 100)

    def _on_dxf_export_finished(self, file_path: str) -> None:
        """Called when DXF export worker completes successfully.

        Args:
            file_path: Path to exported DXF file
        """
        self._toggle_progress(False)
        self.append_log(f"✅ DXF Exported: {file_path}")
        self.graphics_status_label.setText(f"✅ DXF: {Path(file_path).name}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"DXF file saved to:\n{file_path}"
        )

    def _on_svg_export_finished(self, file_path: str) -> None:
        """Called when SVG export worker completes successfully.

        Args:
            file_path: Path to exported SVG file
        """
        self._toggle_progress(False)
        self.append_log(f"✅ SVG Exported: {file_path}")
        self.graphics_status_label.setText(f"✅ SVG: {Path(file_path).name}")

        # Auto-generate preview if available
        if is_preview_available():
            self._generate_svg_preview(file_path)
        else:
            QMessageBox.information(
                self,
                "Export Complete",
                f"SVG file saved to:\n{file_path}\n\n"
                "Install cairosvg for preview support:\n"
                "pip install cairosvg"
            )

    def _on_export_error(self, error_msg: str) -> None:
        """Called when export worker encounters an error.

        Args:
            error_msg: Error message
        """
        self._toggle_progress(False)
        self.append_log(f"❌ Export failed: {error_msg}")
        self.graphics_status_label.setText("❌ Export failed")
        QMessageBox.critical(
            self,
            "Export Error",
            f"Export failed:\n{error_msg}"
        )

    def _generate_svg_preview(self, svg_path: str) -> None:
        """Generate PNG preview from SVG file using worker.

        Args:
            svg_path: Path to SVG file
        """
        png_path = str(Path(svg_path).with_suffix('.png'))

        # Create preview worker
        worker = PreviewWorker(
            svg_path,
            png_path,
            width=800,
            height=None,  # Auto-calculate from SVG
            dpi=150
        )
        worker.signals.started.connect(
            lambda: self.append_log("Generating SVG preview…")
        )
        worker.signals.finished.connect(self._on_preview_finished)
        worker.signals.error.connect(
            lambda msg: self.append_log(f"⚠ Preview failed: {msg}")
        )

        # Start worker
        self._thread_pool.start(worker)

    def _on_preview_finished(self, png_path: str) -> None:
        """Called when preview generation completes.

        Args:
            png_path: Path to generated PNG preview
        """
        self.append_log(f"✅ Preview generated: {png_path}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"SVG and preview saved:\n{png_path}"
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
