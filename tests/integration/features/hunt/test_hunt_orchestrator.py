import pytest
from unittest.mock import MagicMock, patch
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
import threading

pytestmark = pytest.mark.integration


def test_orchestrator_init():
    orchestrator = HuntOrchestrator(
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        get_hunt_selected=MagicMock(),
    )

    assert orchestrator.hunt_running is False


@patch("threading.Thread")
def test_start_hunt(mock_thread):
    mock_schedule = MagicMock()
    orchestrator = HuntOrchestrator(
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        get_hunt_selected=MagicMock(),
    )

    orchestrator.start_hunt({"search_interval": 1.0})
    assert orchestrator.hunt_running is True
    mock_thread.assert_called_once()
    # UI scheduling is now event-driven

    # Try starting again
    orchestrator.start_hunt({"search_interval": 1.0})
    # It should early exit and not start a new thread
    mock_thread.assert_called_once()


def test_stop_hunt():
    orchestrator = HuntOrchestrator(
        locate_target=MagicMock(),
        prepare_skill_runtime=MagicMock(),
        try_cast_skills=MagicMock(),
        bring_window_to_front=MagicMock(),
        bring_window_to_front_by_hwnd=MagicMock(),
        bring_window_to_front_by_pid=MagicMock(),
        iconify_app=MagicMock(),
        get_hunt_selected=MagicMock(),
    )

    orchestrator.hunt_running = True
    orchestrator.stop_hunt()
    assert orchestrator.hunt_running is False
