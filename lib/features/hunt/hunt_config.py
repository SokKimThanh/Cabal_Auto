import json
import math
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = DATA_DIR / "config.json"
HUNT_CONFIG_PATH = DATA_DIR / "hunt_config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "click": {"x": 500, "y": 400, "interval_sec": 2.0},
        "hotkeys": {"toggle": "f8", "exit": "f8"},
        "safety": {"failsafe": True, "pause_key": "f7"},
        "ui": {"topmost": False},
    }


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)


def load_hunt_config():
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Migration/Defaults for new Sprint 22 Phase 3 fields
                if "ui_mode" not in data:
                    data["ui_mode"] = "beginner"

                # Migrate old format if needed (list to dict)
                if isinstance(data.get("monsters"), list):
                    # In older versions, monsters was a list of dicts.
                    # We expect it to be a dict mapping string IDs to dicts, OR a list of string IDs.
                    # The new system relies on monster_repo, so the hunt config just needs a list of IDs for rotation.
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
                if "global_hotkeys" not in data:
                    data["global_hotkeys"] = {
                        "enabled": True,
                        "start_key": "ctrl+shift+r",
                        "stop_key": "ctrl+shift+e",
                    }
                elif "enabled" not in data["global_hotkeys"]:
                    data["global_hotkeys"]["enabled"] = True

                # Normalize fields immediately after loading
                _normalize_window_bounds(data)
                _sanitize_templates(data)

                return data
        except json.JSONDecodeError as e:
            print(f"Error decoding hunt_config.json: {e}")
        except Exception as e:
            print(f"Error loading hunt config: {e}")

    # Default hunt configuration (Sprint 21 Phase 3 structure)
    return {
        "ui_mode": "beginner",
        "hunt_area": {"window_bounds": None},
        "monster_rotation": [],  # List of monster IDs
        "skills": {},  # Dictionary mapping slot ID (e.g. "1") to skill data
        "options": {
            "auto_heal": True,
            "heal_threshold": 40,
            "auto_loot": True,
            "loot_key": "space",
        },
        "global_hotkeys": {
            "enabled": True,
            "start_key": "ctrl+shift+r",
            "stop_key": "ctrl+shift+e",
            "setup_wizard_key": "ctrl+shift+n",  # NEW
            "library_manager_key": "ctrl+shift+l",  # NEW
        },
    }


def save_hunt_config(cfg):
    try:
        with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving hunt config: {e}")
        return False


def _normalize_window_bounds_value(value):
    if not isinstance(value, dict):
        return None
    try:
        return [
            int(value["left"]),
            int(value["top"]),
            int(value["width"]),
            int(value["height"])
        ]
    except (KeyError, ValueError, TypeError):
        return None


def _normalize_template_entry(item):
    if not isinstance(item, dict):
        return None
    path = str(item.get("path", "") or "").strip()
    if not path:
        return None
    name = str(item.get("name", "") or "").strip()
    if not name:
        try:
            name = Path(path).stem
        except Exception:
            name = "template"
    try:
        threshold = float(item.get("threshold", 0.85))
    except (TypeError, ValueError):
        threshold = 0.85
    if not math.isfinite(threshold):
        threshold = 0.85
    threshold = max(0.0, min(threshold, 1.0))
    region = _normalize_window_bounds_value(item.get("region"))
    region_strategy = str(item.get("region_strategy", "") or "").strip()

    return {
        "name": name,
        "path": path,
        "threshold": threshold,
        "region": region,
        "region_strategy": region_strategy
    }


def _normalize_window_bounds(cfg):
    """Normalize window bounds into standard list format [x, y, w, h]."""
    if "hunt_area" in cfg:
        bounds = cfg["hunt_area"].get("window_bounds")
        if bounds:
            if isinstance(bounds, dict):
                try:
                    cfg["hunt_area"]["window_bounds"] = [
                        bounds["left"],
                        bounds["top"],
                        bounds["width"],
                        bounds["height"],
                    ]
                except KeyError:
                    cfg["hunt_area"]["window_bounds"] = None
            elif isinstance(bounds, list) and len(bounds) == 4:
                pass  # already normalized
            else:
                cfg["hunt_area"]["window_bounds"] = None
    return cfg


def _sanitize_templates(cfg):
    """Ensure template paths are strings and relative paths where possible."""
    # This might apply to embedded templates if they still exist in the config
    # In the new architecture, templates are primarily in monster_repo, but
    # we keep this for backward compatibility or global templates.
    if "monsters" in cfg and isinstance(cfg["monsters"], list):
        for m in cfg["monsters"]:
            if isinstance(m, dict) and "templates" in m:
                templates = []
                for tmpl in m["templates"]:
                    normalized = _normalize_template_entry(tmpl)
                    if normalized:
                        templates.append(normalized)
                m["templates"] = templates
    return cfg


class ConfigManager:
    """Wrapper to handle unified config operations across submodules."""

    def __init__(self, cfg: dict, hunt_cfg: dict):
        self.cfg = cfg
        self.hunt_cfg = hunt_cfg

    def save_all(self) -> bool:
        """Save both configs. Returns True if successful."""
        try:
            save_config(self.cfg)
            save_hunt_config(self.hunt_cfg)
            return True
        except Exception as e:
            print(f"Error saving configurations: {e}")
            return False

    def reload_all(self):
        """Reload configs from disk."""
        self.cfg.update(load_config())
        self.hunt_cfg.update(load_hunt_config())
