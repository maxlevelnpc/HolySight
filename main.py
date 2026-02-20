import sys

from PySide6.QtWidgets import QApplication

from app.views import MainView, SettingsView
from app.presenters import MainPresenter, SettingsPresenter
from app.models import CrosshairModel
from app.core.services import ConfigService, HotkeyManager
from app.core.bus import AppBus
from app.core.utils import setup_logging, load_style

from app.assets import res_rc

setup_logging()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("MaxLevelNPC")
    app.setApplicationName("HolySight")
    
    app.setQuitOnLastWindowClosed(False)

    service = ConfigService()
    model = CrosshairModel(service)
    bus = AppBus()
    hotkey = HotkeyManager(bus)
    main_view = MainView(bus, hotkey)
    settings_view = SettingsView(bus)
    MainPresenter(model, main_view)
    SettingsPresenter(model, settings_view)

    main_view.show()
    settings_view.show()
    main_view.tray_icon.show()

    stylesheet = load_style(":/app/assets/styles/styles.css")
    app.setStyleSheet(stylesheet)

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
