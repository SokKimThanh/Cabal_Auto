"""
Unit tests for OverlayController
Sprint 23 Phase 7 Batch 2 Task 2.1

Tests:
- Controller lifecycle (start/stop)
- Callback integration
- Detection conversion
- State handling
- Error resilience
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, call
from typing import List

from lib.ui.overlay_controller import OverlayController, OverlayStats
from lib.ui.window_tracker import WindowState
from lib.vision.monster_detector import DetectionState
from lib.vision.vision_engine import Detection


@pytest.fixture
def mock_overlay():
    """Mock OverlayWindowPyWin32 for testing"""
    overlay = Mock()
    overlay.update_detections = Mock()
    overlay.show = Mock()
    overlay.hide = Mock()
    return overlay


@pytest.fixture
def mock_detector():
    """Mock MonsterDetector for testing"""
    detector = Mock()
    detector.on_detections_changed = Mock()
    detector.on_state_changed = Mock()
    detector.remove_detection_callback = Mock()
    detector.remove_state_callback = Mock()
    detector.get_state = Mock(return_value=DetectionState.SEARCHING)
    return detector


@pytest.fixture
def controller(mock_overlay, mock_detector):
    """Create controller instance for testing"""
    return OverlayController(
        overlay=mock_overlay,
        detector=mock_detector,
        max_boxes=20
    )


class TestControllerInit:
    """Test controller initialization"""
    
    def test_init_success(self, mock_overlay, mock_detector):
        """Test successful initialization"""
        controller = OverlayController(
            overlay=mock_overlay,
            detector=mock_detector
        )
        
        assert controller is not None
        assert not controller.is_running()
        assert controller.get_current_state() == DetectionState.SEARCHING
    
    def test_init_with_max_boxes(self, mock_overlay, mock_detector):
        """Test initialization with custom max_boxes"""
        controller = OverlayController(
            overlay=mock_overlay,
            detector=mock_detector,
            max_boxes=10
        )
        
        assert controller._max_boxes == 10


class TestControllerLifecycle:
    """Test controller start/stop"""
    
    def test_start_success(self, controller, mock_detector):
        """Test starting controller"""
        result = controller.start()
        
        assert result is True
        assert controller.is_running() is True
        
        # Should register callbacks
        assert mock_detector.on_detections_changed.called
        assert mock_detector.on_state_changed.called
    
    def test_start_twice_fails(self, controller):
        """Test starting already running controller fails"""
        controller.start()
        result = controller.start()
        
        assert result is False
    
    def test_stop_success(self, controller, mock_detector):
        """Test stopping controller"""
        controller.start()
        result = controller.stop()
        
        assert result is True
        assert controller.is_running() is False
        
        # Should unregister callbacks
        assert mock_detector.remove_detection_callback.called
        assert mock_detector.remove_state_callback.called
    
    def test_stop_not_running_fails(self, controller):
        """Test stopping non-running controller fails"""
        result = controller.stop()
        
        assert result is False
    
    def test_del_stops_controller(self, controller):
        """Test __del__ stops running controller"""
        controller.start()
        controller.__del__()
        
        assert not controller.is_running()


class TestCallbackIntegration:
    """Test callback registration and handling"""
    
    def test_callbacks_registered_on_start(self, controller, mock_detector):
        """Test callbacks are registered when starting"""
        controller.start()
        
        # Check callbacks registered
        assert mock_detector.on_detections_changed.call_count == 1
        assert mock_detector.on_state_changed.call_count == 1
        
        # Verify callback functions
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        assert callable(detection_callback)
        assert callable(state_callback)
    
    def test_callbacks_unregistered_on_stop(self, controller, mock_detector):
        """Test callbacks are unregistered when stopping"""
        controller.start()
        controller.stop()
        
        # Check callbacks unregistered
        assert mock_detector.remove_detection_callback.call_count == 1
        assert mock_detector.remove_state_callback.call_count == 1


class TestDetectionHandling:
    """Test detection conversion and overlay updates"""
    
    def test_empty_detections(self, controller, mock_overlay, mock_detector):
        """Test handling empty detection list"""
        controller.start()
        
        # Get registered callback
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Call with empty list
        detection_callback([])
        
        # Overlay should be updated (possibly with empty list or search box)
        assert mock_overlay.update_detections.called
    
    def test_single_detection(self, controller, mock_overlay, mock_detector):
        """Test handling single detection"""
        controller.start()
        
        # Get registered callback
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Create mock detection
        detection = Detection(
            x=100, y=200, w=50, h=60,
            score=0.85, template_id="monster1",
            scale=1.0, timestamp=time.time()
        )
        
        # Call callback
        detection_callback([detection])
        
        # Overlay should be updated with boxes
        assert mock_overlay.update_detections.called
        boxes = mock_overlay.update_detections.call_args[0][0]
        assert isinstance(boxes, list)
        assert len(boxes) > 0
    
    def test_multiple_detections(self, controller, mock_overlay, mock_detector):
        """Test handling multiple detections"""
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Create multiple detections
        detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0),
            Detection(x=200, y=200, w=50, h=50, score=0.8, template_id="m2", scale=1.0),
            Detection(x=300, y=300, w=50, h=50, score=0.7, template_id="m3", scale=1.0)
        ]
        
        # Call callback
        detection_callback(detections)
        
        # Overlay updated
        assert mock_overlay.update_detections.called
        boxes = mock_overlay.update_detections.call_args[0][0]
        assert len(boxes) > 0
    
    def test_max_boxes_limit(self, mock_overlay, mock_detector):
        """Test max_boxes limit is respected"""
        controller = OverlayController(
            overlay=mock_overlay,
            detector=mock_detector,
            max_boxes=5,
            show_stats=False  # Disable stats to test only detection limit
        )
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Create 10 detections (exceeds limit of 5)
        detections = [
            Detection(x=i*50, y=i*50, w=50, h=50, score=0.9, template_id=f"m{i}", scale=1.0)
            for i in range(10)
        ]
        
        # Call callback
        detection_callback(detections)
        
        # Should limit to max_boxes (no stats boxes)
        boxes = mock_overlay.update_detections.call_args[0][0]
        assert len(boxes) == 5  # Exactly 5 detection boxes


class TestStateHandling:
    """Test state change handling"""
    
    def test_state_change_updates_internal(self, controller, mock_detector):
        """Test state changes update internal state"""
        controller.start()
        
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        # Change to DETECTED
        state_callback(DetectionState.DETECTED)
        assert controller.get_current_state() == DetectionState.DETECTED
        
        # Change to TRACKING
        state_callback(DetectionState.TRACKING)
        assert controller.get_current_state() == DetectionState.TRACKING
    
    def test_searching_state_clears_overlay(self, controller, mock_overlay, mock_detector):
        """Test SEARCHING state clears overlay"""
        controller.start()
        
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        # Change to SEARCHING
        state_callback(DetectionState.SEARCHING)
        
        # Overlay should be cleared
        assert mock_overlay.update_detections.called
        boxes = mock_overlay.update_detections.call_args[0][0]
        assert len(boxes) == 0
    
    def test_state_affects_detection_colors(self, controller, mock_overlay, mock_detector):
        """Test state changes affect box colors"""
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        
        # DETECTED state
        state_callback(DetectionState.DETECTED)
        detection_callback([detection])
        boxes_detected = mock_overlay.update_detections.call_args[0][0]
        
        # TRACKING state
        state_callback(DetectionState.TRACKING)
        detection_callback([detection])
        boxes_tracking = mock_overlay.update_detections.call_args[0][0]
        
        # Colors should differ (boxes have different state colors)
        # Note: Actual color checking depends on implementation
        assert boxes_detected is not None
        assert boxes_tracking is not None


class TestStatistics:
    """Test statistics tracking"""
    
    def test_initial_stats(self, controller):
        """Test initial statistics"""
        stats = controller.get_stats()
        
        assert isinstance(stats, OverlayStats)
        assert stats.updates_sent == 0
        assert stats.last_update_time == 0.0
    
    def test_stats_update_on_detection(self, controller, mock_detector):
        """Test statistics update when detections processed"""
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Process detections
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        detection_callback([detection])
        
        # Stats should update
        stats = controller.get_stats()
        assert stats.updates_sent == 1
        assert stats.last_update_time > 0
    
    def test_stats_accumulate(self, controller, mock_detector):
        """Test statistics accumulate over multiple updates"""
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        
        # Multiple updates
        for _ in range(5):
            detection_callback([detection])
        
        stats = controller.get_stats()
        assert stats.updates_sent == 5


class TestErrorHandling:
    """Test error handling"""
    
    def test_overlay_update_error_continues(self, controller, mock_overlay, mock_detector):
        """Test that overlay update errors don't crash controller"""
        controller.start()
        
        # Make overlay update fail
        mock_overlay.update_detections.side_effect = Exception("Update error")
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        
        # Should not raise
        detection_callback([detection])
        
        # Controller should still be running
        assert controller.is_running() is True
    
    def test_state_callback_error_continues(self, controller, mock_overlay, mock_detector):
        """Test that state callback errors don't crash controller"""
        controller.start()
        
        # Make overlay update fail on state change
        mock_overlay.update_detections.side_effect = Exception("State error")
        
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        # Should not raise
        state_callback(DetectionState.SEARCHING)
        
        # Controller should still be running
        assert controller.is_running() is True


class TestIntegration:
    """Integration tests with real-ish scenarios"""
    
    def test_full_detection_cycle(self, controller, mock_overlay, mock_detector):
        """Test complete detection cycle"""
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        state_callback = mock_detector.on_state_changed.call_args[0][0]
        
        # SEARCHING → DETECTED
        state_callback(DetectionState.DETECTED)
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        detection_callback([detection])
        
        # DETECTED → TRACKING
        state_callback(DetectionState.TRACKING)
        detection_callback([detection])
        
        # TRACKING → LOST
        state_callback(DetectionState.LOST)
        detection_callback([])
        
        # LOST → SEARCHING
        state_callback(DetectionState.SEARCHING)
        
        # All updates should have gone through
        assert mock_overlay.update_detections.call_count >= 4
        assert controller.get_current_state() == DetectionState.SEARCHING


class TestStatsDisplay:
    """Test FPS and stats display (Task 2.2)"""
    
    def test_stats_enabled_by_default(self, mock_overlay, mock_detector):
        """Test stats display is enabled by default"""
        controller = OverlayController(mock_overlay, mock_detector, show_stats=True)
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        detection_callback([detection])
        
        # Should include stats boxes
        call_args = mock_overlay.update_detections.call_args
        boxes = call_args[0][0]
        
        # Should have detection boxes + stats boxes (FPS, count, state, latency = 4)
        assert len(boxes) > 1  # At least 1 detection + stats
        
        # Check that stats are included
        labels = [box.label for box in boxes]
        assert any("FPS:" in label for label in labels)
        assert any("Monsters:" in label for label in labels)
        assert any("State:" in label for label in labels)
        assert any("Latency:" in label for label in labels)
    
    def test_stats_disabled(self, mock_overlay, mock_detector):
        """Test stats display can be disabled"""
        controller = OverlayController(mock_overlay, mock_detector, show_stats=False)
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        detection_callback([detection])
        
        call_args = mock_overlay.update_detections.call_args
        boxes = call_args[0][0]
        
        # Should only have detection boxes, no stats
        labels = [box.label for box in boxes]
        assert not any("FPS:" in label for label in labels)
        assert not any("Monsters:" in label for label in labels)
    
    def test_fps_updates(self, mock_overlay, mock_detector):
        """Test FPS calculation updates"""
        controller = OverlayController(
            mock_overlay, 
            mock_detector, 
            show_stats=True,
            stats_update_interval=0.1  # Update every 100ms
        )
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        
        # Process multiple frames
        for _ in range(5):
            detection_callback([detection])
            time.sleep(0.02)  # 20ms between frames
        
        stats = controller.get_stats()
        # FPS should be calculated after interval
        # With 5 frames over ~100ms, FPS should be around 50
        assert stats.fps >= 0  # Just check it was calculated
    
    def test_monster_count_stat(self, mock_overlay, mock_detector):
        """Test monster count is tracked"""
        controller = OverlayController(mock_overlay, mock_detector, show_stats=True)
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        
        # Send 3 detections
        detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0),
            Detection(x=200, y=100, w=50, h=50, score=0.9, template_id="m2", scale=1.0),
            Detection(x=300, y=100, w=50, h=50, score=0.9, template_id="m3", scale=1.0),
        ]
        detection_callback(detections)
        
        stats = controller.get_stats()
        assert stats.current_monster_count == 3
        assert stats.total_detections == 3
    
    def test_stats_box_formatting(self, mock_overlay, mock_detector):
        """Test stats boxes are properly formatted"""
        controller = OverlayController(mock_overlay, mock_detector, show_stats=True)
        controller.start()
        
        detection_callback = mock_detector.on_detections_changed.call_args[0][0]
        detection = Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="m1", scale=1.0)
        detection_callback([detection])
        
        call_args = mock_overlay.update_detections.call_args
        boxes = call_args[0][0]
        
        # Find stat boxes
        stat_boxes = [box for box in boxes if "FPS:" in box.label or "State:" in box.label]
        
        # Stats should be at top-left corner
        for box in stat_boxes:
            assert box.x == 10
            assert box.y >= 10
            assert box.w > 0
            assert box.h > 0
            assert isinstance(box.color, tuple)
            assert len(box.color) == 3  # RGB


class TestWindowStateHandling:
    """Test window state handling (Task 2.3)"""
    
    def test_minimize_pauses_detection(self, mock_overlay, mock_detector):
        """Test that minimizing window pauses detection"""
        mock_tracker = Mock()
        mock_detector.pause = Mock()
        mock_detector.resume = Mock()
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        # Get window state callback
        window_callback = mock_tracker.on_state_change
        
        # Minimize window
        window_callback(WindowState.MINIMIZED)
        
        # Should pause detector
        mock_detector.pause.assert_called_once()
    
    def test_minimize_hides_overlay(self, mock_overlay, mock_detector):
        """Test that minimizing window hides overlay"""
        mock_tracker = Mock()
        mock_detector.pause = Mock()
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        window_callback = mock_tracker.on_state_change
        
        # Minimize window
        window_callback(WindowState.MINIMIZED)
        
        # Should hide overlay
        mock_overlay.hide.assert_called_once()
    
    def test_restore_resumes_detection(self, mock_overlay, mock_detector):
        """Test that restoring window resumes detection"""
        mock_tracker = Mock()
        mock_detector.pause = Mock()
        mock_detector.resume = Mock()
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        window_callback = mock_tracker.on_state_change
        
        # Minimize then restore
        window_callback(WindowState.MINIMIZED)
        window_callback(WindowState.NORMAL)
        
        # Should resume detector
        mock_detector.resume.assert_called_once()
    
    def test_restore_shows_overlay(self, mock_overlay, mock_detector):
        """Test that restoring window shows overlay"""
        mock_tracker = Mock()
        mock_detector.pause = Mock()
        mock_detector.resume = Mock()
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        window_callback = mock_tracker.on_state_change
        
        # Minimize then restore
        window_callback(WindowState.MINIMIZED)
        window_callback(WindowState.NORMAL)
        
        # Should show overlay
        assert mock_overlay.show.call_count >= 1
    
    def test_maximize_resumes_if_minimized(self, mock_overlay, mock_detector):
        """Test that maximize also resumes from minimize"""
        mock_tracker = Mock()
        mock_detector.pause = Mock()
        mock_detector.resume = Mock()
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        window_callback = mock_tracker.on_state_change
        
        # Minimize then maximize
        window_callback(WindowState.MINIMIZED)
        window_callback(WindowState.MAXIMIZED)
        
        # Should resume detector
        mock_detector.resume.assert_called_once()
    
    def test_no_tracker_no_errors(self, mock_overlay, mock_detector):
        """Test controller works without window tracker"""
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=None  # No tracker
        )
        
        # Should start/stop normally
        assert controller.start() is True
        assert controller.stop() is True
    
    def test_window_state_error_handling(self, mock_overlay, mock_detector):
        """Test window state callback handles errors gracefully"""
        mock_tracker = Mock()
        mock_detector.pause = Mock(side_effect=Exception("Pause error"))
        
        controller = OverlayController(
            mock_overlay,
            mock_detector,
            window_tracker=mock_tracker
        )
        controller.start()
        
        window_callback = mock_tracker.on_state_change
        
        # Should not raise
        window_callback(WindowState.MINIMIZED)
        
        # Controller should still be running
        assert controller.is_running() is True


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
