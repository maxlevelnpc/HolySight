import sys, json, logging  # noqa E401
from typing import Optional

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QLabel, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QPoint

from widgets import SystemTrayMenu


class HolySight(QWidget):
    def __init__(self):
        super().__init__()
        self._allow_close = False
        self.is_move_mode = False
        self.drag_position: Optional[QPoint] = None

        self.ch_color: str = "red"
        self.ch_border_color: str = "black"
        self.ch_size: int = 8
        self.ch_opacity: float = 1.0
        self.ch_border_thickness: int = 0
        self.ch_img: Optional[str] = None
        self.ch_pos_x: Optional[int] = None
        self.ch_pos_y: Optional[int] = None

        self.load_settings()  # Load settings before packing widgets

        self.setWindowTitle("HolySight")
        self.setWindowIcon(QIcon(":/resources/holy_sight.png"))
        self.setFixedSize(500, 500)
        self.setWindowOpacity(self.ch_opacity)

        # Remove hints and set the window to transparent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # ///////////////////////////////////////////////////////////////////////////

        # Create the crosshair label
        self.crosshair = QLabel(self)
        self.crosshair.setFixedSize(self.ch_size, self.ch_size)
        self.crosshair.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.ch_img:
            self.crosshair.setStyleSheet(
                f"background-color: transparent; "
                f"border: {self.ch_border_thickness}px solid {self.ch_border_color}; "
                f"border-radius: {self.ch_size // 2}px;"
            )
            self.set_pixmap(QPixmap(self.ch_img))
        else:
            self.crosshair.setStyleSheet(
                f"background-color: {self.ch_color}; "
                f"border: {self.ch_border_thickness}px solid {self.ch_border_color}; "
                f"border-radius: {self.ch_size // 2}px;"
            )

        # Put the crosshair label inside a layout to center it
        layout = QVBoxLayout()
        layout.addWidget(self.crosshair, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # ///////////////////////////////////////////////////////////////////////////

        # Create the system tray menu
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(":/resources/holy_sight.png"))
        self.tray_menu = SystemTrayMenu(self, self.crosshair)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)

        # ///////////////////////////////////////////////////////////////////////////

        self.disable_move_mode(init=True)

        # Show the crosshair window and system tray icon
        self.tray_icon.show()
        self.show()

    def enable_move_mode(self) -> None:
        self.is_move_mode = True
        self.tray_menu.move_cursor_btn.setToolTip("Exit Move Mode")
        self.tray_menu.move_cursor_btn.clicked.disconnect()
        self.tray_menu.move_cursor_btn.clicked.connect(self.disable_move_mode)
        self.tray_menu.close()

        if sys.platform == "win32":
            import win32gui
            import win32con
            window_handle = self.winId().__int__()
            ex_style = win32gui.GetWindowLong(window_handle, win32con.GWL_EXSTYLE)
            ex_style &= ~win32con.WS_EX_TRANSPARENT  # Remove WS_EX_TRANSPARENT, so we can move the window
            win32gui.SetWindowLong(window_handle, win32con.GWL_EXSTYLE, ex_style)

    def disable_move_mode(self, init=False) -> None:
        self.is_move_mode = False

        self.tray_menu.move_cursor_btn.setToolTip("Move Crosshair")
        self.tray_menu.move_cursor_btn.clicked.disconnect()
        self.tray_menu.move_cursor_btn.clicked.connect(self.enable_move_mode)  # type: ignore[attr-defined]

        if sys.platform == "win32":
            # Make everything click-trough
            import win32gui
            import win32con
            window_handle = self.winId().__int__()
            ex_style = win32gui.GetWindowLong(window_handle, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(window_handle, win32con.GWL_EXSTYLE, ex_style)
        else:
            if init:
                QMessageBox.warning(
                    self,
                    "Platform Warning",
                    f"This application is optimized for Windows. "
                    f"It may not work properly on <b>`{sys.platform}`</b>"
                )

    def center_window(self) -> None:
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_center = screen_geometry.center()
        window_rect = self.rect()
        window_center = window_rect.center()
        new_position = screen_center - window_center
        self.move(new_position)

    def tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle system tray click events"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.tray_menu.toggle_crosshair()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.tray_menu.open_ch_color_picker()

    def load_settings(self) -> None:
        try:
            with open("./config/settings.json", "r") as f:
                settings = json.load(f)

            self.ch_color = settings.get("ch_color", "red")
            self.ch_border_color = settings.get("ch_border_color", "black")
            self.ch_size = settings.get("ch_size", 8)
            self.ch_opacity = settings.get("ch_opacity", 1.0)
            self.ch_border_thickness = settings.get("ch_border_thickness", 0)
            self.ch_img = settings.get("ch_img", None)
            self.ch_pos_x = settings.get("ch_pos_x", None)
            self.ch_pos_y = settings.get("ch_pos_y", None)
        except FileNotFoundError:
            logging.warning("Settings file not found. Using default values.")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")

    def save_settings(self) -> None:
        settings = {
            "ch_color": self.ch_color,
            "ch_border_color": self.ch_border_color,
            "ch_size": self.ch_size,
            "ch_opacity": self.ch_opacity,
            "ch_border_thickness": self.ch_border_thickness,
            "ch_img": self.ch_img,
            "ch_pos_x": self.pos().x(),
            "ch_pos_y": self.pos().y()
        }

        try:
            with open("./config/settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.crosshair.setPixmap(
            pixmap.scaled(
                self.ch_size, self.ch_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def mousePressEvent(self, event):
        """Start dragging if clicking on move_cursor in move mode."""
        if self.is_move_mode and event.button() == Qt.MouseButton.LeftButton:
            # Check if the click is within move_cursor's geometry
            if self.crosshair.geometry().contains(event.position().toPoint()):
                self.drag_position = event.globalPosition().toPoint() - self.pos()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """Move the window if dragging in move mode."""
        if self.is_move_mode and event.buttons() & Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        """Center the window on double-click within move_cursor."""
        if self.is_move_mode and self.crosshair.geometry().contains(event.position().toPoint()):
            self.center_window()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """Exit move mode on Enter or Escape key."""
        if self.is_move_mode and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Escape):
            self.disable_move_mode()
            event.accept()
        else:
            event.ignore()

    def showEvent(self, event):
        """Restore saved position or center window on show."""
        if self.ch_pos_x is not None and self.ch_pos_y is not None:
            new_position = QPoint(self.ch_pos_x, self.ch_pos_y)
            self.move(new_position)
        else:
            self.center_window()

        super().showEvent(event)

    def closeEvent(self, event):
        """Override the closeEvent to save user settings when closing the app."""
        if self._allow_close:
            event.accept()
            self.save_settings()
        else:
            event.ignore()
