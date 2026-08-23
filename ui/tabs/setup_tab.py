import tkinter as tk
from tkinter import ttk
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None
from ui.components import create_icon_button as _create_icon_btn_component
from lib.ui_style import UIStyle as UI

class SetupTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        pass
