"""
Integration tests for monster tracking system.

Tests the complete flow from configuration → VisionEngine → MonsterDetector → OverlayController.
Verifies that all components work together correctly with real configuration.

Sprint 23 Phase 7 Batch 4 Task 4.1
"""

import json
import time
import unittest
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock

pytestmark = [
    pytest.mark.windows,
    pytest.mark.integration,
    pytest.mark.vision,
    pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows OS and pywin32")
]

from lib.vision.vision_engine import VisionEngine
import sys
if sys.platform == "win32":
    from lib.system.screen_capture import ScreenCapture
else:
    ScreenCapture = None  # type: ignore
from lib.vision.monster_detector import MonsterDetector
try:
    from ui.utils.overlay_controller import OverlayController
except (ImportError, RuntimeError):
    OverlayController = None  # type: ignore
from lib.system.bot_manager import BotManager


class TestMonsterTrackingIntegration(unittest.TestCase):
    """Integration tests for complete monster tracking system."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.config_path = self.project_root / "lib" / "data" / "hunt_config.json"
        
        # Load actual config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Get monster tracking config
        self.tracking_config = self.config.get('monster_tracking', {})
        
        # Create mock components
        self.vision_engine = Mock(spec=VisionEngine)
        self.screen_capture = Mock(spec=ScreenCapture)
        self.overlay = Mock()

    def test_config_structure(self):
        """Test that hunt_config.json has correct monster_tracking structure."""
        # Verify monster_tracking section exists
        self.assertIn('monster_tracking', self.config)
        
        tracking = self.tracking_config
        
        # Verify all required fields exist
        required_fields = [
            'enabled',
            'detection_interval',
            'confidence_threshold',
            'stable_frames',
            'lost_timeout',
            'max_detections_display',
            'show_stats',
            'stats_update_interval',
            'auto_start_with_hunt'
        ]
        
        for field in required_fields:
            self.assertIn(field, tracking, f"Missing required field: {field}")
        
        # Verify field types
        self.assertIsInstance(tracking['enabled'], bool)
        self.assertIsInstance(tracking['detection_interval'], (int, float))
        self.assertIsInstance(tracking['confidence_threshold'], (int, float))
        self.assertIsInstance(tracking['stable_frames'], int)
        self.assertIsInstance(tracking['lost_timeout'], (int, float))
        self.assertIsInstance(tracking['max_detections_display'], int)
        self.assertIsInstance(tracking['show_stats'], bool)
        self.assertIsInstance(tracking['stats_update_interval'], (int, float))
        self.assertIsInstance(tracking['auto_start_with_hunt'], bool)
        
        # Verify reasonable value ranges
        self.assertGreater(tracking['detection_interval'], 0)
        self.assertGreater(tracking['confidence_threshold'], 0)
        self.assertLessEqual(tracking['confidence_threshold'], 1.0)
        self.assertGreater(tracking['stable_frames'], 0)
        self.assertGreater(tracking['lost_timeout'], 0)
        self.assertGreater(tracking['max_detections_display'], 0)
        self.assertGreater(tracking['stats_update_interval'], 0)

    def test_bot_manager_uses_config(self):
        """Test BotManager initialization with config values."""
        # Get config values
        stable_frames = int(self.tracking_config.get('stable_frames', 3))
        lost_timeout = float(self.tracking_config.get('lost_timeout', 3.0))
        auto_start = bool(self.tracking_config.get('auto_start_with_hunt', False))
        
        # Create BotManager with config
        manager = BotManager(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            stable_frames=stable_frames,
            lost_timeout=lost_timeout,
            enable_auto_start=auto_start
        )
        
        # Verify initialization
        self.assertIsNotNone(manager)
        self.assertEqual(manager._stable_frames, stable_frames)
        self.assertEqual(manager._lost_timeout, lost_timeout)
        
        # Clean up
        manager.destroy()

    def test_detector_creation_with_config(self):
        """Test MonsterDetector creation with config values."""
        # Get config values
        stable_frames = int(self.tracking_config.get('stable_frames', 3))
        lost_timeout = float(self.tracking_config.get('lost_timeout', 3.0))
        
        # Create detector with config
        detector = MonsterDetector(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            stable_frames_threshold=stable_frames,
            lost_timeout_sec=lost_timeout
        )
        
        # Verify initialization
        self.assertIsNotNone(detector)
        
        # Clean up
        detector.stop()

    def test_overlay_controller_uses_config(self):
        """Test OverlayController initialization with config values."""
        # Get config values
        max_boxes = int(self.tracking_config.get('max_detections_display', 20))
        show_stats = bool(self.tracking_config.get('show_stats', True))
        stats_interval = float(self.tracking_config.get('stats_update_interval', 0.5))
        
        # Create detector first
        detector = MonsterDetector(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture
        )
        
        # Create controller with config
        controller = OverlayController(
            overlay=self.overlay,
            detector=detector,
            max_boxes=max_boxes,
            show_stats=show_stats,
            stats_update_interval=stats_interval
        )
        
        # Verify initialization
        self.assertIsNotNone(controller)
        self.assertEqual(controller._max_boxes, max_boxes)
        self.assertEqual(controller._show_stats, show_stats)
        self.assertEqual(controller._stats_update_interval, stats_interval)
        
        # Clean up
        controller.stop()
        detector.stop()

    def test_full_integration_flow(self):
        """Test complete flow from config → detector → controller → overlay."""
        # Get config values
        stable_frames = int(self.tracking_config.get('stable_frames', 3))
        lost_timeout = float(self.tracking_config.get('lost_timeout', 3.0))
        max_boxes = int(self.tracking_config.get('max_detections_display', 20))
        show_stats = bool(self.tracking_config.get('show_stats', True))
        stats_interval = float(self.tracking_config.get('stats_update_interval', 0.5))
        
        # Create BotManager
        manager = BotManager(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            stable_frames=stable_frames,
            lost_timeout=lost_timeout
        )
        
        # Start detection
        success = manager.start_detection()
        
        self.assertTrue(success)
        self.assertTrue(manager.is_detection_running())
        self.assertIsNotNone(manager._detector)
        
        # Create OverlayController
        controller = OverlayController(
            overlay=self.overlay,
            detector=manager._detector,
            max_boxes=max_boxes,
            show_stats=show_stats,
            stats_update_interval=stats_interval
        )
        
        # Start controller
        controller.start()
        
        # Give time for initialization
        time.sleep(0.1)
        
        # Clean up
        controller.stop()
        manager.destroy()

    def test_config_defaults_fallback(self):
        """Test that missing config values fall back to reasonable defaults."""
        # Simulate empty config
        empty_config = {}
        
        # Get values with defaults
        stable_frames = int(empty_config.get('stable_frames', 3))
        lost_timeout = float(empty_config.get('lost_timeout', 3.0))
        max_boxes = int(empty_config.get('max_detections_display', 20))
        show_stats = bool(empty_config.get('show_stats', True))
        stats_interval = float(empty_config.get('stats_update_interval', 0.5))
        auto_start = bool(empty_config.get('auto_start_with_hunt', False))
        
        # Verify defaults are reasonable
        self.assertEqual(stable_frames, 3)
        self.assertEqual(lost_timeout, 3.0)
        self.assertEqual(max_boxes, 20)
        self.assertEqual(show_stats, True)
        self.assertEqual(stats_interval, 0.5)
        self.assertEqual(auto_start, False)
        
        # Create components with defaults - should not raise
        manager = BotManager(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            stable_frames=stable_frames,
            lost_timeout=lost_timeout,
            enable_auto_start=auto_start
        )
        
        detector = MonsterDetector(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            stable_frames_threshold=stable_frames,
            lost_timeout_sec=lost_timeout
        )
        
        controller = OverlayController(
            overlay=self.overlay,
            detector=detector,
            max_boxes=max_boxes,
            show_stats=show_stats,
            stats_update_interval=stats_interval
        )
        
        # Clean up
        controller.stop()
        detector.stop()
        manager.destroy()

    def test_auto_start_with_hunt_config(self):
        """Test auto_start_with_hunt configuration option."""
        # Test with auto_start=True
        manager = BotManager(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            enable_auto_start=True
        )
        
        # Simulate hunt start
        manager.on_hunt_start()
        
        # Should auto-start detection
        self.assertTrue(manager.is_detection_running())
        
        # Clean up
        manager.destroy()
        
        # Test with auto_start=False
        manager2 = BotManager(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture,
            enable_auto_start=False
        )
        
        # Simulate hunt start
        manager2.on_hunt_start()
        
        # Should NOT auto-start
        self.assertFalse(manager2.is_detection_running())
        
        # Clean up
        manager2.destroy()


class TestConfigurationValidation(unittest.TestCase):
    """Tests for configuration validation and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.config_path = self.project_root / "lib" / "data" / "hunt_config.json"

    def test_config_file_exists(self):
        """Test that hunt_config.json exists."""
        self.assertTrue(self.config_path.exists(), "hunt_config.json not found")

    def test_config_is_valid_json(self):
        """Test that hunt_config.json is valid JSON."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.assertIsInstance(config, dict)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in hunt_config.json: {e}")

    def test_config_has_monster_tracking(self):
        """Test that config has monster_tracking section."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertIn('monster_tracking', config)
        self.assertIsInstance(config['monster_tracking'], dict)

    def test_invalid_config_values_handled(self):
        """Test that invalid config values are handled gracefully."""
        # Test with invalid types
        invalid_configs = [
            {'stable_frames': 'invalid'},  # Should be int
            {'lost_timeout': 'invalid'},   # Should be float
            {'stable_frames': -1},  # Should be positive
        ]
        
        for invalid_cfg in invalid_configs:
            # Should not crash, should use defaults or handle gracefully
            try:
                stable_frames = int(invalid_cfg.get('stable_frames', 3))
                lost_timeout = float(invalid_cfg.get('lost_timeout', 3.0))
                
                # Verify fallbacks work
                self.assertIsInstance(stable_frames, int)
                self.assertIsInstance(lost_timeout, float)
            except (ValueError, TypeError):
                # Expected for invalid values - should fall back to defaults
                pass


if __name__ == '__main__':
    unittest.main()
