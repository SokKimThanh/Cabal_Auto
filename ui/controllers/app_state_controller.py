import tkinter as tk
from typing import Any, Dict, List, Optional
import threading
import copy

from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    def __init__(self, root: tk.Tk):
        self.root = root
        app = root

        # State
        app.click_running = False
        app.click_thread = None

        app.hunt_thread = None
        app.win_items = []  # list of {'hwnd','pid','title','proc'}
        app.hunt_selected = None  # currently selected window info
        app._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Global hotkeys - registered after config load
        app._global_start_hotkey = None
        app._global_stop_hotkey = None
        app._global_wizard_hotkey = None
        app._global_library_hotkey = None
        app._global_vision_hotkey = None
        app._global_monster_hotkey = None

        app._hotkey_fallback_bound = []
        app._hotkey_import_diag = ""

        # Phase 5: Overlay window for vision detection
        app._overlay_window = None
        app._overlay_enabled = False
        app._overlay_update_thread = None
        app._overlay_stop_event = threading.Event()

        # Phase 7: Monster tracking integration
        app._vision_engine = None
        app._screen_capture = None
        app._bot_manager = None
        app._overlay_controller = None

        app.monster_selected_index = None

        app.skill_selected_index = None
        app.skill_preview_image = None
        app.skill_slot_vars = []
        app.skill_slot_boxes = []
        app.skill_slot_count = 6

        app.monster_manager_win = None
        app.skill_manager_win = None
        app.monster_listbox = None

        # Declare monster quick-select attributes
        app.monster_select_var = tk.StringVar(master=root)
        app.monster_select_combo = None
        app.monster_name_var = tk.StringVar(master=root)
        app.monster_hp_var = tk.StringVar(master=root)
        app.monster_damage_var = tk.StringVar(master=root)
        app.monster_template_var = tk.StringVar(master=root)
        app.monster_estimate_var = tk.StringVar(master=root, value="")

        app.skill_listbox = None
        app.skill_name_var = tk.StringVar(master=root)
        app.skill_key_var = tk.StringVar(master=root)

        try:
            skill_type_default = i18n_t("skill_type_attack", ns=I18N_GLOBAL)
        except Exception:
            skill_type_default = "Attack"

        app.skill_type_var = tk.StringVar(master=root, value=skill_type_default)
        app.skill_cooldown_var = tk.StringVar(master=root)
        app.skill_cast_time_var = tk.StringVar(master=root)
        app.skill_duration_var = tk.StringVar(master=root)

        app._image_refs = []
        app._tooltips = {}
        app.skill_pre_refresh_var = tk.StringVar(master=root)
        app.skill_image_var = tk.StringVar(master=root)
        app.skill_preview_label = None
        app._skill_image_trace = None

        app.monster_description_text = None
        app.monster_template_working = []
        app.monster_template_selected_index = None
        app.monster_template_listbox = None
        app.monster_template_name_var = tk.StringVar(master=root)
        app.monster_template_path_var = tk.StringVar(master=root)
        app.monster_template_threshold_var = tk.StringVar(master=root, value="0.85")
        app.monster_template_region_vars = {
            "left": tk.StringVar(master=root),
            "top": tk.StringVar(master=root),
            "width": tk.StringVar(master=root),
            "height": tk.StringVar(master=root),
        }
        app.monster_template_preview_label = None
        app.monster_template_preview_image = None
        app._monster_template_path_trace = None
        app._thumbnail_cache = {}

        app.monster_bounds_vars = {
            "left": tk.StringVar(master=root),
            "top": tk.StringVar(master=root),
            "width": tk.StringVar(master=root),
            "height": tk.StringVar(master=root),
        }

        app.window_bounds_display_var = tk.StringVar(master=root, value="")

        app.hunt_intermediate_widgets = []
        app.hunt_advanced_widgets = []

        try:
            idle_text = i18n_t("hunt_idle", ns=I18N_GLOBAL)
        except Exception:
            idle_text = "Idle"

        app.hunt_status = tk.StringVar(master=root, value=idle_text)
        app.hunt_target_info = tk.StringVar(master=root, value="Target: None")

    def _validate_hunt_prerequisites(self) -> Optional[str]:
        app = self.root
        title = str(app.hunt_cfg.get("window_title", "") or "").strip()

        if not title and isinstance(getattr(app, "hunt_selected", None), dict):
            title = str(app.hunt_selected.get("title", "")).strip()
        if not title:
            return "Please select a target window first."

        from lib.features.hunt.window_selection_service import WindowSelectionService

        bounds = WindowSelectionService.resolve_bounds(
            app.hunt_cfg, getattr(app, "current_window_bounds", None)
        )
        if not bounds:
            return "Invalid hunt area bounds. Please refresh or reselect the target window."

        templates = app.hunt_cfg.get("templates") or []
        template_path = str(app.hunt_cfg.get("template_path", "") or "").strip()
        if not templates and not template_path:
            return "Please choose at least one monster/template before starting hunt."
        return None

    def _hunt_from_ui(self) -> Dict[str, Any]:
        app = self.root
        from lib.features.hunt.window_selection_service import WindowSelectionService

        cfg = copy.deepcopy(getattr(app, "hunt_cfg", {}))
        if isinstance(getattr(app, "hunt_selected", None), dict):
            cfg["window_title"] = app.hunt_selected.get("title", "")
            cfg["window_pid"] = app.hunt_selected.get("pid")
            cfg["window_hwnd"] = app.hunt_selected.get("hwnd")

        bounds = WindowSelectionService.resolve_bounds(
            cfg, getattr(app, "current_window_bounds", None)
        )
        WindowSelectionService.update_bounds(cfg, bounds)

        hunt_area = cfg.get("hunt_area")
        if isinstance(hunt_area, dict):
            hunt_area["window_title"] = cfg.get("window_title", "")

        simple_vars = {
            "target_key": ("target_key_var", "TAB"),
            "target_cycle_delay": ("target_cycle_var", 0.2),
            "search_interval": ("search_interval_var", 0.25),
            "attack_interval": ("attack_interval_var", 0.15),
            "lost_timeout_sec": ("lost_timeout_var", 1.2),
            "attack_min_duration_sec": ("attack_duration_var", 1.5),
            "attack_press_ms": ("attack_press_var", 60),
        }
        for key, (attr_name, default) in simple_vars.items():
            var = getattr(app, attr_name, None)
            if var is None:
                cfg.setdefault(key, default)
                continue
            raw_value = var.get()
            if isinstance(default, int):
                cfg[key] = int(raw_value or default)
            elif isinstance(default, float):
                cfg[key] = float(raw_value or default)
            else:
                cfg[key] = raw_value or default

        cfg["bring_to_front_each_cycle"] = bool(
            getattr(getattr(app, "bring_front_var", None), "get", lambda: False)()
        )
        if hasattr(app, "_collect_skill_slots"):
            cfg["skill_slots"] = app._collect_skill_slots()
        cfg.setdefault("templates", [])
        return cfg

    def _calculate_monster_estimate(
        self, monster: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        from lib.utils.math_utils import calculate_monster_estimate

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

    def _recommend_attack_settings(self, stats: Dict[str, Any]):
        kill_time = float(stats.get("kill_time", 0.0) or 0.0)
        attack_min = max(1.0, min(6.0, round(kill_time + 0.4, 2)))
        lost_timeout = max(0.5, min(3.0, round(max(kill_time * 0.35, 0.8), 2)))
        return attack_min, lost_timeout

    def _update_monster_estimate_label(self, monster: Optional[Dict[str, Any]]) -> None:
        app = self.root
        if not hasattr(app, "monster_estimate_var"):
            return
        if not monster:
            app.monster_estimate_var.set("")
            return
        stats = self._calculate_monster_estimate(monster)
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        app.monster_estimate_var.set(
            f"ETA {stats['kill_time']:.2f}s | DPS {stats['dps']} | atk {attack_min:.2f}s | lost {lost_timeout:.2f}s"
        )

    def _apply_monster_to_hunt_quick(self, monster: Optional[Dict[str, Any]]) -> None:
        app = self.root
        if not monster:
            return

        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.features.hunt.window_selection_service import WindowSelectionService

        bounds = normalize_window_bounds_value(monster.get("window_bounds"))
        if bounds:
            app.current_window_bounds = bounds
            WindowSelectionService.update_bounds(app.hunt_cfg, bounds)
            if hasattr(app.state_controller, "_update_window_bounds_display"):
                app.state_controller._update_window_bounds_display()

        templates = monster.get("templates") or []
        if isinstance(templates, list):
            app.hunt_cfg["templates"] = copy.deepcopy(templates)
            if templates:
                first_path = str(templates[0].get("path", "") or "").strip()
                if first_path and hasattr(app, "template_var"):
                    app.template_var.set(first_path)
                    app.hunt_cfg["template_path"] = first_path

        stats = self._calculate_monster_estimate(monster)
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        if hasattr(app, "attack_duration_var"):
            app.attack_duration_var.set(f"{attack_min:.2f}")
        if hasattr(app, "lost_timeout_var"):
            app.lost_timeout_var.set(f"{lost_timeout:.2f}")
        self._update_monster_estimate_label(monster)

    def _refresh_slot_key_labels(self) -> None:
        app = self.root
        labels = getattr(app, "skill_slot_key_labels", [])
        vars_ = getattr(app, "skill_slot_vars", [])
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(app, "skills", [])
            if isinstance(skill, dict) and skill.get("name")
        }
        for idx, label in enumerate(labels):
            skill_name = vars_[idx].get().strip() if idx < len(vars_) else ""
            key = ""
            if skill_name:
                key = str(skills_by_name.get(skill_name, {}).get("key", "") or "")
            label.config(text=key.upper() if key else "", fg="#333333")

    def _validate_slot_key_duplicates(self) -> None:
        app = self.root
        labels = getattr(app, "skill_slot_key_labels", [])
        vars_ = getattr(app, "skill_slot_vars", [])
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(app, "skills", [])
            if isinstance(skill, dict) and skill.get("name")
        }
        seen: Dict[str, int] = {}
        duplicate_indices = set()
        for idx, var in enumerate(vars_):
            skill_name = var.get().strip()
            if not skill_name:
                continue
            key = str(skills_by_name.get(skill_name, {}).get("key", "") or "").lower()
            if not key:
                continue
            if key in seen:
                duplicate_indices.add(seen[key])
                duplicate_indices.add(idx)
            else:
                seen[key] = idx
        for idx, label in enumerate(labels):
            label.config(fg="#C62828" if idx in duplicate_indices else "#333333")

    def _apply_hunt_mode(self) -> None:
        return

    def _clear_unsaved_changes(self) -> None:
        app = self.root
        app.has_unsaved_changes = False
        if hasattr(app, "_update_unsaved_indicator"):
            app._update_unsaved_indicator()

    def _update_window_bounds_display(self) -> None:
        app = self.root
        if not hasattr(app, "window_bounds_display_var"):
            return

        from lib.features.hunt.window_selection_service import WindowSelectionService
        from lib.ui_style import UIStyle

        bounds = WindowSelectionService.resolve_bounds(
            getattr(app, "hunt_cfg", {}), getattr(app, "current_window_bounds", None)
        )
        if bounds:
            app.window_bounds_display_var.set(
                f"{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}"
            )
        else:
            app.window_bounds_display_var.set("")

        if hasattr(app, "bounds_status_var") and hasattr(app, "bounds_readiness_label"):
            selected_window = app.win_combo_var.get() if hasattr(app, "win_combo_var") else None

            is_minimized = False
            if selected_window and hasattr(app, "win_items") and isinstance(app.win_items, list):
                selected_hwnd = app.hunt_selected.get("hwnd") if hasattr(app, "hunt_selected") and isinstance(app.hunt_selected, dict) else None
                for item in app.win_items:
                    if selected_hwnd and item.get("hwnd") == selected_hwnd:
                        is_minimized = item.get("is_minimized", False)
                        break
                    elif item.get("title") == selected_window:
                        is_minimized = item.get("is_minimized", False)
                        break

            if not selected_window:
                app.bounds_status_var.set(app._t("bounds_state_select"))
                app.bounds_readiness_label.config(fg=UIStyle.COLOR_WARNING)
            elif is_minimized:
                app.bounds_status_var.set(app._t("bounds_state_minimized"))
                app.bounds_readiness_label.config(fg=UIStyle.COLOR_DANGER)
            elif not bounds:
                app.bounds_status_var.set(app._t("bounds_state_invalid"))
                app.bounds_readiness_label.config(fg=UIStyle.COLOR_WARNING)
            else:
                title = app.hunt_selected.get("title", selected_window) if hasattr(app, "hunt_selected") and isinstance(app.hunt_selected, dict) else selected_window
                app.bounds_status_var.set(app._t("bounds_state_ready").format(title=title))
                app.bounds_readiness_label.config(fg=UIStyle.COLOR_ACCENT)

    def _hunt_locate_target(self, cfg: Dict[str, Any]):
        app = self.root
        from lib.features.hunt.window_selection_service import WindowSelectionService
        from lib.vision.template_matcher import locate_template
        from pathlib import Path

        bounds = WindowSelectionService.resolve_bounds(cfg)
        if not bounds:
            return None, None

        templates = []
        raw_templates = cfg.get("templates") or []
        if isinstance(raw_templates, list):
            templates.extend(t for t in raw_templates if isinstance(t, dict))
        template_path = str(cfg.get("template_path", "") or "").strip()
        if template_path and not templates:
            templates.append(
                {
                    "path": template_path,
                    "name": Path(template_path).stem,
                    "threshold": float(cfg.get("template_threshold", 0.8)),
                    "monster_name": cfg.get("monster_selected_name", ""),
                }
            )

        best_box = None
        best_info = None
        best_score = -1.0
        for template in templates:
            path = str(template.get("path", "") or "").strip()
            if not path:
                continue
            threshold = float(
                template.get("threshold", cfg.get("template_threshold", 0.8))
            )
            box, confidence = locate_template(
                path, region=tuple(bounds), threshold=threshold
            )
            if box is None or confidence < best_score:
                continue
            best_box = box
            best_score = confidence
            best_info = {
                "path": path,
                "name": template.get("name") or Path(path).stem,
                "threshold": threshold,
                "confidence": confidence,
                "monster_name": template.get("monster_name")
                or cfg.get("monster_selected_name", ""),
            }
        return best_box, best_info

    def _prepare_skill_runtime(self, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        app = self.root
        runtime: List[Dict[str, Any]] = []
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(app, "skills", [])
            if isinstance(skill, dict) and skill.get("name")
        }
        for slot in cfg.get("skill_slots", []) or []:
            if not isinstance(slot, dict):
                continue
            base = skills_by_name.get(slot.get("name"), {})
            runtime.append(
                {
                    "name": slot.get("name") or base.get("name") or "",
                    "key": slot.get("key") or base.get("key") or "",
                    "type": slot.get("type") or base.get("type") or "attack",
                    "cooldown": float(
                        slot.get("cooldown") or base.get("cooldown") or 0.0
                    ),
                    "cast_time": float(
                        slot.get("cast_time") or base.get("cast_time") or 0.0
                    ),
                    "_last_cast": 0.0,
                }
            )
        return runtime

    def _try_cast_skills(
        self,
        skill_runtime: List[Dict[str, Any]],
        now: float,
        target_active: bool,
        attack_phase: bool = False,
        skill_stats=None,
    ) -> None:
        app = self.root
        from lib.system.win_input import tap
        import time
        for skill in skill_runtime:
            is_buff = skill.get("type", "attack") == "buff"
            if attack_phase == is_buff:
                continue
            if attack_phase and not target_active:
                continue
            if now - float(skill.get("_last_cast", 0.0)) < float(
                skill.get("cooldown", 0.0)
            ):
                continue
            key = str(skill.get("key", "") or "").strip()
            if not key:
                continue
            tap(key, int(app.hunt_cfg.get("attack_press_ms", 60)))
            skill["_last_cast"] = now
            if skill_stats is not None:
                try:
                    skill_stats.record_cast(
                        skill.get("name") or key, success=True, timestamp=now
                    )
                except Exception:
                    pass
            cast_time = float(skill.get("cast_time", 0.0))
            if cast_time > 0:
                time.sleep(cast_time)
            return
