import numpy as np

from lib.vision.skill_cooldown_detector import SkillCooldownDetector


def test_cooldown_detection_success():
    detector = SkillCooldownDetector(roi=(0.0, 1.0, 0.0, 1.0), threshold=10.0)

    # Create a baseline frame (all white)
    baseline = np.full((100, 100, 3), 255, dtype=np.uint8)
    detector.set_baseline(baseline)

    # Frame hasn't changed enough
    current1 = np.full((100, 100, 3), 250, dtype=np.uint8)
    assert detector.check_cooldown(current1) is False

    # Frame changed drastically (cooldown overlay, e.g., dark)
    current2 = np.full((100, 100, 3), 100, dtype=np.uint8)
    assert detector.check_cooldown(current2) is True

def test_cooldown_detection_no_baseline():
    detector = SkillCooldownDetector(roi=(0.0, 1.0, 0.0, 1.0), threshold=10.0)
    current = np.full((100, 100, 3), 255, dtype=np.uint8)
    # Should not crash, just return False
    assert detector.check_cooldown(current) is False
