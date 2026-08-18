"""
Monster Detector - Real-time detection loop with state management
Sprint 23 Phase 7 Batch 1

Provides:
- Background detection loop with configurable interval
- Thread-safe state management
- Detection state machine (Searching/Detected/Tracking/Lost)
- Callback system for detection events
- Integration with VisionEngine and ScreenCapture

Architecture:
- Runs in separate thread for non-blocking operation
- Thread-safe access to detection results
- Event-driven callbacks for state changes
- Graceful start/stop/pause/resume controls
"""

import time
import logging
import threading
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
from lib.vision.vision_engine import VisionEngine, Detection

if sys.platform == "win32":
    from lib.system.screen_capture import ScreenCapture
else:
    ScreenCapture = None  # type: ignore

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =====================================================================
# Data Classes & Enums
# =====================================================================

class DetectionState(Enum):
    """Detection state machine states"""
    SEARCHING = "searching"      # No detections, actively searching
    DETECTED = "detected"        # Initial detection found
    TRACKING = "tracking"        # Stable tracking established
    LOST = "lost"               # Lost target, timeout before searching


@dataclass
class DetectionStats:
    """Statistics for detection performance"""
    fps: float = 0.0
    latency_ms: float = 0.0
    total_detections: int = 0
    frames_processed: int = 0
    capture_time_ms: float = 0.0
    detection_time_ms: float = 0.0


# =====================================================================
# Monster Detector
# =====================================================================

class MonsterDetector:
    """
    Real-time monster detection with background thread
    
    Features:
    - Configurable detection interval (default 100ms = 10 FPS)
    - Thread-safe state management with locks
    - Detection state machine for UI feedback
    - Callback system for detection events
    - Performance metrics tracking
    
    Usage:
        detector = MonsterDetector(vision_engine, screen_capture)
        detector.on_detections_changed(my_callback)
        detector.start(detection_interval=0.1)
        # ... detector runs in background ...
        detector.stop()
    """
    
    def __init__(
        self, 
        vision_engine: VisionEngine,
        screen_capture: ScreenCapture,
        target_rect: Optional[Dict[str, int]] = None,
        stable_frames_threshold: int = 3,
        lost_timeout_sec: float = 3.0
    ):
        """
        Initialize detector
        
        Args:
            vision_engine: VisionEngine instance for template matching
            screen_capture: ScreenCapture instance for game capture
            target_rect: Optional initial capture region
            stable_frames_threshold: Frames needed to transition DETECTED -> TRACKING
            lost_timeout_sec: Seconds to wait before LOST -> SEARCHING
        """
        self._vision_engine = vision_engine
        self._screen_capture = screen_capture
        self._target_rect = target_rect
        
        # Thread management
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False
        self._lock = threading.RLock()  # Reentrant lock for nested access
        
        # Detection state
        self._detection_interval = 0.1  # 100ms default
        self._latest_detections: List[Detection] = []
        self._detection_state = DetectionState.SEARCHING
        self._state_changed_time = time.time()
        
        # State machine configuration
        self._stable_frames_threshold = stable_frames_threshold
        self._lost_timeout_sec = lost_timeout_sec
        self._stable_frame_count = 0
        
        # Statistics
        self._stats = DetectionStats()
        self._last_frame_time = 0.0
        self._frame_count = 0
        
        # Callbacks
        self._detection_callbacks: List[Callable[[List[Detection]], None]] = []
        self._state_callbacks: List[Callable[[DetectionState], None]] = []
        
        logger.info("[MonsterDetector] Initialized")
    
    # =================================================================
    # Public API - Thread Control
    # =================================================================
    
    def start(self, detection_interval: float = 0.1) -> bool:
        """
        Start detection loop in background thread
        
        Args:
            detection_interval: Time between detections in seconds (default 0.1 = 10 FPS)
            
        Returns:
            True if started successfully, False if already running
        """
        with self._lock:
            if self._running:
                logger.warning("[MonsterDetector] Already running")
                return False
            
            self._detection_interval = detection_interval
            self._running = True
            self._paused = False
            
            # Create and start thread
            self._thread = threading.Thread(
                target=self._detection_loop,
                name="MonsterDetector",
                daemon=True
            )
            self._thread.start()
            
            logger.info(
                f"[MonsterDetector] Started (interval={detection_interval*1000:.0f}ms)"
            )
            return True
    
    def stop(self) -> bool:
        """
        Stop detection loop gracefully
        
        Returns:
            True if stopped successfully, False if not running
        """
        with self._lock:
            if not self._running:
                logger.warning("[MonsterDetector] Not running")
                return False
            
            self._running = False
            self._paused = False
        
        # Wait for thread to finish (outside lock to prevent deadlock)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            
        logger.info("[MonsterDetector] Stopped")
        return True
    
    def pause(self) -> bool:
        """
        Pause detection temporarily (thread keeps running)
        
        Returns:
            True if paused, False if not running
        """
        with self._lock:
            if not self._running:
                logger.warning("[MonsterDetector] Not running, cannot pause")
                return False
            
            self._paused = True
            logger.info("[MonsterDetector] Paused")
            return True
    
    def resume(self) -> bool:
        """
        Resume paused detection
        
        Returns:
            True if resumed, False if not paused or not running
        """
        with self._lock:
            if not self._running:
                logger.warning("[MonsterDetector] Not running, cannot resume")
                return False
            
            if not self._paused:
                logger.warning("[MonsterDetector] Not paused")
                return False
            
            self._paused = False
            logger.info("[MonsterDetector] Resumed")
            return True
    
    # =================================================================
    # Public API - Data Access
    # =================================================================
    
    def get_latest_detections(self) -> List[Detection]:
        """
        Get latest detection results (thread-safe)
        
        Returns:
            List of Detection objects from most recent frame
        """
        with self._lock:
            return self._latest_detections.copy()
    
    def get_state(self) -> DetectionState:
        """
        Get current detection state
        
        Returns:
            Current DetectionState
        """
        with self._lock:
            return self._detection_state
    
    def get_stats(self) -> DetectionStats:
        """
        Get detection statistics
        
        Returns:
            DetectionStats with current metrics
        """
        with self._lock:
            return DetectionStats(
                fps=self._stats.fps,
                latency_ms=self._stats.latency_ms,
                total_detections=self._stats.total_detections,
                frames_processed=self._stats.frames_processed,
                capture_time_ms=self._stats.capture_time_ms,
                detection_time_ms=self._stats.detection_time_ms
            )
    
    def is_running(self) -> bool:
        """Check if detector is running"""
        with self._lock:
            return self._running
    
    def is_paused(self) -> bool:
        """Check if detector is paused"""
        with self._lock:
            return self._paused
    
    # =================================================================
    # Public API - Configuration
    # =================================================================
    
    def set_target_rect(self, rect: Dict[str, int]) -> None:
        """
        Update capture region
        
        Args:
            rect: Dict with keys: left, top, right, bottom, width, height
        """
        with self._lock:
            self._target_rect = rect
            logger.debug(f"[MonsterDetector] Target rect updated: {rect}")
    
    def set_detection_interval(self, interval: float) -> None:
        """
        Update detection interval
        
        Args:
            interval: Time between detections in seconds
        """
        with self._lock:
            self._detection_interval = interval
            logger.info(f"[MonsterDetector] Interval updated: {interval*1000:.0f}ms")
    
    # =================================================================
    # Public API - Callbacks
    # =================================================================
    
    def on_detections_changed(self, callback: Callable[[List[Detection]], None]) -> None:
        """
        Register callback for detection updates
        
        Args:
            callback: Function to call with List[Detection] on each update
        """
        with self._lock:
            if callback not in self._detection_callbacks:
                self._detection_callbacks.append(callback)
                logger.debug("[MonsterDetector] Detection callback registered")
    
    def on_state_changed(self, callback: Callable[[DetectionState], None]) -> None:
        """
        Register callback for state changes
        
        Args:
            callback: Function to call with DetectionState on state change
        """
        with self._lock:
            if callback not in self._state_callbacks:
                self._state_callbacks.append(callback)
                logger.debug("[MonsterDetector] State callback registered")
    
    def remove_detection_callback(self, callback: Callable) -> None:
        """Remove detection callback"""
        with self._lock:
            if callback in self._detection_callbacks:
                self._detection_callbacks.remove(callback)
    
    def remove_state_callback(self, callback: Callable) -> None:
        """Remove state callback"""
        with self._lock:
            if callback in self._state_callbacks:
                self._state_callbacks.remove(callback)
    
    # =================================================================
    # Private - Detection Loop
    # =================================================================
    
    def _detection_loop(self) -> None:
        """
        Main detection loop (runs in background thread)
        
        Loop cycle:
        1. Check if paused
        2. Capture screen
        3. Run detection
        4. Update state
        5. Trigger callbacks
        6. Sleep until next interval
        """
        logger.info("[MonsterDetector] Detection loop started")
        
        while self._running:
            try:
                # Check pause state
                if self._paused:
                    time.sleep(0.05)  # Sleep while paused
                    continue
                
                # Check target rect
                if not self._target_rect:
                    logger.debug("[MonsterDetector] No target rect, skipping frame")
                    time.sleep(self._detection_interval)
                    continue
                
                # Track frame timing
                frame_start = time.time()
                
                # STEP 1: Capture screen
                capture_start = time.time()
                frame = self._capture_frame()
                capture_time = (time.time() - capture_start) * 1000  # ms
                
                if frame is None:
                    logger.debug("[MonsterDetector] Capture failed, skipping frame")
                    time.sleep(self._detection_interval)
                    continue
                
                # STEP 2: Run detection
                detect_start = time.time()
                detections = self._run_detection(frame)
                detect_time = (time.time() - detect_start) * 1000  # ms
                
                # STEP 3: Update state and stats
                with self._lock:
                    self._latest_detections = detections
                    self._frame_count += 1
                    
                    # Update state machine
                    self._update_state(detections)
                    
                    # Update stats
                    self._stats.frames_processed += 1
                    self._stats.total_detections += len(detections)
                    self._stats.capture_time_ms = capture_time
                    self._stats.detection_time_ms = detect_time
                    self._stats.latency_ms = (time.time() - frame_start) * 1000
                    
                    # Calculate FPS
                    if self._last_frame_time > 0:
                        frame_delta = time.time() - self._last_frame_time
                        if frame_delta > 0:
                            self._stats.fps = 1.0 / frame_delta
                    self._last_frame_time = time.time()
                
                # STEP 4: Trigger callbacks (outside lock to prevent deadlock)
                self._trigger_detection_callbacks(detections)
                
                # STEP 5: Sleep until next interval
                elapsed = time.time() - frame_start
                sleep_time = max(0, self._detection_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"[MonsterDetector] Loop error: {e}", exc_info=True)
                time.sleep(self._detection_interval)  # Continue on error
        
        logger.info("[MonsterDetector] Detection loop stopped")
    
    def _capture_frame(self) -> Optional[Any]:
        """
        Capture game screen region
        
        Returns:
            Captured frame or None on error
        """
        try:
            # Use ScreenCapture to get latest frame
            # Note: ScreenCapture runs continuously, we just get latest frame
            frame = self._screen_capture.get_frame(timeout=0.05)
            return frame
            
        except Exception as e:
            logger.error(f"[MonsterDetector] Capture error: {e}")
            return None
    
    def _run_detection(self, frame: Any) -> List[Detection]:
        """
        Run detection pipeline on frame
        
        Args:
            frame: Captured screen frame
            
        Returns:
            List of Detection objects
        """
        try:
            # Use VisionEngine's priority detection pipeline
            detections = self._vision_engine.detect_monster_pipeline(frame)
            return detections
            
        except Exception as e:
            logger.error(f"[MonsterDetector] Detection error: {e}")
            return []
    
    def _trigger_detection_callbacks(self, detections: List[Detection]) -> None:
        """
        Trigger all registered detection callbacks
        
        Args:
            detections: List of detections to pass to callbacks
        """
        # Get callbacks snapshot (thread-safe)
        with self._lock:
            callbacks = self._detection_callbacks.copy()
        
        # Call callbacks outside lock
        for callback in callbacks:
            try:
                callback(detections)
            except Exception as e:
                logger.error(
                    f"[MonsterDetector] Callback error: {e}",
                    exc_info=True
                )
    
    def _trigger_state_callbacks(self, new_state: DetectionState) -> None:
        """
        Trigger all registered state change callbacks
        
        Args:
            new_state: New DetectionState to pass to callbacks
        """
        # Get callbacks snapshot (thread-safe)
        with self._lock:
            callbacks = self._state_callbacks.copy()
        
        # Call callbacks outside lock
        for callback in callbacks:
            try:
                callback(new_state)
            except Exception as e:
                logger.error(
                    f"[MonsterDetector] State callback error: {e}",
                    exc_info=True
                )
    
    # =================================================================
    # Private - State Management
    # =================================================================
    
    def _update_state(self, detections: List[Detection]) -> None:
        """
        Update detection state based on current detections
        
        State machine transitions:
        - SEARCHING -> DETECTED: detections > 0
        - DETECTED -> TRACKING: stable N frames with detections
        - DETECTED -> LOST: detections == 0
        - TRACKING -> LOST: detections == 0
        - LOST -> SEARCHING: timeout exceeded
        
        Args:
            detections: Current frame detections
        """
        current_state = self._detection_state
        new_state = current_state
        has_detections = len(detections) > 0
        time_in_state = time.time() - self._state_changed_time
        
        # State transition logic
        if current_state == DetectionState.SEARCHING:
            if has_detections:
                new_state = DetectionState.DETECTED
                self._stable_frame_count = 1
                logger.info(f"[MonsterDetector] State: SEARCHING -> DETECTED ({len(detections)} found)")
        
        elif current_state == DetectionState.DETECTED:
            if has_detections:
                self._stable_frame_count += 1
                if self._stable_frame_count >= self._stable_frames_threshold:
                    new_state = DetectionState.TRACKING
                    logger.info(
                        f"[MonsterDetector] State: DETECTED -> TRACKING "
                        f"({self._stable_frame_count} stable frames)"
                    )
            else:
                new_state = DetectionState.LOST
                logger.info("[MonsterDetector] State: DETECTED -> LOST (no detections)")
        
        elif current_state == DetectionState.TRACKING:
            if not has_detections:
                new_state = DetectionState.LOST
                logger.info("[MonsterDetector] State: TRACKING -> LOST (target lost)")
            # else: stay in TRACKING
        
        elif current_state == DetectionState.LOST:
            if has_detections:
                new_state = DetectionState.DETECTED
                self._stable_frame_count = 1
                logger.info(f"[MonsterDetector] State: LOST -> DETECTED (reacquired)")
            elif time_in_state >= self._lost_timeout_sec:
                new_state = DetectionState.SEARCHING
                logger.info(
                    f"[MonsterDetector] State: LOST -> SEARCHING "
                    f"(timeout {time_in_state:.1f}s)"
                )
        
        # Apply state change
        if new_state != current_state:
            self._set_state(new_state)
    
    def _set_state(self, new_state: DetectionState) -> None:
        """
        Set new detection state and trigger callbacks
        
        Args:
            new_state: New DetectionState to set
        """
        old_state = self._detection_state
        self._detection_state = new_state
        self._state_changed_time = time.time()
        
        # Reset stable frame counter on certain transitions
        if new_state == DetectionState.SEARCHING or new_state == DetectionState.LOST:
            self._stable_frame_count = 0
        
        # Trigger state callbacks (outside lock to prevent deadlock)
        self._trigger_state_callbacks(new_state)
    
    def get_time_in_state(self) -> float:
        """
        Get time spent in current state
        
        Returns:
            Time in seconds since last state change
        """
        with self._lock:
            return time.time() - self._state_changed_time
    
    # =================================================================
    # Cleanup
    # =================================================================
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._running:
            self.stop()


# =====================================================================
# Module Test
# =====================================================================

if __name__ == "__main__":
    # Quick test
    print("MonsterDetector module loaded")
    print(f"DetectionState enum: {[s.value for s in DetectionState]}")
