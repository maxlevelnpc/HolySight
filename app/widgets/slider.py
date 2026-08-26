from PySide6.QtWidgets import QSlider, QToolTip, QStyleOptionSlider, QStyle
from PySide6.QtCore import Qt, QPoint, QTimer


class Slider(QSlider):
    def __init__(self, parent=None, opacity_mode=False):
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.opacity_mode = opacity_mode

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(1000)
        self._hide_timer.timeout.connect(QToolTip.hideText)

        self.valueChanged.connect(self._show_tooltip)

        self.sliderReleased.connect(QToolTip.hideText)

    def _show_tooltip(self, value: int):
        display_value = f"{value / 10.0:.1f}" if self.opacity_mode else str(value)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            opt,
            QStyle.SubControl.SC_SliderHandle,
            self
        )

        global_pos = self.mapToGlobal(handle_rect.center() + QPoint(0, -40))
        QToolTip.showText(global_pos, display_value, self)

        if not self.isSliderDown():
            self._hide_timer.start()

    def focusOutEvent(self, event):
        QToolTip.hideText()
        self._hide_timer.stop()
        super().focusOutEvent(event)
