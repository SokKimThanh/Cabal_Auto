import pytest
from unittest.mock import MagicMock, patch
from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
import threading

def test_orchestrator_init(mock_orchestrator):
    assert mock_orchestrator.hunt_running is False

@patch('threading.Thread')
def test_start_hunt(mock_thread, mock_orchestrator):
    mock_schedule = MagicMock()
    mock_orchestrator.schedule_ui_task = mock_schedule

    mock_orchestrator.start_hunt({"search_interval": 1.0})
    assert mock_orchestrator.hunt_running is True
    mock_thread.assert_called_once()
    mock_schedule.assert_called_once()

    # Try starting again
    mock_orchestrator.start_hunt({"search_interval": 1.0})
    # It should early exit and not start a new thread
    mock_thread.assert_called_once()

def test_stop_hunt(mock_orchestrator):
    mock_orchestrator.hunt_running = True
    mock_orchestrator.stop_hunt()
    assert mock_orchestrator.hunt_running is False
