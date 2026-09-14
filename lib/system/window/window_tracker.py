from typing import Any, Dict, List, Optional

class WindowTracker:
    """
    Trinh sát: Quản lý trạng thái, tọa độ, danh sách và theo dõi cửa sổ game.
    """
    def __init__(self):
        self._current_window_bounds: Any = None
        self._win_items: List[Dict[str, Any]] = []
        self._hunt_selected: Optional[Dict[str, Any]] = None
        self._bounds_recovery_failed: bool = False

    @property
    def current_window_bounds(self) -> Any:
        return self._current_window_bounds

    @current_window_bounds.setter
    def current_window_bounds(self, value: Any) -> None:
        self._current_window_bounds = value

    @property
    def win_items(self) -> List[Dict[str, Any]]:
        return self._win_items

    @win_items.setter
    def win_items(self, value: List[Dict[str, Any]]) -> None:
        self._win_items = value

    @property
    def hunt_selected(self) -> Optional[Dict[str, Any]]:
        return self._hunt_selected

    @hunt_selected.setter
    def hunt_selected(self, value: Optional[Dict[str, Any]]) -> None:
        self._hunt_selected = value

    @property
    def bounds_recovery_failed(self) -> bool:
        return self._bounds_recovery_failed

    @bounds_recovery_failed.setter
    def bounds_recovery_failed(self, value: bool) -> None:
        self._bounds_recovery_failed = value
