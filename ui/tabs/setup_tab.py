import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING, Optional

from lib.i18n import t as i18n_t, GLOBAL_NS as I18N_GLOBAL
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

    def _build_ui(self):
        # Section 1: Configuration Mode
        mode_frame = tk.LabelFrame(self, text=self._t("setup_mode"), padx=12, pady=10)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 12))

        mode_desc = tk.Label(
            mode_frame, text=self._t("setup_mode_desc"), fg="#666", font=("Arial", 9)
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
                font=("Arial", 9, "bold"),
            )
            rb.grid(row=idx + 1, column=0, sticky="w", pady=2)
            desc_label = tk.Label(
                mode_frame, text=f"  {mode_desc_text}", fg="#666", font=("Arial", 8)
            )
            desc_label.grid(row=idx + 1, column=1, sticky="w", padx=(4, 0), pady=2)

        # Section 2: Global Hotkeys
        hotkey_title = "Global Hotkeys" if self.lang == "en" else "Phím Tắt Toàn Cục"
        hotkey_frame = tk.LabelFrame(self, text=f"⌨️ {hotkey_title}", padx=12, pady=10)
        hotkey_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))

        hotkey_desc_text = (
            "Global hotkeys work even when app is minimized or not focused."
            if self.lang == "en"
            else "Phím tắt toàn cục hoạt động khi ứng dụng thu nhỏ hoặc không focus."
        )
        tk.Label(
            hotkey_frame,
            text=hotkey_desc_text,
            fg="#666",
            font=("Arial", 8),
            wraplength=500,
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_cfg = self.app.hunt_cfg.get("global_hotkeys", {})
        self.app.global_hotkey_enabled_var = tk.BooleanVar(
            value=hotkey_cfg.get("enabled", True)
        )

        enable_text = "Enable Global Hotkeys" if self.lang == "en" else "Bật phím tắt toàn cục"
        tk.Checkbutton(
            hotkey_frame,
            text=enable_text,
            variable=self.app.global_hotkey_enabled_var,
            font=("Arial", 9, "bold"),
            command=self._on_global_hotkey_toggle,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        hotkey_options = [
            "ctrl+shift+r", "ctrl+shift+s", "ctrl+alt+r", "ctrl+alt+s",
            "f9", "f10", "f11", "f12",
        ]

        # Start / Stop Hotkeys
        tk.Label(hotkey_frame, text="Start Hunt:" if self.lang == "en" else "Bắt đầu Hunt:", font=("Arial", 9)).grid(
            row=2, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_start_var = tk.StringVar(value=hotkey_cfg.get("start_key", "ctrl+shift+r"))
        ttk.Combobox(hotkey_frame, textvariable=self.app.global_hotkey_start_var, values=hotkey_options, width=15, state="readonly").grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(hotkey_frame, text="Stop Hunt:" if self.lang == "en" else "Dừng Hunt:", font=("Arial", 9)).grid(
            row=3, column=0, sticky="e", padx=(0, 8), pady=4
        )
        self.app.global_hotkey_stop_var = tk.StringVar(value=hotkey_cfg.get("stop_key", "ctrl+shift+e"))
        ttk.Combobox(hotkey_frame, textvariable=self.app.global_hotkey_stop_var, values=hotkey_options, width=15, state="readonly").grid(row=3, column=1, sticky="w", pady=4)

        # Section 3: Advanced Hunt Settings
        self.adv_frame = tk.LabelFrame(self, text=self._t("setup_advanced"), padx=12, pady=10)
        self.adv_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 12))

        tk.Label(self.adv_frame, text=self._t("target_key")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_target_key_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_key", "TAB")))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_target_key_var, width=8).grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("press_ms")).grid(row=1, column=0, sticky="e", pady=4)
        self.app.setup_press_ms_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_press_ms", 60)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_press_ms_var, width=8).grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("target_cycle")).grid(row=1, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_target_cycle_var = tk.StringVar(value=str(self.app.hunt_cfg.get("target_cycle_delay", 0.2)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_target_cycle_var, width=8).grid(row=1, column=3, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("search_interval")).grid(row=2, column=0, sticky="e", pady=4)
        self.app.setup_search_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("search_interval", 0.25)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_search_interval_var, width=8).grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("attack_interval")).grid(row=2, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_interval_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_interval", 0.15)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_attack_interval_var, width=8).grid(row=2, column=3, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("lost_timeout")).grid(row=3, column=0, sticky="e", pady=4)
        self.app.setup_lost_timeout_var = tk.StringVar(value=str(self.app.hunt_cfg.get("lost_timeout_sec", 1.2)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_lost_timeout_var, width=8).grid(row=3, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("attack_duration")).grid(row=3, column=2, sticky="e", padx=(16, 4), pady=4)
        self.app.setup_attack_duration_var = tk.StringVar(value=str(self.app.hunt_cfg.get("attack_min_duration_sec", 1.5)))
        tk.Entry(self.adv_frame, textvariable=self.app.setup_attack_duration_var, width=8).grid(row=3, column=3, sticky="w", pady=4)

        # Section 4: Window Settings
        self.window_frame = tk.LabelFrame(self, text=self._t("setup_window"), padx=12, pady=10)
        self.window_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))

        tk.Label(self.window_frame, text=self._t("template")).grid(row=0, column=0, sticky="e", pady=4)
        self.app.setup_template_var = tk.StringVar(value=str(self.app.hunt_cfg.get("template_path", "assets/images/target_frame.png")))
        tk.Entry(self.window_frame, textvariable=self.app.setup_template_var, width=40).grid(row=0, column=1, columnspan=2, sticky="w", pady=4)
        tk.Button(self.window_frame, text=self._t("browse"), command=self._browse_template).grid(row=0, column=3, padx=(4, 0), pady=4)

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
            self.adv_frame.grid_remove()
            self.window_frame.grid_remove()
        elif mode == "intermediate":
            self.adv_frame.grid()
            self.window_frame.grid_remove()
        elif mode == "advanced":
            self.adv_frame.grid()
            self.window_frame.grid()
