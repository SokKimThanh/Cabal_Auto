import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from ui.helpers import UIHelper

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.features.monsters.monster_repo import get_target_monster_info
from ui.panels.skill_panel import SkillPanel
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class HuntTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()









    def _show_monster_context_menu(self, event):
        """Show rotation actions while preserving an existing multi-selection."""
        listbox = event.widget
        index = listbox.nearest(event.y)
        if index < 0 or index >= listbox.size():
            return
        if index not in listbox.curselection():
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            listbox.activate(index)
        self.app.monster_context_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _select_all_monsters(self, _event=None):
        """Select every configured rotation row for bulk deletion."""
        if hasattr(self.app, "monster_rotation_listbox") and self.app.monster_rotation_listbox.size():
            self.app.monster_rotation_listbox.selection_set(0, tk.END)
        return "break"


    def _build_ui(self):
        """Streamlined Hunt tab with only essential controls.

        Window selection moved to topbar for quick access via combobox.
        Beginner-friendly: Monster rotation → Skill slots → Quick actions
        """

        # Initialize mode var for compatibility (actual mode selector is in Setup tab)
        self.app.state_controller.set_ui_var('hunt_mode', self.app.state_controller.get_hunt_config_value("ui_mode", "beginner"))

        # Initialize vars for compatibility with hunt loop (values read from hunt_cfg)
        self.app.state_controller.set_ui_var('target_key', str(self.app.state_controller.get_hunt_config_value("target_key", "TAB")))
        # attack_keys removed: per-skill keys from skill_slots are used instead
        self.app.state_controller.set_ui_var('attack_press', str(self.app.state_controller.get_hunt_config_value("attack_press_ms", 60)))
        self.app.state_controller.set_ui_var('target_cycle', str(self.app.state_controller.get_hunt_config_value("target_cycle_delay", 0.2)))
        self.app.state_controller.set_ui_var('search_interval', str(self.app.state_controller.get_hunt_config_value("search_interval", 0.25)))
        self.app.state_controller.set_ui_var('attack_interval', str(self.app.state_controller.get_hunt_config_value("attack_interval", 0.15)))
        self.app.state_controller.set_ui_var('lost_timeout', str(self.app.state_controller.get_hunt_config_value("lost_timeout_sec", 1.2)))
        self.app.state_controller.set_ui_var('attack_duration', str(self.app.state_controller.get_hunt_config_value("attack_min_duration_sec", 1.5)))
        self.app.state_controller.set_ui_var('template', str(self.app.state_controller.get_hunt_config_value("template_path", "assets/images/target_frame.png")))

        region = self.app.state_controller.get_hunt_config_value("region") or ["", "", "", ""]
        self.app.state_controller.ui_vars['reg_l'].set(str(region[0]) if region[0] != "" else "")
        self.app.state_controller.ui_vars['reg_t'].set(str(region[1]) if region[1] != "" else "")
        self.app.state_controller.ui_vars['reg_w'].set(str(region[2]) if region[2] != "" else "")
        self.app.state_controller.ui_vars['reg_h'].set(str(region[3]) if region[3] != "" else "")

        self.app.state_controller.set_ui_var('bring_front', bool(self.app.state_controller.get_hunt_config_value("bring_to_front_each_cycle", False)))

        # Layout: 4-Panel Workspace Redesign (PanedWindow Version Task 10)

        try:
            scale_factor = (
                getattr(self, "tk", None)
                and getattr(self, "tk", None).call("tk", "scaling") * 72 / 100.0
            )
            if scale_factor is None:
                scale_factor = 1.0
        except Exception:
            scale_factor = 1.0

        # Main static container for the entire tab
        self.main_container = tk.Frame(self, bg=UI.BG_BASE)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # We need a style for paned window to ensure background matches
        style = ttk.Style()
        style.configure('TPanedwindow', background=UI.BG_BASE)

        # Left Column Container (~58%)
        self.left_scroll_container = ResponsiveGridBase(self.paned_window, bg=UI.BG_BASE)
        self.left_col_frame = self.left_scroll_container.get_content_frame()
        self.paned_window.add(self.left_scroll_container, weight=58)

        # Right Column Container (~42%)
        self.right_scroll_container = ResponsiveGridBase(self.paned_window, bg=UI.BG_BASE)
        self.right_col_frame = self.right_scroll_container.get_content_frame()
        self.paned_window.add(self.right_scroll_container, weight=42)

        # Stack panels inside the columns
        from ui.panels.monster_target_panel import MonsterTargetPanel
        self.monster_target_panel = MonsterTargetPanel(
            self.left_col_frame,
            self.app,
            scale_factor,
            hunt_tab=self,
        )
        self.monster_target_panel.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(0, UI.SPACE_MD))

        from ui.panels.skill_panel import SkillPanel
        self.skill_panel_controller = SkillPanel(self.left_col_frame, self.app.state_controller, scale_factor, hunt_tab=self)
        # Note: SkillPanel handles its own packing internally in some implementations,
        # but normally it needs to be packed if it's just a frame.
        if isinstance(self.skill_panel_controller, tk.Widget):
            self.skill_panel_controller.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Debug Vision Action Bar
        self.debug_action_frame = tk.Frame(self.left_col_frame, bg=UI.BG_BASE)
        self.debug_action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(UI.SPACE_MD, 0))

        from ui.components.vision_snapshot_debugger import VisionSnapshotDebugger
        self.vision_debugger = VisionSnapshotDebugger(self.app)

        from ui.components.icon_button import create_icon_button
        self.btn_debug_vision = create_icon_button(
            self.debug_action_frame,
            icon_name="search",
            text=self.app._t("vision_debugger.button", default="Debug Vision"),
            command=self.vision_debugger.open_debugger,
            button_type="neutral"
        )
        self.btn_debug_vision.pack(side=tk.RIGHT)

        from ui.panels.target_status_panel import TargetStatusPanel
        self.target_status_panel = TargetStatusPanel(self.right_col_frame, self.app, scale_factor, hunt_tab=self)
        self.target_status_panel.pack(side=tk.TOP, fill=tk.BOTH, pady=(0, UI.SPACE_MD))

        from ui.panels.skill_stats_panel import SkillStatsPanel
        self.skill_stats_panel = SkillStatsPanel(self.right_col_frame, self.app, scale_factor, hunt_tab=self)
        self.skill_stats_panel.pack(side=tk.TOP, fill=tk.BOTH)
