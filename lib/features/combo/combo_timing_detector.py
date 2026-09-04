import time
import cv2
import numpy as np
from typing import Optional, Callable
import logging

logger = logging.getLogger("combo_detector")

class CabalComboDetector:
    def __init__(self, hwnd: int,
                 y_ratio_range: tuple = (0.052, 0.062),
                 x_ratio_range: tuple = (0.415, 0.585),
                 hit_zone_x_ratio: float = 0.78,
                 poll_interval_ms: int = 4,
                 cooldown_guard_ms: int = 120,
                 key_press_callback: Callable = None):
        """
        Initialize the Combo Detector.

        Args:
            hwnd: Window handle to track (not strictly needed if we just get frame, but good for context)
            y_ratio_range: Y range of the combo bar relative to screen height
            x_ratio_range: X range of the combo bar relative to screen width
            hit_zone_x_ratio: X ratio within the combo bar representing the sweet spot (e.g. 0.78 = 78%)
            poll_interval_ms: Polling interval in ms when waiting for frame
            cooldown_guard_ms: Time to wait after pressing key to avoid double-presses
            key_press_callback: Callback to execute when hit zone is reached
        """
        self.hwnd = hwnd
        self.y_ratio_range = y_ratio_range
        self.x_ratio_range = x_ratio_range
        self.hit_zone_x_ratio = hit_zone_x_ratio
        self.poll_interval_ms = poll_interval_ms
        self.cooldown_guard_ms = cooldown_guard_ms
        self.key_press_callback = key_press_callback

    def wait_for_hit_zone(self, screen_capture, timeout_sec: float = None, is_target_alive_check: Callable = None) -> bool:
        """
        Wait for the combo bar to reach the hit zone and execute callback.

        Args:
            screen_capture: Instance of ScreenCapture
            timeout_sec: Maximum time to wait. If None, uses default 2.0s
            is_target_alive_check: Optional callback to check if target is still alive

        Returns:
            True if hit zone reached and callback executed, False if timed out
        """
        if timeout_sec is None:
            timeout_sec = 2.0

        start_time = time.time()

        while (time.time() - start_time) < timeout_sec:
            # Check if target is still alive (fast break)
            if is_target_alive_check and not is_target_alive_check():
                logger.debug("Target dead during wait_for_hit_zone")
                return False

            frame = screen_capture.get_latest_frame()
            if frame is None:
                time.sleep(self.poll_interval_ms / 1000.0)
                continue

            h, w = frame.shape[:2]

            # Extract ROI for combo bar
            y1 = int(h * self.y_ratio_range[0])
            y2 = int(h * self.y_ratio_range[1])
            x1 = int(w * self.x_ratio_range[0])
            x2 = int(w * self.x_ratio_range[1])

            # Ensure valid ROI
            if y1 >= y2 or x1 >= x2 or y2 > h or x2 > w:
                time.sleep(self.poll_interval_ms / 1000.0)
                continue

            roi = frame[y1:y2, x1:x2]

            # Calculate pixel column for hit zone
            hit_x = int(roi.shape[1] * self.hit_zone_x_ratio)

            # Check if hit_x is within bounds
            if hit_x >= roi.shape[1]:
                time.sleep(self.poll_interval_ms / 1000.0)
                continue

            # Extract the column
            column = roi[:, hit_x]

            # Convert to HSV to check brightness (V)
            hsv_column = cv2.cvtColor(column.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV)
            v_values = hsv_column[:, :, 2]

            # If we find a bright pixel (Value > 210), trigger
            if np.any(v_values > 210):
                if self.key_press_callback:
                    # Execute callback (sends skill key)
                    self.key_press_callback()

                    # Cooldown guard to prevent double presses
                    # Split into smaller chunks to allow fast break if target dies
                    chunk_ms = 25
                    chunks = self.cooldown_guard_ms // chunk_ms
                    remainder = self.cooldown_guard_ms % chunk_ms

                    for _ in range(chunks):
                        if is_target_alive_check and not is_target_alive_check():
                            # Target died during cooldown, exit early
                            return True
                        time.sleep(chunk_ms / 1000.0)

                    if remainder > 0:
                        if not (is_target_alive_check and not is_target_alive_check()):
                            time.sleep(remainder / 1000.0)

                return True

            time.sleep(self.poll_interval_ms / 1000.0)

        return False
