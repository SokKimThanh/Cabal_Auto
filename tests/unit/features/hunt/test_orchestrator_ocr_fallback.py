import sys
import pytest
from unittest.mock import MagicMock, patch

sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock out window_manager and other windows specifics before import
sys.modules['lib.system.window_manager'] = MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = MagicMock()

from lib.features.hunt.hunt_orchestrator import HuntOrchestrator
from lib.orchestrator.hunt_status_handler import HuntStatusHandler

def test_ocr_fallback_contract():
    class MockHandler(HuntStatusHandler):
        def __init__(self):
            self.set_target_info_called = False
            self.set_target_info_args = []

        def set_target_info(self, text):
            self.set_target_info_called = True
            self.set_target_info_args.append(text)

        def get_hunt_selected(self): return {"hwnd": 123}
        def schedule_ui_task(self, task): task()
        def on_state_change(self, state): pass
        def on_status_update(self, msg): pass
        def clear_target_ui(self): pass
        def update_skill_stats_display(self, stats): pass
        def bring_window_to_front(self, name): return True
        def bring_window_to_front_by_hwnd(self, hwnd): return True
        def bring_window_to_front_by_pid(self, pid): return True
        def iconify_app(self): pass
        def locate_target(self, params): return (0, 0)
        def prepare_skill_runtime(self, skill_def): return []
        def try_cast_skills(self): pass
        def on_scene_monsters_detected(self, monsters): pass

    mock_handler = MockHandler()

    orchestrator = HuntOrchestrator(
        on_status_update=mock_handler.on_status_update,
        on_state_change=mock_handler.on_state_change,
        locate_target=mock_handler.locate_target,
        prepare_skill_runtime=mock_handler.prepare_skill_runtime,
        try_cast_skills=mock_handler.try_cast_skills,
        bring_window_to_front=mock_handler.bring_window_to_front,
        bring_window_to_front_by_hwnd=mock_handler.bring_window_to_front_by_hwnd,
        bring_window_to_front_by_pid=mock_handler.bring_window_to_front_by_pid,
        iconify_app=mock_handler.iconify_app,
        update_skill_stats_display=mock_handler.update_skill_stats_display,
        get_hunt_selected=mock_handler.get_hunt_selected,
        schedule_ui_task=mock_handler.schedule_ui_task,
        clear_target_ui=mock_handler.clear_target_ui,
        set_target_info=mock_handler.set_target_info,
        on_scene_monsters_detected=mock_handler.on_scene_monsters_detected
    )
    orchestrator.bot_manager = MagicMock()
    orchestrator.vision_engine = MagicMock()
    orchestrator.skill_runtime = MagicMock()

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
                    with patch("lib.features.hunt.window_selection_service.validate_selected_cabal_window") as mock_val:
                        mock_validation = MagicMock()
                        mock_validation.is_valid = True
                        mock_val.return_value = mock_validation

                        orchestrator.bot_manager = MagicMock()
                        orchestrator.bot_manager.screen_capture = MagicMock()
                        orchestrator.bot_manager.screen_capture.hwnd = 123
                        # Return a valid frame that bypasses 'frame is not None' check
                        orchestrator.bot_manager.screen_capture.get_latest_frame.return_value = "mock_frame"

                        # We want to run the loop at least one full cycle
                        # setting hunt_running=False immediately makes it exit the inner loop before it processes the frame
                        def mock_is_alive_side_effect(*args):
                            return True

                        mock_tbd.is_target_alive.side_effect = mock_is_alive_side_effect

                        cfg = {
                            "target_key": "z",
                            "lost_timeout_sec": 0,
                            "target_lost_debounce_frames": 3,
                            "search_tap_delay_sec": 0.0,
                            "attack_interval": 0.0,
                            "target_policy": "any_target",
                            "monster_rotation": [{"monster_id": 0, "priority": 1}],
                        }

                        orchestrator.start_hunt(cfg)
                        import time
                        time.sleep(0.5)
                        orchestrator.hunt_running = False
                        orchestrator.hunt_thread.join(timeout=2.0)

                        # Verify that the fallback mechanism worked and scheduled UI task
                        assert mock_handler.set_target_info_called
                        # The fallback should pass name, hp as None, ID as 0
                        assert "[ID: #0] Unknown Mob (HP: None)" in mock_handler.set_target_info_args[-1]
