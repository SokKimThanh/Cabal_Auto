import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

from lib.features.hotkey.hotkey_validator import validate_hotkey_no_conflict
from lib.features.hunt.config_migrator import migrate_hunt_config
from ui.tabs.hunt_tab import HuntTab

class TestCB3BValidationSuite(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Requires active display or xvfb to run Tkinter tests: {exc}")
        self.root.withdraw()

    def tearDown(self):
        if getattr(self, "root", None) is not None:
            self.root.destroy()

    def test_hotkey_conflict(self):
        """Verify conflict validation blocks incompatible combos"""
        skill_slots = [
            {"name": "Skill1", "key": "q"},
            {"name": "Skill2", "key": "w"},
        ]

        # Should pass (no conflict)
        is_valid, msg = validate_hotkey_no_conflict("Alt+1", skill_slots, {})
        self.assertTrue(is_valid)

        # Should pass (case insensitive config)
        is_valid, msg = validate_hotkey_no_conflict("Q", skill_slots, {})
        self.assertFalse(is_valid)
        self.assertIn("q", msg.lower())

        # Should fail (q already used)
        is_valid, msg = validate_hotkey_no_conflict("q", skill_slots, {})
        self.assertFalse(is_valid)
        self.assertIn("q", msg.lower())

        # Should fail (global hotkey conflict)
        is_valid, msg = validate_hotkey_no_conflict("f8", [], {"pause": "f8"})
        self.assertFalse(is_valid)
        self.assertIn("f8", msg.lower())

    @patch("lib.features.skills.skill_repo.load_skill_library")
    def test_legacy_config_migration(self, mock_load_skill):
        """Test precedence rules for unclassified entries"""
        mock_load_skill.return_value = {
            "s1": {"name": "Mana Heal", "type": "buff"},
            "s2": {"name": "Sword Slash", "type": "attack"}
        }

        legacy_cfg = {
            "skill_slots": [
                {"name": "Fireball", "type": "attack", "key": "1"},  # Has type
                {"name": "Mana Heal", "key": "2"},  # Missing type, in catalog
                {"name": "Unknown Skill", "key": "3"},  # Missing type, not in catalog
            ]
        }
        migrated = migrate_hunt_config(legacy_cfg)

        # Assert Fireball in skill_slots
        self.assertTrue(any(s["name"] == "Fireball" for s in migrated["skill_slots"]))

        # Assert Mana Heal in buff_slots
        self.assertTrue(any(b["name"] == "Mana Heal" for b in migrated["buff_slots"]))
        self.assertEqual(migrated["buff_slots"][0]["type"], "buff")

        # Assert Unknown Skill in skill_slots (default)
        self.assertTrue(any(s["name"] == "Unknown Skill" for s in migrated["skill_slots"]))

        unknown_skill = next(s for s in migrated["skill_slots"] if s["name"] == "Unknown Skill")
        self.assertEqual(unknown_skill["type"], "attack")

    def test_save_reload_round_trip(self):
        """Verify skill_slots/buff_slots don't cross-contaminate"""
        # Mocking the UI data collection logic for round-trip validation
        mock_app = MagicMock()
        mock_app.skills = [
            {"name": "Attack1", "type": "attack", "key": "1"},
            {"name": "Buff1", "type": "buff", "key": "2"}
        ]

        mock_app.hunt_cfg = {
            "buff_slots": [{"name": "Buff1", "duration_sec": 450}]
        }

        var_attack = tk.StringVar(value="Attack1")
        var_empty1 = tk.StringVar(value="")
        var_empty2 = tk.StringVar(value="")
        var_empty3 = tk.StringVar(value="")
        var_buff = tk.StringVar(value="Buff1")
        var_empty4 = tk.StringVar(value="")

        # Combo lane: 0, 1, 2, 3
        # Buff lane: 4, 5, 6, 7
        mock_app.skill_slot_vars = [
            var_attack, var_empty1, var_empty2, var_empty3,
            var_buff, var_empty4
        ]

        mock_app.skill_slot_duration_vars = [
            tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(),
            tk.StringVar(value="450"), tk.StringVar()
        ]

        # Import directly from the file to avoid importing cv2 and GUI
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_gui", "app_gui.py")
        app_gui_module = importlib.util.module_from_spec(spec)
        # Mock transitive dependencies that app_gui uses globally
        import sys
        sys.modules['cv2'] = MagicMock()
        sys.modules['win32gui'] = MagicMock()
        sys.modules['lib.vision.vision_engine'] = MagicMock()
        sys.modules['lib.system.bot_manager'] = MagicMock()
        sys.modules['ui.controllers.overlay_controller'] = MagicMock()
        sys.modules['lib.features.hunt.hunt_runner'] = MagicMock()
        spec.loader.exec_module(app_gui_module)

        # Extract the standalone _collect_skill_slots method to test it isolated
        skills, buffs = app_gui_module.App._collect_skill_slots(mock_app)

        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["name"], "Attack1")
        self.assertEqual(skills[0]["type"], "attack")

        self.assertEqual(len(buffs), 1)
        self.assertEqual(buffs[0]["name"], "Buff1")
        self.assertEqual(buffs[0]["type"], "buff")
        self.assertEqual(buffs[0]["duration_sec"], 450)

    def test_i18n_round_trip(self):
        """Verify all lane headers/labels translate correctly"""
        mock_app = MagicMock()

        def mock_t(key):
            translations = {
                "skill_strip.combo_lane": "Chuỗi Combo",
                "skill_strip.buff_lane": "Làn Buff",
            }
            return translations.get(key, key)

        mock_app._t = mock_t
        mock_app.hunt_cfg = {"combo": {}}
        mock_app.skill_slot_count = 8
        mock_app.skills = []

        tab = HuntTab(self.root, mock_app)
        tab.pack()

        # Force a draw
        self.root.update()

        # Find the titles
        def find_labels(widget, text_match, found=None):
            if found is None:
                found = []
            if isinstance(widget, tk.Label):
                if text_match in widget.cget("text"):
                    found.append(widget)
            for child in widget.winfo_children():
                find_labels(child, text_match, found)
            return found

        combo_labels = find_labels(tab, "Chuỗi Combo")
        buff_labels = find_labels(tab, "Làn Buff")

        self.assertTrue(len(combo_labels) > 0)
        self.assertTrue(len(buff_labels) > 0)

if __name__ == '__main__':
    unittest.main()
