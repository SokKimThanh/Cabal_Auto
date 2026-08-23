"""
Unit tests for MatcherService boundary checks, empty ROIs, and channel normalization.
"""

import cv2
import pytest
import numpy as np
from lib.vision.template_loader import Template
from lib.vision.matcher_service import MatcherService


@pytest.fixture
def matcher_service():
    return MatcherService()


def test_matcher_service_empty_frame_and_roi(matcher_service):
    """Test boundary checks on empty frames and out-of-bounds ROIs"""
    empty_frame = np.array([], dtype=np.uint8)
    assert matcher_service.match_templates(empty_frame, templates={}) == []

    valid_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    out_of_bounds_roi = (200, 200, 50, 50)
    assert matcher_service.match_templates(valid_frame, templates={}, roi=out_of_bounds_roi) == []


def test_matcher_service_bgr_color_matching_mode(matcher_service):
    """Test full 3-channel BGR color matching when use_grayscale=False"""
    np.random.seed(42)
    # Red textured template (high Red, zero Blue)
    red_tpl = np.random.randint(50, 255, (30, 30, 3), dtype=np.uint8)
    red_tpl[:, :, 0] = 0

    template = Template(id="red_tpl", path="dummy", image=red_tpl, threshold=0.7)

    # Blue textured frame patch (high Blue, zero Red)
    blue_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    blue_tex = np.random.randint(50, 255, (30, 30, 3), dtype=np.uint8)
    blue_tex[:, :, 2] = 0
    blue_frame[30:60, 30:60] = blue_tex

    # With use_grayscale=False, matching Red template on Blue frame should yield no detection due to color mismatch
    dets_bgr = matcher_service.match_templates(
        blue_frame,
        templates={template.id: template},
        use_grayscale=False
    )
    assert len(dets_bgr) == 0


def test_matcher_service_channel_compatibility(matcher_service):
    """Test matching with 3-channel BGR frame and 1-channel grayscale frame inputs"""
    tpl_img = np.random.randint(50, 200, (30, 30, 3), dtype=np.uint8)
    template = Template(id="channel_test", path="dummy", image=tpl_img, threshold=0.8)

    # 3-channel frame
    bgr_frame = np.zeros((150, 150, 3), dtype=np.uint8)
    bgr_frame[40:70, 40:70] = tpl_img

    dets_bgr = matcher_service.match_templates(bgr_frame, templates={template.id: template})
    assert len(dets_bgr) > 0
    assert dets_bgr[0].x == 40
    assert dets_bgr[0].y == 40

    # 1-channel grayscale frame directly passed to match_template_at_scale
    gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
    dets_gray = matcher_service.match_template_at_scale(gray_frame, template, scale=1.0, offset_x=0, offset_y=0)
    assert len(dets_gray) > 0
    assert dets_gray[0].x == 40
    assert dets_gray[0].y == 40


def test_matcher_service_nms(matcher_service):
    """Test vectorized Non-Maximum Suppression (NMS)"""
    from lib.vision.vision_engine import Detection

    d1 = Detection(x=10, y=10, w=50, h=50, score=0.9, template_id="t1")
    d2 = Detection(x=12, y=12, w=50, h=50, score=0.8, template_id="t1")  # High overlap
    d3 = Detection(x=200, y=200, w=50, h=50, score=0.85, template_id="t1")  # Distinct

    filtered = matcher_service.nms([d1, d2, d3], iou_threshold=0.3)
    assert len(filtered) == 2
    scores = [d.score for d in filtered]
    assert 0.9 in scores
    assert 0.85 in scores
