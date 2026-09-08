import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.base.responsive_grid_base import ResponsiveGridBase

class SkillStatsPanel(ResponsiveGridBase):
    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        super().__init__(parent, bg=UI.BG_BASE)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._build_ui()

    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))

    def _build_ui(self):
        # We need a Label/Header for the Panel since we removed ttk.LabelFrame
        header_label = tk.Label(
            self.get_content_frame(),
            text="📈 Skill Performance",
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_HEADER,
            anchor="w"
        )
        header_label.pack(fill="x", padx=UI.SPACE_MD, pady=(UI.SPACE_MD, 0))

        # Container for treeview to add padding
        tree_container = tk.Frame(self.get_content_frame(), bg=UI.BG_SURFACE)
        tree_container.pack(fill="both", expand=True, padx=UI.SPACE_LG, pady=UI.SPACE_LG)

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

        stats_scroll = ttk.Scrollbar(
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

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label", "skill_stats_tree"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))

