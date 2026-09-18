import pytest
import tkinter as tk
from ui.components.icon_preview_component import IconPreviewComponent

class MockApp:
    def __init__(self):
        self.lang = "vi"

    def t(self, key, default=""):
        return default

class MockIconHelper:
    def evaluate_icon_status(self, data):
        return "GREEN" if data.get("filepath") else "RED"

def test_icon_preview_component():
    root = tk.Tk()
    app = MockApp()
    icon_helper = MockIconHelper()

    comp = IconPreviewComponent(root, app=app, icon_helper=icon_helper)

    # render empty
    comp.render({})
    assert comp.empty_preview.winfo_viewable() == 1 or comp.empty_preview.grid_info() != {}
    assert comp.lbl_preview.grid_info() == {}

    # render dummy
    comp.render({"icon_key": "dummy_id", "fallback_emoji": "❓", "filepath": ""})
    assert comp.lbl_preview.grid_info() != {}

    root.destroy()
