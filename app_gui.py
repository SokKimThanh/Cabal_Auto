import copy
import ctypes
import json
import math
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import pyautogui  # type: ignore
except Exception:
    pyautogui = None  # type: ignore

try:
    from PIL import Image, ImageDraw, ImageTk  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    ImageDraw = None  # type: ignore

try:
    import keyboard  # type: ignore
except Exception:
    keyboard = None  # type: ignore

from ctypes import wintypes

from lib.vision.template_matcher import locate_template
from lib.vision.vision_engine import VisionEngine
from lib.features.hunt.config_validator import get_valid_hunt_area

try:
    from lib.system.screen_capture import ScreenCapture
except ImportError:
    ScreenCapture = None
from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.i18n import set_default_lang as i18n_set_lang
from lib.i18n import t as i18n_t

# Imported for its side effect: self-registers GLOBAL_TRANSLATIONS into the i18n registry.
from lib.i18n.translations import GLOBAL_TRANSLATIONS  # noqa: F401
from lib.system.bot_manager import BotManager
from ui.helpers.tooltip import attach_i18n_tooltip
from ui.utils.overlay_controller import OverlayController

# Import icon button component
try:
    from ui.components import create_icon_button as _create_icon_btn_component

    _HAS_ICON_COMPONENT = True
except ImportError:
    _HAS_ICON_COMPONENT = False

    # Fallback function for create_icon_button
    def _create_icon_btn_component(
        parent,
        icon_name,
        command=None,
        text=None,
        button_type="green_light",
        icon_size=16,
        button_size=None,
        icon_fallback="",
        tooltip_key=None,
        tooltip_ns=None,
        tooltip_text=None,
        state="normal",
        variant=None,
        width=None,
        padding=None,
        on_hover=None,
        on_leave=None,
        on_focus=None,
        auto_hover_disabled=True,
        **kwargs,
    ):
        """Fallback icon button creator when component not available."""
        import tkinter as tk
        from typing import Literal, cast

        # Cast state to proper type
        btn_state = cast(
            Literal["normal", "active", "disabled"],
            state if state in ["normal", "active", "disabled"] else "normal",
        )
        # Handle None command
        btn_command = command if command is not None else lambda: None
        btn = tk.Button(
            parent,
            text=icon_fallback or "?",
            command=btn_command,
            state=btn_state,
            **kwargs,
        )
        return btn

    print("Warning: Icon button component not available, using fallback")

try:
    from ui.helpers.capture_helper import capture_region_and_save
except Exception:
    capture_region_and_save = None  # type: ignore

from lib.features.hunt.hunt_config import CONFIG_PATH, HUNT_CONFIG_PATH
from lib.features.hunt.hunt_config import (
    ConfigManager,
    _sanitize_templates,
    load_config,
    load_hunt_config,
    save_config,
    save_hunt_config,
)
from lib.features.hunt.hunt_runner import HuntRunner
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
from lib.features.monsters.monster_repo import (
    calculate_monster_estimate,
    load_monster_library,
    save_monster_library,
)
from lib.features.skills.skill_repo import (
    calculate_attack_speed_from_skills,
)
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from ui.controllers.skill_manager_controller import SkillManagerController
from lib.features.skills.skill_stats import (
    SkillStats,
)  # Sprint 22 Patch 1: Training Mode
from lib.features.timing.calculator import (
    calculate_timing,
    format_timing_recommendation,
    get_timing_presets,
)

# =====================================================================
# Single Instance Lock (Prevent multiple app instances)
from ui.controllers.hotkey_controller import HotkeyController

# =====================================================================
from lib.system.hunt_logger import get_hunt_logger
from lib.system.instance_lock import SingleInstanceLock

from lib.system.win_input import tap
from lib.ui_style import UIStyle as UI  # Global UI style constants
from ui.controllers.app_lifecycle_controller import AppLifecycleController
from ui.windows.hotkey_diag_dialog import show_hotkey_diagnostics_modal
from ui.windows.setup_wizard import show_setup_wizard


class App(tk.Tk):

    @property
    def skills(self):
        """Legacy compatibility property for views still expecting self.app.skills."""
        if hasattr(self, "skill_service"):
            return self.skill_service.get_all_skills()
        return []

    @skills.setter
    def skills(self, value):
        """Legacy setter trap to redirect to service."""
        if hasattr(self, "skill_service"):
            self.skill_service.save_skills(value)

    def _t(self, key: str, **kwargs) -> str:
        return i18n_t(key, ns=I18N_GLOBAL, **kwargs)

    def __init__(self):
        super().__init__()
        # Load config and language
        self.cfg = load_config()
        self.hunt_cfg = load_hunt_config()
        self.lang = str(self.cfg.get("ui", {}).get("language", "vi"))
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass

        self.hotkey_controller = HotkeyController(self, self.hunt_cfg)
        # Centralized icon helper
        try:
            from ui.helpers.icon_helper import get_icon_helper
            from ui.icon_library import register_icons

            self.icon_helper = get_icon_helper()
            register_icons(self.icon_helper)
        except Exception:
            self.icon_helper = None

        # Create config manager for wizard
        self.config_mgr = ConfigManager(self.cfg, self.hunt_cfg)

        self.title(self._t("app_title"))
        self.resizable(False, False)

        # Initialize ScanController
        from lib.features.hunt.scan_controller import ScanController
        from ui.icon_library import Icons

        def getter():
            if hasattr(self, "_vision_engine") and self._vision_engine:
                return self._vision_engine
            from lib.vision.vision_engine import get_vision_engine

            return get_vision_engine()

        self.scan_controller = ScanController(
            vision_engine_getter=getter,
            set_status_text=self._update_scan_status_text,
            set_status_icon=self._update_scan_status_icon,
            show_results=self._show_scan_results,
            icons=Icons,
        )

        # State Bookkeeping Extracted
        from ui.controllers.app_window_controller import AppWindowController
        from ui.controllers.library_manager_controller import LibraryManagerController
        from ui.controllers.app_state_controller import AppStateController
        from ui.controllers.overlay_controller import (
            OverlayController as AppOverlayController,
        )
        from ui.controllers.window_tracker_controller import WindowTrackerController
        from lib.features.monsters.monster_library_service import MonsterLibraryService
        from ui.controllers.monster_manager_controller import MonsterManagerController

        self.state_controller = AppStateController(self)
        self.window_controller = AppWindowController(self)
        self.library_manager_controller = LibraryManagerController(self)
        self.overlay_controller = AppOverlayController(self)
        self.window_tracker_controller = WindowTrackerController(self)
        self.monster_library_service = MonsterLibraryService()
        self.monster_manager_controller = MonsterManagerController(self)
        self.skill_service = SkillRuntimeService()
        self.skill_manager_controller = SkillManagerController(self)

        # --- Menu: Settings (includes Global Hotkeys toggle & retry) ---
        try:
            menubar = tk.Menu(self)
            settings_menu = tk.Menu(menubar, tearoff=0)
            # BooleanVar reflects hunt_cfg setting
            gh_cfg = self.hunt_cfg.get("global_hotkeys", {})
            self._global_hotkeys_var = tk.BooleanVar(
                value=bool(gh_cfg.get("enabled", True))
            )

            def _on_toggle_global_hotkeys():
                enabled = bool(self._global_hotkeys_var.get())
                # Persist setting
                self.hunt_cfg.setdefault("global_hotkeys", {})["enabled"] = enabled
                try:
                    save_hunt_config(self.hunt_cfg)
                except Exception:
                    pass
                # Apply immediately
                if enabled:
                    print("[Hotkeys] User enabled global hotkeys via menu")
                    try:
                        self.hotkey_controller.register_all()
                    except Exception as e:
                        print(f"[Hotkeys] Error re-registering hotkeys: {e}")
                else:
                    print("[Hotkeys] User disabled global hotkeys via menu")
                    try:
                        self.hotkey_controller.unregister_all()
                    except Exception as e:
                        print(f"[Hotkeys] Error unregistering hotkeys: {e}")

            settings_menu.add_checkbutton(
                label=self._t("help_shortcuts"),
                variable=self._global_hotkeys_var,
                command=_on_toggle_global_hotkeys,
            )
            settings_menu.add_separator()

            def _retry_hotkeys():
                print("[Hotkeys] User requested retry registration")
                try:
                    self.hotkey_controller.register_all()
                except Exception as e:
                    print(f"[Hotkeys] Retry failed: {e}")

            settings_menu.add_command(
                label="Retry global hotkeys", command=_retry_hotkeys
            )
            menubar.add_cascade(label="Settings", menu=settings_menu)

            # --- Menu: Vision (Sprint 22 Phase 1B) ---
            vision_menu = tk.Menu(menubar, tearoff=0)

            # Open Vision Wizard (Ctrl+Shift+V)
            vision_label = (
                "Open Vision Wizard" if self.lang == "en" else "Mở Trợ lý Vision"
            )
            vision_menu.add_command(
                label=vision_label,
                accelerator="Ctrl+Shift+V",
                command=self.window_controller.open_vision_wizard,
            )

            vision_menu.add_separator()

            # Scan Region (Ctrl+Alt+S)
            scan_label = "Scan Region" if self.lang == "en" else "Quét Vùng"
            vision_menu.add_command(
                label=scan_label, accelerator="Ctrl+Alt+S", command=self._scan_region
            )

            # Add Template (Ctrl+T)
            add_tmpl_label = "Add Template" if self.lang == "en" else "Thêm Template"
            vision_menu.add_command(
                label=add_tmpl_label, accelerator="Ctrl+T", command=self._add_template
            )

            # Manage Templates (Ctrl+Shift+T)
            manage_tmpl_label = (
                "Manage Templates" if self.lang == "en" else "Quản lý Templates"
            )
            vision_menu.add_command(
                label=manage_tmpl_label,
                accelerator="Ctrl+Shift+T",
                command=self._manage_templates,
            )

            vision_menu.add_separator()

            # Toggle Overlay (Ctrl+Shift+O) - using translations
            vision_menu.add_command(
                label=self._t("vision_toggle_overlay"),
                accelerator="Ctrl+Shift+O",
                command=self.overlay_controller.toggle_overlay,
            )

            # Overlay Settings - using translations
            overlay_settings_label = (
                "Overlay Settings..." if self.lang == "en" else "Cài Đặt Overlay..."
            )
            vision_menu.add_command(
                label=overlay_settings_label,
                command=self.overlay_controller.open_settings,
            )

            menubar.add_cascade(label="Vision", menu=vision_menu)
            print("[Vision Menu] Created successfully")

            try:
                self.config(menu=menubar)
            except Exception:
                # Some environments may not support menu on top-level; ignore
                pass
        except Exception as e:
            print(f"[Menu] Error creating menubar: {e}")

        # Check PIL availability (for image preview features)
        self.pil_available = (
            Image is not None and ImageTk is not None and ImageDraw is not None
        )

        self.monsters = self.skill_service._normalize_library_items(
            self.monster_library_service.load_monsters()
        )
        self.monster_selected_name = self.monsters[0]["name"] if self.monsters else None

        # Phase 3: Multi-Monster Support
        self.monster_rotation_list = (
            []
        )  # [{"name": "Coc Go 2", "priority": 1, "enabled": True}, ...]
        self._load_monster_rotation_list()

        # Sprint 22 Patch 2: Separate training dummy list
        self.training_monster_list = (
            []
        )  # [{"name": "Coc go~", "priority": 1, "enabled": True, "training_mode": True}]
        self._config_migrated = False  # Track if migration happened
        self._load_training_monster_list()

        # Sprint 22 Patch 2: Auto-save if "Coc go" was migrated from monster_list to training_monster_list
        if self._config_migrated:
            # Update hunt_cfg with both lists before saving
            self.hunt_cfg["monster_list"] = self.monster_rotation_list
            self.hunt_cfg["training_monster_list"] = self.training_monster_list
            save_hunt_config(self.hunt_cfg)
            self._config_migrated = False
            print(
                "[Migration] ✅ Auto-migrated 'Coc go' variants to training_monster_list and saved config."
            )

        # If migration created anonymous skill_slots (blank names) from legacy attack_keys,
        # try to map them to actual attack skills from the skill library for a better UX.
        try:
            slots = self.hunt_cfg.get("skill_slots", [])
            # find anonymous slots (name is empty but key present)
            anon_indices = [
                i
                for i, s in enumerate(slots)
                if isinstance(s, dict) and not s.get("name") and s.get("key")
            ]
            if anon_indices:
                # Inform the user that a legacy migration occurred (attack_keys -> skill_slots)
                try:
                    # Show a gentle migration notice (one-time modal)
                    messagebox.showinfo(
                        self._t("migration_legacy_attack_keys_title"),
                        self._t("migration_legacy_attack_keys_message"),
                    )
                except Exception:
                    pass

            if anon_indices and self.skills:
                # collect candidate attack skill names that are not already assigned
                assigned = {
                    s.get("name")
                    for s in slots
                    if isinstance(s, dict) and s.get("name")
                }
                attack_names = [
                    sk["name"]
                    for sk in self.skills
                    if sk.get("type", "attack") == "attack"
                    and sk.get("name")
                    and sk.get("name") not in assigned
                ]
                changed = False
                for idx in anon_indices:
                    if not attack_names:
                        break
                    name = attack_names.pop(0)
                    slots[idx]["name"] = name
                    changed = True
                if changed:
                    # persist mapping
                    self.hunt_cfg["skill_slots"] = slots
                    try:
                        save_hunt_config(self.hunt_cfg)
                        try:
                            # show auto-mapped details if available
                            mapped = ", ".join(
                                [
                                    slots[i].get("name", "")
                                    for i in anon_indices
                                    if slots[i].get("name")
                                ]
                            )
                            info_msg = self._t(
                                "migration_legacy_attack_keys_auto_mapped"
                            ).format(mapped=mapped)
                            messagebox.showinfo(self._t("skill_section"), info_msg)
                        except Exception:
                            pass
                        # also set a short hunt status message
                        self.hunt_status.set(self._t("migration_mapped_slots_short"))
                    except Exception:
                        # non-fatal
                        pass
        except Exception:
            pass
        self.skill_selected_name = self.skills[0]["name"] if self.skills else None
        self.skill_slot_saved_names = [
            slot.get("name", "")
            for slot in self.hunt_cfg.get("skill_slots", [])
            if isinstance(slot, dict) and slot.get("name")
        ]
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
        self._thumbnail_cache = {}  # path -> PhotoImage cache
        self.monster_bounds_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }

        # Configuration is already migrated during load_hunt_config
        from lib.features.hunt.window_selection_service import WindowSelectionService

        safe_area = get_valid_hunt_area(self.hunt_cfg)
        self.hunt_cfg["hunt_area"] = safe_area
        self.current_window_bounds = safe_area.get("window_bounds")
        WindowSelectionService.update_bounds(self.hunt_cfg, self.current_window_bounds)

        if pyautogui is not None:
            pyautogui.FAILSAFE = bool(self.cfg.get("safety", {}).get("failsafe", True))

        self._build_ui()
        self.hunt_runner = HuntRunner(
            hunt_cfg=self.hunt_cfg,
            set_status=(
                self.hunt_status.set if hasattr(self, "hunt_status") else lambda _: None
            ),
            set_target_info=(
                self.hunt_target_info.set
                if hasattr(self, "hunt_target_info")
                else lambda _: None
            ),
            get_overlay_ctrl=lambda: getattr(self, "overlay_ctrl", None),
            get_notebook=lambda: getattr(self, "notebook", None),
            tab_setup=getattr(self, "tab_setup", None),
            tab_hunt=getattr(self, "tab_hunt", None),
            schedule_ui_task=lambda fn: (
                self.after(0, fn) if hasattr(self, "after") else fn()
            ),
        )

        self.hunt_orchestrator = HuntOrchestrator(
            on_status_update=(
                self.hunt_status.set if hasattr(self, "hunt_status") else lambda _: None
            ),
            on_state_change=self._on_orchestrator_state_change,
            locate_target=self.state_controller._hunt_locate_target,
            prepare_skill_runtime=self.state_controller._prepare_skill_runtime,
            try_cast_skills=self.state_controller._try_cast_skills,
            bring_window_to_front=self.window_controller._bring_window_to_front,
            bring_window_to_front_by_hwnd=self.window_controller._bring_window_to_front_by_hwnd,
            bring_window_to_front_by_pid=self.window_controller._bring_window_to_front_by_pid,
            iconify_app=self.iconify,
            update_skill_stats_display=getattr(
                self, "update_skill_stats_display", lambda _: None
            ),
            get_hunt_selected=lambda: getattr(self, "hunt_selected", {}),
            schedule_ui_task=lambda fn: (
                self.after(0, fn) if hasattr(self, "after") else fn()
            ),
        )

        # Keyboard shortcuts (Window-focused only)
        self.bind(
            "<Control-k>", lambda e: self.skill_manager_controller.open_window()
        )  # Ctrl+K: Manage skills
        self.bind("<Alt-Key-1>", lambda e: self._switch_to_tab(0))  # Alt+1: Hunt tab
        self.bind("<Alt-Key-2>", lambda e: self._switch_to_tab(1))  # Alt+2: Setup tab

        self.hotkey_controller.register_all()
        self.lifecycle_controller = AppLifecycleController(self)
        self.lifecycle_controller.start_lifecycle()

    # -----------------
    def _build_ui(self):
        from lib.ui_style import UIStyle as UI
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # Header Frame (App Title and Language Selector) - 56px height
        self.header_frame = tk.Frame(self, bg=UI.BG_TITLE, height=56)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        # Title
        tk.Label(
            self.header_frame,
            text=self._t("app_title"),
            bg=UI.BG_TITLE,
            fg=UI.BG_DEFAULT,
            font=UI.FONT_TITLE
        ).pack(side="left", padx=16, pady=14)

        # Right side of header: Language selector
        lang_frame = tk.Frame(self.header_frame, bg=UI.BG_TITLE)
        lang_frame.pack(side="right", padx=16, pady=14)
        tk.Label(
            lang_frame,
            text=self._t("language"),
            bg=UI.BG_TITLE,
            fg=UI.BG_DEFAULT
        ).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cmb = ttk.Combobox(
            lang_frame, textvariable=self.lang_var, state="readonly", width=8
        )
        lang_cmb["values"] = ("en", "vi")
        lang_cmb.pack(side="left", padx=(6, 0))
        lang_cmb.bind("<<ComboboxSelected>>", self.on_language_change)


        # Vùng A: Quick Action Bar - 80px target height (using padding)
        self.action_bar_frame = tk.Frame(self, padx=32, pady=18)
        self.action_bar_frame.pack(fill="x")

        # Window Selection Combobox
        self.win_combo_var = tk.StringVar()
        self.win_combo = ttk.Combobox(
            self.action_bar_frame, textvariable=self.win_combo_var, state="readonly", width=55
        )
        self.win_combo.pack(side="left", fill="y", padx=(0, 12))

        # Auto-populate windows when dropdown is clicked
        self.win_combo.bind(
            "<Button-1>",
            lambda e: (
                self.window_controller.on_hunt_find_windows()
                if not self.win_items
                else None
            ),
        )
        # Handle window selection
        self.win_combo.bind(
            "<<ComboboxSelected>>", self.window_controller.on_window_combo_selected
        )

        # Attach tooltip to combobox explaining window selection
        attach_i18n_tooltip(
            self.win_combo,
            key="window_select_tooltip",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        # Refresh button - Using icon_button component
        refresh_tooltip = (
            "Refresh Window List\n" "Scans for game windows"
            if self.lang == "en"
            else "Làm Mới Danh Sách Cửa Sổ\n" "Quét lại các cửa sổ game"
        )

        refresh_btn = _create_icon_btn_component(
            parent=self.action_bar_frame,
            icon_name="refresh",
            icon_fallback="🔄",
            icon_size=16,
            button_size=36,
            command=self.window_controller.on_hunt_refresh_windows,
            button_type="refresh",
            tooltip_text=refresh_tooltip,
            state="normal",
            auto_hover_disabled=False,
        )
        refresh_btn.pack(side="left", padx=(0, 12))

        # Bounds Readiness State Placeholder (Minimum 260x36)
        self.bounds_placeholder = tk.Frame(self.action_bar_frame, width=260, height=36)
        self.bounds_placeholder.pack(side="left", padx=(0, 12))
        self.bounds_placeholder.pack_propagate(False)

        self.bounds_status_var = tk.StringVar()
        self.bounds_readiness_label = tk.Label(
            self.bounds_placeholder,
            textvariable=self.bounds_status_var,
            font=UI.FONT_LABEL
        )
        self.bounds_readiness_label.pack(side="left", fill="y", padx=5)

        # Start Hunt Button
        start_tooltip = self._t("start_hunt") + "\n(Ctrl+F5)"

        self.hunt_start_btn = _create_icon_btn_component(
            parent=self.action_bar_frame,
            icon_name="start",
            icon_fallback="▶️",
            text=self._t("start_hunt"),
            icon_size=20,
            button_size=44,
            padding={'padx': 20, 'pady': 6},
            command=self.on_hunt_start,
            button_type="green",
            tooltip_text=start_tooltip,
            state="normal",
            auto_hover_disabled=False,
        )
        self.hunt_start_btn.pack(side="left", padx=(0, 12))

        # Stop Hunt Button
        stop_tooltip = self._t("stop_hunt") + "\n(Ctrl+F6)"

        self.hunt_stop_btn = _create_icon_btn_component(
            parent=self.action_bar_frame,
            icon_name="stop",
            icon_fallback="⏹️",
            text=self._t("stop_hunt"),
            icon_size=20,
            button_size=44,
            padding={'padx': 20, 'pady': 6},
            command=self.on_hunt_stop,
            button_type="red",
            tooltip_text=stop_tooltip,
            state="disabled",
            auto_hover_disabled=True,
        )
        self.hunt_stop_btn.pack(side="left")

        # Store notebook reference for keyboard shortcuts
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, pady=(0, 8))

        from ui.tabs.hunt_tab import HuntTab

        self.tab_hunt = HuntTab(self.notebook, self)
        from ui.tabs.setup_tab import SetupTab

        self.tab_setup = SetupTab(self.notebook, self)
        from ui.tabs.stats_tab import StatsTab

        self.tab_stats = StatsTab(self.notebook, self)
        from ui.tabs.help_tab import HelpTab

        self.tab_help = HelpTab(self.notebook, self)
        self.notebook.add(self.tab_hunt, text=self._t("tab_hunt"))
        self.notebook.add(self.tab_setup, text=self._t("tab_setup"))
        self.notebook.add(self.tab_stats, text=self._t("tab_stats"))
        self.notebook.add(self.tab_help, text=self._t("tab_help"))

        # Global Apply Section (below tabs, right-aligned)
        self._build_global_apply_section()

        # DB Status Bar (bottom of window)
        self._db_status_var = tk.StringVar(value="⏳ Đang kiểm tra CSDL...")
        self._db_status_bar = tk.Label(
            self,
            textvariable=self._db_status_var,
            anchor="w",
            padx=8,
            pady=3,
            font=("Arial", 9),
            bg="#e8e8e8",
            fg="#555555",
            relief="sunken",
        )
        self._db_status_bar.pack(fill="x", side="bottom")

    def _build_global_apply_section(self):
        """Build global apply button section below tabs."""
        # Frame for global apply section (right-aligned)
        apply_frame = tk.Frame(self, relief="sunken", bd=1, bg="#f0f0f0")
        apply_frame.pack(fill="x", padx=8, pady=(0, 8))

        # Unsaved changes indicator (left side)
        indicator_frame = tk.Frame(apply_frame, bg="#f0f0f0")
        indicator_frame.pack(side="left", padx=8, pady=6)

        self.unsaved_indicator_label = tk.Label(
            indicator_frame, text="", fg="#666", font=("Arial", 9), bg="#f0f0f0"
        )
        self.unsaved_indicator_label.pack(side="left")

        # Apply All Settings button (right side) - Using global green_light style with save icon
        # Optimized for: Negative Space, Hierarchy, Contrast Ratio (WCAG AA: 5.26:1)
        from ui.helpers.button_styles import get_button_config

        apply_config = get_button_config("green_light")

        # Load save icon (22px to scale with 11pt font)
        save_icon = self._icon("save", "💾", size=22)

        apply_kwargs = dict(apply_config)
        apply_text = self._t("apply_all_settings")
        if not isinstance(save_icon, str):
            apply_kwargs.update({"image": save_icon, "compound": "left"})
            apply_text = f" {apply_text}"
        else:
            apply_text = f"💾 {apply_text}"
        self.global_apply_btn = tk.Button(
            apply_frame,
            text=apply_text,
            command=self.on_global_apply,
            padx=24,
            pady=10,
            **apply_kwargs,
        )
        self.global_apply_btn.pack(
            side="right", padx=10, pady=6
        )  # Increased external margins

        # Scan Manual Button
        from ui.components import create_icon_button
        from ui.icon_library import Icons

        self.scan_btn_icon_name = Icons.SCAN_SCREEN

        def on_scan_clicked():
            if hasattr(self, "scan_controller"):
                self.scan_controller.run_scan(manual=True)

        self.btn_manual_scan = create_icon_button(
            apply_frame,
            icon_name=self.scan_btn_icon_name,
            text="",
            command=on_scan_clicked,
            icon_fallback="🔍",
            icon_size=22,
            padding={"padx": 10, "pady": 10},
        )
        self.btn_manual_scan.pack(side="right", padx=8, pady=6)

        # Keep reference to prevent garbage collection
        if not isinstance(save_icon, str):
            try:
                self._image_refs.append(save_icon)
            except Exception:
                pass

        # Initialize unsaved state
        self.has_unsaved_changes = False
        self._update_unsaved_indicator()

    # Click Tab removed

    # Hunt Tab (Refactored - Sprint 18 Phase 4 Task #2 + UX Enhancement)

    def _update_scan_status_text(self, text):
        if hasattr(self, "hunt_status"):
            self.after(0, lambda: self.hunt_status.set(text))

    def _update_scan_status_icon(self, icon_name):
        if hasattr(self, "btn_manual_scan") and self.btn_manual_scan:
            try:
                from ui.helpers.icon_helper import get_icon_helper

                helper = get_icon_helper()
                img = helper.get_icon(icon_name, fallback="🔍", size=22)

                def update():
                    if isinstance(img, str):
                        self.btn_manual_scan.config(text=img, image="")
                    else:
                        self.btn_manual_scan.config(image=img, text="")
                        self._btn_scan_ref = (
                            img  # Store a single reference to avoid memory leak
                        )

                self.after(0, update)
            except Exception as e:
                print(f"[UI] Error updating scan status icon: {e}")

    def _show_scan_results(self, results):
        pass  # Optional mock since it's just messagebox in real app or we can add it

    def _load_monster_rotation_list(self):
        saved_list = self.hunt_cfg.get("monster_list", [])
        self.monster_rotation_list = []
        for item in saved_list:
            if isinstance(item, dict):
                self.monster_rotation_list.append(
                    {
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "enabled": item.get("enabled", True),
                    }
                )

    def _load_training_monster_list(self):
        saved_list = self.hunt_cfg.get("training_monster_list", [])
        self.training_monster_list = []
        for item in saved_list:
            if isinstance(item, dict):
                self.training_monster_list.append(
                    {
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "enabled": item.get("enabled", True),
                        "training_mode": True,
                    }
                )

    def on_language_change(self, _evt=None):
        self.lang = self.lang_var.get()
        self.cfg.setdefault("ui", {})
        self.cfg["ui"]["language"] = self.lang
        save_config(self.cfg)
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        # Rebuild UI with new language
        self.title(self._t("app_title"))
        self._build_ui()

    def on_setup_wizard(self, hide_parent=True):
        self.window_controller.on_setup_wizard(hide_parent)

    def try_close_setup_wizard(self) -> bool:
        return self.window_controller.try_close_setup_wizard()

    def _switch_to_tab(self, tab_index: int):
        """Switch to specified tab via keyboard shortcut."""
        try:
            if not hasattr(self, "notebook"):
                return

            # Switch to tab
            self.notebook.select(tab_index)

            # Update status with shortcut indicator
            tab_names = ["Hunt", "Setup", "Stats", "Help"]
            if 0 <= tab_index < len(tab_names):
                tab_name = tab_names[tab_index]
                shortcut = f"Alt+{tab_index + 1}"
                if hasattr(self, "hunt_status"):
                    self.hunt_status.set(f"{shortcut}: Switched to {tab_name} tab")
        except Exception as e:
            print(f"Tab switch error: {e}")

    def _on_vision_wizard_closed(self):
        """Callback when Vision Wizard is closed"""
        print("[Vision] Wizard closed")
        # TODO Phase 2: Refresh templates or update UI if needed

    def _update_hotkeys_state(self):
        """Update Setup Wizard hotkey enable/disable state based on UI mode.

        Called when:
        - UI mode changes (beginner/intermediate/advanced)
        - Global hotkeys are re-registered

        Rules:
        - Setup Wizard hotkey: Only active in beginner mode
        - Library Manager hotkey: Always active
        """
        mode = (
            self.setup_mode_var.get() if hasattr(self, "setup_mode_var") else "beginner"
        )

        # Update Setup Wizard hotkey combo state
        if hasattr(self, "wizard_hotkey_combo"):
            if mode == "beginner":
                self.wizard_hotkey_combo.config(state="readonly")
                if hasattr(self, "wizard_hotkey_label"):
                    self.wizard_hotkey_label.config(fg="black")
            else:
                self.wizard_hotkey_combo.config(state="disabled")
                if hasattr(self, "wizard_hotkey_label"):
                    self.wizard_hotkey_label.config(fg="#999")

        # Library Manager hotkey always enabled (no change needed)
        # But we re-register hotkeys to update wizard hotkey state
        if hasattr(self, "hunt_cfg"):
            self.hotkey_controller.register_all()

    # --- Helpers to attempt closing other windows while respecting unsaved changes ---
    def _update_hotkey_diagnostics_ui(self):
        """Update the hotkey status UI based on registration state.

        This new implementation uses a status-driven approach:
        - Success state: Show green checkmark, hide action buttons
        - Partial failure: Show orange warning, show retry button
        - Complete failure: Show red error, show both buttons
        """
        try:
            # Determine current state
            has_import_error = (
                hasattr(self, "_hotkey_import_diag") and self._hotkey_import_diag
            )
            has_failed_hotkeys = (
                hasattr(self.hotkey_controller, "_failed_hotkeys")
                and self.hotkey_controller._failed_hotkeys
            )
            hotkeys_enabled = getattr(
                self.hotkey_controller, "_hotkeys_registered_ok", False
            )

            # Count actual registered hotkeys (not bindings)
            registered_count = 0
            hotkey_details = []

            if getattr(self.hotkey_controller, "_global_start_hotkey", None):
                registered_count += 1
                hotkey_details.append("Start" if self.lang == "en" else "Báº¯t Ä‘áº§u")
            if getattr(self.hotkey_controller, "_global_stop_hotkey", None):
                registered_count += 1
                hotkey_details.append("Stop" if self.lang == "en" else "Dừng")
            if getattr(self.hotkey_controller, "_global_wizard_hotkey", None):
                registered_count += 1
                hotkey_details.append("Wizard" if self.lang == "en" else "Trợ lý")
            if getattr(self.hotkey_controller, "_global_library_hotkey", None):
                registered_count += 1
                hotkey_details.append("Library" if self.lang == "en" else "Thư viện")
            if getattr(self.hotkey_controller, "_global_vision_hotkey", None):
                registered_count += 1
                hotkey_details.append("Vision" if self.lang == "en" else "Thị giác")

            # State 1: Success - All hotkeys registered
            if hotkeys_enabled and not has_failed_hotkeys and not has_import_error:
                # Green success state
                success_text = (
                    "All hotkeys registered successfully"
                    if self.lang == "en"
                    else "Tất cả phím tắt đã đăng ký thành công"
                )
                self._hotkey_status_var.set(f"✅ {success_text}")
                self._hotkey_status_label.config(fg="#4CAF50")  # Green

                # Show count and active hotkeys list
                detail_text = (
                    f"{registered_count} hotkeys active"
                    if self.lang == "en"
                    else f"{registered_count} phím tắt đang hoạt động"
                )
                if hotkey_details:
                    detail_text += f": {', '.join(hotkey_details)}"
                self._hotkey_status_detail_var.set(f"   {detail_text}")

                # Hide action buttons (not needed)
                if hasattr(self, "_hotkey_retry_btn"):
                    self._hotkey_retry_btn.pack_forget()
                if hasattr(self, "_hotkey_details_btn"):
                    self._hotkey_details_btn.pack_forget()

            # State 2: Partial failure - Some hotkeys failed
            elif has_failed_hotkeys and not has_import_error:
                # Orange warning state
                failed_count = len(self.hotkey_controller._failed_hotkeys)
                warning_text = (
                    f"{failed_count} hotkey(s) failed to register"
                    if self.lang == "en"
                    else f"{failed_count} phím tắt đăng ký thất bại"
                )
                self._hotkey_status_var.set(f"⚠️ {warning_text}")
                self._hotkey_status_label.config(fg="#FF9800")  # Orange

                # Show guidance
                guidance = (
                    "Try changing the conflicting hotkey, then click Apply."
                    if self.lang == "en"
                    else "Thử đổi phím tắt bị xung đột, sau đó nhấn Áp dụng."
                )
                self._hotkey_status_detail_var.set(f"   {guidance}")

                # Show retry button only
                if hasattr(self, "_hotkey_retry_btn"):
                    retry_text = (
                        "🔄 Retry Registration"
                        if self.lang == "en"
                        else "🔄 Thử Đăng Ký Lại"
                    )
                    self._hotkey_retry_btn.config(text=retry_text)
                    self._hotkey_retry_btn.pack(side="left", padx=(0, 8))
                if hasattr(self, "_hotkey_details_btn"):
                    self._hotkey_details_btn.pack_forget()

            # State 3: Complete failure - Import error or no hotkeys registered
            else:
                # Red error state
                error_text = (
                    "Hotkeys not available"
                    if self.lang == "en"
                    else "Phím tắt không khả dụng"
                )
                self._hotkey_status_var.set(f"❌ {error_text}")
                self._hotkey_status_label.config(fg="#F44336")  # Red

                # Show explanation
                if has_import_error:
                    explanation = (
                        "The 'keyboard' package is not installed in your Python environment."
                        if self.lang == "en"
                        else "Gói 'keyboard' chưa được cài đặt trong Python của bạn."
                    )
                else:
                    explanation = (
                        "Failed to register global hotkeys."
                        if self.lang == "en"
                        else "Không thể đăng ký phím tắt toàn cục."
                    )
                self._hotkey_status_detail_var.set(f"   {explanation}")

                # Show both buttons
                if hasattr(self, "_hotkey_details_btn"):
                    fix_text = (
                        "📋 Show Fix Instructions"
                        if self.lang == "en"
                        else "📋 Hướng Dẫn Khắc Phục"
                    )
                    self._hotkey_details_btn.config(text=fix_text)
                    self._hotkey_details_btn.pack(side="left", padx=(0, 8))
                if hasattr(self, "_hotkey_retry_btn"):
                    retry_text = (
                        "🔄 Retry After Fix"
                        if self.lang == "en"
                        else "🔄 Thử Lại Sau Khi Sửa"
                    )
                    self._hotkey_retry_btn.config(text=retry_text)
                    self._hotkey_retry_btn.pack(side="left")

        except Exception as e:
            # Fallback: show basic error
            try:
                self._hotkey_status_var.set(f"⚠️ Error updating status: {e}")
                self._hotkey_status_label.config(fg="#FF9800")
            except Exception:
                pass

    def _on_orchestrator_state_change(self, state: str):
        if state == "running":
            self.hunt_start_btn.config(
                state="disabled", bg="#A5D6A7", relief="sunken", cursor="arrow"
            )
            self.hunt_stop_btn.config(
                state="normal", bg="#C62828", relief="raised", cursor="hand2"
            )
            if hasattr(self, "hunt_status"):
                self.hunt_status.set(self._t("hunt_running"))
        elif state in ["idle", "error", "stopped"]:
            self.hunt_start_btn.config(
                state="normal", bg="#4CAF50", relief="raised", cursor="hand2"
            )
            self.hunt_stop_btn.config(
                state="disabled", bg="#FFCDD2", relief="sunken", cursor="arrow"
            )
            if state == "idle" and hasattr(self, "hunt_status"):
                self.hunt_status.set(
                    self._t("hunt_idle") if hasattr(self, "_t") else "Idle"
                )

    def on_hunt_start(self):
        if hasattr(self, "hunt_orchestrator") and self.hunt_orchestrator.hunt_running:
            return

        validation_error = self.state_controller._validate_hunt_prerequisites()
        if validation_error:
            messagebox.showerror(self._t("error_title"), validation_error, parent=self)
            return

        try:
            cfg = self.state_controller._hunt_from_ui()
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), self._t("invalid_hunt").format(e=e)
            )
            return
        save_hunt_config(cfg)
        self.hunt_cfg = cfg

        self.hunt_orchestrator.start_hunt(self.hunt_cfg)

    def on_hunt_stop(self):
        if hasattr(self, "hunt_orchestrator"):
            self.hunt_orchestrator.stop_hunt()

    # -----------------
    # Close
    # -----------------
    def _open_vision_wizard(self):
        self.window_controller.open_vision_wizard()

    def _scan_region(self):
        """
        Scan region for template matching (Ctrl+Alt+S).
        TODO Phase 2: Implement region scanning with overlay.
        """
        print("[Vision] Scan region - TODO Phase 2")
        messagebox.showinfo(
            "Vision - Scan Region",
            "Scan Region feature will be available in Phase 2.\n\n"
            "This will allow you to:\n"
            "• Select a region on screen\n"
            "• Scan for templates in real-time\n"
            "• Save ROI coordinates",
        )

    def _add_template(self):
        """
        Quick add template (Ctrl+T).
        Opens file dialog to select template image.
        TODO Phase 2: Add to config and Vision Wizard list.
        """
        print("[Vision] Add template")

        try:
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*"),
            ]

            file_path = filedialog.askopenfilename(
                parent=self,
                title=(
                    self._t("vision_add_template")
                    if hasattr(self, "_t")
                    else "Add Template"
                ),
                filetypes=filetypes,
            )

            if file_path:
                print(f"[Vision] Selected template: {file_path}")

                # TODO Phase 2: Add to config
                # For now, just show success message
                messagebox.showinfo(
                    "Vision - Add Template",
                    f"Template selected:\n{file_path}\n\n"
                    "Full integration will be available in Phase 2.\n"
                    "Use Vision Wizard (Ctrl+Shift+V) to manage templates.",
                )

        except Exception as e:
            print(f"[Vision] Error adding template: {e}")
            messagebox.showerror(
                self._t("error") if hasattr(self, "_t") else "Error",
                f"Cannot add template:\n{e}",
            )

    def _manage_templates(self):
        """
        Open template management (Ctrl+Shift+T).
        Shortcut to Vision Wizard.
        """
        print("[Vision] Manage templates - opening wizard")
        self.window_controller.open_vision_wizard()

    def _on_rotation_mode_changed(self, event=None):
        """Handle rotation mode change."""
        mode = self.rotation_mode_var.get()
        self.hunt_cfg["rotation_mode"] = mode
        self._refresh_monster_rotation_list()
        self.hunt_status.set(f"Rotation mode: {mode}")

    def _refresh_monster_rotation_list(self):
        """Refresh the monster rotation listbox display.

        Sprint 22 Patch 2: Show training_monster_list when training mode active,
        otherwise show monster_rotation_list (normal monsters).
        """
        if not hasattr(self, "monster_rotation_listbox"):
            return

        self.monster_rotation_listbox.delete(0, tk.END)

        # Sprint 22 Patch 2: Auto-detect training mode from training_monster_list
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        # Update frame title to show current mode
        self._update_monster_frame_title(has_training_list)

        # Choose which list to display
        if has_training_list:
            # Training mode: Show training_monster_list
            display_list = self.training_monster_list
        else:
            # Normal mode: Show monster_rotation_list
            display_list = self.monster_rotation_list

        for item in display_list:
            check = "☑" if item["enabled"] else "☐"
            display = f"{check} {item['name']}"
            if self.hunt_cfg.get("rotation_mode") == "priority":
                display += f" (P{item['priority']})"
            # Add training dummy indicator
            if item.get("training_mode", False):
                display += " 🎯"
            self.monster_rotation_listbox.insert(tk.END, display)

        self._update_monster_status()
        self._update_rotation_mode_description()

        # Update button states if in training mode
        if hasattr(self, "training_mode_var"):
            self._update_training_mode_buttons()

    def _load_skill_slots_from_cfg(self):
        saved = (
            self.hunt_cfg.get("skill_slots", []) if hasattr(self, "hunt_cfg") else []
        )

        # Handle both formats: list of strings (old) and list of dicts (new)
        normalized_slots = []
        for slot in saved:
            if isinstance(slot, dict):
                # New format: {"name": "skill_name"}
                normalized_slots.append(slot.get("name", ""))
            elif isinstance(slot, str):
                # Old format: "skill_name"
                normalized_slots.append(slot)
            else:
                normalized_slots.append("")

        # Extract non-empty names for saved skills
        self.skill_slot_saved_names = [name for name in normalized_slots if name]

        self._refresh_skill_slots_options()

        # Load saved slots into UI
        for idx, var in enumerate(self.skill_slot_vars):
            name = ""
            if idx < len(normalized_slots):
                name = normalized_slots[idx]
            var.set(name)

        self._update_attack_keys_from_slots()

    def _on_setup_mode_changed(self):
        """Handle mode change in Setup tab and sync with Hunt tab."""
        mode = self.setup_mode_var.get()

        # Save mode preference
        self.hunt_cfg["ui_mode"] = mode
        try:
            with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")

        # Sync Hunt tab mode var if it exists
        if hasattr(self, "hunt_mode_var"):
            self.hunt_mode_var.set(mode)
            self.state_controller._apply_hunt_mode()

        # Update Setup tab visibility
        self._update_setup_visibility()

        # Update status if exists
        if hasattr(self, "hunt_status"):
            mode_labels = {
                "beginner": self._t("mode_beginner"),
                "intermediate": self._t("mode_intermediate"),
                "advanced": self._t("mode_advanced"),
            }
            self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)}")

        # Re-register hotkeys (wizard hotkey only in beginner mode)
        # This will update the count display (4 vs 5 hotkeys)
        try:
            self.hotkey_controller.register_all()
        except Exception as e:
            print(f"Warning: Could not re-register hotkeys after mode change: {e}")

    def _apply_setup_settings(self, save_to_file=True):
        """Apply all settings from Setup tab to hunt_config and sync to Hunt tab.

        Args:
            save_to_file: If True, save to hunt_config.json immediately.
                         If False, only update self.hunt_cfg (used by on_global_apply to avoid duplicate writes).
        """
        try:
            # Update hunt_cfg with values from Setup tab
            self.hunt_cfg["target_key"] = self.setup_target_key_var.get()
            # attack_keys removed: attack keys are derived from skill_slots (per-skill key assignments)
            self.hunt_cfg["attack_press_ms"] = int(self.setup_press_ms_var.get())
            self.hunt_cfg["target_cycle_delay"] = float(
                self.setup_target_cycle_var.get()
            )
            self.hunt_cfg["search_interval"] = float(
                self.setup_search_interval_var.get()
            )
            self.hunt_cfg["attack_interval"] = float(
                self.setup_attack_interval_var.get()
            )
            self.hunt_cfg["lost_timeout_sec"] = float(self.setup_lost_timeout_var.get())
            self.hunt_cfg["attack_min_duration_sec"] = float(
                self.setup_attack_duration_var.get()
            )
            self.hunt_cfg["template_threshold"] = float(self.setup_threshold_var.get())
            self.hunt_cfg["template_path"] = self.setup_template_var.get()

            # Region
            try:
                l = int(self.setup_reg_l.get()) if self.setup_reg_l.get() else ""
                t = int(self.setup_reg_t.get()) if self.setup_reg_t.get() else ""
                w = int(self.setup_reg_w.get()) if self.setup_reg_w.get() else ""
                h = int(self.setup_reg_h.get()) if self.setup_reg_h.get() else ""
                self.hunt_cfg["region"] = [l, t, w, h]
            except ValueError:
                self.hunt_cfg["region"] = ["", "", "", ""]

            # Save to file only if requested
            if save_to_file:
                with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)

            # Sync to Hunt tab vars if they exist
            if hasattr(self, "target_key_var"):
                self.target_key_var.set(self.hunt_cfg["target_key"])
            # attack_keys removed: UI reads keys from skill_slots directly
            if hasattr(self, "attack_press_var"):
                self.attack_press_var.set(str(self.hunt_cfg["attack_press_ms"]))
            if hasattr(self, "target_cycle_var"):
                self.target_cycle_var.set(str(self.hunt_cfg["target_cycle_delay"]))
            if hasattr(self, "search_interval_var"):
                self.search_interval_var.set(str(self.hunt_cfg["search_interval"]))
            if hasattr(self, "attack_interval_var"):
                self.attack_interval_var.set(str(self.hunt_cfg["attack_interval"]))
            if hasattr(self, "lost_timeout_var"):
                self.lost_timeout_var.set(str(self.hunt_cfg["lost_timeout_sec"]))
            if hasattr(self, "attack_duration_var"):
                self.attack_duration_var.set(
                    str(self.hunt_cfg["attack_min_duration_sec"])
                )
            if hasattr(self, "template_var"):
                self.template_var.set(self.hunt_cfg["template_path"])
            if hasattr(self, "reg_l"):
                region = self.hunt_cfg["region"]
                self.reg_l.set(str(region[0]) if region[0] != "" else "")
                self.reg_t.set(str(region[1]) if region[1] != "" else "")
                self.reg_w.set(str(region[2]) if region[2] != "" else "")
                self.reg_h.set(str(region[3]) if region[3] != "" else "")

            # Show success feedback only when saving directly (not called from on_global_apply)
            if save_to_file:
                # Update status
                if hasattr(self, "hunt_status"):
                    self.hunt_status.set(self._t("settings_applied_success"))

                # Show success message
                messagebox.showinfo(
                    self._t("success_title"), self._t("settings_applied_message")
                )

        except ValueError as e:
            messagebox.showerror(
                self._t("error_title"),
                self._t("error_invalid_number").format(field=str(e)),
            )
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), f"Failed to apply settings: {e}"
            )

    # Phase 3: Multi-Monster Support Handlers
    def _update_setup_visibility(self):
        """Show/hide Setup tab sections based on current mode.

        NOTE: adv_frame/window_frame live on SetupTab (self.tab_setup), not on App;
        delegate there instead of duplicating the stale pre-Sprint-18 logic.
        """
        if hasattr(self, "tab_setup") and hasattr(
            self.tab_setup, "_update_setup_visibility"
        ):
            self.tab_setup._update_setup_visibility()

        # Update hotkeys state based on mode
        self._update_hotkeys_state()

    def update_skill_stats_display(self, stats_dict):
        """Update skill performance statistics display (Sprint 22 Patch 1).

        Args:
            stats_dict: Dictionary from SkillStats.get_all_stats() containing:
                {
                    'Skill Name': {
                        'cast_count': int,
                        'last_cast': float (timestamp) or None,
                        'time_since_last_cast': float (seconds) or None,
                        'success_rate': float (percentage)
                    },
                    ...
                }
        """
        if not hasattr(self, "skill_stats_tree"):
            return

        # Clear existing rows
        for item in self.skill_stats_tree.get_children():
            self.skill_stats_tree.delete(item)

        if not stats_dict:
            self._show_skill_stats_placeholder()
            return

        # Populate with current stats
        for skill_name, data in stats_dict.items():
            cast_count = data.get("cast_count", 0)
            time_since = data.get("time_since_last_cast")
            success_rate = data.get("success_rate", 0.0)

            # Format last cast time
            if time_since is None:
                last_cast_str = "Never"
            else:
                last_cast_str = self._t("time_ago_format").format(time=time_since)

            # Format cooldown status (simplified - just show "Ready" for now)
            # TODO: Integrate with actual skill cooldown data from skills.json
            cooldown_str = self._t("cooldown_ready")

            # Format success rate
            success_str = f"{success_rate:.1f}%"

            # Determine color tag based on success rate
            if success_rate >= 90:
                tag = "excellent"
            elif success_rate >= 70:
                tag = "good"
            else:
                tag = "poor"

            # Insert row
            self.skill_stats_tree.insert(
                "",
                "end",
                values=(
                    skill_name,
                    cast_count,
                    last_cast_str,
                    cooldown_str,
                    success_str,
                ),
                tags=(tag,),
            )

    def _show_skill_stats_placeholder(self):
        """Show a single greyed-out row when no skill casts have been recorded yet."""
        if not hasattr(self, "skill_stats_tree"):
            return
        self.skill_stats_tree.insert(
            "",
            "end",
            values=(self._t("skill_stats_empty"), "", "", "", ""),
            tags=("placeholder",),
        )

    def _on_monster_toggle(self, event=None):
        """Toggle monster enabled state on double-click.

        Sprint 22 Patch 2: Support both normal and training lists.
        """
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Determine which list we're working with
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Toggle in training_monster_list
            if idx < len(self.training_monster_list):
                self.training_monster_list[idx]["enabled"] = (
                    not self.training_monster_list[idx]["enabled"]
                )
        else:
            # Toggle in monster_rotation_list
            if idx < len(self.monster_rotation_list):
                self.monster_rotation_list[idx]["enabled"] = (
                    not self.monster_rotation_list[idx]["enabled"]
                )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx)

    def _on_monster_list_select(self, event=None):
        """Handle monster list selection for preview."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(self.monster_rotation_list):
            monster = self.monster_rotation_list[idx]
            # Optional: Show monster template preview or stats
            pass

    def _show_monster_context_menu(self, event):
        """Sprint 22 Patch 2: Show context menu on right-click.

        Displays menu at mouse position only if an item is selected.
        """
        # Check if there's a selection at the click position
        try:
            self.monster_rotation_listbox.selection_clear(0, tk.END)
            index = self.monster_rotation_listbox.nearest(event.y)
            self.monster_rotation_listbox.selection_set(index)
            self.monster_rotation_listbox.activate(index)

            # Show context menu at mouse position
            self.monster_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Release the grab
            self.monster_context_menu.grab_release()

    def _on_monster_delete_from_list(self, event=None):
        """Sprint 22 Patch 2: Delete selected monster from rotation list.

        Delete key removes item from current list (normal or training).
        If training_monster_list becomes empty, auto-switch to normal mode.
        """
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Determine which list we're working with
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Delete from training_monster_list
            if idx < len(self.training_monster_list):
                monster_name = self.training_monster_list[idx]["name"]

                # Confirm deletion
                confirm_en = f"Remove '{monster_name}' from training list?"
                confirm_vi = f"Xóa '{monster_name}' khỏi danh sách luyện tập?"
                confirm_msg = confirm_vi if self.lang == "vi" else confirm_en

                if not messagebox.askyesno(self._t("confirm_title"), confirm_msg):
                    return

                del self.training_monster_list[idx]

                # If training list is now empty, auto-switch to normal mode
                if len(self.training_monster_list) == 0:
                    hint_en = "💡 Training list cleared. Switched back to normal monster list."
                    hint_vi = "💡 Đã xóa hết cọc gỗ. Chuyển về danh sách quái thường."
                    messagebox.showinfo(
                        self._t("info_title"), hint_vi if self.lang == "vi" else hint_en
                    )
        else:
            # Delete from monster_rotation_list
            if idx < len(self.monster_rotation_list):
                monster_name = self.monster_rotation_list[idx]["name"]

                confirm_en = f"Remove '{monster_name}' from rotation list?"
                confirm_vi = f"Xóa '{monster_name}' khỏi danh sách săn?"
                confirm_msg = confirm_vi if self.lang == "vi" else confirm_en

                if not messagebox.askyesno(self._t("confirm_title"), confirm_msg):
                    return

                del self.monster_rotation_list[idx]

        self._refresh_monster_rotation_list()

        # Select next item if available
        if idx < self.monster_rotation_listbox.size():
            self.monster_rotation_listbox.selection_set(idx)
        elif self.monster_rotation_listbox.size() > 0:
            self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_up(self):
        """Move selected monster up in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        # Swap with previous
        self.monster_rotation_list[idx], self.monster_rotation_list[idx - 1] = (
            self.monster_rotation_list[idx - 1],
            self.monster_rotation_list[idx],
        )

        # Update priorities if in priority mode
        if self.hunt_cfg.get("rotation_mode") == "priority":
            (
                self.monster_rotation_list[idx]["priority"],
                self.monster_rotation_list[idx - 1]["priority"],
            ) = (
                self.monster_rotation_list[idx - 1]["priority"],
                self.monster_rotation_list[idx]["priority"],
            )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_down(self):
        """Move selected monster down in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] >= len(self.monster_rotation_list) - 1:
            return

        idx = selection[0]
        # Swap with next
        self.monster_rotation_list[idx], self.monster_rotation_list[idx + 1] = (
            self.monster_rotation_list[idx + 1],
            self.monster_rotation_list[idx],
        )

        # Update priorities if in priority mode
        if self.hunt_cfg.get("rotation_mode") == "priority":
            (
                self.monster_rotation_list[idx]["priority"],
                self.monster_rotation_list[idx + 1]["priority"],
            ) = (
                self.monster_rotation_list[idx + 1]["priority"],
                self.monster_rotation_list[idx]["priority"],
            )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx + 1)

    def _on_monster_add_smart(self):
        """Smart add monster with autocomplete and fuzzy matching hints."""
        dialog = tk.Toplevel(self)
        dialog.title(self._t("monster_add_title"))
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        container = tk.Frame(dialog, padx=16, pady=16)
        container.pack(fill="both", expand=True)

        # Title + hint
        title_label = tk.Label(
            container,
            text=self._t("monster_add_instruction"),
            font=("Arial", 10, "bold"),
        )
        title_label.pack(anchor="w", pady=(0, 8))

        hint_text = self._t("monster_add_hint")
        hint_label = tk.Label(
            container,
            text=hint_text,
            fg="#666",
            font=("Arial", 8),
            wraplength=450,
            justify="left",
        )
        hint_label.pack(anchor="w", pady=(0, 12))

        # Search entry with real-time suggestions
        search_frame = tk.Frame(container)
        search_frame.pack(fill="x", pady=(0, 8))

        tk.Label(search_frame, text=self._t("monster_name")).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=(8, 0), fill="x", expand=True)
        search_entry.focus_set()

        # Suggestion listbox
        suggest_frame = tk.LabelFrame(
            container, text=self._t("monster_suggestions"), padx=8, pady=8
        )
        suggest_frame.pack(fill="both", expand=True, pady=(0, 8))

        suggest_listbox = tk.Listbox(suggest_frame, height=10, exportselection=False)
        suggest_listbox.pack(side="left", fill="both", expand=True)

        suggest_scroll = tk.Scrollbar(
            suggest_frame, orient="vertical", command=suggest_listbox.yview
        )
        suggest_scroll.pack(side="right", fill="y")
        suggest_listbox.config(yscrollcommand=suggest_scroll.set)

        # Match info label
        match_info_var = tk.StringVar(value="")
        match_info_label = tk.Label(
            container,
            textvariable=match_info_var,
            fg="#2196F3",
            font=("Arial", 8),
            wraplength=450,
            justify="left",
        )
        match_info_label.pack(fill="x", pady=(0, 8))

        # Populate initial suggestions (filtered by training mode if active)
        def update_suggestions(*args):
            """Update suggestions based on search text with fuzzy matching."""
            import re

            search_text = search_var.get().strip()

            suggest_listbox.delete(0, tk.END)
            match_info_var.set("")

            # Sprint 22 Patch 2: Auto-detect training mode based on training_monster_list
            # Check if training_monster_list exists and has items
            has_training_list = (
                hasattr(self, "training_monster_list")
                and len(self.training_monster_list) > 0
            )
            is_training_mode = (
                has_training_list  # Auto-enable if training list has items
            )

            available_monsters = self.monsters

            if is_training_mode:
                # Training mode: Only show training dummies
                available_monsters = [
                    m for m in self.monsters if m.get("training_mode", False)
                ]
                if not available_monsters:
                    # Sprint 22 Patch 2: Only show warning if training_monster_list is EMPTY
                    # If user already added training dummies to training_monster_list, don't show warning
                    if not has_training_list:
                        debug_msg = f"⚠️ {self._t('no_training_dummies')}"
                        if self.monsters:
                            debug_msg += (
                                f"\n📚 Library has {len(self.monsters)} monsters total"
                            )
                            training_count = sum(
                                1
                                for m in self.monsters
                                if m.get("training_mode", False)
                            )
                            debug_msg += f"\n🎯 Training dummies: {training_count}"
                        match_info_var.set(debug_msg)
                    return

            if not search_text:
                # Show all available monsters (filtered or not)
                for monster in available_monsters:
                    suggest_listbox.insert(tk.END, monster["name"])
                if is_training_mode:
                    match_info_var.set(
                        f"🎯 {self._t('training_dummy_filter')} | {len(available_monsters)} dummy"
                    )
                else:
                    match_info_var.set(
                        f"💡 {self._t('monster_showing_all').format(count=len(available_monsters))}"
                    )
                return

            # Fuzzy search (on filtered list)
            search_clean = re.sub(r"[^a-z0-9\s]", "", search_text.lower()).strip()
            matches = []

            for monster in available_monsters:
                name = monster["name"]
                name_clean = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()

                # Score matches: exact > starts with > contains
                if search_clean == name_clean:
                    matches.append((name, 100))  # Exact match
                elif name_clean.startswith(search_clean):
                    matches.append((name, 80))  # Starts with
                elif search_clean in name_clean:
                    matches.append((name, 60))  # Contains
                elif any(word.startswith(search_clean) for word in name_clean.split()):
                    matches.append((name, 40))  # Word starts with

            # Sort by score (descending)
            matches.sort(key=lambda x: x[1], reverse=True)

            # Display matches
            for name, score in matches:
                suggest_listbox.insert(tk.END, name)

            # Update match info
            if matches:
                match_info_var.set(
                    f"✓ {self._t('monster_found_matches').format(count=len(matches))} | "
                    + self._t("monster_fuzzy_hint")
                )
            else:
                match_info_var.set(
                    f"⚠ {self._t('monster_no_matches')} | "
                    + self._t("monster_try_hint")
                )

        search_var.trace_add("write", update_suggestions)
        update_suggestions()  # Initial population

        # Double-click or Enter to select
        def on_select(event=None):
            selection = suggest_listbox.curselection()
            if not selection:
                return

            monster_name = suggest_listbox.get(selection[0])

            # Sprint 22 Patch 2: Check duplicate based on auto-detected training mode
            has_training_list = (
                hasattr(self, "training_monster_list")
                and len(self.training_monster_list) > 0
            )
            is_training_mode = has_training_list

            # Find monster in library to get training_mode flag
            monster_data = next(
                (m for m in self.monsters if m["name"] == monster_name), None
            )
            training_flag = (
                monster_data.get("training_mode", False) if monster_data else False
            )

            # Determine which list to check and add to
            if training_flag:
                # Training dummy: add to training_monster_list
                check_list = self.training_monster_list
                target_list = "training"
            else:
                # Normal monster: add to monster_rotation_list
                check_list = self.monster_rotation_list
                target_list = "normal"

            if any(m["name"] == monster_name for m in check_list):
                messagebox.showinfo(
                    self._t("info_title"),
                    self._t("monster_already_in_list").format(name=monster_name),
                    parent=dialog,
                )
                return

            # Add to appropriate list
            new_priority = len(check_list) + 1

            if target_list == "training":
                self.training_monster_list.append(
                    {
                        "name": monster_name,
                        "priority": new_priority,
                        "enabled": True,
                        "training_mode": True,
                    }
                )
                # Auto-enable training mode
                if hasattr(self, "training_mode_var"):
                    self.training_mode_var.set(True)
            else:
                self.monster_rotation_list.append(
                    {
                        "name": monster_name,
                        "priority": new_priority,
                        "enabled": True,
                        "training_mode": False,
                    }
                )

            self._refresh_monster_rotation_list()
            dialog.destroy()

        suggest_listbox.bind("<Double-Button-1>", on_select)
        search_entry.bind("<Return>", on_select)

        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text=self._t("add_button"),
            command=on_select,
            font=("Arial", 9, "bold"),
            fg="#4CAF50",
        ).pack(side="left")
        tk.Button(
            btn_frame, text=self._t("cancel_button"), command=dialog.destroy
        ).pack(side="left", padx=(8, 0))

    def on_skill_slot_changed(self, _evt=None):
        self._update_attack_keys_from_slots()
        try:
            self.state_controller._refresh_slot_key_labels()
        except Exception:
            pass
        try:
            self.state_controller._validate_slot_key_duplicates()
        except Exception:
            pass

    def _update_monster_frame_title(self, is_training_mode: bool):
        """Sprint 22 Patch 2: Update frame title to indicate current mode.

        Args:
            is_training_mode: True if showing training_monster_list
        """
        if not hasattr(self, "monster_frame"):
            return

        if is_training_mode:
            # Training mode: Show with special indicator
            title_en = "🎯 Training Dummies (Practice Mode)"
            title_vi = "🎯 Cọc Gỗ Luyện Tập (Chế độ luyện skill)"
            title = title_vi if self.lang == "vi" else title_en

            # Change listbox background to indicate training mode
            if hasattr(self, "monster_rotation_listbox"):
                self.monster_rotation_listbox.config(bg="#FFF8E1")  # Light amber/yellow

            # Show hint for switching back to normal mode
            if hasattr(self, "training_mode_hint_var"):
                hint_en = "💡 To switch back to normal monsters: Delete all training dummies (select + Del key)"
                hint_vi = "💡 Để chuyển về danh sách quái thường: Xóa hết cọc gỗ (chọn + phím Del)"
                self.training_mode_hint_var.set(
                    hint_vi if self.lang == "vi" else hint_en
                )
        else:
            # Normal mode: Regular monsters
            title = self._t("hunt_monsters")

            # Reset listbox background to default
            if hasattr(self, "monster_rotation_listbox"):
                self.monster_rotation_listbox.config(bg="white")

            # Clear hint
            if hasattr(self, "training_mode_hint_var"):
                self.training_mode_hint_var.set("")

        self.monster_frame.config(text=title)

    def _update_monster_status(self):
        """Update current monster hunting status display.

        Sprint 22 Patch 2: Show different status for training mode.
        """
        if not hasattr(self, "monster_status_var"):
            return

        # Check which mode we're in
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Training mode: Show training list status
            enabled = [m for m in self.training_monster_list if m["enabled"]]
            if not enabled:
                status_en = "🎯 No training dummy selected"
                status_vi = "🎯 Chưa chọn cọc gỗ nào"
                self.monster_status_var.set(
                    status_vi if self.lang == "vi" else status_en
                )
                return

            # Show training mode status
            count = len(enabled)
            status_en = (
                f"🎯 Training Mode: {count} dummy"
                if count == 1
                else f"🎯 Training Mode: {count} dummies"
            )
            status_vi = f"🎯 Chế độ luyện tập: {count} cọc gỗ"
            self.monster_status_var.set(status_vi if self.lang == "vi" else status_en)
        else:
            # Normal mode: Show normal monster status
            enabled = [m for m in self.monster_rotation_list if m["enabled"]]
            if not enabled:
                self.monster_status_var.set(self._t("monster_none_selected"))
                return

            mode = self.hunt_cfg.get("rotation_mode", "sequence")
            current_idx = self.hunt_cfg.get("current_monster_index", 0)

            if mode == "sequence":
                if current_idx < len(enabled):
                    current = enabled[current_idx]
                    self.monster_status_var.set(
                        f"Current: {current['name']} | Sequence: {current_idx+1}/{len(enabled)}"
                    )
                else:
                    self.monster_status_var.set(f"Sequence: {len(enabled)} monsters")
            else:  # priority
                sorted_monsters = sorted(enabled, key=lambda m: m["priority"])
                current = sorted_monsters[0]
                self.monster_status_var.set(
                    f"Priority: {current['name']} (P{current['priority']}) | {len(enabled)} total"
                )

    def _refresh_monster_select_options(self, select_name: Optional[str] = None):
        if select_name is not None:
            self.monster_selected_name = select_name
        names = [monster["name"] for monster in self.monsters]
        combo = getattr(self, "monster_select_combo", None)
        select_var = getattr(self, "monster_select_var", None)
        if combo is not None:
            combo["values"] = names
            target_name = self.monster_selected_name or (
                select_name if select_name in names else None
            )
            current = select_var.get() if select_var is not None else ""
            if select_var is not None:
                if target_name and target_name in names:
                    select_var.set(target_name)
                elif current not in names:
                    select_var.set(names[0] if names else "")
        if select_var is not None:
            self.on_monster_select_change()

    def on_monster_select_change(self, _evt=None):
        """Auto-apply monster config when selected from Hunt tab dropdown."""
        select_var = getattr(self, "monster_select_var", None)
        if select_var is None:
            return
        value = select_var.get()
        if value is None:
            return
        name = value.strip()
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster["name"] == name:
                idx = i
                break
        self.monster_selected_index = idx if idx is not None else None
        self.monster_selected_name = name if idx is not None else None

        if idx is not None:
            monster = self.monsters[idx]
            self.state_controller._update_monster_estimate_label(monster)
            # Auto-apply monster config (templates, window_bounds, timing recommendations)
            self.state_controller._apply_monster_to_hunt_quick(monster)
        elif hasattr(self, "monster_estimate_var"):
            self.monster_estimate_var.set("")

    def on_monster_apply_from_select(self):
        if not hasattr(self, "monster_select_var"):
            return
        name = self.monster_select_var.get().strip()
        if not name:
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster["name"] == name:
                idx = i
                break
        if idx is None:
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        self.monster_selected_index = idx
        self.monster_selected_name = name
        self.state_controller._update_monster_estimate_label(self.monsters[idx])
        self.on_monster_use_for_hunt()

    def _refresh_skill_slots_options(self):
        if not hasattr(self, "skill_slot_boxes"):
            return
        names = []
        for skill in self.skills:
            if skill["name"] not in names:
                names.append(skill["name"])
        for saved in getattr(self, "skill_slot_saved_names", []):
            if saved and saved not in names:
                names.append(saved)
        values = [""] + names
        for cmb in self.skill_slot_boxes:
            cmb["values"] = values
        # Also refresh key labels next to each slot
        try:
            self.state_controller._refresh_slot_key_labels()
        except Exception:
            pass

    def _clear_skill_slot(self, var):
        var.set("")
        self._update_attack_keys_from_slots()

    def _update_attack_keys_from_slots(self):
        # attack_keys removed: update saved slot names and refresh options
        self.skill_slot_saved_names = [
            v.get().strip() for v in self.skill_slot_vars if v.get().strip()
        ]
        self._refresh_skill_slots_options()

    def _collect_skill_slots(self):
        if not self.skill_slot_vars:
            self.skill_slot_saved_names = []
            return []
        mapping = {skill["name"]: skill for skill in self.skills}
        slots = []
        saved_names = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            saved_names.append(name)
            slots.append(
                {
                    "name": skill["name"],
                    "key": skill["key"],
                    "type": skill.get("type", "attack"),
                    "cooldown": float(skill.get("cooldown", 0.0)),
                    "cast_time": float(skill.get("cast_time", 0.0)),
                    "image": skill.get("image", ""),
                }
            )
        self.skill_slot_saved_names = saved_names
        return slots

    def on_monster_use_for_hunt(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(
            self.monsters
        ):
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        monster = self.monsters[self.monster_selected_index]

        from lib.features.hunt.config_validator import normalize_window_bounds_value
        from lib.features.hunt.window_selection_service import WindowSelectionService

        # Apply window_bounds
        bounds = normalize_window_bounds_value(monster.get("window_bounds"))
        self.current_window_bounds = bounds
        WindowSelectionService.update_bounds(self.hunt_cfg, bounds)
        self.state_controller._update_window_bounds_display()

        # Apply templates[] array to config
        templates = _sanitize_templates(monster.get("templates"))
        if templates:
            self.hunt_cfg["templates"] = templates
            # Also set legacy template_path to first template for backward compat
            try:
                first_path = templates[0].get("path")
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg["template_path"] = first_path
            except Exception:
                pass
        elif monster.get("template"):
            # Fallback to old single template field
            self.template_var.set(monster["template"])
            self.hunt_cfg["template_path"] = monster["template"]
            self.hunt_cfg["templates"] = []

        try:
            stats = self.state_controller._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return
        kill_time = stats["kill_time"]
        attack_min, lost_timeout = self.state_controller._recommend_attack_settings(
            stats
        )
        self.attack_duration_var.set(f"{attack_min:.2f}")
        self.lost_timeout_var.set(f"{lost_timeout:.2f}")
        base = self._t("monster_estimate_result").format(
            time=kill_time, dps=stats["dps"]
        )
        detail = self._t("monster_estimate_detail").format(
            base=base, attack=attack_min, lost=lost_timeout
        )
        self.monster_estimate_var.set(detail)
        self.hunt_status.set(self._t("monster_applied"))

    # -----------------
    # Skill library helpers
    # -----------------
    def _update_rotation_mode_description(self):
        """Update rotation mode description."""
        if not hasattr(self, "rotation_desc_var"):
            return

        mode = self.rotation_mode_var.get()
        if mode == "sequence":
            self.rotation_desc_var.set("Hunt monsters in order, cycle through list")
        elif mode == "priority":
            self.rotation_desc_var.set("Always hunt highest priority (lowest number)")

    def _update_training_mode_buttons(self):
        """Update monster control buttons based on training mode state.

        Training Mode ON:
        - Add button: Shows finish.ico if dummy set, else add.ico with training tooltip
        - Add button: Disabled if training dummy already in list
        - Up/Down buttons: Disabled (no rotation needed)

        Training Mode OFF:
        - Add button: Shows add.ico with normal tooltip
        - Add button: Always enabled
        - Up/Down buttons: Enabled
        """
        if not hasattr(self, "btn_add_monster"):
            return

        is_training = self.training_mode_var.get()
        has_training_dummy = any(
            m.get("training_mode", False) for m in self.monster_rotation_list
        )

        if is_training:
            # Training mode: Update add button
            if has_training_dummy:
                # Dummy already set - show accept icon and disable
                try:
                    # Use size=16 to match compact button
                    accept_icon = self._icon("accept", "✓", size=16)
                    if isinstance(accept_icon, str):
                        self.btn_add_monster.config(text=accept_icon, state="disabled")
                    else:
                        self.btn_add_monster.config(
                            image=accept_icon, text="", state="disabled"
                        )
                except Exception:
                    self.btn_add_monster.config(text="✓", state="disabled")

                # Update tooltip for locked state
                tooltip_text = self._t("tooltip_add_monster_locked")
                tooltip = getattr(self.btn_add_monster, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(self.btn_add_monster, "_tooltip")
                    except Exception:
                        pass
                self._create_tooltip(self.btn_add_monster, tooltip_text)
            else:
                # No dummy yet - show add icon and enable
                try:
                    # Use size=16 to match compact button
                    add_icon = self._icon("add", "➕", size=16)
                    if isinstance(add_icon, str):
                        self.btn_add_monster.config(text=add_icon, state="normal")
                    else:
                        self.btn_add_monster.config(
                            image=add_icon, text="", state="normal"
                        )
                except Exception:
                    self.btn_add_monster.config(text="➕", state="normal")

                # Update tooltip for training helper
                tooltip_text = self._t("tooltip_add_monster_training")
                tooltip = getattr(self.btn_add_monster, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(self.btn_add_monster, "_tooltip")
                    except Exception:
                        pass
                self._create_tooltip(self.btn_add_monster, tooltip_text)

            # Disable priority reorder buttons with locked icon (white on gray)
            # Use size=16 to match SMALL buttons (36px)
            try:
                locked_icon = self._icon("locked", "🔒", size=16, color="#FFFFFF")
                for btn in [self.btn_move_up, self.btn_move_down]:
                    # IMPORTANT: Keep original bg colors when disabled
                    original_bg = (
                        UI.BTN_NEUTRAL_BG
                        if btn == self.btn_move_up
                        else UI.BTN_NEUTRAL_BG
                    )
                    btn.config(state="disabled", bg=original_bg)
                    if isinstance(locked_icon, str):
                        btn.config(text=locked_icon)
                    else:
                        btn.config(image=locked_icon, text="")
            except Exception:
                self.btn_move_up.config(
                    state="disabled", text="🔒", bg=UI.BTN_NEUTRAL_BG
                )
                self.btn_move_down.config(
                    state="disabled", text="🔒", bg=UI.BTN_NEUTRAL_BG
                )

            # Update tooltips for disabled buttons
            for btn in [self.btn_move_up, self.btn_move_down]:
                # Safely destroy any existing tooltip then create a new one
                try:
                    self._destroy_widget_tooltip(btn)
                except Exception:
                    pass
                self._create_tooltip(btn, self._t("tooltip_reorder_locked"))
        else:
            # Normal mode: Restore defaults
            try:
                # Use size=16 to match compact button
                add_icon = self._icon("add", "➕", size=16)
                if isinstance(add_icon, str):
                    self.btn_add_monster.config(text=add_icon, state="normal")
                else:
                    self.btn_add_monster.config(image=add_icon, text="", state="normal")
            except Exception:
                self.btn_add_monster.config(text="➕", state="normal")

            # Restore normal tooltip
            try:
                self._destroy_widget_tooltip(self.btn_add_monster)
            except Exception:
                pass
            self._create_tooltip(
                self.btn_add_monster, self._t("tooltip_add_monster_normal")
            )

            # Enable priority reorder buttons with original icons and colors (both blue for consistency)
            try:
                # Use size=16 to match SMALL buttons
                up_icon = self._icon("up", "↑", size=16)
                down_icon = self._icon("down", "↓", size=16)

                if isinstance(up_icon, str):
                    self.btn_move_up.config(
                        state="normal",
                        text=up_icon,
                        bg=UI.BTN_INFO_BG,  # Blue for consistency
                        fg=UI.BTN_INFO_FG,
                    )
                else:
                    self.btn_move_up.config(
                        state="normal",
                        image=up_icon,
                        text="",
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG,
                    )

                if isinstance(down_icon, str):
                    self.btn_move_down.config(
                        state="normal",
                        text=down_icon,
                        bg=UI.BTN_INFO_BG,  # Blue for consistency
                        fg=UI.BTN_INFO_FG,
                    )
                else:
                    self.btn_move_down.config(
                        state="normal",
                        image=down_icon,
                        text="",
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG,
                    )
            except Exception:
                self.btn_move_up.config(
                    state="normal",
                    text="↑",
                    bg=UI.BTN_INFO_BG,  # Blue for consistency
                    fg=UI.BTN_INFO_FG,
                )
                self.btn_move_down.config(
                    state="normal",
                    text="↓",
                    bg=UI.BTN_INFO_BG,  # Blue for consistency
                    fg=UI.BTN_INFO_FG,
                )

            # Restore normal tooltips
            try:
                self._destroy_widget_tooltip(self.btn_move_up)
            except Exception:
                pass
            self._create_tooltip(self.btn_move_up, self._t("tooltip_move_up"))

            try:
                self._destroy_widget_tooltip(self.btn_move_down)
            except Exception:
                pass
            self._create_tooltip(self.btn_move_down, self._t("tooltip_move_down"))

    def on_global_apply(self):
        """Global apply handler - saves all settings across all tabs.

        NOTE: Save file only ONCE to avoid duplicate writes and preserve field order.
        """
        try:
            # 1. Apply Setup tab settings (updates hunt_cfg in-place, but don't save yet)
            self._apply_setup_settings(save_to_file=False)

            # 2. Update hunt config from Hunt tab UI (in-place update)
            cfg = self.state_controller._hunt_from_ui()

            # 2.5. Update global hotkeys from Setup tab UI
            if hasattr(self, "global_hotkey_enabled_var"):
                enabled = self.global_hotkey_enabled_var.get()
                start_key = self.global_hotkey_start_var.get()
                stop_key = self.global_hotkey_stop_var.get()
                wizard_key = self.global_hotkey_wizard_var.get()  # NEW
                library_key = self.global_hotkey_library_var.get()  # NEW

                # Validate: all hotkeys must be unique
                vision_key = self.global_hotkey_vision_var.get()
                monster_key = self.global_hotkey_monster_var.get()
                all_keys = [
                    start_key,
                    stop_key,
                    wizard_key,
                    library_key,
                    vision_key,
                    monster_key,
                ]
                if len(all_keys) != len(set(all_keys)):
                    messagebox.showerror(
                        self._t("error_title"),
                        (
                            "All hotkeys must be different!"
                            if self.lang == "en"
                            else "Tất cả phím tắt phải khác nhau!"
                        ),
                    )
                    return

                # Update config
                cfg["global_hotkeys"] = {
                    "enabled": enabled,
                    "start_key": start_key,
                    "stop_key": stop_key,
                    "setup_wizard_key": wizard_key,
                    "library_manager_key": library_key,
                    "vision_wizard_key": vision_key,
                    "monster_editor_key": monster_key,
                }

                # Re-register hotkeys with new settings
                self.hunt_cfg = cfg  # Update instance config first
                self.hotkey_controller.unregister_all()
                self.hotkey_controller.register_all()

            # 3. Save to file ONCE (preserves insertion order in Python 3.7+)
            save_hunt_config(cfg)
            self.hunt_cfg = cfg

            # 4. Clear unsaved changes indicator
            self.state_controller._clear_unsaved_changes()

            # 5. Update status
            self.hunt_status.set(self._t("all_saved"))

            # 6. Show success message
            messagebox.showinfo(
                self._t("success_title"), self._t("settings_applied_message")
            )
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), f"Failed to apply settings: {e}"
            )

    def _reload_setup_advanced_settings(self):
        """Reload Advanced Settings values in Setup tab after timing changes."""
        # Update variables with new values from hunt_cfg
        if hasattr(self, "setup_search_interval_var"):
            self.setup_search_interval_var.set(
                f"{self.hunt_cfg.get('search_interval', 0.25):.2f}"
            )
        if hasattr(self, "setup_attack_interval_var"):
            self.setup_attack_interval_var.set(
                f"{self.hunt_cfg.get('attack_interval', 0.15):.2f}"
            )
        if hasattr(self, "setup_lost_timeout_var"):
            self.setup_lost_timeout_var.set(
                f"{self.hunt_cfg.get('lost_timeout_sec', 0.5):.2f}"
            )
        if hasattr(self, "setup_attack_duration_var"):
            self.setup_attack_duration_var.set(
                f"{self.hunt_cfg.get('attack_min_duration_sec', 5.0):.2f}"
            )

    def _populate_hunt_ui_from_config(self):
        """Populate Hunt tab UI elements from hunt_config.json data."""
        # 1. Window selection
        window_title = self.hunt_cfg.get("window_title", "").strip()
        window_pid = self.hunt_cfg.get("window_pid")
        window_hwnd = self.hunt_cfg.get("window_hwnd")

        if window_title:
            # If we have PID/HWND, create hunt_selected object
            if window_pid and window_hwnd:
                self.hunt_selected = {
                    "title": window_title,
                    "pid": window_pid,
                    "hwnd": window_hwnd,
                    "proc": None,  # Process name not saved in config
                }

                # Populate combobox with saved window (show only window title without PID)
                if hasattr(self, "win_combo"):
                    self.win_combo["values"] = [window_title]
                    self.win_combo.current(0)
                    self.win_items = [self.hunt_selected]

        # 2. Monster template (if exists)
        monster_name = self.hunt_cfg.get("monster_selected_name", "").strip()
        template_path = self.hunt_cfg.get("template_path", "").strip()

        if monster_name:
            # Update monster name display (assuming you have a monster_name variable)
            # This will be shown in UI when monster selection is implemented
            pass

        # 3. Skill slots
        skill_slots = self.hunt_cfg.get("skill_slots", [])
        if skill_slots:
            # Update skill UI (assuming skill slot UI variables exist)
            # This will populate skill comboboxes when skill UI is ready
            pass

        # 4. Update any other UI elements that depend on config
        # (Add more as needed based on your UI structure)
        pass

    def _update_unsaved_indicator(self):
        """Update unsaved changes indicator UI."""
        if not hasattr(self, "unsaved_indicator_label"):
            return

        if self.has_unsaved_changes:
            self.unsaved_indicator_label.config(
                text=f"● {self._t('unsaved_indicator')}", fg="#FF9800"  # Orange color
            )
        else:
            self.unsaved_indicator_label.config(
                text=f"✓ {self._t('all_saved')}", fg="#4CAF50"  # Green color
            )

    def on_close(self):
        self.lifecycle_controller.on_close()

    def destroy(self):
        self.lifecycle_controller.cleanup_before_destroy()
        super().destroy()

    def _icon(
        self, name: str, fallback: str, size: int = 16, color: Optional[str] = None
    ):
        """Fetch an icon image from icon_helper with caching.

        Returns a PhotoImage (when available) or fallback string (emoji) otherwise.
        Keep a reference on self to avoid Tk image garbage collection.

        Args:
            name: Icon name (e.g., 'add', 'locked')
            fallback: Emoji fallback if icon not found
            size: Icon size in pixels
            color: Hex color to tint icon (e.g., '#FFFFFF' for white on gray background)
        """
        try:
            if not hasattr(self, "_icon_cache"):
                self._icon_cache = {}
            key = f"{name}_{size}_{color or 'default'}"
            if key in self._icon_cache:
                return self._icon_cache[key]
            helper = getattr(self, "icon_helper", None)
            if helper is not None:
                try:
                    img = helper.get_icon(
                        name, fallback=fallback, size=size, color=color
                    )
                except Exception:
                    img = fallback
            else:
                img = fallback
            self._icon_cache[key] = img
            return img
        except Exception:
            return fallback

    # -----------------
    # Helper Methods
    # -----------------
    def _create_icon_button(
        self,
        parent,
        icon_emoji,
        command,
        style="compact",
        bg_color=None,
        hover_color=None,
        **kwargs,
    ):
        """Create a standardized icon button following UIStyle guidelines.

        **DEPRECATED**: This method now uses the new icon_button component internally.
        For new code, prefer using `from ui.components import create_icon_button` directly.

        Args:
            parent: Parent widget
            icon_emoji: Emoji text for button (e.g., '➕', '↑', '↓') - used as fallback
            command: Button command callback
            style: Size style - 'compact', 'small', 'medium', or 'large'
            bg_color: Background color (uses BTN_ACCENT_BG if not specified)
            hover_color: Hover color (uses BTN_ACCENT_HOVER if not specified)
            **kwargs: Additional button configuration options

        Returns:
            tk.Button: Configured button widget
        """
        # If component available, use it for better icon quality
        if _HAS_ICON_COMPONENT and _create_icon_btn_component is not None:
            # Map emoji to icon names
            emoji_to_icon = {
                "➕": "add",
                "🗑️": "delete",
                "💾": "save",
                "✖": "cancel",
                "🔄": "refresh",
                "↑": "up",
                "↓": "down",
                "📁": "folder",
                "⚙️": "settings",
                "🔍": "search",
            }

            # Map bg_color to button_type
            button_type_map = {
                UI.BTN_PRIMARY_BG: "green_light",
                UI.BTN_ACCENT_BG: "green_light",
                UI.BTN_DANGER_BG: "red",
                UI.BTN_INFO_BG: "blue",
                UI.BTN_NEUTRAL_BG: "refresh",
            }

            icon_name = emoji_to_icon.get(icon_emoji, "add")
            button_type = button_type_map.get(
                bg_color or UI.BTN_ACCENT_BG, "green_light"
            )

            # Map style to variant
            variant_map = {
                "compact": "compact",
                "small": "small",
                "medium": "medium",
                "large": "large",
            }
            variant = variant_map.get(style, "compact")

            return _create_icon_btn_component(
                parent=parent,
                icon_name=icon_name,
                icon_fallback=icon_emoji,
                command=command,
                button_type=button_type,
                variant=variant,
                icon_size=16,
                **kwargs,
            )

        # Fallback to old emoji-only method if component not available
        style_configs = {
            "compact": {
                "width": 0,
                "height": 0,
                "padx": UI.BTN_ICON_PADDING_COMPACT,
                "pady": UI.BTN_ICON_PADDING_COMPACT,
            },
            "small": {
                "width": UI.BTN_ICON_WIDTH_SMALL,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_SMALL,
                "pady": UI.BTN_ICON_PADDING_SMALL,
            },
            "medium": {
                "width": UI.BTN_ICON_WIDTH_MEDIUM,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_MEDIUM,
                "pady": UI.BTN_ICON_PADDING_MEDIUM,
            },
            "large": {
                "width": UI.BTN_ICON_WIDTH_LARGE,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_LARGE,
                "pady": UI.BTN_ICON_PADDING_LARGE,
            },
        }

        config = style_configs.get(style, style_configs["compact"])

        if bg_color is None:
            bg_color = UI.BTN_ACCENT_BG
        if hover_color is None:
            hover_color = UI.BTN_ACCENT_HOVER

        color_map = {
            UI.BTN_PRIMARY_BG: UI.BTN_PRIMARY_FG,
            UI.BTN_ACCENT_BG: UI.BTN_ACCENT_FG,
            UI.BTN_INFO_BG: UI.BTN_INFO_FG,
            UI.BTN_NEUTRAL_BG: UI.BTN_NEUTRAL_FG,
            UI.BTN_DANGER_BG: UI.BTN_DANGER_FG,
        }
        fg_color = color_map.get(bg_color, UI.BTN_ACCENT_FG)

        button_config = {
            "text": icon_emoji,
            "command": command,
            "font": UI.FONT_BUTTON,
            "bg": bg_color,
            "fg": fg_color,
            "activebackground": hover_color,
            "activeforeground": fg_color,
            "relief": UI.BTN_RELIEF_NORMAL,
            "cursor": "hand2",
            **config,
            **kwargs,
        }

        return tk.Button(parent, **button_config)

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=3,
            )
            label.pack()
            # Store tooltip in a central map to avoid setting dynamic attributes on widgets
            try:
                if not hasattr(self, "_tooltips"):
                    self._tooltips = {}
                self._tooltips[id(widget)] = tooltip
            except Exception:
                # Last-resort: attach to widget (legacy)
                try:
                    widget._tooltip = tooltip
                except Exception:
                    pass

        def on_leave(event):
            try:
                # Prefer centralized map
                if hasattr(self, "_tooltips") and id(widget) in self._tooltips:
                    try:
                        self._tooltips[id(widget)].destroy()
                    except Exception:
                        pass
                    try:
                        del self._tooltips[id(widget)]
                    except Exception:
                        pass
                    return
                # Fallback to widget attribute
                tooltip = getattr(widget, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(widget, "_tooltip")
                    except Exception:
                        pass
            except Exception:
                pass

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _destroy_widget_tooltip(self, widget):
        """Safely destroy a tooltip for a widget (central map or widget attribute)."""
        try:
            if hasattr(self, "_tooltips") and id(widget) in self._tooltips:
                try:
                    self._tooltips[id(widget)].destroy()
                except Exception:
                    pass
                try:
                    del self._tooltips[id(widget)]
                except Exception:
                    pass
                return
            tooltip = getattr(widget, "_tooltip", None)
            if tooltip is not None:
                try:
                    tooltip.destroy()
                except Exception:
                    pass
                try:
                    delattr(widget, "_tooltip")
                except Exception:
                    pass
        except Exception:
            pass



def main():
    """Main entry point with single instance lock."""
    # Check critical dependencies (pywin32 for overlay)
    try:
        import win32gui  # Test pywin32 availability
    except ImportError:
        # Show warning but don't block - overlay will show error when toggled
        print("⚠️ WARNING: pywin32 not installed - overlay feature will not work")
        print("   Run: pip install pywin32")
        print("   Or: python scripts/check_dependencies.py --install")

    # Create single instance lock (using mutex on Windows, file lock on Unix)
    instance_lock = SingleInstanceLock("CabalAutoHunt_v1")

    # Try to acquire lock
    if not instance_lock.acquire():
        # Another instance is already running - show error in both languages
        root = tk.Tk()
        root.withdraw()  # Hide main window

        messagebox.showerror(
            "⚠️ Application Already Running | Ứng dụng đã chạy",
            "❌ CANNOT START: Another instance is already running!\n\n"
            "📌 Only ONE instance can run at a time.\n"
            "🔄 Please close the existing application first, then try again.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ KHÔNG THỂ KHỞI ĐỘNG: Ứng dụng đã đang chạy!\n\n"
            "📌 Chỉ được phép chạy 1 ứng dụng tại một thời điểm.\n"
            "🔄 Vui lòng tắt ứng dụng đang chạy trước, sau đó thử lại.",
            parent=root,
        )

        root.destroy()
        sys.exit(1)

    try:
        try:
            from database import MonsterDatabase

            MonsterDatabase().init_db()
        except Exception as e:
            print(f"[DB Init] Failed to initialize monsters.db: {e}")

        # Start application
        app = App()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()
    finally:
        # Always release lock on exit
        instance_lock.release()


if __name__ == "__main__":
    main()
