from __future__ import annotations
import os
import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, QTimer

from app.core.utils import reposition_window


if TYPE_CHECKING:
    from app.views import MainView
    from app.models import CrosshairModel

log = logging.getLogger(__name__)


class MainPresenter:
    def __init__(self, model: CrosshairModel, ui: MainView) -> None:
        super().__init__()
        self.model = model
        self.ui = ui

        self.setupBehaviour()

    def setupBehaviour(self) -> None:
        # load settings in model
        self.model.load_config()

        self.apply_crosshair_settings()

        self.model.colorChanged.connect(self.ui.set_crosshair_style)
        self.model.sizeChanged.connect(self.ui.update_crosshair_size)
        self.model.opacityChanged.connect(self.ui.update_crosshair_opacity)
        self.model.imageChanged.connect(self.ui.update_crosshair_img)
        self.model.borderColorChanged.connect(self.ui.set_crosshair_style)
        self.model.borderSizeChanged.connect(self.ui.set_crosshair_style)
        self.ui.windowPositionChanged.connect(lambda v: setattr(self.model, "pos", v))
        self.ui.bus.stateChanged.connect(self.ui.update_crosshair_state)
        self.ui.bus.crosshairVisibilityChanged.connect(self.ui.update_crosshair_visibility)
        self.ui.bus.activateMainWindow.connect(self.ui.activate_window)
        self.ui.bus.centerMainWindow.connect(lambda: reposition_window(self.ui))
        self.ui.tray_crosshair_settings.triggered.connect(self.ui.bus.showSettingsWindow)
        self.ui.tray_exit_app.triggered.connect(self.ui.quit_app)
        QApplication.instance().aboutToQuit.connect(self.save_settings)

        QTimer.singleShot(300, lambda: self.ui.crosshair.setVisible(True))

    def apply_crosshair_settings(self) -> None:
        """apply loaded config data at app init"""
        color = self.model.color
        size = self.model.size
        img = self.model.image
        opacity = self.model.opacity
        bcolor = self.model.bcolor
        bsize = self.model.bsize

        self.ui.crosshair.setFixedSize(size, size)
        log.debug(f'Set fixed size for crosshair: W: {size} H: {size}')

        if img and os.path.exists(img):
            self.ui.set_crosshair_img(img)
            log.debug(f"Image exist. Set custom image: `{os.path.basename(img)}`")
        else:
            self.ui.set_crosshair_style(self.model.get_style_req)
            log.debug(f"Set crosshair Color: {color}, BColor: {bcolor} and BSize: {bsize}.")
            
        self.ui.setWindowOpacity(opacity)
        log.debug(f"Set crosshair opacity: `{opacity}`")

        self.reposition_crosshair()
        log.debug(f"Crosshair repositioned. Position resolved.\n")

    @Slot()
    def save_settings(self) -> None:
        """Save current settings at exit"""
        config_data = {
            "ch_color": self.model.color,
            "ch_size": self.model.size,
            "ch_opacity": self.model.opacity,
            "ch_image": self.model.image,
            "ch_bcolor": self.model.bcolor,
            "ch_bsize": self.model.bsize,
            # save window pos
            "ch_pos": self.ui.pos().toTuple()
        }
        self.model.service.save_config_data(config_data)
    
    def reposition_crosshair(self) -> None:
        """Move crosshair to saved coord pos or center it"""
        x, y = self.model.pos

        # TODO: change the values in json
        # for the first time user open the app. or any beter way
        if x > 6666 or y > 6666:
            reposition_window(self.ui, True)
        else:
            self.ui.move(x, y)

        # crosshair widget visually represent window pos
        pos = self.ui._window_pos_as_crosshair()
        self.model.pos = pos
