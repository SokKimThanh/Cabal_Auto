import tkinter as tk
from lib.ui_style import UIStyle as UI

class ActivityLogsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=UI.BG_DEFAULT)
        self.app = app

        # Header
        self.header_frame = tk.Frame(self, bg=UI.BG_SECTION, height=36)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            self.header_frame,
            text=self.app._t("logs_title"),
            bg=UI.BG_SECTION,
            fg=UI.COLOR_TEXT,
            font=UI.FONT_SECTION
        )
        self.title_label.pack(side="left", padx=12)

        self.clear_btn = tk.Button(
            self.header_frame,
            text=self.app._t("logs_clear"),
            bg=UI.BG_SECTION,
            fg=UI.COLOR_TEXT,
            font=UI.FONT_SMALL,
            relief="flat",
            activebackground=UI.COLOR_INFO,
            activeforeground=UI.BG_DEFAULT,
            cursor="hand2",
            command=self.clear
        )
        self.clear_btn.pack(side="right", padx=12)

        # Content container
        self.content_frame = tk.Frame(self, bg=UI.BG_PANEL)
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Text widget
        self.text_widget = tk.Text(
            self.content_frame,
            bg=UI.BG_PANEL, fg=UI.COLOR_TEXT,
            font=UI.FONT_SMALL, wrap="word", state="disabled",
            relief="flat", padx=12, pady=12
        )
        self.text_widget.pack(fill="both", expand=True, side="left")

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.content_frame, command=self.text_widget.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

    def append_message(self, message: str):
        """Appends a message to the text widget and auto-scrolls to the bottom."""
        self.text_widget.config(state="normal")
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.config(state="disabled")
        self.text_widget.see(tk.END)

    def trim_to_limit(self, limit: int = 1000):
        """Trims the text widget to keep only the latest `limit` lines."""
        lines = int(self.text_widget.index('end-1c').split('.')[0])
        if lines > limit:
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", f"{lines - limit + 1}.0")
            self.text_widget.config(state="disabled")

    def clear(self):
        """Clears all text from the text widget."""
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state="disabled")
