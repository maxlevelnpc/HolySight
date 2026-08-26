from __future__ import annotations
import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QColorDialog
from PySide6.QtGui import Qt, QIcon
from PySide6.QtCore import Slot

from app.core.types import CrosshairMode


if TYPE_CHECKING:
    from app.views import SettingsView
    from app.models import CrosshairModel

log = logging.getLogger(__name__)


class SettingsPresenter:
    def __init__(self, model: CrosshairModel, ui: SettingsView):
        super().__init__()
        self.model = model
        self.ui = ui

        self.setupBehaviour()

    def setupBehaviour(self) -> None:
        self.ui.sizer_slider.setValue(self.model.size)
        self.ui.opacity_slider.setValue(int(self.model.opacity * 10))
        self.ui.border_slider.setValue(self.model.bsize)

        self.ui.sizer_slider.valueChanged.connect(lambda v: setattr(self.model, "size", v))
        self.ui.opacity_slider.valueChanged.connect(lambda v: setattr(self.model, "opacity", v))
        self.ui.border_slider.valueChanged.connect(lambda v: setattr(self.model, "bsize", v))
        self.ui.info_dialog.clicked.connect(self.ui.show_app_info)
        self.ui.color_preview.clicked.connect(self.open_color_picker)
        self.ui.image_preview.clicked.connect(self.open_image_picker)
        self.ui.border_color_preview.clicked.connect(lambda: self.open_color_picker(border=True))
        self.ui.move_crosshair.clicked.connect(lambda: self.ui.on_crosshair_mode_changed(CrosshairMode.MOVE))
        self.ui.hide_btn.clicked.connect(self.set_crosshair_visibility)
        self.ui.bus.stateChangedFinished.connect(lambda: self.ui.on_crosshair_mode_changed(CrosshairMode.GAME))
        self.ui.bus.showSettingsWindow.connect(self.ui.show_window)
        self.model.positionChanged.connect(self.ui.update_visual_coord)

        self.apply_settings()

    def apply_settings(self):
        """Apply settings from loaded config data"""
        color = self.model.color
        img = self.model.image
        bcolor = self.model.bcolor
        pos = self.model.pos

        self.ui.color_preview.setText(color)
        self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", color)
        log.debug(f"Color picker button background set to: {color}`")

        self.ui.border_color_preview.setText(bcolor)
        self.ui.set_color_picker_btn_style(self.ui.border_color_preview, "black", bcolor)
        log.debug(f"Border color picker button background set to: {bcolor}`")

        self.ui.update_visual_coord(pos)

        if img and os.path.exists(img):
            self.set_preview_icon(img)
            self.on_crosshair_image_set(disable=True)
            self.ui.image_preview.setToolTip("Click to reset.")

    @Slot(bool)
    def open_color_picker(self, border: bool = False):
        color_picker = QColorDialog.getColor(
            parent=self.ui,
            title="Select Border Color" if border else "Select Color"
        )
        if not color_picker.isValid():
            return

        color = color_picker.name()

        if border:
            self.model.bcolor = color
            self.ui.border_color_preview.setText(color)
            self.ui.set_color_picker_btn_style(self.ui.border_color_preview, "black", color)
        else:
            self.model.color = color
            self.ui.color_preview.setText(color)
            self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", color)

    @Slot()
    def open_image_picker(self) -> None:
        if self.model.image:
            self.ui.image_preview.setIcon(QIcon())
            self.ui.image_preview.setText("Set\nImage")
            self.ui.image_preview.setToolTip("")
            self.ui.image_preview.setCursor(Qt.CursorShape.ArrowCursor)
            self.on_crosshair_image_set(disable=False)
            self.model.image = ""
            return

        img, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Choose Crosshair Image",
            filter=(
                "All Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif *.webp);;"
            )
        )

        if img:
            self.set_preview_icon(img)
            self.model.image = img
            self.on_crosshair_image_set(disable=True)
            self.ui.image_preview.setToolTip("Click to reset.")
            self.ui.image_preview.setCursor(Qt.CursorShape.PointingHandCursor)
            log.debug("Image picker: Crosshair image has been set.")

    def set_preview_icon(self, img: str) -> None:
        if not os.path.exists(img):
            return

        self.ui.image_preview.setIcon(QIcon(img))
        self.ui.image_preview.setText("")
        self.ui.image_preview.setIconSize(self.ui.image_preview.size() * 0.8)
        log.debug(f"Preview image has been set: {os.path.basename(img)}")

    def on_crosshair_image_set(self, disable: bool = True) -> None:
        self.ui.color_preview.setDisabled(disable)
        self.ui.border_color_preview.setDisabled(disable)
        self.ui.border_slider.setDisabled(disable)

        if disable:
            self.ui.set_color_picker_btn_style(self.ui.color_preview, "white", "#262b3d")
            self.ui.set_color_picker_btn_style(self.ui.border_color_preview, "white", "#262b3d")
        else:
            self.ui.set_color_picker_btn_style(self.ui.color_preview, "black", self.model.color)
            self.ui.set_color_picker_btn_style(self.ui.border_color_preview, "black", self.model.bcolor)

        self.ui.color_preview.setText("//" if disable else self.model.color)
        self.ui.border_color_preview.setText("//" if disable else self.model.bcolor)

        self.ui.color_preview.setToolTip("Disabled" if disable else "")
        self.ui.border_color_preview.setToolTip("Disabled" if disable else "")
        self.ui.border_slider.setToolTip("Disabled" if disable else "")

    @Slot()
    def set_crosshair_visibility(self) -> None:
        self.ui.bus.crosshairVisibilityChanged.emit()  # tell main window to update crosshair visibility
        b = self.ui.hide_btn
        b.setText("Hide Crosshair") if b.text() == "Show Crosshair" else b.setText("Show Crosshair")
        log.debug(f"Crosshair visibily set to: {not b.text() == "Show Crosshair"}")
