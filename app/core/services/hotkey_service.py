from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from pynput import keyboard
from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from app.core.bus import AppBus

log = logging.getLogger(__name__)


class HotkeyManager(QObject):
    def __init__(self, bus: AppBus) -> None:
        super().__init__()
        self.bus = bus

        self.listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+v": self.toggle_visibility,
            "<ctrl>+<alt>+x": self.center_crosshair,
            "<ctrl>+<alt>+s": self.show_settings,
            # "<ctrl>+<alt>+m": self.move_crosshair,
            # "<ctrl>+<alt>+c": self.set_crosshair_color,
            # "<ctrl>+<alt>+i": self.set_crosshair_img,
        })
        self.listener.start()

    def toggle_visibility(self) -> None:
        self.bus.globalVisibilityChanged.emit()

    def center_crosshair(self) -> None:
        self.bus.centerMainWindow.emit()

    def show_settings(self) -> None:
        self.bus.showSettingsWindow.emit()

    def stop(self) -> None:
        log.debug("LISTENER STOPPED.")
        self.listener.stop()
