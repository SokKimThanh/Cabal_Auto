"""
Cabal Combo Bar Timing Detector

Detects the hit-zone sweet spot on the horizontal combo bar and triggers skill execution
at optimal timing to achieve 20+ hit combos without breaking the chain.
"""

import time
import logging
from typing import Optional, Callable
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class CabalComboDetector:
    """
    Detects sweet spot on Cabal's horizontal combo bar and triggers skill presses.
    
    The combo bar is located below the target health bar at the top center of the screen.
    A bright pixel (vạch sáng) moves horizontally, and we detect when it reaches the
    hit-zone (around x_ratio 0.78, between two vertical markers).
    """
    
    # HSV threshold for detecting bright pixel (vạch sáng) on combo bar
    HSV_VALUE_THRESHOLD = 210
    
    # Chunk size for cooldown guard to allow early exit on target death
    COOLDOWN_CHUNK_MS = 25
    
    def __init__(
        self,
        hwnd: int,
        y_ratio_range: tuple = (0.052, 0.062),
        x_ratio_range: tuple = (0.415, 0.585),
        hit_zone_x_ratio: float = 0.78,
        poll_interval_ms: int = 4,
        cooldown_guard_ms: int = 120,
        key_press_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the combo detector.
        
        Args:
            hwnd: Window handle for the game window (for DPI awareness)
            y_ratio_range: (start_ratio, end_ratio) for combo bar vertical position
                          (0.0 = top, 1.0 = bottom)
            x_ratio_range: (left_ratio, right_ratio) for combo bar horizontal bounds
            hit_zone_x_ratio: Horizontal position of the sweet spot (where to detect)
            poll_interval_ms: Sleep between frame checks (milliseconds)
            cooldown_guard_ms: Duration to block after pressing (prevents double-press)
            key_press_callback: Optional callback to fire skill key when sweet spot detected
        """
        self.hwnd = hwnd
        self.y_ratio_range = y_ratio_range
        self.x_ratio_range = x_ratio_range
        self.hit_zone_x_ratio = hit_zone_x_ratio
        self.poll_interval_ms = poll_interval_ms
        self.cooldown_guard_ms = cooldown_guard_ms
        self.key_press_callback = key_press_callback
        
        self._last_trigger_time = 0
        
        logger.debug(
            f"CabalComboDetector initialized: hit_zone_x={hit_zone_x_ratio}, "
            f"cooldown={cooldown_guard_ms}ms, poll={poll_interval_ms}ms"
        )
    
    def wait_for_hit_zone(
        self,
        screen_capture,
        timeout_sec: Optional[float] = None,
        is_target_alive_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Wait for the bright pixel to reach the hit-zone sweet spot.
        
        Args:
            screen_capture: ScreenCapture instance to read frames from
            timeout_sec: Maximum time to wait (None = read from config)
            is_target_alive_check: Optional callback to check if target is still alive.
                                   If provided and returns False during cooldown guard,
                                   exits early to allow fast-break targeting.
        
        Returns:
            True if sweet spot was detected and key pressed
            False if timeout reached without detection
        """
        # Load timeout from config if not provided
        if timeout_sec is None:
            try:
                from lib.data.hunt_config import cfg
                timeout_sec = cfg.get("combo", {}).get("hit_zone_timeout_sec", 2.0)
            except Exception:
                timeout_sec = 2.0
        
        start_time = time.time()
        poll_interval_sec = self.poll_interval_ms / 1000.0
        
        while time.time() - start_time < timeout_sec:
            # Get latest frame
            frame = screen_capture.get_latest_frame()
            
            if frame is None:
                time.sleep(poll_interval_sec)
                continue
            
            # Check for bright pixel in hit-zone
            if self._check_hit_zone(frame):
                # Fire the skill callback
                if self.key_press_callback:
                    try:
                        self.key_press_callback()
                    except Exception as e:
                        logger.error(f"Error calling key_press_callback: {e}")
                
                # Cooldown guard: prevent double-press
                # Split into chunks to allow early exit on target death
                guard_end_time = time.time() + (self.cooldown_guard_ms / 1000.0)
                chunk_sec = self.COOLDOWN_CHUNK_MS / 1000.0
                
                while time.time() < guard_end_time:
                    # Check if target died during cooldown guard
                    if is_target_alive_check and not is_target_alive_check():
                        logger.debug("Target died during cooldown guard - exiting early")
                        return True
                    
                    # Sleep for a chunk
                    remaining = guard_end_time - time.time()
                    sleep_time = min(chunk_sec, remaining)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                return True
            
            time.sleep(poll_interval_sec)
        
        logger.debug(f"Hit-zone timeout after {timeout_sec}s")
        return False
    
    def _check_hit_zone(self, frame: np.ndarray) -> bool:
        """
        Check if the bright pixel is at the hit-zone position.
        
        Args:
            frame: BGR frame from screen capture
        
        Returns:
            True if bright pixel detected at hit-zone
        """
        try:
            h, w = frame.shape[:2]
            
            # Calculate ROI bounds
            y_start = int(h * self.y_ratio_range[0])
            y_end = int(h * self.y_ratio_range[1])
            x_start = int(w * self.x_ratio_range[0])
            x_end = int(w * self.x_ratio_range[1])
            
            # Clamp to frame bounds
            y_start = max(0, y_start)
            y_end = min(h, y_end)
            x_start = max(0, x_start)
            x_end = min(w, x_end)
            
            if y_start >= y_end or x_start >= x_end:
                return False
            
            # Extract ROI
            roi = frame[y_start:y_end, x_start:x_end]
            
            # Calculate hit-zone column relative to ROI
            roi_width = x_end - x_start
            hit_zone_col = int(roi_width * self.hit_zone_x_ratio)
            hit_zone_col = max(0, min(hit_zone_col, roi_width - 1))
            
            # Convert to HSV and check value channel at hit-zone
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Take a vertical line at hit-zone column and check if any pixel is bright
            hit_zone_pixels = hsv_roi[:, hit_zone_col, 2]  # V channel
            
            if np.any(hit_zone_pixels > self.HSV_VALUE_THRESHOLD):
                logger.debug(f"Bright pixel detected at hit-zone: max_v={np.max(hit_zone_pixels)}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error in _check_hit_zone: {e}", exc_info=True)
            return False

