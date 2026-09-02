import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.tabs.hunt_tab import HuntTab

class MockApp:
    def __getattr__(self, name):
        # Fallback for all other mock methods/properties
        if name.startswith('_on_'):
            return MagicMock()
        return MagicMock()

    def __init__(self, root):
        self.hunt_cfg = {}
        self.active_target_status_frame = MagicMock()
        self.monster_frame = MagicMock()
        self.active_target_frame = MagicMock()
        self.monster_tree = MagicMock()
        self.monsters = []
        self.skill_slot_count = 0

        # TK variables required by hunt_tab
        self.hunt_status = tk.StringVar(value="idle")
        self.target_status = tk.StringVar(value="")
        self.target_hp_var = tk.DoubleVar(value=0.0)
        self.last_target_time = tk.StringVar(value="")
        self.last_skill_used = tk.StringVar(value="")
        self.hunt_target_info = tk.StringVar(value="")
        self.hunt_target_hp = tk.StringVar(value="")
        self.hunt_mode_var = tk.StringVar(value="beginner")
        self.target_key_var = tk.StringVar(value="TAB")
        self.attack_press_var = tk.StringVar(value="60")
        self.target_cycle_var = tk.StringVar(value="0.2")
        self.search_interval_var = tk.StringVar(value="0.25")
        self.attack_interval_var = tk.StringVar(value="0.15")
        self.lost_timeout_var = tk.StringVar(value="1.2")
        self.attack_duration_var = tk.StringVar(value="1.5")
        self.template_var = tk.StringVar(value="")
        self.reg_l = tk.StringVar()
        self.reg_t = tk.StringVar()
        self.reg_w = tk.StringVar()
        self.reg_h = tk.StringVar()
        self.bring_front_var = tk.BooleanVar(value=False)
        self.rotation_mode_var = tk.StringVar(value="sequence")
        self.rotation_desc_var = tk.StringVar(value="")

        self.is_hunting = False

        self.root = root

    def _t(self, key, *args, **kwargs):
        return key

    def _create_icon_button(self, *args, **kwargs):
        return tk.Button(self.root)

    def _create_tooltip(self, *args, **kwargs):
        pass

@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk cannot initialize in this environment: {exc}")
    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def hunt_tab(tk_root):
    app = MockApp(tk_root)
    # mock get_icon and create_icon_button to prevent PIL/image loading issues
    app.get_icon = MagicMock(return_value=None)

    # Needs to mock UI.FONT_SECTION etc if not defined properly in headless

    tab = HuntTab(tk_root, app)
    return tab

def test_hunt_tab_horizontal_layout(hunt_tab):
    hunt_tab.update_idletasks()

    col_0_config = hunt_tab.columnconfigure(0)
    col_1_config = hunt_tab.columnconfigure(1)

    # ensure minsize constraint is removed or reasonably small
    # For a 1366px screen, two cols of 776px = 1552px which is too large
    # The requirement is to eliminate the minsize=776.
    assert int(col_0_config.get('minsize', 0)) < 776, f"Unexpected column 0 config: {col_0_config}"
    assert int(col_1_config.get('minsize', 0)) < 776, f"Unexpected column 1 config: {col_1_config}"

    # ensure they are weighted evenly
    assert int(col_0_config.get('weight', 0)) > 0, f"Unexpected column 0 config: {col_0_config}"
    assert col_0_config.get('weight') == col_1_config.get('weight'), (
        f"Column weights differ: col_0={col_0_config}, col_1={col_1_config}"
    )
