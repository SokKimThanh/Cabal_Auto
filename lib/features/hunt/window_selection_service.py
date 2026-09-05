from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from lib.features.hunt.config_validator import normalize_window_bounds_value
from lib.system.window_manager import WindowManager


@dataclass
class WindowValidationResult:
    is_valid: bool
    code: str
    window: Optional[Dict[str, Any]] = None


def validate_selected_cabal_window(selected: Any, known_items: List[Dict[str, Any]], allowed_processes: List[str] = ["cabal.exe"]) -> WindowValidationResult:
    if not isinstance(selected, dict) or not isinstance(selected.get("hwnd"), int):
        return WindowValidationResult(False, "no_window_selected")

    hwnd = selected["hwnd"]
    wm = WindowManager()
    info = wm.get_window_info(hwnd)

    if info is None or not wm.is_window_valid(hwnd):
        return WindowValidationResult(False, "window_unavailable")

    if info.pid != selected.get("pid"):
        return WindowValidationResult(False, "window_changed")

    if info.process_name.lower() not in allowed_processes:
        return WindowValidationResult(False, "no_cabal_window")

    if not info.is_visible or not info.is_enabled or info.is_minimized or info.is_offscreen:
        return WindowValidationResult(False, "window_unavailable")

    # Valid known items check (make sure it's in the currently scanned list if known_items is provided)
    if known_items:
        if hwnd not in {item["hwnd"] for item in known_items}:
            return WindowValidationResult(False, "window_changed")

    # Need to output dict format matching UI's expected 'hunt_selected' format
    win_dict = {
        "hwnd": int(info.hwnd),
        "pid": int(info.pid),
        "title": (info.title or "").strip(),
        "proc": info.process_name,
        "bounds": normalize_window_bounds_value(info.rect),
        "is_minimized": info.is_minimized
    }
    return WindowValidationResult(True, "ok", win_dict)


class WindowRecoveryController:
    """Shared retry logic for window recovery (UX1 + UX5.2)."""

    _instance = None  # Singleton

    def __init__(self):
        self._retry_in_progress = False
        self._retry_step = 0
        self._retry_max = 3
        self._hwnd = None
        self._on_progress = None
        self._on_failure = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_async_recovery(self, hwnd: int, on_progress=None, on_failure=None):
        """Start 3-step recovery (500ms spacing via self.after)."""
        if self._retry_in_progress:
            return  # Lock: already retrying

        self._retry_in_progress = True
        self._retry_step = 0
        self._hwnd = hwnd
        self._on_progress = on_progress
        self._on_failure = on_failure

        self._execute_retry_step()

    def _execute_retry_step(self):
        """Execute one retry step."""
        self._retry_step += 1

        if self._on_progress:
            self._on_progress(self._retry_step)

        # Attempt restore
        wm = WindowManager()
        success = wm.restore(self._hwnd) and wm.set_foreground(self._hwnd)

        if success or self._retry_step >= self._retry_max:
            self._retry_in_progress = False
            if not success and self._on_failure:
                self._on_failure()
            return

        # Next step logic should be implemented by caller since this runs asynchronously


class WindowSelectionService:
    """Service for target window and bounds validation logic used by hunt setup/runtime."""

    @staticmethod
    def resolve_bounds(config: Any, current_bounds: Optional[List[int]] = None) -> Optional[List[int]]:
        """Resolve the active window bounds from the config or current bounds.

        Checks current_bounds first, then hunt_area.window_bounds, then root window_bounds.
        Normalizes and returns the first valid bounds found.
        """
        # 1. Prefer current active bounds if valid
        bounds = normalize_window_bounds_value(current_bounds)
        if bounds is not None:
            return bounds

        if not isinstance(config, dict):
            return None

        # 2. Check hunt_area.window_bounds
        hunt_area = config.get("hunt_area")
        if isinstance(hunt_area, dict):
            bounds = normalize_window_bounds_value(hunt_area.get("window_bounds"))
            if bounds is not None:
                return bounds

        # 3. Check legacy root window_bounds
        return normalize_window_bounds_value(config.get("window_bounds"))

    @staticmethod
    def update_bounds(config: Any, bounds: Any) -> Optional[List[int]]:
        """Normalize the bounds and safely update both root and hunt_area locations in the config.

        Returns the normalized bounds if successful, or None if malformed.
        """
        if not isinstance(config, dict):
            return None

        normalized = normalize_window_bounds_value(bounds)

        # Always update root config for compatibility
        config["window_bounds"] = normalized

        # Ensure hunt_area exists and update it
        hunt_area = config.get("hunt_area")
        if not isinstance(hunt_area, dict):
            hunt_area = {}
            config["hunt_area"] = hunt_area

        hunt_area["window_bounds"] = normalized
        return normalized
