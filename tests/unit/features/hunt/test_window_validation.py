import sys
import unittest.mock as mock

# Completely mock lib.system.window_manager to avoid ctypes.windll import error on Linux
wm_mock = mock.MagicMock()
sys.modules["lib.system.window_manager"] = wm_mock

import pytest
from lib.features.hunt.window_selection_service import validate_selected_cabal_window

class MockWindowInfo:
    def __init__(self, hwnd=123, title="Cabal", pid=456, process_name="cabal.exe", is_visible=True, is_enabled=True, is_minimized=False, is_offscreen=False):
        self.hwnd = hwnd
        self.title = title
        self.pid = pid
        self.process_name = process_name
        self.rect = {"left": 0, "top": 0, "right": 100, "bottom": 100, "width": 100, "height": 100}
        self.is_visible = is_visible
        self.is_enabled = is_enabled
        self.is_minimized = is_minimized
        self.is_offscreen = is_offscreen

class MockWindowManager:
    def __init__(self, info=None, valid=True):
        self.info = info
        self.valid = valid

    def get_window_info(self, hwnd):
        return self.info

    def is_window_valid(self, hwnd):
        return self.valid

@pytest.fixture
def valid_info():
    return MockWindowInfo()

def test_validate_no_window_selected():
    res = validate_selected_cabal_window(None, [])
    assert not res.is_valid
    assert res.code == "no_window_selected"

def test_validate_valid_window(monkeypatch, valid_info):
    monkeypatch.setattr("lib.features.hunt.window_selection_service.WindowManager", lambda: MockWindowManager(info=valid_info))
    selected = {"hwnd": 123, "pid": 456}
    res = validate_selected_cabal_window(selected, [{"hwnd": 123}])
    assert res.is_valid
    assert res.code == "ok"
    assert res.window["hwnd"] == 123

def test_validate_wrong_process(monkeypatch, valid_info):
    valid_info.process_name = "notepad.exe"
    monkeypatch.setattr("lib.features.hunt.window_selection_service.WindowManager", lambda: MockWindowManager(info=valid_info))
    selected = {"hwnd": 123, "pid": 456}
    res = validate_selected_cabal_window(selected, [{"hwnd": 123}])
    assert not res.is_valid
    assert res.code == "no_cabal_window"

def test_validate_changed_pid(monkeypatch, valid_info):
    valid_info.pid = 999
    monkeypatch.setattr("lib.features.hunt.window_selection_service.WindowManager", lambda: MockWindowManager(info=valid_info))
    selected = {"hwnd": 123, "pid": 456}
    res = validate_selected_cabal_window(selected, [{"hwnd": 123}])
    assert not res.is_valid
    assert res.code == "window_changed"

def test_validate_window_minimized(monkeypatch, valid_info):
    valid_info.is_minimized = True
    monkeypatch.setattr("lib.features.hunt.window_selection_service.WindowManager", lambda: MockWindowManager(info=valid_info))
    selected = {"hwnd": 123, "pid": 456}
    res = validate_selected_cabal_window(selected, [{"hwnd": 123}])
    assert not res.is_valid
    assert res.code == "window_unavailable"

def test_validate_window_closed(monkeypatch, valid_info):
    monkeypatch.setattr("lib.features.hunt.window_selection_service.WindowManager", lambda: MockWindowManager(info=valid_info, valid=False))
    selected = {"hwnd": 123, "pid": 456}
    res = validate_selected_cabal_window(selected, [{"hwnd": 123}])
    assert not res.is_valid
    assert res.code == "window_unavailable"
