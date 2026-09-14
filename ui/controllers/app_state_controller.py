import logging

logger = logging.getLogger(__name__)
import tkinter as tk
from typing import Any, Dict, List, Optional
import threading
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from lib.events.event_dispatcher import EventDispatcher
from lib.system.config.config_repository import ConfigRepository
from lib.system.window.window_tracker import WindowTracker

from lib.ui.stores.monster_session_manager import MonsterSessionManager


from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    @property
    def hunt_cfg(self) -> Dict[str, Any]:
        return self.config_repository.get_config()

    @hunt_cfg.setter
    def hunt_cfg(self, value: Dict[str, Any]) -> None:
        self.config_repository.set_config(value)

    @property
    def has_unsaved_changes(self) -> bool:
        return self._has_unsaved_changes

    @has_unsaved_changes.setter
    def has_unsaved_changes(self, value: bool) -> None:
        self._has_unsaved_changes = value

    @property
    def bounds_recovery_failed(self) -> bool:
        return self.window_tracker.bounds_recovery_failed

    @bounds_recovery_failed.setter
    def bounds_recovery_failed(self, value: bool) -> None:
        self.window_tracker.bounds_recovery_failed = value

    @property
    def win_items(self) -> List[Dict[str, Any]]:
        return self.window_tracker.win_items

    @win_items.setter
    def win_items(self, value: List[Dict[str, Any]]) -> None:
        self.window_tracker.win_items = value

    @property
    def hunt_selected(self) -> Optional[Dict[str, Any]]:
        return self.window_tracker.hunt_selected

    @hunt_selected.setter
    def hunt_selected(self, value: Optional[Dict[str, Any]]) -> None:
        self.window_tracker.hunt_selected = value

    @property
    def current_window_bounds(self) -> Any:
        return self.window_tracker.current_window_bounds

    @current_window_bounds.setter
    def current_window_bounds(self, value: Any) -> None:
        self.window_tracker.current_window_bounds = value



    def __init__(self, root: tk.Tk):
        self.root = root

        # Stores
        self.config_repository = ConfigRepository()
        self.event_dispatcher = EventDispatcher()
        self.window_tracker = WindowTracker()
        self._monster_session_manager = MonsterSessionManager()

        # State
        self._has_unsaved_changes = False
        self.skill_slot_vars = []
        self._collect_skill_slots_func = None

        self.click_running = False
        self.click_thread = None

        self.hunt_thread = None
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Character class selection for presets
        hunt_settings = self.config_repository.get_config()
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
        self._combo_mode_active = False

        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self._image_refs = []
        self._tooltips = {}
        self.monster_template_working = None
        self.monster_template_selected_index = None
        self._thumbnail_cache = {}

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
        self.event_dispatcher.register_callback(event, handler)

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        self.event_dispatcher.emit(event, *args, **kwargs)

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
        return self._monster_session_manager.get_rotation()

    @monster_rotation.setter
    def monster_rotation(self, value):
        self._monster_session_manager.set_rotation(value)

    def _refresh_slot_key_labels(self) -> None:

        vars_ = self.skill_slot_vars
        service = SkillRuntimeService()
        skills_by_name = {
            skill.get("name"): skill
            for skill in service.get_all_skills()
            if isinstance(skill, dict) and skill.get("name")
        }
        keys_list = []
        for var in vars_:
            skill_name = var.get().strip()
            key = ""
            if skill_name:
                key = str(skills_by_name.get(skill_name, {}).get("key", "") or "")
            keys_list.append(key.upper() if key else "")

        self._emit_event("on_skill_keys_updated", keys_list)

    def _validate_slot_key_duplicates(self) -> None:

        vars_ = self.skill_slot_vars
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

        self._emit_event("on_skill_key_duplicates_detected", duplicate_indices)

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
