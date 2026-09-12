from typing import Dict, Any, Optional
import copy
from lib.features.hunt.config_validator import normalize_window_bounds_value
from lib.features.hunt.window_selection_service import WindowSelectionService
from lib.features.monsters.monster_repo import calculate_monster_estimate

class HuntSetupService:
    @staticmethod
    def calculate_monster_estimate(monster: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        stats = calculate_monster_estimate(monster) or {}
        kill_time = float(stats.get("estimated_time_sec", 0.0))
        return {
            "kill_time": round(kill_time, 2),
            "dps": int(stats.get("required_dps", 0) or 0),
            "effective_hp": stats.get("effective_hp", 0),
            "base_hp": stats.get("base_hp", 0),
            "defense": stats.get("defense", 0),
            "level": stats.get("level", 0),
        }

    @staticmethod
    def recommend_attack_settings(stats: Dict[str, Any]):
        kill_time = float(stats.get("kill_time", 0.0) or 0.0)
        attack_min = max(1.0, min(6.0, round(kill_time + 0.4, 2)))
        lost_timeout = max(0.5, min(3.0, round(max(kill_time * 0.35, 0.8), 2)))
        return attack_min, lost_timeout

    @staticmethod
    def apply_monster_to_hunt_quick(monster: Optional[Dict[str, Any]], state_controller) -> None:
        if not monster:
            return

        bounds = normalize_window_bounds_value(monster.get("window_bounds"))
        if bounds:
            state_controller.current_window_bounds = bounds
            WindowSelectionService.update_bounds(state_controller.hunt_cfg, bounds)
            if hasattr(state_controller, "_update_window_bounds_display"):
                state_controller._update_window_bounds_display()

        templates = monster.get("templates") or []
        if isinstance(templates, list):
            state_controller.hunt_cfg["templates"] = copy.deepcopy(templates)
            if templates:
                first_path = str(templates[0].get("path", "") or "").strip()
                if first_path and state_controller.get_ui_var("template") is not None:
                    state_controller.set_ui_var('template', first_path)
                    state_controller.hunt_cfg["template_path"] = first_path

        stats = HuntSetupService.calculate_monster_estimate(monster)
        attack_min, lost_timeout = HuntSetupService.recommend_attack_settings(stats)
        if state_controller.get_ui_var("attack_duration") is not None:
            state_controller.set_ui_var('attack_duration', f"{attack_min:.2f}")
        if state_controller.get_ui_var("lost_timeout") is not None:
            state_controller.set_ui_var('lost_timeout', f"{lost_timeout:.2f}")

        if state_controller.get_ui_var("monster_estimate") is not None:
            if not monster:
                state_controller.set_ui_var("monster_estimate", "")
            else:
                state_controller.set_ui_var(
                    "monster_estimate",
                    f"ETA {stats['kill_time']:.2f}s | DPS {stats['dps']} | atk {attack_min:.2f}s | lost {lost_timeout:.2f}s"
                )
