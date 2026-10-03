from PySide6.QtCore import Signal, QObject


class AppBus(QObject):
    showSettingsWindow = Signal()
    centerMainWindow = Signal()

    globalVisibilityChanged = Signal()
