"""
Simple validation tests for Phase 8 modules
Tests basic imports and class instantiation without Windows APIs
"""

import sys
from pathlib import Path
import pytest

pytestmark = pytest.mark.unit


# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_imports_work_on_windows():
    """Test that imports work on Windows platform"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    try:
        from lib.system import screen_capture, window_manager
        print("✓ Imports successful")
        assert True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        assert False, f"Import error: {e}"


def test_screen_capture_classes_exist():
    """Test that ScreenCapture classes are defined"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.screen_capture import ScreenCapture, CaptureStats, create_capture
    
    assert ScreenCapture is not None, "ScreenCapture class should exist"
    assert CaptureStats is not None, "CaptureStats class should exist"
    assert create_capture is not None, "create_capture function should exist"
    print("✓ ScreenCapture classes exist")


def test_window_manager_classes_exist():
    """Test that WindowManager classes are defined"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.window_manager import WindowManager, WindowInfo
    
    assert WindowManager is not None, "WindowManager class should exist"
    assert WindowInfo is not None, "WindowInfo class should exist"
    print("✓ WindowManager classes exist")


def test_screen_capture_instantiation():
    """Test that ScreenCapture can be instantiated"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.screen_capture import ScreenCapture
    
    capture = ScreenCapture(queue_size=5, target_fps=15)
    
    assert capture.queue_size == 5, "queue_size should be 5"
    assert capture.target_fps == 15, "target_fps should be 15"
    assert capture.running == False, "Should not be running initially"
    assert capture.hwnd is None, "hwnd should be None initially"
    print("✓ ScreenCapture instantiation works")


def test_window_manager_instantiation():
    """Test that WindowManager can be instantiated"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.window_manager import WindowManager
    
    wm = WindowManager()
    
    assert wm is not None, "WindowManager should be instantiated"
    assert hasattr(wm, 'find_window'), "Should have find_window method"
    assert hasattr(wm, 'get_window_rect'), "Should have get_window_rect method"
    print("✓ WindowManager instantiation works")


def test_capture_stats_dataclass():
    """Test CaptureStats dataclass"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.screen_capture import CaptureStats
    
    stats = CaptureStats()
    
    assert stats.frames_captured == 0, "frames_captured should default to 0"
    assert stats.frames_dropped == 0, "frames_dropped should default to 0"
    assert stats.fps == 0.0, "fps should default to 0.0"
    assert stats.avg_capture_time_ms == 0.0, "avg_capture_time_ms should default to 0.0"
    print("✓ CaptureStats dataclass works")


def test_window_info_dataclass():
    """Test WindowInfo dataclass"""
    if sys.platform != "win32":
        print("SKIP: Not Windows platform")
        return
    
    from lib.system.window_manager import WindowInfo
    
    info = WindowInfo(
        hwnd=1001,
        title="Test Window",
        class_name="TestClass",
        pid=1234,
        process_name="test.exe",
        rect={'left': 0, 'top': 0, 'right': 100, 'bottom': 100, 'width': 100, 'height': 100},
        is_visible=True,
        is_enabled=True,
        is_minimized=False,
        is_maximized=False,
        is_foreground=False
    )
    
    assert info.hwnd == 1001, "hwnd should be preserved"
    assert info.title == "Test Window", "title should be preserved"
    assert info.is_visible == True, "is_visible should be True"
    print("✓ WindowInfo dataclass works")


def test_non_windows_platform_check():
    """Test that modules raise ImportError on non-Windows"""
    if sys.platform == "win32":
        print("SKIP: Is Windows platform")
        return
    
    try:
        from lib.system import screen_capture
        print("✗ Should have raised ImportError on non-Windows")
        assert False, "Should raise ImportError on non-Windows"
    except ImportError as e:
        assert "Windows" in str(e), "Error message should mention Windows"
        print(f"✓ Correctly raised ImportError: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 8 Simple Validation Tests")
    print("=" * 60)
    
    tests = [
        test_imports_work_on_windows,
        test_screen_capture_classes_exist,
        test_window_manager_classes_exist,
        test_screen_capture_instantiation,
        test_window_manager_instantiation,
        test_capture_stats_dataclass,
        test_window_info_dataclass,
        test_non_windows_platform_check,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test in tests:
        print(f"\nRunning: {test.__name__}")
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {e}")
            failed += 1
        except Exception as e:
            if "SKIP" in str(e):
                skipped += 1
            else:
                print(f"  ERROR: {e}")
                failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
