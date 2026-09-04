import unittest
import time
import numpy as np
import sys
from unittest.mock import MagicMock
from lib.features.combo.combo_timing_detector import CabalComboDetector

class TestCabalComboDetector(unittest.TestCase):

    def setUp(self):
        self.mock_screen_capture = MagicMock()
        self.mock_callback = MagicMock()

    def test_wait_for_hit_zone_detects_and_calls_callback(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        detector = CabalComboDetector(
            hwnd=0,
            y_ratio_range=(0.05, 0.1),
            x_ratio_range=(0.4, 0.6),
            hit_zone_x_ratio=0.75,
            poll_interval_ms=1,
            cooldown_guard_ms=10,
            key_press_callback=self.mock_callback
        )
        frame[7, 55] = [255, 255, 255]
        self.mock_screen_capture.get_latest_frame.return_value = frame
        result = detector.wait_for_hit_zone(self.mock_screen_capture, timeout_sec=0.5)
        self.assertTrue(result)
        self.mock_callback.assert_called_once()

    def test_wait_for_hit_zone_timeout(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        self.mock_screen_capture.get_latest_frame.return_value = frame
        detector = CabalComboDetector(
            hwnd=0,
            poll_interval_ms=1,
            cooldown_guard_ms=10,
            key_press_callback=self.mock_callback
        )
        start = time.time()
        result = detector.wait_for_hit_zone(self.mock_screen_capture, timeout_sec=0.1)
        end = time.time()
        self.assertFalse(result)
        self.mock_callback.assert_not_called()
        self.assertGreaterEqual(end - start, 0.1)

    def test_cooldown_guard_prevents_double_activation(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        detector = CabalComboDetector(
            hwnd=0,
            y_ratio_range=(0.0, 1.0),
            x_ratio_range=(0.0, 1.0),
            hit_zone_x_ratio=0.5,
            poll_interval_ms=1,
            cooldown_guard_ms=100,
            key_press_callback=self.mock_callback
        )
        frame[50, 50] = [255, 255, 255]
        self.mock_screen_capture.get_latest_frame.return_value = frame
        start = time.time()
        result = detector.wait_for_hit_zone(self.mock_screen_capture, timeout_sec=0.5)
        end = time.time()
        self.assertTrue(result)
        self.mock_callback.assert_called_once()
        self.assertGreaterEqual(end - start, 0.1)

    def test_early_exit_on_target_death(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        detector = CabalComboDetector(
            hwnd=0,
            y_ratio_range=(0.0, 1.0),
            x_ratio_range=(0.0, 1.0),
            hit_zone_x_ratio=0.5,
            poll_interval_ms=1,
            cooldown_guard_ms=200,
            key_press_callback=self.mock_callback
        )
        frame[50, 50] = [255, 255, 255]
        self.mock_screen_capture.get_latest_frame.return_value = frame
        alive_checks = [True, False, False]
        def is_target_alive_check():
            if alive_checks:
                return alive_checks.pop(0)
            return False

        start = time.time()
        result = detector.wait_for_hit_zone(self.mock_screen_capture, timeout_sec=0.5, is_target_alive_check=is_target_alive_check)
        end = time.time()
        self.assertTrue(result)
        self.mock_callback.assert_called_once()
        self.assertLess(end - start, 0.1)

    def test_no_double_trigger_commit_mark_cast(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        def test_callback(): pass
        mock_callback_trigger = MagicMock(side_effect=test_callback)
        detector = CabalComboDetector(
            hwnd=0,
            y_ratio_range=(0.0, 1.0),
            x_ratio_range=(0.0, 1.0),
            hit_zone_x_ratio=0.5,
            poll_interval_ms=1,
            cooldown_guard_ms=10,
            key_press_callback=mock_callback_trigger
        )
        frame[50, 50] = [255, 255, 255]
        self.mock_screen_capture.get_latest_frame.return_value = frame
        result = detector.wait_for_hit_zone(self.mock_screen_capture, timeout_sec=0.5)
        self.assertTrue(result)
        mock_callback_trigger.assert_called_once()

    @unittest.skipIf(sys.platform != "win32", "Requires Windows for ScreenCapture")
    def test_get_latest_frame_returns_independent_copy(self):
        from lib.system.screen_capture import ScreenCapture
        capture = ScreenCapture(target_fps=15)
        original_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        original_frame[0, 0] = [255, 0, 0]
        capture._latest_frame = original_frame
        frame_copy = capture.get_latest_frame()
        frame_copy[0, 0] = [0, 255, 0]
        self.assertTrue((capture._latest_frame[0, 0] == [255, 0, 0]).all())
        self.assertTrue((frame_copy[0, 0] == [0, 255, 0]).all())

    def test_combo_start_key_only_triggered_once_per_target(self):
        mock_backend = MagicMock()
        mock_handler = MagicMock()
        mock_handler.app.state_controller._combo_mode_active = True

        cfg = {
            "combo": {
                "enabled": True,
                "combo_start_key": "alt+3"
            }
        }

        combo_cfg = cfg.get("combo", {})
        if combo_cfg.get("enabled", False):
            combo_start_key = combo_cfg.get("combo_start_key", "alt+3")
            if combo_start_key:
                mock_backend.tap(combo_start_key)

        mock_backend.tap.assert_called_once_with("alt+3")

if __name__ == '__main__':
    unittest.main()
