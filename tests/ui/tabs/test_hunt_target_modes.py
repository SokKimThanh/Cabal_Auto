import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.tabs.hunt_tab import HuntTab

@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def mock_app(root):
    app = MagicMock(spec=tk.Tk)
    app.hunt_cfg = {}
    app.click_running = False
    app.monster_rotation = []
    app._t = lambda key: key
    app.hunt_status = tk.StringVar()
    app.hunt_target_info = tk.StringVar()
    app.monster_estimate_var = tk.StringVar()
    app.training_mode_status_var = tk.StringVar()
    app._on_monster_add_smart = lambda: None
    app._on_monster_move_up = lambda: None
    app._on_monster_move_down = lambda: None
    app._on_monster_delete_from_list = lambda: None
    app.on_skill_slot_changed = lambda e: None
    app._clear_skill_slot = lambda v: None
    app._refresh_monster_select_options = lambda: None
    app.skill_slot_count = 4
    app._refresh_monster_rotation_list = lambda: None
    app._on_rotation_mode_changed = lambda e: None
    # Mocks for methods
    app._create_icon_button = lambda *args, **kwargs: tk.Button(args[0])
    app._create_tooltip = lambda *args, **kwargs: None
    return app

def test_target_policy_vars(root, mock_app):
    # App now initializes target_policy_var itself? Wait, it's done in HuntTab
    hunt_tab = HuntTab(root, mock_app)
    assert hasattr(mock_app, "target_policy_var")
    assert mock_app.target_policy_var.get() == "configured_only"
    assert hunt_tab.configured_container.winfo_manager() == "pack"
    assert hunt_tab.detected_container.winfo_manager() == ""
    assert hunt_tab.any_target_container.winfo_manager() == ""

def test_target_policy_changes(root, mock_app):
    hunt_tab = HuntTab(root, mock_app)
    mock_app.target_policy_var.set("all_resolved")
    assert mock_app.hunt_cfg["target_policy"] == "all_resolved"
    assert mock_app.has_unsaved_changes is True

def test_hunt_running_locks_policy(root, mock_app):
    hunt_tab = HuntTab(root, mock_app)
    mock_app.click_running = True
    mock_app.target_policy_var.set("any_target")
    # Should revert to configured_only since hunt is running
    assert mock_app.target_policy_var.get() == "configured_only"
