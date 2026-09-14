from typing import Any
from lib.features.hunt.window_selection_service import WindowSelectionService
from lib.features.hunt.hunt_config import save_hunt_config
from lib.ui.dialog_service import DialogService
from lib.i18n import t as i18n_t

class HuntController:
    def __init__(self, state_controller: Any, hunt_orchestrator: Any, app_root: Any):
        self.state_controller = state_controller
        self.hunt_orchestrator = hunt_orchestrator
        self.app_root = app_root

    def request_start_hunt(self) -> None:
        if self.state_controller.is_bot_running():
            return

        validation_error = WindowSelectionService.validate_prerequisites(
            self.state_controller.hunt_selected,
            self.state_controller.win_items,
            self.state_controller.hunt_cfg,
            self.state_controller.current_window_bounds
        )
        if validation_error:
            DialogService.show_error(i18n_t("error_title"), validation_error, parent=self.app_root)
            return

        try:
            from lib.ui.controllers.hunt_config_controller import HuntConfigController
            cfg = HuntConfigController().build_config(self.state_controller)
        except Exception as e:
            DialogService.show_error(
                i18n_t("error_title"), i18n_t("invalid_hunt").format(e=e), parent=self.app_root
            )
            return

        save_hunt_config(cfg)
        self.state_controller.hunt_cfg = cfg

        if self.hunt_orchestrator:
            self.hunt_orchestrator.start_hunt(self.state_controller.hunt_cfg)

    def request_stop_hunt(self) -> None:
        if self.hunt_orchestrator:
            self.hunt_orchestrator.stop_hunt()
