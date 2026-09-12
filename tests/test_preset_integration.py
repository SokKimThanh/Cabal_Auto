from lib.features.skills.skill_preset_service import SkillPresetService
import unittest
from unittest.mock import MagicMock, patch

from lib.features.skills.skill_preset_service import SkillPresetService
from ui.controllers.app_state_controller import AppStateController


class TestPresetIntegration(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()

        # Patch tkinter Variables used in UI State initialization
        self.patcher_string = patch('tkinter.StringVar')
        self.patcher_bool = patch('tkinter.BooleanVar')
        self.patcher_string.start()
        self.patcher_bool.start()

        self.app_state = AppStateController(self.root)
        self.service = SkillPresetService()

    def tearDown(self):
        self.patcher_string.stop()
        self.patcher_bool.stop()

    def tearDown(self):
        pass

    @patch("lib.features.skills.skill_preset_service.SkillPresetService.apply_preset")
    def test_load_preset_for_class(self, mock_apply):
        mock_apply.return_value = {
            "success": True,
            "preset": {"is_default": True},
            "skill_slots": {"attack_combo": [1, 2], "buff_lane": [3]},
        }

        self.app_state.load_preset_for_class(1, 100)

        self.assertEqual(self.app_state._active_preset_id, 100)
        self.assertEqual(self.app_state._preset_mode, "default")
        self.assertEqual(len(self.app_state.skill_slots["attack_combo"]), 2)
        self.assertEqual(self.app_state.skill_slots["attack_combo"][0]["skill_id"], 1)

    def test_set_skill_slot_switches_to_custom(self):
        self.app_state._preset_mode = "default"
        self.app_state.skill_slots = {"attack_combo": []}

        self.app_state.set_skill_slot("attack_combo", 0, 999)

        self.assertEqual(self.app_state._preset_mode, "custom")
        self.assertEqual(self.app_state.skill_slots["attack_combo"][0]["skill_id"], 999)

    @patch(
        "lib.features.skills.skill_preset_service.SkillPresetService.create_custom_preset"
    )
    def test_save_custom_preset_creates_new(self, mock_create):
        mock_create.return_value = {"success": True, "preset_id": 200}

        self.app_state._preset_mode = "custom"
        self.app_state._current_class_id = 1
        self.app_state.skill_slots = {"attack_combo": [{"skill_id": 5}]}

        self.app_state.save_custom_preset("My Custom Preset")

        mock_create.assert_called_once()
        self.assertEqual(self.app_state._active_preset_id, 200)


if __name__ == "__main__":
    unittest.main()
