import pytest
from unittest.mock import MagicMock, patch
import sys
import numpy as np
import time

# Mock win32 modules for testing on non-Windows/headless
sys.modules['win32gui'] = MagicMock()
sys.modules['win32ui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['ctypes'] = MagicMock()
sys.modules['ctypes.windll'] = MagicMock()
import win32gui
sys.platform = "win32"

from lib.system.screen_capture import ScreenCapture
from lib.features.hunt.scanner import AutoScanner
from lib.vision.vision_engine import VisionEngine

@pytest.fixture
def mock_vision_engine():
    engine = MagicMock(spec=VisionEngine)
    engine.detect_monster_pipeline.return_value = []
    engine.match_templates.return_value = []
    return engine

@pytest.fixture
def scanner(mock_vision_engine):
    return AutoScanner(mock_vision_engine)

def test_roi_crop_from_correct_window(scanner, mock_vision_engine):
    """Test that AutoScanner passes the correct hwnd to ScreenCapture and uses the frame."""
    target_hwnd = 12345
    window_info = {"hwnd": target_hwnd, "rect": {"width": 800, "height": 600}}

    # Setup mock screen capture
    mock_capture = MagicMock()
    mock_capture.hwnd = None
    mock_capture.start.return_value = True

    # Create a dummy frame
    dummy_frame = np.zeros((600, 800, 3), dtype=np.uint8)
    mock_capture.get_frame.return_value = dummy_frame

    scanner.screen_capture = mock_capture

    # Mock the window_rect on screen_capture to test coordinate conversion
    mock_capture.window_rect = {"left": 50, "top": 50, "right": 850, "bottom": 650, "width": 800, "height": 600}

    # Run scan with absolute coordinates
    hunt_config = {"rois": {"hunt_area": [60, 60, 100, 100]}}
    scanner.scan_screen(window_info, hunt_config)

    # Verify that start was called with the correct hwnd
    mock_capture.start.assert_called_once()
    kwargs = mock_capture.start.call_args.kwargs
    assert kwargs.get('hwnd') == target_hwnd

    # Verify vision engine used the converted relative ROI on the captured frame
    # Absolute (60, 60) - Offset (50, 50) = Relative (10, 10)
    mock_vision_engine.detect_monster_pipeline.assert_called_once()
    args, kwargs = mock_vision_engine.detect_monster_pipeline.call_args
    assert np.array_equal(args[0], dummy_frame)
    assert kwargs.get('roi') == (10, 10, 100, 100)

@patch('lib.system.screen_capture.win32gui')
def test_screen_capture_uses_provided_hwnd(mock_win32gui):
    """Test that ScreenCapture uses the provided hwnd and doesn't search by title."""
    capture = ScreenCapture(backend="bitblt") # Avoid dxcam trying to load

    target_hwnd = 98765
    mock_win32gui.GetClientRect.return_value = (0, 0, 800, 600)
    mock_win32gui.ClientToScreen.return_value = (100, 100)

    # Start capture with provided hwnd
    assert capture.start(window_title="Test", hwnd=target_hwnd) == True

    # Verify it used the provided hwnd
    assert capture.hwnd == target_hwnd

    # Should not have called EnumWindows since we provided the hwnd
    mock_win32gui.EnumWindows.assert_not_called()

    capture.stop()

@patch('lib.system.screen_capture.win32gui')
def test_screen_capture_updates_rect_on_move(mock_win32gui):
    """Test that window movement updates capture rect properly."""
    capture = ScreenCapture(backend="bitblt")

    target_hwnd = 11111
    # Initial position
    mock_win32gui.GetClientRect.return_value = (0, 0, 800, 600)
    mock_win32gui.ClientToScreen.return_value = (100, 100)
    mock_win32gui.IsWindow.return_value = True
    mock_win32gui.IsIconic.return_value = False

    capture.start(window_title="Test", hwnd=target_hwnd)

    # Verify initial rect
    assert capture.window_rect["left"] == 100
    assert capture.window_rect["top"] == 100

    # Simulate window move (ClientToScreen returns new coords)
    mock_win32gui.ClientToScreen.return_value = (200, 300)

    # Wait for capture loop to update
    time.sleep(0.2)

    # Verify rect updated
    assert capture.window_rect["left"] == 200
    assert capture.window_rect["top"] == 300

    capture.stop()
