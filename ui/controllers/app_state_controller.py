import logging

logger = logging.getLogger(__name__)
import tkinter as tk
from typing import Any, Dict, List, Optional
import threading
import copy
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from lib.ui.stores.hunt_config_store import HuntConfigStore
from lib.ui.stores.monster_session_manager import MonsterSessionManager


from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    @property
    def hunt_cfg(self) -> Dict[str, Any]:
        if not hasattr(self, "_config_store"):
            return {}
        return self._config_store.get_config()

    @hunt_cfg.setter
    def hunt_cfg(self, value: Dict[str, Any]) -> None:
        if not hasattr(self, "_config_store"):
            self._config_store = HuntConfigStore()
        self._config_store.set_config(value)

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

        # Stores
        self._config_store = HuntConfigStore()
        self._monster_session_manager = MonsterSessionManager()

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
        self.current_window_bounds = None
        self._collect_skill_slots_func: Any = None

        self.ui_vars = {}
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
            "monster_template_preview_image": None,
        }
        self.monster_template_region_vars = {}
        self.monster_bounds_vars = {}

        self.init_tkinter_vars(root)


    def init_tkinter_vars(self, root: tk.Tk) -> None:
        """Initializes all Tkinter variables securely within the controller lifecycle."""
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
            "hunt_mode": tk.StringVar(master=root),
            "target_key": tk.StringVar(master=root),
            "target_cycle": tk.StringVar(master=root),
            "search_interval": tk.StringVar(master=root),
            "attack_interval": tk.StringVar(master=root),
            "lost_timeout": tk.StringVar(master=root),
            "attack_duration": tk.StringVar(master=root),
            "attack_press": tk.StringVar(master=root),
            "template": tk.StringVar(master=root),
            "monster_status": tk.StringVar(master=root),
            "training_mode_hint": tk.StringVar(master=root),
            "reg_l": tk.StringVar(master=root),
            "reg_t": tk.StringVar(master=root),
            "reg_w": tk.StringVar(master=root),
            "reg_h": tk.StringVar(master=root),
            "global_hotkey_library": tk.StringVar(master=root),
            "global_hotkey_vision": tk.StringVar(master=root),
            "global_hotkey_monster": tk.StringVar(master=root),
            "is_hunting": tk.BooleanVar(master=root, value=False),
            "training_mode": tk.BooleanVar(master=root, value=False),
            "global_hotkeys_enabled_legacy": tk.BooleanVar(master=root, value=True),
            "lang": tk.StringVar(master=root, value="vi"),
            "db_status": tk.StringVar(master=root, value="⠋ Đang kiểm tra CSDL..."),
            "hotkey_status": tk.StringVar(master=root),
            "hotkey_status_detail": tk.StringVar(master=root),
            "bounds_status": tk.StringVar(master=root),
            "win_combo": tk.StringVar(master=root),
            "rotation_mode": tk.StringVar(master=root, value="cycle"),
            "rotation_desc": tk.StringVar(master=root)
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
        return bool(self.get_ui_var("is_hunting"))

    @property
    def monster_rotation(self):
        if not hasattr(self, "_monster_session_manager"):
            return []
        return self._monster_session_manager.get_rotation()

    @monster_rotation.setter
    def monster_rotation(self, value):
        if not hasattr(self, "_monster_session_manager"):
            self._monster_session_manager = MonsterSessionManager()
        self._monster_session_manager.set_rotation(value)

    def build_hunt_config_from_state(self) -> Dict[str, Any]:

        from lib.features.hunt.window_selection_service import WindowSelectionService

        cfg = copy.deepcopy(self.hunt_cfg)
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
        _collect_func = getattr(self, "_collect_skill_slots_func", None)
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
        service = SkillRuntimeService()
        skills_by_name = {
            skill.get("name"): skill
            for skill in service.get_all_skills()
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
        service = SkillRuntimeService()
        skills_by_name = {
            skill.get("name"): skill
            for skill in service.get_all_skills()
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
