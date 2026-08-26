from __future__ import annotations
import logging
from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QVBoxLayout, QMenu, QWidget
from PySide6.QtGui import QCloseEvent, QIcon, QAction, QCursor
from PySide6.QtCore import Qt, QPoint, Slot, Signal

from app.core.utils import reposition_window
from app.core.types import CrosshairMode
from app.widgets import CrosshairWidget

if TYPE_CHECKING:
    from app.core.bus import AppBus
    from app.core.services.hotkey_service import HotkeyManager

log = logging.getLogger(__name__)


class MainView(QWidget):
    windowPositionChanged = Signal(tuple)

    def __init__(self, bus: AppBus, hotkey_manager: HotkeyManager) -> None:
        super().__init__()
        self.bus = bus
        self.hotkey_manager = hotkey_manager

        self.drag_pos: Optional[QPoint] = None

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("HolySight")
        self.setWindowIcon(QIcon(":/app/assets/icons/holy_sight.png"))
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
        self.tray_icon.setIcon(QIcon(":/app/assets/icons/holy_sight.png"))
        self.tray_icon.setToolTip("HolySight")

        self.tray_menu = QMenu()
        self.tray_menu.setObjectName("WIN_trayMenu")
        self.tray_crosshair_settings = QAction("Open Settings")
        self.tray_menu.addAction(self.tray_crosshair_settings)
        self.tray_menu.addSeparator()
        self.tray_exit_app = QAction("Exit")
        self.tray_menu.addAction(self.tray_exit_app)
        self.tray_icon.setContextMenu(self.tray_menu)

    @Slot(int)
    def update_crosshair_size(self, size: int) -> None:
        self.crosshair.setFixedSize(size, size)
        self._set_visual_coord()
        log.debug(f"Update crosshair size: {size}")

    @Slot(str, object)
    def update_crosshair_img(self, img: str, data) -> None:
        self.set_crosshair_img(img)  # path or empty sting
        if not img:
            # restyle crosshair after image reset
            self.set_crosshair_style(data)

        log.debug(f"Update crosshair image: {img}")

    @Slot(float)
    def update_crosshair_opacity(self, opacity: int) -> None:
        self.setWindowOpacity(opacity)
        log.debug(f"Update crosshair opacity: {opacity}")

    @Slot(str)
    def update_crosshair_state(self, mode: CrosshairMode) -> None:
        if mode == CrosshairMode.MOVE:
            self.set_input_transparency(False)
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self.activateWindow()
        else:
            self.set_input_transparency(True)
            self.unsetCursor()

        self.bus.crosshairMode = mode
        log.debug(f"Update crosshair state. Crosshair is now `{mode}`")

    def set_crosshair_img(self, img : str = "") -> None:
        self.crosshair.set_image(img)

    @Slot(object)
    def set_crosshair_style(self, style) -> None:
        v = style()
        self.crosshair.set_style(*v)

    def set_input_transparency(self, enable: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enable)
        self.show()
        log.debug(f"Window transparency set to: `{enable}`")

    @Slot()
    def update_crosshair_visibility(self) -> None:
        c = self.crosshair
        c.setVisible(False) if c.isVisible() else c.setVisible(True)

    def show_tray_menu(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.tray_menu.popup(QCursor.pos())

    @Slot()
    def quit_app(self) -> None:
        log.debug("APP QUIT.")
        self.stop_global_listener()
        QApplication.quit()

    def _window_pos_as_crosshair(self) -> tuple[int, int]:
        center_x = self.pos().x() + (self.size().width() // 2)
        center_y = self.pos().y() + (self.size().height() // 2)

        return center_x, center_y

    def _set_visual_coord(self):
        rpos = self._window_pos_as_crosshair()
        self.windowPositionChanged.emit(rpos)

    def stop_global_listener(self):
        self.hotkey_manager.stop()

    # ----------------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.crosshair.geometry().contains(event.position().toPoint()):
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

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
            # set WindowTransparentForInput flag to flase
            self.bus.stateChangedFinished.emit()

        # move window with arrow keys
        elif event.key() == Qt.Key.Key_Left:
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
