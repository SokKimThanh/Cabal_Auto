import pytest
from unittest.mock import MagicMock, patch
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
import threading

def test_orchestrator_init():
    orchestrator = HuntOrchestrator(
        handler=MagicMock(),
        bot_manager=MagicMock(),
        vision_engine=MagicMock(),
        skill_runtime=MagicMock()
    )

    assert orchestrator.hunt_running is False

@patch('threading.Thread')
def test_start_hunt(mock_thread):
    mock_handler = MagicMock()
    orchestrator = HuntOrchestrator(
        handler=mock_handler,
        bot_manager=MagicMock(),
        vision_engine=MagicMock(),
        skill_runtime=MagicMock()
    )

    orchestrator.start_hunt({"search_interval": 1.0})
    assert orchestrator.hunt_running is True
    mock_thread.assert_called_once()
    mock_handler.schedule_ui_task.assert_called_once()

    # Try starting again
    orchestrator.start_hunt({"search_interval": 1.0})
    # It should early exit and not start a new thread
    mock_thread.assert_called_once()

def test_stop_hunt():
    orchestrator = HuntOrchestrator(
        handler=MagicMock(),
        bot_manager=MagicMock(),
        vision_engine=MagicMock(),
        skill_runtime=MagicMock()
    )

    orchestrator.hunt_running = True
    orchestrator.stop_hunt()
    assert orchestrator.hunt_running is False
