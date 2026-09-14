import logging

logger = logging.getLogger(__name__)
import tkinter as tk
from typing import Any, Dict, List, Optional
import threading
import copy
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from lib.ui.stores.hunt_config_store import HuntConfigStore
from lib.ui.stores.monster_session_manager import MonsterSessionManager


from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    @property
    def hunt_cfg(self) -> Dict[str, Any]:
        return self._config_store.get_config()

    @hunt_cfg.setter
    def hunt_cfg(self, value: Dict[str, Any]) -> None:
        self._config_store.set_config(value)

    @property
    def has_unsaved_changes(self) -> bool:
        return self._has_unsaved_changes

    @has_unsaved_changes.setter
    def has_unsaved_changes(self, value: bool) -> None:
        self._has_unsaved_changes = value

    @property
    def bounds_recovery_failed(self) -> bool:
        return self._bounds_recovery_failed

    @bounds_recovery_failed.setter
    def bounds_recovery_failed(self, value: bool) -> None:
        self._bounds_recovery_failed = value

    @property
    def win_items(self) -> List[Dict[str, Any]]:
        return self._win_items

    @win_items.setter
    def win_items(self, value: List[Dict[str, Any]]) -> None:
        self._win_items = value

    @property
    def hunt_selected(self) -> Optional[Dict[str, Any]]:
        return self._hunt_selected

    @hunt_selected.setter
    def hunt_selected(self, value: Optional[Dict[str, Any]]) -> None:
        self._hunt_selected = value

    @property
    def current_window_bounds(self) -> Any:
        return self._current_window_bounds

    @current_window_bounds.setter
    def current_window_bounds(self, value: Any) -> None:
        self._current_window_bounds = value



    def __init__(self, root: tk.Tk):
        self.root = root

        # Stores
        self._config_store = HuntConfigStore()
        self._monster_session_manager = MonsterSessionManager()

        # State
        self._has_unsaved_changes = False
        self._bounds_recovery_failed = False
        self._win_items = []  # list of {'hwnd','pid','title','proc'}
        self._hunt_selected = None  # currently selected window info
        self._current_window_bounds = None
        self.skill_slot_key_labels = []
        self.skill_slot_vars = []
        self._collect_skill_slots_func = None

        self.click_running = False
        self.click_thread = None

        self.hunt_thread = None
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Character class selection for presets
        hunt_settings = self._config_store.get_config()
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

        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self._image_refs = []
        self._tooltips = {}
        self.monster_template_working = None
        self.monster_template_selected_index = None
        self._thumbnail_cache = {}
        self.current_window_bounds = None

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


    def set_current_class(self, class_id: int) -> bool:
        """
        Safely changes the current class, prompting for unsaved changes if necessary.
        Returns True if the class was changed, False if the user cancelled.
        """
        import tkinter.messagebox as messagebox

        if self.has_unsaved_changes:
            title = i18n_t("warning_title", ns=I18N_GLOBAL)
            msg = i18n_t("msg_unsaved_class_change", ns=I18N_GLOBAL)

            if not messagebox.askyesno(title, msg, parent=self.root):
                return False

        self._current_class_id = class_id

        # Save to hunt_cfg
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
        return bool(self.get_ui_var("is_hunting"))

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

    @property
    def monster_rotation(self):
        return self._monster_session_manager.get_rotation()

    @monster_rotation.setter
    def monster_rotation(self, value):
        self._monster_session_manager.set_rotation(value)

    def _refresh_slot_key_labels(self) -> None:

        labels = self.skill_slot_key_labels
        vars_ = self.skill_slot_vars
        service = SkillRuntimeService()
        skills_by_name = {
            skill.get("name"): skill
            for skill in service.get_all_skills()
            if isinstance(skill, dict) and skill.get("name")
        }
        keys_list = []
        for idx, var in enumerate(vars_):
            skill_name = var.get().strip()
            key = ""
            if skill_name:
                key = str(skills_by_name.get(skill_name, {}).get("key", "") or "")
            keys_list.append(key.upper() if key else "")

        self._emit_event("on_skill_keys_updated", keys_list)

    def _validate_slot_key_duplicates(self) -> None:

        labels = self.skill_slot_key_labels
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
