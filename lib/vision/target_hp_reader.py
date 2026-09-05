import time
from lib.vision.target_bar_detector import TargetBarDetector

class TargetHPReader:
    def __init__(self, target_bar_detector: TargetBarDetector):
        self.detector = target_bar_detector
        self.last_hp = 100.0
        self.last_update_time = 0.0
        self.throttle_ms = 150
        self.min_diff = 1.0

    def calculate_target_hp_percent(self, frame) -> float:
        now = time.monotonic()
        # Throttle frequency
        if (now - self.last_update_time) * 1000 < self.throttle_ms:
            return self.last_hp

        current_hp = self.detector.get_hp_percentage(frame)

        # Always update throttle timer
        self.last_update_time = now

        # Jitter smoothing
        if abs(current_hp - self.last_hp) >= self.min_diff or current_hp == 0.0 or current_hp == 100.0:
            self.last_hp = current_hp

        return self.last_hp

    def reset(self):
        self.last_hp = 100.0
        self.last_update_time = 0.0
