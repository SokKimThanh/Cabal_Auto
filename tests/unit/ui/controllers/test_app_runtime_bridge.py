import pytest
from unittest.mock import MagicMock
import sys

# Mock tkinter for headless environment
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

from ui.controllers.app_runtime_bridge import AppRuntimeBridgeMixin

class DummyApp(AppRuntimeBridgeMixin):
    def __init__(self):
        self.hotkey_controller = MagicMock()
        self.overlay_controller = MagicMock()
        self.window_tracker_controller = MagicMock()

        # for backwards compat checks in current code
        self.hotkey_mgr = MagicMock()
        self.window_controller = MagicMock()
        self.hunt_cfg = {"overlay": {}}

def test_bridge_interfaces_defined():
    app = DummyApp()

    app._register_global_hotkeys()
    app.hotkey_controller.register_all.assert_called_once()

    app._unregister_global_hotkeys()
    app.hotkey_controller.unregister_all.assert_called_once()

    app._on_vision_wizard_hotkey()
    app.hotkey_controller.on_vision_wizard.assert_called_once()

    app._on_monster_editor_hotkey()
    app.hotkey_controller.on_monster_editor.assert_called_once()

    app._start_overlay_window_tracker(12345)
    app.window_tracker_controller.start.assert_called_once_with(12345)

    app._stop_overlay_window_tracker()
    app.window_tracker_controller.stop.assert_called_once()

    app._open_overlay_settings()
    app.overlay_controller.open_settings.assert_called_once()
