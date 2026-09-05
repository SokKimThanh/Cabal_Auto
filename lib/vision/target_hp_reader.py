import time
from lib.vision.target_bar_detector import TargetBarDetector

class TargetHPReader:
    def __init__(self, target_bar_detector: TargetBarDetector):
        self.detector = target_bar_detector
        self.last_drawn_percent = 100.0
        self.last_draw_time = 0.0
        self.throttle_ms = 100
        self.min_delta_percent = 0.5

    def calculate_target_hp_percent(self, frame) -> float:
        now = time.monotonic()
        current_percent = self.detector.get_hp_percentage(frame)

        # Check time window
        time_elapsed = (now - self.last_draw_time) * 1000
        if time_elapsed < self.throttle_ms:
            return self.last_drawn_percent

        # Time OK, check delta
        delta = abs(current_percent - self.last_drawn_percent)
        if delta >= self.min_delta_percent:  # ✅ AND logic
            self.last_drawn_percent = current_percent
            self.last_draw_time = now

        # Death signal
        if current_percent == 0.0:
            self.last_drawn_percent = 0.0
            return 0.0

        return self.last_drawn_percent

    def reset(self):
        self.last_drawn_percent = 100.0
        self.last_draw_time = 0.0
