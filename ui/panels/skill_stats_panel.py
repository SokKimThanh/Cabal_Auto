import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI


class SkillStatsPanel(ttk.LabelFrame):
    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        padding = (int(8 * scale_factor), int(6 * scale_factor))
        super().__init__(parent, text="📈 Skill Performance", padding=padding)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._build_ui()

    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))

    def _build_ui(self):
        # Container for treeview to add padding
        tree_container = tk.Frame(self, bg=UI.BG_SURFACE)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        stats_columns = ("skill", "casts", "last_cast", "cooldown", "success")
        self.app.skill_stats_tree = ttk.Treeview(
            tree_container,
            columns=stats_columns,
            show="headings",
            height=3,
        )
        stats_headings = {
            "skill": ("skill_name_col", int(120 * self.scale_factor)),
            "casts": ("cast_count_col", int(60 * self.scale_factor)),
            "last_cast": ("last_cast_col", int(90 * self.scale_factor)),
            "cooldown": ("cooldown_col", int(80 * self.scale_factor)),
            "success": ("success_rate_col", int(80 * self.scale_factor)),
        }
        for col, (i18n_key, width) in stats_headings.items():
            self.app.skill_stats_tree.heading(col, text=self.app._t(i18n_key))
            # Let the skill name column absorb extra width on wider windows; keep the rest fixed.
            self.app.skill_stats_tree.column(
                col, width=width, anchor="center", stretch=(col == "skill")
            )

        stats_scroll = tk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.app.skill_stats_tree.yview,
        )
        self.app.skill_stats_tree.config(yscrollcommand=stats_scroll.set)
        self.app.skill_stats_tree.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")

        self.app.skill_stats_tree.tag_configure(
            "striped_even", background=UI.BG_ELEVATED, foreground=UI.TEXT_PRIMARY
        )
        self.app.skill_stats_tree.tag_configure(
            "striped_odd", background=UI.BG_BASE, foreground=UI.TEXT_PRIMARY
        )
        self.app.skill_stats_tree.tag_configure("excellent", foreground=UI.ACCENT_GREEN)
        self.app.skill_stats_tree.tag_configure("good", foreground=UI.ACCENT_AMBER)
        self.app.skill_stats_tree.tag_configure("poor", foreground=UI.DANGER)
        self.app.skill_stats_tree.tag_configure("placeholder", foreground=UI.TEXT_MUTED)

        self.app.skill_stats_tree.insert(
            "",
            "end",
            values=(self.app._t("skill_stats_empty"), "", "", "", ""),
            tags=("placeholder",),
        )

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label", "skill_stats_tree"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))

