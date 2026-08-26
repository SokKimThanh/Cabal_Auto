"""
Vision Engine - Core OpenCV detection, tracking, and worker thread facade.
Sprint 22 Phase 2 / Refactored modular architecture (< 300 lines).

Delegates:
- Template loading & caching -> TemplateService (lib/vision/template_loader.py)
- Template matching & NMS -> MatcherService (lib/vision/matcher_service.py)
"""

import cv2
import numpy as np
import json
import time
import logging
import threading
import queue
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict

from lib.vision.template_loader import Template, TemplateService
from lib.vision.matcher_service import MatcherService

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import screen capture module (Windows only)
if sys.platform == "win32":
    from lib.system.screen_capture import ScreenCapture
    from lib.system.window_manager import WindowManager
else:
    ScreenCapture = None  # type: ignore
    WindowManager = None  # type: ignore


# =====================================================================
# Data Classes (Re-exported for backward compatibility)
# =====================================================================


@dataclass
class Detection:
    """Single detection result"""

    x: int
    y: int
    w: int
    h: int
    score: float
    template_id: str
    scale: float = 1.0
    method_used: str = "template"
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def bbox(self) -> Tuple[int, int, int, int]:
        """Return (x, y, w, h)"""
        return (self.x, self.y, self.w, self.h)

    def center(self) -> Tuple[int, int]:
        """Return center point (cx, cy)"""
        return (self.x + self.w // 2, self.y + self.h // 2)


@dataclass
class TrackedObject:
    """Tracked object with hybrid tracking"""

    tracker_id: str
    bbox: Tuple[int, int, int, int]
    template_id: str
    confidence: float
    last_verify_score: float
    frames_tracked: int = 0
    last_verify_frame: int = 0
    detect_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =====================================================================
# Vision Engine Core
# =====================================================================


class VisionEngine:
    """
    Core vision engine facade coordinating template management, matching, tracking, and async worker threads.
    """

    def __init__(self, config_dir: str = "lib/data"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # ⚡ Bolt Optimization: Cache feature detectors
        self._detectors = {}

        # Services
        self.template_service = TemplateService(self.config_dir)
        self.matcher_service = MatcherService()

        # Region config
        self.region_config_path = self.config_dir / "vision_region.json"
        self.default_region: Optional[Tuple[int, int, int, int]] = None

        # Trackers
        self.trackers: Dict[str, Dict[str, Any]] = {}
        self.next_tracker_id = 1

        # Parameters
        self.params = {
            "nms_iou_threshold": 0.3,
            "verify_interval": 30,
            "verify_threshold": 0.5,
            "max_scales": 3,
            "tracker_type": "CSRT",
            "match_method": cv2.TM_CCOEFF_NORMED,
            "fps_limit": 15,
            "downscale_factor": 1.0,
            "use_grayscale": True,
            "feature_type": "ORB",
            "hsv_lower": (0, 120, 120),
            "hsv_upper": (10, 255, 255),
            "hsv_min_area": 50,
            "hsv_max_area": 100000,
            "target_threat_levels": ["gray", "yellow"],
            "hsv_ranges": {
                "yellow": [((20, 100, 100), (35, 255, 255))],
                "gray": [((0, 0, 150), (180, 30, 230))],
                "red": [
                    ((0, 120, 120), (10, 255, 255)),
                    ((170, 120, 120), (180, 255, 255)),
                ],
            },
        }

        # State
        self.frame_count = 0
        self.debug_mode = False

        # Screen capture integration
        self.screen_capture: Optional["ScreenCapture"] = None  # type: ignore
        self.capture_hwnd: Optional[int] = None
        self.capture_enabled = False
        self.window_manager: Optional["WindowManager"] = None  # type: ignore

        if sys.platform == "win32" and WindowManager:
            try:
                self.window_manager = WindowManager()  # type: ignore
            except Exception as e:
                logger.warning(f"Failed to initialize WindowManager: {e}")

        # Worker threads and queue
        self.worker_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.result_queue: queue.Queue = queue.Queue(maxsize=5)
        self.frame_callback: Optional[Callable] = None

        self._load_region_config()
        logger.info(f"VisionEngine initialized with {len(self.templates)} templates")

    @property
    def templates(self) -> Dict[str, Template]:
        return self.template_service.templates

    @property
    def templates_config_path(self) -> Path:
        return self.template_service.templates_config_path

    # =====================================================================
    # Template Management Delegation
    # =====================================================================

    def load_templates(self, path_list: List[str]) -> Dict[str, Template]:
        return self.template_service.load_templates(path_list)

    def add_template(
        self, path: str, threshold: float = 0.7, scales: Optional[List[float]] = None
    ) -> Optional[Template]:
        return self.template_service.add_template(
            path, threshold, scales, self.params["max_scales"]
        )

    def remove_template(self, template_id: str) -> bool:
        return self.template_service.remove_template(template_id)

    def get_template(self, template_id: str) -> Optional[Template]:
        return self.template_service.get_template(template_id)

    def list_templates(self) -> List[Template]:
        return self.template_service.list_templates()

    # =====================================================================
    # Detection Delegation
    # =====================================================================

    def match_templates(
        self,
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None,
        templates: Optional[List[str]] = None,
        scales: Optional[List[float]] = None,
        max_results: int = 10,
        use_grayscale: Optional[bool] = None,
    ) -> List[Detection]:
        self.matcher_service.match_method = self.params.get(
            "match_method", cv2.TM_CCOEFF_NORMED
        )
        self.matcher_service.nms_iou_threshold = self.params.get(
            "nms_iou_threshold", 0.3
        )
        use_gray = (
            use_grayscale
            if use_grayscale is not None
            else self.params.get("use_grayscale", True)
        )
        return self.matcher_service.match_templates(
            frame=frame,
            templates=self.templates,
            roi=roi,
            template_ids=templates,
            scales=scales,
            max_scales=self.params["max_scales"],
            max_results=max_results,
            use_grayscale=use_gray,
            debug_mode=self.debug_mode,
        )

    def _match_template_at_scale(
        self,
        frame: np.ndarray,
        template: Template,
        scale: float,
        offset_x: int,
        offset_y: int,
    ) -> List[Detection]:
        use_gray = self.params.get("use_grayscale", True)
        return self.matcher_service.match_template_at_scale(
            frame, template, scale, offset_x, offset_y, use_grayscale=use_gray
        )

    def nms(
        self, detections: List[Detection], iou_threshold: float = 0.3
    ) -> List[Detection]:
        return self.matcher_service.nms(detections, iou_threshold)

    # =====================================================================
    # Tracking Logic
    # =====================================================================

    def start_track(self, frame: np.ndarray, detection: Detection) -> str:
        tracker_id = f"track_{self.next_tracker_id}"
        self.next_tracker_id += 1

        tracker_type = self.params.get("tracker_type", "CSRT").upper()

        try:
            if tracker_type == "CSRT":
                tracker = cv2.legacy.TrackerCSRT_create()  # type: ignore
            elif tracker_type == "KCF":
                tracker = cv2.legacy.TrackerKCF_create()  # type: ignore
            else:
                logger.warning(
                    f"Unknown tracker type: {tracker_type}, falling back to CSRT"
                )
                tracker = cv2.legacy.TrackerCSRT_create()  # type: ignore
        except AttributeError:
            if tracker_type == "CSRT":
                tracker = cv2.TrackerCSRT_create()  # type: ignore
            elif tracker_type == "KCF":
                tracker = cv2.TrackerKCF_create()  # type: ignore
            else:
                logger.warning(
                    f"Unknown tracker type: {tracker_type}, falling back to CSRT"
                )
                tracker = cv2.TrackerCSRT_create()  # type: ignore

        bbox = detection.bbox()
        if not tracker.init(frame, bbox):
            return ""

        tracked_obj = TrackedObject(
            tracker_id=tracker_id,
            bbox=bbox,
            template_id=detection.template_id,
            confidence=detection.score,
            last_verify_score=detection.score,
            frames_tracked=0,
            last_verify_frame=self.frame_count,
            detect_time=detection.timestamp,
        )

        self.trackers[tracker_id] = {
            "tracker": tracker,
            "tracked_obj": tracked_obj,
            "template": self.get_template(detection.template_id),
        }
        return tracker_id

    def update_tracks(self, frame: np.ndarray) -> List[TrackedObject]:
        self.frame_count += 1
        updated_tracks, to_remove = [], []

        for tracker_id, track_data in self.trackers.items():
            tracker = track_data["tracker"]
            tracked_obj = track_data["tracked_obj"]
            template = track_data["template"]

            success, bbox = tracker.update(frame)
            if not success:
                to_remove.append(tracker_id)
                continue

            tracked_obj.bbox = tuple(map(int, bbox))
            tracked_obj.frames_tracked += 1

            if (self.frame_count - tracked_obj.last_verify_frame) >= self.params[
                "verify_interval"
            ]:
                verify_score = self.reverify_track(frame, tracked_obj, template)
                tracked_obj.last_verify_score = verify_score
                tracked_obj.last_verify_frame = self.frame_count

                if verify_score < self.params["verify_threshold"]:
                    to_remove.append(tracker_id)
                    continue

            updated_tracks.append(tracked_obj)

        for tid in to_remove:
            self.stop_track(tid)

        return updated_tracks

    def reverify_track(
        self,
        frame: np.ndarray,
        tracked_obj: TrackedObject,
        template: Optional[Template],
    ) -> float:
        if template is None or template.image is None:
            return 0.0

        try:
            x, y, w, h = tracked_obj.bbox
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(frame.shape[1], x + w + margin)
            y2 = min(frame.shape[0], y + h + margin)

            roi = frame[y1:y2, x1:x2]
            if roi.size == 0 or roi.shape[0] == 0 or roi.shape[1] == 0:
                return 0.0

            detections = self._match_template_at_scale(
                roi, template, scale=1.0, offset_x=x1, offset_y=y1
            )
            return max((d.score for d in detections), default=0.0)
        except Exception as e:
            logger.error(f"Error re-verifying track: {e}")
            return 0.0

    def stop_track(self, tracker_id: str) -> bool:
        if tracker_id in self.trackers:
            del self.trackers[tracker_id]
            return True
        return False

    def stop_all_tracks(self):
        self.trackers.clear()

    def get_tracked_objects(self) -> List[TrackedObject]:
        return [track_data["tracked_obj"] for track_data in self.trackers.values()]

    # =====================================================================
    # Advanced HSV Detection & Feature Matching
    # =====================================================================

    def detect_hsv_target(
        self,
        frame: np.ndarray,
        lower_hsv: Optional[Tuple[int, int, int]] = None,
        upper_hsv: Optional[Tuple[int, int, int]] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        roi: Optional[Tuple[int, int, int, int]] = None,
        downscale_factor: float = 1.0,
        target_threat_levels: Optional[List[str]] = None,
    ) -> List[Detection]:
        if (
            frame is None
            or frame.size == 0
            or frame.shape[0] == 0
            or frame.shape[1] == 0
        ):
            return []

        min_a = (
            min_area if min_area is not None else self.params.get("hsv_min_area", 50)
        )
        max_a = (
            max_area
            if max_area is not None
            else self.params.get("hsv_max_area", 100000)
        )
        frame_h, frame_w = frame.shape[:2]

        offset_x, offset_y = 0, 0
        if roi is not None:
            rx, ry, rw, rh = roi
            rx = max(0, min(rx, frame_w - 1))
            ry = max(0, min(ry, frame_h - 1))
            rw = max(1, min(rw, frame_w - rx))
            rh = max(1, min(rh, frame_h - ry))
            work_frame = frame[ry : ry + rh, rx : rx + rw]
            offset_x, offset_y = rx, ry
        else:
            work_frame = frame

        if work_frame.size == 0 or work_frame.shape[0] == 0 or work_frame.shape[1] == 0:
            return []

        if 0.0 < downscale_factor < 1.0:
            scaled_w = max(1, int(work_frame.shape[1] * downscale_factor))
            scaled_h = max(1, int(work_frame.shape[0] * downscale_factor))
            proc_frame = cv2.resize(work_frame, (scaled_w, scaled_h))
            scale_x = work_frame.shape[1] / float(scaled_w)
            scale_y = work_frame.shape[0] / float(scaled_h)
        else:
            proc_frame = work_frame
            scale_x, scale_y = 1.0, 1.0

        hsv = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2HSV)
        active_levels = (
            target_threat_levels
            if target_threat_levels is not None
            else self.params.get("target_threat_levels", ["gray", "yellow"])
        )
        active_levels_lower = [str(lvl).lower() for lvl in active_levels]

        hsv_ranges = self.params.get(
            "hsv_ranges",
            {
                "yellow": [((20, 100, 100), (35, 255, 255))],
                "gray": [((0, 0, 150), (180, 30, 230))],
                "red": [
                    ((0, 120, 120), (10, 255, 255)),
                    ((170, 120, 120), (180, 255, 255)),
                ],
            },
        )

        if lower_hsv is not None and upper_hsv is not None:
            lower_b, upper_b = np.array(lower_hsv, dtype=np.uint8), np.array(
                upper_hsv, dtype=np.uint8
            )
            if lower_b[0] > upper_b[0]:
                m1 = cv2.inRange(
                    hsv, np.array([0, lower_b[1], lower_b[2]], dtype=np.uint8), upper_b
                )
                m2 = cv2.inRange(
                    hsv,
                    lower_b,
                    np.array([180, upper_b[1], upper_b[2]], dtype=np.uint8),
                )
                mask = cv2.bitwise_or(m1, m2)
            else:
                mask = cv2.inRange(hsv, lower_b, upper_b)
            apply_red_filter = (
                target_threat_levels is not None and "red" not in active_levels_lower
            )
        else:
            combined_mask = None
            for level in active_levels_lower:
                for r_lower, r_upper in hsv_ranges.get(level, []):
                    sub_m = cv2.inRange(
                        hsv,
                        np.array(r_lower, dtype=np.uint8),
                        np.array(r_upper, dtype=np.uint8),
                    )
                    combined_mask = (
                        sub_m
                        if combined_mask is None
                        else cv2.bitwise_or(combined_mask, sub_m)
                    )

            if combined_mask is None:
                return []
            mask = combined_mask
            apply_red_filter = "red" not in active_levels_lower

        red_mask = None
        if apply_red_filter:
            for r_lower, r_upper in hsv_ranges.get("red", []):
                sub_r = cv2.inRange(
                    hsv,
                    np.array(r_lower, dtype=np.uint8),
                    np.array(r_upper, dtype=np.uint8),
                )
                red_mask = (
                    sub_r if red_mask is None else cv2.bitwise_or(red_mask, sub_r)
                )

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []

        detections = []
        now = time.time()

        for cnt in contours:
            area_proc = cv2.contourArea(cnt)
            area_orig = area_proc * scale_x * scale_y
            if min_a <= area_orig <= max_a:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                if apply_red_filter and red_mask is not None:
                    red_roi = red_mask[by : by + bh, bx : bx + bw]
                    if red_roi.size > 0 and cv2.countNonZero(red_roi) > 0.25 * (
                        bw * bh
                    ):
                        continue

                orig_x = max(0, min(int(offset_x + bx * scale_x), frame_w - 1))
                orig_y = max(0, min(int(offset_y + by * scale_y), frame_h - 1))
                orig_w = max(1, min(int(bw * scale_x), frame_w - orig_x))
                orig_h = max(1, min(int(bh * scale_y), frame_h - orig_y))

                score = min(1.0, float(area_orig / max_a)) if max_a > 0 else 1.0
                detections.append(
                    Detection(
                        x=orig_x,
                        y=orig_y,
                        w=orig_w,
                        h=orig_h,
                        score=score if score > 0 else 0.85,
                        template_id="hsv_target",
                        scale=1.0,
                        method_used="hsv_mask",
                        timestamp=now,
                    )
                )

        detections.sort(key=lambda d: d.w * d.h, reverse=True)
        return detections

    def detect_features(
        self,
        frame: np.ndarray,
        template: Template,
        feature_type: Optional[str] = None,
        min_matches: int = 4,
        roi: Optional[Tuple[int, int, int, int]] = None,
        downscale_factor: float = 1.0,
    ) -> List[Detection]:
        if (
            frame is None
            or frame.size == 0
            or frame.shape[0] == 0
            or frame.shape[1] == 0
        ):
            return []
        if template is None or template.image is None or template.image.size == 0:
            return []

        ftype = (feature_type or self.params.get("feature_type", "ORB")).upper()
        frame_h, frame_w = frame.shape[:2]

        offset_x, offset_y = 0, 0
        if roi is not None:
            rx, ry, rw, rh = roi
            rx = max(0, min(rx, frame_w - 1))
            ry = max(0, min(ry, frame_h - 1))
            rw = max(1, min(rw, frame_w - rx))
            rh = max(1, min(rh, frame_h - ry))
            work_frame = frame[ry : ry + rh, rx : rx + rw]
            offset_x, offset_y = rx, ry
        else:
            work_frame = frame

        if work_frame.size == 0 or work_frame.shape[0] == 0 or work_frame.shape[1] == 0:
            return []

        if 0.0 < downscale_factor < 1.0:
            scaled_w = max(1, int(work_frame.shape[1] * downscale_factor))
            scaled_h = max(1, int(work_frame.shape[0] * downscale_factor))
            proc_frame = cv2.resize(work_frame, (scaled_w, scaled_h))
            scale_x = work_frame.shape[1] / float(scaled_w)
            scale_y = work_frame.shape[0] / float(scaled_h)
        else:
            proc_frame = work_frame
            scale_x, scale_y = 1.0, 1.0

        # Create a detector per call to avoid sharing mutable OpenCV state
        # across concurrent detect_features invocations.
        if ftype == "SIFT" and hasattr(cv2, "SIFT_create"):
            detector = cv2.SIFT_create(nfeatures=500)
            norm = cv2.NORM_L2
        else:
            detector = cv2.ORB_create(nfeatures=500)
            norm = cv2.NORM_HAMMING

        gray_frame = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2GRAY)

        # ⚡ Bolt Optimization: Use cached template features if available,
        # but invalidate them when the underlying template image changes.
        template_source = (
            template.image_gray if template.image_gray is not None else template.image
        )
        template_cache_key = (
            id(template_source),
            getattr(template_source, "shape", None),
            getattr(getattr(template_source, "dtype", None), "str", None),
        )
        cached_template_features = template.features.get(ftype)

        if (
            isinstance(cached_template_features, dict)
            and cached_template_features.get("cache_key") == template_cache_key
        ):
            kp1, des1 = cached_template_features["features"]
        else:
            if template.image_gray is not None:
                gray_template = template.image_gray
            elif template.image is not None:
                gray_template = cv2.cvtColor(template.image, cv2.COLOR_BGR2GRAY)
            else:
                return []
            kp1, des1 = detector.detectAndCompute(gray_template, None)
            template.features[ftype] = {
                "cache_key": template_cache_key,
                "features": (kp1, des1),
            }

        kp2, des2 = detector.detectAndCompute(gray_frame, None)

        if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
            return []

        matcher = cv2.BFMatcher(norm, crossCheck=False)
        try:
            matches = matcher.knnMatch(des1, des2, k=2)
        except Exception as e:
            logger.error(f"Error in feature matching: {e}")
            return []

        good_matches = [
            m[0]
            for m in matches
            if len(m) == 2 and m[0].distance < 0.75 * m[1].distance
        ]
        if len(good_matches) < max(4, min_matches):
            return []

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(
            -1, 1, 2
        )
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(
            -1, 1, 2
        )

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return []

        th, tw = gray_template.shape
        pts = np.float32([[0, 0], [0, th - 1], [tw - 1, th - 1], [tw - 1, 0]]).reshape(
            -1, 1, 2
        )
        try:
            dst = cv2.perspectiveTransform(pts, M)
        except Exception:
            return []

        x_coords, y_coords = dst[:, 0, 0], dst[:, 0, 1]
        min_x, max_x = np.min(x_coords), np.max(x_coords)
        min_y, max_y = np.min(y_coords), np.max(y_coords)

        orig_x = max(0, min(int(offset_x + min_x * scale_x), frame_w - 1))
        orig_y = max(0, min(int(offset_y + min_y * scale_y), frame_h - 1))
        orig_w = max(1, min(int((max_x - min_x) * scale_x), frame_w - orig_x))
        orig_h = max(1, min(int((max_y - min_y) * scale_y), frame_h - orig_y))

        score = min(1.0, float(len(good_matches)) / 50.0)
        return [
            Detection(
                x=orig_x,
                y=orig_y,
                w=orig_w,
                h=orig_h,
                score=score,
                template_id=template.id,
                scale=1.0,
                method_used=f"{ftype.lower()}_features",
                timestamp=time.time(),
            )
        ]

    def detect_monster_pipeline(
        self,
        frame: np.ndarray,
        template_ids: Optional[List[str]] = None,
        roi: Optional[Tuple[int, int, int, int]] = None,
        downscale_factor: Optional[float] = None,
        confidence_threshold: float = 0.6,
        use_fast_hsv: bool = True,
    ) -> List[Detection]:
        if frame is None or frame.size == 0:
            return []

        scale_factor = (
            downscale_factor
            if downscale_factor is not None
            else self.params.get("downscale_factor", 1.0)
        )
        search_roi = roi if roi is not None else self.default_region

        if use_fast_hsv:
            hsv_detections = self.detect_hsv_target(
                frame, roi=search_roi, downscale_factor=scale_factor
            )
            if hsv_detections:
                return hsv_detections

        templates_to_search = (
            [
                self.templates[tid]
                for tid in template_ids
                if tid in self.templates and self.templates[tid].enabled
            ]
            if template_ids
            else [t for t in self.templates.values() if t.enabled]
        )
        secondary_detections = []

        for tpl in templates_to_search:
            feat_dets = self.detect_features(
                frame, template=tpl, roi=search_roi, downscale_factor=scale_factor
            )
            for d in feat_dets:
                if d.score >= confidence_threshold:
                    secondary_detections.append(d)

        if secondary_detections:
            secondary_detections.sort(key=lambda d: d.score, reverse=True)
            return secondary_detections

        tmpl_dets = self.match_templates(
            frame, roi=search_roi, templates=template_ids, scales=[0.8, 1.0, 1.2]
        )
        return [d for d in tmpl_dets if d.score >= confidence_threshold]

    # =====================================================================
    # Async Worker Thread & Screen Capture API
    # =====================================================================

    def start_worker(
        self, frame_callback: Optional[Callable[[], Optional[np.ndarray]]] = None
    ) -> None:
        if self.worker_running:
            return
        if frame_callback is None and self.is_capture_active():
            self.frame_callback = self.get_capture_frame
        elif frame_callback is not None:
            self.frame_callback = frame_callback
        else:
            return

        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_worker(self) -> None:
        if not self.worker_running:
            return
        self.worker_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except queue.Empty:
                break

        self.stop_all_tracks()
        if self.is_capture_active():
            self.stop_capture()

    def get_result(self, timeout: float = 0.0) -> Optional[Dict[str, Any]]:
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _worker_loop(self) -> None:
        fps_limit = self.params.get("fps_limit", 15)
        frame_time = 1.0 / fps_limit

        while self.worker_running:
            loop_start = time.time()
            try:
                if not self.frame_callback:
                    time.sleep(0.1)
                    continue

                frame = self.frame_callback()
                if frame is None:
                    time.sleep(0.1)
                    continue

                result = self._process_frame(frame)
                try:
                    self.result_queue.put_nowait(result)
                except queue.Full:
                    try:
                        self.result_queue.get_nowait()
                        self.result_queue.put_nowait(result)
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)

            elapsed = time.time() - loop_start
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        rendered_frame = frame.copy()

        if len(self.trackers) == 0:
            detections = self.match_templates(frame, roi=self.default_region)
            for det in detections:
                cv2.rectangle(
                    rendered_frame,
                    (det.x, det.y),
                    (det.x + det.w, det.y + det.h),
                    (0, 255, 0),
                    2,
                )
                label = f"{det.template_id} {det.score:.2f}"
                cv2.putText(
                    rendered_frame,
                    label,
                    (det.x, det.y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
            return {
                "type": "detections",
                "data": [d.to_dict() for d in detections],
                "frame": rendered_frame,
                "timestamp": time.time(),
            }
        else:
            tracks = self.update_tracks(frame)
            for track in tracks:
                x, y, w, h = track.bbox
                cv2.rectangle(rendered_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                label = f"{track.template_id} {track.confidence:.2f}"
                cv2.putText(
                    rendered_frame,
                    label,
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                )
            return {
                "type": "tracks",
                "data": [t.to_dict() for t in tracks],
                "frame": rendered_frame,
                "timestamp": time.time(),
            }

    def reset(self):
        """Reset engine state"""
        self.stop_all_tracks()
        self.frame_count = 0
        logger.info("Engine reset")

    def focus_capture_window(self) -> bool:
        """Bring captured window to foreground"""
        if not self.capture_hwnd or sys.platform != "win32" or not self.window_manager:
            return False
        try:
            return self.window_manager.set_foreground(self.capture_hwnd)
        except Exception as e:
            logger.error(f"Error focusing window: {e}")
            return False

    def start_capture(
        self, window_title: str, target_fps: int = 15, queue_size: int = 5
    ) -> bool:
        if sys.platform != "win32" or not ScreenCapture or not self.window_manager:
            return False
        hwnd = self.window_manager.find_window(title_contains=window_title)
        if not hwnd:
            return False
        self.stop_capture()
        try:
            if hasattr(ScreenCapture, "start_capture"):
                cap = ScreenCapture(hwnd, queue_size=queue_size, target_fps=target_fps)
                cap.start_capture()
            else:
                cap = ScreenCapture(queue_size=queue_size, target_fps=target_fps)
                if not cap.start(window_title):
                    return False

            self.screen_capture = cap
            self.capture_hwnd = hwnd
            self.capture_enabled = True
            self.params["fps_limit"] = target_fps
            return True
        except Exception as e:
            logger.error(f"Failed to start screen capture: {e}")
            self.screen_capture = None
            self.capture_hwnd = None
            self.capture_enabled = False
            return False

    def stop_capture(self) -> None:
        if self.screen_capture:
            try:
                if hasattr(self.screen_capture, "stop_capture"):
                    self.screen_capture.stop_capture()
                elif hasattr(self.screen_capture, "stop"):
                    self.screen_capture.stop()
            except Exception as e:
                logger.error(f"Error stopping capture: {e}")
            finally:
                self.screen_capture = None
                self.capture_hwnd = None
                self.capture_enabled = False

    def get_capture_frame(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        if not self.capture_enabled or not self.screen_capture:
            return None
        try:
            return self.screen_capture.get_frame(timeout=timeout)
        except Exception:
            return None

    def is_capture_active(self) -> bool:
        return bool(
            self.capture_enabled
            and self.screen_capture
            and self.screen_capture.is_capturing
        )

    def set_params(self, params_dict: Dict[str, Any]):
        self.params.update(params_dict)

    def get_params(self) -> Dict[str, Any]:
        return self.params.copy()

    def set_debug(self, enabled: bool):
        self.debug_mode = enabled
        if enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def get_capture_stats(self) -> Optional[Dict[str, Any]]:
        if not self.capture_enabled or not self.screen_capture:
            return None
        try:
            stats = (
                self.screen_capture.get_stats()
                if hasattr(self.screen_capture, "get_stats")
                else None
            )
            if stats:
                return {
                    "fps": stats.fps,
                    "frames_captured": stats.frames_captured,
                    "frames_dropped": stats.frames_dropped,
                    "queue_size": stats.queue_size,
                    "last_update": stats.last_update,
                }
            return None
        except Exception as e:
            logger.error(f"Error getting capture stats: {e}")
            return None

    def get_threshold_presets(self) -> Dict[str, float]:
        return {"low": 0.5, "normal": 0.7, "strict": 0.85}

    def _save_templates_config(self):
        self.template_service.save_templates_config()

    def _load_templates_config(self):
        self.template_service.load_templates_config()

    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
        self.default_region = region
        self._save_region_config()

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        return self.default_region

    def _load_region_config(self):
        if not self.region_config_path.exists():
            return
        try:
            with open(self.region_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            region = data.get("default_region")
            if region:
                self.default_region = tuple(region)
        except Exception as e:
            logger.error(f"Error loading region config: {e}")

    def _save_region_config(self):
        try:
            data = {
                "default_region": (
                    list(self.default_region) if self.default_region else None
                )
            }
            with open(self.region_config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving region config: {e}")


_engine_instance: Optional[VisionEngine] = None


def get_vision_engine(config_dir: str = "lib/data") -> VisionEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = VisionEngine(config_dir)
    return _engine_instance
