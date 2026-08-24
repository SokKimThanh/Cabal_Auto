import tkinter as tk
from typing import Any, Dict, List, Optional
from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import t as i18n_t


class AppStateController:
    """Manages bound state variables and bookkeeping for the root App instance."""

    def __init__(self, root: tk.Tk):
        self.root = root

        # State
        self.click_running = False
        self.click_thread = None

        self.hunt_thread = None
        self.win_items = []  # list of {'hwnd','pid','title','proc'}
        self.hunt_selected = None  # currently selected window info
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Global hotkeys - registered after config load
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._global_wizard_hotkey = None
        self._global_library_hotkey = None
        self._global_vision_hotkey = None
        self._global_monster_hotkey = None

        self._hotkey_fallback_bound = []
        self._hotkey_import_diag = ""

        # Phase 5: Overlay window for vision detection
        self._overlay_window = None
        self._overlay_enabled = False
        self._overlay_update_thread = None

        import threading

        self._overlay_stop_event = threading.Event()

        # Phase 7: Monster tracking integration
        self._vision_engine = None
        self._screen_capture = None
        self._bot_manager = None
        self._overlay_controller = None

        self.monster_selected_index = None

        self.skill_selected_index = None
        self.skill_preview_image = None
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6

        self.monster_manager_win = None
        self.skill_manager_win = None
        self.monster_listbox = None

        # Declare monster quick-select attributes
        self.monster_select_var = tk.StringVar()
        self.monster_select_combo = None
        self.monster_name_var = tk.StringVar()
        self.monster_hp_var = tk.StringVar()
        self.monster_damage_var = tk.StringVar()
        self.monster_template_var = tk.StringVar()
        self.monster_estimate_var = tk.StringVar(value="")

        self.skill_listbox = None
        self.skill_name_var = tk.StringVar()
        self.skill_key_var = tk.StringVar()

        try:
            skill_type_default = i18n_t("skill_type_attack", ns=I18N_GLOBAL)
        except Exception:
            skill_type_default = "Attack"

        self.skill_type_var = tk.StringVar(value=skill_type_default)
        self.skill_cooldown_var = tk.StringVar()
        self.skill_cast_time_var = tk.StringVar()
        self.skill_duration_var = tk.StringVar()

        self._image_refs = []
        self._tooltips = {}
        self.skill_pre_refresh_var = tk.StringVar()
        self.skill_image_var = tk.StringVar()
        self.skill_preview_label = None
        self._skill_image_trace = None

        self.monster_description_text = None
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self.monster_template_listbox = None
        self.monster_template_name_var = tk.StringVar()
        self.monster_template_path_var = tk.StringVar()
        self.monster_template_threshold_var = tk.StringVar(value="0.85")
        self.monster_template_region_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }
        self.monster_template_preview_label = None
        self.monster_template_preview_image = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}

        self.monster_bounds_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }

        self.window_bounds_display_var = tk.StringVar(value="")

        self.hunt_intermediate_widgets = []
        self.hunt_advanced_widgets = []

        try:
            idle_text = i18n_t("hunt_idle", ns=I18N_GLOBAL)
        except Exception:
            idle_text = "Idle"

        self.hunt_status = tk.StringVar(value=idle_text)
        self.hunt_target_info = tk.StringVar(value="Target: None")

    def attach_to_app(self):
        """Inject state directly into the root application to maintain compatibility."""
        app = self.root

        state_attrs = (
            "click_running",
            "click_thread",
            "hunt_thread",
            "win_items",
            "hunt_selected",
            "_skip_auto_bring",
            "_global_start_hotkey",
            "_global_stop_hotkey",
            "_global_wizard_hotkey",
            "_global_library_hotkey",
            "_global_vision_hotkey",
            "_global_monster_hotkey",
            "_hotkey_fallback_bound",
            "_hotkey_import_diag",
            "_overlay_window",
            "_overlay_enabled",
            "_overlay_update_thread",
            "_overlay_stop_event",
            "_vision_engine",
            "_screen_capture",
            "_bot_manager",
            "_overlay_controller",
            "monster_selected_index",
            "skill_selected_index",
            "skill_preview_image",
            "skill_slot_vars",
            "skill_slot_boxes",
            "skill_slot_count",
        )

        for name in state_attrs:
            setattr(app, name, getattr(self, name))

        app.monster_manager_win = self.monster_manager_win
        app.skill_manager_win = self.skill_manager_win
        app.monster_listbox = self.monster_listbox

        app.monster_select_var = self.monster_select_var
        app.monster_select_combo = self.monster_select_combo
        app.monster_name_var = self.monster_name_var
        app.monster_hp_var = self.monster_hp_var
        app.monster_damage_var = self.monster_damage_var
        app.monster_template_var = self.monster_template_var
        app.monster_estimate_var = self.monster_estimate_var

        app.skill_listbox = self.skill_listbox
        app.skill_name_var = self.skill_name_var
        app.skill_key_var = self.skill_key_var
        app.skill_type_var = self.skill_type_var
        app.skill_cooldown_var = self.skill_cooldown_var
        app.skill_cast_time_var = self.skill_cast_time_var
        app.skill_duration_var = self.skill_duration_var

        app._image_refs = self._image_refs
        app._tooltips = self._tooltips

        app.skill_pre_refresh_var = self.skill_pre_refresh_var
        app.skill_image_var = self.skill_image_var
        app.skill_preview_label = self.skill_preview_label
        app._skill_image_trace = self._skill_image_trace

        app.monster_description_text = self.monster_description_text
        app.monster_template_working = self.monster_template_working
        app.monster_template_selected_index = self.monster_template_selected_index
        app.monster_template_listbox = self.monster_template_listbox
        app.monster_template_name_var = self.monster_template_name_var
        app.monster_template_path_var = self.monster_template_path_var
        app.monster_template_threshold_var = self.monster_template_threshold_var
        app.monster_template_region_vars = self.monster_template_region_vars

        app.monster_template_preview_label = self.monster_template_preview_label
        app.monster_template_preview_image = self.monster_template_preview_image
        app._monster_template_path_trace = self._monster_template_path_trace
        app._thumbnail_cache = self._thumbnail_cache

        app.monster_bounds_vars = self.monster_bounds_vars

        app.window_bounds_display_var = self.window_bounds_display_var

        app.hunt_intermediate_widgets = self.hunt_intermediate_widgets
        app.hunt_advanced_widgets = self.hunt_advanced_widgets

        app.hunt_status = self.hunt_status
        app.hunt_target_info = self.hunt_target_info
