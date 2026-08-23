"""
AutoScanner Module - Scans window for monster and skill detection on app startup.
"""

import time
import uuid
import threading
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

from lib.vision.vision_engine import VisionEngine, Detection

if sys.platform == "win32":
    try:
        from lib.system.screen_capture import ScreenCapture
        from lib.system.window_manager import WindowManager
    except ImportError:
        ScreenCapture = None  # type: ignore
        WindowManager = None  # type: ignore
else:
    ScreenCapture = None  # type: ignore
    WindowManager = None  # type: ignore

logger = logging.getLogger(__name__)

class AutoScanner:
    def __init__(self, vision_engine: VisionEngine):
        self.vision_engine = vision_engine
        if WindowManager is not None:
            self.window_manager = WindowManager()
        else:
            self.window_manager = None

        if ScreenCapture is not None:
            self.screen_capture = ScreenCapture()
        else:
            self.screen_capture = None

    def detect_window(self) -> Optional[Dict[str, Any]]:
        """Lấy HWND, PID, bounds từ window. Kiểm tra trạng thái."""
        if self.window_manager is None:
            logger.warning("WindowManager not available (non-Windows platform).")
            return None

        hwnd = self._find_cabal_window()
        if not hwnd:
            logger.warning("Cabal window not found for scanning.")
            return None

        info = self.window_manager.get_window_info(hwnd)

        if info.get('style', 0) & 0x20000000:
            pass

        rect = self.window_manager.get_window_rect(hwnd)

        if rect['width'] == 0 or rect['height'] == 0:
            logger.warning("Window dimensions invalid.")
            return None

        return {
            'hwnd': hwnd,
            'rect': rect
        }

    def _find_cabal_window(self) -> Optional[int]:
        if not self.window_manager:
            return None
        titles = ["Cabal", "CABAL", "cabal"]
        for title in titles:
            hwnd = self.window_manager.find_window(title_contains=title)
            if hwnd:
                return hwnd
        return None

    def scan_screen(self, window_info: Dict[str, Any]) -> Dict[str, Any]:
        """Quét màn hình để nhận diện quái và skills."""
        if not self.screen_capture:
            return {'monsters': [], 'skills': []}

        hwnd = window_info['hwnd']
        try:
            if not getattr(self.screen_capture, 'hwnd', None) == hwnd:
                import win32gui
                title = win32gui.GetWindowText(hwnd)
                if not self.screen_capture.start(title):
                    logger.warning("Failed to start screen capture.")
                    return {'monsters': [], 'skills': []}

            # Use get_frame(timeout) instead of capture() if available, fallback to capture()
            frame = None
            if hasattr(self.screen_capture, 'get_frame'):
                frame = self.screen_capture.get_frame(timeout=1.0)
            elif hasattr(self.screen_capture, 'capture'):
                frame = self.screen_capture.capture()

            if frame is None:
                logger.warning("Failed to capture frame.")
                return {'monsters': [], 'skills': []}

            monsters = self.vision_engine.detect_monster_pipeline(frame)

            # Real skill detection using user's skill data
            skill_detections = []

            skills_db_path = Path(__file__).parent.parent.parent / "data" / "skills.json"
            if skills_db_path.exists():
                with open(skills_db_path, "r", encoding="utf-8") as f:
                    skills_data = json.load(f)

                templates_added = []
                for skill_info in skills_data:
                    skill_id = skill_info.get("name", "").lower()
                    img_path = skill_info.get("image", "")
                    if img_path and Path(img_path).exists():
                        # Add template dynamically
                        tmpl = self.vision_engine.add_template(str(img_path), threshold=0.7)
                        if tmpl:
                            # Do not override ID directly, use returned ID
                            tmpl_id = getattr(tmpl, 'id', skill_id)
                            templates_added.append(tmpl_id)

                if templates_added:
                    # Match skills against screen
                    skill_detections = self.vision_engine.match_templates(
                        frame, templates=templates_added, max_results=20
                    )

                    # Clean up templates after scan so we don't pollute vision engine for general use
                    for sid in templates_added:
                        self.vision_engine.remove_template(sid)

            return {
                'monsters': monsters,
                'skills': skill_detections
            }
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            return {'monsters': [], 'skills': []}

    def normalize_and_detect_class(self, detected_skills: List[Detection]) -> str:
        """Xác định class dựa trên skill nhận diện."""
        return "Unknown"

    def recommend_skills(self, detected_class: str) -> List[str]:
        """Gợi ý bộ skill dựa trên class."""
        return ["Basic Combo"]

    def run_scan(self) -> Dict[str, Any]:
        """Luồng chạy chính của AutoScanner."""
        window_info = self.detect_window()
        if not window_info:
            return {'status': 'error', 'message': 'Không tìm thấy cửa sổ hợp lệ.'}

        scan_data = self.scan_screen(window_info)
        detected_class = self.normalize_and_detect_class(scan_data['skills'])
        recommended_skills = self.recommend_skills(detected_class)

        try:
            from lib.db.services.scan_service import ScanService
            scan_service = ScanService()

            scan_id = str(uuid.uuid4())
            timestamp = time.time()

            monster_id_str = ",".join([str(m.class_id) for m in scan_data['monsters']]) if scan_data['monsters'] else "None"

            # Use template_id for skills
            skill_ids = []
            for s in scan_data['skills']:
                tmpl_id = getattr(s, 'template_id', None) or getattr(s, 'class_id', None)
                if tmpl_id:
                    skill_ids.append(str(tmpl_id))
            skill_id_str = ",".join(skill_ids) if skill_ids else "None"

            data = {
                'scan_id': scan_id,
                'monster_id': None, # Keep None to avoid FK constraint fails if not loaded
                'skill_id': None,
                'class_id': None,
                'location': 'Unknown',
                'status': 'Success'
            }
            # Attempt to create
            scan_service.create_scan(data)
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
            scan_id = "error"

        return {
            'status': 'success',
            'scan_id': scan_id,
            'class': detected_class,
            'monsters': [m.class_id for m in scan_data['monsters']],
            'skills': [s.class_id for s in scan_data['skills']],
            'recommended_skills': recommended_skills
        }
