import tkinter as tk
from typing import Any, Dict, List, Optional
import threading

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
