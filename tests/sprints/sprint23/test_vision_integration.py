"""
Tests for Vision Engine integration with Screen Capture (Sprint 23 Phase 8)

Tests the integration between VisionEngine and ScreenCapture/WindowManager.
Validates that vision engine can use screen capture as frame source.

Test Categories:
- Integration tests: VisionEngine + ScreenCapture
- Capture management: start/stop capture
- Worker integration: automatic frame source selection
- Statistics: capture stats integration

Author: Sprint 23 Team
Date: 2025-10-23
"""

# =====================================================================
# STEP 1: Platform and Optional Imports Check
# =====================================================================

import sys
import pytest

# Platform check - only run on Windows
pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="Screen capture integration only supported on Windows"
)

# =====================================================================
# STEP 2: Standard Library Imports
# =====================================================================

import time
from typing import Optional
from unittest.mock import Mock, MagicMock, patch, call
import threading

# =====================================================================
# STEP 3: Third-Party Imports (with availability checks)
# =====================================================================

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # type: ignore

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None  # type: ignore

# =====================================================================
# STEP 4: Project Imports
# =====================================================================

from lib.vision.vision_engine import VisionEngine

if sys.platform == "win32":
    from lib.system.screen_capture import ScreenCapture, CaptureStats
    from lib.system.window_manager import WindowManager, WindowInfo


# =====================================================================
# STEP 5: Test Fixtures
# =====================================================================

@pytest.fixture
def vision_engine():
    """Create VisionEngine instance"""
    engine = VisionEngine(config_dir="tests/tmp/vision_config")
    yield engine
    # Cleanup
    if engine.is_capture_active():
        engine.stop_capture()
    if engine.worker_running:
        engine.stop_worker()


@pytest.fixture
def mock_window_manager():
    """Mock WindowManager for testing"""
    with patch('lib.vision.vision_engine.WindowManager') as mock_wm:
        # Setup find_window
        mock_wm.find_window.return_value = 12345  # Mock hwnd
        
        # Setup get_window_info
        mock_info = Mock(spec=WindowInfo)
        mock_info.is_minimized = False
        mock_info.is_maximized = False
        mock_info.is_visible = True
        mock_wm.get_window_info.return_value = mock_info
        
        # Setup set_foreground
        mock_wm.set_foreground.return_value = True
        
        yield mock_wm


@pytest.fixture
def mock_screen_capture():
    """Mock ScreenCapture for testing"""
    with patch('lib.vision.vision_engine.ScreenCapture') as mock_sc:
        # Create mock instance
        mock_instance = MagicMock()
        mock_sc.return_value = mock_instance
        
        # Setup mock methods
        mock_instance.start_capture.return_value = None
        mock_instance.stop_capture.return_value = None
        mock_instance.is_capturing = True
        
        # Setup get_frame to return test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8) if HAS_NUMPY else None
        mock_instance.get_frame.return_value = test_frame
        
        # Setup get_stats
        mock_stats = Mock(spec=CaptureStats)
        mock_stats.fps = 15.0
        mock_stats.frames_captured = 100
        mock_stats.frames_dropped = 5
        mock_stats.queue_size = 3
        mock_stats.last_update = time.time()
        mock_instance.get_stats.return_value = mock_stats
        
        yield mock_sc, mock_instance


# =====================================================================
# STEP 6: Helper Functions
# =====================================================================

def create_test_frame(width: int = 640, height: int = 480) -> Optional[np.ndarray]:
    """Create test frame for testing"""
    if not HAS_NUMPY:
        return None
    return np.zeros((height, width, 3), dtype=np.uint8)


# =====================================================================
# STEP 7: Test Classes - Basic Integration
# =====================================================================

@pytest.mark.unit
@pytest.mark.windows
class TestVisionEngineCapture:
    """Test VisionEngine screen capture methods"""
    
    def test_start_capture_success(self, vision_engine, mock_window_manager, 
                                   mock_screen_capture):
        """Test starting screen capture successfully"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        result = vision_engine.start_capture(window_title="Test Window")
        
        # Verify
        assert result is True
        assert vision_engine.capture_enabled is True
        assert vision_engine.capture_hwnd == 12345
        mock_window_manager.find_window.assert_called_once()
        mock_sc.assert_called_once()
        mock_instance.start_capture.assert_called_once()
    
    def test_start_capture_window_not_found(self, vision_engine, mock_window_manager,
                                           mock_screen_capture):
        """Test starting capture when window not found"""
        mock_window_manager.find_window.return_value = None
        
        # Start capture
        result = vision_engine.start_capture(window_title="NonExistent")
        
        # Verify
        assert result is False
        assert vision_engine.capture_enabled is False
        assert vision_engine.capture_hwnd is None
    
    def test_start_capture_with_fps(self, vision_engine, mock_window_manager,
                                   mock_screen_capture):
        """Test starting capture with custom FPS"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture with 30 FPS
        result = vision_engine.start_capture(window_title="Test", target_fps=30)
        
        # Verify
        assert result is True
        assert vision_engine.params['fps_limit'] == 30
        mock_sc.assert_called_once()
        # Check constructor args
        args, kwargs = mock_sc.call_args
        assert kwargs.get('target_fps') == 30
    
    def test_stop_capture(self, vision_engine, mock_window_manager, 
                         mock_screen_capture):
        """Test stopping screen capture"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start then stop
        vision_engine.start_capture(window_title="Test")
        vision_engine.stop_capture()
        
        # Verify
        assert vision_engine.capture_enabled is False
        assert vision_engine.capture_hwnd is None
        assert vision_engine.screen_capture is None
        mock_instance.stop_capture.assert_called_once()
    
    def test_stop_capture_when_not_active(self, vision_engine):
        """Test stopping capture when not active (should not error)"""
        # Should not raise exception
        vision_engine.stop_capture()
        assert vision_engine.capture_enabled is False


@pytest.mark.unit
@pytest.mark.windows
class TestCaptureFrameAccess:
    """Test frame access from screen capture"""
    
    def test_get_capture_frame_success(self, vision_engine, mock_window_manager,
                                       mock_screen_capture):
        """Test getting frame from capture"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Get frame
        frame = vision_engine.get_capture_frame(timeout=0.5)
        
        # Verify
        assert frame is not None
        if HAS_NUMPY:
            assert isinstance(frame, np.ndarray)
        mock_instance.get_frame.assert_called_once()
    
    def test_get_capture_frame_when_not_active(self, vision_engine):
        """Test getting frame when capture not active"""
        frame = vision_engine.get_capture_frame()
        assert frame is None
    
    def test_is_capture_active(self, vision_engine, mock_window_manager,
                               mock_screen_capture):
        """Test checking if capture is active"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Initially not active
        assert vision_engine.is_capture_active() is False
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        mock_instance.is_capturing = True
        
        # Now active
        assert vision_engine.is_capture_active() is True
        
        # Stop capture
        vision_engine.stop_capture()
        
        # Not active again
        assert vision_engine.is_capture_active() is False


@pytest.mark.unit
@pytest.mark.windows
class TestCaptureStatistics:
    """Test capture statistics integration"""
    
    def test_get_capture_stats(self, vision_engine, mock_window_manager,
                               mock_screen_capture):
        """Test getting capture statistics"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Get stats
        stats = vision_engine.get_capture_stats()
        
        # Verify
        assert stats is not None
        assert 'fps' in stats
        assert 'frames_captured' in stats
        assert 'frames_dropped' in stats
        assert 'queue_size' in stats
        assert stats['fps'] == 15.0
        assert stats['frames_captured'] == 100
        assert stats['frames_dropped'] == 5
        assert stats['queue_size'] == 3
    
    def test_get_capture_stats_when_not_active(self, vision_engine):
        """Test getting stats when capture not active"""
        stats = vision_engine.get_capture_stats()
        assert stats is None


@pytest.mark.unit
@pytest.mark.windows
class TestWindowControl:
    """Test window control integration"""
    
    def test_focus_capture_window(self, vision_engine, mock_window_manager,
                                  mock_screen_capture):
        """Test focusing captured window"""
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Focus window
        result = vision_engine.focus_capture_window()
        
        # Verify
        assert result is True
        mock_window_manager.set_foreground.assert_called_once()
    
    def test_focus_capture_window_when_not_active(self, vision_engine):
        """Test focusing when capture not active"""
        result = vision_engine.focus_capture_window()
        assert result is False


# =====================================================================
# STEP 8: Test Classes - Worker Integration
# =====================================================================

@pytest.mark.unit
@pytest.mark.windows
class TestWorkerIntegration:
    """Test worker thread integration with screen capture"""
    
    def test_start_worker_with_capture(self, vision_engine, mock_window_manager,
                                       mock_screen_capture):
        """Test starting worker with active screen capture"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Start worker without callback (should use capture)
        vision_engine.start_worker()
        
        # Verify
        assert vision_engine.worker_running is True
        assert vision_engine.frame_callback is not None
        
        # Cleanup
        vision_engine.stop_worker()
    
    def test_start_worker_with_callback(self, vision_engine):
        """Test starting worker with custom callback"""
        # Custom callback
        callback = Mock(return_value=create_test_frame())
        
        # Start worker with callback
        vision_engine.start_worker(frame_callback=callback)
        
        # Verify
        assert vision_engine.worker_running is True
        assert vision_engine.frame_callback == callback
        
        # Cleanup
        vision_engine.stop_worker()
    
    def test_start_worker_no_source(self, vision_engine):
        """Test starting worker with no frame source"""
        # Should not start worker
        vision_engine.start_worker()
        
        # Verify
        assert vision_engine.worker_running is False
    
    def test_stop_worker_stops_capture(self, vision_engine, mock_window_manager,
                                      mock_screen_capture):
        """Test that stopping worker also stops capture"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture and worker
        vision_engine.start_capture(window_title="Test")
        vision_engine.start_worker()
        
        # Stop worker
        vision_engine.stop_worker()
        
        # Verify capture also stopped
        assert vision_engine.worker_running is False
        mock_instance.stop_capture.assert_called()


# =====================================================================
# STEP 9: Test Classes - Error Handling
# =====================================================================

@pytest.mark.unit
@pytest.mark.windows
class TestErrorHandling:
    """Test error handling in integration"""
    
    def test_start_capture_exception_handling(self, vision_engine, 
                                              mock_window_manager):
        """Test exception handling during capture start"""
        # Make ScreenCapture raise exception
        with patch('lib.vision.vision_engine.ScreenCapture') as mock_sc:
            mock_sc.side_effect = RuntimeError("GDI error")
            
            # Should handle exception gracefully
            result = vision_engine.start_capture(window_title="Test")
            
            assert result is False
            assert vision_engine.capture_enabled is False
    
    def test_get_frame_exception_handling(self, vision_engine, mock_window_manager,
                                         mock_screen_capture):
        """Test exception handling during frame get"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Make get_frame raise exception
        mock_instance.get_frame.side_effect = RuntimeError("Frame error")
        
        # Should handle exception gracefully
        frame = vision_engine.get_capture_frame()
        assert frame is None
    
    def test_stop_capture_exception_handling(self, vision_engine, mock_window_manager,
                                            mock_screen_capture):
        """Test exception handling during capture stop"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Make stop_capture raise exception
        mock_instance.stop_capture.side_effect = RuntimeError("Stop error")
        
        # Should handle exception gracefully
        vision_engine.stop_capture()
        
        # Should still cleanup state
        assert vision_engine.capture_enabled is False
        assert vision_engine.screen_capture is None


# =====================================================================
# STEP 10: Integration Tests (require real window)
# =====================================================================

@pytest.mark.slow
@pytest.mark.windows
@pytest.mark.skipif(not HAS_NUMPY or not HAS_CV2, 
                   reason="Requires numpy and opencv")
class TestRealIntegration:
    """Integration tests with real components (manual testing)"""
    
    def test_full_integration_flow(self, vision_engine):
        """
        Test full integration flow (requires Notepad window).
        
        This test is marked as slow and should be run manually.
        It requires a real window to capture.
        """
        # Try to find Notepad window
        if sys.platform == "win32" and WindowManager:
            hwnd = WindowManager.find_window(title="Notepad")  # type: ignore
            
            if hwnd:
                # Start capture
                result = vision_engine.start_capture(
                    window_title="Notepad",
                    target_fps=15
                )
                
                if result:
                    # Get some frames
                    frames_received = 0
                    for _ in range(5):
                        frame = vision_engine.get_capture_frame(timeout=0.5)
                        if frame is not None:
                            frames_received += 1
                            assert frame.shape[2] == 3  # BGR
                        time.sleep(0.1)
                    
                    # Get stats
                    stats = vision_engine.get_capture_stats()
                    assert stats is not None
                    assert stats['frames_captured'] > 0
                    
                    # Stop
                    vision_engine.stop_capture()
                    
                    # Verify we got some frames
                    assert frames_received > 0
                else:
                    pytest.skip("Could not start capture")
            else:
                pytest.skip("Notepad window not found")
        else:
            pytest.skip("Not on Windows or WindowManager not available")


# =====================================================================
# STEP 11: Performance Tests
# =====================================================================

@pytest.mark.performance
@pytest.mark.windows
@pytest.mark.skipif(not HAS_NUMPY, reason="Requires numpy")
class TestPerformance:
    """Performance tests for integration"""
    
    def test_frame_callback_overhead(self, vision_engine, mock_window_manager,
                                    mock_screen_capture):
        """Test overhead of using capture as frame callback"""
        mock_sc, mock_instance = mock_screen_capture
        
        # Start capture
        vision_engine.start_capture(window_title="Test")
        
        # Measure frame callback time
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            frame = vision_engine.get_capture_frame(timeout=0.01)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / iterations
        
        # Should be fast (< 5ms per call)
        assert avg_time < 0.005, f"Frame callback too slow: {avg_time*1000:.2f}ms"


# =====================================================================
# STEP 12: Cleanup and Utilities
# =====================================================================

def test_module_imports():
    """Test that all required modules are importable"""
    if sys.platform == "win32":
        assert ScreenCapture is not None
        assert WindowManager is not None
    
    # Vision engine should always be importable
    assert VisionEngine is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
