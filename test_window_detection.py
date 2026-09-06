#!/usr/bin/env python3
"""Test window detection service"""

from lib.features.hunt.window_detection_service import WindowDetectionService
from lib.system.window_manager import WindowManager

print("[Test] Testing window enumeration...")
print()

# Test 1: Raw enumeration
print("=" * 60)
print("TEST 1: WindowDetectionService.find_all_cabal_windows()")
print("=" * 60)
try:
    service = WindowDetectionService()
    all_windows = service.find_all_cabal_windows()
    print(f"✓ Found {len(all_windows)} Cabal windows:")
    for i, w in enumerate(all_windows):
        print(f"  [{i}] {w['title']} [PID:{w['pid']}, HWND:{w['hwnd']}]")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: WindowManager.list_windows()
print("=" * 60)
print("TEST 2: WindowManager.list_windows()")
print("=" * 60)
try:
    wm = WindowManager()
    all_wins = wm.list_windows()
    print(f"✓ Found {len(all_wins)} total windows:")
    for i, w in enumerate(all_wins[:10]):  # Show first 10
        print(f"  [{i}] {w['title'][:50]}")
    if len(all_wins) > 10:
        print(f"  ... and {len(all_wins) - 10} more")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Best window detection
print("=" * 60)
print("TEST 3: WindowDetectionService.find_best_cabal_window()")
print("=" * 60)
try:
    service = WindowDetectionService()
    best = service.find_best_cabal_window()
    if best:
        print(f"✓ Best window: {best['title']} [PID:{best['pid']}]")
    else:
        print("✗ No best window found")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("[Test] Done!")
