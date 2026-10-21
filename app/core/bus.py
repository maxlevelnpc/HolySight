from PySide6.QtCore import Signal, QObject


class AppBus(QObject):
    showSettingsWindow = Signal()
    centerMainWindow = Signal()
    preferencesChanged = Signal(dict)
    rightMouseButtonStateChanged = Signal(bool)

    globalVisibilityChanged = Signal()
