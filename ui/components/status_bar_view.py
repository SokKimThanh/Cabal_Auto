import tkinter as tk
from lib.ui_style_v2 import UIStyleV2 as UI

class StatusBarView(tk.Frame):
    def __init__(self, parent, app, *args, **kwargs):
        super().__init__(parent, bg=UI.BG_SUBTLE, bd=0, *args, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Left Section: DB Status
        status_var = None
        if hasattr(self.app, 'state_controller') and self.app.state_controller:
            status_var = self.app.state_controller.ui_vars.get('db_status')

        if not status_var:
            status_var = tk.StringVar(value="Đang kết nối...")

        self.db_status_label = tk.Label(
            self,
            textvariable=status_var,
            anchor="w",
            padx=12,
            font=UI.FONT_SMALL,
            bg=UI.BG_SUBTLE,
            fg=UI.TEXT_MUTED,
            relief="flat",
        )
        self.db_status_label.pack(side="left", fill="y")

        # Right Section: Version and Status
        self.right_status_label = tk.Label(
            self,
            text="v2.1.0 · CSDL: ✓ · 0 lỗi",
            anchor="e",
            padx=12,
            font=UI.FONT_SMALL,
            bg=UI.BG_SUBTLE,
            fg=UI.TEXT_MUTED,
            relief="flat",
        )
        self.right_status_label.pack(side="right", fill="y")
