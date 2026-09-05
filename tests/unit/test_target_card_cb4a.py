import os
import pytest
import time

pytest.importorskip("tkinter", reason="Skipping UI tests because tkinter is not available")
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

from ui.tabs.hunt_tab import HuntTab
from lib.vision.target_hp_reader import TargetHPReader

class DummyApp:
    def __init__(self):
        self.hunt_cfg = {}
        self.hunt_status = tk.StringVar()
        self.hunt_target_info = tk.StringVar()

    def _t(self, key):
        return key

    def schedule_ui_task(self, task):
        task()

    def __getattr__(self, name):
        if name.startswith('_on_') or name.startswith('_refresh_') or name.startswith('_create_') or name.startswith('_update_'):
            return lambda *args, **kwargs: tk.Label() if name.startswith('_create_') else None
        if name.endswith('_var'):
            class DummyVar(tk.Variable):
                def __init__(self, name=""):
                    self.val = ""
                    self._name = name

                def set(self, val):
                    self.val = val

                def get(self):
                    return self.val

                def trace_add(self, *args, **kwargs):
                    pass
            var = DummyVar(name=name)
            setattr(self, name, var)
            return var
        if name == "skill_slot_count":
            return 8
        if name == "combo_start_key_cmb":
            cmb = tk.Entry()
            setattr(self, name, cmb)
            return cmb
        if name == "skills":
            return []

        class MockMagic:
            def __call__(self, *args, **kwargs):
                pass
            def __getattr__(self, name):
                return MockMagic()
        return MockMagic()


class TestTargetCardCB4A(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = DummyApp()
        self.tab = HuntTab(self.root, self.app)

    def tearDown(self):
        self.root.destroy()

    @patch('database.get_monster_by_id_api')
    @patch('lib.features.monsters.monster_repo.load_monster_library', return_value={})
    def test_case_1_valid_monster(self, mock_load, mock_get):
        mock_get.return_value = {
            "id": "999",
            "name": "Dragon",
            "level": "50",
            "hp": 5000,
            "defense": 300,
            "image_path": "path/to/dragon.png"
        }

        self.tab.update_target_card("999")
        self.assertEqual(self.tab.target_name_label.cget("text"), "Dragon")
        self.assertEqual(self.tab.target_hp_label.cget("text"), "5000")
        self.assertEqual(self.tab.target_level_label.cget("text"), "50")

    @patch('database.get_monster_by_id_api', return_value=None)
    @patch('database.find_monster_by_name_api', return_value=None)
    @patch('lib.features.monsters.monster_repo.load_monster_library', return_value={})
    def test_case_2_missing_asset(self, mock_load, mock_find, mock_get):
        self.tab.update_target_card("UnknownMob")
        self.assertEqual(self.tab.target_name_label.cget("text"), "UnknownMob")
        self.assertEqual(self.tab.target_hp_label.cget("text"), "10000")
        # Should set fallback
        self.assertEqual(self.tab.target_image_label.cget("text"), "[ NO IMAGE ]")

    def test_case_3_combat_transition(self):
        self.tab.update_status("APPROACHING")
        self.assertEqual(self.tab.status_label.cget("text"), "APPROACHING")

        self.tab.update_status("ATTACKING")
        self.tab.update_hp_display(50.0)
        self.assertEqual(self.tab.status_label.cget("text"), "ATTACKING")
        self.assertEqual(self.tab.hp_progressbar.cget("value"), 50.0)

        self.tab.update_status("TARGET_DEAD")
        self.tab.update_hp_display(0.0)
        self.assertEqual(self.tab.status_label.cget("text"), "TARGET_DEAD")
        self.assertEqual(self.tab.hp_progressbar.cget("value"), 0.0)

        # Test clear target card with delay = 0
        self.tab.clear_target_card(0)
        self.assertEqual(self.tab.hp_progressbar.cget("value"), 0.0)
        self.assertEqual(self.tab.target_name_label.cget("text"), "Unknown Target")
        self.assertEqual(self.tab.status_label.cget("text"), "IDLE")

    def test_case_4_rapid_retarget_race(self):
        # We start a clear with delay
        self.tab.clear_target_card(200)

        self.assertIsNotNone(self.tab._pending_clear_id)

        # Rapid retarget before clear executes
        with patch('database.get_monster_by_id_api', return_value={
            "id": "1", "name": "Slime", "level": "1", "hp": 100, "defense": 10, "image_path": None
        }):
            self.tab.update_target_card("1")

        self.assertIsNone(getattr(self.tab, "_pending_clear_id", None))
        self.assertEqual(self.tab.target_name_label.cget("text"), "Slime")

        # We process Tkinter events
        self.root.update()

        # Wait a bit to ensure the after_cancel worked (if it didn't, the text would revert to Unknown Target)
        time.sleep(0.3)
        self.root.update()

        self.assertEqual(self.tab.target_name_label.cget("text"), "Slime")

    @patch('database.get_monster_by_id_api', return_value=None)
    @patch('database.find_monster_by_name_api', return_value=None)
    @patch('lib.features.monsters.monster_repo.load_monster_library', return_value={})
    def test_case_5_placeholder_hp(self, mock_load, mock_find, mock_get):
        from lib.features.monsters.monster_repo import get_target_monster_info
        info = get_target_monster_info("Ghost")

        self.assertEqual(info["hp"], 10000)
        self.assertTrue(info.get("is_placeholder"))

    def test_case_6_no_duplicate_hp_logic(self):
        mock_detector = MagicMock()
        mock_detector.get_hp_percentage.return_value = 75.0

        reader = TargetHPReader(mock_detector)
        frame = MagicMock()

        hp = reader.calculate_target_hp_percent(frame)
        self.assertEqual(hp, 75.0)

        mock_detector.get_hp_percentage.assert_called_once_with(frame)

if __name__ == '__main__':
    unittest.main()
