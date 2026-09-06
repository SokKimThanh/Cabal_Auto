import unittest
from unittest.mock import MagicMock
from lib.features.setup.screen_state_analyzer import ScreenStateAnalyzer
from lib.features.hunt.scanner import AutoScanner

class TestScreenStateAnalyzer(unittest.TestCase):
    def test_screen_state_analyzer_extraction(self):
        analyzer = ScreenStateAnalyzer()

        # Mocking actual detection, in real implementation it would use the snapshot
        state = analyzer.scan_screen_state(12345)

        self.assertIn('character_class', state)
        self.assertEqual(state['character_class'], "Unknown")

        self.assertIn('character_level', state)
        self.assertEqual(state['character_level'], 1)

        self.assertIn('hp_percent', state)
        self.assertEqual(state['hp_percent'], 100.0)

    def test_screen_state_analyzer_location_detection(self):
        analyzer = ScreenStateAnalyzer()
        location = analyzer.detect_location_type(None)
        self.assertEqual(location, "ZONE")

    def test_screen_state_analyzer_validation(self):
        analyzer = ScreenStateAnalyzer()
        result = analyzer.validate_skill_keys("warrior", {})
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.mismatches), 0)

    def test_auto_scanner_multi_region_window(self):
        # Setup mock window manager
        mock_window_manager = MagicMock()
        # Let's say it returns a hwnd if Korean title is passed
        def mock_find_window(title_contains):
            if title_contains == "카발":
                return 9999
            return None
        mock_window_manager.find_window.side_effect = mock_find_window

        scanner = AutoScanner(MagicMock())
        scanner.window_manager = mock_window_manager

        hwnd = scanner._find_cabal_window()
        self.assertEqual(hwnd, 9999)

        # Test Polish title
        def mock_find_window_polish(title_contains):
            if title_contains == "Cabała":
                return 8888
            return None
        mock_window_manager.find_window.side_effect = mock_find_window_polish

        hwnd = scanner._find_cabal_window()
        self.assertEqual(hwnd, 8888)

if __name__ == '__main__':
    unittest.main()
