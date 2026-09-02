import pytest
import numpy as np
from lib.vision.target_bar_detector import TargetBarDetector

@pytest.fixture
def detector():
    return TargetBarDetector()

def create_synthetic_frame(width=1920, height=1080, fill_ratio=0.5, bgr_color=(0, 255, 255), is_black=False):
    """
    Creates a synthetic frame with an optional target bar.
    """
    if is_black:
        return np.zeros((height, width, 3), dtype=np.uint8)

    frame = np.full((height, width, 3), (50, 50, 50), dtype=np.uint8) # Dark gray background

    # Calculate ROI based on detector's logic
    roi_top = int(height * 0.048)
    roi_bottom = int(height * 0.065)
    roi_left = int(width * 0.42)
    roi_right = int(width * 0.58)

    roi_width = roi_right - roi_left
    fill_width = int(roi_width * fill_ratio)

    # Draw the bar
    if fill_width > 0:
        frame[roi_top:roi_bottom, roi_left:roi_left+fill_width] = bgr_color

    return frame

def test_yellow_bar_alive(detector):
    # Yellow in BGR is (0, 255, 255)
    # This maps roughly to HSV [30, 255, 255] which is within the bounds [12, 130, 130] - [32, 255, 255]
    frame = create_synthetic_frame(bgr_color=(0, 255, 255))
    assert detector.is_target_alive(frame) is True

    # Also verify HP percentage
    hp = detector.get_hp_percentage(frame)
    assert 45.0 <= hp <= 55.0 # Should be around 50%

def test_empty_black_frame(detector):
    frame = create_synthetic_frame(is_black=True)
    assert detector.is_target_alive(frame) is False
    assert detector.get_hp_percentage(frame) == 0.0

def test_none_corrupted_frame(detector):
    assert detector.is_target_alive(None) is False
    assert detector.is_target_alive(np.array([])) is False
    assert detector.get_hp_percentage(None) == 0.0

def test_different_resolutions(detector):
    # 1080p
    frame_1080 = create_synthetic_frame(width=1920, height=1080)
    assert detector.is_target_alive(frame_1080) is True

    # 4K
    frame_4k = create_synthetic_frame(width=3840, height=2160)
    assert detector.is_target_alive(frame_4k) is True

def test_get_client_size_hwnd():
    import sys
    from unittest.mock import MagicMock, patch

    # Mock win32gui to return a valid rect
    mock_win32gui = MagicMock()
    mock_win32gui.GetClientRect.return_value = (0, 0, 800, 600)

    with patch.dict('sys.modules', {'win32gui': mock_win32gui}):
        # Re-import to pickup mock
        import lib.vision.target_bar_detector
        from importlib import reload
        reload(lib.vision.target_bar_detector)
        TargetBarDetector = lib.vision.target_bar_detector.TargetBarDetector

        detector = TargetBarDetector(hwnd=123)

        # Should get the client size from the mock
        w, h = detector._get_client_size()
        assert w == 800
        assert h == 600
        assert mock_win32gui.GetClientRect.called

        # Test fallback to frame size when mismatched
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        roi = detector._get_roi(frame)
    # The ROI is computed on 1280x720, not 800x600 because it falls back to frame shape
    # Let's check ROI dimensions
    top = int(720 * detector.roi_top_frac)
    bottom = int(720 * detector.roi_bottom_frac)
    left = int(1280 * detector.roi_left_frac)
    right = int(1280 * detector.roi_right_frac)

    assert roi.shape == (bottom - top, right - left, 3)

def test_dark_colored_non_empty_bar(detector):
    # Dark yellow/brown: e.g. BGR (0, 150, 150)
    # HSV would be ~ [30, 255, 150] which is in bounds (V >= 130)
    frame = create_synthetic_frame(bgr_color=(0, 150, 150))

    # Ensure it's not detected as a black frame
    assert detector.is_target_alive(frame) is True

    # A bar that is just barely bright enough to be non-empty but overall very dark.
    # The mean intensity check for black frames uses threshold < 5
    # Let's create a very dark bar
    frame_dark = np.zeros((1080, 1920, 3), dtype=np.uint8)
    roi_top = int(1080 * 0.048)
    roi_bottom = int(1080 * 0.065)
    roi_left = int(1920 * 0.42)
    roi_right = int(1920 * 0.58)

    # Fill only a tiny portion with dark yellow, rest is black.
    # Overall ROI mean might be low, but we want to make sure the black frame detection
    # only catches TRULY black frames (mean < 5).
    # If mean >= 5, it should be processed.
    # We will make the whole ROI mean around 6.
    frame_dark[roi_top:roi_bottom, roi_left:roi_right] = (2, 2, 2) # Very dark gray background

    # Add a valid color block
    # Lower HSV [12, 130, 130] -> approx BGR (0, 130, 130) to (0, 255, 255)
    valid_color = (0, 140, 140)
    fill_width = int((roi_right - roi_left) * 0.1) # 10% width
    frame_dark[roi_top:roi_bottom, roi_left:roi_left+fill_width] = valid_color

    assert detector.is_target_alive(frame_dark) is True
