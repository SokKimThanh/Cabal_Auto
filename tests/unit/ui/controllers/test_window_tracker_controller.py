import pytest
from unittest.mock import MagicMock, patch
from ui.controllers.window_tracker_controller import WindowTrackerController

def test_tracker_lifecycle_start_stop():
    parent = MagicMock()
    controller = WindowTrackerController(parent)

    with patch('ui.controllers.window_tracker_controller.WindowTracker') as mock_tracker_class:
        mock_tracker_instance = MagicMock()
        mock_tracker_class.return_value = mock_tracker_instance

        # Test start
        controller.start(123)
        mock_tracker_class.assert_called_once_with(target_hwnd=123, poll_rate=60)
        mock_tracker_instance.start.assert_called_once()
        assert controller.get_tracker() == mock_tracker_instance

        # Test stop
        controller.stop()
        mock_tracker_instance.stop.assert_called_once()
        assert controller.get_tracker() is None

def test_tracker_duplicate_start():
    parent = MagicMock()
    controller = WindowTrackerController(parent)

    with patch('ui.controllers.window_tracker_controller.WindowTracker') as mock_tracker_class:
        first_tracker_instance = MagicMock()
        first_tracker_instance.is_running.return_value = True
        second_tracker_instance = MagicMock()
        mock_tracker_class.side_effect = [first_tracker_instance, second_tracker_instance]

        # Initial start
        controller.start(123)
        mock_tracker_class.assert_called_once_with(target_hwnd=123, poll_rate=60)
        first_tracker_instance.start.assert_called_once()
        assert controller.get_tracker() == first_tracker_instance

        # Duplicate start with same HWND and tracker running
        controller.start(123)
        assert mock_tracker_class.call_count == 1  # Shouldn't instantiate a new one
        assert first_tracker_instance.start.call_count == 1

        # Start with new HWND
        controller.start(456)
        first_tracker_instance.stop.assert_called_once()  # First one should be stopped
        assert mock_tracker_class.call_count == 2  # New tracker instantiated
        assert mock_tracker_class.call_args_list[1].kwargs == {"target_hwnd": 456, "poll_rate": 60}
        second_tracker_instance.start.assert_called_once()
        assert controller.get_tracker() == second_tracker_instance

def test_tracker_missing_target_hwnd():
    parent = MagicMock()
    controller = WindowTrackerController(parent)

    with patch('ui.controllers.window_tracker_controller.WindowTracker') as mock_tracker_class:
        controller.start(None)
        mock_tracker_class.assert_not_called()
        assert controller.get_tracker() is None

        controller.start(0)
        mock_tracker_class.assert_not_called()
        assert controller.get_tracker() is None