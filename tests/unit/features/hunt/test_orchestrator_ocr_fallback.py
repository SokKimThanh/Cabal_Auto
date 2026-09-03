import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock out window_manager and other windows specifics before import
sys.modules['lib.system.window_manager'] = MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = MagicMock()

from lib.features.hunt.hunt_orchestrator import HuntOrchestrator

def test_ocr_fallback_contract():
    # Setup mocks
    mock_on_status = MagicMock()
    mock_on_state = MagicMock()
    mock_locate = MagicMock()
    mock_prepare = MagicMock()
    mock_try_cast = MagicMock()
    mock_bring_window = MagicMock()
    mock_bring_hwnd = MagicMock()
    mock_bring_pid = MagicMock()
    mock_iconify = MagicMock()
    mock_update_stats = MagicMock()
    mock_get_selected = MagicMock(return_value={"hwnd": 123})

    # We will capture tasks scheduled for the UI
    ui_tasks = []
    def mock_schedule(task):
        ui_tasks.append(task)
        task() # execute it synchronously

    mock_set_target_info = MagicMock()

    orchestrator = HuntOrchestrator(
        on_status_update=mock_on_status,
        on_state_change=mock_on_state,
        locate_target=mock_locate,
        prepare_skill_runtime=mock_prepare,
        try_cast_skills=mock_try_cast,
        bring_window_to_front=mock_bring_window,
        bring_window_to_front_by_hwnd=mock_bring_hwnd,
        bring_window_to_front_by_pid=mock_bring_pid,
        iconify_app=mock_iconify,
        update_skill_stats_display=mock_update_stats,
        get_hunt_selected=mock_get_selected,
        schedule_ui_task=mock_schedule,
        set_target_info=mock_set_target_info
    )

    with patch("lib.features.hunt.hunt_orchestrator.find_monster_by_name_api") as mock_find:
        # Simulate unknown monster from DB (returns None)
        mock_find.return_value = None

        with patch("lib.features.hunt.hunt_orchestrator.TargetBarDetector") as MockTBD:
            mock_tbd = MagicMock()
            mock_tbd.is_target_alive.return_value = True
            MockTBD.return_value = mock_tbd

            with patch("lib.features.hunt.hunt_orchestrator.TargetNameReader") as MockTNR:
                mock_tnr = MagicMock()
                mock_tnr.read_name.return_value = "Unknown Mob"
                MockTNR.return_value = mock_tnr

                with patch("lib.features.hunt.hunt_orchestrator.get_hunt_logger", MagicMock()):

                    orchestrator.bot_manager = MagicMock()
                    orchestrator.bot_manager.screen_capture = MagicMock()
                    orchestrator.bot_manager.screen_capture.hwnd = 123
                    # Return a valid frame that bypasses 'frame is not None' check
                    orchestrator.bot_manager.screen_capture.get_latest_frame.return_value = "mock_frame"

                    # Run the loop just once, then exit
                    def mock_is_alive_side_effect(*args):
                        orchestrator.hunt_running = False
                        return True
                    mock_tbd.is_target_alive.side_effect = mock_is_alive_side_effect

                    cfg = {
                        "target_key": "z",
                        "lost_timeout_sec": 0,
                        "target_lost_debounce_frames": 3,
                        "search_tap_delay_sec": 0.0,
                        "attack_interval": 0.0,
                    }

                    orchestrator.start_hunt(cfg)
                    orchestrator.hunt_thread.join(timeout=2.0)

                    # Verify that the fallback mechanism worked and scheduled UI task
                    assert mock_set_target_info.called
                    # The fallback should pass name, hp as None, ID as 0
                    assert "[ID: #0] Unknown Mob (HP: None)" in mock_set_target_info.call_args[0][0]
