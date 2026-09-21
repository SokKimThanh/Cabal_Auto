import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.dialogs.icon_picker import IconPickerWindow

class DummyIconHelper:
    def __init__(self):
        self.icon_map = {
            "save": ("save", "💾"),
            "delete": ("delete", "🗑️"),
            "add": ("add", "➕")
        }
    def get_icon(self, name, fallback, size):
        return fallback

@pytest.fixture
def icon_picker_dialog():
    root = tk.Tk()

    # Mock icon helper
    import ui.dialogs.icon_picker
    ui.dialogs.icon_picker.get_icon_helper = MagicMock(return_value=DummyIconHelper())

    on_select_mock = MagicMock()
    dialog = IconPickerWindow(root, on_select_mock)

    yield dialog, on_select_mock

    dialog.destroy()
    root.destroy()

def test_icon_picker_search_debounce(icon_picker_dialog):
    dialog, _ = icon_picker_dialog

    # Simulate typing in search box
    dialog.search_var.set("save")

    assert dialog._search_after_id is not None

    # Trigger after immediately for testing
    dialog.after_cancel(dialog._search_after_id)
    dialog._render_grid()

    # Should only show 'save' icon
    children = dialog.scrollable_frame.winfo_children()
    # 1 child frame for 'save' icon
    assert len(children) == 1

    # Check if callback is called on select
    dialog._on_icon_click("save")
    dialog.on_select.assert_called_once_with("save")
