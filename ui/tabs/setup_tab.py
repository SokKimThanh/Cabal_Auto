from tkinter import ttk
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class SetupTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        pass
