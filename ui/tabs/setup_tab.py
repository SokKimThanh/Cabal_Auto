import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING, Optional

from lib.i18n import t as i18n_t, GLOBAL_NS as I18N_GLOBAL
from lib.ui_style import UIStyle
from ui.helpers.tooltip import attach_i18n_tooltip

if TYPE_CHECKING:
    from app_gui import App


class SetupTab(tk.Frame):
    def __init__(self, parent: ttk.Notebook, app: "App", *args, **kwargs):
        super().__init__(parent, padx=12, pady=12, *args, **kwargs)
        self.parent = parent
        self.app = app
        self.lang = getattr(app, "lang", "vi")

        self._build_ui()
        self._update_setup_visibility()

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, "_t"):
            return self.app._t(key, **kwargs)
        return i18n_t(key, ns=I18N_GLOBAL, lang=self.lang, **kwargs)


    def _build_collapsible_group(self, row, title_key, desc_key, content_builder):
        group_frame = tk.Frame(self)
        group_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        group_frame.grid_columnconfigure(0, weight=1)

        is_visible_var = tk.BooleanVar(value=False)
        header_frame = tk.Frame(group_frame)
        header_frame.grid(row=0, column=0, sticky="nsew")
        header_frame.grid_columnconfigure(0, weight=1)

        btn_text_var = tk.StringVar(value=f"▶ {self._t(title_key)}")

        content_frame = tk.LabelFrame(group_frame, padx=12, pady=10)


        def toggle(event=None):
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

        # Make the entire header frame clickable
        header_frame.bind("<Button-1>", toggle)
        header_frame.configure(cursor="hand2")

        btn = tk.Label(header_frame, textvariable=btn_text_var, font=UIStyle.FONT_SECTION, fg=UIStyle.COLOR_PRIMARY, cursor="hand2")
        btn.bind("<Button-1>", toggle)
        btn.pack(side="left")

        if desc_key:
            desc_label = tk.Label(header_frame, text=self._t(desc_key), fg=UIStyle.COLOR_MUTED, font=UIStyle.FONT_SMALL, cursor="hand2")
            desc_label.bind("<Button-1>", toggle)
            desc_label.pack(side="left", padx=(8, 0))

        content_builder(content_frame)

        # Store these for _update_setup_visibility to show/hide the entire group
        return group_frame, is_visible_var, toggle

    def _build_hotkeys_content(self, frame):
        hotkey_cfg = self.app.hunt_cfg.get("global_hotkeys", {})
        self.app.global_hotkey_enabled_var = tk.BooleanVar(value=hotkey_cfg.get("enabled", True))

        enable_text = "Enable Global Hotkeys" if self.lang == "en" else "Bật phím tắt toàn cục"
        tk.Checkbutton(
            frame, text=enable_text, variable=self.app.global_hotkey_enabled_var,
            font=UIStyle.FONT_LABEL, command=self._on_global_hotkey_toggle,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_options = [
            "ctrl+shift+r", "ctrl+shift+e", "ctrl+shift+s", "ctrl+alt+r", "ctrl+alt+s",
            "f9", "f10", "f11", "f12",
        ]

        tk.Label(frame, text="Start Hunt:" if self.lang == "en" else "Bắt đầu Hunt:", font=UIStyle.FONT_TEXT).grid(
            row=1, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_start_var = tk.StringVar(value=hotkey_cfg.get("start_key", "ctrl+shift+r"))
        ttk.Combobox(frame, textvariable=self.app.global_hotkey_start_var, values=hotkey_options, width=15, state="readonly").grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(frame, text="Stop Hunt:" if self.lang == "en" else "Dừng Hunt:", font=UIStyle.FONT_TEXT).grid(
            row=2, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_stop_var = tk.StringVar(value=hotkey_cfg.get("stop_key", "ctrl+shift+e"))
        ttk.Combobox(frame, textvariable=self.app.global_hotkey_stop_var, values=hotkey_options, width=15, state="readonly").grid(row=2, column=1, sticky="w", pady=4)


    def _validate_numeric(self, action, value_if_allowed):
        if action == '1': # Insertion
            if value_if_allowed:
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
        return True

    def _build_advanced_content(self, frame):

        tk.Label(frame, text=self._t("target_key")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_target_key_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_key", "TAB")))
        tk.Entry(frame, textvariable=self.app.setup_target_key_var, width=8).grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(frame, text=self._t("press_ms")).grid(row=1, column=0, sticky="e", pady=4)
        self.app.setup_press_ms_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_press_ms", 60)))
        tk.Entry(frame, textvariable=self.app.setup_press_ms_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(frame, text=self._t("target_cycle")).grid(row=1, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_target_cycle_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_cycle_delay", 0.2)))
        tk.Entry(frame, textvariable=self.app.setup_target_cycle_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=1, column=3, sticky="w", pady=4)

        tk.Label(frame, text=self._t("search_interval")).grid(row=2, column=0, sticky="e", pady=4)
        self.app.setup_search_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("search_interval", 0.25)))
        tk.Entry(frame, textvariable=self.app.setup_search_interval_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(frame, text=self._t("attack_interval")).grid(row=2, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_interval", 0.15)))
        tk.Entry(frame, textvariable=self.app.setup_attack_interval_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=2, column=3, sticky="w", pady=4)

        tk.Label(frame, text=self._t("lost_timeout")).grid(row=3, column=0, sticky="e", pady=4)
        self.app.setup_lost_timeout_var = tk.StringVar(value=str(self.app.hunt_cfg.get("lost_timeout_sec", 1.2)))
        tk.Entry(frame, textvariable=self.app.setup_lost_timeout_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(frame, text=self._t("attack_duration")).grid(row=3, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_duration_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_min_duration_sec", 1.5)))
        tk.Entry(frame, textvariable=self.app.setup_attack_duration_var, width=8, validate="key", validatecommand=(self.register(self._validate_numeric), "%d", "%P")).grid(row=3, column=3, sticky="w", pady=4)

    def _build_window_content(self, frame):
        tk.Label(frame, text=self._t("template")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_template_var = tk.StringVar(value=str(self.app.hunt_cfg.get("template_path", "assets/images/target_frame.png")))
        tk.Entry(frame, textvariable=self.app.setup_template_var, width=30).grid(row=0, column=1, columnspan=2, sticky="w", pady=4)
        tk.Button(frame, text=self._t("browse"), command=self._browse_template).grid(row=0, column=3, padx=(4, 0), pady=4)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Section 1: Configuration Mode
        mode_frame = tk.LabelFrame(self, text=self._t("setup_mode"), padx=12, pady=10)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 12))

        mode_desc = tk.Label(
            mode_frame, text=self._t("setup_mode_desc"), fg=UIStyle.COLOR_MUTED, font=UIStyle.FONT_TEXT
        )
        mode_desc.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        current_mode = self.app.hunt_cfg.get("ui_mode", "beginner")
        self.app.setup_mode_var = tk.StringVar(value=current_mode)

        modes = [
            ("beginner", self._t("mode_beginner"), self._t("mode_beginner_desc")),
            ("intermediate", self._t("mode_intermediate"), self._t("mode_intermediate_desc")),
            ("advanced", self._t("mode_advanced"), self._t("mode_advanced_desc")),
        ]

        for idx, (mode_val, mode_label, mode_desc_text) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=mode_label,
                variable=self.app.setup_mode_var,
                value=mode_val,
                command=self._on_setup_mode_changed,
                font=UIStyle.FONT_LABEL,
            )
            rb.grid(row=idx + 1, column=0, sticky="w", pady=2)
            desc_label = tk.Label(
                mode_frame, text=f"  {mode_desc_text}", fg=UIStyle.COLOR_MUTED, font=UIStyle.FONT_SMALL
            )
            desc_label.grid(row=idx + 1, column=1, sticky="w", padx=(4, 0), pady=2)

        # Section 2: Global Hotkeys
        self.hotkey_group, self.hotkey_visible, self.hotkey_toggle = self._build_collapsible_group(
            1, "setup_hotkeys", "setup_hotkeys_desc", self._build_hotkeys_content
        )

        # Section 3: Advanced Hunt Settings
        self.adv_group, self.adv_visible, self.adv_toggle = self._build_collapsible_group(
            2, "setup_advanced", "setup_advanced_desc", self._build_advanced_content
        )

        # Section 4: Window Settings
        self.window_group, self.window_visible, self.window_toggle = self._build_collapsible_group(
            3, "setup_window", "setup_window_desc", self._build_window_content
        )
    def _browse_template(self):
        path = filedialog.askopenfilename(
            title="Select template image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if path:
            self.app.setup_template_var.set(path)

    def _on_setup_mode_changed(self):
        if hasattr(self.app, "_on_setup_mode_changed"):
            self.app._on_setup_mode_changed()
        self._update_setup_visibility()

    def _on_global_hotkey_toggle(self):
        if hasattr(self.app, "_on_global_hotkey_toggle"):
            self.app._on_global_hotkey_toggle()


    def _update_setup_visibility(self):
        mode = self.app.setup_mode_var.get() if hasattr(self.app, "setup_mode_var") else "beginner"
        if mode == "beginner":
            self.adv_group.grid_remove()
            self.window_group.grid_remove()
        elif mode == "intermediate":
            self.adv_group.grid()
            self.window_group.grid_remove()
        elif mode == "advanced":
            self.adv_group.grid()
            self.window_group.grid()
