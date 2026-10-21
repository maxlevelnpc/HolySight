from __future__ import annotations
import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup

from app.core.types import ADSType


log = logging.getLogger(__name__)


class PreferencesDialog(QDialog):
    def __init__(self, data: dict, parent=None) -> None:
        super().__init__(parent)
        self.data = data

        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle("Preferences")
        self.setFixedSize(260, 360)
        self.setObjectName("WIN_settings")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ----------------------------------------------------------------------------

        rmb_layout = QVBoxLayout()
        rmb_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        rmb_title = QLabel("Hide crosshair on Right Mouse Button")
        rmb_title.setObjectName("sectionTitleLabel")

        self.rmb_group = QButtonGroup()
        self.rmb_never = QRadioButton("Never")
        self.rmb_hold = QRadioButton("Hold ADS")
        self.rmb_hold.setProperty("type", ADSType.HOLD)
        self.rmb_toggle = QRadioButton("Toggle ADS")
        self.rmb_toggle.setProperty("type", ADSType.TOGGLE)
        self.rmb_group.addButton(self.rmb_never)
        self.rmb_group.addButton(self.rmb_hold)
        self.rmb_group.addButton(self.rmb_toggle)

        rmb_layout.addWidget(rmb_title)
        rmb_layout.addWidget(self.rmb_never)
        rmb_layout.addWidget(self.rmb_hold)
        rmb_layout.addWidget(self.rmb_toggle)

        self.save_btn = QPushButton("Save && Close")
        self.save_btn.clicked.connect(self.accept)

        # ----------------------------------------------------------------------------

        main_layout.addLayout(rmb_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apply_settings()

    def apply_settings(self) -> None:
        rmb = self.data.get("rmb")

        for btn in self.rmb_group.buttons():
            if btn.property("type") == rmb:
                btn.setChecked(True)

    def get_additional_settings(self) -> dict[str, Any]:
        data = {
            "rmb": self.rmb_group.checkedButton().property("type")
        }

        return data
