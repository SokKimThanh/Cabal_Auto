"""
Overlay Integration Demo - Test overlay with simulated vision detections
Sprint 23 Phase 5

Demonstrates:
1. Creating overlay with WindowTracker
2. Simulating detection data from VisionEngine
3. Updating overlay in real-time
4. Handling window movement/resize

Usage:
    python tests/demos/demo_overlay_vision.py
"""

import sys
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.ui.overlay_window_pywin32 import OverlayWindowPyWin32, DetectionBox
from lib.ui.detection_converter import detections_to_boxes, create_empty_search_box
from lib.vision.vision_engine import Detection
from lib.system.window_manager import WindowManager


def simulate_detections(frame_num: int) -> list:
    """
    Simulate vision detection results.
    
    Returns random detections every N frames to simulate
    the vision engine finding/losing monsters.
    """
    # Every 5 frames, chance to detect monsters
    if frame_num % 5 != 0:
        return []
    
    # 70% chance to detect something
    if random.random() > 0.7:
        return []
    
    # Generate 1-3 random detections
    num_detections = random.randint(1, 3)
    detections = []
    
    for i in range(num_detections):
        detection = Detection(
            x=random.randint(100, 600),
            y=random.randint(100, 400),
            w=random.randint(50, 150),
            h=random.randint(50, 150),
            score=random.uniform(0.7, 0.95),
            template_id=f"monster_{random.choice(['orc', 'skeleton', 'goblin'])}",
            scale=1.0,
            timestamp=time.time()
        )
        detections.append(detection)
    
    return detections


def main():
    """Main demo loop."""
    print("=" * 60)
    print("Overlay Vision Integration Demo")
    print("=" * 60)
    
    # 1. Find CABAL window
    print("\n[1] Finding CABAL window...")
    wm = WindowManager()
    windows = wm.list_windows()
    
    cabal_window = None
    for w in windows:
        if 'CABAL' in w.title.upper():
            cabal_window = w
            print(f"    ✅ Found: {w.title} [HWND:{w.hwnd}]")
            break
    
    if not cabal_window:
        print("    ❌ CABAL window not found!")
        print("    💡 Please open CABAL game and try again.")
        return
    
    # 2. Create overlay
    print("\n[2] Creating overlay...")
    overlay = OverlayWindowPyWin32(
        target_rect=cabal_window.rect,
        alpha=0.7,
        fps_limit=15,
        enable_click_through=True
    )
    overlay.create()
    overlay.show()
    print("    ✅ Overlay created and shown")
    
    # 3. Simulation loop
    print("\n[3] Starting simulation loop...")
    print("    Press Ctrl+C to stop")
    print("-" * 60)
    
    frame_num = 0
    detection_state = "searching"  # 'searching', 'detected', 'tracking'
    
    try:
        while True:
            frame_num += 1
            
            # Simulate vision engine detection
            detections = simulate_detections(frame_num)
            
            if detections:
                # Detections found!
                detection_state = "detected"
                boxes = detections_to_boxes(detections, state=detection_state)
                print(f"[Frame {frame_num:04d}] 🎯 Detected {len(detections)} monsters")
            else:
                # No detections - show searching state
                detection_state = "searching"
                boxes = [create_empty_search_box(x=200, y=150, w=300, h=200)]
                if frame_num % 30 == 0:  # Print every 30 frames
                    print(f"[Frame {frame_num:04d}] 🔍 Searching...")
            
            # Update overlay
            overlay.update_detections(boxes)
            
            # Sleep to maintain ~15 FPS
            time.sleep(1.0 / 15.0)
            
    except KeyboardInterrupt:
        print("\n\n[4] Stopping demo...")
    
    finally:
        # Cleanup
        overlay.hide()
        overlay.destroy()
        print("    ✅ Overlay cleaned up")
        print("\n" + "=" * 60)
        print("Demo complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
