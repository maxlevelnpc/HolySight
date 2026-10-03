import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.views import MainView, SettingsView
from app.presenters import MainPresenter, SettingsPresenter
from app.models import CrosshairModel
from app.core.services import ConfigService, HotkeyManager
from app.core.bus import AppBus
from app.core.utils import setup_logging, load_style

from app.assets import res_rc


log_dir = Path(os.environ["LOCALAPPDATA"]) / "MaxLevelNPC" / "HolySight"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "app.log"

setup_logging(log_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("MaxLevelNPC")
    app.setApplicationName("HolySight")
    app.setQuitOnLastWindowClosed(False)

    service = ConfigService()
    model = CrosshairModel(service)
    bus = AppBus()
    hotkey = HotkeyManager(bus)
    main_view = MainView()
    settings_view = SettingsView()
    MainPresenter(hotkey, bus, model, main_view)
    SettingsPresenter(bus, model, settings_view)

    stylesheet = load_style(":/styles.css")
    app.setStyleSheet(stylesheet)

    main_view.show()
    settings_view.show()
    main_view.tray_icon.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
