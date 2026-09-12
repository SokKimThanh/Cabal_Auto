import logging

logger = logging.getLogger(__name__)
import tkinter as tk
from typing import Any, Dict, List, Optional
import threading
import copy

from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    @property
    def hunt_cfg(self) -> Dict[str, Any]:
        return getattr(self, "_hunt_cfg", {})

    @hunt_cfg.setter
    def hunt_cfg(self, value: Dict[str, Any]) -> None:
        self._hunt_cfg = value

    @property
    def has_unsaved_changes(self) -> bool:
        return getattr(self, "_has_unsaved_changes", False)

    @has_unsaved_changes.setter
    def has_unsaved_changes(self, value: bool) -> None:
        self._has_unsaved_changes = value

    @property
    def bounds_recovery_failed(self) -> bool:
        return getattr(self, "_bounds_recovery_failed", False)

    @bounds_recovery_failed.setter
    def bounds_recovery_failed(self, value: bool) -> None:
        self._bounds_recovery_failed = value

    @property
    def win_items(self) -> List[Dict[str, Any]]:
        return getattr(self, "_win_items", [])

    @win_items.setter
    def win_items(self, value: List[Dict[str, Any]]) -> None:
        self._win_items = value

    @property
    def hunt_selected(self) -> Optional[Dict[str, Any]]:
        return getattr(self, "_hunt_selected", None)

    @hunt_selected.setter
    def hunt_selected(self, value: Optional[Dict[str, Any]]) -> None:
        self._hunt_selected = value

    @property
    def current_window_bounds(self) -> Any:
        return getattr(self, "_current_window_bounds", None)

    @current_window_bounds.setter
    def current_window_bounds(self, value: Any) -> None:
        self._current_window_bounds = value



    def __init__(self, root: tk.Tk):
        self.root = root






        # State
        self.click_running = False
        self.click_thread = None

        self.hunt_thread = None
        self._win_items = []  # list of {'hwnd','pid','title','proc'}
        self._hunt_selected = None  # currently selected window info
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Character class selection for presets
        hunt_settings = getattr(self, "hunt_cfg", {})
        self._current_class_id = hunt_settings.get("last_active_class_id", 1)

        # Global hotkeys - registered after config load
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._global_library_hotkey = None
        self._global_vision_hotkey = None
        self._global_monster_hotkey = None

        self._hotkey_fallback_bound = []
        self._hotkey_import_diag = ""

        # Phase 5: Overlay window for vision detection
        self._overlay_window = None
        self._overlay_enabled = False
        self._overlay_update_thread = None
        self._overlay_stop_event = threading.Event()

        # Phase 7: Monster tracking integration
        self._vision_engine = None
        self._screen_capture = None
        self._bot_manager = None
        self._overlay_controller = None

        self.monster_selected_index = None

        self.skill_selected_index = None
        self.skill_preview_image = None

        # Preset State
        self._active_preset_id = None
        self._preset_mode = "default"
        self.skill_slots = {"attack_combo": [], "buff_lane": []}
        self._callbacks = {}
        self._combo_mode_active = False

        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self._image_refs = []
        self._tooltips = {}
        self.monster_template_working = None
        self.monster_template_selected_index = None
        self._thumbnail_cache = {}
        self.monster_rotation = []
        self.current_window_bounds = None

        self.ui_vars = {
            "monster_select": tk.StringVar(master=root),
            "monster_name": tk.StringVar(master=root),
            "monster_hp": tk.StringVar(master=root),
            "monster_damage": tk.StringVar(master=root),
            "monster_template": tk.StringVar(master=root),
            "monster_estimate": tk.StringVar(master=root, value=""),

            "skill_name": tk.StringVar(master=root),
            "skill_key": tk.StringVar(master=root),
            "skill_type": tk.StringVar(master=root),
            "skill_cooldown": tk.StringVar(master=root),
            "skill_cast_time": tk.StringVar(master=root),
            "skill_duration": tk.StringVar(master=root),
            "skill_pre_refresh": tk.StringVar(master=root),
            "skill_image": tk.StringVar(master=root),

            "monster_template_name": tk.StringVar(master=root),
            "monster_template_path": tk.StringVar(master=root),
            "monster_template_threshold": tk.StringVar(master=root, value="0.85"),

            "window_bounds_display": tk.StringVar(master=root, value=""),
            "hunt_status": tk.StringVar(master=root),
            "hunt_target_info": tk.StringVar(master=root, value=i18n_t("target_card.target_none")),
            "target_policy": tk.StringVar(master=root),
            "setup_template": tk.StringVar(master=root),
            "setup_target_key": tk.StringVar(master=root),
            "setup_target_cycle": tk.StringVar(master=root),
            "setup_search_interval": tk.StringVar(master=root),
            "setup_attack_interval": tk.StringVar(master=root),
            "setup_lost_timeout": tk.StringVar(master=root),
            "setup_attack_duration": tk.StringVar(master=root),
            "setup_press_ms": tk.StringVar(master=root),
            "bring_front": tk.StringVar(master=root),
            "global_hotkey_enabled": tk.BooleanVar(master=root),
            "global_hotkey_start": tk.StringVar(master=root),
            "global_hotkey_stop": tk.StringVar(master=root),
            "global_hotkey_library": tk.StringVar(master=root),
            "global_hotkey_vision": tk.StringVar(master=root),
            "global_hotkey_monster": tk.StringVar(master=root),
            "monster_status": tk.StringVar(master=root),
            "training_mode": tk.BooleanVar(master=root, value=False),
            "global_hotkeys_enabled_legacy": tk.BooleanVar(master=root, value=True),
            "lang": tk.StringVar(master=root, value="vi"),
            "db_status": tk.StringVar(master=root, value="⠋ Đang kiểm tra CSDL..."),
            "hotkey_status": tk.StringVar(master=root),
            "hotkey_status_detail": tk.StringVar(master=root),
            "bounds_status": tk.StringVar(master=root),
            "win_combo": tk.StringVar(master=root),
            "template": tk.StringVar(master=root),
            "attack_duration": tk.StringVar(master=root),
            "lost_timeout": tk.StringVar(master=root),
            "rotation_mode": tk.StringVar(master=root, value="cycle"),
            "rotation_desc": tk.StringVar(master=root)
        }

        self.ui_widgets = {
            "monster_select_combo": None,
            "monster_manager_win": None,
            "skill_manager_win": None,
            "monster_listbox": None,
            "skill_listbox": None,
            "skill_preview_label": None,
            "monster_description_text": None,
            "monster_template_listbox": None,
            "monster_template_preview_label": None,
            "monster_template_preview_image": None
        }

        self.monster_template_region_vars = {
            "left": tk.StringVar(master=root),
            "top": tk.StringVar(master=root),
            "width": tk.StringVar(master=root),
            "height": tk.StringVar(master=root),
        }

        self.monster_bounds_vars = {
            "left": tk.StringVar(master=root),
            "top": tk.StringVar(master=root),
            "width": tk.StringVar(master=root),
            "height": tk.StringVar(master=root),
        }


    def register_callback(self, event: str, handler) -> None:
        if event not in self._callbacks:
            self._callbacks[event] = []
        if handler not in self._callbacks[event]:
            self._callbacks[event].append(handler)

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        if event in self._callbacks:
            for handler in self._callbacks[event]:
                try:
                    handler(*args, **kwargs)
                except Exception:
                    logger.exception("Error in callback for %s", event)


    def set_current_class(self, class_id: int) -> bool:
        """
        Safely changes the current class, prompting for unsaved changes if necessary.
        Returns True if the class was changed, False if the user cancelled.
        """
        import tkinter.messagebox as messagebox

        if getattr(self, "has_unsaved_changes", False):
            title = i18n_t("warning_title", ns=I18N_GLOBAL)
            msg = i18n_t("msg_unsaved_class_change", ns=I18N_GLOBAL)

            if not messagebox.askyesno(title, msg, parent=self.root):
                return False

        self._current_class_id = class_id

        # Save to hunt_cfg
        if hasattr(self.root, "hunt_cfg"):
            self.hunt_cfg["last_active_class_id"] = class_id
            from lib.features.hunt.hunt_config import save_hunt_config
            save_hunt_config(self.hunt_cfg)

        # Clear unsaved changes since we are loading a fresh preset from DB
        self._clear_unsaved_changes()

        # Auto load preset for the new class
        self.load_preset_for_class(class_id)

        return True

    def load_preset_for_class(
        self, class_id: int, preset_id: Optional[int] = None
    ) -> None:
        self._current_class_id = class_id
        from lib.features.skills.skill_preset_service import SkillPresetService

        service = SkillPresetService()
        if preset_id is None:
            # Try to load default preset
            presets = service.list_presets_by_class(class_id)
            default_preset = next((p for p in presets if p["is_default"]), None)
            if default_preset:
                preset_id = default_preset["preset_id"]
            elif presets:
                preset_id = presets[0]["preset_id"]

        if preset_id is not None:
            result = service.apply_preset(preset_id, class_id)
            if result.get("success"):
                self._active_preset_id = preset_id
                mode = "default" if result["preset"].get("is_default") else "custom"
                self._preset_mode = mode

                # Transform to app state structure
                self.skill_slots = {"attack_combo": [], "buff_lane": []}
                for lane, skill_ids in result.get("skill_slots", {}).items():
                    for idx, skill_id in enumerate(skill_ids):
                        self.skill_slots[lane].append(
                            {
                                "position": idx,
                                "lane_type": lane,
                                "skill_id": skill_id,
                                "skill_name": "Unknown",  # Will populate later or via UI
                                "user_hotkey": "",
                                "assigned": False,
                                "is_ready": True,
                                "cooldown_remaining": 0.0,
                            }
                        )
                self._emit_event("on_preset_changed")
                self._emit_event("on_skill_slots_changed")
        else:
            # When the class has no presets at all, clear the skill slots
            self._active_preset_id = None
            self._preset_mode = "custom"
            self.skill_slots = {"attack_combo": [], "buff_lane": []}
            self._emit_event("on_preset_changed")
            self._emit_event("on_skill_slots_changed")

    def apply_default_preset(self, class_id: int) -> None:
        self.load_preset_for_class(class_id)

    def set_custom_mode(self) -> None:
        self._preset_mode = "custom"
        self._emit_event("on_preset_changed")

    def update_preset_state(self, preset_id: int, mode: str) -> None:
        """Encapsulates preset state updates."""
        self._active_preset_id = preset_id
        self._preset_mode = mode
        self._emit_event("on_preset_changed")

    def save_custom_preset(self, preset_name: str) -> None:
        from lib.features.skills.skill_preset_service import SkillPresetService

        if self._preset_mode == "custom" and self._active_preset_id:
            service = SkillPresetService()
            preset = service.preset_repo.get_preset(self._active_preset_id)
            if preset and not preset.get("is_default"):
                skill_slots_for_db = {
                    lane: [s["skill_id"] for s in self.skill_slots.get(lane, [])]
                    for lane in self.skill_slots
                }
                service.update_custom_preset(
                    self._active_preset_id, skill_slots_for_db
                )
            else:
                # Need to create new custom preset
                skill_slots_for_db = {
                    lane: [s["skill_id"] for s in self.skill_slots.get(lane, [])]
                    for lane in self.skill_slots
                }
                res = service.create_custom_preset(
                    self._current_class_id, preset_name, skill_slots_for_db
                )
                if res.get("success"):
                    self._active_preset_id = res.get("preset_id")
        else:
            # Need to create new custom preset
            service = SkillPresetService()
            skill_slots_for_db = {
                lane: [s["skill_id"] for s in self.skill_slots.get(lane, [])]
                for lane in self.skill_slots
            }
            res = service.create_custom_preset(
                self._current_class_id, preset_name, skill_slots_for_db
            )
            if res.get("success"):
                self._active_preset_id = res.get("preset_id")
                self._preset_mode = "custom"

        self._emit_event("on_preset_changed")

    def get_available_presets(self, class_id: int) -> list:
        from lib.features.skills.skill_preset_service import SkillPresetService

        service = SkillPresetService()
        return service.list_presets_by_class(class_id)

    def activate_combo_mode(self) -> None:
        self._combo_mode_active = True
        self._emit_event("on_combo_mode_activated")

    def deactivate_combo_mode(self) -> None:
        self._combo_mode_active = False
        self._emit_event("on_combo_mode_deactivated")

    def get_combo_mode_status(self) -> str:
        return (
            "active" if self._combo_mode_active else "inactive"
        )

    def is_bot_running(self) -> bool:
        if hasattr(self.root, "hunt_orchestrator"):
            return getattr(self.root.hunt_orchestrator, "hunt_running", False)
        return False

    def set_skill_slot(self, lane: str, position: int, skill_id: int) -> None:
        if lane not in self.skill_slots:
            self.skill_slots[lane] = []
        while len(self.skill_slots[lane]) <= position:
            self.skill_slots[lane].append(
                {
                    "position": len(self.skill_slots[lane]),
                    "lane_type": lane,
                    "skill_id": None,
                    "skill_name": "",
                    "user_hotkey": "",
                    "assigned": False,
                    "is_ready": True,
                    "cooldown_remaining": 0.0,
                }
            )
        self.skill_slots[lane][position]["skill_id"] = skill_id
        self.skill_slots[lane][position]["assigned"] = skill_id is not None

        # If changing a slot in default mode, automatically switch to custom mode
        if self._preset_mode == "default":
            self.set_custom_mode()

        self._emit_event("on_skill_slots_changed")

    def set_skill_hotkey(self, lane: str, position: int, hotkey: str) -> None:
        if lane in self.skill_slots and position < len(
            self.skill_slots[lane]
        ):
            self.skill_slots[lane][position]["user_hotkey"] = hotkey
            self._emit_event("on_hotkey_changed")

    def update_skill_cooldown(self, lane: str, position: int, remaining: float) -> None:
        if lane in self.skill_slots and position < len(
            self.skill_slots[lane]
        ):
            self.skill_slots[lane][position]["cooldown_remaining"] = remaining
            self.skill_slots[lane][position]["is_ready"] = remaining <= 0.0
            self._emit_event("on_cooldown_updated")

    def build_hunt_config_from_state(self) -> Dict[str, Any]:

        from lib.features.hunt.window_selection_service import WindowSelectionService

        cfg = copy.deepcopy(getattr(self, "hunt_cfg", {}))
        if not isinstance(cfg.get("skill_slots"), list):
            cfg["skill_slots"] = []

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

        if self.get_ui_var("target_policy") is not None:
            cfg["target_policy"] = self.get_ui_var("target_policy")

        simple_vars = {
            "target_key": ("setup_target_key_var", "TAB"),
            "target_cycle_delay": ("setup_target_cycle_var", 0.2),
            "search_interval": ("setup_search_interval_var", 0.25),
            "attack_interval": ("setup_attack_interval_var", 0.15),
            "lost_timeout_sec": ("setup_lost_timeout_var", 1.2),
            "attack_min_duration_sec": ("setup_attack_duration_var", 1.5),
            "attack_press_ms": ("setup_press_ms_var", 60),
        }

        cfg["ui_mode"] = "advanced"

        if self.get_ui_var("setup_template") is not None:
            cfg["template_path"] = self.get_ui_var("setup_template")

        for key, (attr_name, default) in simple_vars.items():
            var = self.get_ui_var(attr_name.replace("_var", ""))
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

        cfg["bring_to_front_each_cycle"] = bool(self.get_ui_var("bring_front"))
        cfg["skill_slots"] = []
        if hasattr(self, "_collect_skill_slots_func") and callable(self._collect_skill_slots_func):
            collected = self._collect_skill_slots_func()
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
        rotation = getattr(self, "monster_rotation", [])
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

        if self.get_ui_var("global_hotkey_enabled") is not None:
            enabled = self.get_ui_var("global_hotkey_enabled")
            hotkeys = cfg.get("global_hotkeys", {})

            def _hotkey_value(attr_name, config_name, default):
                variable = self.get_ui_var(attr_name.replace("_var", ""))
                return (
                    variable.get()
                    if variable is not None
                    else hotkeys.get(config_name, default)
                )

            cfg["global_hotkeys"] = {
                "enabled": enabled,
                "start_key": _hotkey_value("global_hotkey_start_var", "start_key", "ctrl+shift+r"),
                "stop_key": _hotkey_value("global_hotkey_stop_var", "stop_key", "ctrl+shift+e"),
                "library_manager_key": _hotkey_value("global_hotkey_library_var", "library_manager_key", "ctrl+shift+l"),
                "vision_wizard_key": _hotkey_value("global_hotkey_vision_var", "vision_wizard_key", "ctrl+shift+v"),
                "monster_editor_key": _hotkey_value("global_hotkey_monster_var", "monster_editor_key", "ctrl+shift+m"),
            }

        return cfg

    def _refresh_slot_key_labels(self) -> None:

        labels = getattr(self, "skill_slot_key_labels", [])
        vars_ = getattr(self, "skill_slot_vars", [])
        skills_by_name = {
            skill.get("name"): skill
            for skill in getattr(self.root, "skills", [])
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
            for skill in getattr(self.root, "skills", [])
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
        if "unsaved_indicator_func" in self.ui_widgets:
            if callable(self.ui_widgets.get("unsaved_indicator_func")): self.ui_widgets["unsaved_indicator_func"]()

    def get_ui_var(self, name: str) -> Any:
        if name in self.ui_vars:
            return self.ui_vars[name].get()
        return None

    def set_ui_var(self, name: str, value: Any) -> None:
        if name in self.ui_vars:
            self.ui_vars[name].set(value)
