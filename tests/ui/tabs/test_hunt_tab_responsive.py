import pytest
import tkinter as tk
from unittest.mock import MagicMock
from ui.tabs.hunt_tab import HuntTab


class MockApp:
    def __getattr__(self, name):
        if name.startswith('_on_'):
            return MagicMock()
        return MagicMock()

    def __init__(self, root):
        self.hunt_cfg = {}
        self.active_target_status_frame = MagicMock()
        self.monster_frame = MagicMock()
        self.skill_stats_frame = MagicMock()
        self.monster_tree = MagicMock()
        self.monsters = []
        self.skill_slot_count = 0

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
    app.get_icon = MagicMock(return_value=None)
    tab = HuntTab(tk_root, app)
    return tab


def test_hunt_tab_responsive_wide(hunt_tab):
    hunt_tab.update_idletasks()

    # Simulate a wide window > 850
    class MockEvent:
        width = 1000

    hunt_tab._on_resize(MockEvent())
    hunt_tab.update_idletasks()

    # Needs to wait for debounce to apply layout
    hunt_tab.after(150, lambda: hunt_tab.quit())
    hunt_tab.mainloop()

    assert hunt_tab._current_layout == "wide"
    assert hunt_tab.app.monster_frame.grid_info()['row'] == 0
    assert hunt_tab.app.monster_frame.grid_info()['column'] == 0
    assert hunt_tab.app.active_target_status_frame.grid_info()['row'] == 0
    assert hunt_tab.app.active_target_status_frame.grid_info()['column'] == 1
    assert hunt_tab.skill_strip_frame.grid_info()['row'] == 1


def test_hunt_tab_responsive_narrow(hunt_tab):
    hunt_tab.update_idletasks()

    # Simulate a narrow window < 850
    class MockEvent:
        width = 600

    hunt_tab._on_resize(MockEvent())
    hunt_tab.update_idletasks()

    # Needs to wait for debounce to apply layout
    hunt_tab.after(150, lambda: hunt_tab.quit())
    hunt_tab.mainloop()

    assert hunt_tab._current_layout == "narrow"
    assert hunt_tab.app.active_target_status_frame.grid_info()['row'] == 0
    assert hunt_tab.app.active_target_status_frame.grid_info()['column'] == 0
    assert hunt_tab.app.active_target_status_frame.grid_info()['columnspan'] == 2
    assert hunt_tab.app.monster_frame.grid_info()['row'] == 1
    assert hunt_tab.app.monster_frame.grid_info()['column'] == 0
    assert hunt_tab.app.monster_frame.grid_info()['columnspan'] == 2
    assert hunt_tab.skill_strip_frame.grid_info()['row'] == 2
