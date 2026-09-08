import tkinter as tk
from ui.components.base.responsive_grid_base import ResponsiveGridBase
from ui.components.empty_state import EmptyState
from lib.ui_style_v2 import UIStyleV2 as UIStyle


class SkillManagerFrame(ResponsiveGridBase):
    """
    Skill Manager Workspace View.
    Currently acts as a placeholder for future CRUD implementation.
    """

    def __init__(self, parent, app, **kwargs):
        # Set default background to match app
        kwargs.setdefault("bg", UIStyle.BG_BASE)
        super().__init__(parent, **kwargs)
        self.app = app

        self._build_ui()

    def _build_ui(self):
        content = self.get_content_frame()

        # Configure layout to center the empty state
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # Using standard translated strings if available, else fallback
        title_msg = "Quản lý Kỹ năng (Đang phát triển)"
        sub_msg = "Không gian này sẽ được sử dụng để phát triển chức năng quản lý thư viện kỹ năng trực tiếp trên Workspace."

        if hasattr(self.app, "_t"):
            # Attempt translations (fallback to default string if not found)
            title_msg = self.app._t("skill_manager_wip_title", fallback=title_msg)
            sub_msg = self.app._t("skill_manager_wip_sub", fallback=sub_msg)

        # Build empty state component
        self.empty_state = EmptyState(
            content,
            icon="⚔️",
            message=title_msg,
            submessage=sub_msg
        )
        # Using grid inside the content frame to center
        self.empty_state.grid(row=0, column=0, sticky="nsew", pady=40)

    def on_view_shown(self):
        """Lifecycle hook called when view becomes visible."""
        pass

    def on_view_hidden(self):
        """Lifecycle hook called when view becomes hidden."""
        pass
