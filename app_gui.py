from ui.windows.setup_wizard import show_setup_wizard
from dialogs.monster_picker import MonsterPickerDialog
from ui.windows.hotkey_diag_dialog import show_hotkey_diagnostics_modal
from ui.controllers.app_lifecycle_controller import AppLifecycleController
from lib.ui_style import UIStyle as UI  # Global UI style constants
from lib.system.win_input import tap
from lib.system.instance_lock import SingleInstanceLock
from lib.system.hunt_logger import get_hunt_logger
from ui.controllers.hotkey_controller import HotkeyController
from lib.features.timing.calculator import (
    calculate_timing,
    format_timing_recommendation,
    get_timing_presets,
)
from lib.features.skills.skill_stats import (
    SkillStats,
)  # Sprint 22 Patch 1: Training Mode
from ui.controllers.skill_manager_controller import SkillManagerController
from lib.features.skills.skill_runtime_service import SkillRuntimeService
from lib.features.skills.skill_repo import (
    calculate_attack_speed_from_skills,
)
from lib.features.monsters.monster_repo import (
    calculate_monster_estimate,
    load_monster_library,
    save_monster_library,
)
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
from lib.features.hunt.hunt_runner import HuntRunner
from lib.features.hunt.hunt_config import (
    ConfigManager,
    _sanitize_templates,
    load_config,
    load_hunt_config,
    save_config,
    save_hunt_config,
)
from lib.features.hunt.hunt_config import CONFIG_PATH, HUNT_CONFIG_PATH
from ui.utils.overlay_controller import OverlayController
from ui.helpers.tooltip import attach_i18n_tooltip
from lib.system.bot_manager import BotManager
from lib.i18n import t as i18n_t
from lib.i18n import set_default_lang as i18n_set_lang
from lib.i18n import GLOBAL_NS as I18N_GLOBAL
from lib.features.hunt.config_validator import get_valid_hunt_area
from lib.vision.vision_engine import VisionEngine
from lib.vision.template_matcher import locate_template
from ctypes import wintypes
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import copy
import ctypes
import json
import math
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import queue
from typing import Any, Dict, List, Optional

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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


try:
    from lib.system.screen_capture import ScreenCapture
except ImportError:
    ScreenCapture = None

# Imported for its side effect: self-registers GLOBAL_TRANSLATIONS into the i18n registry.
from lib.i18n.translations import GLOBAL_TRANSLATIONS  # noqa: F401

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


# =====================================================================
# Single Instance Lock (Prevent multiple app instances)

# =====================================================================


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
        self._is_destroyed = False
        self._last_height_under_900 = False
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
        self.resizable(True, True)

        # Calculate scale factor for layout limits
        try:
            dpi_percent = self.tk.call('tk', 'scaling') * 72
            scale_factor = dpi_percent / 100.0
        except Exception:
            scale_factor = 1.0

        self.minsize(int(1220 * scale_factor), int(656 * scale_factor))

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Limit initial geometry to not cover taskbar/titlebar
        max_init_w = screen_w - 20
        max_init_h = screen_h - 80

        w = min(1920, max_init_w)
        h = min(1080, max_init_h)

        x = max((screen_w - w) // 2, 0)
        y = max((screen_h - h) // 2, 0)
        self.geometry(f"{w}x{h}+{x}+{y}")

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
        self.monster_rotation = []
        self._load_monster_rotation_list()

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
            bot_manager=self.hunt_runner.bot_manager,
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
            clear_target_ui=self.clear_target_ui,
            set_target_info=lambda txt: getattr(self, "hunt_target_info", tk.StringVar()).set(txt)
        )

        # Keyboard shortcuts (Window-focused only)
        self.bind(
            "<Control-k>", lambda e: self.skill_manager_controller.open_window()
        )  # Ctrl+K: Manage skills
        self.bind("<Alt-Key-1>", lambda e: self.switch_view('hunt'))  # Alt+1: Hunt tab
        self.bind("<Alt-Key-2>", lambda e: self.switch_view('setup'))  # Alt+2: Setup tab

        # Responsive layout bindings
        self.bind("<Configure>", self._on_window_configure)

        self.hotkey_controller.register_all()
        self.lifecycle_controller = AppLifecycleController(self)
        self.lifecycle_controller.start_lifecycle()

    # -----------------
    def _build_ui(self):
        from lib.ui_style import UIStyle as UI
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # --- UX2.1: Core Grid Construction ---
        # Isolated main container for the upcoming UI redesign
        self.main_shell = tk.Frame(self, bg=UI.BG_DEFAULT)

        # Get DPI scale factor for layout (100% = 1.0, 125% = 1.25, etc.)
        try:
            dpi_percent = self.tk.call('tk', 'scaling') * 72
            scale_factor = dpi_percent / 100.0
        except Exception:
            scale_factor = 1.0

        # Grid Configuration for main_shell (Explicit minsize & DPI Guard)
        self.main_shell.columnconfigure(0, minsize=int(260 * scale_factor), weight=0)  # Vùng C1 - Sidebar
        self.main_shell.columnconfigure(1, minsize=int(960 * scale_factor), weight=1)  # Vùng B - Workspace

        self.main_shell.rowconfigure(0, minsize=int(80 * scale_factor), weight=0)      # Vùng A - Action Bar
        self.main_shell.rowconfigure(1, minsize=int(540 * scale_factor), weight=1)     # Vùng B - Nội dung chính
        self.main_shell.rowconfigure(2, minsize=int(36 * scale_factor), weight=0)      # Vùng C2 - Logs, footer full-width

        # Vùng A: Quick Action Bar (Spans full width)
        self.shell_zone_a = tk.Frame(self.main_shell, bg=UI.BG_DEFAULT)
        self.shell_zone_a.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Vùng C1: Secondary Configuration Sidebar (Spans rows 1 and 2)
        self.shell_zone_c1 = tk.Frame(self.main_shell, bg=UI.BG_PANEL)
        self.shell_zone_c1.grid(row=1, column=0, rowspan=2, sticky="nsew")
        self.shell_zone_c1.configure(padx=16, pady=20)
        self.shell_zone_c1.grid_propagate(False)

        # Build Sidebar Navigation
        sidebar_items = [
            ("sidebar_quick_setup", lambda: self.switch_view('setup'), UI.FONT_SECTION, 'setup'),
            ("sidebar_managers", None, UI.FONT_SECTION, None),
            ("btn_monster_manager", self.monster_manager_controller.open_window, UI.FONT_LABEL, None),
            ("btn_skill_manager", self.skill_manager_controller.open_window, UI.FONT_LABEL, None),
            ("btn_library_manager", self.library_manager_controller.open_library_manager, UI.FONT_LABEL, None),
            ("sidebar_configuration", lambda: self.switch_view('setup'), UI.FONT_SECTION, 'setup'),
            ("sidebar_support", lambda: self.switch_view('help'), UI.FONT_SECTION, 'help'),
            ("tab_hunt", lambda: self.switch_view('hunt'), UI.FONT_SECTION, 'hunt'),
            ("sidebar_activity_logs", lambda: self.switch_view("logs"), UI.FONT_SECTION, "logs"),

        ]
        self._sidebar_widgets = []

        for item_idx, item in enumerate(sidebar_items):
            key, command, font, view_target = item
            if command is None:
                # Section label
                lbl = tk.Label(
                    self.shell_zone_c1,
                    text=self._t(key),
                    bg=UI.BG_PANEL,
                    fg=UI.COLOR_TEXT,
                    font=font,
                    anchor="w"
                )
                lbl.pack(fill="x", pady=(10, 4))
                self._sidebar_widgets.append((lbl, key, view_target))
            else:
                # Button
                btn = tk.Button(
                    self.shell_zone_c1,
                    text=self._t(key),
                    command=command,
                    bg=UI.BG_SECTION,
                    fg=UI.COLOR_TEXT,
                    font=font,
                    anchor="w",
                    padx=12,
                    pady=8,
                    relief="flat",
                    cursor="hand2"
                )
                if font == UI.FONT_LABEL:
                    # Indent sub-items slightly
                    btn.pack(fill="x", pady=2, padx=(12, 0))
                else:
                    btn.pack(fill="x", pady=2)
                self._sidebar_widgets.append((btn, key, view_target))

        # Vùng B: Active Hunt Workspace
        self.shell_zone_b = tk.Frame(self.main_shell, bg=UI.BG_DEFAULT)
        self.shell_zone_b.grid(row=1, column=1, sticky="nsew")


        self.after(100, self._poll_log_queue)
        self.after(1000, self._update_logs_metrics)

        # Vùng A: Quick Action Bar - 80px target height (using padding)
        self.action_bar_frame = tk.Frame(self.shell_zone_a, padx=32, pady=18, bg=UI.BG_DEFAULT)
        self.action_bar_frame.grid(row=0, column=0, sticky="nsew")
        self.shell_zone_a.grid_columnconfigure(0, weight=1)
        self.shell_zone_a.grid_rowconfigure(0, minsize=80, weight=1)

        # Configure columns for action_bar_frame
        self.action_bar_frame.columnconfigure(0, minsize=380, weight=1)  # Window Selection
        self.action_bar_frame.columnconfigure(1, minsize=44, weight=0)   # Refresh
        self.action_bar_frame.columnconfigure(2, minsize=44, weight=0)   # Scan
        self.action_bar_frame.columnconfigure(3, minsize=260, weight=0)  # Bounds
        self.action_bar_frame.columnconfigure(4, minsize=160, weight=0)  # Start/Stop
        self.action_bar_frame.columnconfigure(5, minsize=80, weight=0)   # Language

        # Window Selection Combobox
        self.win_combo_var = tk.StringVar()
        self.win_combo = ttk.Combobox(
            self.action_bar_frame, textvariable=self.win_combo_var, state="readonly"
        )
        self.win_combo.grid(row=0, column=0, sticky="ew", padx=(0, 12))

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
        refresh_tooltip = self._t("refresh_tooltip") + "\n" + self._t("refresh_tooltip_desc") if hasattr(self, "_t") else "Refresh"

        self.refresh_btn = _create_icon_btn_component(
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
        self.refresh_btn.grid(row=0, column=1, sticky="w", padx=(0, 12))

        # Scan Manual Button
        from ui.icon_library import Icons
        self.scan_btn_icon_name = Icons.SCAN_SCREEN

        def on_scan_clicked():
            if hasattr(self, "scan_controller"):
                self.scan_controller.run_scan(manual=True)

        self.btn_manual_scan = _create_icon_btn_component(
            parent=self.action_bar_frame,
            icon_name=self.scan_btn_icon_name,
            icon_fallback="🔍",
            icon_size=16,
            button_size=36,
            command=on_scan_clicked,
            button_type="green_light",
            tooltip_text=self._t("scan_tooltip") if hasattr(self, "_t") else "Scan",
            state="normal",
            auto_hover_disabled=False,
        )
        self.btn_manual_scan.grid(row=0, column=2, sticky="w", padx=(0, 12))

        # Bounds Readiness State Placeholder (Minimum 260x36)
        self.bounds_placeholder = tk.Frame(self.action_bar_frame, width=260, height=36)
        self.bounds_placeholder.grid(row=0, column=3, sticky="w", padx=(0, 12))
        self.bounds_placeholder.pack_propagate(False)

        self.bounds_status_var = tk.StringVar()
        self.bounds_readiness_label = tk.Label(
            self.bounds_placeholder,
            textvariable=self.bounds_status_var,
            font=UI.FONT_LABEL
        )
        self.bounds_readiness_label.pack(side="left", fill="y", padx=5)

        # Unified Start/Stop Button (width 140px minimum layout space available, so we use min width via grid and padding)
        start_tooltip = self._t("start_hunt") + "\n(Ctrl+F5/F6)"

        self.start_stop_btn = _create_icon_btn_component(
            parent=self.action_bar_frame,
            icon_name="start",
            icon_fallback="▶️",
            text=self._t("start_hunt"),
            icon_size=20,
            button_size=44,
            padding={'padx': 20, 'pady': 6},
            command=self.on_start_stop_clicked,
            button_type="green",
            tooltip_text=start_tooltip,
            state="normal",
            auto_hover_disabled=False,
            width=140
        )

        # Grid it into columns 3 and 4 merged, or just use 3 since we redefined it
        self.start_stop_btn.grid(row=0, column=4, sticky="w", padx=(0, 12))

        # Language Selector (moved from header)
        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_cmb = ttk.Combobox(
            self.action_bar_frame, textvariable=self.lang_var, state="readonly", width=4
        )
        self.lang_cmb["values"] = ("en", "vi")
        self.lang_cmb.grid(row=0, column=5, sticky="e")
        self.lang_cmb.bind("<<ComboboxSelected>>", self.on_language_change)

        # DPI Scaling Guard using main action bar frame width
        # 1920 is standard. If the window is compressed significantly (< 1200), we fallback to compact.
        def on_action_bar_configure(event):
            if hasattr(self, 'state_controller') and hasattr(self.state_controller, '_update_window_bounds_display'):
                if event.width < 1200 and not getattr(self, '_bounds_compact_mode', False):
                    self._bounds_compact_mode = True
                    self.state_controller._update_window_bounds_display()
                elif event.width >= 1200 and getattr(self, '_bounds_compact_mode', False):
                    self._bounds_compact_mode = False
                    self.state_controller._update_window_bounds_display()
        self.action_bar_frame.bind("<Configure>", on_action_bar_configure)

        # UX2: View Manager for Zone B
        self._current_view = None
        self._views = {}

        from ui.views.hunt_workspace_frame import HuntWorkspaceFrame
        from ui.views.setup_content_frame import SetupContentFrame
        from ui.views.help_support_frame import HelpSupportFrame
        from ui.views.stats_content_frame import StatsContentFrame
        from ui.views.activity_logs_frame import ActivityLogsFrame

        self._views["hunt"] = HuntWorkspaceFrame(self.shell_zone_b, self)
        self._views["setup"] = SetupContentFrame(self.shell_zone_b, self)
        self._views["help"] = HelpSupportFrame(self.shell_zone_b, self)
        self._views["stats"] = StatsContentFrame(self.shell_zone_b, self)
        self._views["logs"] = ActivityLogsFrame(self.shell_zone_b, self)

        self.logs_text_widget = self._views["logs"].text_widget


        # Retain tab references for backward compatibility with orchestrators/runners
        self.tab_hunt = self._views['hunt'].hunt_tab if hasattr(self._views['hunt'], 'hunt_tab') else None
        self.tab_setup = self._views['setup'].setup_tab if hasattr(self._views['setup'], 'setup_tab') else None
        self.tab_stats = self._views['stats'].stats_tab if hasattr(self._views['stats'], 'stats_tab') else None
        self.tab_help = self._views['help'].help_tab if hasattr(self._views['help'], 'help_tab') else None
        self.notebook = None

        # Display default view
        self.switch_view('hunt')

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
            font=UI.FONT_TEXT,
            bg="#e8e8e8",
            fg="#555555",
            relief="sunken",
        )
        self._db_status_bar.pack(fill="x", side="bottom")

        self.main_shell.pack(fill="both", expand=True, pady=(10, 0))

    def _build_global_apply_section(self):
        """Build global apply button section below tabs."""
        # Frame for global apply section (right-aligned)
        self.global_apply_frame = tk.Frame(self, relief="sunken", bd=1, bg="#f0f0f0")
        apply_frame = self.global_apply_frame
        apply_frame.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

        # Unsaved changes indicator (left side)
        indicator_frame = tk.Frame(apply_frame, bg="#f0f0f0")
        indicator_frame.pack(side="left", padx=8, pady=6)

        self.unsaved_indicator_label = tk.Label(
            indicator_frame, text="", fg="#666", font=UI.FONT_TEXT, bg="#f0f0f0"
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
        self.global_apply_btn.pack(side="right", padx=10, pady=6)

        if not isinstance(save_icon, str):
            try:
                self._image_refs.append(save_icon)
            except Exception:
                pass

        self.has_unsaved_changes = False
        self._update_unsaved_indicator()

    def _on_window_configure(self, event):
        pass




    def _check_initial_logs_state(self):
        """Check window height and auto-collapse logs if needed (UX4B.1)."""
        self.update_idletasks()
        current_height = self.winfo_height()
        if current_height < 900:
            self._last_height_under_900 = True
            if getattr(self, "logs_expanded", False):
                self._toggle_bottom_logs()
        else:
            self._last_height_under_900 = False

    def _update_logs_metrics(self):
        """Update metrics on the bottom logs header."""
        if self._is_destroyed:
            return

        try:
            fps = 0.0
            scans = 0
            running_time = "00:00:00"

            # Here we might fetch actual metrics from app components
            # We would need to read this from HuntLogger or VisionEngine
            # But let's check HuntLogger session start
            logger = get_hunt_logger()
            if hasattr(logger, "session_start"):
                duration = (datetime.now() - logger.session_start).total_seconds()
                h = int(duration // 3600)
                m = int((duration % 3600) // 60)
                s = int(duration % 60)
                running_time = f"{h:02d}:{m:02d}:{s:02d}"

            # Basic dummy stats if actual stats not easily available
            # In real system, we hook into VisionEngine or main orchestrator stats
            from lib.system.hunt_logger import get_hunt_logger

            # Since VisionEngine stats are inside its instance, let's just make it generic or try to extract from global
            self.logs_metrics_label.config(text=f"⚡ FPS: {fps:.1f} | 🎯 Quét: {scans} | ⏱ Chạy: {running_time}")

        except Exception:
            pass

        self.after(1000, self._update_logs_metrics)

    def _poll_log_queue(self):
        """Poll log messages from HuntLogger and append to UI (UX4B.2)."""
        if self._is_destroyed:
            return

        try:
            logger = get_hunt_logger()
            if hasattr(logger, "ui_queue"):
                if getattr(logger, "dropped_log_count", 0) > 0:
                    dropped = logger.dropped_log_count
                    logger.dropped_log_count = 0
                    warn_msg = f"[!] Đã bỏ qua {dropped} dòng log do quá tải"
                    if 'logs' in getattr(self, '_views', {}):
                        self._views['logs'].append_message(warn_msg)

                lines_processed = 0
                while lines_processed < 50:
                    try:
                        record = logger.ui_queue.get_nowait()
                        # QueueHandler.prepare() automatically formats the message into record.message in Python 3.2+
                        if hasattr(record, "message"):
                            msg = record.message
                        else:
                            msg = record.getMessage()

                        if 'logs' in getattr(self, '_views', {}):
                            self._views['logs'].append_message(msg)
                        lines_processed += 1
                    except queue.Empty:
                        break

                if lines_processed > 0 and 'logs' in getattr(self, '_views', {}):
                    self._views['logs'].trim_to_limit(1000)

        except Exception as e:
            print(f"Error polling logs: {e}")

        # Flush frequently
        self.after(100, self._poll_log_queue)

    def switch_view(self, view_key: str):
        if not hasattr(self, '_views') or view_key not in self._views:
            return

        # Hide current view
        if hasattr(self, '_current_view') and self._current_view:
            self._current_view.grid_remove()
            if hasattr(self._current_view, "on_view_hidden"):
                self._current_view.on_view_hidden()

        # Show new view
        target_view = self._views[view_key]
        target_view.grid(row=0, column=0, sticky="nsew")

        # Zone B needs grid row/col configs
        self.shell_zone_b.columnconfigure(0, weight=1)
        self.shell_zone_b.rowconfigure(0, weight=1)

        self._current_view = target_view
        self.current_view_key = view_key

        # Update sidebar selected state
        if hasattr(self, '_sidebar_widgets'):
            for widget, _, view_target in self._sidebar_widgets:
                if isinstance(widget, tk.Button):
                    if view_target == view_key:
                        widget.config(bg=UI.COLOR_INFO, fg=UI.BG_DEFAULT)
                    else:
                        widget.config(bg=UI.BG_SECTION, fg=UI.COLOR_TEXT)

        if hasattr(target_view, "on_view_shown"):
            target_view.on_view_shown()

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
        saved_list = self.hunt_cfg.get("monster_rotation", [])
        self.monster_rotation = []
        for item in saved_list:
            if isinstance(item, dict):
                self.monster_rotation.append(
                    {
                        "monster_id": item.get("monster_id", 0),
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "dungeon_id": item.get("dungeon_id", None),
                    }
                )

    def on_language_change(self, _evt=None):
        # Save selection based on hwnd to prevent loss on language change
        saved_hwnd = None
        if getattr(self, "hunt_selected", None) and isinstance(self.hunt_selected, dict):
            saved_hwnd = self.hunt_selected.get("hwnd")

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
        self.title(self._t("app_title"))
        self.refresh_translations()

        # Re-apply window selection robustly by hwnd
        if saved_hwnd and hasattr(self, "win_items_map"):
            new_title = self.win_items_map.get(saved_hwnd)
            if new_title and hasattr(self, "win_items"):
                for idx, item in enumerate(self.win_items):
                    if item.get("hwnd") == saved_hwnd:
                        if hasattr(self, "win_combo"):
                            self.win_combo.current(idx)
                        if hasattr(self, "win_combo_var"):
                            self.win_combo_var.set(new_title)
                        self.window_controller.on_window_combo_selected()
                        break

    def refresh_translations(self):
        # Save selection based on hwnd to prevent loss on language change
        saved_hwnd = None
        if getattr(self, "hunt_selected", None) and isinstance(self.hunt_selected, dict):
            saved_hwnd = self.hunt_selected.get("hwnd")

        # Dynamically update text on widgets without rebuilding
        # _create_icon_btn_component returns a wrapper with set_text/set_tooltip if it's our custom component
        # But if it returns standard button, we config directly.
        self._refresh_start_stop_visual()

        if hasattr(self.refresh_btn, "set_tooltip"):
            refresh_tooltip_new = self._t("refresh_tooltip") + "\n" + self._t("refresh_tooltip_desc")
            self.refresh_btn.set_tooltip(refresh_tooltip_new)

        # Update combo tooltip
        try:
            from ui.helpers.tooltip import attach_i18n_tooltip
            from lib.i18n import I18N_GLOBAL
            attach_i18n_tooltip(
                self.win_combo,
                key="window_select_tooltip",
                ns=I18N_GLOBAL,
                lang_provider=lambda: self.lang,
            )
        except ImportError:
            pass

        # Update bounds readiness label explicitly via state controller
        if hasattr(self, 'state_controller') and hasattr(self.state_controller, '_update_window_bounds_display'):
            self.state_controller._update_window_bounds_display()

        # Optionally update tabs here, though the prompt primarily requests
        # Zone A widgets to change immediately without losing state.
        # Now handled by views instead of notebook
        if hasattr(self, 'update_shell_translations'):
            self.update_shell_translations()

    def update_shell_translations(self):
        """Update i18n text for shell elements like sidebar."""
        if hasattr(self, '_sidebar_widgets'):
            for widget, key, _ in self._sidebar_widgets:
                try:
                    if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                        widget.config(text=self._t(key))
                except Exception:
                    pass

    def on_setup_wizard(self, hide_parent=True):
        self.window_controller.on_setup_wizard(hide_parent)

    def try_close_setup_wizard(self) -> bool:
        return self.window_controller.try_close_setup_wizard()

    def try_close_library_manager(self) -> bool:
        return self.library_manager_controller.try_close_library_manager()

    def _switch_to_tab(self, tab_index: int):
        """Switch to specified tab via keyboard shortcut."""
        try:
            tab_map = {0: 'hunt', 1: 'setup', 2: 'stats', 3: 'help'}
            if tab_index in tab_map:
                self.switch_view(tab_map[tab_index])
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

    def _refresh_start_stop_visual(self):
        is_running = hasattr(self, "hunt_orchestrator") and getattr(self.hunt_orchestrator, "hunt_running", False)

        if is_running:
            text = self._t("stop_hunt")
            tooltip = self._t("stop_hunt") + "\n(Ctrl+F6)"
            bg_color = UI.BTN_STOP_BG
        else:
            text = self._t("start_hunt")
            tooltip = self._t("start_hunt") + "\n(Ctrl+F5)"
            bg_color = UI.BTN_START_BG

        if hasattr(self.start_stop_btn, "set_text"):
            self.start_stop_btn.set_text(text)
            self.start_stop_btn.set_tooltip(tooltip)
            # Custom component coloring would rely on button_type typically,
            # but we can fallback to config if needed. We assume custom wrapper might support bg configure.
            try:
                self.start_stop_btn.config(bg=bg_color)
            except Exception:
                pass
        else:
            self.start_stop_btn.config(text=text, bg=bg_color)

    def on_start_stop_clicked(self):
        if getattr(self, "_action_locked", False):
            return

        self._action_locked = True

        # Debounce: Disable button while state transition resolves
        if hasattr(self.start_stop_btn, "configure"):
            self.start_stop_btn.configure(state="disabled")
        elif hasattr(self.start_stop_btn, "config"):
            self.start_stop_btn.config(state="disabled")

        is_running = hasattr(self, "hunt_orchestrator") and getattr(self.hunt_orchestrator, "hunt_running", False)
        if is_running:
            self._request_stop_hunt()
        else:
            self._request_start_hunt()

        self.after(500, self._reenable_start_stop_btn)

    def _reenable_start_stop_btn(self):
        self._action_locked = False
        if hasattr(self.start_stop_btn, "configure"):
            self.start_stop_btn.configure(state="normal")
        elif hasattr(self.start_stop_btn, "config"):
            self.start_stop_btn.config(state="normal")
        self._refresh_start_stop_visual()

    def _on_orchestrator_state_change(self, state: str):
        if state == "running":
            if hasattr(self, "hunt_status"):
                self.hunt_status.set(self._t("hunt_running"))
            if hasattr(self, "tab_hunt") and hasattr(self.tab_hunt, "update_hunt_status_color"):
                self.tab_hunt.update_hunt_status_color("running")
        elif state in ["idle", "error", "stopped"]:
            if state == "idle" and hasattr(self, "hunt_status"):
                self.hunt_status.set(
                    self._t("hunt_idle") if hasattr(self, "_t") else "Idle"
                )
            if hasattr(self, "tab_hunt") and hasattr(self.tab_hunt, "update_hunt_status_color"):
                self.tab_hunt.update_hunt_status_color(state)

        self._refresh_start_stop_visual()

    def _request_start_hunt(self):
        if hasattr(self, "hunt_orchestrator") and getattr(self.hunt_orchestrator, "hunt_running", False):
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

    def _request_stop_hunt(self):
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
        display_mode = self.rotation_mode_var.get()
        if hasattr(self, "rotation_mode_map"):
            mode = self.rotation_mode_map.get(display_mode, display_mode)
        else:
            mode = display_mode

        if mode not in {"sequence", "priority"}:
            mode = "sequence"

        self.hunt_cfg["rotation_mode"] = mode
        self._refresh_monster_rotation_list()
        self.hunt_status.set(f"Rotation mode: {mode}")

    def promote_detected_monster(self, selection):
        if not selection:
            return

        idx = selection[0]
        if not hasattr(self, '_detected_snapshot_items') or idx >= len(self._detected_snapshot_items):
            return

        runtime_item = self._detected_snapshot_items[idx]

        # Only db_match items with valid monster_id can be promoted
        if runtime_item.get("resolution_state") != "db_match" or not runtime_item.get("monster_id"):
            return

        monster_id = runtime_item["monster_id"]
        dungeon_id = runtime_item.get("dungeon_id")

        # Check for duplicates
        for existing in self.monster_rotation:
            if existing.get("monster_id") == monster_id and existing.get("dungeon_id") == dungeon_id:
                # Already exists
                return

        # Calculate new priority
        max_priority = 0
        for m in self.monster_rotation:
            if m.get("priority", 0) > max_priority:
                max_priority = m.get("priority", 0)

        new_priority = max_priority + 1

        # Add to rotation
        new_entry = {
            "monster_id": monster_id,
            "name": runtime_item.get("name", "Unknown"),
            "priority": new_priority,
            "dungeon_id": dungeon_id
        }
        self.monster_rotation.append(new_entry)

        # Normalize priorities 1..N
        self.monster_rotation.sort(key=lambda x: x.get("priority", 999))
        for i, m in enumerate(self.monster_rotation, 1):
            m["priority"] = i

        self.has_unsaved_changes = True
        if hasattr(self, "_update_unsaved_indicator"):
            self._update_unsaved_indicator()

        self._refresh_monster_rotation_list()

        # We also need to refresh the detected list to show the 'Added' status
        if hasattr(self, '_last_snapshot'):
            self._update_detected_monsters_list(self._last_snapshot)

    def on_scene_monsters_detected(self, snapshot):
        # Throttle/ensure running on main thread is done by HuntOrchestrator
        self._last_snapshot = snapshot
        if self.hunt_cfg.get("target_policy", "configured_only") == "all_resolved":
            self._update_detected_monsters_list(snapshot)

    def _update_detected_monsters_list(self, snapshot):
        if not hasattr(self, "detected_monsters_listbox"):
            return

        current_selection = self.detected_monsters_listbox.curselection()
        selected_idx = current_selection[0] if current_selection else None

        # We need to maintain scroll position if possible
        yview = self.detected_monsters_listbox.yview()

        self.detected_monsters_listbox.delete(0, tk.END)
        self._detected_snapshot_items = []

        configured_keys = {(m.get("monster_id"), m.get("dungeon_id")) for m in getattr(self, 'monster_rotation', []) if m.get("monster_id")}

        for idx, item in enumerate(snapshot):
            self._detected_snapshot_items.append(item)

            name = item.get("name", "Unknown")
            resolution_state = item.get("resolution_state", "unmapped_visual")
            monster_id = item.get("monster_id")

            if resolution_state == "db_match":
                status = "✓ "
                if (monster_id, item.get("dungeon_id")) in configured_keys:
                    status += f"[{self._t('monster_promoted')}] "
                elif item.get("confidence", 0) > 0:
                    status += f"({item['confidence']:.2f}) "
                display_text = f"{status}{name} #{monster_id} - {self._t('monster_db_match')}"
            elif resolution_state == "db_miss":
                display_text = f"⚠ {name} - {self._t('monster_db_missing')}"
            else:
                display_text = f"❓ {self._t('monster_unidentified')} ({item.get('template_label', '')})"

            self.detected_monsters_listbox.insert(tk.END, display_text)

        if selected_idx is not None and selected_idx < len(self._detected_snapshot_items):
            self.detected_monsters_listbox.selection_set(selected_idx)

        self.detected_monsters_listbox.yview_moveto(yview[0])


    def _refresh_monster_rotation_list(self):
        """Refresh the configured monster rotation UI queue."""
        if not hasattr(self, "monster_rotation_listbox"):
            return

        self.monster_rotation_listbox.delete(0, tk.END)

        from database import get_monster_by_id_api, find_monster_by_name_api

        # In-memory cache for DB queries during this panel's lifetime
        if not hasattr(self, "_monster_metadata_cache"):
            self._monster_metadata_cache = {}

        # Re-sort list just to be safe
        self.monster_rotation.sort(key=lambda x: x.get("priority", 999))

        for idx, entry in enumerate(self.monster_rotation):
            monster_id = entry.get("monster_id")
            name = entry.get("name")
            dungeon_id = entry.get("dungeon_id")

            cache_key = f"{monster_id}_{name}_{dungeon_id}"

            if cache_key not in self._monster_metadata_cache:
                # 1. Try by ID
                db_record = get_monster_by_id_api(str(monster_id)) if monster_id else None
                # 2. Try by Name fallback
                if not db_record and name:
                    db_record = find_monster_by_name_api(name, dungeon_id)
                self._monster_metadata_cache[cache_key] = db_record
            else:
                db_record = self._monster_metadata_cache[cache_key]

            if db_record:
                # Resolved metadata
                level = db_record.get("level", "--")
                hp = db_record.get("hp", "--")
                display_str = f"[#{monster_id}] {name} - Lv.{level} | HP: {hp}"
            else:
                # Missing metadata
                display_str = f"[{self._t('monster_rotation_unknown')}] {name} - Lv.-- | HP: --"

            self.monster_rotation_listbox.insert(tk.END, display_str)

    def _on_monster_move_up(self):
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        # Swap in RAM
        self.monster_rotation[idx], self.monster_rotation[idx - 1] = (
            self.monster_rotation[idx - 1],
            self.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_down(self):
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == len(self.monster_rotation) - 1:
            return

        idx = selection[0]
        # Swap in RAM
        self.monster_rotation[idx], self.monster_rotation[idx + 1] = (
            self.monster_rotation[idx + 1],
            self.monster_rotation[idx],
        )

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx + 1)

    def _on_monster_delete_from_list(self, _evt=None):
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        selected_indices = sorted(
            (idx for idx in selection if 0 <= idx < len(self.monster_rotation)),
            reverse=True,
        )
        if not selected_indices:
            return
        first_deleted_index = min(selected_indices)
        for idx in selected_indices:
            del self.monster_rotation[idx]

        # Re-assign priority to be continuous 1..N
        for i, entry in enumerate(self.monster_rotation):
            entry["priority"] = i + 1

        self._mark_unsaved()
        self._refresh_monster_rotation_list()

        if len(self.monster_rotation) > 0:
            new_sel = min(first_deleted_index, len(self.monster_rotation) - 1)
            self.monster_rotation_listbox.selection_set(new_sel)

    def _on_monster_add_smart(self):
        def on_monster_selected(record):
            # Check for duplicate
            monster_id = record["monster_id"]
            dungeon_id = record.get("dungeon_id")

            # Deduplicate by (monster_id, dungeon_id)
            for entry in self.monster_rotation:
                if entry.get("monster_id") == monster_id and entry.get("dungeon_id") == dungeon_id:
                    messagebox.showinfo(
                        self._t("info_title", ns="ui"),
                        self._t("monster_already_in_list").format(name=record["name"]),
                        parent=self
                    )
                    return

            # Add with new priority
            new_priority = len(self.monster_rotation) + 1
            new_entry = {
                "monster_id": monster_id,
                "name": record["name"],
                "priority": new_priority,
                "dungeon_id": dungeon_id
            }

            self.monster_rotation.append(new_entry)
            self._mark_unsaved()

            self._refresh_monster_rotation_list()

        MonsterPickerDialog(self, getattr(self, "lang", "vi"), on_monster_selected, self._t)

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

    def _update_monster_frame_title(self):
        """Update frame title to indicate current mode."""
        if not hasattr(self, "monster_frame"):
            return

        title = self._t("hunt_monsters")

        # Reset listbox background to default
        if hasattr(self, "monster_rotation_listbox"):
            self.monster_rotation_listbox.config(bg="white")

        self.monster_frame.config(text=title)

    def _update_monster_status(self):
        """Update current monster hunting status display."""
        if not hasattr(self, "monster_status_var"):
            return

        if not self.monster_rotation:
            self.monster_status_var.set(self._t("monster_none_selected"))
            return

        mode = self.hunt_cfg.get("rotation_mode", "sequence")

        if mode == "sequence":
            self.monster_status_var.set(f"Sequence: {len(self.monster_rotation)} monsters")
        else:
            sorted_monsters = sorted(self.monster_rotation, key=lambda m: m.get("priority", 1))
            current = sorted_monsters[0]
            self.monster_status_var.set(
                f"Priority: {current['name']} (P{current.get('priority', 1)}) | {len(self.monster_rotation)} total"
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
            m.get("training_mode", False) for m in self.monster_rotation
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
            # Ensure canonical schemas
            self.hunt_cfg["monster_rotation"] = getattr(self, "monster_rotation", [])
            self.hunt_cfg["skill_slots"] = self.hunt_cfg.get("skill_slots", [])
            # 1. Apply legacy setup settings when the compatibility method exists.
            apply_setup_settings = getattr(self, "_apply_setup_settings", None)
            if callable(apply_setup_settings):
                apply_setup_settings(save_to_file=False)

            # 2. Update hunt config from Hunt tab UI (in-place update)
            cfg = self.state_controller._hunt_from_ui()

            # 2.5. Update global hotkeys from Setup tab UI
            if hasattr(self, "global_hotkey_enabled_var"):
                enabled = self.global_hotkey_enabled_var.get()
                hotkeys = cfg.get("global_hotkeys", {})

                def _hotkey_value(attr_name, config_name, default):
                    variable = getattr(self, attr_name, None)
                    return variable.get() if variable is not None else hotkeys.get(config_name, default)

                start_key = _hotkey_value("global_hotkey_start_var", "start_key", "ctrl+shift+r")
                stop_key = _hotkey_value("global_hotkey_stop_var", "stop_key", "ctrl+shift+e")
                wizard_key = _hotkey_value("global_hotkey_wizard_var", "setup_wizard_key", "ctrl+alt+n")
                library_key = _hotkey_value("global_hotkey_library_var", "library_manager_key", "ctrl+shift+l")

                # Validate: all hotkeys must be unique
                vision_key = _hotkey_value("global_hotkey_vision_var", "vision_wizard_key", "ctrl+shift+v")
                monster_key = _hotkey_value("global_hotkey_monster_var", "monster_editor_key", "ctrl+shift+m")
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
            if not save_hunt_config(cfg):
                raise RuntimeError("Could not save hunt configuration")
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


    def _mark_unsaved(self):
        self.has_unsaved_changes = True
        self._update_unsaved_indicator()

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

    def clear_target_ui(self):
        if hasattr(self, "hunt_target_info"):
            self.hunt_target_info.set("Target: None")
        if hasattr(self, "monster_rotation_listbox"):
            try:
                self.monster_rotation_listbox.selection_clear(0, tk.END)
            except Exception as e:
                import logging
                logging.debug(f"Failed to clear monster rotation listbox: {e}")

    def on_close(self):
        self.lifecycle_controller.on_close()

    def destroy(self):
        self._is_destroyed = True
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
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
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

        # Hydrate i18n from database
        try:
            from lib.i18n import load_from_db
            load_from_db()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[i18n Init] Failed to call load_from_db: {e}")

        # Start application
        app = App()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        print("[Main] Tkinter window initialized and mainloop starting...")
        app.mainloop()
    finally:
        # Always release lock on exit
        instance_lock.release()


if __name__ == "__main__":
    main()
