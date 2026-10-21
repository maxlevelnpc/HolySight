from __future__ import annotations
import os
import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot

from app.core.types import ADSType


if TYPE_CHECKING:
    from app.core.services.hotkey_service import HotkeyManager
    from app.core.bus import AppBus
    from app.views import MainView
    from app.models import CrosshairModel

log = logging.getLogger(__name__)


class MainPresenter:
    def __init__(self, hotkey_manager: HotkeyManager, bus: AppBus, model: CrosshairModel, ui: MainView) -> None:
        self.hotkey = hotkey_manager
        self.model = model
        self.ui = ui
        self.bus = bus

        self.setupPresenter()

    def setupPresenter(self) -> None:
        # load settings in model
        self.model.load_config()

        self.apply_crosshair_settings()

        self.model.colorChanged.connect(self.ui.set_crosshair_color)
        self.model.sizeChanged.connect(self.ui.update_crosshair_size)
        self.model.opacityChanged.connect(self.ui.update_crosshair_opacity)
        self.model.imageChanged.connect(self.ui.set_crosshair_img)
        self.model.moveModeChanged.connect(self.ui.update_crosshair_move_state)
        self.model.visibilityChanged.connect(self.ui.update_crosshair_visibility)
        self.ui.windowPositionChanged.connect(lambda v: setattr(self.model, "pos", v))
        self.ui.returnPressed.connect(lambda v=False: setattr(self.model, "movable", v))
        self.bus.centerMainWindow.connect(self.ui.center_and_update_visual_pos)
        self.bus.rightMouseButtonStateChanged.connect(self.hide_crosshair_on_rmb)
        self.bus.preferencesChanged.connect(self.update_additional_settings)
        self.ui.tray_crosshair_settings.triggered.connect(self.bus.showSettingsWindow)
        self.ui.tray_exit_app.triggered.connect(self.quit_app)
        self.ui.tray_icon.activated.connect(self.ui.show_tray_menu)
        QApplication.instance().aboutToQuit.connect(self.save_settings)

    def apply_crosshair_settings(self) -> None:
        """apply loaded config data at app init"""
        color = self.model.color
        size = self.model.size
        img = self.model.image
        opacity = self.model.opacity

        self.ui.crosshair.set_style(size=size)
        log.debug(f'Set fixed size for crosshair: W: {size} H: {size}')

        if img:
            if os.path.exists(img):
                self.ui.set_crosshair_img(img)
                log.debug(f"Image exist. Set custom image: `{os.path.basename(img)}`")
            else:
                self.ui.set_crosshair_color(color)
                log.debug(f"Image path exist but the file is missing `{img}`. Set crosshair Color: `{color}`")
        else:
            self.ui.set_crosshair_color(color)
            log.debug(f"Set crosshair Color: {color}")

        self.ui.setWindowOpacity(opacity)
        log.debug(f"Set crosshair opacity: `{opacity}`")

        self.reposition_crosshair()
        log.debug("Crosshair repositioned. Position resolved.\n")

    @Slot()
    def save_settings(self) -> None:
        """Save current settings at exit"""
        config_data = {
            "crosshair_data": {
                "ch_color": self.model.color,
                "ch_size": self.model.size,
                "ch_opacity": self.model.opacity,
                "ch_image": self.model.image,
                "ch_pos": self.model.pos,
            },
            "additional_settings": {
                "hide_on_rmb": self.model.hide_on_rmb and self.model.hide_on_rmb.value
            }
        }

        self.model.service.save_config_data(config_data)

    def reposition_crosshair(self) -> None:
        """Move crosshair to saved coord pos or center it"""
        if self.model.pos is None:
            self.ui.center_crosshair()
            # update crosshair pos in model
            self.model.pos = self.ui.get_crosshair_pos()
            return

        x, y = self.model.pos
        win_pos = self.ui.get_window_pos((x, y))
        self.ui.move(*win_pos)

    def update_additional_settings(self, data: dict) -> None:
        rmb = data.get("rmb")

        self.model.hide_on_rmb = rmb
        # init state must be shown for HODL
        if self.model.hidden and rmb == ADSType.HOLD:
            self.model.hidden = False

    def hide_crosshair_on_rmb(self, pressed: bool) -> None:
        if self.model.hide_on_rmb == ADSType.TOGGLE:
            if not pressed:  # on clicked
                self.model.hidden = not self.model.hidden

        elif self.model.hide_on_rmb == ADSType.HOLD:
            self.model.hidden = pressed

    @Slot()
    def quit_app(self) -> None:
        log.debug("APP QUIT.")
        self.hotkey.stop()
        QApplication.quit()
