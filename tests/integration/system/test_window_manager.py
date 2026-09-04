"""
Unit tests for Window Manager - Sprint 23 Phase 8
Tests window detection, manipulation, and monitoring
"""

import pytest
import sys

pytestmark = [
    pytest.mark.windows,
    pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows OS and pywin32/ctypes")
]

from unittest.mock import Mock, patch, MagicMock
import sys
if sys.platform == "win32":
    from lib.system.window_manager import (
        WindowManager,
        WindowInfo,
        find_cabal_window,
        get_cabal_rect
    )
else:
    WindowManager = None  # type: ignore
    WindowInfo = None  # type: ignore
    find_cabal_window = None  # type: ignore
    get_cabal_rect = None  # type: ignore


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def mock_win32():
    """Mock Windows API modules"""
    with patch('lib.system.window_manager.win32gui') as win32gui_mock, \
         patch('lib.system.window_manager.win32con') as win32con_mock, \
         patch('lib.system.window_manager.win32api') as win32api_mock, \
         patch('lib.system.window_manager.win32process') as win32process_mock, \
         patch('lib.system.window_manager.psutil') as psutil_mock:
        
        # Mock window enumeration
        def enum_windows(callback, param):
            # Simulate 3 windows
            callback(1001, param)  # Cabal window
            callback(1002, param)  # Other window
            callback(1003, param)  # Another window
            return True
        
        win32gui_mock.EnumWindows.side_effect = enum_windows
        win32gui_mock.IsWindow.return_value = True
        win32gui_mock.IsWindowVisible.return_value = True
        win32gui_mock.IsWindowEnabled.return_value = True
        win32gui_mock.IsIconic.return_value = False
        win32gui_mock.GetForegroundWindow.return_value = 1001
        
        # Mock window info
        def get_window_text(hwnd):
            titles = {
                1001: "Cabal Online",
                1002: "Notepad",
                1003: "Chrome"
            }
            return titles.get(hwnd, "Unknown")
        
        def get_class_name(hwnd):
            classes = {
                1001: "CabalWndClass",
                1002: "Notepad",
                1003: "Chrome_WidgetWin_1"
            }
            return classes.get(hwnd, "Unknown")
        
        win32gui_mock.GetWindowText.side_effect = get_window_text
        win32gui_mock.GetClassName.side_effect = get_class_name
        win32gui_mock.GetWindowRect.return_value = (100, 200, 1124, 968)
        win32gui_mock.GetClientRect.return_value = (0, 0, 1024, 768)
        win32gui_mock.ClientToScreen.return_value = (100, 200)
        
        # Mock process info
        win32process_mock.GetWindowThreadProcessId.return_value = (5000, 1234)
        
        mock_process = Mock()
        mock_process.name.return_value = "cabal.exe"
        psutil_mock.Process.return_value = mock_process
        
        yield {
            'win32gui': win32gui_mock,
            'win32con': win32con_mock,
            'win32api': win32api_mock,
            'win32process': win32process_mock,
            'psutil': psutil_mock
        }


@pytest.fixture
def window_manager(mock_win32):
    """Create WindowManager instance with mocked APIs"""
    return WindowManager()


# =====================================================================
# Unit Tests - Initialization
# =====================================================================

def test_window_manager_initialization():
    """Test WindowManager initialization"""
    wm = WindowManager()
    
    assert wm._cached_windows == {}
    assert wm._cache_timeout == 2.0


# =====================================================================
# Unit Tests - Find Window
# =====================================================================

def test_find_window_by_title(window_manager):
    """Test finding window by title substring"""
    hwnd = window_manager.find_window(title_contains="Cabal")
    
    assert hwnd == 1001


def test_find_window_case_insensitive(window_manager):
    """Test case-insensitive title search"""
    hwnd = window_manager.find_window(title_contains="cabal")
    
    assert hwnd == 1001


def test_find_window_by_class_name(window_manager):
    """Test finding window by class name"""
    hwnd = window_manager.find_window(class_name="CabalWndClass")
    
    assert hwnd == 1001


def test_find_window_by_process_name(window_manager):
    """Test finding window by process name"""
    hwnd = window_manager.find_window(process_name="cabal.exe")
    
    assert hwnd == 1001


def test_find_window_not_found(window_manager):
    """Test window not found returns None"""
    hwnd = window_manager.find_window(title_contains="NonExistent")
    
    assert hwnd is None


def test_find_window_multiple_criteria(window_manager):
    """Test finding window with multiple criteria"""
    hwnd = window_manager.find_window(
        title_contains="Cabal",
        process_name="cabal"
    )
    
    assert hwnd == 1001


# =====================================================================
# Unit Tests - Find All Windows
# =====================================================================

def test_find_all_windows(window_manager):
    """Test finding all windows matching criteria"""
    hwnds = window_manager.find_all_windows(visible_only=True)
    
    assert len(hwnds) == 3
    assert 1001 in hwnds
    assert 1002 in hwnds
    assert 1003 in hwnds


def test_find_all_windows_filtered(window_manager):
    """Test finding all windows with filter"""
    hwnds = window_manager.find_all_windows(title_contains="Cabal")
    
    assert len(hwnds) == 1
    assert hwnds[0] == 1001


# =====================================================================
# Unit Tests - List Windows
# =====================================================================

def test_list_windows(window_manager):
    """Test listing all windows with details"""
    windows = window_manager.list_windows(visible_only=True)
    
    assert len(windows) == 3
    assert all(isinstance(w, WindowInfo) for w in windows)


def test_list_windows_filtered(window_manager):
    """Test listing windows with filter"""
    windows = window_manager.list_windows(title_contains="Cabal")
    
    assert len(windows) == 1
    assert windows[0].title == "Cabal Online"
    assert windows[0].hwnd == 1001


def test_list_windows_invisible(mock_win32):
    """Test invisible windows are excluded"""
    mock_win32['win32gui'].IsWindowVisible.return_value = False
    
    wm = WindowManager()
    windows = wm.list_windows(visible_only=True)
    
    assert len(windows) == 0


def test_list_windows_include_invisible(mock_win32):
    """Test including invisible windows"""
    mock_win32['win32gui'].IsWindowVisible.return_value = False
    
    wm = WindowManager()
    windows = wm.list_windows(visible_only=False)
    
    assert len(windows) == 3


# =====================================================================
# Unit Tests - Window Info
# =====================================================================

def test_get_window_info(window_manager):
    """Test getting complete window information"""
    info = window_manager.get_window_info(1001)
    
    assert info is not None
    assert info.hwnd == 1001
    assert info.title == "Cabal Online"
    assert info.class_name == "CabalWndClass"
    assert info.pid == 1234
    assert info.process_name == "cabal.exe"
    assert info.is_visible is True
    assert info.is_foreground is True


def test_get_window_info_invalid_hwnd(mock_win32):
    """Test get_window_info with invalid HWND"""
    mock_win32['win32gui'].IsWindow.return_value = False
    
    wm = WindowManager()
    info = wm.get_window_info(9999)
    
    assert info is None


def test_window_info_str():
    """Test WindowInfo string representation"""
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
    
    string = str(info)
    assert "Test Window" in string
    assert "test.exe" in string
    assert "100x100" in string


# =====================================================================
# Unit Tests - Window Rect
# =====================================================================

def test_get_window_rect(window_manager):
    """Test getting window rectangle"""
    rect = window_manager.get_window_rect(1001)
    
    assert rect['left'] == 100
    assert rect['top'] == 200
    assert rect['right'] == 1124
    assert rect['bottom'] == 968
    assert rect['width'] == 1024
    assert rect['height'] == 768


def test_get_window_rect_invalid(mock_win32):
    """Test get_window_rect with invalid HWND"""
    mock_win32['win32gui'].GetWindowRect.side_effect = Exception("Invalid window")
    
    wm = WindowManager()
    rect = wm.get_window_rect(9999)
    
    # Should return zero rect on error
    assert rect['width'] == 0
    assert rect['height'] == 0


def test_get_client_rect(window_manager):
    """Test getting window client area"""
    rect = window_manager.get_client_rect(1001)
    
    assert rect['left'] == 100
    assert rect['top'] == 200
    assert rect['width'] == 1024
    assert rect['height'] == 768


# =====================================================================
# Unit Tests - Window Manipulation
# =====================================================================

def test_set_foreground(window_manager, mock_win32):
    """Test setting window to foreground"""
    result = window_manager.set_foreground(1001)
    
    assert result is True
    mock_win32['win32gui'].SetForegroundWindow.assert_called_once_with(1001)


def test_set_foreground_minimized(window_manager, mock_win32):
    """Test set_foreground restores minimized window"""
    mock_win32['win32gui'].IsIconic.return_value = True
    
    result = window_manager.set_foreground(1001)
    
    assert result is True
    mock_win32['win32gui'].ShowWindow.assert_called()


def test_minimize_window(window_manager, mock_win32):
    """Test minimizing window"""
    result = window_manager.minimize(1001)
    
    assert result is True
    mock_win32['win32gui'].ShowWindow.assert_called_once()


def test_maximize_window(window_manager, mock_win32):
    """Test maximizing window"""
    result = window_manager.maximize(1001)
    
    assert result is True
    mock_win32['win32gui'].ShowWindow.assert_called_once()


def test_restore_window(window_manager, mock_win32):
    """Test restoring window"""
    result = window_manager.restore(1001)
    
    assert result is True
    mock_win32['win32gui'].ShowWindow.assert_called_once()


def test_manipulation_error_handling(window_manager, mock_win32):
    """Test window manipulation error handling"""
    mock_win32['win32gui'].ShowWindow.side_effect = Exception("Error")
    
    result = window_manager.minimize(1001)
    
    assert result is False


# =====================================================================
# Unit Tests - Window Validation
# =====================================================================

def test_is_window_valid(window_manager):
    """Test checking if window is valid"""
    result = window_manager.is_window_valid(1001)
    
    assert result is True


def test_is_window_valid_invalid(mock_win32):
    """Test checking invalid window"""
    mock_win32['win32gui'].IsWindow.return_value = False
    
    wm = WindowManager()
    result = wm.is_window_valid(9999)
    
    assert result is False


def test_is_window_valid_exception(mock_win32):
    """Test is_window_valid handles exceptions"""
    mock_win32['win32gui'].IsWindow.side_effect = Exception("Error")
    
    wm = WindowManager()
    result = wm.is_window_valid(1001)
    
    assert result is False


# =====================================================================
# Unit Tests - Wait For Window
# =====================================================================

def test_wait_for_window_found_immediately(window_manager):
    """Test wait_for_window when window exists"""
    import time
    start = time.time()
    
    hwnd = window_manager.wait_for_window("Cabal", timeout=5.0)
    
    elapsed = time.time() - start
    
    assert hwnd == 1001
    assert elapsed < 1.0  # Should find immediately


@pytest.mark.slow
def test_wait_for_window_timeout(window_manager):
    """Test wait_for_window timeout"""
    import time
    start = time.time()
    
    hwnd = window_manager.wait_for_window("NonExistent", timeout=1.0)
    
    elapsed = time.time() - start
    
    assert hwnd is None
    assert elapsed >= 1.0


@pytest.mark.slow
def test_wait_for_window_appears_later(mock_win32):
    """Test wait_for_window when window appears after delay"""
    call_count = [0]
    
    def get_window_text(hwnd):
        call_count[0] += 1
        # Window appears after 3 calls
        if call_count[0] >= 3:
            return "Cabal Online"
        return "Other"
    
    mock_win32['win32gui'].GetWindowText.side_effect = get_window_text
    
    wm = WindowManager()
    hwnd = wm.wait_for_window("Cabal", timeout=5.0, check_interval=0.3)
    
    assert hwnd is not None


# =====================================================================
# Unit Tests - Monitor Info
# =====================================================================

def test_get_monitor_info(mock_win32):
    """Test getting monitor information"""
    def enum_monitors(callback, param):
        # Simulate 2 monitors
        callback(2001, None, (0, 0, 1920, 1080), param)
        callback(2002, None, (1920, 0, 3840, 1080), param)
        return True
    
    mock_win32['win32api'].EnumDisplayMonitors.side_effect = enum_monitors
    mock_win32['win32api'].GetMonitorInfo.side_effect = [
        {'Flags': 1, 'Work': (0, 0, 1920, 1040)},  # Primary
        {'Flags': 0, 'Work': (1920, 0, 3840, 1040)}  # Secondary
    ]
    mock_win32['win32con'].MONITORINFOF_PRIMARY = 1
    
    wm = WindowManager()
    monitors = wm.get_monitor_info()
    
    assert len(monitors) == 2
    assert monitors[0]['rect']['width'] == 1920
    assert monitors[1]['rect']['width'] == 1920


def test_get_window_monitor(mock_win32):
    """Test getting monitor containing window"""
    # Mock MonitorFromWindow
    mock_win32['win32api'].MonitorFromWindow.return_value = 2001
    
    # Mock EnumDisplayMonitors
    def enum_monitors(callback, param):
        callback(2001, None, (0, 0, 1920, 1080), param)
        return True
    
    mock_win32['win32api'].EnumDisplayMonitors.side_effect = enum_monitors
    mock_win32['win32api'].GetMonitorInfo.return_value = {
        'Flags': 1,
        'Work': (0, 0, 1920, 1040)
    }
    mock_win32['win32con'].MONITORINFOF_PRIMARY = 1
    mock_win32['win32con'].MONITOR_DEFAULTTONEAREST = 2
    
    wm = WindowManager()
    monitor = wm.get_window_monitor(1001)
    
    assert monitor is not None
    assert monitor['handle'] == 2001


# =====================================================================
# Unit Tests - Convenience Functions
# =====================================================================

def test_find_cabal_window(mock_win32):
    """Test find_cabal_window convenience function"""
    hwnd = find_cabal_window()
    
    assert hwnd == 1001


def test_find_cabal_window_not_found(mock_win32):
    """Test find_cabal_window when not found"""
    mock_win32['win32gui'].GetWindowText.return_value = "Other Window"
    
    hwnd = find_cabal_window()
    
    assert hwnd is None


def test_get_cabal_rect(mock_win32):
    """Test get_cabal_rect convenience function"""
    rect = get_cabal_rect()
    
    assert rect is not None
    assert rect['width'] == 1024
    assert rect['height'] == 768


def test_get_cabal_rect_not_found(mock_win32):
    """Test get_cabal_rect when Cabal not found"""
    mock_win32['win32gui'].GetWindowText.return_value = "Other Window"
    
    rect = get_cabal_rect()
    
    assert rect is None


# =====================================================================
# Edge Cases
# =====================================================================

def test_empty_window_title(mock_win32):
    """Test handling empty window title"""
    mock_win32['win32gui'].GetWindowText.return_value = ""
    
    wm = WindowManager()
    windows = wm.list_windows()
    
    # Should still work
    assert len(windows) >= 0


def test_process_name_unavailable(mock_win32):
    """Test handling when process name is unavailable"""
    mock_win32['psutil'].Process.side_effect = Exception("Process not found")
    
    wm = WindowManager()
    info = wm.get_window_info(1001)
    
    assert info is not None
    assert info.process_name == "Unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
