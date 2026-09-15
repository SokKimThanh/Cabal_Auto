from typing import Any
from lib.ui.dialog_service import DialogService
from lib.features.hunt.hunt_config import save_hunt_config
from lib.ui.controllers.hunt_config_controller import HuntConfigController

class GlobalConfigController:
    """Controller responsible for handling global configuration applies."""
    def __init__(self, state_controller: Any, hotkey_controller: Any, translation_func: Any, app_instance: Any = None):
        self.state_controller = state_controller
        self.hotkey_controller = hotkey_controller
        self._t = translation_func
        self.app_instance = app_instance

    def apply_all_configs(self) -> None:
        """Global apply handler - saves all settings across all tabs."""
        try:
            # Ensure canonical schemas
            if not isinstance(self.state_controller.hunt_cfg.get("monster_rotation"), list):
                self.state_controller.hunt_cfg["monster_rotation"] = getattr(
                    self.app_instance, "monster_rotation", getattr(self.state_controller, "monster_rotation", [])
                )
            if not isinstance(self.state_controller.hunt_cfg.get("skill_slots"), list):
                self.state_controller.hunt_cfg["skill_slots"] = []

            apply_setup_settings = getattr(self.app_instance, "_apply_setup_settings", None)
            if callable(apply_setup_settings):
                apply_setup_settings(save_to_file=False)  # pylint: disable=not-callable

            try:
                self.state_controller._validate_slot_key_duplicates()
            except ValueError as ve:
                DialogService.show_error(self._t("error_title"), str(ve))
                return
            except Exception:
                pass

            cfg = HuntConfigController().build_config(self.state_controller)

            if "global_hotkeys" in cfg:
                hk = cfg["global_hotkeys"]
                all_keys = [
                    hk.get("start_key"),
                    hk.get("stop_key"),
                    hk.get("library_manager_key"),
                    hk.get("vision_wizard_key"),
                    hk.get("monster_editor_key"),
                    hk.get("build_manager_key"),
                ]
                all_keys = [k for k in all_keys if k]
                if len(all_keys) != len(set(all_keys)):
                    lang = getattr(self.state_controller, "lang", "en")
                    DialogService.show_error(
                        self._t("error_title"),
                        (
                            "All hotkeys must be different!"
                            if lang == "en"
                            else "Tất cả phím tắt phải khác nhau!"
                        ),
                    )
                    return

                self.state_controller.hunt_cfg = cfg  # Update instance config first
                self.hotkey_controller.unregister_all()
                self.hotkey_controller.register_all()

            if not save_hunt_config(cfg):
                raise RuntimeError("Could not save hunt configuration")
            self.state_controller.hunt_cfg = cfg

            self.state_controller._clear_unsaved_changes()

            self.state_controller.set_ui_var('hunt_status', self._t("all_saved"))

            DialogService.show_info(
                self._t("success_title"), self._t("settings_applied_message")
            )
        except Exception as e:
            DialogService.show_error(
                self._t("error_title"), f"Failed to apply settings: {e}"
            )
