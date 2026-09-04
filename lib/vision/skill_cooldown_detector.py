import cv2
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger("hunt_loop")


class SkillCooldownDetector:
    """
    Detects if a skill on the hotbar went on cooldown.
    Uses mean absolute pixel difference on a predefined ROI.
    """
    def __init__(self, roi: Tuple[float, float, float, float], threshold: float = 30.0):
        """
        roi: (y_start_ratio, y_end_ratio, x_start_ratio, x_end_ratio)
        threshold: The visual change threshold (e.g. average pixel diff)
        """
        self.roi = roi
        self.threshold = threshold
        self.baseline_frame: Optional[np.ndarray] = None
        self.last_check_frame: Optional[np.ndarray] = None

    def set_baseline(self, frame: np.ndarray):
        """Set the baseline frame right before pressing the skill."""
        self.baseline_frame = self._extract_roi(frame)

    def check_cooldown(self, current_frame: np.ndarray) -> bool:
        """
        Check if the cooldown visual effect is active.
        Returns True if cooldown is detected, False otherwise.
        """
        if self.baseline_frame is None:
            logger.debug("Cannot check cooldown without a baseline frame.")
            return False

        roi_frame = self._extract_roi(current_frame)
        if roi_frame is None or self.baseline_frame is None:
            return False

        if roi_frame.shape != self.baseline_frame.shape:
            return False

        # Convert to grayscale for comparison
        gray_baseline = cv2.cvtColor(self.baseline_frame, cv2.COLOR_BGR2GRAY)
        gray_current = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray_baseline, gray_current)

        # Calculate mean difference
        mean_diff = np.mean(diff)

        # If the visual difference is higher than threshold, we assume a cooldown overlay appeared
        return bool(mean_diff > self.threshold)

    def _extract_roi(self, frame: np.ndarray) -> Optional[np.ndarray]:
        if frame is None:
            return None
        h, w = frame.shape[:2]
        y_start = max(0, int(h * self.roi[0]))
        y_end = min(h, int(h * self.roi[1]))
        x_start = max(0, int(w * self.roi[2]))
        x_end = min(w, int(w * self.roi[3]))

        if y_start >= y_end or x_start >= x_end:
            return None

        return frame[y_start:y_end, x_start:x_end].copy()
