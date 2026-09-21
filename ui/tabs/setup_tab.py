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
        hotkey_cfg = self.app.state_controller.hunt_cfg.get("global_hotkeys", {})
        self.app.state_controller.set_ui_var('global_hotkey_enabled', hotkey_cfg.get("enabled", True))
        self.app.state_controller.ui_vars['global_hotkey_enabled'].trace_add("write", self._on_setting_changed)

        chk = ttk.Checkbutton(
            frame,
            variable=self.app.state_controller.ui_vars['global_hotkey_enabled'],
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
        self.app.state_controller.set_ui_var('global_hotkey_start', hotkey_cfg.get("start_key", "ctrl+shift+r"))
        self.app.state_controller.ui_vars['global_hotkey_start'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('global_hotkey_stop', hotkey_cfg.get("stop_key", "ctrl+shift+e"))
        self.app.state_controller.ui_vars['global_hotkey_stop'].trace_add("write", self._on_setting_changed)

        # Container for the two Comboboxes side by side
        hotkey_container = ttk.Frame(frame)
        hotkey_container.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Combobox(
            hotkey_container,
            textvariable=self.app.state_controller.ui_vars['global_hotkey_start'],
            values=hotkey_options,
            width=15,
            state="readonly",
        ).pack(side="left")

        ttk.Label(hotkey_container, text=" / ").pack(side="left")

        ttk.Combobox(
            hotkey_container,
            textvariable=self.app.state_controller.ui_vars['global_hotkey_stop'],
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
        self.app.state_controller.set_ui_var('setup_target_key', str(self.app.state_controller.hunt_cfg.get("target_key", "TAB")))
        self.app.state_controller.ui_vars['setup_target_key'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_press_ms', str(self.app.state_controller.hunt_cfg.get("attack_press_ms", 60)))
        self.app.state_controller.ui_vars['setup_press_ms'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_target_cycle', str(self.app.state_controller.hunt_cfg.get("target_cycle_delay", 0.2)))
        self.app.state_controller.ui_vars['setup_target_cycle'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_search_interval', str(self.app.state_controller.hunt_cfg.get("search_interval", 0.25)))
        self.app.state_controller.ui_vars['setup_search_interval'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_attack_interval', str(self.app.state_controller.hunt_cfg.get("attack_interval", 0.15)))
        self.app.state_controller.ui_vars['setup_attack_interval'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_lost_timeout', str(self.app.state_controller.hunt_cfg.get("lost_timeout_sec", 1.2)))
        self.app.state_controller.ui_vars['setup_lost_timeout'].trace_add("write", self._on_setting_changed)

        self.app.state_controller.set_ui_var('setup_attack_duration', str(self.app.state_controller.hunt_cfg.get("attack_min_duration_sec", 1.5)))
        self.app.state_controller.ui_vars['setup_attack_duration'].trace_add("write", self._on_setting_changed)

        self._add_entry_row(frame, 0, "target_key", self.app.state_controller.ui_vars['setup_target_key'])

        self._add_entry_row(
            frame, 1, "press_ms", self.app.state_controller.ui_vars['setup_press_ms'], validate=True,
            from_=10, to=1000, increment=10, is_float=False, col_offset=0
        )
        self._add_entry_row(
            frame,
            1,
            "target_cycle",
            self.app.state_controller.ui_vars['setup_target_cycle'],
            col_offset=3,
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True
        )
        self._add_entry_row(
            frame,
            2,
            "search_interval",
            self.app.state_controller.ui_vars['setup_search_interval'],
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True, col_offset=0
        )
        self._add_entry_row(
            frame,
            2,
            "attack_interval",
            self.app.state_controller.ui_vars['setup_attack_interval'],
            col_offset=3,
            validate=True,
            from_=0.1, to=5.0, increment=0.1, is_float=True
        )
        self._add_entry_row(
            frame, 3, "lost_timeout", self.app.state_controller.ui_vars['setup_lost_timeout'], validate=True,
            from_=0.5, to=10.0, increment=0.1, is_float=True, col_offset=0
        )
        self._add_entry_row(
            frame,
            3,
            "attack_duration",
            self.app.state_controller.ui_vars['setup_attack_duration'],
            col_offset=3,
            validate=True,
            from_=0.5, to=60.0, increment=0.5, is_float=True
        )

    def _build_window_content(self, frame):
        self.app.bind_text(ttk.Label(frame), "template").grid(
            row=0, column=0, sticky="e", pady=4
        )
        self.app.state_controller.set_ui_var('setup_template', str(self.app.state_controller.hunt_cfg.get("template_path", "assets/images/target_frame.png")))
        self.app.state_controller.ui_vars['setup_template'].trace_add("write", self._on_setting_changed)
        ttk.Entry(frame, textvariable=self.app.state_controller.ui_vars['setup_template'], width=30).grid(
            row=0, column=1, columnspan=2, sticky="ew", pady=4
        )
        self.browse_btn = ttk.Button(frame, command=self._browse_template)
        self.app.bind_text(self.browse_btn, "browse")
        self.browse_btn.grid(row=0, column=3, padx=(4, 0), pady=4)

    def _build_system_roi_content(self, frame):
        import json
        import os

        tk.Label(
            frame,
            text=self.app._t("setup_roi.description") if hasattr(self.app, "_t") else "Quản lý Vùng Quét Hệ Thống (System ROIs)",
            font=UIStyleV2.FONT_SMALL,
            fg=UIStyleV2.TEXT_MUTED,
            bg=UIStyleV2.THEME_BG_APP
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        roi_keys = ["combo_bar", "self_stats", "minimap"]

        for idx, key in enumerate(roi_keys):
            row = idx + 1
            lbl_text = self.app._t(f"setup_roi.{key}") if hasattr(self.app, "_t") else key.replace("_", " ").title()
            tk.Label(frame, text=lbl_text, bg=UIStyleV2.THEME_BG_APP, fg=UIStyleV2.TEXT_PRIMARY).grid(row=row, column=0, sticky="w", pady=4)

            val_var = tk.StringVar()
            cfg = self.app.state_controller.hunt_cfg
            rois = cfg.get("rois", {})
            current = rois.get(key, [])
            val_var.set(str(current) if current else "Not set")

            tk.Entry(frame, textvariable=val_var, state="readonly", width=25, bg=UIStyleV2.BG_ELEVATED, fg=UIStyleV2.TEXT_MUTED, relief="flat").grid(row=row, column=1, sticky="ew", padx=10, pady=4)

            def _make_on_draw(k=key, v=val_var):
                def _draw():
                    from ui.helpers.capture_helper import CaptureHelper
                    def _on_drawn(region):
                        if region:
                            v.set(str(list(region)))

                            if "rois" not in self.app.state_controller.hunt_cfg:
                                self.app.state_controller.hunt_cfg["rois"] = {}
                            self.app.state_controller.hunt_cfg["rois"][k] = list(region)

                            # Atomic save
                            cfg_path = getattr(self.app.state_controller, "config_file", "config/hunt_config.json")
                            tmp_path = cfg_path + ".tmp"
                            try:
                                with open(tmp_path, "w", encoding="utf-8") as f:
                                    json.dump(self.app.state_controller.hunt_cfg, f, indent=4)
                                os.replace(tmp_path, cfg_path)
                            except Exception as e:
                                print(f"Failed atomic save: {e}")

                    CaptureHelper.start_region_selection(self, _on_drawn)
                return _draw

            btn_draw = tk.Button(
                frame,
                text=self.app._t("setup_roi.draw") if hasattr(self.app, "_t") else "Vẽ lại",
                command=_make_on_draw(),
                bg=UIStyleV2.BG_ELEVATED,
                fg=UIStyleV2.ACCENT_BLUE,
                relief="flat"
            )
            btn_draw.grid(row=row, column=2, sticky="e", pady=4)

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

        # Section 5: System ROI Manager (Task 8)
        self.roi_group, self.roi_visible, self.roi_toggle = (
            self._build_collapsible_group(
                4, "setup_system_roi", "setup_system_roi_desc", self._build_system_roi_content
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
                self.app.state_controller.ui_vars['setup_template'].set(path)
            self.browse_btn.state(["!disabled"])

        self.after(50, open_dialog)



    def _on_global_hotkey_toggle(self):
        if hasattr(self.app, "_on_global_hotkey_toggle"):
            self.app._on_global_hotkey_toggle()

    def _update_setup_visibility(self):
        # All groups are always visible now since we only have advanced mode.
        self.adv_group.grid()
        self.window_group.grid()
