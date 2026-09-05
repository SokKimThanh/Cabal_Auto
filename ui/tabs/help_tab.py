import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle


class HelpTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(
            self,
            text="Help & Support",
            font=(UIStyle.resolve_font_family("display"), 16, "bold"),
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
            bg=UIStyle.THEME_BG_APP,
            fg=UIStyle.THEME_TEXT_PRIMARY,
            font=(UIStyle.resolve_font_family("body"), 10),
            wrap="word",
            state="normal",
            relief="flat",
            padx=8,
            pady=8,
        )
        text.insert("1.0", content)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)
