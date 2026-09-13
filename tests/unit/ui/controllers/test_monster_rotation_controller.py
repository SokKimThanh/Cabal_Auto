import unittest
from unittest.mock import MagicMock, patch
from lib.ui.controllers.monster_rotation_controller import MonsterRotationController

class TestMonsterRotationController(unittest.TestCase):
    def setUp(self):
        self.state_controller = MagicMock()
        self.state_controller.monster_rotation = []
        self.state_controller.has_unsaved_changes = False

        self.controller = MonsterRotationController(self.state_controller)

    @patch('lib.ui.controllers.monster_rotation_controller.EventBus')
    def test_promote_detected_monster_valid(self, mock_event_bus):
        runtime_item = {
            "resolution_state": "db_match",
            "monster_id": "m123",
            "name": "Test Monster",
            "dungeon_id": "d1"
        }

        self.controller.promote_detected_monster(runtime_item)

        self.assertEqual(len(self.state_controller.monster_rotation), 1)
        self.assertEqual(self.state_controller.monster_rotation[0]["monster_id"], "m123")
        self.assertEqual(self.state_controller.monster_rotation[0]["priority"], 1)
        self.assertTrue(self.state_controller.has_unsaved_changes)
        mock_event_bus.trigger.assert_called_once()

    @patch('lib.ui.controllers.monster_rotation_controller.EventBus')
    def test_promote_detected_monster_duplicate(self, mock_event_bus):
        self.state_controller.monster_rotation = [{
            "monster_id": "m123",
            "dungeon_id": "d1",
            "priority": 1
        }]

        runtime_item = {
            "resolution_state": "db_match",
            "monster_id": "m123",
            "name": "Test Monster",
            "dungeon_id": "d1"
        }

        self.controller.promote_detected_monster(runtime_item)

        self.assertEqual(len(self.state_controller.monster_rotation), 1)
        mock_event_bus.trigger.assert_not_called()

if __name__ == '__main__':
    unittest.main()
