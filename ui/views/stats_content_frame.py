import tkinter as tk
from tkinter import ttk
from ui.tabs.stats_tab import StatsTab

class StatsContentFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.stats_tab = StatsTab(self, app)
        self.stats_tab.pack(fill="both", expand=True)

    def on_view_shown(self):
        pass

    def on_view_hidden(self):
        pass
