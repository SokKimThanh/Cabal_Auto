"""
Example: Using VisionEngine with Screen Capture (Sprint 23 Phase 8)

Demonstrates how to use the integrated screen capture system with vision engine.

This example shows:
1. Starting screen capture for a game window
2. Using capture as frame source for worker
3. Getting capture statistics
4. Proper cleanup

Author: Sprint 23 Team
Date: 2025-10-23
"""

import sys
import time
import cv2

# Check Windows platform
if sys.platform != "win32":
    print("This example requires Windows platform")
    sys.exit(1)

from lib.vision.vision_engine import VisionEngine
from lib.system.window_manager import WindowManager


def main():
    """Main example function"""
    
    # Configuration
    WINDOW_TITLE = "Notepad"  # Change to your target window
    TARGET_FPS = 15
    CAPTURE_DURATION = 10  # seconds
    
    print("=" * 60)
    print("Vision Engine with Screen Capture Example")
    print("=" * 60)
    
    # Step 1: Create window manager
    print("\n1. Initializing WindowManager...")
    window_manager = WindowManager()
    print("✓ WindowManager created")
    
    # Step 2: Find target window
    print(f"\n2. Finding window: '{WINDOW_TITLE}'...")
    hwnd = window_manager.find_window(title_contains=WINDOW_TITLE)
    
    if not hwnd:
        print(f"❌ Window not found: {WINDOW_TITLE}")
        print("\nAvailable windows:")
        windows = window_manager.list_windows(visible_only=True)
        for win in windows[:10]:  # Show first 10
            print(f"  - {win.title}")
        return
    
    print(f"✓ Found window (hwnd={hwnd})")
    
    # Step 3: Get window info
    info = window_manager.get_window_info(hwnd)
    if info:
        print(f"  Title: {info.title}")
        print(f"  Size: {info.rect['width']}x{info.rect['height']}")
        print(f"  Position: ({info.rect['x']}, {info.rect['y']})")
        print(f"  Minimized: {info.is_minimized}")
        print(f"  Process: {info.process_name if info.process_name else 'N/A'}")
    
    # Step 4: Create vision engine
    print("\n3. Creating VisionEngine...")
    engine = VisionEngine()
    print("✓ VisionEngine created")
    
    # Step 5: Start screen capture
    print(f"\n4. Starting screen capture (target FPS: {TARGET_FPS})...")
    success = engine.start_capture(
        window_title=WINDOW_TITLE,
        target_fps=TARGET_FPS,
        queue_size=5
    )
    
    if not success:
        print("❌ Failed to start screen capture")
        return
    
    print("✓ Screen capture started")
    
    # Step 5: Start worker (will use capture automatically)
    print("\n4. Starting worker thread...")
    engine.start_worker()  # No callback needed - uses capture
    print("✓ Worker started")
    
    # Step 6: Display frames and statistics
    print(f"\n5. Capturing for {CAPTURE_DURATION} seconds...")
    print("Press 'q' to quit early\n")
    
    start_time = time.time()
    frames_displayed = 0
    last_stats_time = time.time()
    
    try:
        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= CAPTURE_DURATION:
                break
            
            # Get frame from capture
            frame = engine.get_capture_frame(timeout=0.1)
            
            if frame is not None:
                frames_displayed += 1
                
                # Display frame
                cv2.imshow(f"Capture: {WINDOW_TITLE}", frame)
                
                # Display statistics every second
                if time.time() - last_stats_time >= 1.0:
                    stats = engine.get_capture_stats()
                    if stats:
                        print(f"[{elapsed:.1f}s] "
                              f"FPS: {stats['fps']:.1f} | "
                              f"Captured: {stats['frames_captured']} | "
                              f"Dropped: {stats['frames_dropped']} | "
                              f"Queue: {stats['queue_size']}")
                    last_stats_time = time.time()
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nQuitting early...")
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Step 7: Cleanup
        print("\n6. Cleaning up...")
        
        # Stop worker (also stops capture)
        engine.stop_worker()
        print("✓ Worker stopped")
        
        # Close windows
        cv2.destroyAllWindows()
        print("✓ Windows closed")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("Final Statistics:")
        print("=" * 60)
        print(f"Duration: {time.time() - start_time:.1f}s")
        print(f"Frames displayed: {frames_displayed}")
        
        # Get final stats before cleanup
        if engine.is_capture_active():
            stats = engine.get_capture_stats()
            if stats:
                print(f"Total captured: {stats['frames_captured']}")
                print(f"Total dropped: {stats['frames_dropped']}")
                print(f"Average FPS: {stats['fps']:.1f}")
                drop_rate = (stats['frames_dropped'] / max(stats['frames_captured'], 1)) * 100
                print(f"Drop rate: {drop_rate:.1f}%")
        
        print("=" * 60)
        print("\n✓ Example completed successfully!")


def list_windows():
    """Helper function to list all windows"""
    print("\nListing all visible windows:")
    print("-" * 60)
    
    window_manager = WindowManager()
    windows = window_manager.list_windows(visible_only=True)
    
    for i, win in enumerate(windows, 1):
        print(f"{i}. {win.title}")
        print(f"   Size: {win.rect['width']}x{win.rect['height']}")
        print(f"   Process: {win.process_name if win.process_name else 'N/A'}")
        print()


if __name__ == "__main__":
    # Uncomment to list all windows first
    # list_windows()
    
    main()
