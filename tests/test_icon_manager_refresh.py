import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.views.icon_manager_frame import IconManagerFrame

class DummyApp:
    def __init__(self):
        self.lang = "vi"
    def _t(self, key, **kwargs):
        return key
    def i18n_t(self, key, **kwargs):
        return key
    def bind_text(self, *args, **kwargs):
        pass
    def emit_event(self, *args):
        pass

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_on_refresh_clears_selection(root):
    app = DummyApp()
    db = MagicMock()
    frame = IconManagerFrame(root, app, db)

    # Mock components to avoid deep initialization issues if any
    frame.tree_component = MagicMock()
    frame.tree_component.tree.selection.return_value = ('icon_123',)

    frame.available_elements_tree = MagicMock()
    frame.available_elements_tree.selection.return_value = ('elem_1',)

    frame.icon_form = MagicMock()
    frame.preview_component = MagicMock()
    frame.image_library = MagicMock()
    frame.usage_tree = MagicMock()

    frame.var_current_mapping_icon = tk.StringVar()
    frame.var_usage_element = tk.StringVar()
    frame.var_usage_mod = tk.StringVar()
    frame.var_usage_comp = tk.StringVar()
    frame.var_element_search = tk.StringVar()

    # Run _on_refresh
    frame._on_refresh()

    # Verify selection_remove was called with unpacked arguments
    frame.tree_component.tree.selection_remove.assert_called_with('icon_123')
    frame.available_elements_tree.selection_remove.assert_called_with('elem_1')

    # Verify focus was cleared
    frame.tree_component.tree.focus.assert_called_with('')
    frame.available_elements_tree.focus.assert_called_with('')

    # Verify _last_selected_item_id is reset
    assert frame._last_selected_item_id is None
