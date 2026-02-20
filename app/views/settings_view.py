from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from PySide6.QtGui import QIcon
from PySide6.QtCore import QEvent, Qt, Slot, QSize
from PySide6.QtWidgets import (
    QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QMessageBox, QGraphicsDropShadowEffect
)

from app.widgets import Slider
from app.core.types import CrosshairMode

if TYPE_CHECKING:
    from app.core.bus import AppBus

log = logging.getLogger(__name__)


class SettingsView(QWidget):
    def __init__(self, bus: AppBus) -> None:
        super().__init__()
        self.bus = bus
        
        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle(" ")
        self.setWindowIcon(QIcon(":/app/assets/icons/holy_sight.png"))
        self.setFixedSize(200, 350)
        # self.setWindowOpacity(0.95)
        self.setObjectName("WIN_settings")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ----------------------------------------------------------------------------

        self.crosshair_coord_layout = QHBoxLayout()
        self.crosshair_coord_layout.addStretch()
        self.crosshair_coord_layout.addSpacing(8)
        self.crosshair_coord = QLabel()
        self.info_dialog = QPushButton()
        self.info_dialog.setFixedSize(22, 22)
        self.info_dialog.setIcon(QIcon(":/app/assets/icons/info.png"))
        self.info_dialog.setIconSize(QSize(14, 14))
        self.info_dialog.setObjectName("iconBtn")
        self.crosshair_coord_layout.addWidget(self.crosshair_coord)
        self.crosshair_coord_layout.addStretch()
        self.crosshair_coord_layout.addWidget(self.info_dialog)

        self.crosshair_form_layout = QFormLayout()
        
        self.color_preview = QPushButton()
        self.color_preview.setFixedHeight(30)
        self.color_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_preview.setObjectName("colorPickerBtn")

        self.sizer_slider = Slider()
        self.sizer_slider.setRange(5, 200)

        self.opacity_slider = Slider(opacity_mode=True)
        self.opacity_slider.setRange(0, 255)

        self.border_slider = Slider()
        self.border_slider.setRange(0, 10)

        self.border_color_preview = QPushButton()
        self.border_color_preview.setFixedHeight(30)
        self.border_color_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.border_color_preview.setObjectName("colorPickerBtn")

        self.crosshair_form_layout.addRow("Color", self.color_preview)
        self.crosshair_form_layout.addRow("Size", self.sizer_slider)
        self.crosshair_form_layout.addRow("Opacity", self.opacity_slider)
        self.crosshair_form_layout.addRow("Border Size", self.border_slider)
        self.crosshair_form_layout.addRow("Border Color", self.border_color_preview)

        self.image_preview = QPushButton()
        self.image_preview.setText("Set\nImage")
        self.image_preview.setFixedSize(60, 60)
        self.image_preview.setObjectName("setImageBtn")

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setFixedHeight(34)
        self.info_label.setVisible(False)
        self.info_label.setObjectName("infoLabel")
        self.text_info = (
                    "Drag the crosshair or use the arrow keys to move it. "
                    "Double-click or press <b>Ctrl+Alt+C</b> to center."
                )

        self.move_crosshair = QPushButton("Move Crosshair")
        self.move_crosshair.setFixedHeight(25)

        self.hide_btn = QPushButton("Hide Crosshair")
        self.hide_btn.setFixedHeight(25)

        self.main_layout.addLayout(self.crosshair_coord_layout)
        self.main_layout.addSpacing(6)
        self.main_layout.addLayout(self.crosshair_form_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.move_crosshair)
        self.main_layout.addWidget(self.hide_btn)

        self.apply_shadow(self.info_dialog)
        self.apply_shadow(self.color_preview)
        self.apply_shadow(self.border_color_preview)
        self.apply_shadow(self.move_crosshair, offset=(0, 2))
        self.apply_shadow(self.hide_btn, offset=(0, 2))
        self.apply_shadow(self.image_preview, color="#10276d", blur=30)

    def show_app_info(self):
        QMessageBox.information(
            self, 
            "Info", 
            "<b>APP SHORTCUTS</b><br><br>"
            "<b>Ctrl + Alt + X</b>  Toggle visibility<br>"
            "<b>Ctrl + Alt + C</b>  Center crosshair"
        )

    def show_window(self) -> None:
        if not self.isVisible():
            self.show()
        
        if self.isMinimized():
            self.showNormal()

    @Slot(int, int)
    def update_visual_coord(self, pos: tuple) -> None:
        x, y = pos
        self.crosshair_coord.setText(f"x: {x}\ty: {y}")
        log.debug(f"Update visual coordinate: X: {x}, Y: {y}")

    def set_color_picker_btn_style(self, btn: QPushButton, color: str, bg_color: str) -> None:
        btn.setStyleSheet(f"""
            QPushButton#colorPickerBtn {{ 
                color: {color}; 
                background-color: {bg_color};
                font-weight: bold;
            }}
        """)

    def apply_shadow(self, widget, color="#181818", blur=20, offset=(0, 0)):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setXOffset(offset[0])
        shadow.setYOffset(offset[1])
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Escape):
            if self.bus.crosshairMode == CrosshairMode.MOVE:
                self.info_label.setText("Press Enter again to exit move mode...")
                log.debug("Main Window is now activated.")
                self.bus.activateMainWindow.emit()
    
    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow() and self.bus.crosshairMode == CrosshairMode.MOVE:
                self.info_label.setText(self.text_info)
                log.debug("Settings Window Activated.")