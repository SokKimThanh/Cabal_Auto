import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.panels.skill_panel import SkillPanel

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def app_state_mock():
    app_state = MagicMock()
    app_state._t.side_effect = lambda key, **kwargs: f"translated_{key}"
    app_state.hunt_cfg = {"combo": {"enabled": False}}
    app_state.register_callback = MagicMock()
    app_state._current_class_id = 1  # Fix for sqlite binding MagicMock
    return app_state

def test_skill_panel_toggle_combo(root, app_state_mock):
    # Instantiate the SkillPanel
    panel = SkillPanel(root, app_state_mock)

    # Check initial values from the build toggle section
    # Notice that `auto_combo_var` initializes to `True` implicitly during backwards compat build.
    assert panel.widgets["auto_combo_var"].get() is True

    # Act: Perform click equivalent
    panel.btn_toggle_combo.invoke()

    # Verify underlying boolean var changed
    assert panel.widgets["auto_combo_var"].get() is False

    # Verify hunt_cfg state was written correctly
    assert app_state_mock.hunt_cfg["combo"]["enabled"] is False

    # Verify button visual translation updated
    assert panel.btn_toggle_combo.cget("text") == "translated_skill_panel.combo_start"

    # Act: Click again
    panel.btn_toggle_combo.invoke()

    # Verify true
    assert panel.widgets["auto_combo_var"].get() is True
    assert app_state_mock.hunt_cfg["combo"]["enabled"] is True
    assert panel.btn_toggle_combo.cget("text") == "translated_skill_panel.combo_stop"

    panel.destroy()
