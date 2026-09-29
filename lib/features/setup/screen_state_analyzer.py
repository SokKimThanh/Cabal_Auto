"""Screen state analyzer — REFACTOR(#6).

Detect class / location / monster presence từ game screen.
Sử dụng template matching cho class icon (ROI cố định).
"""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Vị trí ROI của class icon trong HUD (tỉ lệ so với window size)
# Điều chỉnh theo layout thực tế của Cabal
CLASS_ICON_ROI_RATIO = {
    "left": 0.02,
    "top": 0.02,
    "width": 0.04,
    "height": 0.04,
}

CLASS_MATCH_THRESHOLD = 0.7

CLASS_ICON_DIR = Path(__file__).resolve().parents[3] / "assets" / "class_icons"

class ValidationResult:
    def __init__(self, is_valid: bool, mismatches: List[Dict[str, Any]] = None):
        self.is_valid = is_valid
        self.mismatches = mismatches or []

class ScreenStateAnalyzer:
    """Analyze game screen state via template matching."""

    def __init__(self):
        self._class_templates: Dict[str, np.ndarray] = {}
        self._load_class_templates()

    def _load_class_templates(self):
        """Load class icon templates từ assets."""
        if not CLASS_ICON_DIR.exists():
            logger.warning(f"[Analyzer] Class icon dir not found: {CLASS_ICON_DIR}")
            return

        for icon_path in CLASS_ICON_DIR.glob("*.png"):
            try:
                img = cv2.imread(str(icon_path), cv2.IMREAD_COLOR)
                if img is not None:
                    class_name = icon_path.stem  # blader.png → "blader"
                    self._class_templates[class_name] = img
            except Exception as e:
                logger.error(f"[Analyzer] Load {icon_path} failed: {e}")

        logger.info(f"[Analyzer] Loaded {len(self._class_templates)} class templates")

    def _capture_window(self, hwnd: int) -> Optional[np.ndarray]:
        """Capture screenshot của window."""
        if not hwnd:
            return None
        try:
            from lib.system.screen_capture import ScreenCapture
            import win32gui

            title = win32gui.GetWindowText(hwnd)
            cap = ScreenCapture(queue_size=1, target_fps=1)
            if not cap.start(title):
                return None

            frame = cap.get_frame(timeout=1.0)
            cap.stop()
            return frame
        except Exception as e:
            logger.error(f"[Analyzer] Capture failed: {e}")
            return None

    def _extract_class_roi(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Crop ROI của class icon từ frame."""
        if frame is None or frame.size == 0:
            return None
        h, w = frame.shape[:2]
        x1 = int(w * CLASS_ICON_ROI_RATIO["left"])
        y1 = int(h * CLASS_ICON_ROI_RATIO["top"])
        x2 = x1 + int(w * CLASS_ICON_ROI_RATIO["width"])
        y2 = y1 + int(h * CLASS_ICON_ROI_RATIO["height"])
        return frame[y1:y2, x1:x2]

    def get_character_class_from_screen(self, frame: Optional[np.ndarray]) -> str:
        """Detect class bằng template matching."""
        if frame is None or not self._class_templates:
            return "Unknown"

        roi = self._extract_class_roi(frame)
        if roi is None or roi.size == 0:
            return "Unknown"

        best_class = "Unknown"
        best_score = CLASS_MATCH_THRESHOLD

        for class_name, template in self._class_templates.items():
            # Resize template khớp ROI nếu cần
            if template.shape[:2] != roi.shape[:2]:
                template_resized = cv2.resize(template, (roi.shape[1], roi.shape[0]))
            else:
                template_resized = template

            result = cv2.matchTemplate(roi, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_class = class_name

        return best_class

    def detect_location_type(self, frame: Optional[np.ndarray]) -> str:
        """Detect TOWN/ZONE. TODO: cần asset map indicator."""
        # REFACTOR(#6): Placeholder — cần asset riêng để detect.
        # Hiện tạm dùng heuristic: nếu có HP bar của quái → ZONE.
        return "ZONE"

    def detect_monster_presence(self, frame: Optional[np.ndarray]) -> bool:
        """Detect monster presence bằng HSV target detect."""
        if frame is None:
            return False
        try:
            from lib.vision.vision_engine import get_vision_engine
            engine = get_vision_engine()
            detections = engine.detect_hsv_target(frame)
            return len(detections) > 0
        except Exception as e:
            logger.error(f"[Analyzer] Detect monster failed: {e}")
            return False

    def scan_screen_state(self, hwnd: int) -> Dict[str, Any]:
        """Full scan."""
        frame = self._capture_window(hwnd)

        return {
            "character_class": self.get_character_class_from_screen(frame),
            "character_level": 1,
            "hp_percent": 100.0,
            "mp_percent": 100.0,
            "location": self.detect_location_type(frame),
            "has_monster": self.detect_monster_presence(frame),
            "skill_mismatches": [],
        }

    def validate_skill_keys(self, character_class: str, skill_config: Dict[str, Any]) -> ValidationResult:
        """Compare required_class vs detected_class."""
        # Stub — chưa implement
        return ValidationResult(True, [])
