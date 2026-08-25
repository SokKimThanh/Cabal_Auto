from typing import Any, Dict, List, Optional

def normalize_window_bounds_value(bounds: Any) -> Optional[List[int]]:
    """Normalize window bounds into standard list format [x, y, w, h]."""
    if bounds:
        if isinstance(bounds, dict):
            try:
                return [
                    int(bounds["left"]),
                    int(bounds["top"]),
                    int(bounds["width"]),
                    int(bounds["height"]),
                ]
            except (KeyError, ValueError, TypeError):
                return None
        elif isinstance(bounds, list) and len(bounds) == 4:
            try:
                return [int(v) for v in bounds]
            except (ValueError, TypeError):
                return None
    return None

def validate_hunt_area(hunt_area: Any) -> Dict[str, Any]:
    """Validate and normalize a hunt_area dictionary.

    Returns a safe dictionary with standard defaults for missing or malformed fields.
    """
    if not isinstance(hunt_area, dict):
        return {"window_title": None, "window_bounds": None}

    safe_area: Dict[str, Any] = {
        "window_title": hunt_area.get("window_title"),
        "window_bounds": normalize_window_bounds_value(hunt_area.get("window_bounds"))
    }

    # Ensure window_title is a string or None
    if safe_area["window_title"] is not None and not isinstance(safe_area["window_title"], str):
        safe_area["window_title"] = str(safe_area["window_title"])

    return safe_area

def get_valid_hunt_area(hunt_cfg: Any) -> Dict[str, Any]:
    """Extract and validate the hunt_area from a full hunt configuration dictionary.

    Returns a safe, normalized hunt_area dictionary.
    """
    if not isinstance(hunt_cfg, dict):
        return {"window_title": None, "window_bounds": None}

    return validate_hunt_area(hunt_cfg.get("hunt_area"))
