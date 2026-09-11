import tkinter as tk

from ui.components.base.responsive_grid_base import ResponsiveGridBase
from lib.ui_style_v2 import UIStyleV2 as UIStyle


class IconManagerFrame(ResponsiveGridBase):
    def __init__(self, parent, app=None, *args, **kwargs):
        super().__init__(parent, app=app, bg=UIStyle.BG_BASE, *args, **kwargs)
        self.app = app
        self._setup_ui()

    def _setup_ui(self):
        content_frame = self.get_content_frame()
        # Row 0: Top Filter Bar
        # Row 1: Vùng Content chính
        # Row 2: Bottom Bar
        content_frame.grid_rowconfigure(0, weight=0)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_rowconfigure(2, weight=0)
        content_frame.grid_columnconfigure(0, weight=1)

        # 1. Top Filter Bar
        self.top_filter_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.top_filter_frame.grid(row=0, column=0, sticky="ew")
        self.top_filter_frame.grid_propagate(False)  # For visualizing

        tk.Label(self.top_filter_frame, text="Top Filter Bar Area", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(pady=20)

        # 2. Main Content (Left - Right split)
        self.main_content_frame = tk.Frame(content_frame, bg=UIStyle.BG_BASE)
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", pady=UIStyle.SPACE_MD)

        # Configure columns for split
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=0, minsize=250)  # Left Sidebar (Master List)
        self.main_content_frame.grid_columnconfigure(1, weight=1)              # Right Detail Zone

        # Left Master List Frame
        self.left_master_frame = tk.Frame(self.main_content_frame, bg=UIStyle.BG_ELEVATED)
        self.left_master_frame.grid(row=0, column=0, sticky="nsew", padx=(0, UIStyle.SPACE_SM))
        tk.Label(self.left_master_frame, text="Master List Area", bg=UIStyle.BG_ELEVATED, fg=UIStyle.TEXT_PRIMARY).pack(expand=True)

        # Right Detail Frame
        self.right_detail_frame = tk.Frame(self.main_content_frame, bg=UIStyle.BG_SURFACE)
        self.right_detail_frame.grid(row=0, column=1, sticky="nsew", padx=(UIStyle.SPACE_SM, 0))
        tk.Label(self.right_detail_frame, text="Detail & Form Area", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).pack(expand=True)

        # 3. Bottom Action Bar
        self.bottom_action_frame = tk.Frame(content_frame, bg=UIStyle.BG_SUBTLE, height=60)
        self.bottom_action_frame.grid(row=2, column=0, sticky="ew")
        self.bottom_action_frame.grid_propagate(False)
        tk.Label(self.bottom_action_frame, text="Bottom Action Bar Area", bg=UIStyle.BG_SUBTLE, fg=UIStyle.TEXT_PRIMARY).pack(pady=20)
