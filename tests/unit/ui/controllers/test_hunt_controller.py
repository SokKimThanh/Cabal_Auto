import unittest
from unittest.mock import MagicMock, patch
from lib.ui.controllers.hunt_controller import HuntController

class TestHuntController(unittest.TestCase):
    def setUp(self):
        self.state_controller = MagicMock()
        self.hunt_orchestrator = MagicMock()
        self.app_root = MagicMock()
        self.controller = HuntController(self.state_controller, self.hunt_orchestrator, self.app_root)

    @patch('lib.ui.controllers.hunt_controller.WindowSelectionService')
    @patch('lib.ui.controllers.hunt_controller.save_hunt_config')
    def test_request_start_hunt_success(self, mock_save, mock_window_service):
        self.state_controller.is_bot_running.return_value = False
        mock_window_service.validate_prerequisites.return_value = None
        self.state_controller.build_hunt_config_from_state.return_value = {"config": "test"}

        self.controller.request_start_hunt()

        self.state_controller.build_hunt_config_from_state.assert_called_once()
        mock_save.assert_called_once_with({"config": "test"})
        self.assertEqual(self.state_controller.hunt_cfg, {"config": "test"})
        self.hunt_orchestrator.start_hunt.assert_called_once_with({"config": "test"})

    def test_request_stop_hunt(self):
        self.controller.request_stop_hunt()
        self.hunt_orchestrator.stop_hunt.assert_called_once()

if __name__ == '__main__':
    unittest.main()
