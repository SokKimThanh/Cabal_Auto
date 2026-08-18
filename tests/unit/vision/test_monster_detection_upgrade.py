"""
Unit tests for upgraded Monster Detection System (3D perspective, scale, rotation, HSV fallback, ROI, downscaling, edge cases).
"""

import pytest
import numpy as np
import cv2
import time
from lib.vision.vision_engine import VisionEngine, Template, Detection


@pytest.fixture
def vision_engine(tmp_path):
    """Fixture providing a clean VisionEngine instance"""
    engine = VisionEngine(config_dir=str(tmp_path))
    return engine


def test_detection_dataclass():
    """Test Detection dataclass bbox and center calculations"""
    det = Detection(x=100, y=200, w=50, h=60, score=0.9, template_id="test_tpl", method_used="test")
    assert det.bbox() == (100, 200, 50, 60)
    assert det.center() == (125, 230)
    assert det.to_dict()["score"] == 0.9


def test_hsv_target_detection(vision_engine):
    """Test fast HSV target (e.g. red target outline/health bar) detection"""
    # Create a black image with a bright red rectangle in the center
    frame = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(frame, (200, 150), (260, 180), (0, 0, 255), -1)  # BGR Red

    # Detect red color (HSV: H near 0/180, S high, V high)
    lower_red = (0, 150, 150)
    upper_red = (10, 255, 255)

    detections = vision_engine.detect_hsv_target(
        frame,
        lower_hsv=lower_red,
        upper_hsv=upper_red,
        min_area=50,
        max_area=10000
    )

    assert len(detections) > 0
    best_det = detections[0]
    assert best_det.method_used == "hsv_mask"
    assert abs(best_det.x - 200) <= 2
    assert abs(best_det.y - 150) <= 2
    assert abs(best_det.w - 60) <= 2
    assert abs(best_det.h - 30) <= 2
    assert best_det.center() == (best_det.x + best_det.w // 2, best_det.y + best_det.h // 2)


def test_hsv_noise_filtering(vision_engine):
    """Test min_area and max_area filtering for HSV detection"""
    frame = np.zeros((400, 600, 3), dtype=np.uint8)
    # Very small noise speck (2x2 pixels)
    cv2.rectangle(frame, (10, 10), (12, 12), (0, 0, 255), -1)
    # Normal target (40x40 = 1600 area)
    cv2.rectangle(frame, (100, 100), (140, 140), (0, 0, 255), -1)
    # Huge background block (200x200 = 40000 area)
    cv2.rectangle(frame, (300, 100), (500, 300), (0, 0, 255), -1)

    lower_red = (0, 150, 150)
    upper_red = (10, 255, 255)

    # Filter out noise (<100) and huge area (>10000)
    detections = vision_engine.detect_hsv_target(
        frame,
        lower_hsv=lower_red,
        upper_hsv=upper_red,
        min_area=100,
        max_area=10000
    )

    assert len(detections) == 1
    assert abs(detections[0].x - 100) <= 2


def test_feature_matching_orb(vision_engine):
    """Test ORB feature matching with scale and rotation"""
    # Create synthetic pattern image
    tpl_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(tpl_img, (50, 50), 40, (255, 255, 255), -1)
    cv2.rectangle(tpl_img, (20, 20), (80, 80), (100, 200, 50), 3)
    cv2.line(tpl_img, (0, 0), (100, 100), (0, 255, 0), 2)
    cv2.line(tpl_img, (0, 100), (100, 0), (255, 0, 0), 2)

    template = Template(
        id="pattern_monster",
        path="synthetic",
        image=tpl_img,
        threshold=0.6
    )

    # Place transformed image in a larger scene
    scene = np.zeros((600, 800, 3), dtype=np.uint8)

    # Rotate 30 deg and scale 1.2x
    M = cv2.getRotationMatrix2D((50, 50), 30, 1.2)
    transformed_tpl = cv2.warpAffine(tpl_img, M, (120, 120))

    # Place in scene at offset (300, 200)
    scene[200:320, 300:420] = transformed_tpl

    detections = vision_engine.detect_features(
        scene,
        template=template,
        feature_type='ORB',
        min_matches=4
    )

    assert len(detections) > 0
    det = detections[0]
    assert det.method_used == "orb_features"
    # Check bounding box overlaps scene region (300:420, 200:320)
    assert 250 <= det.x <= 450
    assert 150 <= det.y <= 350


def test_roi_and_downscaling(vision_engine):
    """Test Region of Interest (ROI) and downscaling coordinate remapping"""
    frame = np.zeros((1000, 1000, 3), dtype=np.uint8)
    # Place target at (600, 600)
    cv2.rectangle(frame, (600, 600), (650, 650), (0, 0, 255), -1)

    lower_red = (0, 150, 150)
    upper_red = (10, 255, 255)

    # Define ROI covering (500, 500, 300, 300)
    roi = (500, 500, 300, 300)

    # Test with 0.5x downscaling
    detections = vision_engine.detect_hsv_target(
        frame,
        lower_hsv=lower_red,
        upper_hsv=upper_red,
        min_area=50,
        roi=roi,
        downscale_factor=0.5
    )

    assert len(detections) > 0
    det = detections[0]
    # Check that remapped coordinates match original full frame position (~600, 600)
    assert abs(det.x - 600) <= 5
    assert abs(det.y - 600) <= 5
    assert abs(det.w - 50) <= 5
    assert abs(det.h - 50) <= 5


def test_monster_pipeline_priority(vision_engine):
    """Test Fast Priority Pipeline: Fast HSV path executes first when available"""
    frame = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add target outline/HP bar
    cv2.rectangle(frame, (200, 200), (250, 230), (0, 0, 255), -1)

    # Set engine HSV params
    vision_engine.set_params({
        'hsv_lower': (0, 150, 150),
        'hsv_upper': (10, 255, 255),
        'hsv_min_area': 10
    })

    detections = vision_engine.detect_monster_pipeline(frame, use_fast_hsv=True)

    assert len(detections) > 0
    assert detections[0].method_used == "hsv_mask"
    assert abs(detections[0].x - 200) <= 2


def test_edge_cases_empty_and_black_images(vision_engine):
    """Edge Case Tests: Empty, black, zero keypoints, out-of-bounds ROI"""
    # 1. Empty image
    empty_frame = np.array([], dtype=np.uint8)
    assert vision_engine.detect_hsv_target(empty_frame) == []
    assert vision_engine.detect_monster_pipeline(empty_frame) == []

    # 2. Black frame with no features or target
    black_frame = np.zeros((200, 200, 3), dtype=np.uint8)
    assert vision_engine.detect_hsv_target(black_frame) == []

    # 3. Feature matching with zero keypoints
    blank_template = Template(
        id="blank",
        path="blank",
        image=np.zeros((50, 50, 3), dtype=np.uint8)
    )
    assert vision_engine.detect_features(black_frame, blank_template) == []

    # 4. Out-of-bounds / invalid ROI
    out_of_bounds_roi = (1000, 1000, 500, 500)
    assert vision_engine.detect_hsv_target(black_frame, roi=out_of_bounds_roi) == []

    # 5. Extremely small downscale factor or invalid dimensions
    assert vision_engine.detect_hsv_target(black_frame, downscale_factor=0.00001) == []
