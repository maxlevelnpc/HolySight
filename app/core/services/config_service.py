import logging
import json
import os

from app.core.types import ConfigData

log = logging.getLogger(__name__)


class ConfigService:
    def __init__(self) -> None:
        self.cfg_path = os.path.join(os.getcwd(), "app", "data", "settings.json")
        
    def load_config_data(self) -> ConfigData:
        # default values
        config_data: ConfigData = {
            "ch_color": "#ff0000",
            "ch_size": 20,
            "ch_opacity": 1.0,
            "ch_image": "",
            "ch_bcolor": "#0078cf",
            "ch_bsize": 0,
            "ch_pos": (0, 0),
        }

        try:
            with open(self.cfg_path, "r") as f:
                config_data = json.load(f)
        except Exception as e:
            log.error(f"Failed to load settings: {e}")

        return config_data
    
    def save_config_data(self, config_data: ConfigData) -> None:
        try:
            with open(self.cfg_path, "w") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save settings: {e}")