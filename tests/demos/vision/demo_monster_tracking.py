"""
Monster Tracking Demo Script
Sprint 23 Phase 7 Batch 4 Task 4.2

Demonstrates monster tracking system without full app.
Shows how to use the monster tracking components programmatically.

Features:
- Initialize vision system
- Start monster detection
- Create overlay controller
- Display real-time detections
- Show performance stats

Usage:
    python tests/demos/vision/demo_monster_tracking.py
    
Requirements:
    - Game window must be running
    - Monster templates configured in hunt_config.json
    - Overlay window available
"""

import sys
import time
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from lib.vision.vision_engine import VisionEngine
from lib.system.screen_capture import ScreenCapture
from lib.system.bot_manager import BotManager
from ui.utils.overlay_controller import OverlayController


def load_config():
    """Load hunt configuration."""
    config_path = project_root / "lib" / "data" / "hunt_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_banner():
    """Print demo banner."""
    print("=" * 70)
    print("MONSTER TRACKING DEMO - Sprint 23 Phase 7")
    print("=" * 70)
    print()


def print_config_summary(config):
    """Print configuration summary."""
    tracking = config.get('monster_tracking', {})
    
    print("Configuration:")
    print(f"  Enabled: {tracking.get('enabled', False)}")
    print(f"  Detection Interval: {tracking.get('detection_interval', 0.1)}s")
    print(f"  Confidence Threshold: {tracking.get('confidence_threshold', 0.7)}")
    print(f"  Stable Frames: {tracking.get('stable_frames', 3)}")
    print(f"  Lost Timeout: {tracking.get('lost_timeout', 3.0)}s")
    print(f"  Max Detections Display: {tracking.get('max_detections_display', 20)}")
    print(f"  Show Stats: {tracking.get('show_stats', True)}")
    print(f"  Stats Update Interval: {tracking.get('stats_update_interval', 0.5)}s")
    print()


def print_instructions():
    """Print usage instructions."""
    print("Instructions:")
    print("  1. Make sure game window is running")
    print("  2. Overlay will show detected monsters with bounding boxes")
    print("  3. Stats will display FPS, latency, and detection count")
    print("  4. Press Ctrl+C to stop demo")
    print()


def create_mock_overlay():
    """Create mock overlay for demo (prints to console)."""
    class MockOverlay:
        def __init__(self):
            self.last_boxes = []
            self.last_stats = None
            
        def update_detection_boxes(self, boxes, stats=None):
            """Update detection boxes (console output)."""
            if boxes != self.last_boxes or stats != self.last_stats:
                self.last_boxes = boxes
                self.last_stats = stats
                
                # Clear some lines
                print("\r" + " " * 100 + "\r", end="")
                
                if boxes:
                    print(f"\r[DETECTIONS] Count: {len(boxes)} ", end="")
                    for box in boxes[:3]:  # Show first 3
                        name = box.get('name', 'Unknown')
                        conf = box.get('confidence', 0.0)
                        print(f"| {name}({conf:.2f}) ", end="")
                else:
                    print("\r[DETECTIONS] No monsters detected", end="")
                
                if stats:
                    fps = stats.get('fps', 0.0)
                    latency = stats.get('latency_ms', 0.0)
                    total = stats.get('total_detections', 0)
                    print(f"| FPS: {fps:.1f} Lat: {latency:.1f}ms Total: {total}", end="")
                
                print("", flush=True)
        
        def clear_detection_boxes(self):
            """Clear detection boxes."""
            print("\r[CLEARED] All detections cleared" + " " * 50)
            self.last_boxes = []
            self.last_stats = None
    
    return MockOverlay()


def demo_basic_detection(config):
    """Demo 1: Basic detection without overlay."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Detection (No Overlay)")
    print("=" * 70)
    
    tracking = config.get('monster_tracking', {})
    
    # Create components
    print("[1/4] Creating VisionEngine...")
    vision_engine = VisionEngine()
    
    print("[2/4] Creating ScreenCapture...")
    screen_capture = ScreenCapture()
    
    print("[3/4] Creating BotManager...")
    manager = BotManager(
        vision_engine=vision_engine,
        screen_capture=screen_capture,
        stable_frames=int(tracking.get('stable_frames', 3)),
        lost_timeout=float(tracking.get('lost_timeout', 3.0))
    )
    
    # Register callback
    detection_count = [0]
    
    def on_detections(detections):
        detection_count[0] = len(detections)
        if detections:
            print(f"\r[DETECTED] {len(detections)} monsters found", end="", flush=True)
    
    manager.on_detections_changed(on_detections)
    
    print("[4/4] Starting detection...")
    success = manager.start_detection()
    
    if success:
        print("[OK] Detection running! Detecting for 5 seconds...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        
        # Get stats
        stats = manager.get_bot_stats()
        print(f"\n\nStats:")
        print(f"  Detections Count: {stats.detections_count}")
        print(f"  Detection FPS: {stats.detection_fps:.1f}")
        print(f"  Uptime: {stats.uptime_seconds:.1f}s")
    else:
        print("[ERROR] Failed to start detection")
    
    # Cleanup
    print("\nCleaning up...")
    manager.destroy()
    print("[OK] Demo 1 complete!\n")


def demo_with_overlay_controller(config):
    """Demo 2: Detection with OverlayController."""
    print("\n" + "=" * 70)
    print("DEMO 2: Detection with OverlayController")
    print("=" * 70)
    
    tracking = config.get('monster_tracking', {})
    
    # Create components
    print("[1/5] Creating VisionEngine...")
    vision_engine = VisionEngine()
    
    print("[2/5] Creating ScreenCapture...")
    screen_capture = ScreenCapture()
    
    print("[3/5] Creating BotManager...")
    manager = BotManager(
        vision_engine=vision_engine,
        screen_capture=screen_capture,
        stable_frames=int(tracking.get('stable_frames', 3)),
        lost_timeout=float(tracking.get('lost_timeout', 3.0))
    )
    
    print("[4/5] Starting detection...")
    success = manager.start_detection()
    
    if not success:
        print("[ERROR] Failed to start detection")
        manager.destroy()
        return
    
    print("[5/5] Creating OverlayController with mock overlay...")
    overlay = create_mock_overlay()
    
    controller = OverlayController(
        overlay=overlay,
        detector=manager._detector,
        max_boxes=int(tracking.get('max_detections_display', 20)),
        show_stats=bool(tracking.get('show_stats', True)),
        stats_update_interval=float(tracking.get('stats_update_interval', 0.5))
    )
    
    controller.start()
    print("[OK] OverlayController running! Monitoring for 10 seconds...")
    print("(Watch console for real-time detection updates)\n")
    
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stopping demo...")
    
    # Cleanup
    print("\n\nCleaning up...")
    controller.stop()
    manager.destroy()
    print("[OK] Demo 2 complete!\n")


def demo_auto_start_with_hunt(config):
    """Demo 3: Auto-start with hunt integration."""
    print("\n" + "=" * 70)
    print("DEMO 3: Auto-Start with Hunt Integration")
    print("=" * 70)
    
    tracking = config.get('monster_tracking', {})
    
    # Create components with auto-start enabled
    print("[1/3] Creating BotManager with auto-start enabled...")
    vision_engine = VisionEngine()
    screen_capture = ScreenCapture()
    
    manager = BotManager(
        vision_engine=vision_engine,
        screen_capture=screen_capture,
        enable_auto_start=True  # Enable auto-start
    )
    
    print("[2/3] Simulating hunt start...")
    manager.on_hunt_start()
    
    if manager.is_detection_running():
        print("[OK] Detection auto-started with hunt!")
        print("Running for 5 seconds...")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        
        # Get stats
        stats = manager.get_bot_stats()
        print(f"\nStats:")
        print(f"  Detections Count: {stats.detections_count}")
    else:
        print("[ERROR] Auto-start failed")
    
    print("[3/3] Simulating hunt stop...")
    manager.on_hunt_stop()
    
    if not manager.is_detection_running():
        print("[OK] Detection auto-stopped with hunt!")
    
    # Cleanup
    print("\nCleaning up...")
    manager.destroy()
    print("[OK] Demo 3 complete!\n")


def main():
    """Main demo entry point."""
    try:
        # Print banner
        print_banner()
        
        # Load config
        print("Loading configuration...")
        config = load_config()
        print_config_summary(config)
        print_instructions()
        
        # Check if enabled
        tracking = config.get('monster_tracking', {})
        if not tracking.get('enabled', False):
            print("[WARNING] Monster tracking is disabled in config!")
            print("          Set 'monster_tracking.enabled' to true to use this feature.")
            print()
        
        # Run demos
        input("Press ENTER to start Demo 1 (Basic Detection)...")
        demo_basic_detection(config)
        
        input("Press ENTER to start Demo 2 (With OverlayController)...")
        demo_with_overlay_controller(config)
        
        input("Press ENTER to start Demo 3 (Auto-Start with Hunt)...")
        demo_auto_start_with_hunt(config)
        
        # Done
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETE!")
        print("=" * 70)
        print("\nNext Steps:")
        print("  - Review logs/hunt_structured.jsonl for detection logs")
        print("  - Adjust config values in lib/data/hunt_config.json")
        print("  - Run full app with: python app_gui.py")
        print()
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Demo stopped by user")
    except FileNotFoundError as e:
        print(f"\n[ERROR] File not found: {e}")
        print("Make sure you run this from the project root directory")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
