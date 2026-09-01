from lib.vision.target_bar_detector import TargetBarDetector
import numpy as np

detector = TargetBarDetector()
frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

# Check basic is_target_alive
print("Alive with empty frame:", detector.is_target_alive(frame))

# Mock some red health bar
roi_coords = detector._get_roi_coords(1080, 1920)
print("ROI coords:", roi_coords)

top, bottom, left, right = roi_coords
frame[top:bottom, left:right] = [0, 0, 255]  # BGR for Red
print("Alive with red frame:", detector.is_target_alive(frame))
