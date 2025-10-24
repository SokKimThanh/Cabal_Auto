"""
BotManager - Central coordination for hunt bot components
Sprint 23 Phase 7 Batch 3 Task 3.1

Provides:
- MonsterDetector lifecycle management
- Integration with hunt loop
- Thread-safe state access
- Component coordination

Architecture:
- Singleton pattern: One manager per app instance
- Facade pattern: Simplifies component interaction
- Thread-safe: All public methods are thread-safe

Usage:
    manager = BotManager(vision_engine, screen_capture)
    manager.start_detection()
    # ... hunt loop runs ...
    state = manager.get_detector_state()
    manager.stop_detection()
"""

import threading
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from lib.vision.vision_engine import VisionEngine
from lib.system.screen_capture import ScreenCapture
from lib.vision.monster_detector import MonsterDetector, DetectionState, DetectionStats

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class BotStats:
    """Aggregated statistics for bot operations"""
    detector_running: bool = False
    detection_state: str = "searching"
    detections_count: int = 0
    detection_fps: float = 0.0
    uptime_seconds: float = 0.0


# =====================================================================
# Bot Manager
# =====================================================================

class BotManager:
    """
    Central manager for hunt bot components
    
    Coordinates:
    - MonsterDetector lifecycle
    - Component state management
    - Thread-safe access to detector
    
    Thread Safety:
    - All public methods use _lock for synchronization
    - Safe to call from GUI thread or hunt thread
    
    Lifecycle:
    1. __init__() - Create manager with dependencies
    2. start_detection() - Start monster detection
    3. get_detector_state() - Query state during hunt
    4. stop_detection() - Stop detection
    5. destroy() - Cleanup on app shutdown
    """
    
    def __init__(
        self,
        vision_engine: VisionEngine,
        screen_capture: ScreenCapture,
        stable_frames: int = 3,
        lost_timeout: float = 3.0,
        enable_auto_start: bool = False
    ):
        """
        Initialize BotManager
        
        Args:
            vision_engine: VisionEngine instance for detection
            screen_capture: ScreenCapture instance for frame capture
            stable_frames: Frames needed for state transitions (default: 3)
            lost_timeout: Timeout for LOST -> SEARCHING (default: 3.0s)
            enable_auto_start: Auto-start detection on hunt start
        """
        self._vision_engine = vision_engine
        self._screen_capture = screen_capture
        self._stable_frames = stable_frames
        self._lost_timeout = lost_timeout
        self._enable_auto_start = enable_auto_start
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Components
        self._detector: Optional[MonsterDetector] = None
        self._detector_enabled = False
        
        # State tracking
        self._hunt_running = False
        self._start_time: float = 0.0
        
        logger.info("[BotManager] Initialized")
    
    # =================================================================
    # Public API - Lifecycle
    # =================================================================
    
    def start_detection(
        self,
        confidence_threshold: float = 0.7,
        target_rect: Optional[Dict[str, int]] = None
    ) -> bool:
        """
        Start monster detection
        
        Args:
            confidence_threshold: Detection confidence threshold (not used yet)
            target_rect: Optional capture region override
            
        Returns:
            True if started successfully, False otherwise
        """
        with self._lock:
            if self._detector and self._detector.is_running():
                logger.warning("[BotManager] Detector already running")
                return False
            
            try:
                # Create detector if needed
                if not self._detector:
                    self._detector = MonsterDetector(
                        vision_engine=self._vision_engine,
                        screen_capture=self._screen_capture,
                        target_rect=target_rect,
                        stable_frames_threshold=self._stable_frames,
                        lost_timeout_sec=self._lost_timeout
                    )
                    logger.info("[BotManager] Created MonsterDetector")
                
                # Start detection loop
                success = self._detector.start()
                if success:
                    self._detector_enabled = True
                    import time
                    self._start_time = time.time()
                    logger.info("[BotManager] Detection started successfully")
                else:
                    logger.error("[BotManager] Failed to start detection")
                
                return success
                
            except Exception as e:
                logger.error(f"[BotManager] Error starting detection: {e}", exc_info=True)
                return False
    
    def stop_detection(self) -> bool:
        """
        Stop monster detection
        
        Returns:
            True if stopped successfully, False otherwise
        """
        with self._lock:
            if not self._detector:
                logger.warning("[BotManager] No detector to stop")
                return False
            
            try:
                success = self._detector.stop()
                if success:
                    self._detector_enabled = False
                    logger.info("[BotManager] Detection stopped successfully")
                else:
                    logger.warning("[BotManager] Detector was not running")
                
                return success
                
            except Exception as e:
                logger.error(f"[BotManager] Error stopping detection: {e}", exc_info=True)
                return False
    
    def pause_detection(self) -> bool:
        """
        Pause detection (for window minimize, etc.)
        
        Returns:
            True if paused successfully
        """
        with self._lock:
            if not self._detector:
                return False
            
            try:
                success = self._detector.pause()
                if success:
                    logger.info("[BotManager] Detection paused")
                return success
            except Exception as e:
                logger.error(f"[BotManager] Error pausing detection: {e}", exc_info=True)
                return False
    
    def resume_detection(self) -> bool:
        """
        Resume detection after pause
        
        Returns:
            True if resumed successfully
        """
        with self._lock:
            if not self._detector:
                return False
            
            try:
                success = self._detector.resume()
                if success:
                    logger.info("[BotManager] Detection resumed")
                return success
            except Exception as e:
                logger.error(f"[BotManager] Error resuming detection: {e}", exc_info=True)
                return False
    
    def destroy(self) -> None:
        """
        Cleanup manager and all components
        
        Call on app shutdown to ensure clean teardown.
        """
        with self._lock:
            logger.info("[BotManager] Destroying manager...")
            
            # Stop detector
            if self._detector:
                try:
                    self._detector.stop()
                except Exception as e:
                    logger.error(f"[BotManager] Error stopping detector: {e}")
                self._detector = None
            
            self._detector_enabled = False
            self._hunt_running = False
            
            logger.info("[BotManager] Destroyed")
    
    # =================================================================
    # Public API - Hunt Integration
    # =================================================================
    
    def on_hunt_start(self) -> None:
        """
        Called when hunt starts
        
        Auto-starts detection if enabled.
        """
        with self._lock:
            self._hunt_running = True
            logger.info("[BotManager] Hunt started")
            
            # Auto-start detection if enabled
            if self._enable_auto_start and not self._detector_enabled:
                self.start_detection()
    
    def on_hunt_stop(self) -> None:
        """
        Called when hunt stops
        
        Stops detection automatically.
        """
        with self._lock:
            self._hunt_running = False
            logger.info("[BotManager] Hunt stopped")
            
            # Stop detection
            if self._detector_enabled:
                self.stop_detection()
    
    # =================================================================
    # Public API - State Access
    # =================================================================
    
    def get_detector_state(self) -> Optional[DetectionState]:
        """
        Get current detection state
        
        Returns:
            DetectionState or None if detector not running
        """
        with self._lock:
            if self._detector:
                return self._detector.get_state()
            return None
    
    def get_detector_stats(self) -> Optional[DetectionStats]:
        """
        Get detector statistics
        
        Returns:
            DetectionStats or None if detector not running
        """
        with self._lock:
            if self._detector:
                return self._detector.get_stats()
            return None
    
    def get_bot_stats(self) -> BotStats:
        """
        Get aggregated bot statistics
        
        Returns:
            BotStats with current metrics
        """
        with self._lock:
            stats = BotStats()
            
            if self._detector:
                stats.detector_running = self._detector.is_running()
                
                detector_stats = self._detector.get_stats()
                if detector_stats:
                    stats.detections_count = detector_stats.total_detections
                    stats.detection_fps = detector_stats.fps
                
                state = self._detector.get_state()
                if state:
                    stats.detection_state = state.value
            
            # Calculate uptime
            if self._start_time > 0:
                import time
                stats.uptime_seconds = time.time() - self._start_time
            
            return stats
    
    def is_detection_running(self) -> bool:
        """Check if detection is currently running"""
        with self._lock:
            return self._detector is not None and self._detector.is_running()
    
    def is_hunt_running(self) -> bool:
        """Check if hunt is currently active"""
        with self._lock:
            return self._hunt_running
    
    # =================================================================
    # Public API - Callback Registration
    # =================================================================
    
    def on_detections_changed(self, callback) -> bool:
        """
        Register callback for detection updates
        
        Args:
            callback: Function(detections: List[Detection]) -> None
            
        Returns:
            True if registered successfully
        """
        with self._lock:
            if not self._detector:
                logger.warning("[BotManager] No detector to register callback")
                return False
            
            try:
                self._detector.on_detections_changed(callback)
                return True
            except Exception as e:
                logger.error(f"[BotManager] Error registering callback: {e}")
                return False
    
    def on_state_changed(self, callback) -> bool:
        """
        Register callback for state changes
        
        Args:
            callback: Function(state: DetectionState) -> None
            
        Returns:
            True if registered successfully
        """
        with self._lock:
            if not self._detector:
                logger.warning("[BotManager] No detector to register callback")
                return False
            
            try:
                self._detector.on_state_changed(callback)
                return True
            except Exception as e:
                logger.error(f"[BotManager] Error registering callback: {e}")
                return False
    
    # =================================================================
    # Cleanup
    # =================================================================
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.destroy()
        except Exception:
            pass


# =====================================================================
# Module Test
# =====================================================================

if __name__ == "__main__":
    print("BotManager module loaded")
    print(f"BotStats fields: {BotStats.__dataclass_fields__.keys()}")
