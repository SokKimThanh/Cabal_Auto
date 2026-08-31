import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock

@pytest.fixture
def app_instance():
    from app_gui import App
    app = App()
    app.update()
    yield app
    app.destroy()

def test_debounce_click(app_instance):
    # Mock orchestrator and validation
    app_instance.hunt_orchestrator = MagicMock()
    app_instance.hunt_orchestrator.hunt_running = False
    app_instance.state_controller._validate_hunt_prerequisites = MagicMock(return_value=None)
    app_instance.state_controller._hunt_from_ui = MagicMock(return_value={})
    app_instance.hunt_cfg = {}

    with patch("app_gui.save_hunt_config") as mock_save:
        # Click 5 times
        for _ in range(5):
            app_instance.on_hunt_start()

        # Assert start was only called once because of debounce
        assert app_instance.hunt_orchestrator.start_hunt.call_count == 1
        assert getattr(app_instance, "_action_locked", False) is True

def test_minimize_recovery(app_instance):
    import sys
    from unittest.mock import MagicMock

    # Pre-mock the module in sys.modules to avoid ImportError
    mock_wm_module = MagicMock()
    mock_wm_class = MagicMock()
    mock_wm_module.WindowManager = mock_wm_class
    sys.modules['lib.system.window_manager'] = mock_wm_module

    # We must mock it in app_window_controller since that's where the local import is executed.
    # However, since the import is inside the function: `from lib.system.window_manager import WindowManager`
    # patching sys.modules should be enough for the inner import to pick up the mocked class.

    mock_wm_instance = MagicMock()
    mock_wm_class.return_value = mock_wm_instance

    class MockInfo:
        is_minimized = True
        rect = {'left': -32000, 'top': -32000}
    mock_wm_instance.get_window_info.return_value = MockInfo()

    app_instance.hunt_selected = {"hwnd": 12345}

    with patch("time.sleep"):  # Avoid actual sleep
        app_instance.window_controller.on_hunt_refresh_windows()

    assert mock_wm_instance.restore.call_count == 3

def test_dynamic_i18n(app_instance):
    app_instance.lang_var.set("en")
    app_instance.on_language_change()

    # In 'en' language
    if hasattr(app_instance.hunt_start_btn, "cget"):
        text = app_instance.hunt_start_btn.cget("text")
        # Ensure it contains 'Start' (e.g. 'Start Hunt')
        assert "Start" in text

    app_instance.lang_var.set("vi")
    app_instance.on_language_change()

    # In 'vi' language (fallback text or defined translations)
    if hasattr(app_instance.hunt_start_btn, "cget"):
        text = app_instance.hunt_start_btn.cget("text")
        assert "Bắt Đầu" in text or "Start" not in text  # Checking it changed
