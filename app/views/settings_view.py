from __future__ import annotations
import logging

from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import (
    QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QMessageBox, QGraphicsDropShadowEffect
)

from app.widgets import Slider, ImageDropButton


log = logging.getLogger(__name__)


class SettingsView(QWidget):
    returnPressed = Signal()
    windowClosed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle(" ")
        self.setWindowIcon(QIcon(":/holy_sight.png"))
        self.setFixedSize(200, 350)
        self.setObjectName("WIN_settings")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ----------------------------------------------------------------------------

        self.crosshair_coord = QLabel()
        self.crosshair_coord.setObjectName("infoLabel")
        self.crosshair_coord.setAlignment(Qt.AlignmentFlag.AlignCenter)

        color_layout = QHBoxLayout()
        color_layout.setSpacing(0)
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(60, 60)
        self.color_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_preview.setObjectName("colorPickerBtn")
        self.image_preview = ImageDropButton()
        self.image_preview.setText("Set\nImage")
        self.image_preview.setObjectName("setImageBtn")
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.image_preview)

        self.crosshair_form_layout = QFormLayout()
        self.crosshair_form_layout.setContentsMargins(10, 0, 10, 0)
        self.sizer_slider = Slider()
        self.sizer_slider.setRange(5, 200)
        self.opacity_slider = Slider(opacity_mode=True)
        self.opacity_slider.setRange(0, 10)
        self.crosshair_form_layout.addRow("Size", self.sizer_slider)
        self.crosshair_form_layout.addRow("Opacity", self.opacity_slider)

        self.move_crosshair = QPushButton("Move")
        self.move_crosshair.setFixedHeight(25)

        self.hide_btn = QPushButton("Hide")
        self.hide_btn.setFixedHeight(25)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.shortcuts_info = (
            "<b>Ctrl+Alt+S</b>  Open this window<br>"
            "<b>Ctrl+Alt+X</b>  Center crosshair<br>"
            "<b>Ctrl+Alt+V</b>  Toggle visibility<br>"
        )
        self.drag_info = (
            "Drag the crosshair or use the arrow keys to move it.<br>"
            "Double-click or press <b>Ctrl+Alt+X</b> to center."
        )
        self.info_label.setText(self.shortcuts_info)

        self.main_layout.addWidget(self.crosshair_coord)
        self.main_layout.addSpacing(6)
        self.main_layout.addLayout(color_layout)
        self.main_layout.addLayout(self.crosshair_form_layout)
        self.main_layout.addSpacing(6)
        self.main_layout.addWidget(self.move_crosshair)
        self.main_layout.addWidget(self.hide_btn)
        self.main_layout.addSpacing(6)
        self.main_layout.addWidget(self.info_label)

    def show_window(self) -> None:
        if not self.isVisible():
            self.show()

        if self.isMinimized():
            self.showNormal()

    @Slot()
    def on_crosshair_move_mode_changed(self, movable: bool) -> None:
        if movable:
            self.info_label.setText(self.drag_info)
            self.move_crosshair.setText("(Press Enter to exit)")
            self.move_crosshair.setDisabled(True)
        else:
            self.info_label.setText(self.shortcuts_info)
            self.move_crosshair.setText("Move")
            self.move_crosshair.setDisabled(False)

    @Slot(int, int)
    def update_visual_coord(self, pos: tuple) -> None:
        x, y = pos
        self.crosshair_coord.setText(f"x: {x}   y: {y}")
        log.debug(f"Update visual coordinate: X: {x}, Y: {y}")

    def set_color_picker_btn_style(self, btn: QPushButton, color: str, bg_color: str) -> None:
        btn.setStyleSheet(f"""
            QPushButton#colorPickerBtn {{
                color: {color};
                background-color: {bg_color};
                font-weight: bold;
            }}
        """)

    def apply_shadow(self, widget, color="#181818", blur=20, offset=(0, 0), brightness=120) -> None:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setXOffset(offset[0])
        shadow.setYOffset(offset[1])

        shadow_color = QColor(color)
        shadow_color.setAlpha(brightness)

        shadow.setColor(shadow_color)
        widget.setGraphicsEffect(shadow)

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Escape):
            self.returnPressed.emit()
            log.debug("[Settings] Enter key pressed. Exit Move Mode.")

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        self.windowClosed.emit()
        log.debug("Settings window closed. Exit Move Mode.")
