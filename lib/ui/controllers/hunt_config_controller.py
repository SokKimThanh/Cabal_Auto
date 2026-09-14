import copy
from typing import Dict, Any

from lib.features.hunt.window_selection_service import WindowSelectionService
from lib.features.hunt.hunt_constants import (
    DEFAULT_TARGET_KEY,
    DEFAULT_TARGET_CYCLE_DELAY,
    DEFAULT_SEARCH_INTERVAL,
    DEFAULT_ATTACK_INTERVAL,
    DEFAULT_LOST_TIMEOUT,
    DEFAULT_ATTACK_MIN_DURATION,
    DEFAULT_ATTACK_PRESS_MS,
    DEFAULT_START_HOTKEY,
    DEFAULT_STOP_HOTKEY,
    DEFAULT_LIBRARY_MANAGER_KEY,
    DEFAULT_VISION_WIZARD_KEY,
    DEFAULT_MONSTER_EDITOR_KEY,
)

class HuntConfigController:
    """Controller responsible for building the hunt configuration from application state."""

    def build_config(self, state_controller: Any) -> Dict[str, Any]:
        """Builds and returns the hunt configuration dictionary based on UI state."""
        cfg = copy.deepcopy(state_controller.hunt_cfg)

        if not isinstance(cfg.get("skill_slots"), list):
            cfg["skill_slots"] = []

        if isinstance(getattr(state_controller, "hunt_selected", None), dict):
            cfg["window_title"] = state_controller.hunt_selected.get("title", "")
            cfg["window_pid"] = state_controller.hunt_selected.get("pid")
            cfg["window_hwnd"] = state_controller.hunt_selected.get("hwnd")

        bounds = WindowSelectionService.resolve_bounds(
            cfg, getattr(state_controller, "current_window_bounds", None)
        )
        WindowSelectionService.update_bounds(cfg, bounds)

        hunt_area = cfg.get("hunt_area")
        if isinstance(hunt_area, dict):
            hunt_area["window_title"] = cfg.get("window_title", "")

        if state_controller.get_ui_var("target_policy") is not None:
            cfg["target_policy"] = state_controller.get_ui_var("target_policy")

        simple_vars = {
            "target_key": ("setup_target_key_var", DEFAULT_TARGET_KEY),
            "target_cycle_delay": ("setup_target_cycle_var", DEFAULT_TARGET_CYCLE_DELAY),
            "search_interval": ("setup_search_interval_var", DEFAULT_SEARCH_INTERVAL),
            "attack_interval": ("setup_attack_interval_var", DEFAULT_ATTACK_INTERVAL),
            "lost_timeout_sec": ("setup_lost_timeout_var", DEFAULT_LOST_TIMEOUT),
            "attack_min_duration_sec": ("setup_attack_duration_var", DEFAULT_ATTACK_MIN_DURATION),
            "attack_press_ms": ("setup_press_ms_var", DEFAULT_ATTACK_PRESS_MS),
        }

        cfg["ui_mode"] = "advanced"

        if state_controller.get_ui_var("setup_template") is not None:
            cfg["template_path"] = state_controller.get_ui_var("setup_template")

        for key, (attr_name, default) in simple_vars.items():
            var = state_controller.get_ui_var(attr_name.replace("_var", ""))
            if var is None:
                cfg.setdefault(key, default)
                continue
            raw_value = var
            if isinstance(default, int):
                cfg[key] = int(raw_value or default)
            elif isinstance(default, float):
                cfg[key] = float(raw_value or default)
            else:
                cfg[key] = raw_value or default

        cfg["bring_to_front_each_cycle"] = bool(state_controller.get_ui_var("bring_front"))
        cfg["skill_slots"] = []
        _collect_func = getattr(state_controller, "_collect_skill_slots_func", None)
        if _collect_func is not None and callable(_collect_func):
            collected = _collect_func()  # pylint: disable=not-callable
            if isinstance(collected, list):
                for s in collected:
                    if isinstance(s, dict):
                        cfg["skill_slots"].append(
                            {
                                "id": s.get("id", s.get("name", "")),
                                "key": s.get("key", ""),
                                "cast_time": float(s.get("cast_time", 0.0)),
                                "cooldown": float(s.get("cooldown", 0.0)),
                                "type": s.get("type", "attack"),
                                "name": s.get("name", ""),
                            }
                        )

        cfg["monster_rotation"] = []
        rotation = getattr(state_controller, "monster_rotation", [])
        if isinstance(rotation, list):
            for i, m in enumerate(rotation):
                if isinstance(m, dict):
                    cfg["monster_rotation"].append(
                        {
                            "monster_id": m.get("monster_id", m.get("id", 0)),
                            "name": m.get("name", ""),
                            "priority": m.get("priority", i + 1),
                            "dungeon_id": m.get("dungeon_id", None),
                        }
                    )

        cfg.setdefault("templates", [])

        if state_controller.get_ui_var("global_hotkey_enabled") is not None:
            enabled = state_controller.get_ui_var("global_hotkey_enabled")
            hotkeys = cfg.get("global_hotkeys", {})

            def _hotkey_value(attr_name, config_name, default):
                variable = state_controller.get_ui_var(attr_name.replace("_var", ""))
                return (
                    variable.get()
                    if hasattr(variable, "get")
                    else variable
                    if variable is not None
                    else hotkeys.get(config_name, default)
                )

            cfg["global_hotkeys"] = {
                "enabled": enabled,
                "start_key": _hotkey_value("global_hotkey_start_var", "start_key", DEFAULT_START_HOTKEY),
                "stop_key": _hotkey_value("global_hotkey_stop_var", "stop_key", DEFAULT_STOP_HOTKEY),
                "library_manager_key": _hotkey_value("global_hotkey_library_var", "library_manager_key", DEFAULT_LIBRARY_MANAGER_KEY),
                "vision_wizard_key": _hotkey_value("global_hotkey_vision_var", "vision_wizard_key", DEFAULT_VISION_WIZARD_KEY),
                "monster_editor_key": _hotkey_value("global_hotkey_monster_var", "monster_editor_key", DEFAULT_MONSTER_EDITOR_KEY),
            }

        return cfg
