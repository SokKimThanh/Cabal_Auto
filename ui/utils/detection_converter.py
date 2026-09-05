"""
Detection Converter - Convert VisionEngine detections to Overlay display format
Sprint 23 Phase 5 - Overlay Integration

Provides utility functions to convert VisionEngine Detection objects
to OverlayWindow DetectionBox format for real-time visualization.
"""

from typing import List, Tuple, Optional
from lib.vision.vision_engine import Detection
from ui.windows.overlay_window import DetectionBox


def detection_to_box(
    detection: Detection,
    label: Optional[str] = None,
    color: Optional[Tuple[int, int, int]] = None,
    state: str = "detected",
) -> DetectionBox:
    """
    Convert VisionEngine Detection to Overlay DetectionBox.

    Args:
        detection: VisionEngine Detection object
        label: Custom label, or None to auto-generate from template_id
        color: RGB color tuple, or None to auto-select by state
        state: Detection state ('searching', 'detected', 'tracking')

    Returns:
        DetectionBox ready for overlay rendering

    Example:
        >>> detection = Detection(x=100, y=200, w=50, h=60, score=0.85, template_id="monster1", scale=1.0)
        >>> box = detection_to_box(detection, state="detected")
        >>> overlay.update_detections([box])
    """
    # Auto-generate label if not provided
    if label is None:
        label = f"{detection.template_id} ({detection.score:.2f})"

    # Auto-select color if not provided
    if color is None:
        color = get_state_color(state)

    return DetectionBox(
        x=detection.x,
        y=detection.y,
        w=detection.w,
        h=detection.h,
        label=label,
        color=color,
        confidence=detection.score,
    )


def detections_to_boxes(
    detections: List[Detection], state: str = "detected", max_boxes: int = 20
) -> List[DetectionBox]:
    """
    Convert multiple VisionEngine Detections to Overlay DetectionBoxes.

    Args:
        detections: List of Detection objects from VisionEngine
        state: State for all boxes ('searching', 'detected', 'tracking')
        max_boxes: Maximum number of boxes to create (limit for performance)

    Returns:
        List of DetectionBox objects

    Example:
        >>> detections = engine.match_templates(frame)
        >>> boxes = detections_to_boxes(detections, state="detected")
        >>> overlay.update_detections(boxes)
    """
    boxes = []

    for idx, detection in enumerate(detections[:max_boxes]):
        # Label with index number
        label = f"#{idx+1} {detection.template_id} ({detection.score:.0%})"

        box = detection_to_box(detection, label=label, state=state)
        boxes.append(box)

    return boxes


def get_state_color(state: str) -> Tuple[int, int, int]:
    """
    Get RGB color for detection state.

    Args:
        state: 'searching', 'detected', 'tracking'

    Returns:
        RGB tuple (0-255 range)
    """
    STATE_COLORS = {
        "searching": (255, 0, 0),  # Red
        "detected": (0, 255, 0),  # Green
        "tracking": (0, 150, 255),  # Blue-ish
        "lost": (255, 255, 0),  # Yellow
    }

    return STATE_COLORS.get(state, (128, 128, 128))  # Gray default


def create_empty_search_box(
    x: int = 100, y: int = 100, w: int = 200, h: int = 150
) -> DetectionBox:
    """
    Create a "searching" box when no detections found.

    Args:
        x, y, w, h: Bounding box coordinates

    Returns:
        DetectionBox with "Searching..." state

    Example:
        >>> if not detections:
        >>>     overlay.update_detections([create_empty_search_box()])
    """
    return DetectionBox(
        x=x,
        y=y,
        w=w,
        h=h,
        label="Searching for monsters...",
        color=(255, 0, 0),  # Red
        confidence=0.0,
    )


# =====================================================================
# Usage Examples
# =====================================================================

if __name__ == "__main__":
    # Example 1: Single detection
    from lib.vision.vision_engine import Detection

    det = Detection(
        x=100,
        y=200,
        w=50,
        h=60,
        score=0.85,
        template_id="monster_orc",
        scale=1.0,
        timestamp=0.0,
    )

    box = detection_to_box(det, state="detected")
    print(f"DetectionBox: {box}")

    # Example 2: Multiple detections
    detections = [
        Detection(100, 200, 50, 60, 0.85, "monster1", 1.0),
        Detection(300, 400, 60, 70, 0.92, "monster2", 1.0),
        Detection(500, 100, 55, 65, 0.78, "monster3", 1.0),
    ]

    boxes = detections_to_boxes(detections, state="tracking")
    print(f"Created {len(boxes)} boxes for overlay")

    # Example 3: No detections
    empty_box = create_empty_search_box()
    print(f"Empty search box: {empty_box}")
