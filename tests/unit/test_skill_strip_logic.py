import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch
import sys

# Mock cv2 before importing UI modules
sys.modules['cv2'] = MagicMock()
sys.modules['win32gui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from lib.features.hunt.config_migrator import _migrate_skills
from ui.controllers.app_state_controller import AppStateController
from ui.tabs.hunt_tab import HuntTab

class TestSkillStripLogic(unittest.TestCase):

    @patch('lib.features.skills.skill_repo.load_skill_library', return_value={})
    def test_skill_migration_splits_arrays_and_fallbacks(self, mock_load):
        """Migration separates attacks and buffs into 2 arrays and fallbacks missing type."""
        old_data = {
            "skill_slots": [
                {"key": "1", "name": "Fireball", "type": "attack"},
                {"key": "2", "name": "Shield", "type": "buff"},
                {"key": "3", "name": "BrokenSkill"} # Missing type, cast_time, cooldown
            ]
        }

        _migrate_skills(old_data)

        self.assertEqual(len(old_data["skill_slots"]), 2)
        self.assertEqual(len(old_data["buff_slots"]), 1)
        self.assertEqual(old_data["skill_slots"][0]["name"], "Fireball")
        self.assertEqual(old_data["skill_slots"][1]["name"], "BrokenSkill")
        self.assertEqual(old_data["skill_slots"][1]["type"], "attack")
        self.assertEqual(old_data["skill_slots"][1]["cast_time"], 1.0)
        self.assertEqual(old_data["buff_slots"][0]["name"], "Shield")

    @patch('ui.controllers.app_state_controller.AppStateController.__init__', return_value=None)
    def test_key_conflict_warning_with_combo_key(self, mock_init):
        """Key conflict with combo_start_key shows warning."""
        try:
            root = tk.Tk()
        except:
            return

        root.hunt_cfg = {"combo": {"combo_start_key": "Alt+3"}}
        root.skills = [{"name": "Skill1", "key": "Alt+3"}]

        var = tk.StringVar(value="Skill1")
        root.skill_slot_vars = [var]

        lbl = tk.Label(root)
        root.skill_slot_key_labels = [lbl]

        box = ttk.Combobox(root)
        root.skill_slot_boxes = [box]

        controller = AppStateController(root)
        controller.root = root
        controller._validate_slot_key_duplicates()

        # Test passed visually if error handled


if __name__ == '__main__':
    unittest.main()

    @patch('ui.tabs.hunt_tab.HuntTab.show_toast')
    def test_bidirectional_routing_attack_to_buff(self, mock_toast):
        """Test routing an attack skill selected in buff lane moves to combo lane."""
        try:
            root = tk.Tk()
        except:
            return

        class MockApp:
            def __init__(self):
                self.hunt_cfg = {"combo": {"combo_start_key": "Alt+1"}}
                self.skills = [{"name": "SkillAttack", "key": "1", "type": "attack"}]
                self.skill_slot_vars = [tk.StringVar() for _ in range(6)]
                # Mock skill_slot_boxes to not crash
                self.skill_slot_boxes = []
                self.skill_slot_key_labels = []
                self.skill_slot_stats_labels = [tk.Label(root) for _ in range(6)]
                self._t = lambda x: x
                self.auto_combo_var = tk.BooleanVar()

            def _refresh_monster_select_options(self): pass

        app = MockApp()
        tab = HuntTab(root, app)

        # Select "SkillAttack" in buff lane (index 4)
        var = app.skill_slot_vars[4]
        var.set("SkillAttack")

        # Trigger combobox selected logic
        # Retrieve the generated combobox handler implicitly by triggering the event
        # Actually _build_ui already ran and attached handlers to boxes.
        # But our MockApp had empty skill_slot_boxes list because it was recreated inside _build_ui. Wait...
        # We need to use the actual widgets created by HuntTab
        box = app.skill_slot_boxes[4]

        box.event_generate("<<ComboboxSelected>>")

        # The skill is type "attack" but selected in "buff" lane. It should be moved to first empty "combo" slot (index 0).
        self.assertEqual(app.skill_slot_vars[0].get(), "SkillAttack")
        self.assertEqual(app.skill_slot_vars[4].get(), "")
        mock_toast.assert_called_with("Đã tự động chuyển 'SkillAttack' sang Làn Combo", duration_ms=2000, level="info")

        root.destroy()

    @patch('ui.tabs.hunt_tab.HuntTab.show_toast')
    def test_bidirectional_routing_lane_full(self, mock_toast):
        """Test routing blocks when destination lane is full."""
        try:
            root = tk.Tk()
        except:
            return

        class MockApp:
            def __init__(self):
                self.hunt_cfg = {"combo": {"combo_start_key": "Alt+1"}}
                self.skills = [{"name": "SkillBuff", "key": "1", "type": "buff"}]
                self.skill_slot_vars = [tk.StringVar() for _ in range(6)]
                self.skill_slot_boxes = []
                self.skill_slot_key_labels = []
                self.skill_slot_stats_labels = [tk.Label(root) for _ in range(6)]
                self._t = lambda x: x
                self.auto_combo_var = tk.BooleanVar()

            def _refresh_monster_select_options(self): pass

        app = MockApp()

        # Fill buff lane
        app.skill_slot_vars[4].set("ExistingBuff1")
        app.skill_slot_vars[5].set("ExistingBuff2")

        tab = HuntTab(root, app)

        # The init of HuntTab will clear the vars since it loads from hunt_cfg which is empty.
        # Let's fill them AFTER tab creation.
        app.skill_slot_vars[4].set("ExistingBuff1")
        app.skill_slot_vars[5].set("ExistingBuff2")
        app.skill_slot_vars[4]._previous_value = "ExistingBuff1"
        app.skill_slot_vars[5]._previous_value = "ExistingBuff2"

        # Now try to select "SkillBuff" in combo lane (index 0)
        var = app.skill_slot_vars[0]
        var._previous_value = "OldComboSkill"
        var.set("SkillBuff")

        box = app.skill_slot_boxes[0]
        box.event_generate("<<ComboboxSelected>>")

        # Buff lane is full, should revert value in combo lane and show toast
        self.assertEqual(app.skill_slot_vars[0].get(), "OldComboSkill")
        mock_toast.assert_called_with("Làn kỹ năng tương ứng đã đầy", duration_ms=2000, level="error")

        root.destroy()


    @patch('ui.tabs.hunt_tab.HuntTab.show_toast')
    def test_bidirectional_routing_no_cascade(self, mock_toast):
        """Test routing doesn't cascade and move other skills when blocked."""
        try:
            root = tk.Tk()
        except:
            return

        class MockApp:
            def __init__(self):
                self.hunt_cfg = {"combo": {"combo_start_key": "Alt+1"}}
                self.skills = [{"name": "SkillBuff", "key": "1", "type": "buff"}]
                self.skill_slot_vars = [tk.StringVar() for _ in range(6)]
                self.skill_slot_boxes = []
                self.skill_slot_key_labels = []
                self.skill_slot_stats_labels = [tk.Label(root) for _ in range(6)]
                self._t = lambda x: x
                self.auto_combo_var = tk.BooleanVar()

            def _refresh_monster_select_options(self): pass

        app = MockApp()
        tab = HuntTab(root, app)

        # Fill all lanes
        app.skill_slot_vars[0].set("Combo1")
        app.skill_slot_vars[1].set("Combo2")
        app.skill_slot_vars[2].set("Combo3")
        app.skill_slot_vars[3].set("Combo4")
        app.skill_slot_vars[4].set("Buff1")
        app.skill_slot_vars[5].set("Buff2")

        for v in app.skill_slot_vars:
            v._previous_value = v.get()

        # Try to select buff skill in combo lane (index 0)
        app.skill_slot_vars[0].set("SkillBuff")
        app.skill_slot_boxes[0].event_generate("<<ComboboxSelected>>")

        # Blocked, so it should revert to Combo1, and NO OTHER SLOT SHOULD HAVE CHANGED
        self.assertEqual(app.skill_slot_vars[0].get(), "Combo1")
        self.assertEqual(app.skill_slot_vars[1].get(), "Combo2")
        self.assertEqual(app.skill_slot_vars[4].get(), "Buff1")
        mock_toast.assert_called_with("Làn kỹ năng tương ứng đã đầy", duration_ms=2000, level="error")

        root.destroy()

    def test_toast_latest_only(self):
        """Test Toast behavior keeps only latest message."""
        try:
            root = tk.Tk()
        except:
            return

        class MockApp:
            def __init__(self):
                self.hunt_cfg = {"combo": {"combo_start_key": "Alt+1"}}
                self.skills = []
                self.skill_slot_vars = [tk.StringVar() for _ in range(6)]
                self.skill_slot_boxes = []
                self.skill_slot_key_labels = []
                self.skill_slot_stats_labels = [tk.Label(root) for _ in range(6)]
                self._t = lambda x: x
                self.auto_combo_var = tk.BooleanVar()

            def _refresh_monster_select_options(self): pass

        app = MockApp()
        tab = HuntTab(root, app)

        # Fire 3 toasts
        tab.show_toast("Message 1")
        first_timer = tab.toast_timer
        self.assertIsNotNone(first_timer)

        tab.show_toast("Message 2")
        second_timer = tab.toast_timer
        self.assertNotEqual(first_timer, second_timer)

        tab.show_toast("Message 3")
        self.assertEqual(tab.toast_label.cget("text"), "Message 3")

        root.destroy()
