import pytest
import tkinter as tk
from ui.components.icon_form_component import IconFormComponent

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_icon_form_component_initialization(root):
    form = IconFormComponent(root)
    assert form is not None
    assert isinstance(form, IconFormComponent)

def test_icon_form_get_set_data(root):
    form = IconFormComponent(root)

    test_data = {
        "name": "Test Name",
        "icon_key": "test_key",
        "category": "Test Cat",
        "fallback_emoji": "😃",
        "tooltip_key": "test_tooltip",
        "filepath": "test_path.png",
        "tooltip_en": "",
        "tooltip_vi": ""
    }

    form.set_form_data(test_data)
    result = form.get_form_data()

    assert result["name"] == "Test Name"
    assert result["icon_key"] == "test_key"
    assert result["filepath"] == "test_path.png"

def test_icon_form_states(root):
    form = IconFormComponent(root)

    form.enter_view_mode()
    assert str(form.entry_name.cget("state")) == "disabled"
    assert str(form.entry_icon_key.cget("state")) == "disabled" or str(form.entry_name.cget("state")) == "disabled"

    form.enter_add_mode()
    assert str(form.entry_name.cget("state")) == "normal"
    assert str(form.entry_icon_key.cget("state")) == "normal" or str(form.entry_name.cget("state")) == "normal"

    form.enter_edit_mode()
    assert str(form.entry_name.cget("state")) == "normal"
    assert str(form.entry_icon_key.cget("state")) == "disabled" or str(form.entry_name.cget("state")) == "disabled"
