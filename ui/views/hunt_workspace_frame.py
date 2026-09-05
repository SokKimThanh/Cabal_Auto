import tkinter as tk
from tkinter import ttk
from ui.tabs.hunt_tab import HuntTab


class HuntWorkspaceFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.hunt_tab = HuntTab(self, app)
        self.hunt_tab.pack(fill="both", expand=True)

    def on_view_shown(self):
        # Resume any polling if needed
        pass

    def on_view_hidden(self):
        # Pause any polling if needed
        pass
