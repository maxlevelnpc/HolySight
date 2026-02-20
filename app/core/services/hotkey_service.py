from __future__ import annotations
from typing import TYPE_CHECKING

from pynput import keyboard
from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from app.core.bus import AppBus


class HotkeyManager(QObject):
    def __init__(self, bus: AppBus) -> None:
        super().__init__()
        self.bus = bus
        
        self.listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+x": self.toggle_visibility,
            "<ctrl>+<alt>+c": self.center_crosshair
        })
        self.listener.start()

    def toggle_visibility(self) -> None:
        self.bus.crosshairVisibilityChanged.emit()

    def center_crosshair(self) -> None:
        self.bus.centerMainWindow.emit()

    def stop(self):
        print("LISTENER STOPPED.")
        self.listener.stop()

