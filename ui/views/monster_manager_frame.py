import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle
from tkinter import ttk


class MonsterManagerFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        label = tk.Label(
            self,
            text="Monster Manager Workspace",
            font=(UIStyle.resolve_font_family("body"), 16),
        )
        label.pack(expand=True)

    def on_view_shown(self):
        pass

    def on_view_hidden(self):
        pass
