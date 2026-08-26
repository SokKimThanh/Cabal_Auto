from unittest.mock import MagicMock
from ui.controllers.hotkey_controller import HotkeyController


def test_hotkey_controller_register_all():
    parent = MagicMock()
    parent.hotkey_mgr = MagicMock()

    controller = HotkeyController(parent)
    controller.register_all()

    parent.hotkey_mgr.register_all.assert_called_once()


def test_hotkey_controller_unregister_all():
    parent = MagicMock()
    parent.hotkey_mgr = MagicMock()

    controller = HotkeyController(parent)
    controller.unregister_all()

    parent.hotkey_mgr.unregister_all.assert_called_once()


def test_hotkey_controller_on_setup_wizard():
    parent = MagicMock()
    parent.hunt_cfg = {"ui_mode": "beginner"}
    parent._setup_wizard_win = None
    parent.setup_wizard_win = None
    parent._setup_wizard = None
    parent.window_controller = MagicMock()

    controller = HotkeyController(parent)
    controller.on_setup_wizard()

    assert parent.after.call_count == 1
    args, kwargs = parent.after.call_args
    assert args[0] == 0
    args, kwargs = parent.after.call_args
    assert args[0] == 0


def test_hotkey_controller_on_library_manager():
    parent = MagicMock()
    parent.library_manager_win = None

    controller = HotkeyController(parent)
    controller.on_library_manager()

    parent.after.assert_called_once_with(
        0, parent.window_controller.open_library_manager
    )
