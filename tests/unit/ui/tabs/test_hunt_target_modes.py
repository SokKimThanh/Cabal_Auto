import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.tabs.hunt_tab import HuntTab

pytestmark = pytest.mark.unit


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def mock_app(root):
    app = MagicMock(spec=tk.Tk)
    app.state_controller = MagicMock()
    app.state_controller.ui_vars = {}
    app.hunt_cfg = {}
    app.click_running = False
    app.monster_rotation = []
    app._t = lambda key, **kwargs: key
    app.on_skill_slot_changed = lambda e: None
    app._clear_skill_slot = lambda v: None
    app._refresh_monster_select_options = lambda: None
    app.skill_slot_count = 4
    app._refresh_monster_rotation_list = lambda: None
    app._on_rotation_mode_changed = lambda e: None
    app._create_icon_button = lambda *args, **kwargs: tk.Button(args[0])
    app._create_tooltip = lambda *args, **kwargs: None
    return app


