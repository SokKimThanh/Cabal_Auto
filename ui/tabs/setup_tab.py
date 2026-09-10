"""
Setup Tab Module.
Provides the UI for application configuration and setup.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING

from lib.i18n import t as i18n_t, GLOBAL_NS as I18N_GLOBAL
from lib.ui_style_v2 import UIStyleV2
from ui.components.base.responsive_grid_base import ResponsiveGridBase

if TYPE_CHECKING:
    from app_gui import App


class SetupTab(ResponsiveGridBase):
    """
    Setup Tab UI Class.
    Manages settings, hotkeys, and configuration modes.
    """
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    # pylint: disable=too-many-ancestors,protected-access

    def __init__(self, parent: ttk.Notebook, app: "App", *args, **kwargs):
        super().__init__(parent, bg=UIStyleV2.THEME_BG_APP, *args, **kwargs)
        # Pad the content frame instead to maintain visual consistency
        self.get_content_frame().configure(padx=12, pady=12)
        self.parent = parent
        self.app = app
        self.lang = getattr(app, "lang", "vi")
        self.browse_btn = None

        self._build_ui()
        self._update_setup_visibility()

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, "_t"):
            return self.app._t(key, **kwargs)
        return i18n_t(key, ns=I18N_GLOBAL, lang=self.lang, **kwargs)

    def _on_setting_changed(self, *args):
        """Callback triggered when any setting is modified."""
        if hasattr(self.app, "_mark_unsaved"):
            self.app._mark_unsaved()

    def _build_collapsible_group(self, row, title_key, desc_key, content_builder):
        group_frame = ttk.Frame(self.get_content_frame())
        group_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        group_frame.grid_columnconfigure(0, weight=1)

        is_visible_var = tk.BooleanVar(value=True)
        header_frame = ttk.Frame(group_frame)
        header_frame.grid(row=0, column=0, sticky="nsew")
        header_frame.grid_columnconfigure(0, weight=1)

        btn_text_var = tk.StringVar(value=f"▶ {self._t(title_key)}")

        content_frame = tk.Frame(
            group_frame,
            bg=UIStyleV2.THEME_BG_APP,
            padx=UIStyleV2.SPACE_MD,
            pady=UIStyleV2.SPACE_SM,
        )

        def toggle(_event=None):
            visible = not is_visible_var.get()
            is_visible_var.set(visible)
            if visible:
                btn_text_var.set(f"▼ {self._t(title_key)}")
                content_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
                content_frame.grid_columnconfigure(1, weight=1)
                content_frame.grid_columnconfigure(3, weight=1)
            else:
                btn_text_var.set(f"▶ {self._t(title_key)}")
                content_frame.grid_remove()

        # Make the entire header frame clickable and accessible
        header_frame.bind("<Button-1>", toggle)
        header_frame.bind("<Return>", toggle)
        header_frame.bind("<space>", toggle)
        header_frame.configure(
            cursor="hand2",
            takefocus=1,
        )

        def _on_focus_in(_event):
            try:
                pass
            except tk.TclError:
                pass

        def _on_focus_out(_event):
            try:
                pass
            except tk.TclError:
                pass

        header_frame.bind("<FocusIn>", _on_focus_in)
        header_frame.bind("<FocusOut>", _on_focus_out)

        btn = ttk.Label(
            header_frame,
            textvariable=btn_text_var,
            cursor="hand2",
        )
        btn.bind("<Button-1>", toggle)
        btn.pack(side="left")

        if desc_key:
            desc_label = self.app.bind_text(ttk.Label(
                header_frame,
                cursor="hand2",
            ), desc_key)
            desc_label.bind("<Button-1>", toggle)
            desc_label.pack(side="left", padx=(8, 0))

        content_builder(content_frame)

        # Initial render based on is_visible_var
        if is_visible_var.get():
            btn_text_var.set(f"▼ {self._t(title_key)}")
            content_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
            content_frame.grid_columnconfigure(1, weight=1)
            content_frame.grid_columnconfigure(3, weight=1)

        # Store these for _update_setup_visibility to show/hide the entire group
        return group_frame, is_visible_var, toggle

    def _build_hotkeys_content(self, frame):
        hotkey_cfg = self.app.hunt_cfg.get("global_hotkeys", {})
        self.app.global_hotkey_enabled_var = tk.BooleanVar(
            value=hotkey_cfg.get("enabled", True)
        )
        self.app.global_hotkey_enabled_var.trace_add("write", self._on_setting_changed)

        chk = ttk.Checkbutton(
            frame,
            variable=self.app.global_hotkey_enabled_var,
            command=self._on_global_hotkey_toggle,
        )
        self.app.bind_text(chk, "enable_global_hotkeys")
        chk.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_options = [
            "ctrl+shift+r",
            "ctrl+shift+e",
            "ctrl+shift+s",
            "ctrl+alt+r",
            "ctrl+alt+s",
            "f9",
            "f10",
            "f11",
            "f12",
        ]

        self.app.bind_text(ttk.Label(frame), "start_stop_hotkeys").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self.app.global_hotkey_start_var = tk.StringVar(
            value=hotkey_cfg.get("start_key", "ctrl+shift+r")
        )
        self.app.global_hotkey_start_var.trace_add("write", self._on_setting_changed)

        self.app.global_hotkey_stop_var = tk.StringVar(
            value=hotkey_cfg.get("stop_key", "ctrl+shift+e")
        )
        self.app.global_hotkey_stop_var.trace_add("write", self._on_setting_changed)

        # Container for the two Comboboxes side by side
        hotkey_container = ttk.Frame(frame)
        hotkey_container.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Combobox(
            hotkey_container,
            textvariable=self.app.global_hotkey_start_var,
            values=hotkey_options,
            width=15,
            state="readonly",
        ).pack(side="left")

        ttk.Label(hotkey_container, text=" / ").pack(side="left")

        ttk.Combobox(
            hotkey_container,
            textvariable=self.app.global_hotkey_stop_var,
            values=hotkey_options,
            width=15,
            state="readonly",
        ).pack(side="left")

    def _validate_numeric(self, action, value_if_allowed):
        if action == "1":  # Insertion
            if value_if_allowed:
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
        return True

    def _add_entry_row(
        self, frame, row, label_key, var_obj, col_offset=0, width=8,
        validate=False, from_=0, to=100, increment=1, is_float=False
    ):
        self.app.bind_text(ttk.Label(frame), label_key).grid(
            row=row,
            column=0 + col_offset,
            sticky="e",
            padx=(16 if col_offset else 0, 4),
            pady=4,
        )
        kwargs = {
            "textvariable": var_obj,
            "width": width,
            "from_": from_,
            "to": to,
            "increment": increment,
        }
        if is_float:
            kwargs["format"] = "%.2f"

        if validate:
            kwargs.update(
                {
                    "validate": "key",
                    "validatecommand": (
                        self.register(self._validate_numeric),
                        "%d",
                        "%P",
                    ),
                }
            )
            input_widget = ttk.Spinbox(frame, **kwargs)
        else:
            # For non-numeric fields like target_key, use Entry
            # We don't want Spinbox for string values
            input_widget = ttk.Entry(frame, textvariable=var_obj, width=width)

        input_widget.grid(
            row=row, column=1 + col_offset, sticky="ew", pady=4
        )

        # Add warning label placeholder
        warning_label = ttk.Label(frame, text="", foreground=UIStyleV2.THEME_STATE_READY)
        warning_label.grid(row=row, column=2 + col_offset, sticky="w", padx=(4, 0))

        def check_warning(*_args):
            try:
                val = float(var_obj.get())
                if is_float and val < 0.2 and label_key in ("search_interval", "attack_interval"):
                    warning_label.config(text="⚠️", foreground=UIStyleV2.THEME_STATE_DANGER)
                elif val > to or val < from_:
                    warning_label.config(text="⚠️", foreground=UIStyleV2.THEME_STATE_DANGER)
                else:
                    warning_label.config(text="")
            except ValueError:
                pass

        var_obj.trace_add("write", check_warning)
        check_warning() # Initial check

    def _build_advanced_content(self, frame):
        self.app.setup_target_key_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("target_key", "TAB"))
        )
        self.app.setup_target_key_var.trace_add("write", self._on_setting_changed)

        self.app.setup_press_ms_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_press_ms", 60))
        )
        self.app.setup_press_ms_var.trace_add("write", self._on_setting_changed)

        self.app.setup_target_cycle_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("target_cycle_delay", 0.2))
        )
        self.app.setup_target_cycle_var.trace_add("write", self._on_setting_changed)

        self.app.setup_search_interval_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("search_interval", 0.25))
        )
        self.app.setup_search_interval_var.trace_add("write", self._on_setting_changed)

        self.app.setup_attack_interval_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_interval", 0.15))
        )
        self.app.setup_attack_interval_var.trace_add("write", self._on_setting_changed)

        self.app.setup_lost_timeout_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("lost_timeout_sec", 1.2))
        )
        self.app.setup_lost_timeout_var.trace_add("write", self._on_setting_changed)

        self.app.setup_attack_duration_var = tk.StringVar(
            value=str(self.app.hunt_cfg.get("attack_min_duration_sec", 1.5))
        )
        self.app.setup_attack_duration_var.trace_add("write", self._on_setting_changed)

        self._add_entry_row(frame, 0, "target_key", self.app.setup_target_key_var)

        self._add_entry_row(
            frame, 1, "press_ms", self.app.setup_press_ms_var, validate=True,
            from_=10, to=1000, increment=10, is_float=False, col_offset=0
        )
        self._add_entry_row(
            frame,
            1,
            "target_cycle",
            self.app.setup_target_cycle_var,
            col_offset=3,
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True
        )
        self._add_entry_row(
            frame,
            2,
            "search_interval",
            self.app.setup_search_interval_var,
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True, col_offset=0
        )
        self._add_entry_row(
            frame,
            2,
            "attack_interval",
            self.app.setup_attack_interval_var,
            col_offset=3,
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True
        )
        self._add_entry_row(
            frame, 3, "lost_timeout", self.app.setup_lost_timeout_var, validate=True,
            from_=0.5, to=10.0, increment=0.1, is_float=True, col_offset=0
        )
        self._add_entry_row(
            frame,
            3,
            "attack_duration",
            self.app.setup_attack_duration_var,
            col_offset=3,
            validate=True,
            from_=0.5, to=60.0, increment=0.5, is_float=True
        )

    def _build_window_content(self, frame):
        self.app.bind_text(ttk.Label(frame), "template").grid(
            row=0, column=0, sticky="e", pady=4
        )
        self.app.setup_template_var = tk.StringVar(
            value=str(
                self.app.hunt_cfg.get("template_path", "assets/images/target_frame.png")
            )
        )
        self.app.setup_template_var.trace_add("write", self._on_setting_changed)
        ttk.Entry(frame, textvariable=self.app.setup_template_var, width=30).grid(
            row=0, column=1, columnspan=2, sticky="ew", pady=4
        )
        self.browse_btn = ttk.Button(frame, command=self._browse_template)
        self.app.bind_text(self.browse_btn, "browse")
        self.browse_btn.grid(row=0, column=3, padx=(4, 0), pady=4)

    def _build_ui(self):
        self.get_content_frame().grid_columnconfigure(0, weight=1)
        self.get_content_frame().grid_columnconfigure(1, weight=1)

        # Section 2: Global Hotkeys
        self.hotkey_group, self.hotkey_visible, self.hotkey_toggle = (
            self._build_collapsible_group(
                1, "setup_hotkeys", "setup_hotkeys_desc", self._build_hotkeys_content
            )
        )

        # Section 3: Advanced Hunt Settings
        self.adv_group, self.adv_visible, self.adv_toggle = (
            self._build_collapsible_group(
                2, "setup_advanced", "setup_advanced_desc", self._build_advanced_content
            )
        )

        # Section 4: Window Settings
        self.window_group, self.window_visible, self.window_toggle = (
            self._build_collapsible_group(
                3, "setup_window", "setup_window_desc", self._build_window_content
            )
        )

    def _browse_template(self):
        self.browse_btn.state(["disabled"])

        def open_dialog():
            path = filedialog.askopenfilename(
                title="Select template image",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
            )
            if path:
                self.app.setup_template_var.set(path)
            self.browse_btn.state(["!disabled"])

        self.after(50, open_dialog)



    def _on_global_hotkey_toggle(self):
        if hasattr(self.app, "_on_global_hotkey_toggle"):
            self.app._on_global_hotkey_toggle()

    def _update_setup_visibility(self):
        # All groups are always visible now since we only have advanced mode.
        self.adv_group.grid()
        self.window_group.grid()
