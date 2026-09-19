import tkinter as tk
from tkinter import ttk
from ui.tabs.setup_tab import SetupTab


class SetupContentFrame(ttk.Frame):
    MODULE_NAME = "setup_content_frame"
    SCREEN_NAME = "main"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_tab = SetupTab(self, app)
        self.setup_tab.pack(fill="both", expand=True)

    def on_view_shown(self):
        pass

    def on_view_hidden(self):
        pass
