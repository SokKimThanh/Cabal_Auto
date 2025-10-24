"""
Unit tests for MonsterDetector
Sprint 23 Phase 7 Batch 1 Task 1.1

Tests:
- Thread lifecycle (start/stop/pause/resume)
- Thread safety (concurrent access)
- Callback system
- State management
- Error handling
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch
from typing import List

from lib.vision.monster_detector import (
    MonsterDetector,
    DetectionState,
    DetectionStats
)
from lib.vision.vision_engine import Detection


@pytest.fixture
def mock_vision_engine():
    """Mock VisionEngine for testing"""
    engine = Mock()
    engine.match_templates = Mock(return_value=[])
    return engine


@pytest.fixture
def mock_screen_capture():
    """Mock ScreenCapture for testing"""
    capture = Mock()
    capture.get_frame = Mock(return_value=Mock())  # Return dummy frame
    return capture


@pytest.fixture
def detector(mock_vision_engine, mock_screen_capture):
    """Create detector instance for testing"""
    return MonsterDetector(
        vision_engine=mock_vision_engine,
        screen_capture=mock_screen_capture,
        target_rect={'left': 0, 'top': 0, 'right': 800, 'bottom': 600, 'width': 800, 'height': 600}
    )


class TestMonsterDetectorInit:
    """Test detector initialization"""
    
    def test_init_success(self, mock_vision_engine, mock_screen_capture):
        """Test successful initialization"""
        detector = MonsterDetector(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture
        )
        
        assert detector is not None
        assert not detector.is_running()
        assert not detector.is_paused()
        assert detector.get_state() == DetectionState.SEARCHING
        assert len(detector.get_latest_detections()) == 0
    
    def test_init_with_target_rect(self, mock_vision_engine, mock_screen_capture):
        """Test initialization with target rect"""
        rect = {'left': 10, 'top': 20, 'width': 800, 'height': 600}
        detector = MonsterDetector(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture,
            target_rect=rect
        )
        
        assert detector is not None
        detector.set_target_rect(rect)  # Should not error


class TestThreadLifecycle:
    """Test thread start/stop/pause/resume"""
    
    def test_start_success(self, detector):
        """Test starting detector"""
        result = detector.start(detection_interval=0.05)
        
        assert result is True
        assert detector.is_running() is True
        assert detector.is_paused() is False
        
        # Cleanup
        detector.stop()
    
    def test_start_twice_fails(self, detector):
        """Test starting already running detector fails"""
        detector.start(detection_interval=0.05)
        result = detector.start(detection_interval=0.05)
        
        assert result is False  # Second start should fail
        
        # Cleanup
        detector.stop()
    
    def test_stop_success(self, detector):
        """Test stopping detector"""
        detector.start(detection_interval=0.05)
        time.sleep(0.1)  # Let it run briefly
        
        result = detector.stop()
        
        assert result is True
        assert detector.is_running() is False
    
    def test_stop_not_running_fails(self, detector):
        """Test stopping non-running detector fails"""
        result = detector.stop()
        
        assert result is False
    
    def test_pause_success(self, detector):
        """Test pausing detector"""
        detector.start(detection_interval=0.05)
        
        result = detector.pause()
        
        assert result is True
        assert detector.is_paused() is True
        assert detector.is_running() is True  # Still running, just paused
        
        # Cleanup
        detector.stop()
    
    def test_pause_not_running_fails(self, detector):
        """Test pausing non-running detector fails"""
        result = detector.pause()
        
        assert result is False
    
    def test_resume_success(self, detector):
        """Test resuming paused detector"""
        detector.start(detection_interval=0.05)
        detector.pause()
        
        result = detector.resume()
        
        assert result is True
        assert detector.is_paused() is False
        
        # Cleanup
        detector.stop()
    
    def test_resume_not_paused_fails(self, detector):
        """Test resuming non-paused detector fails"""
        detector.start(detection_interval=0.05)
        
        result = detector.resume()
        
        assert result is False  # Not paused, so resume fails
        
        # Cleanup
        detector.stop()
    
    def test_resume_not_running_fails(self, detector):
        """Test resuming non-running detector fails"""
        result = detector.resume()
        
        assert result is False


class TestThreadSafety:
    """Test thread-safe operations"""
    
    def test_concurrent_get_detections(self, detector):
        """Test concurrent access to detection results"""
        detector.start(detection_interval=0.05)
        time.sleep(0.1)
        
        # Multiple threads reading concurrently
        results = []
        
        def read_detections():
            for _ in range(10):
                detections = detector.get_latest_detections()
                results.append(len(detections))
                time.sleep(0.01)
        
        threads = [threading.Thread(target=read_detections) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 30  # 3 threads * 10 reads
        
        # Cleanup
        detector.stop()
    
    def test_concurrent_state_access(self, detector):
        """Test concurrent state access"""
        detector.start(detection_interval=0.05)
        
        states = []
        
        def read_state():
            for _ in range(10):
                state = detector.get_state()
                states.append(state)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=read_state) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(states) == 30
        
        # Cleanup
        detector.stop()
    
    def test_set_target_rect_while_running(self, detector):
        """Test updating target rect while running"""
        detector.start(detection_interval=0.05)
        time.sleep(0.05)
        
        new_rect = {'left': 100, 'top': 100, 'width': 400, 'height': 400}
        detector.set_target_rect(new_rect)  # Should not crash
        
        time.sleep(0.1)
        
        # Cleanup
        detector.stop()


class TestCallbackSystem:
    """Test callback registration and triggering"""
    
    def test_register_detection_callback(self, detector):
        """Test registering detection callback"""
        callback = Mock()
        detector.on_detections_changed(callback)
        
        # Start and wait for a few frames
        detector.start(detection_interval=0.05)
        time.sleep(0.2)
        
        # Callback should have been called
        assert callback.call_count > 0
        
        # Cleanup
        detector.stop()
    
    def test_register_state_callback(self, detector):
        """Test registering state callback"""
        callback = Mock()
        detector.on_state_changed(callback)
        
        # Note: State callbacks tested more in Task 1.2
        # For now, just verify registration works
        assert callback in detector._state_callbacks
    
    def test_remove_detection_callback(self, detector):
        """Test removing detection callback"""
        callback = Mock()
        detector.on_detections_changed(callback)
        detector.remove_detection_callback(callback)
        
        assert callback not in detector._detection_callbacks
    
    def test_remove_state_callback(self, detector):
        """Test removing state callback"""
        callback = Mock()
        detector.on_state_changed(callback)
        detector.remove_state_callback(callback)
        
        assert callback not in detector._state_callbacks
    
    def test_callback_receives_detections(self, detector, mock_vision_engine):
        """Test callback receives detection data"""
        # Mock some detections
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0),
            Detection(x=200, y=200, w=50, h=50, score=0.8, template_id='monster2', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        received_detections = []
        
        def callback(detections: List[Detection]):
            received_detections.append(detections)
        
        detector.on_detections_changed(callback)
        detector.start(detection_interval=0.05)
        time.sleep(0.15)  # Wait for a few frames
        
        # Should have received detection updates
        assert len(received_detections) > 0
        
        # Cleanup
        detector.stop()
    
    def test_callback_error_does_not_crash(self, detector):
        """Test that callback errors don't crash detector"""
        def bad_callback(detections):
            raise ValueError("Test error")
        
        detector.on_detections_changed(bad_callback)
        detector.start(detection_interval=0.05)
        time.sleep(0.15)
        
        # Detector should still be running despite callback error
        assert detector.is_running() is True
        
        # Cleanup
        detector.stop()


class TestDataAccess:
    """Test data access methods"""
    
    def test_get_latest_detections(self, detector):
        """Test getting latest detections"""
        detections = detector.get_latest_detections()
        
        assert isinstance(detections, list)
        assert len(detections) == 0  # No detections initially
    
    def test_get_state(self, detector):
        """Test getting current state"""
        state = detector.get_state()
        
        assert state == DetectionState.SEARCHING
    
    def test_get_stats(self, detector):
        """Test getting statistics"""
        stats = detector.get_stats()
        
        assert isinstance(stats, DetectionStats)
        assert stats.fps >= 0
        assert stats.frames_processed == 0  # No frames yet
    
    def test_stats_update_while_running(self, detector):
        """Test stats update during operation"""
        detector.start(detection_interval=0.05)
        time.sleep(0.2)  # Let it run
        
        stats = detector.get_stats()
        
        assert stats.frames_processed > 0
        assert stats.fps > 0
        
        # Cleanup
        detector.stop()


class TestConfiguration:
    """Test configuration methods"""
    
    def test_set_detection_interval(self, detector):
        """Test setting detection interval"""
        detector.set_detection_interval(0.2)
        
        # Interval should be updated (internal state check)
        assert detector._detection_interval == 0.2
    
    def test_set_target_rect(self, detector):
        """Test setting target rect"""
        rect = {'left': 10, 'top': 20, 'width': 800, 'height': 600}
        detector.set_target_rect(rect)
        
        assert detector._target_rect == rect
    
    def test_interval_applied_on_start(self, detector):
        """Test interval is applied when starting"""
        detector.start(detection_interval=0.1)
        
        assert detector._detection_interval == 0.1
        
        # Cleanup
        detector.stop()


class TestErrorHandling:
    """Test error handling"""
    
    def test_capture_error_continues(self, detector, mock_screen_capture):
        """Test that capture errors don't stop detector"""
        # Make capture fail
        mock_screen_capture.get_frame.side_effect = Exception("Capture error")
        
        detector.start(detection_interval=0.05)
        time.sleep(0.2)
        
        # Detector should still be running
        assert detector.is_running() is True
        
        # Cleanup
        detector.stop()
    
    def test_detection_error_continues(self, detector, mock_vision_engine):
        """Test that detection errors don't stop detector"""
        # Make detection fail
        mock_vision_engine.match_templates.side_effect = Exception("Detection error")
        
        detector.start(detection_interval=0.05)
        time.sleep(0.2)
        
        # Detector should still be running
        assert detector.is_running() is True
        
        # Cleanup
        detector.stop()
    
    def test_no_target_rect_skips_frame(self, detector):
        """Test that missing target rect skips frame gracefully"""
        detector.set_target_rect(None)
        
        detector.start(detection_interval=0.05)
        time.sleep(0.1)
        
        stats = detector.get_stats()
        # Should still be running but not processing frames
        assert detector.is_running() is True
        
        # Cleanup
        detector.stop()


class TestCleanup:
    """Test cleanup and resource management"""
    
    def test_stop_waits_for_thread(self, detector):
        """Test that stop() waits for thread to finish"""
        detector.start(detection_interval=0.05)
        time.sleep(0.1)
        
        detector.stop()
        
        # Thread should be stopped
        if detector._thread:
            assert not detector._thread.is_alive()
    
    def test_del_stops_detector(self, detector):
        """Test that __del__ stops running detector"""
        detector.start(detection_interval=0.05)
        time.sleep(0.05)
        
        # Delete detector
        detector.__del__()
        
        # Should be stopped
        assert not detector.is_running()


class TestStateMachine:
    """Test detection state machine (Task 1.2)"""
    
    def test_initial_state_is_searching(self, detector):
        """Test initial state is SEARCHING"""
        assert detector.get_state() == DetectionState.SEARCHING
    
    def test_searching_to_detected_on_detection(self, detector, mock_vision_engine):
        """Test SEARCHING -> DETECTED when detections found"""
        # Mock detections
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.15)  # Wait for a few frames
        
        # Should transition to DETECTED
        state = detector.get_state()
        assert state == DetectionState.DETECTED or state == DetectionState.TRACKING
        
        # Cleanup
        detector.stop()
    
    def test_detected_to_tracking_after_stable_frames(self, detector, mock_vision_engine):
        """Test DETECTED -> TRACKING after N stable frames"""
        # Mock continuous detections
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        # Start with 3 frame threshold
        detector._stable_frames_threshold = 3
        detector.start(detection_interval=0.05)
        
        # Wait for enough frames to reach TRACKING
        time.sleep(0.3)  # ~6 frames at 50ms interval
        
        state = detector.get_state()
        assert state == DetectionState.TRACKING
        
        # Cleanup
        detector.stop()
    
    def test_detected_to_lost_on_no_detection(self, detector, mock_vision_engine):
        """Test DETECTED -> LOST when detections disappear"""
        # First have detections
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.1)  # Let it detect
        
        # Now remove detections
        mock_vision_engine.match_templates.return_value = []
        time.sleep(0.1)  # Wait for state update
        
        state = detector.get_state()
        assert state == DetectionState.LOST
        
        # Cleanup
        detector.stop()
    
    def test_tracking_to_lost_on_no_detection(self, detector, mock_vision_engine):
        """Test TRACKING -> LOST when target lost"""
        # First establish tracking
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        detector._stable_frames_threshold = 2
        
        detector.start(detection_interval=0.05)
        time.sleep(0.2)  # Establish TRACKING
        
        # Verify in TRACKING
        assert detector.get_state() == DetectionState.TRACKING
        
        # Now lose target
        mock_vision_engine.match_templates.return_value = []
        time.sleep(0.1)
        
        state = detector.get_state()
        assert state == DetectionState.LOST
        
        # Cleanup
        detector.stop()
    
    def test_lost_to_searching_after_timeout(self, detector, mock_vision_engine):
        """Test LOST -> SEARCHING after timeout"""
        # Set short timeout for testing
        detector._lost_timeout_sec = 0.2
        
        # First get to LOST state
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.1)  # Get to DETECTED
        
        # Lose target
        mock_vision_engine.match_templates.return_value = []
        time.sleep(0.1)  # Get to LOST
        
        # Wait for timeout
        time.sleep(0.3)  # Wait beyond timeout
        
        state = detector.get_state()
        assert state == DetectionState.SEARCHING
        
        # Cleanup
        detector.stop()
    
    def test_lost_to_detected_on_reacquisition(self, detector, mock_vision_engine):
        """Test LOST -> DETECTED when target reacquired"""
        # Get to LOST state
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.1)  # DETECTED
        
        # Lose target
        mock_vision_engine.match_templates.return_value = []
        time.sleep(0.1)  # LOST
        
        # Reacquire target
        mock_vision_engine.match_templates.return_value = mock_detections
        time.sleep(0.1)
        
        state = detector.get_state()
        assert state == DetectionState.DETECTED or state == DetectionState.TRACKING
        
        # Cleanup
        detector.stop()
    
    def test_state_change_triggers_callback(self, detector, mock_vision_engine):
        """Test state changes trigger callbacks"""
        state_changes = []
        
        def state_callback(state: DetectionState):
            state_changes.append(state)
        
        detector.on_state_changed(state_callback)
        
        # Trigger state change: SEARCHING -> DETECTED
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.15)
        
        # Should have state change callbacks
        assert len(state_changes) > 0
        assert DetectionState.DETECTED in state_changes or DetectionState.TRACKING in state_changes
        
        # Cleanup
        detector.stop()
    
    def test_get_time_in_state(self, detector):
        """Test getting time in current state"""
        detector.start(detection_interval=0.05)
        time.sleep(0.1)
        
        time_in_state = detector.get_time_in_state()
        assert time_in_state >= 0.0
        assert time_in_state < 1.0  # Should be recent
        
        # Cleanup
        detector.stop()
    
    def test_stable_frame_counter_reset_on_lost(self, detector, mock_vision_engine):
        """Test stable frame counter resets when entering LOST state"""
        # Get some stable frames
        mock_detections = [
            Detection(x=100, y=100, w=50, h=50, score=0.9, template_id='monster1', scale=1.0)
        ]
        mock_vision_engine.match_templates.return_value = mock_detections
        
        detector.start(detection_interval=0.05)
        time.sleep(0.1)  # Build up stable frames
        
        # Lose target
        mock_vision_engine.match_templates.return_value = []
        time.sleep(0.1)
        
        # Counter should be reset
        assert detector._stable_frame_count == 0
        
        # Cleanup
        detector.stop()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
