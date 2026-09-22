import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.events.event_bus import EventBus, SkillStatsUpdatedEvent
import time

class SkillStatsPanel(ResponsiveGridBase):
    MODULE_NAME = "skill_stats_panel"
    SCREEN_NAME = "main"

    def __init__(self, parent, app, scale_factor=1.0, hunt_tab=None):
        super().__init__(parent, bg=UI.BG_BASE)
        self.app = app
        self.scale_factor = scale_factor
        self.hunt_tab = hunt_tab
        self._last_update_time = 0
        self._build_ui()
        self._bind_events()

    def _bind_events(self):
        EventBus.bind(SkillStatsUpdatedEvent, self._on_stats_updated)

    def destroy(self):
        EventBus.unbind(SkillStatsUpdatedEvent, self._on_stats_updated)
        super().destroy()

    def _on_stats_updated(self, event: SkillStatsUpdatedEvent):
        # Throttle updates to 1s
        now = time.time()
        if now - self._last_update_time < 1.0:
            return
        self._last_update_time = now

        def do_update():
            if not self.winfo_exists():
                return

            # Clear treeview
            for item in self.skill_stats_tree.get_children():
                self.skill_stats_tree.delete(item)

            # Take up to 50 items
            stats_list = list(event.stats.items())[:50]

            for i, (skill_name, data) in enumerate(stats_list):
                casts = data.get("cast_count", 0)
                last_cast = f"{data.get('last_cast', 0):.1f}s"
                cooldown = f"{data.get('cooldown', 0):.1f}s"

                success_rate = data.get("success_rate", 0)
                success_str = f"{success_rate:5.1f}%"

                # Tag logic
                tag = "striped_even" if i % 2 == 0 else "striped_odd"
                if success_rate >= 90:
                    tag = "excellent"
                elif success_rate >= 70:
                    tag = "good"
                elif success_rate > 0:
                    tag = "poor"

                self.skill_stats_tree.insert(
                    "",
                    "end",
                    values=(skill_name, casts, last_cast, cooldown, success_str),
                    tags=(tag,)
                )

        self.after(0, do_update)

    def _scale_font(self, base_size: int) -> int:
        return max(8, int(base_size * self.scale_factor))

    def _build_ui(self):
        # We need a Label/Header for the Panel since we removed ttk.LabelFrame
        header_label = tk.Label(
            self.get_content_frame(),
            text="📈 Skill Performance",
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY,
            font=UI.get_font("title", weight="bold"),
            anchor="w"
        )
        header_label.pack(fill="x", padx=UI.SPACE_MD, pady=(UI.SPACE_MD, 0))

        # Container for treeview to add padding
        tree_container = tk.Frame(self.get_content_frame(), bg=UI.BG_SURFACE)
        tree_container.pack(fill="both", expand=True, padx=UI.SPACE_LG, pady=UI.SPACE_LG)

        stats_columns = ("skill", "casts", "last_cast", "cooldown", "success")
        self.skill_stats_tree = ttk.Treeview(
            tree_container,
            columns=stats_columns,
            show="headings",

        )
        stats_headings = {
            "skill": ("skill_name_col", int(120 * self.scale_factor)),
            "casts": ("cast_count_col", int(60 * self.scale_factor)),
            "last_cast": ("last_cast_col", int(90 * self.scale_factor)),
            "cooldown": ("cooldown_col", int(80 * self.scale_factor)),
            "success": ("success_rate_col", int(80 * self.scale_factor)),
        }
        if hasattr(self.app, "bind_text"):
            class TreeviewHeadingBinder:
                def __init__(self, tree, column):
                    self.tree = tree
                    self.column = column
                def set_text(self, text):
                    try:
                        self.tree.heading(self.column, text=text)
                    except Exception:
                        pass

            for col, (i18n_key, width) in stats_headings.items():
                self.app.bind_text(TreeviewHeadingBinder(self.skill_stats_tree, col), i18n_key)
                self.skill_stats_tree.column(
                    col, width=width, anchor="center", stretch=(col == "skill")
                )
        else:
            for col, (i18n_key, width) in stats_headings.items():
                self.skill_stats_tree.heading(col, text=self.app._t(i18n_key))
                self.skill_stats_tree.column(
                    col, width=width, anchor="center", stretch=(col == "skill")
                )

        stats_scroll = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.skill_stats_tree.yview,
        )
        self.skill_stats_tree.config(yscrollcommand=stats_scroll.set)
        self.skill_stats_tree.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")

        # Set mono font for the treeview columns
        style = ttk.Style()
        mono_font = UI.resolve_font_family("mono")
        style.configure("Mono.Treeview", font=(mono_font, self._scale_font(10)))
        self.skill_stats_tree.configure(style="Mono.Treeview")

        self.skill_stats_tree.tag_configure(
            "striped_even", background=UI.BG_ELEVATED, foreground=UI.TEXT_PRIMARY
        )
        self.skill_stats_tree.tag_configure(
            "striped_odd", background=UI.BG_BASE, foreground=UI.TEXT_PRIMARY
        )
        self.skill_stats_tree.tag_configure("excellent", foreground=UI.ACCENT_GREEN)
        self.skill_stats_tree.tag_configure("good", foreground=UI.ACCENT_AMBER)
        self.skill_stats_tree.tag_configure("poor", foreground=UI.DANGER)

        if getattr(self, "hunt_tab", None):
            for prop in ["target_image_label", "target_name_label", "status_label",
                         "target_level_label", "target_hp_label", "target_def_label",
                         "hp_canvas", "hp_percent_label", "recovery_frame", "hp_bg", "hp_fill", "hp_text",
                         "hunt_status_badge", "hunt_status_label", "skill_stats_tree"]:
                if hasattr(self.app, prop):
                    setattr(self.hunt_tab, prop, getattr(self.app, prop))

