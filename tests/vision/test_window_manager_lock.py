import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock win32 modules for testing on non-Windows
sys.modules['win32gui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['ctypes'] = MagicMock()
sys.modules['ctypes.wintypes'] = MagicMock()

from lib.system.window_manager import WindowManager, WindowInfo

@pytest.fixture(autouse=True)
def reset_window_manager_lock():
    # Setup
    WindowManager._locked_hwnd = None
    yield
    # Teardown
    WindowManager._locked_hwnd = None


def test_lock_and_unlock_selection():
    wm = WindowManager()
    assert wm._locked_hwnd is None
    assert wm.get_selected_window() is None

    # Test lock
    wm.lock_selection(1234)
    assert WindowManager._locked_hwnd == 1234

    # Mock get_window_info since we are not on actual Windows
    with patch.object(WindowManager, 'get_window_info') as mock_get_window_info:
        mock_info = MagicMock(spec=WindowInfo)
        mock_info.hwnd = 1234
        mock_get_window_info.return_value = mock_info

        selected = wm.get_selected_window()
        assert selected is not None
        assert selected.hwnd == 1234
        mock_get_window_info.assert_called_once_with(1234)

    # Test unlock
    wm.unlock_selection()
    assert WindowManager._locked_hwnd is None
    assert wm.get_selected_window() is None
