import sys
from unittest.mock import MagicMock, patch

# Isolate headless-only mocks to just the import of the module-under-test
with patch.dict(
    sys.modules,
    {
        "tkinter": MagicMock(),
        "tkinter.messagebox": MagicMock(),
        "PIL": MagicMock(),
        "PIL.ImageTk": MagicMock(),
    },
):
    from ui.controllers.hotkey_controller import HotkeyController

@patch('ui.controllers.hotkey_controller.keyboard')
def test_hotkey_controller_register_all(mock_keyboard):
    # Explicitly test a config setup
    hunt_cfg = {
        "global_hotkeys": {
            "enabled": True,
            "start_key": "f5",
            "stop_key": "f6",
            "setup_wizard_key": "f7",
            "library_manager_key": "f8",
            "vision_wizard_key": "f9",
            "monster_editor_key": "f10"
        },
        "ui_mode": "beginner"
    }

    parent = MagicMock()
    parent.hunt_cfg = hunt_cfg

    controller = HotkeyController(parent, hunt_cfg)
    controller.register_all()

    assert mock_keyboard.add_hotkey.call_count == 6
    mock_keyboard.add_hotkey.assert_any_call("f5", controller.on_hunt_start, suppress=False)
    mock_keyboard.add_hotkey.assert_any_call("f10", controller.on_monster_editor, suppress=False)

@patch('ui.controllers.hotkey_controller.keyboard')
def test_hotkey_controller_unregister_all(mock_keyboard):
    hunt_cfg = {
        "global_hotkeys": {
            "enabled": True,
            "start_key": "f5",
            "stop_key": "f6",
            "setup_wizard_key": "f7",
            "library_manager_key": "f8",
            "vision_wizard_key": "f9",
            "monster_editor_key": "f10"
        },
        "ui_mode": "beginner"
    }

    parent = MagicMock()
    parent.hunt_cfg = hunt_cfg

    controller = HotkeyController(parent, hunt_cfg)

    # We need a mock handler returned to be removed
    mock_keyboard.add_hotkey.return_value = "mock_handler"
    controller.register_all()

    controller.unregister_all()

    assert mock_keyboard.remove_hotkey.call_count == 6  # 6 hotkeys registered by default

def test_hotkey_controller_on_setup_wizard():
    hunt_cfg = {"ui_mode": "beginner"}

    parent = MagicMock()
    parent.hunt_cfg = hunt_cfg
    parent._setup_wizard_win = None
    parent.setup_wizard_win = None
    parent._setup_wizard = None

    controller = HotkeyController(parent, hunt_cfg)
    controller.on_setup_wizard()

    assert parent.after.call_count == 1
    args, kwargs = parent.after.call_args
    assert args[0] == 0

def test_hotkey_controller_on_library_manager():
    parent = MagicMock()
    parent.hunt_cfg = {}
    parent.library_manager_win = None

    controller = HotkeyController(parent, {})
    controller.on_library_manager()

    parent.after.assert_called_once_with(
        0, parent.window_controller.open_library_manager
    )
