import json
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


from lib.features.hunt.config_migrator import migrate_hunt_config

def load_hunt_config():
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

                data = migrate_hunt_config(data)

                # Normalize fields immediately after loading
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


def _sanitize_templates(cfg):
    """Ensure template paths are strings and relative paths where possible."""
    # This might apply to embedded templates if they still exist in the config
    # In the new architecture, templates are primarily in monster_repo, but
    # we keep this for backward compatibility or global templates.
    if "monsters" in cfg and isinstance(cfg["monsters"], list):
        for m in cfg["monsters"]:
            if isinstance(m, dict) and "templates" in m:
                for tmpl in m["templates"]:
                    if isinstance(tmpl, dict):
                        if "path" in tmpl and not isinstance(tmpl["path"], str):
                            print(
                                f"Warning: Fixing invalid template path in config: {tmpl['path']}"
                            )
                            tmpl["path"] = str(tmpl["path"]) if tmpl["path"] else ""
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
