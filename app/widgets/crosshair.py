import os

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPixmap
from PySide6.QtCore import Qt, QRectF


class CrosshairWidget(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.ch_color = QColor("green")
        self.ch_size = 20
        self.ch_bcolor = QColor("black")
        self.ch_bsize = 0
        self.ch_pixmap = None
        
        self._pen = QPen(self.ch_bcolor, self.ch_bsize)
        self._brush = QBrush(self.ch_color)
        
        self._sync_container_size()

    def _sync_container_size(self):
        # total size = diameter + border on both sides
        total_dim = self.ch_size + (self.ch_bsize * 2)
        self.setFixedSize(int(total_dim), int(total_dim))
        
        # center the widget in parent whenever it resizes
        x = (self.parentWidget().width() - self.width()) // 2
        y = (self.parentWidget().height() - self.height()) // 2
        self.move(x, y)

    def set_style(self, color=None, size=None, bcolor=None, bsize=None):
        if color: 
            self.ch_color = QColor(color)
            self._brush.setColor(color)
        if bcolor: 
            self.ch_bcolor = QColor(bcolor)
            self._pen.setColor(bcolor)
        if bsize is not None: 
            self.ch_bsize = bsize
            self._pen.setWidth(bsize)
        if size is not None: 
            self.ch_size = size

        self._sync_container_size()
        self.update()
    
    def set_image(self, img: str):
        if img and os.path.exists(img):
            self.ch_pixmap = QPixmap(img)
        else:
            self.ch_pixmap = None
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        # draw the border outside
        margin = self.ch_bsize / 2 if self.ch_bsize > 0 else 0
        content_rect = QRectF(self.rect()).adjusted(margin, margin, -margin, -margin)

        if self.ch_pixmap and not self.ch_pixmap.isNull():
            p.drawPixmap(content_rect.toRect(), self.ch_pixmap)
        else:
            p.setPen(self._pen) if self.ch_bsize > 0 else p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self._brush) if self.ch_color.alpha() > 0 else p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(content_rect)
