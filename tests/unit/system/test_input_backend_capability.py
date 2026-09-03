import pytest
from unittest.mock import patch

from lib.system.input_backend import BackgroundWindowMessageBackend, WIN32_AVAILABLE, ForegroundSendInputBackend
from lib.system.input_capability import InputCapabilityManager, InputCapabilityState

@pytest.fixture
def mock_win32gui():
    with patch("lib.system.input_backend.win32gui") as mock:
        yield mock

@pytest.fixture
def mock_win32con():
    with patch("lib.system.input_backend.win32con") as mock:
        mock.WM_KEYDOWN = 0x0100
        mock.WM_KEYUP = 0x0101
        yield mock

def test_foreground_backend_tap():
    with patch("lib.system.win_input.tap") as mock_tap:
        backend = ForegroundSendInputBackend()
        assert backend.mode == "foreground"
        result = backend.tap("A", 100)
        assert result is True
        mock_tap.assert_called_once_with("A", 100)

@pytest.mark.skipif(not WIN32_AVAILABLE, reason="win32 API not available")
def test_background_backend_key_down(mock_win32gui, mock_win32con):
    hwnd = 12345
    backend = BackgroundWindowMessageBackend(hwnd)

    assert backend.key_down("A") is True

    mock_win32gui.PostMessage.assert_called_once()
    args, kwargs = mock_win32gui.PostMessage.call_args
    assert args[0] == hwnd
    assert args[1] == mock_win32con.WM_KEYDOWN
    assert args[2] == 0x41
    assert "A" in backend._held_keys

@pytest.mark.skipif(not WIN32_AVAILABLE, reason="win32 API not available")
def test_background_backend_close_releases_keys(mock_win32gui, mock_win32con):
    hwnd = 12345
    backend = BackgroundWindowMessageBackend(hwnd)

    backend._held_keys.add("C")
    backend._held_keys.add("D")

    backend.close()

    assert mock_win32gui.PostMessage.call_count == 2
    assert len(backend._held_keys) == 0

def test_input_capability_manager_unverified(tmp_path):
    with patch("lib.system.input_capability.CAPABILITY_DB_FILE", str(tmp_path / "cap")):
        mgr = InputCapabilityManager(1234, "background", None)
        assert mgr._get_state() == InputCapabilityState.UNVERIFIED

def test_input_capability_manager_check_and_verify(tmp_path):
    with patch("lib.system.input_capability.CAPABILITY_DB_FILE", str(tmp_path / "cap")):
        mgr = InputCapabilityManager(1234, "background", None)

        with patch("lib.system.input_backend.BackgroundWindowMessageBackend.tap", return_value=True):
            state, ready = mgr.check_and_verify_capability()
            assert state == InputCapabilityState.SUPPORTED
            assert ready is True

def test_input_capability_manager_check_and_verify_fail(tmp_path):
    with patch("lib.system.input_capability.CAPABILITY_DB_FILE", str(tmp_path / "cap")):
        mgr = InputCapabilityManager(1234, "background", None)

        with patch("lib.system.input_backend.BackgroundWindowMessageBackend.tap", return_value=False):
            state, ready = mgr.check_and_verify_capability()
            assert state == InputCapabilityState.UNSUPPORTED
            assert ready is False
