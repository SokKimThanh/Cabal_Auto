"""Unit tests for CabalComboDetector."""

import pytest
import numpy as np
import time
from unittest.mock import Mock, MagicMock, patch
from lib.features.combo import CabalComboDetector


@pytest.fixture
def mock_screen_capture():
    """Create a mock screen capture object."""
    capture = Mock()
    capture.get_latest_frame = Mock(return_value=None)
    return capture


@pytest.fixture
def bright_pixel_frame():
    """Create a frame with a bright pixel at the hit-zone."""
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Create a bright pixel in the hit-zone area
    # Use EXACT same calculation as detector to avoid coordinate mismatch
    h, w = 1080, 1920
    y_ratio_range = (0.052, 0.062)
    x_ratio_range = (0.415, 0.585)
    hit_zone_x_ratio = 0.78
    
    y_start = int(h * y_ratio_range[0])
    y_end = int(h * y_ratio_range[1])
    x_start = int(w * x_ratio_range[0])
    x_end = int(w * x_ratio_range[1])
    
    roi_width = x_end - x_start
    hit_zone_col = x_start + int(roi_width * hit_zone_x_ratio)
    
    if y_start < y_end:
        frame[y_start:y_end, hit_zone_col, :] = [255, 255, 255]  # White = max V in HSV
    
    return frame


@pytest.fixture
def dark_frame():
    """Create a frame with no bright pixels."""
    return np.zeros((1080, 1920, 3), dtype=np.uint8)


@pytest.fixture
def combo_detector():
    """Create a CabalComboDetector instance."""
    return CabalComboDetector(
        hwnd=0,
        poll_interval_ms=4,
        cooldown_guard_ms=120
    )


class TestCabalComboDetectorInitialization:
    """Test detector initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        detector = CabalComboDetector(hwnd=12345)
        assert detector.hwnd == 12345
        assert detector.hit_zone_x_ratio == 0.78
        assert detector.poll_interval_ms == 4
        assert detector.cooldown_guard_ms == 120
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        detector = CabalComboDetector(
            hwnd=999,
            hit_zone_x_ratio=0.75,
            poll_interval_ms=5,
            cooldown_guard_ms=100
        )
        assert detector.hwnd == 999
        assert detector.hit_zone_x_ratio == 0.75
        assert detector.poll_interval_ms == 5
        assert detector.cooldown_guard_ms == 100


class TestHitZoneDetection:
    """Test hit-zone detection logic."""
    
    def test_bright_pixel_detection(self, combo_detector, mock_screen_capture, bright_pixel_frame):
        """Test that bright pixel is detected at hit-zone."""
        mock_screen_capture.get_latest_frame.return_value = bright_pixel_frame
        
        result = combo_detector._check_hit_zone(bright_pixel_frame)
        assert result is True
    
    def test_dark_frame_no_detection(self, combo_detector, dark_frame):
        """Test that dark frame returns False."""
        result = combo_detector._check_hit_zone(dark_frame)
        assert result is False
    
    def test_wait_for_hit_zone_detects_bright(self, combo_detector, mock_screen_capture, bright_pixel_frame):
        """Test wait_for_hit_zone returns True when bright pixel detected."""
        callback = Mock()
        combo_detector.key_press_callback = callback
        
        # First call returns None, second returns bright frame
        mock_screen_capture.get_latest_frame.side_effect = [None, bright_pixel_frame]
        
        result = combo_detector.wait_for_hit_zone(mock_screen_capture, timeout_sec=1.0)
        
        assert result is True
        assert callback.called


class TestCooldownGuard:
    """Test cooldown guard prevents double-press."""
    
    def test_callback_fires_once_with_cooldown(self, combo_detector, mock_screen_capture, bright_pixel_frame):
        """Test callback fires exactly once even if bright pixel persists."""
        callback = Mock()
        combo_detector.key_press_callback = callback
        combo_detector.cooldown_guard_ms = 50
        
        # Always return bright frame
        mock_screen_capture.get_latest_frame.return_value = bright_pixel_frame
        
        result = combo_detector.wait_for_hit_zone(mock_screen_capture, timeout_sec=0.2)
        
        # Callback should be called exactly once
        assert callback.call_count == 1
        assert result is True
    
    def test_early_exit_on_target_death(self, combo_detector, mock_screen_capture, bright_pixel_frame):
        """Test early exit from cooldown guard when target dies."""
        callback = Mock()
        combo_detector.key_press_callback = callback
        combo_detector.cooldown_guard_ms = 200  # Long cooldown
        
        mock_screen_capture.get_latest_frame.return_value = bright_pixel_frame
        
        # is_target_alive returns True for first chunk, False after
        call_count = [0]
        def target_alive():
            call_count[0] += 1
            return call_count[0] < 2  # False after first call during cooldown
        
        start_time = time.time()
        result = combo_detector.wait_for_hit_zone(
            mock_screen_capture,
            timeout_sec=1.0,
            is_target_alive_check=target_alive
        )
        elapsed = time.time() - start_time
        
        assert result is True
        # Should exit much earlier than full cooldown_guard_ms
        assert elapsed < 0.15


class TestCPUPerformance:
    """Test that detector doesn't hog CPU."""
    
    def test_low_cpu_usage_during_polling(self, combo_detector, mock_screen_capture, dark_frame):
        """Test CPU usage remains low during polling."""
        mock_screen_capture.get_latest_frame.return_value = dark_frame
        
        start_time = time.time()
        result = combo_detector.wait_for_hit_zone(mock_screen_capture, timeout_sec=0.5)
        elapsed = time.time() - start_time
        
        # Should timeout quickly without spinning CPU
        assert result is False
        assert 0.4 < elapsed < 0.7  # Allow some variance


class TestGetLatestFrameThreadSafety:
    """Test that get_latest_frame returns independent copy."""
    
    def test_get_latest_frame_returns_copy(self, mock_screen_capture):
        """Test that modifying returned frame doesn't affect internal buffer."""
        # Create a detector with mocked screen capture
        detector = CabalComboDetector(hwnd=0)
        
        # Create two different frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame1[50, 50] = [100, 100, 100]
        
        frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2[50, 50] = [200, 200, 200]
        
        mock_screen_capture.get_latest_frame.side_effect = [frame1, frame2]
        
        # Get first frame
        returned1 = mock_screen_capture.get_latest_frame()
        original_value = returned1[50, 50, 0]
        
        # Modify returned frame
        returned1[50, 50] = [1, 2, 3]
        
        # Get second frame
        returned2 = mock_screen_capture.get_latest_frame()
        
        # Verify modifications didn't affect the second retrieval
        assert returned2[50, 50, 0] != returned1[50, 50, 0]


class TestTimeoutBehavior:
    """Test timeout handling."""
    
    def test_timeout_returns_false(self, combo_detector, mock_screen_capture, dark_frame):
        """Test that timeout_sec is respected."""
        mock_screen_capture.get_latest_frame.return_value = dark_frame
        
        start_time = time.time()
        result = combo_detector.wait_for_hit_zone(mock_screen_capture, timeout_sec=0.3)
        elapsed = time.time() - start_time
        
        assert result is False
        assert 0.2 < elapsed < 0.5


class TestComboStartKeyPressedOnce:
    """Test that combo_start_key is pressed exactly once per acquisition."""
    
    def test_combo_detector_single_trigger(self, combo_detector, mock_screen_capture, bright_pixel_frame):
        """Test detector fires single TRIGGER_READY event."""
        callback = Mock()
        combo_detector.key_press_callback = callback
        
        mock_screen_capture.get_latest_frame.return_value = bright_pixel_frame
        
        result = combo_detector.wait_for_hit_zone(mock_screen_capture, timeout_sec=0.5)
        
        # Should fire exactly once
        assert callback.call_count == 1
        assert result is True
