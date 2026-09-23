from typing import Dict, Any

class SetupTabController:
    """Controller for SetupTab to manage specific configuration reads and states."""
    def __init__(self, app_state):
        self.app_state = app_state

    def get_target_key(self) -> str:
        return str(self.app_state.get_hunt_config_value("target_key", "TAB"))

    def get_attack_press_ms(self) -> str:
        return str(self.app_state.get_hunt_config_value("attack_press_ms", 60))

    def get_target_cycle_delay(self) -> str:
        return str(self.app_state.get_hunt_config_value("target_cycle_delay", 0.2))

    def get_search_interval(self) -> str:
        return str(self.app_state.get_hunt_config_value("search_interval", 0.25))

    def get_attack_interval(self) -> str:
        return str(self.app_state.get_hunt_config_value("attack_interval", 0.15))

    def get_lost_timeout_sec(self) -> str:
        return str(self.app_state.get_hunt_config_value("lost_timeout_sec", 1.2))

    def get_attack_min_duration_sec(self) -> str:
        return str(self.app_state.get_hunt_config_value("attack_min_duration_sec", 1.5))

    def get_rois(self) -> Dict[str, Any]:
        return self.app_state.get_hunt_config_value("rois", {})

    def set_roi(self, key: str, region: list) -> bool:
        rois = self.get_rois()
        rois[key] = region
        self.app_state.set_hunt_config_value("rois", rois)
        return self.app_state.save_hunt_config()
