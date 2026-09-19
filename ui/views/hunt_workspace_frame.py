import tkinter as tk
from tkinter import ttk
from ui.tabs.hunt_tab import HuntTab


class HuntWorkspaceFrame(ttk.Frame):
    MODULE_NAME = "hunt_workspace_frame"
    SCREEN_NAME = "main"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.hunt_tab = HuntTab(self, app)
        self.hunt_tab.pack(fill="both", expand=True)

        # Temporary backward compatibility mappings for external references
        self.app.btn_move_up = getattr(self.app, "btn_move_up", None)
        self.app.btn_move_down = getattr(self.app, "btn_move_down", None)

    def on_view_shown(self):
        # Resume any polling if needed
        pass

    def on_view_hidden(self):
        # Pause any polling if needed
        pass
