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

def migrate_hunt_config(data: Any) -> Dict[str, Any]:
    """Migrates and normalizes the hunt config dictionary in-place."""
    if not isinstance(data, dict):
        data = {}

    if "ui_mode" not in data:
        data["ui_mode"] = "beginner"

    # Migrate old format if needed (list to dict)
    if isinstance(data.get("monsters"), list):
        old_list = data["monsters"]
        new_rotation = []
        for m in old_list:
            if isinstance(m, dict) and "id" in m:
                new_rotation.append(m["id"])
            elif isinstance(m, str):
                new_rotation.append(m)
        data["monster_rotation"] = new_rotation
        # Clear out the old embedded monsters to avoid confusion
        data["monsters"] = []

    if "monster_rotation" not in data:
        data["monster_rotation"] = []

    if "skills" not in data:
        data["skills"] = {}

    # Ensure global hotkeys exist
    if not isinstance(data.get("global_hotkeys"), dict):
        data["global_hotkeys"] = {
            "enabled": True,
            "start_key": "ctrl+shift+r",
            "stop_key": "ctrl+shift+e",
        }
    else:
        if "enabled" not in data["global_hotkeys"]:
            data["global_hotkeys"]["enabled"] = True

    # Normalize window_bounds
    hunt_area = data.get("hunt_area")
    if not isinstance(hunt_area, dict):
        data["hunt_area"] = {"window_bounds": None}
    else:
        bounds = hunt_area.get("window_bounds")
        data["hunt_area"]["window_bounds"] = normalize_window_bounds_value(bounds)

    return data
