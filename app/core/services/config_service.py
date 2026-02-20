import logging
import json
from typing import Final
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from app.core.types import ConfigData

log = logging.getLogger(__name__)


DEFAULT_CONFIG: Final[ConfigData] = {
    "ch_color": "#ff0000",
    "ch_size": 20,
    "ch_opacity": 1.0,
    "ch_image": "",
    "ch_bcolor": "#0078cf",
    "ch_bsize": 0,
    "ch_pos": (99999, 99999)
}


class ConfigService:
    def __init__(self) -> None:
        config_dir = Path(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        )
        config_dir.mkdir(parents=True, exist_ok=True)

        self.cfg_path = config_dir / "settings.json"        

    def load_config_data(self) -> ConfigData:
        if not self.cfg_path.exists():
            return DEFAULT_CONFIG.copy()

        try:
            with self.cfg_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}  # type: ignore
        except Exception as e:
            log.error(f"Failed to load settings: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config_data(self, config_data: ConfigData) -> None:
        try:
            with self.cfg_path.open("w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save settings: {e}")