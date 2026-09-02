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



import os
import tempfile
import threading

_CONFIG_LOCK = threading.RLock()


def save_hunt_config(cfg):
    with _CONFIG_LOCK:
        temp_path = None
        try:
            # Ensure parent directory exists
            HUNT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_path = tempfile.mkstemp(dir=HUNT_CONFIG_PATH.parent, prefix=HUNT_CONFIG_PATH.name + ".")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, HUNT_CONFIG_PATH)
            temp_path = None
            return True
        except Exception as e:
            print(f"Error saving hunt config: {e}")
            return False
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

import shutil
from lib.features.hunt.config_migrator import migrate_hunt_config

def load_hunt_config():
    with _CONFIG_LOCK:
        data = {}
        success_load = False
        if HUNT_CONFIG_PATH.exists():
            try:
                with open(HUNT_CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                success_load = True
            except json.JSONDecodeError as e:
                print(f"Error decoding hunt_config.json: {e}")
            except Exception as e:
                print(f"Error loading hunt config: {e}")

        original_version = data.get("schema_version", 1) if success_load else 0


        # Always migrate (it will skip version changes if already current, but always runs _sanitize_v3)
        data = migrate_hunt_config(data)

        new_version = data.get("schema_version")

        if original_version != new_version and original_version < 3:
            if HUNT_CONFIG_PATH.exists():
                backup_path = HUNT_CONFIG_PATH.with_suffix(".json.bak")
                shutil.copy2(HUNT_CONFIG_PATH, backup_path)

            _sanitize_templates(data)
            save_hunt_config(data)
        else:
            _sanitize_templates(data)

        return data

        # Default hunt configuration fallback omitted as migrate_hunt_config will build a valid dict


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

def update_hunt_config(mutator_func):
    """Thread-safe read-modify-write operation using a mutation callback."""
    with _CONFIG_LOCK:
        cfg = load_hunt_config()
        if mutator_func(cfg) is not False:
            return save_hunt_config(cfg)
        return False
