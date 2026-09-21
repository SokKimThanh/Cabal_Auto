import tkinter as tk
from tkinter import ttk
from ui.tabs.hunt_tab import HuntTab
from ui.components.hunt_status_ticker import HuntStatusTicker

class HuntWorkspaceFrame(ttk.Frame):
    MODULE_NAME = "hunt_workspace_frame"
    SCREEN_NAME = "main"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.hunt_tab = HuntTab(self, app)
        self.hunt_tab.pack(side=tk.TOP, fill="both", expand=True)

        self.status_ticker = HuntStatusTicker(self, app)
        self.status_ticker.pack(side=tk.BOTTOM, fill=tk.X)

        # Temporary backward compatibility mappings for external references
        self.app.btn_move_up = getattr(self.app, "btn_move_up", None)
        self.app.btn_move_down = getattr(self.app, "btn_move_down", None)

    def on_view_shown(self):
        # Resume any polling if needed
        pass

    def on_view_hidden(self):
        # Pause any polling if needed
        pass
