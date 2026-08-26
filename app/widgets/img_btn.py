import os
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal

from app.core.constants import SUPPORTED_EXTS


class ImageDropButton(QPushButton):
    imageDropped = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(60, 60)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            _, ext = os.path.splitext(file_path.lower())

            if ext.lstrip('.') in SUPPORTED_EXTS:
                event.acceptProposedAction()
                self.setCursor(Qt.CursorShape.DragCopyCursor)

    def dragLeaveEvent(self, event) -> None:
        self.unsetCursor()
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.imageDropped.emit(file_path)
            event.acceptProposedAction()

        self.unsetCursor()
