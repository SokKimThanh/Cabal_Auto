import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.status_badge import StatusBadge

class TargetStatusPanel(ttk.LabelFrame):
    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        padding = (int(8 * scale_factor), int(6 * scale_factor))
        super().__init__(parent, text="📊 Target Status", padding=padding)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._build_ui()

    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))

    def _build_ui(self):
        # Header Bar
        status_frame = tk.Frame(
            self,
            relief="flat",
            bd=1,
            height=32,
            bg=UI.BG_SURFACE,
        )
        status_frame.pack(fill="x", pady=(0, 4), padx=8)

        self.app.hunt_status_badge = StatusBadge(status_frame, status="waiting")
        self.app.hunt_status_badge.pack(side="left", padx=8, pady=6)

        # Keep reference for legacy code in HuntTab
        if self.hunt_tab is not None:
            self.hunt_tab.hunt_status_label = self.app.hunt_status_badge
            self.hunt_tab.hunt_status_badge = self.app.hunt_status_badge
        self.app.hunt_target_info_label = tk.Label(
            status_frame,
            textvariable=self.app.hunt_target_info,
            font=UI.FONT_LABEL,
            fg=UI.TEXT_SECONDARY,
            anchor="e",
        )
        self.app.hunt_target_info_label.pack(side="right", padx=8, pady=6)

        # ProgressBar Canvas
        self.app.hp_canvas = tk.Canvas(
            self, height=24, bg=UI.BG_SURFACE, highlightthickness=0
        )
        self.app.hp_canvas.pack(fill="x", padx=8, pady=(8, 2))

        def _on_hp_canvas_resize(event):
            width = event.width
            if hasattr(self.app, "hp_bg"):
                self.app.hp_canvas.coords(self.app.hp_bg, 0, 0, width, 24)
            if hasattr(self.app, "hp_text"):
                self.app.hp_canvas.coords(self.app.hp_text, width / 2, 12)

        self.app.hp_canvas.bind("<Configure>", _on_hp_canvas_resize)

        self.app.hp_bg = self.app.hp_canvas.create_rectangle(
            0, 0, 1, 24, fill="#1f1f1f", outline="#1f1f1f"
        )
        self.app.hp_fill = self.app.hp_canvas.create_rectangle(
            0, 0, 0, 24, fill="#f97316", outline="#f97316"
        )
        self.app.hp_text = self.app.hp_canvas.create_text(
            0, 12, text="", fill="white", anchor="center"
        )

        self.app.hp_percent_label = tk.Label(
            self, text="-", bg=UI.BG_SURFACE, fg=UI.TEXT_SECONDARY, anchor="w"
        )
        self.app.hp_percent_label.pack(fill="x", padx=8, anchor="w", pady=(0, 4))

        # Recovery Frame
        self.app.recovery_frame = tk.Frame(
            self,
            bg=UI.ACCENT_AMBER,
        )
        self.app.recovery_frame.pack_forget()

        def _on_recovery_click():
            if hasattr(self.app.hunt_tab, "_on_recovery_click"):
                self.app.hunt_tab._on_recovery_click()

        self.app.recovery_btn = tk.Button(
            self.app.recovery_frame,
            text=self.app._t("target_card.recovery_btn"),
            font=UI.FONT_BUTTON,
            bg=UI.BG_ELEVATED,
            fg=UI.TEXT_MUTED,
            relief="flat",
            command=_on_recovery_click,
        )
        self.app.recovery_btn.pack(fill="x", padx=4, pady=4)

        # Resource Bar (Mana) Placeholder
        self.resource_canvas = tk.Canvas(
            self, height=16, bg=UI.BG_SURFACE, highlightthickness=0
        )
        self.resource_canvas.pack(fill="x", padx=8, pady=(10, 2))

        def _on_mp_canvas_resize(event):
            width = event.width
            self.resource_canvas.coords(self.mp_bg, 0, 0, width, 16)

        self.resource_canvas.bind("<Configure>", _on_mp_canvas_resize)

        self.mp_bg = self.resource_canvas.create_rectangle(
            0, 0, 1, 16, fill="#1f1f1f", outline="#1f1f1f"
        )
        self.mp_fill = self.resource_canvas.create_rectangle(
            0, 0, 0, 16, fill="#3b82f6", outline="#3b82f6"
        )

        self.resource_label = tk.Label(
            self, text="- / - MP", bg=UI.BG_SURFACE, fg=UI.TEXT_SECONDARY, anchor="w"
        )
        self.resource_label.pack(fill="x", padx=8, anchor="w", pady=(0, 4))

        # Status Effects and Defense placeholders
        tk.Label(
            self, text="Status Effects:", bg=UI.BG_SURFACE, fg=UI.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", padx=8, pady=(10, 0))

        self.status_effects_frame = tk.Frame(self, bg=UI.BG_SURFACE)
        self.status_effects_frame.pack(fill="x", padx=8, pady=(4, 10))
        tk.Label(self.status_effects_frame, text="None", bg=UI.BG_SURFACE, fg=UI.TEXT_MUTED).pack(side="left")

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label", "skill_stats_tree"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))
