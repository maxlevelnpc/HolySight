from __future__ import annotations
import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QColorDialog
from PySide6.QtGui import Qt, QIcon
from PySide6.QtCore import Slot

from app.core.constants import SUPPORTED_EXTS

if TYPE_CHECKING:
    from app.core.bus import AppBus
    from app.views import SettingsView
    from app.models import CrosshairModel

log = logging.getLogger(__name__)


class SettingsPresenter:
    def __init__(self, bus: AppBus, model: CrosshairModel, ui: SettingsView) -> None:
        super().__init__()
        self.model = model
        self.ui = ui
        self.bus = bus

        self.setupPresenter()

    def setupPresenter(self) -> None:
        self.ui.sizer_slider.setValue(self.model.size)
        self.ui.opacity_slider.setValue(int(self.model.opacity * 10))

        self.ui.color_preview.clicked.connect(self.request_update_crosshair_color)
        self.ui.sizer_slider.valueChanged.connect(lambda v: setattr(self.model, "size", v))
        self.ui.opacity_slider.valueChanged.connect(lambda v: setattr(self.model, "opacity", v))
        self.ui.image_preview.clicked.connect(self.request_update_crosshair_img)
        self.ui.image_preview.imageDropped.connect(self.request_update_crosshair_img)
        self.model.positionChanged.connect(self.ui.update_visual_coord)
        self.model.moveModeChanged.connect(self.ui.on_crosshair_move_mode_changed)
        self.model.imageChanged.connect(self.on_crosshair_img_changed)
        self.bus.globalVisibilityChanged.connect(self.request_update_crosshair_visibility)
        self.ui.move_crosshair.clicked.connect(lambda checked=False, disable=False: self.request_update_crosshair_move_state(disable))
        self.ui.windowClosed.connect(lambda checked=False, disable=True: self.request_update_crosshair_move_state(disable))
        self.ui.returnPressed.connect(lambda checked=False, disable=True: self.request_update_crosshair_move_state(disable))
        self.ui.hide_btn.clicked.connect(self.request_update_crosshair_visibility)
        self.bus.showSettingsWindow.connect(self.ui.show_window)

        self.apply_settings()

        self.ui.apply_shadow(self.ui.color_preview, color=self.model.color, blur=30)
        self.ui.apply_shadow(self.ui.move_crosshair, offset=(0, 2))
        self.ui.apply_shadow(self.ui.hide_btn, offset=(0, 2))
        self.ui.apply_shadow(self.ui.image_preview, color="#0e9ae0", blur=30)

    def apply_settings(self) -> None:
        """Apply settings from loaded config data"""
        color = self.model.color
        img = self.model.image
        pos = self.model.pos

        self.ui.color_preview.setText(color)
        self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", color)
        log.debug(f"Color picker button background set to: {color}`")

        self.ui.update_visual_coord(pos)

        if img and os.path.exists(img):
            self.set_crosshair_img_preview(img)

    def request_update_crosshair_move_state(self, disable_move: bool = False) -> None:
        if disable_move:
            movable = False
        else:
            movable = not self.model.movable

        # update attr and tell main window to update the crosshair state
        self.model.movable = movable

        self.ui.on_crosshair_move_mode_changed(movable)

    @Slot(bool)
    def request_update_crosshair_color(self) -> None:
        color_picker = QColorDialog.getColor(parent=self.ui, title="Select Color")
        if not color_picker.isValid():
            return

        color = color_picker.name()

        # update attr and tell main window to change the crosshair color
        self.model.color = color

        self.ui.color_preview.setText(color)
        self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", color)
        self.ui.apply_shadow(self.ui.color_preview, color=color, blur=30)

    @Slot()
    def request_update_crosshair_img(self) -> None:
        if self.model.image:
            self.reset_crosshair_img_preview()

            # update attr and tell main window to reset crosshair img
            self.model.image = ""
            return

        spaced_exts = " ".join(f"*.{ext}" for ext in SUPPORTED_EXTS)
        ext_filter = f"All Files ({spaced_exts});;"
        img, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Choose Crosshair Image",
            filter=ext_filter
        )

        if img:
            # update attr and tell main window to set new crosshair img
            self.model.image = img

    @Slot()
    def request_update_crosshair_visibility(self) -> None:
        hidden = self.model.hidden
        b = self.ui.hide_btn
        b.setText("Hide") if hidden else b.setText("Show")

        # update attr and tell main window to update crosshair visibility
        self.model.hidden = not hidden

        log.debug(f"Crosshair is now visible: {hidden}")

    def reset_crosshair_img_preview(self) -> None:
        self.ui.image_preview.setIcon(QIcon())
        self.ui.image_preview.setText("Set\nImage")
        self.ui.image_preview.setCursor(Qt.CursorShape.ArrowCursor)
        self.ui.color_preview.setDisabled(False)
        self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", self.model.color)
        self.ui.apply_shadow(self.ui.color_preview, color=self.model.color)
        self.ui.color_preview.setText(self.model.color)

    def set_crosshair_img_preview(self, img: str) -> None:
        self.ui.image_preview.setIcon(QIcon(img))
        self.ui.image_preview.setIconSize(self.ui.image_preview.size() * 0.8)
        self.ui.image_preview.setText("")
        self.ui.image_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.color_preview.setDisabled(True)
        self.ui.set_color_picker_btn_style(self.ui.color_preview, "white", "#262b3d")
        self.ui.apply_shadow(self.ui.color_preview, color="#121314")
        self.ui.color_preview.setText("//")

    def on_crosshair_img_changed(self, img: str) -> None:
        self.set_crosshair_img_preview(img) if img else self.reset_crosshair_img_preview()
