from typing import Any

class HotkeyController:
    """Controller for global hotkey management."""

    def __init__(self, parent: Any):
        self.parent = parent
        self.hotkey_mgr = getattr(parent, "hotkey_mgr", None)

    def register_all(self) -> None:
        if self.hotkey_mgr:
            self.hotkey_mgr.register_all()

    def unregister_all(self) -> None:
        if self.hotkey_mgr:
            self.hotkey_mgr.unregister_all()

    def on_vision_wizard(self, *_args) -> None:
        if hasattr(self.parent, "window_controller"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.window_controller.open_vision_wizard)
            else:
                self.parent.window_controller.open_vision_wizard()

    def on_monster_editor(self, *_args) -> None:
        if hasattr(self.parent, "window_controller"):
            if hasattr(self.parent, "after"):
                self.parent.after(0, self.parent.window_controller.open_monster_manager)
            else:
                self.parent.window_controller.open_monster_manager()
