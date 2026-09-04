from abc import ABC, abstractmethod
from typing import Dict, Tuple, Callable, Optional

class HuntStatusHandler(ABC):
    """Abstract base class for orchestrator status callbacks."""

    # UI Update callbacks
    @abstractmethod
    def on_status_update(self, message: str) -> None:
        """Status message to display in UI."""
        pass

    @abstractmethod
    def on_state_change(self, state: str) -> None:
        """Hunt state changed."""
        pass

    @abstractmethod
    def update_skill_stats_display(self, stats: dict) -> None:
        """Update skill statistics in UI."""
        pass

    @abstractmethod
    def set_target_info(self, info: str) -> None:
        """Set target information display."""
        pass

    @abstractmethod
    def clear_target_ui(self) -> None:
        """Clear target information from UI."""
        pass

    # Window Management callbacks
    @abstractmethod
    def bring_window_to_front(self, window_name: str) -> bool:
        """Bring window to foreground."""
        pass

    @abstractmethod
    def bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        """Bring window to front by handle."""
        pass

    @abstractmethod
    def bring_window_to_front_by_pid(self, pid: int) -> bool:
        """Bring window to front by process ID."""
        pass

    @abstractmethod
    def iconify_app(self) -> None:
        """Minimize application."""
        pass

def locate_target(self, params: Dict) -> Tuple[Optional[Tuple[int, int, int, int]], Optional[dict]]:

    @abstractmethod
    def prepare_skill_runtime(self, skill_def: Dict) -> list:
        """Prepare skill for execution."""
        pass

    @abstractmethod
    def try_cast_skills(self, *args, **kwargs) -> None:
        """Attempt to cast skills."""
        pass

    @abstractmethod
    def on_scene_monsters_detected(self, monsters: Tuple) -> None:
        """Monsters detected in scene."""
        pass

    # Utility callbacks
    @abstractmethod
    def get_hunt_selected(self) -> Dict:
        """Get currently selected hunt."""
        pass

    @abstractmethod
    def schedule_ui_task(self, task: Callable[[], None]) -> None:
        """Schedule task to run on UI thread."""
        pass
