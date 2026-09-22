import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from ui.components.icon_button import create_icon_button, create_icon_label
from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor

class MockParent:
    def __init__(self, tk_parent):
        self.tk_parent = tk_parent
        self.MODULE_NAME = "test_module"
        self.SCREEN_NAME = "test_screen"

    def winfo_id(self):
        return self.tk_parent.winfo_id()

def test_create_icon_button_registers_element_id():
    root = tk.Tk()
    parent = MockParent(root)
    # mock the master property that tk widgets usually have
    setattr(parent, "master", root)
    # create_icon_button expects a valid tk widget as parent usually, but it looks like
    # it climbs the tree. Let's create a real frame and set the attrs on it instead.

    frame = tk.Frame(root)
    frame.MODULE_NAME = "test_module"
    frame.SCREEN_NAME = "test_screen"

    registry = UIElementRegistry.instance()
    registry.clear()

    btn = create_icon_button(
        parent=frame,
        element_id="test_btn_123",
        icon_name="settings"
    )

    elements = registry.get_all()
    assert len(elements) == 1
    assert elements[0].element_id == "test_btn_123"
    assert elements[0].element_type == "button"
    assert elements[0].module == "test_module"

    root.destroy()

def test_create_icon_label_registers_element_id():
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.MODULE_NAME = "test_module"
    frame.SCREEN_NAME = "test_screen"

    registry = UIElementRegistry.instance()
    registry.clear()

    # Needs mock image helper to avoid TclError
    with patch("ui.components.icon_button.IconHelper") as MockHelper:
        mock_helper_instance = MockHelper.return_value
        img = tk.PhotoImage(width=1, height=1)
        mock_helper_instance.get_icon.return_value = img

        lbl = create_icon_label(
            parent=frame,
            element_id="test_lbl_456",
            icon_name="info"
        )

    elements = registry.get_all()
    assert len(elements) == 1
    assert elements[0].element_id == "test_lbl_456"
    assert elements[0].element_type == "label"
    assert elements[0].module == "test_module"

    root.destroy()

def test_duplicate_registration_logs_warning_on_type_mismatch():
    import logging
    registry = UIElementRegistry.instance()
    registry.clear()

    desc1 = UIElementDescriptor("test_id", "mod", "screen", "button")
    registry.register(desc1)

    desc2 = UIElementDescriptor("test_id", "mod", "screen", "label")

    with patch.object(logging.getLogger("lib.events.ui_element_registry"), "warning") as mock_warning:
        registry.register(desc2)
        mock_warning.assert_called_once()
        assert "Type mismatch" in mock_warning.call_args[0][0]

def test_duplicate_registration_silent_on_match():
    import logging
    registry = UIElementRegistry.instance()
    registry.clear()

    desc1 = UIElementDescriptor("test_id", "mod", "screen", "button")
    registry.register(desc1)

    desc2 = UIElementDescriptor("test_id", "mod", "screen", "button")

    with patch.object(logging.getLogger("lib.events.ui_element_registry"), "warning") as mock_warning:
        registry.register(desc2)
        mock_warning.assert_not_called()
