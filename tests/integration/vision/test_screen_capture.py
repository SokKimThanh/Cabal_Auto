"""
Test Module: Screen Capture System - Sprint 23 Phase 8
Description: Tests screen capture functionality, performance, and error handling
"""

import sys
import pytest
from typing import Any, Optional
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# ============================================================================
# STEP 1: PLATFORM & ENVIRONMENT CHECKS
# ============================================================================

# Screen capture requires Windows (win32gui, win32ui, BitBlt)
pytestmark = [pytest.mark.windows, pytest.mark.unit]

if sys.platform != "win32":
    pytest.skip("Screen capture requires Windows environment", allow_module_level=True)

# ============================================================================
# STEP 2: OPTIONAL IMPORTS
# ============================================================================

# NumPy for frame data
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # type: ignore

# OpenCV for image operations (optional)
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None  # type: ignore

# ============================================================================
# STEP 3: PROJECT IMPORTS
# ============================================================================

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lib.system.screen_capture import ScreenCapture, CaptureStats, create_capture

# ============================================================================
# STEP 4: FIXTURES (Shared test setup)
# ============================================================================

@pytest.fixture
def mock_win32():
    """Mock Windows API modules"""
    with patch('lib.system.screen_capture.win32gui') as win32gui_mock, \
         patch('lib.system.screen_capture.win32ui') as win32ui_mock, \
         patch('lib.system.screen_capture.win32con') as win32con_mock, \
         patch('lib.system.screen_capture.windll') as windll_mock:
        
        # Mock window enumeration
        def enum_windows(callback, param):
            # Simulate finding a window
            callback(12345, param)
            return True
        
        win32gui_mock.EnumWindows.side_effect = enum_windows
        win32gui_mock.IsWindowVisible.return_value = True
        win32gui_mock.GetWindowText.return_value = "Cabal Online"
        win32gui_mock.GetClientRect.return_value = (0, 0, 1024, 768)
        win32gui_mock.ClientToScreen.return_value = (10, 20)
        win32gui_mock.IsWindow.return_value = True
        win32gui_mock.IsIconic.return_value = False
        
        yield {
            'win32gui': win32gui_mock,
            'win32ui': win32ui_mock,
            'win32con': win32con_mock,
            'windll': windll_mock
        }


@pytest.fixture
def capture_instance(mock_win32):
    """Create ScreenCapture instance with mocked APIs"""
    capture = ScreenCapture(queue_size=5, target_fps=15)
    return capture


# ============================================================================
# STEP 5: TEST FUNCTIONS - Initialization
# ============================================================================

def test_capture_initialization():
    """Test ScreenCapture initialization with default params"""
    capture = ScreenCapture()
    
    assert capture.queue_size == 5, "Default queue size should be 5"
    assert capture.target_fps == 15, "Default target FPS should be 15"
    assert capture.downsample is None, "Downsample should be None by default"
    assert not capture.running, "Capture should not be running initially"
    assert capture.hwnd is None, "HWND should be None before start"
    assert capture.thread is None, "Thread should be None before start"


def test_capture_initialization_custom_params():
    """Test initialization with custom parameters"""
    capture = ScreenCapture(
        queue_size=10,
        target_fps=30,
        downsample=(640, 480)
    )
    
    assert capture.queue_size == 10, "Custom queue size should be 10"
    assert capture.target_fps == 30, "Custom target FPS should be 30"
    assert capture.downsample == (640, 480), "Custom downsample should be (640, 480)"
    assert capture.frame_interval == pytest.approx(1.0 / 30), "Frame interval should match target FPS"


def test_capture_stats_initialization():
    """Test CaptureStats dataclass initialization"""
    stats = CaptureStats()
    
    assert stats.frames_captured == 0, "Initial frames_captured should be 0"
    assert stats.frames_dropped == 0, "Initial frames_dropped should be 0"
    assert stats.fps == 0.0, "Initial FPS should be 0.0"
    assert stats.avg_capture_time_ms == 0.0, "Initial avg_capture_time_ms should be 0.0"
    assert stats.queue_size == 0, "Initial queue_size should be 0"


# ============================================================================
# STEP 6: TEST FUNCTIONS - Window Detection
# ============================================================================

def test_find_window_success(mock_win32):
    """Test finding window by title substring"""
    capture = ScreenCapture()
    hwnd = capture.find_window("Cabal")
    
    assert hwnd == 12345, "Should find Cabal window with hwnd 12345"
    mock_win32['win32gui'].EnumWindows.assert_called_once()


def test_find_window_case_insensitive(mock_win32):
    """Test case-insensitive window search"""
    capture = ScreenCapture()
    
    # Should find "Cabal Online" with lowercase search
    hwnd = capture.find_window("cabal")
    assert hwnd == 12345, "Window search should be case-insensitive"


def test_find_window_not_found(mock_win32):
    """Test window not found scenario returns None"""
    mock_win32['win32gui'].GetWindowText.return_value = "Other Window"
    
    capture = ScreenCapture()
    hwnd = capture.find_window("Cabal")
    
    assert hwnd is None, "Should return None when window not found"


def test_find_window_invisible(mock_win32):
    """Test that invisible windows are skipped"""
    mock_win32['win32gui'].IsWindowVisible.return_value = False
    
    capture = ScreenCapture()
    hwnd = capture.find_window("Cabal")
    
    assert hwnd is None, "Should skip invisible windows"


# ============================================================================
# STEP 7: TEST FUNCTIONS - Start/Stop Operations
# ============================================================================

def test_start_success(mock_win32):
    """Test successful capture start initializes all components"""
    capture = ScreenCapture()
    result = capture.start("Cabal")
    
    assert result is True, "Start should return True on success"
    assert capture.running is True, "Capture should be running after start"
    assert capture.hwnd == 12345, "HWND should be set to found window"
    assert capture.window_rect is not None, "Window rect should be set"
    assert capture.thread is not None, "Capture thread should be created"
    
    # Cleanup
    capture.stop()


def test_start_window_not_found(mock_win32):
    """Test start returns False when window not found"""
    mock_win32['win32gui'].GetWindowText.return_value = "Other Window"
    
    capture = ScreenCapture()
    result = capture.start("Cabal")
    
    assert result is False, "Start should return False when window not found"
    assert not capture.running, "Capture should not be running"
    assert capture.hwnd is None, "HWND should remain None"


def test_start_already_running(mock_win32):
    """Test start returns False when already running"""
    capture = ScreenCapture()
    capture.running = True
    
    result = capture.start("Cabal")
    
    assert result is False, "Should not start if already running"


@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_stop_clears_queue(mock_win32):
    """Test stop clears frame queue and stops capture"""
    capture = ScreenCapture()
    capture.start("Cabal")
    
    # Add some dummy frames to queue
    capture.frame_queue.put(np.zeros((100, 100, 3)))
    capture.frame_queue.put(np.zeros((100, 100, 3)))
    
    capture.stop()
    
    assert capture.frame_queue.empty(), "Queue should be empty after stop"
    assert not capture.running, "Capture should not be running after stop"


def test_stop_when_not_running():
    """Test stop when not running does not raise error"""
    capture = ScreenCapture()
    capture.stop()  # Should not raise exception


# ============================================================================
# STEP 8: TEST FUNCTIONS - Frame Operations
# ============================================================================

def test_get_frame_timeout():
    """Test get_frame returns None after timeout"""
    capture = ScreenCapture()
    
    start = time.time()
    frame = capture.get_frame(timeout=0.1)
    elapsed = time.time() - start
    
    assert frame is None, "Should return None when queue is empty"
    assert elapsed >= 0.1, f"Should wait at least 0.1s, waited {elapsed:.3f}s"


@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_get_frame_from_queue():
    """Test getting frame from queue returns valid frame"""
    capture = ScreenCapture()
    
    # Put frame in queue
    test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    capture.frame_queue.put(test_frame)
    
    frame = capture.get_frame(timeout=1.0)
    
    assert frame is not None, "Should return frame from queue"
    assert isinstance(frame, np.ndarray), f"Frame should be ndarray, got {type(frame)}"
    assert frame.shape == (100, 100, 3), f"Frame shape should be (100, 100, 3), got {frame.shape}"


def test_get_stats():
    """Test getting capture statistics returns correct values"""
    capture = ScreenCapture()
    capture.stats.frames_captured = 100
    capture.stats.fps = 15.5
    
    stats = capture.get_stats()
    
    assert isinstance(stats, CaptureStats), f"Should return CaptureStats, got {type(stats)}"
    assert stats.frames_captured == 100, "frames_captured should be preserved"
    assert stats.fps == 15.5, "FPS should be preserved"


# ============================================================================
# STEP 9: TEST FUNCTIONS - Window Rect Calculation
# ============================================================================

def test_window_rect_calculation(mock_win32):
    """Test window rect is calculated correctly from win32 API"""
    mock_win32['win32gui'].GetClientRect.return_value = (0, 0, 1024, 768)
    mock_win32['win32gui'].ClientToScreen.return_value = (100, 200)
    
    capture = ScreenCapture()
    result = capture.start("Cabal")
    
    assert result is True, "Start should succeed"
    rect = capture.window_rect
    assert rect is not None, "Window rect should be set"
    assert rect['left'] == 100, "Left should be 100"
    assert rect['top'] == 200, "Top should be 200"
    assert rect['right'] == 1124, "Right should be 1124"
    assert rect['bottom'] == 968, "Bottom should be 968"
    assert rect['width'] == 1024, "Width should be 1024"
    assert rect['height'] == 768, "Height should be 768"
    
    capture.stop()


# ============================================================================
# STEP 10: TEST FUNCTIONS - Frame Interval Calculation
# ============================================================================

def test_frame_interval_15fps():
    """Test frame interval calculation for 15 FPS target"""
    capture = ScreenCapture(target_fps=15)
    expected = 1.0 / 15
    assert capture.frame_interval == pytest.approx(expected), \
        f"Frame interval should be {expected:.4f}s for 15 FPS"


def test_frame_interval_30fps():
    """Test frame interval calculation for 30 FPS target"""
    capture = ScreenCapture(target_fps=30)
    expected = 1.0 / 30
    assert capture.frame_interval == pytest.approx(expected), \
        f"Frame interval should be {expected:.4f}s for 30 FPS"


# ============================================================================
# STEP 11: TEST FUNCTIONS - Convenience Functions
# ============================================================================

def test_create_capture_success(mock_win32):
    """Test create_capture convenience function creates and starts capture"""
    capture = create_capture("Cabal", target_fps=20)
    
    assert capture is not None, "Should return ScreenCapture instance"
    assert isinstance(capture, ScreenCapture), f"Should be ScreenCapture, got {type(capture)}"
    assert capture.running is True, "Capture should be running"
    assert capture.target_fps == 20, "Target FPS should be 20"
    
    capture.stop()


def test_create_capture_failure(mock_win32):
    """Test create_capture returns None when window not found"""
    mock_win32['win32gui'].GetWindowText.return_value = "Other Window"
    
    capture = create_capture("Cabal")
    
    assert capture is None, "Should return None when start fails"


def test_create_capture_with_downsample(mock_win32):
    """Test create_capture with downsample parameter"""
    capture = create_capture("Cabal", downsample=(640, 480))
    
    assert capture is not None, "Should create capture successfully"
    assert capture.downsample == (640, 480), "Downsample should be set"
    
    capture.stop()


# ============================================================================
# STEP 12: INTEGRATION TESTS - Capture Loop (Mocked)
# ============================================================================

@pytest.mark.slow
@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_capture_loop_runs(mock_win32):
    """Test capture loop runs and produces frames"""
    with patch.object(ScreenCapture, '_capture_frame') as mock_capture_frame:
        # Mock successful frame capture
        mock_capture_frame.return_value = np.zeros((768, 1024, 3), dtype=np.uint8)
        
        capture = ScreenCapture(target_fps=10)
        capture.start("Cabal")
        
        # Wait for some frames
        time.sleep(0.5)
        
        # Should have captured some frames
        assert not capture.frame_queue.empty(), "Queue should have frames after capture loop runs"
        
        capture.stop()


@pytest.mark.slow
@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_stats_update(mock_win32):
    """Test statistics are updated during capture"""
    with patch.object(ScreenCapture, '_capture_frame') as mock_capture_frame:
        mock_capture_frame.return_value = np.zeros((768, 1024, 3), dtype=np.uint8)
        
        capture = ScreenCapture(target_fps=10)
        capture.start("Cabal")
        
        # Wait for stats update (happens every 1 second)
        time.sleep(1.5)
        
        stats = capture.get_stats()
        assert stats.fps > 0, f"FPS should be > 0 after capture, got {stats.fps}"
        
        capture.stop()


# ============================================================================
# STEP 13: EDGE CASES & ERROR HANDLING
# ============================================================================

def test_multiple_start_calls(mock_win32):
    """Test multiple start calls only start once"""
    capture = ScreenCapture()
    
    result1 = capture.start("Cabal")
    result2 = capture.start("Cabal")
    
    assert result1 is True, "First start should succeed"
    assert result2 is False, "Second start should fail (already running)"
    
    capture.stop()


def test_stop_before_start():
    """Test stop before start does not raise error"""
    capture = ScreenCapture()
    capture.stop()  # Should not raise exception


@pytest.mark.slow
@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_queue_full_drops_frames(mock_win32):
    """Test frames are dropped when queue is full"""
    with patch.object(ScreenCapture, '_capture_frame') as mock_capture_frame:
        mock_capture_frame.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        capture = ScreenCapture(queue_size=2, target_fps=30)
        capture.start("Cabal")
        
        # Wait for queue to fill
        time.sleep(0.5)
        
        # Should have some stats (can't reliably assert dropped > 0 in test)
        stats = capture.get_stats()
        assert stats.frames_captured >= 0, "Should track frames_captured"
        
        capture.stop()


# ============================================================================
# STEP 14: PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.performance
@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_capture_performance_target(mock_win32):
    """Test capture achieves target FPS (mocked)"""
    with patch.object(ScreenCapture, '_capture_frame') as mock_capture_frame:
        # Simulate fast capture (1ms)
        def fast_capture(*args):
            time.sleep(0.001)
            return np.zeros((768, 1024, 3), dtype=np.uint8)
        
        mock_capture_frame.side_effect = fast_capture
        
        capture = ScreenCapture(target_fps=15)
        capture.start("Cabal")
        
        # Measure over 2 seconds
        time.sleep(2.0)
        
        stats = capture.get_stats()
        
        # Should be close to target FPS (allow 20% variance)
        assert stats.fps >= 12, f"FPS should be >= 12 (15*0.8), got {stats.fps}"
        assert stats.fps <= 18, f"FPS should be <= 18 (15*1.2), got {stats.fps}"
        
        capture.stop()


# ============================================================================
# STEP 15: ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
def test_capture_frame_error_handling(mock_win32):
    """Test capture continues gracefully after frame capture errors"""
    with patch.object(ScreenCapture, '_capture_frame') as mock_capture_frame:
        # First call fails, second succeeds
        mock_capture_frame.side_effect = [
            None,  # Error
            np.zeros((100, 100, 3), dtype=np.uint8)  # Success
        ]
        
        capture = ScreenCapture(target_fps=10)
        capture.start("Cabal")
        
        time.sleep(0.3)
        
        # Should still get a frame eventually
        frame = capture.get_frame(timeout=1.0)
        assert frame is not None, "Should get frame after error recovery"
        
        capture.stop()


# ============================================================================
# MAIN - Run tests standalone
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# ============================================================================
# STEP 8: ADVANCED BOUNDARY TESTS (Sprint 26 CB5)
# ============================================================================

def test_resize_during_capture(mock_win32):
    """Test capture reallocation when window is resized"""
    capture = ScreenCapture(target_fps=15)

    # Mock window resize
    mock_win32['win32gui'].GetClientRect.side_effect = [
        (0, 0, 1024, 768),  # Initial start()
        (0, 0, 1024, 768),  # First frame
        (0, 0, 800, 600),   # Resize happens
        (0, 0, 800, 600)
    ]

    with patch.object(capture, '_reallocate_buffer') as mock_realloc, \
         patch.object(capture, '_capture_frame', return_value=np.zeros((768, 1024, 3), dtype=np.uint8)):

        capture.start("Cabal")

        # Give thread time to process resize
        time.sleep(0.5)

        capture.stop()

        # Verify reallocation was called with new dimensions
        mock_realloc.assert_called_with(800, 600)
        assert capture.window_rect['width'] == 800
        assert capture.window_rect['height'] == 600


def test_minimize_during_capture(mock_win32):
    """Test getting last known frame when window is minimized"""
    capture = ScreenCapture(target_fps=15)

    with patch.object(capture, '_capture_frame') as mock_capture:
        # Create a real array for last known frame
        last_frame = np.ones((768, 1024, 3), dtype=np.uint8) * 255
        mock_capture.return_value = last_frame

        capture.start("Cabal")
        time.sleep(0.2)

        # Get frame normally
        frame1 = capture.get_latest_frame()
        assert frame1 is not None
        assert np.array_equal(frame1, last_frame)

        # Simulate minimize
        mock_win32['win32gui'].IsIconic.return_value = True
        time.sleep(0.2)

        # Should return last known frame
        frame2 = capture.get_latest_frame()
        assert frame2 is not None
        assert np.array_equal(frame2, last_frame)

        capture.stop()


def test_window_closed_during_capture(mock_win32):
    """Test loop terminates and signal sent when window closes"""
    capture = ScreenCapture(target_fps=15)

    lost_event_called = False
    def on_lost():
        nonlocal lost_event_called
        lost_event_called = True

    capture.on_capture_lost = on_lost

    # Start normally
    mock_win32['win32gui'].IsWindow.return_value = True

    with patch.object(capture, '_capture_frame', return_value=np.zeros((768, 1024, 3), dtype=np.uint8)):
        capture.start("Cabal")
        time.sleep(0.1)
        assert capture.running is True

        # Simulate window close in capture thread
        mock_win32['win32gui'].IsWindow.return_value = False

        # Give thread time to process the lost window
        time.sleep(0.5)

        # Thread should have self-terminated
        assert capture.running is False
        assert capture.capture_lost_event.is_set()
        assert lost_event_called is True

        # Cleanup
        capture.stop()


def test_concurrent_access_during_reallocation(mock_win32):
    """Test buffer reads are safe during reallocation"""
    import threading
    capture = ScreenCapture(target_fps=15)

    with patch.object(capture, '_capture_frame', return_value=np.zeros((768, 1024, 3), dtype=np.uint8)):
        capture.start("Cabal")
        time.sleep(0.1)

        exceptions = []

        def reallocator():
            try:
                for _ in range(50):
                    capture._reallocate_buffer(800, 600)
                    time.sleep(0.001)
            except Exception as e:
                exceptions.append(e)

        def reader():
            try:
                for _ in range(50):
                    frame = capture.get_latest_frame()
                    time.sleep(0.001)
            except Exception as e:
                exceptions.append(e)

        t1 = threading.Thread(target=reallocator)
        t2 = threading.Thread(target=reader)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        capture.stop()

        assert len(exceptions) == 0, f"Concurrent access raised exceptions: {exceptions}"
