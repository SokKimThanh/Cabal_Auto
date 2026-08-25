from typing import Any, Dict, List, Optional
from lib.features.hunt.config_validator import normalize_window_bounds_value

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
