from __future__ import annotations
import logging
from typing import Optional

from PySide6.QtWidgets import QSystemTrayIcon, QVBoxLayout, QMenu, QWidget
from PySide6.QtGui import QIcon, QAction, QCursor, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPoint, Slot, Signal, QRect

from app.core.utils import reposition_window
from app.widgets import CrosshairWidget

log = logging.getLogger(__name__)


class MainView(QWidget):
    windowPositionChanged = Signal(tuple)
    returnPressed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.drag_pos: Optional[QPoint] = None
        self._move_mode_active: bool = False

        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle("HolySight")
        self.setWindowIcon(QIcon(":/holy_sight.png"))
        self.setFixedSize(500, 500)
        self.setObjectName("WIN_main")

        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)  # stay on top + prevent Tool window to close
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput)  # click-thru

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------------------------------

        self.crosshair = CrosshairWidget(self)
        self.crosshair.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.crosshair.setObjectName("crosshair")
        self.crosshair.setVisible(False)

        main_layout.addWidget(self.crosshair, alignment=Qt.AlignmentFlag.AlignCenter)

        # ----------------------------------------------------------------------------

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(":/holy_sight.png"))
        self.tray_icon.setToolTip("HolySight")

        self.tray_menu = QMenu()
        self.tray_menu.setObjectName("WIN_trayMenu")
        self.tray_crosshair_settings = QAction("Settings")
        self.tray_menu.addAction(self.tray_crosshair_settings)
        self.tray_menu.addSeparator()
        self.tray_exit_app = QAction("Exit")
        self.tray_menu.addAction(self.tray_exit_app)
        self.tray_icon.setContextMenu(self.tray_menu)

    @Slot(int)
    def update_crosshair_size(self, size: int) -> None:
        self.crosshair.setFixedSize(size, size)
        self._set_visual_coord()
        self.update()
        log.debug(f"Update crosshair size: {size}")

    @Slot(str)
    def set_crosshair_img(self, img: str) -> None:
        self.crosshair.set_image(img)  # path or empty sting
        log.debug(f"Update crosshair image: {img}")

    @Slot(float)
    def update_crosshair_opacity(self, opacity: int) -> None:
        self.setWindowOpacity(opacity)
        log.debug(f"Update crosshair opacity: {opacity}")

    @Slot(str)
    def update_crosshair_move_state(self, movable) -> None:
        self._move_mode_active = movable
        if movable:
            self.set_input_transparency(False)
            self.activateWindow()
        else:
            self.set_input_transparency(True)

        log.debug(f"Update crosshair state. Movable: `{movable}`")

    def set_crosshair_color(self, color) -> None:
        self.crosshair.set_style(color)

    def set_input_transparency(self, enable: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enable)
        self.show()
        log.debug(f"Window transparency set to: `{enable}`")

    @Slot()
    def update_crosshair_visibility(self, hidden) -> None:
        self.crosshair.setVisible(not hidden)

    def show_tray_menu(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.tray_menu.popup(QCursor.pos())

    def _window_pos_as_crosshair(self) -> tuple[int, int]:
        center_x = self.pos().x() + (self.size().width() // 2)
        center_y = self.pos().y() + (self.size().height() // 2)

        return center_x, center_y

    def _set_visual_coord(self) -> None:
        rpos = self._window_pos_as_crosshair()
        self.windowPositionChanged.emit(rpos)

    # ----------------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if self.crosshair.geometry().contains(event.position().toPoint()):
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos is not None:
            # allow to move window by dragging crosshair widget
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            self._set_visual_coord()

    def mouseDoubleClickEvent(self, event) -> None:
        super().mouseDoubleClickEvent(event)
        if self.crosshair.geometry().contains(event.position().toPoint()):
            # center the overlay window
            reposition_window(self, True)
            self._set_visual_coord()

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        step = 1
        pos = self.pos()

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Escape):
            self.returnPressed.emit()
            log.debug("[MainWindow] Enter key pressed. Exit Move Mode.")

        # move window with arrow keys
        if event.key() == Qt.Key.Key_Left:
            self.move(pos - QPoint(step, 0))
            self._set_visual_coord()
        elif event.key() == Qt.Key.Key_Up:
            self.move(pos - QPoint(0, step))
            self._set_visual_coord()
        elif event.key() == Qt.Key.Key_Right:
            self.move(pos + QPoint(step, 0))
            self._set_visual_coord()
        elif event.key() == Qt.Key.Key_Down:
            self.move(pos + QPoint(0, step))
            self._set_visual_coord()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        if self._move_mode_active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            w = self.crosshair.width()
            h = self.crosshair.height()

            win_center = self.rect().center()

            rect = QRect(0, 0, w + 12, h + 12)
            rect.moveCenter(win_center)

            painter.setBrush(QColor(59, 130, 246, 25))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 4, 4)

            pen = QPen()
            pen.setColor(QColor(59, 130, 246, 200))
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setWidth(2)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.drawRoundedRect(rect, 4, 4)
