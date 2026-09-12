import re

with open('ui/controllers/app_state_controller.py', 'r') as f:
    content = f.read()

props = """
    @property
    def hunt_cfg(self) -> Dict[str, Any]:
        return getattr(self, "_hunt_cfg", {})

    @hunt_cfg.setter
    def hunt_cfg(self, value: Dict[str, Any]) -> None:
        self._hunt_cfg = value

    @property
    def has_unsaved_changes(self) -> bool:
        return getattr(self, "_has_unsaved_changes", False)

    @has_unsaved_changes.setter
    def has_unsaved_changes(self, value: bool) -> None:
        self._has_unsaved_changes = value

    @property
    def bounds_recovery_failed(self) -> bool:
        return getattr(self, "_bounds_recovery_failed", False)

    @bounds_recovery_failed.setter
    def bounds_recovery_failed(self, value: bool) -> None:
        self._bounds_recovery_failed = value

    @property
    def win_items(self) -> List[Dict[str, Any]]:
        return getattr(self, "_win_items", [])

    @win_items.setter
    def win_items(self, value: List[Dict[str, Any]]) -> None:
        self._win_items = value

    @property
    def hunt_selected(self) -> Optional[Dict[str, Any]]:
        return getattr(self, "_hunt_selected", None)

    @hunt_selected.setter
    def hunt_selected(self, value: Optional[Dict[str, Any]]) -> None:
        self._hunt_selected = value

    @property
    def current_window_bounds(self) -> Any:
        return getattr(self, "_current_window_bounds", None)

    @current_window_bounds.setter
    def current_window_bounds(self, value: Any) -> None:
        self._current_window_bounds = value

"""

if "def hunt_cfg(" not in content:
    content = content.replace("class AppStateController:\n    \"\"\"Manages bound state variables and bookkeeping for the root App instance.\"\"\"", "class AppStateController:\n    \"\"\"Manages bound state variables and bookkeeping for the root App instance.\"\"\"\n" + props)
    content = content.replace("self.win_items =", "self._win_items =")
    content = content.replace("self.hunt_selected =", "self._hunt_selected =")
    content = content.replace("self.hunt_cfg =", "self._hunt_cfg =")
    with open('ui/controllers/app_state_controller.py', 'w') as f:
        f.write(content)
