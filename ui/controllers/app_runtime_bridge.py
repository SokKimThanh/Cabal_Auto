import copy
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import tkinter as tk
from tkinter import messagebox

from lib.features.hunt.hunt_config import save_hunt_config
from lib.features.monsters.monster_repo import calculate_monster_estimate
from lib.system.win_input import tap
from lib.vision.template_matcher import locate_template


class AppRuntimeBridgeMixin:
    @staticmethod
    def _normalize_library_items(items: Any) -> List[Dict[str, Any]]:
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        if isinstance(items, dict):
            normalized: List[Dict[str, Any]] = []
            for key, value in items.items():
                if not isinstance(value, dict):
                    continue
                item = dict(value)
                item.setdefault("id", key)
                item.setdefault("name", str(item.get("name") or key))
                normalized.append(item)
            return normalized
        return []

    def _register_global_hotkeys(self) -> None:
        if hasattr(self, "hotkey_controller") and self.hotkey_controller:
            self.hotkey_controller.register_all()

    def _unregister_global_hotkeys(self) -> None:
        if hasattr(self, "hotkey_controller") and self.hotkey_controller:
            self.hotkey_controller.unregister_all()

    def _set_db_status(self, message: str, ok: bool) -> None:
        if hasattr(self, "_db_status_var") and self._db_status_var:
            self._db_status_var.set(message)
        if hasattr(self, "_db_status_bar") and self._db_status_bar:
            self._db_status_bar.config(
                bg="#d4edda" if ok else "#f8d7da",
                fg="#155724" if ok else "#721c24",
            )

    def _update_window_bounds_display(self) -> None:
        if not hasattr(self, "window_bounds_display_var"):
            return

        from lib.features.hunt.window_selection_service import WindowSelectionService

        bounds = WindowSelectionService.resolve_bounds(
            getattr(self, "hunt_cfg", {}), getattr(self, "current_window_bounds", None)
        )
        if bounds:
            self.window_bounds_display_var.set(
                f"{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}"
            )
        else:
            self.window_bounds_display_var.set("")

    def _list_windows(
        self, title_contains: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.window_controller._list_windows(title_contains)

    def on_hunt_refresh_windows(self, *_args) -> None:
        self.window_controller.on_hunt_refresh_windows(*_args)

    def on_hunt_find_windows(self, _evt=None) -> None:
        self.window_controller.on_hunt_find_windows(_evt)

    def on_window_combo_selected(self, _evt=None) -> None:
        self.window_controller.on_window_combo_selected(_evt)

    def _auto_detect_and_save_cabal_window(self) -> None:
        self.window_controller._auto_detect_and_save_cabal_window()

    def _bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        return self.window_controller._bring_window_to_front_by_hwnd(hwnd)

    def _bring_window_to_front_by_pid(self, pid: int) -> bool:
        return self.window_controller._bring_window_to_front_by_pid(pid)

    def _bring_window_to_front(self, title: str) -> bool:
        return self.window_controller._bring_window_to_front(title)

    def _validate_hunt_prerequisites(self) -> Optional[str]:
        title = str(self.hunt_cfg.get("window_title", "") or "").strip()

        if not title and isinstance(getattr(self, "hunt_selected", None), dict):
            title = str(self.hunt_selected.get("title", "")).strip()
        if not title:
            return "Please select a target window first."

        from lib.features.hunt.window_selection_service import WindowSelectionService

        bounds = WindowSelectionService.resolve_bounds(
            self.hunt_cfg, getattr(self, "current_window_bounds", None)
        )
        if not bounds:
            return "Invalid hunt area bounds. Please refresh or reselect the target window."

        templates = self.hunt_cfg.get("templates") or []
        template_path = str(self.hunt_cfg.get("template_path", "") or "").strip()
        if not templates and not template_path:
            return "Please choose at least one monster/template before starting hunt."
        return None

    def _hunt_from_ui(self) -> Dict[str, Any]:
        from lib.features.hunt.window_selection_service import WindowSelectionService

        cfg = copy.deepcopy(getattr(self, "hunt_cfg", {}))
        if isinstance(getattr(self, "hunt_selected", None), dict):
            cfg["window_title"] = self.hunt_selected.get("title", "")
            cfg["window_pid"] = self.hunt_selected.get("pid")
            cfg["window_hwnd"] = self.hunt_selected.get("hwnd")

        bounds = WindowSelectionService.resolve_bounds(
            cfg, getattr(self, "current_window_bounds", None)
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
            var = getattr(self, attr_name, None)
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
            getattr(getattr(self, "bring_front_var", None), "get", lambda: False)()
        )
        if hasattr(self, "_collect_skill_slots"):
            cfg["skill_slots"] = self._collect_skill_slots()
        cfg.setdefault("templates", [])
        return cfg

    def _hunt_locate_target(self, cfg: Dict[str, Any]):
        from lib.features.hunt.window_selection_service import WindowSelectionService

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
        runtime: List[Dict[str, Any]] = []
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(self, "skills", [])
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
            tap(key, int(self.hunt_cfg.get("attack_press_ms", 60)))
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

    def _calculate_monster_estimate(
        self, monster: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
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
        if not hasattr(self, "monster_estimate_var"):
            return
        if not monster:
            self.monster_estimate_var.set("")
            return
        stats = self._calculate_monster_estimate(monster)
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        self.monster_estimate_var.set(
            f"ETA {stats['kill_time']:.2f}s | DPS {stats['dps']} | atk {attack_min:.2f}s | lost {lost_timeout:.2f}s"
        )

    def _apply_monster_to_hunt_quick(self, monster: Optional[Dict[str, Any]]) -> None:
        if not monster:
            return

        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.features.hunt.window_selection_service import WindowSelectionService

        bounds = normalize_window_bounds_value(monster.get("window_bounds"))
        if bounds:
            self.current_window_bounds = bounds
            WindowSelectionService.update_bounds(self.hunt_cfg, bounds)
            self._update_window_bounds_display()

        templates = monster.get("templates") or []
        if isinstance(templates, list):
            self.hunt_cfg["templates"] = copy.deepcopy(templates)
            if templates:
                first_path = str(templates[0].get("path", "") or "").strip()
                if first_path and hasattr(self, "template_var"):
                    self.template_var.set(first_path)
                    self.hunt_cfg["template_path"] = first_path

        stats = self._calculate_monster_estimate(monster)
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        if hasattr(self, "attack_duration_var"):
            self.attack_duration_var.set(f"{attack_min:.2f}")
        if hasattr(self, "lost_timeout_var"):
            self.lost_timeout_var.set(f"{lost_timeout:.2f}")
        self._update_monster_estimate_label(monster)

    def _refresh_slot_key_labels(self) -> None:
        labels = getattr(self, "skill_slot_key_labels", [])
        vars_ = getattr(self, "skill_slot_vars", [])
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(self, "skills", [])
            if isinstance(skill, dict) and skill.get("name")
        }
        for idx, label in enumerate(labels):
            skill_name = vars_[idx].get().strip() if idx < len(vars_) else ""
            key = ""
            if skill_name:
                key = str(skills_by_name.get(skill_name, {}).get("key", "") or "")
            label.config(text=key.upper() if key else "", fg="#333333")

    def _validate_slot_key_duplicates(self) -> None:
        labels = getattr(self, "skill_slot_key_labels", [])
        vars_ = getattr(self, "skill_slot_vars", [])
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(self, "skills", [])
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
        self.has_unsaved_changes = False
        if hasattr(self, "_update_unsaved_indicator"):
            self._update_unsaved_indicator()

    def _start_overlay_window_tracker(self, target_hwnd: int) -> None:
        if (
            hasattr(self, "window_tracker_controller")
            and self.window_tracker_controller
        ):
            self.window_tracker_controller.start(target_hwnd)

    def _stop_overlay_window_tracker(self) -> None:
        if (
            hasattr(self, "window_tracker_controller")
            and self.window_tracker_controller
        ):
            self.window_tracker_controller.stop()

    def get_window_tracker(self) -> Optional[Any]:
        if (
            hasattr(self, "window_tracker_controller")
            and self.window_tracker_controller
        ):
            return self.window_tracker_controller.get_tracker()
        return None

    def _toggle_overlay(self, *_args) -> None:
        if hasattr(self, "overlay_controller") and getattr(self, "overlay_controller", None) is not None:
            self.overlay_controller.toggle_overlay(*_args)
        else:
            print("[Warning] overlay_controller not initialized; cannot toggle overlay.")

    def _open_overlay_settings(self, *_args) -> None:
        if hasattr(self, "overlay_controller") and self.overlay_controller:
            self.overlay_controller.open_settings(*_args)
            return

        from ui.utils.overlay_settings import OverlaySettingsDialog

        overlay_cfg = copy.deepcopy(self.hunt_cfg.get("overlay", {}))

        def on_apply(new_config: Dict[str, Any]) -> None:
            self.hunt_cfg["overlay"] = new_config
            save_hunt_config(self.hunt_cfg)

        dialog = OverlaySettingsDialog(
            parent=self,
            current_config=overlay_cfg,
            lang=getattr(self, "lang", "vi"),
            on_apply=on_apply,
        )
        dialog.show()

    def _open_library_manager(self) -> None:
        self.library_manager_controller.open_library_manager()

    def _on_vision_wizard_hotkey(self, *_args) -> None:
        if hasattr(self, "hotkey_controller") and self.hotkey_controller:
            self.hotkey_controller.on_vision_wizard(*_args)
        else:
            self.after(0, self.window_controller.open_vision_wizard)

    def _on_monster_editor_hotkey(self, *_args) -> None:
        if hasattr(self, "hotkey_controller") and self.hotkey_controller:
            self.hotkey_controller.on_monster_editor(*_args)
        else:
            self.after(0, self.window_controller.open_monster_manager)

    def try_close_library_manager(self) -> bool:
        return self.library_manager_controller.try_close_library_manager()

    def _after_hunt_stop(self) -> None:
        self.hunt_running = False
        if hasattr(self, "hunt_start_btn"):
            self.hunt_start_btn.config(state="normal", relief="raised", cursor="hand2")
        if hasattr(self, "hunt_stop_btn"):
            self.hunt_stop_btn.config(state="disabled", relief="sunken", cursor="arrow")
        if hasattr(self, "hunt_status"):
            self.hunt_status.set(
                self._t("hunt_idle") if hasattr(self, "_t") else "Idle"
            )
        if getattr(self, "_bot_manager", None) is not None:
            try:
                self._bot_manager.on_hunt_stop()
            except Exception:
                pass
