"""PyQt6 interface for the Skylon Elements Sash Window Designer."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Dict, Tuple

from PyQt6.QtCore import Qt
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .backend import calculations, database, drawings, export_excel, export_pdf
from .backend.models import Project


class MainWindow(QMainWindow):
    """Main application window encapsulating the designer workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Skylon Elements – Sash Window Designer")
        self.resize(1200, 800)

        self._project: Project | None = None
        self._window_data: Dict[str, object] | None = None
        self._export_payload: Dict[str, object] | None = None
        self._drawings: Dict[str, str] = {}

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

        # Right panel with results and preview
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

        main_layout.addWidget(right_panel, 1)

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
            self._window_data = window_export
            self._export_payload = export_payload

            self._update_results_label(window_export)
            self._update_preview()

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
            self._window_data = None
            self._export_payload = None
            self._drawings = {}
            self._set_export_buttons_enabled(False)
            self.preview_label.clear()
            self.results_label.setText("Calculation failed. Check inputs and retry.")

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


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
