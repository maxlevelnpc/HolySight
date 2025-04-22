from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication, QMenu, QLabel, QSlider, QVBoxLayout, QWidget, QWidgetAction, QColorDialog, QPushButton, QHBoxLayout,
    QFileDialog
)

menu_style = """
    QMenu {
        background-color: #2c2c2c;
        color: white;
        border: 1px solid #444;
        padding: 5px;
        font-family: Segoe UI;
        font-size: 12px;
    }
    QMenu::item {
        padding: 2px 4px 2px 1px;
        background-color: transparent;
        spacing: 1px;
    }
    QMenu::icon {
        padding-left: 4px;
    }
    QMenu::item:selected {
        background-color: #444;
        color: #fff;
    }
    QMenu::separator {
        height: 1px;
        background: #555;
        margin: 5px 0;
    }
"""


class SystemTrayMenu(QMenu):
    def __init__(self, parent: QWidget, crosshair: QLabel):
        super().__init__(parent)
        self._ch_color: str = parent.ch_color  # type: ignore[attr-defined]
        self._ch_border_color: str = parent.ch_border_color  # type: ignore[attr-defined]
        self._ch_size: int = parent.ch_size  # type: ignore[attr-defined]
        self._ch_opacity: int = parent.ch_opacity  # type: ignore[attr-defined]
        self._ch_border_thickness: int = parent.ch_border_thickness  # type: ignore[attr-defined]
        self._ch_img = parent.ch_img  # type: ignore[attr-defined]
        self.crosshair = crosshair

        self.setStyleSheet(menu_style)

        # ////////////////////////////////////////////////////////////////////////////////////////////

        self.slider_action = QWidgetAction(self)
        self.slider_widget = self._create_sizer_slider()
        self.slider_action.setDefaultWidget(self.slider_widget)
        self.addAction(self.slider_action)

        self.opacity_slider_action = QWidgetAction(self)
        self.opacity_slider_widget = self._create_opacity_slider()
        self.opacity_slider_action.setDefaultWidget(self.opacity_slider_widget)
        self.addAction(self.opacity_slider_action)

        self.border_slider_action = QWidgetAction(self)
        self.border_slider_widget = self._create_border_slider()
        self.border_slider_action.setDefaultWidget(self.border_slider_widget)
        self.addAction(self.border_slider_action)

        self.color_button_action = QWidgetAction(self)
        self.color_button = self._create_color_button()
        self.color_button_action.setDefaultWidget(self.color_button)
        self.addAction(self.color_button_action)

        self.addSeparator()

        self.custom_img = self.addAction(QIcon(":/resources/icon_2.png"), "Reset" if self._ch_img else "Set image")
        self.custom_img.triggered.connect(self.reset_custom_img if self._ch_img else self.set_custom_img)

        self.show_action = self.addAction(QIcon(":/resources/icon_3.png"), "Hide")
        self.show_action.triggered.connect(self.toggle_crosshair)

        quit_action = self.addAction(QIcon(":/resources/icon_1.png"), "Exit")
        quit_action.triggered.connect(self.exit_app)

    def _create_color_button(self) -> QWidget:
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(22, 22)
        self.color_btn.setToolTip("Crosshair color")
        self.color_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._ch_color};
                border: 1px solid black;
            }}
            QPushButton:hover {{
                background-color: {self._ch_color};
            }}
            """
        )
        self.color_btn.clicked.connect(self.open_ch_color_picker)

        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedSize(22, 22)
        self.border_color_btn.setToolTip("Crosshair border color")
        self.border_color_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._ch_border_color};
                border: 1px solid black;
            }}
            QPushButton:hover {{
                background-color: {self._ch_border_color};
            }}
            """
        )
        self.border_color_btn.clicked.connect(self.open_ch_border_color_picker)

        self.move_cursor_btn = QPushButton()
        self.move_cursor_btn.setFixedSize(22, 22)
        self.move_cursor_btn.setToolTip("Move crosshair")
        self.move_cursor_btn.setIcon(QIcon(":/resources/move_cursor.png"))
        self.move_cursor_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            """
        )
        self.move_cursor_btn.setToolTip("Move Crosshair")
        self.move_cursor_btn.clicked.connect(self.parent().enable_move_mode)  # type: ignore[attr-defined]

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.border_color_btn)
        layout.addWidget(self.move_cursor_btn)
        return container

    def open_ch_color_picker(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 1px solid black;
                }}
                QPushButton:hover {{
                    background-color: {color.name()};
                }}
                """
            )
            self.crosshair.setStyleSheet(self.crosshair.styleSheet() + f"background-color: {color.name()};")
            self.parent().ch_color = color.name()

    def open_ch_border_color_picker(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 1px solid black;
                }}
                QPushButton:hover {{
                    background-color: {color.name()};
                }}
                """
            )
            self.crosshair.setStyleSheet(
                self.crosshair.styleSheet() + f"border: {self._ch_border_thickness}px solid {color.name()};"
            )
            self.parent().ch_border_color = color.name()

    def _create_sizer_slider(self) -> QWidget:
        slider_widget = QWidget()

        sizer_slider = QSlider(Qt.Orientation.Horizontal)
        sizer_slider.setFixedWidth(80)
        sizer_slider.setToolTip("Size")
        sizer_slider.setRange(6, 400)  # Bigger value for psychopath 🗿
        sizer_slider.setValue(self._ch_size)
        sizer_slider.valueChanged.connect(self._adjust_crosshair_size)

        layout = QVBoxLayout(slider_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sizer_slider)
        return slider_widget

    def _create_opacity_slider(self) -> QWidget:
        opacity_slider_widget = QWidget()

        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setFixedWidth(80)
        opacity_slider.setToolTip("Opacity")
        opacity_slider.setRange(0, 255)
        opacity_slider.setValue(self._ch_opacity * 255)
        opacity_slider.valueChanged.connect(self._adjust_crosshair_opacity)

        layout = QVBoxLayout(opacity_slider_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(opacity_slider)
        return opacity_slider_widget

    def _create_border_slider(self) -> QWidget:
        border_slider_widget = QWidget()

        border_slider = QSlider(Qt.Orientation.Horizontal)
        border_slider.setFixedWidth(80)
        border_slider.setToolTip("Border thickness")
        border_slider.setRange(0, 10)
        border_slider.setValue(self._ch_border_thickness)
        border_slider.valueChanged.connect(self._adjust_crosshair_border)

        layout = QVBoxLayout(border_slider_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(border_slider)
        return border_slider_widget

    def _adjust_crosshair_size(self, value: int) -> None:
        size = value
        border_radius = size // 2
        self.parent().ch_size = size

        self.crosshair.setFixedSize(size, size)

        if self.crosshair.pixmap() is not None and self._ch_img is not None:
            self.crosshair.setStyleSheet(
                self.crosshair.styleSheet() + f"background-color: transparent; border-radius: {border_radius}px;"
            )
            scaled = QPixmap(self._ch_img).scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.crosshair.setPixmap(scaled)
        else:
            self.crosshair.setStyleSheet(self.crosshair.styleSheet() + f"border-radius: {border_radius}px;")

    def _adjust_crosshair_opacity(self, value: float) -> None:
        """Adjust the crosshair opacity based on the slider value"""
        opacity = value / 255  # Convert the slider value (0-255) to a float (0.0 - 1.0)
        self.parent().setWindowOpacity(opacity)
        self.parent().ch_opacity = opacity

    def _adjust_crosshair_border(self, value: int) -> None:
        """Adjust the border thickness of the crosshair"""
        self.crosshair.setStyleSheet(self.crosshair.styleSheet() + f"border: {value}px solid {self._ch_border_color};")
        self.parent().ch_border_thickness = value

    def set_custom_img(self) -> None:
        img, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Crosshair Image",
            filter=(
                "All Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif *.webp);;"
                "PNG Files (*.png);;"
                "JPEG Files (*.jpg *.jpeg);;"
                "SVG Files (*.svg);;"
                "Bitmap Files (*.bmp);;"
                "GIF Files (*.gif);;"
                "WebP Files (*.webp)"
            )
        )

        if not img:
            return

        self.crosshair.setStyleSheet(self.crosshair.styleSheet() + f"background-color: transparent;")

        pixmap = QPixmap(img)
        self.crosshair.setPixmap(
            pixmap.scaled(
                self.crosshair.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.custom_img.setText("Reset")
        self.custom_img.triggered.disconnect(self.set_custom_img)
        self.custom_img.triggered.connect(self.reset_custom_img)

        self._ch_img = img
        self.parent().ch_img = img

    def reset_custom_img(self) -> None:
        self._ch_img = None
        self.parent().ch_img = None

        self.crosshair.setPixmap(QPixmap())  # Clear pixmap
        self.crosshair.setFixedSize(self._ch_size, self._ch_size)
        self.crosshair.setStyleSheet(
            f"background-color: {self._ch_color};"
            f"border: {self._ch_border_thickness}px solid {self._ch_border_color};"
            f"border-radius: {self._ch_size // 2}px;"
        )
        self.custom_img.setText("Set image")
        self.custom_img.triggered.disconnect(self.reset_custom_img)
        self.custom_img.triggered.connect(self.set_custom_img)

    def toggle_crosshair(self) -> None:
        if self.parent().isVisible():
            self.parent().hide()
            self.show_action.setText("Show")
        else:
            self.parent().show()
            self.parent().raise_()
            self.show_action.setText("Hide")

    def exit_app(self) -> None:
        self.parent()._allow_close = True
        QApplication.quit()
