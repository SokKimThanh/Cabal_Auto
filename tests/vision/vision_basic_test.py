"""
Basic Vision Engine Tests
Sprint 22 Phase 2

Tests core engine functionality with sample images.
"""

import sys
import os
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mark as vision test
pytestmark = pytest.mark.vision

import cv2
import numpy as np
from lib.vision.vision_engine import VisionEngine, Detection, TrackedObject, Template


def create_sample_image(width=640, height=480, color=(100, 100, 100)):
    """Create a sample image for testing"""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    return img


def create_sample_template(width=50, height=50, color=(255, 0, 0)):
    """Create a sample template"""
    template = np.zeros((height, width, 3), dtype=np.uint8)
    template[:] = color
    # Add distinct pattern
    cv2.rectangle(template, (10, 10), (40, 40), (0, 255, 0), 2)
    return template


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def samples_dir():
    """Create samples directory with test images."""
    test_dir = Path(__file__).parent / "samples"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base frame
    frame = create_sample_image(640, 480, (50, 50, 50))
    
    # Add template pattern at known location
    template = create_sample_template(50, 50, (200, 100, 100))
    x, y = 100, 100
    frame[y:y+50, x:x+50] = template
    
    # Save images
    frame_path = test_dir / "test_frame.png"
    template_path = test_dir / "test_template.png"
    cv2.imwrite(str(frame_path), frame)
    cv2.imwrite(str(template_path), template)
    
    return test_dir


@pytest.fixture(scope="module")
def engine():
    """Create VisionEngine instance for testing."""
    return VisionEngine(config_dir="lib/data")


@pytest.fixture(scope="module")
def template_path(samples_dir):
    """Get path to test template image."""
    return samples_dir / "test_template.png"


@pytest.fixture(scope="module")
def frame_path(samples_dir):
    """Get path to test frame image."""
    return samples_dir / "test_frame.png"


@pytest.fixture
def frame(frame_path):
    """Load test frame image."""
    img = cv2.imread(str(frame_path))
    assert img is not None, f"Failed to load frame from {frame_path}"
    return img


@pytest.fixture
def detections(engine, frame_path):
    """Get sample detections for testing."""
    frame = cv2.imread(str(frame_path))
    return engine.match_templates(frame, roi=None, max_results=10)


# ============================================================================
# TESTS
# ============================================================================

def test_engine_initialization(engine):
    """Test 1: Engine initialization"""
    assert engine is not None, "Engine should be created"
    assert isinstance(engine.get_params(), dict), "Params should be dict"
    assert isinstance(engine.get_threshold_presets(), dict), "Presets should be dict"


def test_template_loading(engine, template_path):
    """Test 2: Template loading"""
    # Load template
    templates = engine.load_templates([str(template_path)])
    
    assert len(templates) > 0, "Should load at least one template"
    
    template_id = list(templates.keys())[0]
    template = templates[template_id]
    
    assert template.id is not None, "Template should have ID"
    assert template.path == str(template_path), "Template path should match"
    assert template.image is not None, "Template image should be loaded"
    assert template.threshold > 0, "Template should have threshold"


def test_detection(engine, frame, detections):
    """Test 3: Template detection"""
    # Verify detections
    assert isinstance(detections, list), "Should return list of detections"
    
    # Verify detection structure
    for det in detections:
        assert isinstance(det, Detection), "Should return Detection objects"
        assert hasattr(det, 'x'), "Detection should have x"
        assert hasattr(det, 'y'), "Detection should have y"
        assert hasattr(det, 'w'), "Detection should have w"
        assert hasattr(det, 'h'), "Detection should have h"
        assert hasattr(det, 'score'), "Detection should have score"
        assert hasattr(det, 'template_id'), "Detection should have template_id"
        assert hasattr(det, 'scale'), "Detection should have scale"


def test_nms(engine):
    """Test 4: NMS (Non-Maximum Suppression)"""
    # Create overlapping detections
    detections = [
        Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="test", scale=1.0),
        Detection(x=105, y=105, w=50, h=50, score=0.8, template_id="test", scale=1.0),
        Detection(x=200, y=200, w=50, h=50, score=0.85, template_id="test", scale=1.0),
    ]
    
    # Apply NMS
    filtered = engine.nms(detections, iou_threshold=0.3)
    
    assert len(filtered) < len(detections), "NMS should reduce overlapping detections"
    assert len(filtered) >= 1, "NMS should keep at least one detection"
    assert all(isinstance(d, Detection) for d in filtered), "Should return Detection objects"


def test_tracking(engine, frame, detections):
    """Test 5: Tracking"""
    if not detections:
        pytest.skip("No detections available for tracking test")
    
    # Start tracking first detection
    detection = detections[0]
    tracker_id = engine.start_track(frame, detection)
    
    assert tracker_id != "", "Should return valid tracker ID"
    assert isinstance(tracker_id, str), "Tracker ID should be string"
    
    # Update tracks
    tracks = engine.update_tracks(frame)
    
    assert isinstance(tracks, list), "Should return list of tracks"
    
    if tracks:
        track = tracks[0]
        assert isinstance(track, TrackedObject), "Should return TrackedObject"
        assert hasattr(track, 'tracker_id'), "Track should have tracker_id"
        assert hasattr(track, 'bbox'), "Track should have bbox"
        assert hasattr(track, 'confidence'), "Track should have confidence"
    
    # Stop tracking
    stopped = engine.stop_track(tracker_id)
    assert stopped, "Should stop tracker successfully"


def test_config_persistence(engine):
    """Test 6: Config persistence"""
    # Save templates config
    engine._save_templates_config()
    
    # Check config file exists
    assert engine.templates_config_path.exists(), "Templates config should be saved"
    
    # Set and save region
    test_region = (10, 10, 100, 100)
    engine.set_region(test_region)
    
    assert engine.region_config_path.exists(), "Region config should be saved"
    assert engine.get_region() == test_region, "Region should be saved correctly"




# ============================================================================
# MANUAL TESTING SCRIPT (not for pytest)
# ============================================================================

if __name__ == "__main__":
    """Manual test execution - creates sample images and runs tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "VISION ENGINE TESTS" + " "*24 + "║")
    print("║" + " "*12 + "(Manual Execution Mode)" + " "*23 + "║")
    print("╚" + "="*58 + "╝")
    print("\n⚠️  For automated testing, use: pytest tests/vision/vision_basic_test.py")
    print()
    
    sys.exit(pytest.main([__file__, "-v"]))
