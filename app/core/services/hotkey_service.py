from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from pynput import keyboard, mouse
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

        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def toggle_visibility(self) -> None:
        self.bus.globalVisibilityChanged.emit()

    def center_crosshair(self) -> None:
        self.bus.centerMainWindow.emit()

    def show_settings(self) -> None:
        self.bus.showSettingsWindow.emit()

    def on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if button == mouse.Button.right:
            self.bus.rightMouseButtonStateChanged.emit(pressed)

    def stop(self) -> None:
        log.debug("LISTENER STOPPED.")
        self.listener.stop()
        self.mouse_listener.stop()
