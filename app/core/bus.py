from PySide6.QtCore import Signal, QObject
from app.core.types import CrosshairMode


class AppBus(QObject):
    stateChanged = Signal(object)
    stateChangedFinished = Signal()
    crosshairVisibilityChanged = Signal()
    showSettingsWindow = Signal()
    activateMainWindow = Signal()
    centerMainWindow = Signal()

    def __init__(self) -> None:        
        super().__init__()
        self._curr_mode = CrosshairMode.GAME
    
    @property
    def crosshairMode(self) -> CrosshairMode:
        return self._curr_mode
    
    @crosshairMode.setter
    def crosshairMode(self, mode: CrosshairMode) -> None:
        self._curr_mode = mode
