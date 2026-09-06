import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI


class HelpTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(
            self,
            text="Help & Support",
            font=UI.FONT_TITLE,
        )
        title.pack(anchor="w", pady=(0, 16))

        content = """1. Configuration Mode
- Beginner: Basic setup for simple hunting.
- Intermediate: Access to advanced timings.
- Advanced: Full control over internal parameters.

2. Global Hotkeys
- Start Hunt: Starts the bot processing.
- Stop Hunt: Stops the bot safely.

3. Logs and Stats
- Logs: Shows detailed activity and debug information.
- Stats: Displays real-time hunting statistics."""

        text = tk.Text(
            self,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY,
            font=UI.FONT_BODY,
            wrap="word",
            state="normal",
            relief="flat",
            padx=8,
            pady=8,
        )
        text.insert("1.0", content)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)
