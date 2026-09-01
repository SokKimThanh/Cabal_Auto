import tkinter as tk
from tkinter import ttk
from ui.tabs.help_tab import HelpTab

class HelpSupportFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.help_tab = HelpTab(self, app)
        self.help_tab.pack(fill="both", expand=True)

    def on_view_shown(self):
        pass

    def on_view_hidden(self):
        pass
