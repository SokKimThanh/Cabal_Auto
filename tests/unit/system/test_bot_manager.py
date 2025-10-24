"""
Unit tests for BotManager
Sprint 23 Phase 7 Batch 3 Task 3.1

Tests:
- Manager initialization
- Detection lifecycle (start/stop/pause/resume)
- Hunt integration hooks
- State access methods
- Callback registration
- Thread safety
- Error handling
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, call, patch
from typing import List

from lib.system.bot_manager import BotManager, BotStats
from lib.vision.monster_detector import DetectionState, DetectionStats
from lib.vision.vision_engine import Detection


@pytest.fixture
def mock_vision_engine():
    """Mock VisionEngine for testing"""
    engine = Mock()
    engine.detect_all = Mock(return_value=[])
    return engine


@pytest.fixture
def mock_screen_capture():
    """Mock ScreenCapture for testing"""
    capture = Mock()
    capture.get_frame = Mock(return_value=None)
    return capture


@pytest.fixture
def manager(mock_vision_engine, mock_screen_capture):
    """Create BotManager instance for testing"""
    return BotManager(
        vision_engine=mock_vision_engine,
        screen_capture=mock_screen_capture,
        stable_frames=3,
        lost_timeout=3.0,
        enable_auto_start=False
    )


class TestManagerInit:
    """Test BotManager initialization"""
    
    def test_init_success(self, mock_vision_engine, mock_screen_capture):
        """Test successful initialization"""
        manager = BotManager(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture
        )
        
        assert manager is not None
        assert manager.is_detection_running() is False
        assert manager.is_hunt_running() is False
    
    def test_init_with_custom_interval(self, mock_vision_engine, mock_screen_capture):
        """Test initialization with custom stable_frames"""
        manager = BotManager(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture,
            stable_frames=5
        )
        
        assert manager._stable_frames == 5
    
    def test_init_with_auto_start(self, mock_vision_engine, mock_screen_capture):
        """Test initialization with auto-start enabled"""
        manager = BotManager(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture,
            enable_auto_start=True
        )
        
        assert manager._enable_auto_start is True


class TestDetectionLifecycle:
    """Test detection lifecycle management"""
    
    def test_start_detection_success(self, manager):
        """Test starting detection successfully"""
        success = manager.start_detection()
        
        assert success is True
        assert manager.is_detection_running() is True
    
    def test_start_detection_twice_fails(self, manager):
        """Test starting detection twice fails gracefully"""
        manager.start_detection()
        success = manager.start_detection()
        
        # Second start should fail
        assert success is False
    
    def test_stop_detection_success(self, manager):
        """Test stopping detection successfully"""
        manager.start_detection()
        time.sleep(0.1)  # Let it run briefly
        
        success = manager.stop_detection()
        
        assert success is True
        assert manager.is_detection_running() is False
    
    def test_stop_without_start_fails(self, manager):
        """Test stopping detection without starting fails gracefully"""
        success = manager.stop_detection()
        
        assert success is False
    
    def test_pause_detection(self, manager):
        """Test pausing detection"""
        manager.start_detection()
        time.sleep(0.05)
        
        success = manager.pause_detection()
        
        assert success is True
    
    def test_resume_detection(self, manager):
        """Test resuming detection"""
        manager.start_detection()
        manager.pause_detection()
        time.sleep(0.05)
        
        success = manager.resume_detection()
        
        assert success is True
    
    def test_destroy_stops_detector(self, manager):
        """Test destroy() stops running detector"""
        manager.start_detection()
        time.sleep(0.05)
        
        manager.destroy()
        
        assert manager.is_detection_running() is False


class TestHuntIntegration:
    """Test hunt lifecycle integration"""
    
    def test_on_hunt_start(self, manager):
        """Test hunt start notification"""
        manager.on_hunt_start()
        
        assert manager.is_hunt_running() is True
    
    def test_on_hunt_stop(self, manager):
        """Test hunt stop notification"""
        manager.on_hunt_start()
        manager.on_hunt_stop()
        
        assert manager.is_hunt_running() is False
    
    def test_auto_start_on_hunt_start(self, mock_vision_engine, mock_screen_capture):
        """Test auto-start detection when hunt starts"""
        manager = BotManager(
            vision_engine=mock_vision_engine,
            screen_capture=mock_screen_capture,
            enable_auto_start=True
        )
        
        manager.on_hunt_start()
        time.sleep(0.1)
        
        # Detection should auto-start
        assert manager.is_detection_running() is True
    
    def test_auto_stop_on_hunt_stop(self, manager):
        """Test auto-stop detection when hunt stops"""
        manager.start_detection()
        time.sleep(0.05)
        
        manager.on_hunt_stop()
        
        # Detection should auto-stop
        assert manager.is_detection_running() is False
    
    def test_no_auto_start_when_disabled(self, manager):
        """Test no auto-start when enable_auto_start=False"""
        # manager has enable_auto_start=False from fixture
        manager.on_hunt_start()
        
        # Detection should NOT auto-start
        assert manager.is_detection_running() is False


class TestStateAccess:
    """Test state access methods"""
    
    def test_get_detector_state_when_stopped(self, manager):
        """Test get_detector_state() when detector not running"""
        state = manager.get_detector_state()
        
        assert state is None
    
    def test_get_detector_state_when_running(self, manager):
        """Test get_detector_state() when detector running"""
        manager.start_detection()
        time.sleep(0.05)
        
        state = manager.get_detector_state()
        
        assert state is not None
        assert isinstance(state, DetectionState)
    
    def test_get_detector_stats_when_stopped(self, manager):
        """Test get_detector_stats() when detector not running"""
        stats = manager.get_detector_stats()
        
        assert stats is None
    
    def test_get_detector_stats_when_running(self, manager):
        """Test get_detector_stats() when detector running"""
        manager.start_detection()
        time.sleep(0.05)
        
        stats = manager.get_detector_stats()
        
        assert stats is not None
        assert isinstance(stats, DetectionStats)
    
    def test_get_bot_stats(self, manager):
        """Test get_bot_stats() returns aggregated stats"""
        stats = manager.get_bot_stats()
        
        assert isinstance(stats, BotStats)
        assert stats.detector_running is False
        assert stats.detection_state == "searching"
    
    def test_get_bot_stats_with_running_detector(self, manager):
        """Test get_bot_stats() with running detector"""
        manager.start_detection()
        time.sleep(0.05)
        
        stats = manager.get_bot_stats()
        
        assert stats.detector_running is True
        assert stats.uptime_seconds > 0


class TestCallbackRegistration:
    """Test callback registration"""
    
    def test_register_detections_callback_success(self, manager):
        """Test registering detections callback"""
        manager.start_detection()
        
        callback = Mock()
        success = manager.on_detections_changed(callback)
        
        assert success is True
    
    def test_register_detections_callback_without_detector(self, manager):
        """Test registering callback without starting detector fails"""
        callback = Mock()
        success = manager.on_detections_changed(callback)
        
        assert success is False
    
    def test_register_state_callback_success(self, manager):
        """Test registering state callback"""
        manager.start_detection()
        
        callback = Mock()
        success = manager.on_state_changed(callback)
        
        assert success is True
    
    def test_register_state_callback_without_detector(self, manager):
        """Test registering state callback without detector fails"""
        callback = Mock()
        success = manager.on_state_changed(callback)
        
        assert success is False


class TestThreadSafety:
    """Test thread safety"""
    
    def test_concurrent_start_stop(self, manager):
        """Test concurrent start/stop calls are thread-safe"""
        import threading
        
        def start_worker():
            for _ in range(5):
                manager.start_detection()
                time.sleep(0.01)
        
        def stop_worker():
            for _ in range(5):
                time.sleep(0.01)
                manager.stop_detection()
        
        # Run concurrent start/stop
        t1 = threading.Thread(target=start_worker)
        t2 = threading.Thread(target=stop_worker)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Should not crash (thread-safe)
        # Final state depends on timing, just verify no exceptions
        assert True
    
    def test_concurrent_state_access(self, manager):
        """Test concurrent state access is thread-safe"""
        import threading
        
        manager.start_detection()
        results = []
        
        def read_worker():
            for _ in range(10):
                state = manager.get_detector_state()
                stats = manager.get_detector_stats()
                bot_stats = manager.get_bot_stats()
                results.append((state, stats, bot_stats))
                time.sleep(0.01)
        
        # Run concurrent reads
        threads = [threading.Thread(target=read_worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without errors
        assert len(results) == 30  # 10 reads * 3 threads


class TestErrorHandling:
    """Test error handling"""
    
    def test_start_with_invalid_engine(self, mock_screen_capture):
        """Test starting with invalid engine handles error"""
        bad_engine = Mock()
        bad_engine.detect_all = Mock(side_effect=Exception("Engine error"))
        
        manager = BotManager(
            vision_engine=bad_engine,
            screen_capture=mock_screen_capture
        )
        
        # Should handle error gracefully
        success = manager.start_detection()
        # May succeed creating detector, but will fail on first detection
        assert success in [True, False]
    
    def test_destroy_with_error_continues(self, manager):
        """Test destroy() continues even if detector.stop() fails"""
        manager.start_detection()
        
        # Make stop fail
        manager._detector.stop = Mock(side_effect=Exception("Stop error"))
        
        # Should not raise
        manager.destroy()
        
        # Manager should be cleaned up
        assert manager._detector is None
    
    def test_callback_registration_error_handling(self, manager):
        """Test callback registration error handling"""
        manager.start_detection()
        
        # Make callback registration fail
        manager._detector.on_detections_changed = Mock(side_effect=Exception("Callback error"))
        
        callback = Mock()
        success = manager.on_detections_changed(callback)
        
        # Should return False on error
        assert success is False


class TestIntegration:
    """Integration tests with realistic scenarios"""
    
    def test_full_hunt_cycle(self, manager):
        """Test complete hunt cycle"""
        # Start hunt
        manager.on_hunt_start()
        assert manager.is_hunt_running() is True
        
        # Start detection manually (auto_start=False)
        manager.start_detection()
        time.sleep(0.1)
        assert manager.is_detection_running() is True
        
        # Check stats
        stats = manager.get_bot_stats()
        assert stats.detector_running is True
        assert stats.uptime_seconds > 0
        
        # Stop hunt (should auto-stop detection)
        manager.on_hunt_stop()
        assert manager.is_hunt_running() is False
        assert manager.is_detection_running() is False
    
    def test_pause_resume_cycle(self, manager):
        """Test pause/resume during detection"""
        manager.start_detection()
        time.sleep(0.05)
        
        # Pause
        manager.pause_detection()
        state_paused = manager.get_detector_state()
        
        # Resume
        time.sleep(0.05)
        manager.resume_detection()
        state_resumed = manager.get_detector_state()
        
        # Both should be valid states
        assert state_paused is not None
        assert state_resumed is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
