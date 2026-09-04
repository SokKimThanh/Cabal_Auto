import pytest
import sys
from unittest.mock import MagicMock

# Inject headless mocks
sys.modules['win32gui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32ui'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()

import tkinter as tk
from ui.tabs.hunt_tab import HuntTab

@pytest.fixture
def mock_app():
    app = MagicMock()
    app.hunt_cfg = {"combo": {"enabled": False, "combo_start_key": "Alt+3"}}
    app.skills = [
        {"name": "Fireball", "cast_time": 1.2, "cooldown": 5.0},
        {"name": "Ice Lance", "cast_time": 0.8},  # Missing cooldown
        {"name": "Unknown Skill"} # Missing both
    ]
    app._t = lambda key: key
    app.skill_slot_count = 6
    # we will initialize this inside the test function after tk.Tk() is created
    return app

def test_auto_combo_state_toggle(mock_app):
    root = tk.Tk()
    mock_app.tk = root.tk
    # We must properly initialize the boolean var
    mock_app.auto_combo_var = tk.BooleanVar(value=False)

    # We must patch get_icon so it doesn't fail on HuntTab init
    mock_app.get_icon = MagicMock(return_value=None)
    mock_app.hunt_status = tk.StringVar(value="idle")
    mock_app.target_status = tk.StringVar(value="")
    mock_app.target_hp_var = tk.DoubleVar(value=0.0)
    mock_app.last_target_time = tk.StringVar(value="")
    mock_app.last_skill_used = tk.StringVar(value="")
    mock_app.hunt_target_info = tk.StringVar(value="")
    mock_app.hunt_target_hp = tk.StringVar(value="")
    mock_app.hunt_mode_var = tk.StringVar(value="beginner")
    mock_app.target_key_var = tk.StringVar(value="TAB")
    mock_app.attack_press_var = tk.StringVar(value="60")
    mock_app.target_cycle_var = tk.StringVar(value="0.2")
    mock_app.search_interval_var = tk.StringVar(value="0.25")
    mock_app.attack_interval_var = tk.StringVar(value="0.15")
    mock_app.lost_timeout_var = tk.StringVar(value="1.2")
    mock_app.attack_duration_var = tk.StringVar(value="1.5")
    mock_app.template_var = tk.StringVar(value="")
    mock_app.reg_l = tk.StringVar()
    mock_app.reg_t = tk.StringVar()
    mock_app.reg_w = tk.StringVar()
    mock_app.reg_h = tk.StringVar()
    mock_app.bring_front_var = tk.BooleanVar(value=False)
    mock_app.rotation_mode_var = tk.StringVar(value="sequence")
    mock_app.rotation_desc_var = tk.StringVar(value="")
    mock_app._create_tooltip = MagicMock()
    mock_app.monster_status_var = tk.StringVar()

    tab = HuntTab(root, mock_app)

    combo_start_key_cmb = mock_app.combo_start_key_cmb
    assert str(combo_start_key_cmb.cget("state")) == "disabled"

    for widget in tab.skill_strip_frame.winfo_children()[0].winfo_children()[0].winfo_children():
        if isinstance(widget, tk.Checkbutton):
            # The initial value was False. toggle it via UI.
            widget.invoke()
            break

    assert str(combo_start_key_cmb.cget("state")) == "normal"
    root.destroy()

def test_placeholder_fallback_full(mock_app):
    root = tk.Tk()
    mock_app.tk = root.tk
    mock_app.auto_combo_var = tk.BooleanVar(value=False)
    mock_app.get_icon = MagicMock(return_value=None)
    mock_app.hunt_status = tk.StringVar(value="idle")
    mock_app.target_status = tk.StringVar(value="")
    mock_app.target_hp_var = tk.DoubleVar(value=0.0)
    mock_app.last_target_time = tk.StringVar(value="")
    mock_app.last_skill_used = tk.StringVar(value="")
    mock_app.hunt_target_info = tk.StringVar(value="")
    mock_app.hunt_target_hp = tk.StringVar(value="")
    mock_app.hunt_mode_var = tk.StringVar(value="beginner")
    mock_app.target_key_var = tk.StringVar(value="TAB")
    mock_app.attack_press_var = tk.StringVar(value="60")
    mock_app.target_cycle_var = tk.StringVar(value="0.2")
    mock_app.search_interval_var = tk.StringVar(value="0.25")
    mock_app.attack_interval_var = tk.StringVar(value="0.15")
    mock_app.lost_timeout_var = tk.StringVar(value="1.2")
    mock_app.attack_duration_var = tk.StringVar(value="1.5")
    mock_app.template_var = tk.StringVar(value="")
    mock_app.reg_l = tk.StringVar()
    mock_app.reg_t = tk.StringVar()
    mock_app.reg_w = tk.StringVar()
    mock_app.reg_h = tk.StringVar()
    mock_app.bring_front_var = tk.BooleanVar(value=False)
    mock_app.rotation_mode_var = tk.StringVar(value="sequence")
    mock_app.rotation_desc_var = tk.StringVar(value="")
    mock_app._create_tooltip = MagicMock()
    mock_app.monster_status_var = tk.StringVar()

    tab = HuntTab(root, mock_app)

    lbl = tk.Label(root)
    tab.update_card_stats(lbl, "Unknown Skill")

    assert lbl.cget("text") == "⚡ --s | ⏳ --s"
    root.destroy()

def test_placeholder_fallback_partial(mock_app):
    root = tk.Tk()
    mock_app.tk = root.tk
    mock_app.auto_combo_var = tk.BooleanVar(value=False)
    mock_app.get_icon = MagicMock(return_value=None)
    mock_app.hunt_status = tk.StringVar(value="idle")
    mock_app.target_status = tk.StringVar(value="")
    mock_app.target_hp_var = tk.DoubleVar(value=0.0)
    mock_app.last_target_time = tk.StringVar(value="")
    mock_app.last_skill_used = tk.StringVar(value="")
    mock_app.hunt_target_info = tk.StringVar(value="")
    mock_app.hunt_target_hp = tk.StringVar(value="")
    mock_app.hunt_mode_var = tk.StringVar(value="beginner")
    mock_app.target_key_var = tk.StringVar(value="TAB")
    mock_app.attack_press_var = tk.StringVar(value="60")
    mock_app.target_cycle_var = tk.StringVar(value="0.2")
    mock_app.search_interval_var = tk.StringVar(value="0.25")
    mock_app.attack_interval_var = tk.StringVar(value="0.15")
    mock_app.lost_timeout_var = tk.StringVar(value="1.2")
    mock_app.attack_duration_var = tk.StringVar(value="1.5")
    mock_app.template_var = tk.StringVar(value="")
    mock_app.reg_l = tk.StringVar()
    mock_app.reg_t = tk.StringVar()
    mock_app.reg_w = tk.StringVar()
    mock_app.reg_h = tk.StringVar()
    mock_app.bring_front_var = tk.BooleanVar(value=False)
    mock_app.rotation_mode_var = tk.StringVar(value="sequence")
    mock_app.rotation_desc_var = tk.StringVar(value="")
    mock_app._create_tooltip = MagicMock()
    mock_app.monster_status_var = tk.StringVar()

    tab = HuntTab(root, mock_app)

    lbl = tk.Label(root)
    tab.update_card_stats(lbl, "Ice Lance")

    assert lbl.cget("text") == "⚡ 0.8s | ⏳ --s"
    root.destroy()

def test_dynamic_i18n(mock_app):
    root = tk.Tk()
    mock_app.tk = root.tk
    mock_app.auto_combo_var = tk.BooleanVar(value=False)
    mock_app.get_icon = MagicMock(return_value=None)
    mock_app.hunt_status = tk.StringVar(value="idle")
    mock_app.target_status = tk.StringVar(value="")
    mock_app.target_hp_var = tk.DoubleVar(value=0.0)
    mock_app.last_target_time = tk.StringVar(value="")
    mock_app.last_skill_used = tk.StringVar(value="")
    mock_app.hunt_target_info = tk.StringVar(value="")
    mock_app.hunt_target_hp = tk.StringVar(value="")
    mock_app.hunt_mode_var = tk.StringVar(value="beginner")
    mock_app.target_key_var = tk.StringVar(value="TAB")
    mock_app.attack_press_var = tk.StringVar(value="60")
    mock_app.target_cycle_var = tk.StringVar(value="0.2")
    mock_app.search_interval_var = tk.StringVar(value="0.25")
    mock_app.attack_interval_var = tk.StringVar(value="0.15")
    mock_app.lost_timeout_var = tk.StringVar(value="1.2")
    mock_app.attack_duration_var = tk.StringVar(value="1.5")
    mock_app.template_var = tk.StringVar(value="")
    mock_app.reg_l = tk.StringVar()
    mock_app.reg_t = tk.StringVar()
    mock_app.reg_w = tk.StringVar()
    mock_app.reg_h = tk.StringVar()
    mock_app.bring_front_var = tk.BooleanVar(value=False)
    mock_app.rotation_mode_var = tk.StringVar(value="sequence")
    mock_app.rotation_desc_var = tk.StringVar(value="")
    mock_app._create_tooltip = MagicMock()
    mock_app.monster_status_var = tk.StringVar()
    tab = HuntTab(root, mock_app)

    found_combo_lane = False
    for widget in tab.skill_strip_frame.winfo_children()[0].winfo_children()[1].winfo_children():
        for sub_widget in widget.winfo_children():
            if isinstance(sub_widget, tk.Label):
                if "skill_strip.combo_lane" in sub_widget.cget("text") or "Combo Chain" in sub_widget.cget("text"):
                    found_combo_lane = True

    assert found_combo_lane
    root.destroy()

def test_legacy_buttons_removed(mock_app):
    root = tk.Tk()
    mock_app.tk = root.tk
    mock_app.auto_combo_var = tk.BooleanVar(value=False)
    mock_app.get_icon = MagicMock(return_value=None)
    mock_app.hunt_status = tk.StringVar(value="idle")
    mock_app.target_status = tk.StringVar(value="")
    mock_app.target_hp_var = tk.DoubleVar(value=0.0)
    mock_app.last_target_time = tk.StringVar(value="")
    mock_app.last_skill_used = tk.StringVar(value="")
    mock_app.hunt_target_info = tk.StringVar(value="")
    mock_app.hunt_target_hp = tk.StringVar(value="")
    mock_app.hunt_mode_var = tk.StringVar(value="beginner")
    mock_app.target_key_var = tk.StringVar(value="TAB")
    mock_app.attack_press_var = tk.StringVar(value="60")
    mock_app.target_cycle_var = tk.StringVar(value="0.2")
    mock_app.search_interval_var = tk.StringVar(value="0.25")
    mock_app.attack_interval_var = tk.StringVar(value="0.15")
    mock_app.lost_timeout_var = tk.StringVar(value="1.2")
    mock_app.attack_duration_var = tk.StringVar(value="1.5")
    mock_app.template_var = tk.StringVar(value="")
    mock_app.reg_l = tk.StringVar()
    mock_app.reg_t = tk.StringVar()
    mock_app.reg_w = tk.StringVar()
    mock_app.reg_h = tk.StringVar()
    mock_app.bring_front_var = tk.BooleanVar(value=False)
    mock_app.rotation_mode_var = tk.StringVar(value="sequence")
    mock_app.rotation_desc_var = tk.StringVar(value="")
    mock_app._create_tooltip = MagicMock()
    mock_app.monster_status_var = tk.StringVar()
    tab = HuntTab(root, mock_app)

    for widget in tab.skill_strip_frame.winfo_children():
        for sub_widget in widget.winfo_children():
            try:
                assert "skill_slot_clear" not in str(sub_widget.cget("text"))
            except tk.TclError:
                pass
    root.destroy()
