import os

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QColor, QBrush, QPixmap
from PySide6.QtCore import Qt, QRectF


class CrosshairWidget(QLabel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.ch_color = QColor("green")
        self.ch_size = 20
        self.ch_pixmap = None

        self._brush = QBrush(self.ch_color)

        self._sync_container_size()

    def _sync_container_size(self) -> None:
        # total size is now strictly the shape diameter
        self.setFixedSize(int(self.ch_size), int(self.ch_size))

        # center the widget in parent whenever it resizes
        x = (self.parentWidget().width() - self.width()) // 2
        y = (self.parentWidget().height() - self.height()) // 2
        self.move(x, y)

    def set_style(self, color: str = None, size: int = None) -> None:
        if color:
            self.ch_color = QColor(color)
            self._brush.setColor(color)
        if size is not None:
            self.ch_size = size

        self._sync_container_size()
        self.update()

    def set_image(self, img: str) -> None:
        if img and os.path.exists(img):
            self.ch_pixmap = QPixmap(img)
        else:
            self.ch_pixmap = None
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        content_rect = QRectF(self.rect())

        if self.ch_pixmap and not self.ch_pixmap.isNull():
            p.drawPixmap(content_rect.toRect(), self.ch_pixmap)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self._brush) if self.ch_color.alpha() > 0 else p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(content_rect)
