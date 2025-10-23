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


def save_sample_images(samples_dir):
    """Create and save sample images for testing"""
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base frame
    frame = create_sample_image(640, 480, (50, 50, 50))
    
    # Add template pattern at known location
    template = create_sample_template(50, 50, (200, 100, 100))
    x, y = 100, 100
    frame[y:y+50, x:x+50] = template
    
    # Save images
    cv2.imwrite(str(samples_dir / "test_frame.png"), frame)
    cv2.imwrite(str(samples_dir / "test_template.png"), template)
    
    print(f"✅ Created sample images in {samples_dir}")
    return samples_dir / "test_frame.png", samples_dir / "test_template.png"


def test_engine_initialization():
    """Test 1: Engine initialization"""
    print("\n" + "="*60)
    print("TEST 1: Engine Initialization")
    print("="*60)
    
    engine = VisionEngine(config_dir="lib/data")
    
    assert engine is not None, "Engine should be created"
    assert isinstance(engine.get_params(), dict), "Params should be dict"
    assert isinstance(engine.get_threshold_presets(), dict), "Presets should be dict"
    
    print("✅ Engine initialized successfully")
    print(f"   Params: {engine.get_params()}")
    print(f"   Presets: {engine.get_threshold_presets()}")
    
    return engine


def test_template_loading(engine, template_path):
    """Test 2: Template loading"""
    print("\n" + "="*60)
    print("TEST 2: Template Loading")
    print("="*60)
    
    # Load template
    templates = engine.load_templates([str(template_path)])
    
    assert len(templates) > 0, "Should load at least one template"
    
    template_id = list(templates.keys())[0]
    template = templates[template_id]
    
    assert template.id is not None, "Template should have ID"
    assert template.path == str(template_path), "Template path should match"
    assert template.image is not None, "Template image should be loaded"
    assert template.threshold > 0, "Template should have threshold"
    
    print(f"✅ Loaded template: {template.id}")
    print(f"   Path: {template.path}")
    print(f"   Threshold: {template.threshold}")
    print(f"   Scales: {template.scales}")
    print(f"   Image shape: {template.image.shape}")
    
    return template


def test_detection(engine, frame_path):
    """Test 3: Template detection"""
    print("\n" + "="*60)
    print("TEST 3: Template Detection")
    print("="*60)
    
    # Load frame
    frame = cv2.imread(str(frame_path))
    assert frame is not None, "Frame should load"
    
    # Detect templates
    detections = engine.match_templates(frame, roi=None, max_results=10)
    
    print(f"✅ Detection completed")
    print(f"   Frame shape: {frame.shape}")
    print(f"   Detections found: {len(detections)}")
    
    # Verify detection structure
    for i, det in enumerate(detections):
        assert isinstance(det, Detection), "Should return Detection objects"
        assert hasattr(det, 'x'), "Detection should have x"
        assert hasattr(det, 'y'), "Detection should have y"
        assert hasattr(det, 'w'), "Detection should have w"
        assert hasattr(det, 'h'), "Detection should have h"
        assert hasattr(det, 'score'), "Detection should have score"
        assert hasattr(det, 'template_id'), "Detection should have template_id"
        assert hasattr(det, 'scale'), "Detection should have scale"
        
        print(f"   Detection {i+1}: bbox=({det.x}, {det.y}, {det.w}, {det.h}), "
              f"score={det.score:.3f}, template={det.template_id}, scale={det.scale}")
    
    return detections, frame


def test_nms(engine):
    """Test 4: NMS (Non-Maximum Suppression)"""
    print("\n" + "="*60)
    print("TEST 4: NMS (Non-Maximum Suppression)")
    print("="*60)
    
    # Create overlapping detections
    detections = [
        Detection(x=100, y=100, w=50, h=50, score=0.9, template_id="test", scale=1.0),
        Detection(x=105, y=105, w=50, h=50, score=0.8, template_id="test", scale=1.0),
        Detection(x=200, y=200, w=50, h=50, score=0.85, template_id="test", scale=1.0),
    ]
    
    print(f"   Before NMS: {len(detections)} detections")
    
    # Apply NMS
    filtered = engine.nms(detections, iou_threshold=0.3)
    
    print(f"   After NMS: {len(filtered)} detections")
    
    assert len(filtered) < len(detections), "NMS should reduce overlapping detections"
    assert all(isinstance(d, Detection) for d in filtered), "Should return Detection objects"
    
    print("✅ NMS working correctly")
    
    return filtered


def test_tracking(engine, frame, detections):
    """Test 5: Tracking"""
    print("\n" + "="*60)
    print("TEST 5: Tracking")
    print("="*60)
    
    if not detections:
        print("⚠️  No detections available, skipping tracking test")
        return []
    
    # Start tracking first detection
    detection = detections[0]
    tracker_id = engine.start_track(frame, detection)
    
    assert tracker_id != "", "Should return valid tracker ID"
    
    print(f"✅ Started tracking: {tracker_id}")
    print(f"   Detection: ({detection.x}, {detection.y}, {detection.w}, {detection.h})")
    
    # Simulate a few frame updates
    tracked_objects = []
    for i in range(3):
        # Update tracks (with same frame for simplicity)
        tracks = engine.update_tracks(frame)
        
        assert isinstance(tracks, list), "Should return list"
        
        if tracks:
            track = tracks[0]
            assert isinstance(track, TrackedObject), "Should return TrackedObject"
            assert hasattr(track, 'tracker_id'), "Track should have tracker_id"
            assert hasattr(track, 'bbox'), "Track should have bbox"
            assert hasattr(track, 'confidence'), "Track should have confidence"
            assert hasattr(track, 'last_verify_score'), "Track should have last_verify_score"
            
            print(f"   Frame {i+1}: bbox={track.bbox}, confidence={track.confidence:.3f}, "
                  f"verify={track.last_verify_score:.3f}")
            
            tracked_objects.append(track)
    
    # Stop tracking
    stopped = engine.stop_track(tracker_id)
    assert stopped, "Should stop tracker successfully"
    
    print(f"✅ Stopped tracking: {tracker_id}")
    
    return tracked_objects


def test_config_persistence(engine):
    """Test 6: Config persistence"""
    print("\n" + "="*60)
    print("TEST 6: Config Persistence")
    print("="*60)
    
    # Save templates config
    engine._save_templates_config()
    
    # Check config file exists
    assert engine.templates_config_path.exists(), "Templates config should be saved"
    
    # Set and save region
    test_region = (10, 10, 100, 100)
    engine.set_region(test_region)
    
    assert engine.region_config_path.exists(), "Region config should be saved"
    assert engine.get_region() == test_region, "Region should be saved correctly"
    
    print("✅ Config persistence working")
    print(f"   Templates config: {engine.templates_config_path}")
    print(f"   Region config: {engine.region_config_path}")
    print(f"   Saved region: {engine.get_region()}")


def run_all_tests():
    """Run all vision engine tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "VISION ENGINE TESTS" + " "*24 + "║")
    print("║" + " "*15 + "Sprint 22 Phase 2" + " "*26 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Setup
        samples_dir = Path(__file__).parent / "samples"
        frame_path, template_path = save_sample_images(samples_dir)
        
        # Run tests
        engine = test_engine_initialization()
        template = test_template_loading(engine, template_path)
        detections, frame = test_detection(engine, frame_path)
        filtered = test_nms(engine)
        tracked = test_tracking(engine, frame, detections)
        test_config_persistence(engine)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ All tests passed!")
        print(f"   Templates loaded: {len(engine.templates)}")
        print(f"   Detections found: {len(detections)}")
        print(f"   After NMS: {len(filtered)}")
        print(f"   Tracking updates: {len(tracked)}")
        print("="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
