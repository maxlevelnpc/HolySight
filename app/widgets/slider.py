from PySide6.QtWidgets import QSlider, QToolTip, QStyleOptionSlider, QStyle
from PySide6.QtCore import Qt, QPoint


class Slider(QSlider):
    def __init__(self, parent=None, opacity_mode=False):
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.opacity_mode = opacity_mode

        # Show tooltip while dragging
        self.sliderMoved.connect(self._show_tooltip)
        # Hide tooltip when released
        self.sliderReleased.connect(QToolTip.hideText)

    def _show_tooltip(self, value: int):
        display_value = f"{value / 255:.2f}" if self.opacity_mode else str(value)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            opt,
            QStyle.SubControl.SC_SliderHandle,
            self
        )
        global_pos = self.mapToGlobal(handle_rect.center() + QPoint(0, -40))  # slightly above handle
        QToolTip.showText(global_pos, display_value, self)