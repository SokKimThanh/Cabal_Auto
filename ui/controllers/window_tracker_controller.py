from typing import Any

class WindowTrackerController:
    """Controller for tracking game window bounds and overlay alignment."""

    def __init__(self, parent: Any):
        self.parent = parent

    def start(self) -> None:
        setattr(self.parent, "_window_tracker", None)
    def stop(self) -> None:
        if hasattr(self.parent, "_window_tracker"):
            self.parent._window_tracker = None
