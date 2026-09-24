import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI

from ui.components.compact_window_selector import CompactWindowSelector
from ui.panels.screen_state_panel import ScreenStatePanel
from ui.helpers.button_styles import get_button_config

from ui.icon_library import Icons
from ui.components import create_icon_button as _create_icon_btn_component
import logging
from lib.events.event_bus import EventBus, GlobalApplyEvent, StartStopHuntEvent, LanguageChangedEvent
from lib.i18n import t as i18n_t
from lib.i18n import GLOBAL_NS as I18N_GLOBAL

logger = logging.getLogger(__name__)

class ActionBarView(tk.Frame):
    def __init__(self, parent, state_controller, *args, window_controller=None, scan_controller=None, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, *args, **kwargs)
        self.state_controller = state_controller
        self.window_controller = window_controller
        self.scan_controller = scan_controller

        self.action_bar_frame = self
        self.configure(padx=32, pady=10)

        # Configure columns for action_bar_frame (2 columns as requested)
        self.action_bar_frame.columnconfigure(0, weight=1)  # Left (Window Status)
        self.action_bar_frame.columnconfigure(1, weight=0)  # Right (Actions)

        self._build_col1_window_status()
        self._build_col2_actions()

    def _t(self, key):
        return i18n_t(key, ns=I18N_GLOBAL)

    def _build_col1_window_status(self):
        col1_frame = tk.Frame(self.action_bar_frame, bg=UI.BG_ELEVATED, bd=1, relief="solid", highlightbackground=UI.BORDER_PRIMARY, highlightthickness=1)
        col1_frame.grid(row=0, column=0, sticky="w")

        # Header Row (Always visible)
        status_header = tk.Frame(col1_frame, bg=UI.BG_ELEVATED)
        status_header.pack(fill="x", padx=8, pady=6)

        self.window_status_lbl = tk.Label(
            status_header,
            text=self._t("window_status_label"),
            font=UI.FONT_SECTION,
            fg=UI.TEXT_PRIMARY,
            bg=UI.BG_ELEVATED
        )
        self.window_status_lbl.pack(side="left", padx=(0, 12))

        def on_window_selected_from_compact(window_dict):
            """Callback when user selects window from compact selector."""
            try:
                # Set hunt_selected with window info
                self.state_controller.hunt_selected = {
                    "hwnd": window_dict.get("hwnd"),
                    "pid": window_dict.get("pid"),
                    "title": window_dict.get("title"),
                    "bounds": window_dict.get("bounds"),
                }
                # Save to config
                self.state_controller.set_hunt_config_value("window_pid", window_dict.get("pid"))
                self.state_controller.set_hunt_config_value("window_hwnd", window_dict.get("hwnd"))
                self.state_controller.set_hunt_config_value("window_title", window_dict.get("title"))
                self.state_controller.save_hunt_config()
                # Update bounds display
                if self.window_controller:
                    self.window_controller.update_window_bounds_display()
                self.state_controller.set_ui_var('hunt_status', f"✓ Selected: {window_dict['title']}")
            except Exception as e:
                logger.error(f"Error selecting window: {e}")

        self.compact_window_selector = CompactWindowSelector(
            status_header,
            on_window_selected=on_window_selected_from_compact,
            window_controller=self.window_controller,
            root=self.winfo_toplevel(),
        )
        # Auto-refresh window list on startup
        self.compact_window_selector._on_refresh()
        self.compact_window_selector.get_frame().pack(side="left", padx=(0, 12))

        # Scan Manual Button
        self.scan_btn_icon_name = Icons.SCAN_SCREEN

        def on_scan_clicked():
            if self.scan_controller:
                self.scan_controller.run_scan(manual=True)

        self.btn_manual_scan = _create_icon_btn_component(
            parent=status_header,
            icon_name=self.scan_btn_icon_name,
            icon_fallback="",
            icon_size=16,
            button_size=32,
            command=on_scan_clicked,
            button_type="green_light",
            tooltip_text=self._t("scan_tooltip"),
            state="normal",
            auto_hover_disabled=False,
        )
        self.btn_manual_scan.pack(side="left", padx=(0, 12))

        # Expanded Frame (Hidden initially)
        self.expanded_status_frame = tk.Frame(col1_frame, bg=UI.BG_BASE, highlightbackground=UI.BORDER_SUBTLE, highlightthickness=1)

        # Screen State Panel (inside expanded)
        self.bounds_placeholder = tk.Frame(self.expanded_status_frame, bg=UI.BG_BASE)
        self.bounds_placeholder.pack(side="left", fill="both", expand=True, padx=8, pady=4)

        self.screen_state_panel = ScreenStatePanel(self.bounds_placeholder)
        self.screen_state_panel.pack(side="left", fill="both", expand=True)

        def close_expanded_status():
            self.expanded_status_frame.pack_forget()
            expand_btn.config(text="▼")

        def toggle_expanded_status():
            if self.expanded_status_frame.winfo_ismapped():
                close_expanded_status()
            else:
                self.expanded_status_frame.pack(fill="x", expand=True, padx=4, pady=(0, 4))
                expand_btn.config(text="▲")

        close_btn = tk.Button(
            self.expanded_status_frame, text="✖", font=UI.FONT_SMALL, bg=UI.BG_BASE, fg=UI.TEXT_MUTED, bd=0, command=close_expanded_status, cursor="hand2"
        )
        close_btn.pack(side="right", anchor="n", padx=4, pady=4)

        expand_btn = tk.Button(
            status_header, text="▼", font=UI.FONT_SMALL, bg=UI.BG_ELEVATED, fg=UI.TEXT_SECONDARY, bd=0, command=toggle_expanded_status, cursor="hand2"
        )
        expand_btn.pack(side="right", padx=4)

    def _build_col2_actions(self):
        col2_frame = tk.Frame(self.action_bar_frame, bg=UI.BG_BASE)
        col2_frame.grid(row=0, column=1, sticky="e")

        # Global Apply Button
        apply_config = get_button_config("green_light")
        apply_kwargs = dict(apply_config)

        self.global_apply_btn = tk.Button(
            col2_frame,
            text=f"✓ {self._t('apply_all_settings_saved')}",
            command=lambda: EventBus.trigger(GlobalApplyEvent()),
            padx=16,
            pady=6,
            bg=UI.ACCENT_GREEN,
            activebackground=UI.ACCENT_GREEN_BG,
            state="disabled",
            **{k: v for k, v in apply_kwargs.items() if k not in ["bg", "activebackground"]}
        )
        self.global_apply_btn.pack(side="left", padx=(0, 12))

        # Unified Start/Stop Button
        start_tooltip = self._t("start_hunt") + "\n(Ctrl+F5/F6)"
        self.start_stop_btn = _create_icon_btn_component(
            parent=col2_frame,
            icon_name="start",
            icon_fallback="",
            text=self._t("start_hunt"),
            icon_size=20,
            button_size=44,
            padding={"padx": 20, "pady": 6},
            command=lambda: EventBus.trigger(StartStopHuntEvent()),
            button_type="primary",
            bg_color=UI.ACCENT_GREEN,
            hover_color=UI.ACCENT_GREEN_BG,
            tooltip_text=start_tooltip,
            state="normal",
            auto_hover_disabled=False,
            width=140,
        )
        self.start_stop_btn.pack(side="left", padx=(0, 12))

        # Language Selector
        import tkinter.ttk as ttk
        if 'lang' not in self.state_controller.ui_vars:
            self.state_controller.ui_vars['lang'] = tk.StringVar(value=self.state_controller.get_ui_var('lang', 'en'))
        self.lang_cmb = ttk.Combobox(
            col2_frame, textvariable=self.state_controller.ui_vars['lang'], state="readonly", width=4
        )
        self.lang_cmb["values"] = ("en", "vi")
        self.lang_cmb.pack(side="left", padx=(0, 12))
        self.lang_cmb.bind("<<ComboboxSelected>>", lambda e: EventBus.trigger(LanguageChangedEvent(self.state_controller.get_ui_var('lang'))))

    def update_translations(self):
        """Update strings inside the Action Bar."""
        if hasattr(self, "window_status_lbl"):
            self.window_status_lbl.config(text=self._t("window_status_label"))

        # Start/stop button text should be updated separately or by app.refresh_translations if it accesses this
