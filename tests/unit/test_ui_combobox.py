import tkinter as tk
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_tkinter(monkeypatch):
    # Dummy mock để tránh Tkinter cần display server
    class MockTk(tk.Tk):
        def __init__(self, *args, **kwargs):
            pass
        def bind(self, *args, **kwargs):
            pass
    monkeypatch.setattr(tk, "Tk", MockTk)
    class MockStringVar:
        def __init__(self, *args, **kwargs):
            self.val = ''
            self.traces = []
        def get(self): return self.val
        def set(self, v):
            self.val = v
            for t in self.traces: t()
            self.val = ''
        def trace_add(self, mode, cb): self.traces.append(cb)
        monkeypatch.setattr(tk, "StringVar", MockStringVar)

class MockApp:
    def __init__(self):
        self.lang = "vi"
    def i18n_t(self, key, **kwargs):
        if key == "btn_add": return "Add"
        if key == "btn_edit": return "Edit"
        if key == "btn_delete": return "Delete"
        if key == "btn_refresh": return "Refresh"
        if key == "btn_sync": return "Sync"
        if key == "btn_save": return "Save"
        if key == "btn_cancel": return "Cancel"
        return key
    def bind_translation(self, widget, key, **kwargs):
        pass

@patch('ui.components.base.responsive_grid_base.ResponsiveGridBase._on_enter')
@patch('ui.components.base.responsive_grid_base.ResponsiveGridBase._on_leave')
@patch('ui.views.icon_manager_frame.get_db')
@patch('ui.views.icon_manager_frame.IconService')
def test_i18n_validation(mock_icon_service, mock_get_db, m1, m2):
    try:
        from ui.views.icon_manager_frame import IconManagerFrame
        root = tk.Tk()
        app = MockApp()

        # Mock _REGISTRY
        with patch('lib.i18n._REGISTRY', {'ns1': {'vi': {'valid_key': 'Dịch'}}}), \
             patch('lib.i18n.t', side_effect=lambda k, default=None, **kw: "Dịch" if k == "valid_key" else default):

            frame = IconManagerFrame(root, app=app)

            # Check initial load keys
            assert 'valid_key' in frame._available_keys

            # Test valid key
            frame.var_tooltip_key.set('valid_key')
            # Trigger trace manually for tests
            frame._validate_tooltip_key()
            assert frame.lbl_tooltip_warning.cget('text') == ""

            # Test invalid key
            frame.var_tooltip_key.set('invalid_key')
            frame._validate_tooltip_key()
            assert frame.lbl_tooltip_warning.cget('text') == "⚠️"

            # Test autocomplete filter
            frame.entry_tooltip.get = MagicMock(return_value='val')
            frame.entry_tooltip.delete = MagicMock()

            event = MagicMock()
            event.keysym = 'a'
            event.char = 'a'
            frame._autocomplete_tooltip(event)

            # should filter down to 'valid_key'
            assert 'valid_key' in frame.entry_tooltip['values']

        root.destroy()
    except tk.TclError:
        pytest.skip("No display server found for Tkinter")
