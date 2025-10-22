"""
Vision Engine - Core OpenCV detection and tracking system
Sprint 22 Phase 2

Provides:
- Multi-template, multi-scale detection
- NMS (Non-Maximum Suppression)
- Hybrid tracking (tracker + periodic re-verification)
- Template management
- Config persistence

Architecture:
- UI calls engine API (no cv2 in UI code)
- Engine handles all CV operations
- Returns data structures for UI overlay
"""

import cv2
import numpy as np
import json
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class Detection:
    """Single template detection result"""
    x: int
    y: int
    w: int
    h: int
    score: float
    template_id: str
    scale: float
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
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    template_id: str
    confidence: float
    last_verify_score: float
    frames_tracked: int = 0
    last_verify_frame: int = 0
    detect_time: float = 0.0  # For FIFO prioritization
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Template:
    """Template metadata"""
    id: str
    path: str
    threshold: float = 0.7
    scales: List[float] = None
    enabled: bool = True
    image: Optional[np.ndarray] = None  # Loaded image (not serialized)
    thumbnail: Optional[np.ndarray] = None  # For UI preview
    
    def __post_init__(self):
        if self.scales is None:
            self.scales = [1.0]  # Default: no scaling
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize without image data"""
        return {
            'id': self.id,
            'path': self.path,
            'threshold': self.threshold,
            'scales': self.scales,
            'enabled': self.enabled
        }


# =====================================================================
# Vision Engine Core
# =====================================================================

class VisionEngine:
    """
    Core vision engine for detection and tracking.
    
    Features:
    - Multi-template detection with multi-scale support
    - NMS for duplicate removal
    - Hybrid tracking (CV tracker + periodic template re-verification)
    - Template management and persistence
    - Debug mode with logging
    """
    
    def __init__(self, config_dir: str = "lib/data"):
        """
        Initialize vision engine.
        
        Args:
            config_dir: Directory for config files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Templates
        self.templates: Dict[str, Template] = {}
        self.templates_config_path = self.config_dir / "vision_templates.json"
        
        # Region config
        self.region_config_path = self.config_dir / "vision_region.json"
        self.default_region: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
        
        # Trackers
        self.trackers: Dict[str, Dict[str, Any]] = {}  # tracker_id -> {tracker, tracked_obj, ...}
        self.next_tracker_id = 1
        
        # Parameters
        self.params = {
            'nms_iou_threshold': 0.3,
            'verify_interval': 30,  # Re-verify every N frames
            'verify_threshold': 0.5,  # Min score to keep tracking
            'max_scales': 3,  # Limit scale variations
            'tracker_type': 'CSRT',  # CSRT or KCF
            'match_method': cv2.TM_CCOEFF_NORMED,  # Matching method
        }
        
        # State
        self.frame_count = 0
        self.debug_mode = False
        
        # Load configs
        self._load_templates_config()
        self._load_region_config()
        
        logger.info(f"VisionEngine initialized with {len(self.templates)} templates")
    
    # =====================================================================
    # Template Management
    # =====================================================================
    
    def load_templates(self, path_list: List[str]) -> Dict[str, Template]:
        """
        Load templates from file paths.
        
        Args:
            path_list: List of image file paths
            
        Returns:
            Dictionary of loaded templates {id: Template}
        """
        loaded = {}
        
        for path in path_list:
            if not os.path.exists(path):
                logger.warning(f"Template not found: {path}")
                continue
            
            try:
                # Generate template ID from filename
                template_id = Path(path).stem
                
                # Load image
                image = cv2.imread(path)
                if image is None:
                    logger.error(f"Failed to load image: {path}")
                    continue
                
                # Create thumbnail (for UI preview)
                thumbnail = cv2.resize(image, (100, 100), interpolation=cv2.INTER_AREA)
                
                # Check if template already exists in config
                if template_id in self.templates:
                    template = self.templates[template_id]
                    template.image = image
                    template.thumbnail = thumbnail
                else:
                    # Create new template with defaults
                    template = Template(
                        id=template_id,
                        path=path,
                        threshold=0.7,
                        scales=[1.0],
                        enabled=True,
                        image=image,
                        thumbnail=thumbnail
                    )
                
                loaded[template_id] = template
                self.templates[template_id] = template
                
                logger.info(f"Loaded template: {template_id} ({image.shape})")
                
            except Exception as e:
                logger.error(f"Error loading template {path}: {e}")
        
        return loaded
    
    def add_template(self, path: str, threshold: float = 0.7, 
                     scales: List[float] = None) -> Optional[Template]:
        """
        Add a single template.
        
        Args:
            path: Path to template image
            threshold: Detection threshold (0.0-1.0)
            scales: Scale variations [0.8, 1.0, 1.2]
            
        Returns:
            Template object if successful, None otherwise
        """
        if scales is None:
            scales = [1.0]
        
        result = self.load_templates([path])
        if result:
            template_id = list(result.keys())[0]
            template = result[template_id]
            template.threshold = threshold
            template.scales = scales[:self.params['max_scales']]  # Limit scales
            
            self._save_templates_config()
            return template
        
        return None
    
    def remove_template(self, template_id: str) -> bool:
        """Remove a template"""
        if template_id in self.templates:
            del self.templates[template_id]
            self._save_templates_config()
            logger.info(f"Removed template: {template_id}")
            return True
        return False
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Template]:
        """Get all templates"""
        return list(self.templates.values())
    
    # =====================================================================
    # Detection
    # =====================================================================
    
    def match_templates(
        self,
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None,
        templates: Optional[List[str]] = None,
        scales: Optional[List[float]] = None,
        max_results: int = 10
    ) -> List[Detection]:
        """
        Detect templates in frame with multi-scale matching.
        
        Args:
            frame: Input frame (BGR)
            roi: Region of interest (x, y, w, h) or None for full frame
            templates: List of template IDs to match, or None for all enabled
            scales: Override scales, or None to use template scales
            max_results: Maximum detections to return
            
        Returns:
            List of Detection objects
        """
        if frame is None or frame.size == 0:
            logger.warning("Empty frame provided")
            return []
        
        # Get region to search
        if roi is not None:
            x, y, w, h = roi
            search_region = frame[y:y+h, x:x+w]
            offset_x, offset_y = x, y
        else:
            search_region = frame
            offset_x, offset_y = 0, 0
        
        # Select templates to match
        if templates is None:
            templates_to_match = [t for t in self.templates.values() if t.enabled]
        else:
            templates_to_match = [self.templates[tid] for tid in templates 
                                 if tid in self.templates and self.templates[tid].enabled]
        
        if not templates_to_match:
            logger.debug("No templates to match")
            return []
        
        # Detect all templates at all scales
        all_detections = []
        
        for template in templates_to_match:
            if template.image is None:
                logger.warning(f"Template {template.id} has no image loaded")
                continue
            
            # Get scales to try
            template_scales = scales if scales else template.scales
            
            for scale in template_scales[:self.params['max_scales']]:
                detections = self._match_template_at_scale(
                    search_region,
                    template,
                    scale,
                    offset_x,
                    offset_y
                )
                all_detections.extend(detections)
        
        # Apply NMS to remove duplicates
        filtered = self.nms(all_detections, self.params['nms_iou_threshold'])
        
        # Sort by score and limit results
        filtered.sort(key=lambda d: d.score, reverse=True)
        result = filtered[:max_results]
        
        if self.debug_mode:
            logger.debug(f"Detected {len(result)} objects (from {len(all_detections)} before NMS)")
        
        return result
    
    def _match_template_at_scale(
        self,
        frame: np.ndarray,
        template: Template,
        scale: float,
        offset_x: int,
        offset_y: int
    ) -> List[Detection]:
        """
        Match single template at specific scale.
        
        Returns:
            List of Detection objects above threshold
        """
        detections = []
        
        try:
            # Resize template
            template_img = template.image
            if scale != 1.0:
                new_w = int(template_img.shape[1] * scale)
                new_h = int(template_img.shape[0] * scale)
                if new_w <= 0 or new_h <= 0:
                    return []
                template_img = cv2.resize(template_img, (new_w, new_h))
            
            # Check if template fits in frame
            if template_img.shape[0] > frame.shape[0] or template_img.shape[1] > frame.shape[1]:
                return []
            
            # Match template
            result = cv2.matchTemplate(frame, template_img, self.params['match_method'])
            
            # Find all matches above threshold
            threshold = template.threshold
            locations = np.where(result >= threshold)
            
            # Create detections
            for pt in zip(*locations[::-1]):  # (x, y)
                x, y = pt
                w, h = template_img.shape[1], template_img.shape[0]
                score = float(result[y, x])
                
                detection = Detection(
                    x=x + offset_x,
                    y=y + offset_y,
                    w=w,
                    h=h,
                    score=score,
                    template_id=template.id,
                    scale=scale,
                    timestamp=time.time()
                )
                detections.append(detection)
        
        except Exception as e:
            logger.error(f"Error matching template {template.id} at scale {scale}: {e}")
        
        return detections
    
    def nms(self, detections: List[Detection], iou_threshold: float = 0.3) -> List[Detection]:
        """
        Non-Maximum Suppression to remove overlapping detections.
        
        Args:
            detections: List of Detection objects
            iou_threshold: IoU threshold (0.0-1.0)
            
        Returns:
            Filtered list of detections
        """
        if not detections:
            return []
        
        # Sort by score (descending)
        detections = sorted(detections, key=lambda d: d.score, reverse=True)
        
        keep = []
        
        while detections:
            # Keep highest score detection
            best = detections[0]
            keep.append(best)
            detections = detections[1:]
            
            # Remove overlapping detections
            detections = [
                d for d in detections
                if self._iou(best.bbox(), d.bbox()) < iou_threshold
            ]
        
        return keep
    
    def _iou(self, box1: Tuple[int, int, int, int], 
             box2: Tuple[int, int, int, int]) -> float:
        """
        Calculate IoU (Intersection over Union) between two boxes.
        
        Args:
            box1, box2: (x, y, w, h)
            
        Returns:
            IoU value (0.0-1.0)
        """
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    # =====================================================================
    # Tracking
    # =====================================================================
    
    def start_track(self, frame: np.ndarray, detection: Detection) -> str:
        """
        Start tracking a detection.
        
        Args:
            frame: Current frame
            detection: Detection to track
            
        Returns:
            Tracker ID
        """
        tracker_id = f"track_{self.next_tracker_id}"
        self.next_tracker_id += 1
        
        # Create tracker
        if self.params['tracker_type'] == 'CSRT':
            tracker = cv2.TrackerCSRT_create()
        elif self.params['tracker_type'] == 'KCF':
            tracker = cv2.TrackerKCF_create()
        else:
            logger.warning(f"Unknown tracker type: {self.params['tracker_type']}, using CSRT")
            tracker = cv2.TrackerCSRT_create()
        
        # Initialize tracker
        bbox = detection.bbox()
        success = tracker.init(frame, bbox)
        
        if not success:
            logger.error(f"Failed to initialize tracker for detection: {detection}")
            return ""
        
        # Create tracked object
        tracked_obj = TrackedObject(
            tracker_id=tracker_id,
            bbox=bbox,
            template_id=detection.template_id,
            confidence=detection.score,
            last_verify_score=detection.score,
            frames_tracked=0,
            last_verify_frame=self.frame_count,
            detect_time=detection.timestamp
        )
        
        # Store tracker
        self.trackers[tracker_id] = {
            'tracker': tracker,
            'tracked_obj': tracked_obj,
            'template': self.templates.get(detection.template_id)
        }
        
        logger.info(f"Started tracking: {tracker_id} for template {detection.template_id}")
        
        return tracker_id
    
    def update_tracks(self, frame: np.ndarray) -> List[TrackedObject]:
        """
        Update all active trackers.
        
        Args:
            frame: Current frame
            
        Returns:
            List of tracked objects
        """
        self.frame_count += 1
        
        updated_tracks = []
        to_remove = []
        
        for tracker_id, track_data in self.trackers.items():
            tracker = track_data['tracker']
            tracked_obj = track_data['tracked_obj']
            template = track_data['template']
            
            # Update tracker
            success, bbox = tracker.update(frame)
            
            if not success:
                logger.debug(f"Tracker {tracker_id} lost target")
                to_remove.append(tracker_id)
                continue
            
            # Update tracked object
            tracked_obj.bbox = tuple(map(int, bbox))
            tracked_obj.frames_tracked += 1
            
            # Periodic re-verification
            if (self.frame_count - tracked_obj.last_verify_frame) >= self.params['verify_interval']:
                verify_score = self.reverify_track(frame, tracked_obj, template)
                tracked_obj.last_verify_score = verify_score
                tracked_obj.last_verify_frame = self.frame_count
                
                if verify_score < self.params['verify_threshold']:
                    logger.debug(f"Tracker {tracker_id} failed verification (score={verify_score:.2f})")
                    to_remove.append(tracker_id)
                    continue
            
            updated_tracks.append(tracked_obj)
        
        # Remove failed trackers
        for tracker_id in to_remove:
            self.stop_track(tracker_id)
        
        return updated_tracks
    
    def reverify_track(
        self,
        frame: np.ndarray,
        tracked_obj: TrackedObject,
        template: Optional[Template]
    ) -> float:
        """
        Re-verify tracked object using template matching.
        
        Args:
            frame: Current frame
            tracked_obj: Tracked object
            template: Template to verify against
            
        Returns:
            Verification score (0.0-1.0)
        """
        if template is None or template.image is None:
            return 0.0
        
        try:
            # Extract region around tracked bbox (with margin)
            x, y, w, h = tracked_obj.bbox
            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(frame.shape[1], x + w + margin)
            y2 = min(frame.shape[0], y + h + margin)
            
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                return 0.0
            
            # Match template in ROI
            detections = self._match_template_at_scale(
                roi,
                template,
                scale=1.0,
                offset_x=x1,
                offset_y=y1
            )
            
            if detections:
                # Return best match score
                return max(d.score for d in detections)
            
            return 0.0
        
        except Exception as e:
            logger.error(f"Error re-verifying track: {e}")
            return 0.0
    
    def stop_track(self, tracker_id: str) -> bool:
        """
        Stop tracking a specific tracker.
        
        Args:
            tracker_id: Tracker ID to stop
            
        Returns:
            True if stopped successfully
        """
        if tracker_id in self.trackers:
            del self.trackers[tracker_id]
            logger.info(f"Stopped tracking: {tracker_id}")
            return True
        return False
    
    def stop_all_tracks(self):
        """Stop all active trackers"""
        self.trackers.clear()
        logger.info("Stopped all trackers")
    
    def get_tracked_objects(self) -> List[TrackedObject]:
        """Get all currently tracked objects"""
        return [track_data['tracked_obj'] for track_data in self.trackers.values()]
    
    # =====================================================================
    # Configuration
    # =====================================================================
    
    def set_params(self, params_dict: Dict[str, Any]):
        """Update engine parameters"""
        self.params.update(params_dict)
        logger.info(f"Updated params: {params_dict}")
    
    def get_params(self) -> Dict[str, Any]:
        """Get current parameters"""
        return self.params.copy()
    
    def set_debug(self, enabled: bool):
        """Enable/disable debug mode"""
        self.debug_mode = enabled
        if enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.info(f"Debug mode: {'enabled' if enabled else 'disabled'}")
    
    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
        """Set default search region"""
        self.default_region = region
        self._save_region_config()
        logger.info(f"Set default region: {region}")
    
    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Get default search region"""
        return self.default_region
    
    # =====================================================================
    # Persistence
    # =====================================================================
    
    def _load_templates_config(self):
        """Load templates from config file"""
        if not self.templates_config_path.exists():
            logger.info("No templates config found, using defaults")
            return
        
        try:
            with open(self.templates_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for template_data in data.get('templates', []):
                template = Template(**template_data)
                self.templates[template.id] = template
            
            logger.info(f"Loaded {len(self.templates)} templates from config")
        
        except Exception as e:
            logger.error(f"Error loading templates config: {e}")
    
    def _save_templates_config(self):
        """Save templates to config file"""
        try:
            data = {
                'templates': [t.to_dict() for t in self.templates.values()]
            }
            
            with open(self.templates_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.templates)} templates to config")
        
        except Exception as e:
            logger.error(f"Error saving templates config: {e}")
    
    def _load_region_config(self):
        """Load region from config file"""
        if not self.region_config_path.exists():
            return
        
        try:
            with open(self.region_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            region = data.get('default_region')
            if region:
                self.default_region = tuple(region)
            
            logger.info(f"Loaded region config: {self.default_region}")
        
        except Exception as e:
            logger.error(f"Error loading region config: {e}")
    
    def _save_region_config(self):
        """Save region to config file"""
        try:
            data = {
                'default_region': list(self.default_region) if self.default_region else None
            }
            
            with open(self.region_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved region config: {self.default_region}")
        
        except Exception as e:
            logger.error(f"Error saving region config: {e}")
    
    # =====================================================================
    # Utility
    # =====================================================================
    
    def get_threshold_presets(self) -> Dict[str, float]:
        """Get threshold presets"""
        return {
            'low': 0.5,
            'normal': 0.7,
            'strict': 0.85
        }
    
    def reset(self):
        """Reset engine state"""
        self.stop_all_tracks()
        self.frame_count = 0
        logger.info("Engine reset")


# =====================================================================
# Singleton instance getter
# =====================================================================

_engine_instance: Optional[VisionEngine] = None


def get_vision_engine(config_dir: str = "lib/data") -> VisionEngine:
    """
    Get or create vision engine singleton.
    
    Args:
        config_dir: Config directory path
        
    Returns:
        VisionEngine instance
    """
    global _engine_instance
    
    if _engine_instance is None:
        _engine_instance = VisionEngine(config_dir)
    
    return _engine_instance


# =====================================================================
# Example usage (for testing)
# =====================================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Vision Engine initialized")
    print("Use get_vision_engine() to get singleton instance")
    
    # Example
    engine = get_vision_engine()
    print(f"Threshold presets: {engine.get_threshold_presets()}")
    print(f"Parameters: {engine.get_params()}")
