import ctypes
import json
import math
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, List
import copy

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import pyautogui  # type: ignore
except Exception:
    pyautogui = None  # type: ignore

try:
    from PIL import Image, ImageTk, ImageDraw  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    ImageDraw = None  # type: ignore

try:
    import keyboard  # type: ignore
except Exception:
    keyboard = None  # type: ignore

from ctypes import wintypes

from lib.vision.template_matcher import locate_template
from lib.vision.vision_engine import VisionEngine
from lib.system.screen_capture import ScreenCapture
from lib.system.bot_manager import BotManager
from ui.utils.overlay_controller import OverlayController
from lib.i18n.translations import GLOBAL_TRANSLATIONS
from ui.helpers.tooltip import attach_i18n_tooltip
from lib.i18n import (
    register_bulk as i18n_register_bulk,
    t as i18n_t,
    set_default_lang as i18n_set_lang,
    GLOBAL_NS as I18N_GLOBAL,
)

# Import icon button component
try:
    from ui.components import create_icon_button as _create_icon_btn_component
    from ui.components.window_position_selector import create_app_window_selector, create_game_window_selector
    _HAS_ICON_COMPONENT = True
except ImportError:
    _HAS_ICON_COMPONENT = False
    _create_icon_btn_component = None  # type: ignore
    create_app_window_selector = None  # type: ignore
    create_game_window_selector = None  # type: ignore
    print("Warning: Icon button component not available, using fallback")

try:
    from ui.helpers.capture_helper import capture_region_and_save
except Exception:
    capture_region_and_save = None  # type: ignore

from lib.system.win_input import tap
from lib.system.hunt_logger import get_hunt_logger
from lib.features.timing.calculator import (
    calculate_timing,
    format_timing_recommendation,
    get_timing_presets,
)
from lib.features.skills.skill_stats import (
    SkillStats,
)  # Sprint 22 Patch 1: Training Mode
from lib.ui_style import UIStyle as UI  # Global UI style constants


# =====================================================================
# Single Instance Lock (Prevent multiple app instances)
# =====================================================================
class SingleInstanceLock:
    """Cross-platform single instance lock.

    Ensures only one instance of the application can run at a time.
    Uses Windows mutex on Windows, fcntl file lock on Unix-like systems.
    """

    def __init__(self, app_name: str = "CabalAutoHunt"):
        """Initialize single instance lock.

        Args:
            app_name: Unique application name for mutex/lock identification
        """
        self.app_name = app_name
        self.mutex = None
        self.lock_file = None
        self.is_locked = False

        # For Unix: lock file in tmp directory
        if sys.platform != "win32":
            lock_dir = Path(__file__).parent / "tmp"
            lock_dir.mkdir(parents=True, exist_ok=True)
            self.lock_file_path = lock_dir / f"{app_name}.lock"

    def acquire(self) -> bool:
        """Acquire the lock. Returns True if successful, False if another instance is running.

        Returns:
            bool: True if lock acquired successfully, False if another instance holds the lock.
        """
        try:
            if sys.platform == "win32":
                # Windows: Use named mutex (more reliable than file locking)
                import ctypes
                from ctypes import wintypes

                # Create mutex name (Global for all users, Local for current user)
                mutex_name = f"Global\\{self.app_name}_SingleInstance"

                # Try to create mutex
                kernel32 = ctypes.windll.kernel32
                self.mutex = kernel32.CreateMutexW(None, False, mutex_name)

                # Check if mutex already exists (ERROR_ALREADY_EXISTS = 183)
                last_error = kernel32.GetLastError()
                if last_error == 183:  # ERROR_ALREADY_EXISTS
                    return False

                self.is_locked = True
                return True
            else:
                # Unix: Use fcntl file lock
                import fcntl

                try:
                    self.lock_file = open(self.lock_file_path, "w")
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.is_locked = True
                    # Write PID for debugging
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return True
                except (OSError, IOError):
                    if self.lock_file:
                        self.lock_file.close()
                    return False
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False

    def release(self):
        """Release the lock and clean up."""
        try:
            if sys.platform == "win32":
                # Windows: Close mutex handle
                if self.mutex and self.is_locked:
                    import ctypes

                    kernel32 = ctypes.windll.kernel32
                    kernel32.CloseHandle(self.mutex)
                    self.is_locked = False
            else:
                # Unix: Unlock and close file
                if self.lock_file and self.is_locked:
                    import fcntl

                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    self.lock_file.close()
                    self.is_locked = False

                    # Remove lock file
                    if self.lock_file_path.exists():
                        self.lock_file_path.unlink()
        except Exception as e:
            print(f"Error releasing lock: {e}")

    def __del__(self):
        """Cleanup on object destruction."""
        self.release()


# Register centralized translations at startup
try:
    i18n_register_bulk(I18N_GLOBAL, GLOBAL_TRANSLATIONS)
except Exception:
    pass

# Optional setup wizard import
try:
    from ui.windows.setup_wizard import show_setup_wizard  # type: ignore
except Exception:
    show_setup_wizard = None  # type: ignore

# Local ToolTip class removed; using centralized attach_i18n_tooltip from lib.tooltip

# All data files centralized in lib/data/ for consistency
_LIB_DATA_DIR = Path(__file__).parent / "lib" / "data"
CONFIG_PATH = _LIB_DATA_DIR / "config.json"
HUNT_CONFIG_PATH = _LIB_DATA_DIR / "hunt_config.json"
MONSTER_DB_PATH = _LIB_DATA_DIR / "monsters.json"
SKILL_DB_PATH = _LIB_DATA_DIR / "skills.json"


def _normalize_window_bounds(value):
    keys = ("left", "top", "width", "height")
    if isinstance(value, dict):
        try:
            normalized = {k: int(value.get(k, 0)) for k in keys}
        except (TypeError, ValueError):
            return None
        if normalized["width"] <= 0 or normalized["height"] <= 0:
            return None
        return normalized
    if isinstance(value, (list, tuple)) and len(value) == 4:
        try:
            left, top, width, height = [int(v) for v in value]
        except (TypeError, ValueError):
            return None
        if width <= 0 or height <= 0:
            return None
        return {"left": left, "top": top, "width": width, "height": height}
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
    region = _normalize_window_bounds(item.get("region"))
    region_strategy = str(item.get("region_strategy", "") or "").strip()
    grayscale = item.get("grayscale")
    tmpl = {
        "name": name,
        "path": path,
        "threshold": threshold,
        "region": region,
    }
    if region_strategy:
        tmpl["region_strategy"] = region_strategy
    if grayscale is not None:
        tmpl["grayscale"] = bool(grayscale)
    return tmpl


def _sanitize_templates(value):
    templates = []
    if isinstance(value, list):
        for entry in value:
            normalized = _normalize_template_entry(entry)
            if normalized:
                templates.append(normalized)
    return templates


def load_monster_library():
    if not MONSTER_DB_PATH.exists():
        return []
    try:
        with open(MONSTER_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        monsters = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                if not name:
                    continue
                try:
                    hp = float(item.get("hp", 0))
                    dmg = float(item.get("damage_per_hit", 0))
                except (TypeError, ValueError):
                    continue
                if hp <= 0 or dmg <= 0:
                    continue
                template = str(item.get("template", "") or "").strip()
                description = str(item.get("description", "") or "").strip()
                training_mode = bool(item.get("training_mode", False))
                window_bounds = _normalize_window_bounds(item.get("window_bounds"))
                templates = _sanitize_templates(item.get("templates"))
                monsters.append(
                    {
                        "name": name,
                        "hp": hp,
                        "damage_per_hit": dmg,
                        "template": template,
                        "description": description,
                        "training_mode": training_mode,
                        "window_bounds": window_bounds,
                        "templates": templates,
                    }
                )
        return monsters
    except Exception:
        return []


def save_monster_library(monsters):
    safe = []
    for item in monsters:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        try:
            hp = float(item.get("hp", 0))
            dmg = float(item.get("damage_per_hit", 0))
        except (TypeError, ValueError):
            continue
        template = str(item.get("template", "") or "").strip()
        description = str(item.get("description", "") or "").strip()
        training_mode = bool(item.get("training_mode", False))
        window_bounds = _normalize_window_bounds(item.get("window_bounds"))
        templates = _sanitize_templates(item.get("templates"))
        safe.append(
            {
                "name": name,
                "hp": hp,
                "damage_per_hit": dmg,
                "template": template,
                "description": description,
                "training_mode": training_mode,
                "window_bounds": window_bounds,
                "templates": templates,
            }
        )
    with open(MONSTER_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def load_skill_library():
    if not SKILL_DB_PATH.exists():
        return []
    try:
        with open(SKILL_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                key = str(item.get("key", "")).strip().upper()
                if not name or not key:
                    continue
                skill_type = str(item.get("type", "attack")).strip().lower()
                if skill_type not in ("attack", "buff"):
                    skill_type = "attack"
                try:
                    cooldown = float(item.get("cooldown", 0.0))
                    cast_time = float(item.get("cast_time", 0.0))
                except (TypeError, ValueError):
                    cooldown = 0.0
                    cast_time = 0.0
                image = str(item.get("image", "") or "").strip()
                skills.append(
                    {
                        "name": name,
                        "key": key,
                        "type": skill_type,
                        "cooldown": max(cooldown, 0.0),
                        "cast_time": max(cast_time, 0.0),
                        "image": image,
                    }
                )
        return skills
    except Exception:
        return []


def save_skill_library(skills):
    safe = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        key = str(item.get("key", "")).strip().upper()
        if not name or not key:
            continue
        skill_type = str(item.get("type", "attack")).strip().lower()
        if skill_type not in ("attack", "buff"):
            skill_type = "attack"
        try:
            cooldown = float(item.get("cooldown", 0.0))
            cast_time = float(item.get("cast_time", 0.0))
        except (TypeError, ValueError):
            continue
        image = str(item.get("image", "") or "").strip()
        safe.append(
            {
                "name": name,
                "key": key,
                "type": skill_type,
                "cooldown": max(cooldown, 0.0),
                "cast_time": max(cast_time, 0.0),
                "image": image,
            }
        )
    with open(SKILL_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def calculate_attack_speed_from_skills(skill_names):
    """
    Calculate effective attack speed from selected skills.

    Args:
        skill_names: List of skill names to use for hunting

    Returns:
        tuple: (attacks_per_second, average_cooldown, skill_count)
        Returns (None, None, 0) if no valid skills

    Example:
        skills = ["Dark Explosion", "Fire Ball"]
        aps, avg_cd, count = calculate_attack_speed_from_skills(skills)
        # aps = 0.67 (if avg cooldown is 1.5s)
    """
    if not skill_names:
        return (None, None, 0)

    skills_data = load_skill_library()
    if not skills_data:
        return (None, None, 0)

    # Build skill lookup dict
    skill_dict = {s["name"]: s for s in skills_data}

    # Collect cooldowns for selected skills
    total_cooldown = 0.0
    valid_count = 0

    for skill_name in skill_names:
        if skill_name in skill_dict:
            skill = skill_dict[skill_name]
            # Only count attack skills for attack speed calculation
            if skill.get("type", "attack").lower() == "attack":
                cooldown = float(skill.get("cooldown", 1.0))
                if cooldown > 0:
                    total_cooldown += cooldown
                    valid_count += 1

    if valid_count == 0:
        return (None, None, 0)

    avg_cooldown = total_cooldown / valid_count
    attacks_per_second = 1.0 / avg_cooldown if avg_cooldown > 0 else 1.0

    return (attacks_per_second, avg_cooldown, valid_count)


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
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_hunt_config():
    # Default hunt config if file missing
    default = {
        "window_title": "Cabal",
        "target_key": "Z",  # Changed from TAB to Z (more common for target cycling)
        "attack_press_ms": 60,
        "target_cycle_delay": 0.2,
        "search_interval": 0.25,
        "attack_interval": 0.15,
        "template_path": "assets/images/target_frame.png",
        "region": None,
        "confidence": 0.85,
        "grayscale": True,
        "lost_timeout_sec": 1.2,
        "attack_min_duration_sec": 1.5,
        "bring_to_front_each_cycle": False,
        "skill_slots": [],
        "window_bounds": None,
        # Phase 3: Multi-Monster Support
        "monster_list": [],  # [{"name": "Coc Go 2", "priority": 1}, ...]
        "rotation_mode": "sequence",  # "sequence" or "priority"
        "current_monster_index": 0,  # For sequence rotation
    }
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            default.update(data)
        except Exception:
            pass
    default.setdefault("skill_slots", [])

    # Backward compatibility: if legacy 'attack_keys' present and no skill_slots configured,
    # migrate them into skill_slots (attack keys become anonymous attack slots).
    try:
        if default.get("attack_keys") and not default.get("skill_slots"):
            atk = default.get("attack_keys") or []
            # Limit to skill_slot_count (6) to avoid oversized configs
            max_slots = 6
            slots = []
            for i, k in enumerate(atk[:max_slots]):
                slots.append(
                    {
                        "name": "",
                        "key": str(k).upper(),
                        "type": "attack",
                        "cooldown": 0.0,
                        "cast_time": 0.0,
                        "image": "",
                    }
                )
            default["skill_slots"] = slots
            # Remove legacy key to avoid re-migration
            try:
                del default["attack_keys"]
            except Exception:
                pass
            # Write back the migrated config
            try:
                with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(default, f, ensure_ascii=False, indent=2)
                print(
                    "[Migration] ✅ Migrated legacy attack_keys into skill_slots and saved hunt_config.json"
                )
            except Exception:
                print(
                    "[Migration] ⚠️ Failed to save migrated hunt_config.json; continuing with in-memory migration"
                )
    except Exception:
        # Non-fatal migration failure
        pass

    # Backward compatibility: migrate monster_selected_name → monster_list
    if "monster_selected_name" in default and default["monster_selected_name"]:
        if not default.get("monster_list"):
            default["monster_list"] = [
                {"name": default["monster_selected_name"], "priority": 1}
            ]

    # Ensure monster_list exists
    default.setdefault("monster_list", [])
    default.setdefault("rotation_mode", "sequence")
    default.setdefault("current_monster_index", 0)

    # Ensure global_hotkeys section exists
    default.setdefault(
        "global_hotkeys",
        {"enabled": True, "start_key": "ctrl+shift+r", "stop_key": "ctrl+shift+e"},
    )

    return default


def save_hunt_config(cfg):
    with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class ConfigManager:
    """Wrapper class for config management to interface with SetupWizard."""

    def __init__(self, cfg, hunt_cfg):
        self.cfg = cfg
        self.hunt_cfg = hunt_cfg

    def set(self, section, key, value):
        """Set a configuration value."""
        if section == "hunt_config":
            self.hunt_cfg[key] = value
        elif section == "config":
            self.cfg[key] = value
        else:
            # Handle other sections if needed
            if section not in self.cfg:
                self.cfg[section] = {}
            self.cfg[section][key] = value

    def get(self, section, key, default=None):
        """Get a configuration value."""
        if section == "hunt_config":
            return self.hunt_cfg.get(key, default)
        elif section == "config":
            return self.cfg.get(key, default)
        else:
            return self.cfg.get(section, {}).get(key, default)

    def save(self):
        """Save both config files."""
        save_config(self.cfg)
        save_hunt_config(self.hunt_cfg)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load config and language
        self.cfg = load_config()
        self.hunt_cfg = load_hunt_config()
        self.lang = str(self.cfg.get("ui", {}).get("language", "vi"))
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass

        # Centralized icon helper
        try:
            from ui.helpers.icon_helper import get_icon_helper

            self.icon_helper = get_icon_helper()
        except Exception:
            self.icon_helper = None

        # Create config manager for wizard
        self.config_mgr = ConfigManager(self.cfg, self.hunt_cfg)

        self.title(self._t("app_title"))
        self.resizable(False, False)

        # --- Menu: Settings (includes Global Hotkeys toggle & retry) ---
        try:
            menubar = tk.Menu(self)
            settings_menu = tk.Menu(menubar, tearoff=0)
            # BooleanVar reflects hunt_cfg setting
            gh_cfg = self.hunt_cfg.get("global_hotkeys", {})
            self._global_hotkeys_var = tk.BooleanVar(
                value=bool(gh_cfg.get("enabled", True))
            )

            def _on_toggle_global_hotkeys():
                enabled = bool(self._global_hotkeys_var.get())
                # Persist setting
                self.hunt_cfg.setdefault("global_hotkeys", {})["enabled"] = enabled
                try:
                    save_hunt_config(self.hunt_cfg)
                except Exception:
                    pass
                # Apply immediately
                if enabled:
                    print("[Hotkeys] User enabled global hotkeys via menu")
                    try:
                        self._register_global_hotkeys()
                    except Exception as e:
                        print(f"[Hotkeys] Error re-registering hotkeys: {e}")
                else:
                    print("[Hotkeys] User disabled global hotkeys via menu")
                    try:
                        self._unregister_global_hotkeys()
                    except Exception as e:
                        print(f"[Hotkeys] Error unregistering hotkeys: {e}")

            settings_menu.add_checkbutton(
                label=self._t("help_shortcuts"),
                variable=self._global_hotkeys_var,
                command=_on_toggle_global_hotkeys,
            )
            settings_menu.add_separator()

            def _retry_hotkeys():
                print("[Hotkeys] User requested retry registration")
                try:
                    self._register_global_hotkeys()
                except Exception as e:
                    print(f"[Hotkeys] Retry failed: {e}")

            settings_menu.add_command(
                label="Retry global hotkeys", command=_retry_hotkeys
            )
            menubar.add_cascade(label="Settings", menu=settings_menu)
            
            # --- Menu: Vision (Sprint 22 Phase 1B) ---
            vision_menu = tk.Menu(menubar, tearoff=0)
            
            # Open Vision Wizard (Ctrl+Shift+V)
            vision_label = "Open Vision Wizard" if self.lang == "en" else "Mở Trợ lý Vision"
            vision_menu.add_command(
                label=vision_label,
                accelerator="Ctrl+Shift+V",
                command=self._open_vision_wizard
            )
            
            vision_menu.add_separator()
            
            # Scan Region (Ctrl+Alt+S)
            scan_label = "Scan Region" if self.lang == "en" else "Quét Vùng"
            vision_menu.add_command(
                label=scan_label,
                accelerator="Ctrl+Alt+S",
                command=self._scan_region
            )
            
            # Add Template (Ctrl+T)
            add_tmpl_label = "Add Template" if self.lang == "en" else "Thêm Template"
            vision_menu.add_command(
                label=add_tmpl_label,
                accelerator="Ctrl+T",
                command=self._add_template
            )
            
            # Manage Templates (Ctrl+Shift+T)
            manage_tmpl_label = "Manage Templates" if self.lang == "en" else "Quản lý Templates"
            vision_menu.add_command(
                label=manage_tmpl_label,
                accelerator="Ctrl+Shift+T",
                command=self._manage_templates
            )
            
            vision_menu.add_separator()
            
            # Toggle Overlay (Ctrl+Shift+O) - using translations
            vision_menu.add_command(
                label=self._t("vision_toggle_overlay"),
                accelerator="Ctrl+Shift+O",
                command=self._toggle_overlay
            )
            
            # Overlay Settings - using translations
            overlay_settings_label = "Overlay Settings..." if self.lang == "en" else "Cài Đặt Overlay..."
            vision_menu.add_command(
                label=overlay_settings_label,
                command=self._open_overlay_settings
            )
            
            menubar.add_cascade(label="Vision", menu=vision_menu)
            print("[Vision Menu] Created successfully")
            
            # --- Menu: Monster Editor (Monster CRUD) ---
            monster_menu = tk.Menu(menubar, tearoff=0)
            
            # Open Monster Editor (Ctrl+Shift+M)
            try:
                from lib.i18n import t as i18n_t
                monster_label = i18n_t('menu_open_monster_editor', ns='monster_editor', 
                                      default='Open Monster Manager' if self.lang == 'en' else 'Mở Quản Lý Quái Vật')
            except:
                monster_label = "Open Monster Manager" if self.lang == "en" else "Mở Quản Lý Quái Vật"
            
            monster_menu.add_command(
                label=monster_label,
                accelerator="Ctrl+Shift+M",
                command=self._open_monster_editor
            )
            
            menubar.add_cascade(label="Monster", menu=monster_menu)
            print("[Monster Menu] Created successfully")
            
            try:
                self.config(menu=menubar)
            except Exception:
                # Some environments may not support menu on top-level; ignore
                pass
        except Exception as e:
            print(f"[Menu] Error creating menubar: {e}")

        # Check PIL availability (for image preview features)
        self.pil_available = (
            Image is not None and ImageTk is not None and ImageDraw is not None
        )

        # State
        self.click_running = False
        self.click_thread = None
        self.hunt_running = False
        self.hunt_thread = None
        self.win_items = []  # list of {'hwnd','pid','title','proc'}
        self.hunt_selected = None  # currently selected window info
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front

        # Global hotkeys - registered after config load
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._global_wizard_hotkey = None  # NEW: Setup Wizard (Ctrl+Shift+N)
        self._global_library_hotkey = None  # NEW: Library Manager (Ctrl+Shift+L)
        self._global_vision_hotkey = None  # NEW Sprint 22: Vision Wizard (Ctrl+Shift+V)
        self._global_monster_hotkey = None  # NEW: Monster Editor (Ctrl+Shift+M)
        # Fallback when `keyboard` package not available in this interpreter
        self._hotkey_fallback_bound = (
            []
        )  # list of tkinter sequence strings bound via bind_all
        self._hotkey_import_diag = ""
        
        # Phase 5: Overlay window for vision detection
        self._overlay_window: Optional[Any] = None  # OverlayWindow instance
        self._overlay_enabled = False
        self._overlay_update_thread: Optional[threading.Thread] = None
        self._overlay_stop_event = threading.Event()
        
        # Phase 7: Monster tracking integration
        self._vision_engine: Optional[VisionEngine] = None
        self._screen_capture: Optional[ScreenCapture] = None
        self._bot_manager: Optional[BotManager] = None
        self._overlay_controller: Optional[OverlayController] = None

        self.monsters = load_monster_library()
        self.monster_selected_index = None
        self.monster_selected_name = self.monsters[0]["name"] if self.monsters else None

        # Phase 3: Multi-Monster Support
        self.monster_rotation_list = (
            []
        )  # [{"name": "Coc Go 2", "priority": 1, "enabled": True}, ...]
        self._load_monster_rotation_list()

        # Sprint 22 Patch 2: Separate training dummy list
        self.training_monster_list = (
            []
        )  # [{"name": "Coc go~", "priority": 1, "enabled": True, "training_mode": True}]
        self._config_migrated = False  # Track if migration happened
        self._load_training_monster_list()

        # Sprint 22 Patch 2: Auto-save if "Coc go" was migrated from monster_list to training_monster_list
        if self._config_migrated:
            # Update hunt_cfg with both lists before saving
            self.hunt_cfg["monster_list"] = self.monster_rotation_list
            self.hunt_cfg["training_monster_list"] = self.training_monster_list
            save_hunt_config(self.hunt_cfg)
            self._config_migrated = False
            print(
                "[Migration] ✅ Auto-migrated 'Coc go' variants to training_monster_list and saved config."
            )

        self.skills = load_skill_library()
        # If migration created anonymous skill_slots (blank names) from legacy attack_keys,
        # try to map them to actual attack skills from the skill library for a better UX.
        try:
            slots = self.hunt_cfg.get("skill_slots", [])
            # find anonymous slots (name is empty but key present)
            anon_indices = [
                i
                for i, s in enumerate(slots)
                if isinstance(s, dict) and not s.get("name") and s.get("key")
            ]
            if anon_indices:
                # Inform the user that a legacy migration occurred (attack_keys -> skill_slots)
                try:
                    # Show a gentle migration notice (one-time modal)
                    messagebox.showinfo(
                        self._t("migration_legacy_attack_keys_title"),
                        self._t("migration_legacy_attack_keys_message"),
                    )
                except Exception:
                    pass

            if anon_indices and self.skills:
                # collect candidate attack skill names that are not already assigned
                assigned = {
                    s.get("name")
                    for s in slots
                    if isinstance(s, dict) and s.get("name")
                }
                attack_names = [
                    sk["name"]
                    for sk in self.skills
                    if sk.get("type", "attack") == "attack"
                    and sk.get("name")
                    and sk.get("name") not in assigned
                ]
                changed = False
                for idx in anon_indices:
                    if not attack_names:
                        break
                    name = attack_names.pop(0)
                    slots[idx]["name"] = name
                    changed = True
                if changed:
                    # persist mapping
                    self.hunt_cfg["skill_slots"] = slots
                    try:
                        save_hunt_config(self.hunt_cfg)
                        try:
                            # show auto-mapped details if available
                            mapped = ", ".join(
                                [
                                    slots[i].get("name", "")
                                    for i in anon_indices
                                    if slots[i].get("name")
                                ]
                            )
                            info_msg = self._t(
                                "migration_legacy_attack_keys_auto_mapped"
                            ).format(mapped=mapped)
                            messagebox.showinfo(self._t("skill_section"), info_msg)
                        except Exception:
                            pass
                        # also set a short hunt status message
                        self.hunt_status.set(self._t("migration_mapped_slots_short"))
                    except Exception:
                        # non-fatal
                        pass
        except Exception:
            pass
        self.skill_selected_index = None
        self.skill_selected_name = self.skills[0]["name"] if self.skills else None
        self.skill_preview_image = None
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self.skill_slot_saved_names = [
            slot.get("name", "")
            for slot in self.hunt_cfg.get("skill_slots", [])
            if isinstance(slot, dict) and slot.get("name")
        ]
        self.monster_manager_win = None
        self.skill_manager_win = None
        self.monster_listbox = None
        # Declare monster quick-select attributes for type-checker and runtime
        self.monster_select_var = tk.StringVar()
        self.monster_select_combo = None  # type: Optional[ttk.Combobox]
        self.monster_name_var = tk.StringVar()
        self.monster_hp_var = tk.StringVar()
        self.monster_damage_var = tk.StringVar()
        self.monster_template_var = tk.StringVar()
        self.monster_estimate_var = tk.StringVar(value="")
        self.skill_listbox = None
        self.skill_name_var = tk.StringVar()
        self.skill_key_var = tk.StringVar()
        self.skill_type_var = tk.StringVar(value=self._t("skill_type_attack"))
        self.skill_cooldown_var = tk.StringVar()
        self.skill_cast_time_var = tk.StringVar()
        self.skill_duration_var = tk.StringVar()
        # Keep references to images (PhotoImage) to prevent GC. Tkinter will
        # garbage-collect PhotoImage objects unless a Python reference is held.
        # We store images here rather than attaching arbitrary attributes to
        # widgets to reduce static-analysis false-positives and centralize
        # resource ownership. Some files still use dynamic attribute access
        # (e.g., `root._image_refs`) for backward compatibility; those uses
        # are annotated with `# type: ignore[attr-defined]` where needed.
        self._image_refs = []  # type: List[Any]
        # Central tooltip store to avoid attaching dynamic attributes to widgets
        self._tooltips = {}
        self.skill_pre_refresh_var = tk.StringVar()
        self.skill_image_var = tk.StringVar()
        self.skill_preview_label = None
        self._skill_image_trace = None
        self.monster_description_text = None
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self.monster_template_listbox = None
        self.monster_template_name_var = tk.StringVar()
        self.monster_template_path_var = tk.StringVar()
        self.monster_template_threshold_var = tk.StringVar(value="0.85")
        self.monster_template_region_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }
        self.monster_template_preview_label = None
        self.monster_template_preview_image = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}  # path -> PhotoImage cache
        self.monster_bounds_vars = {
            "left": tk.StringVar(),
            "top": tk.StringVar(),
            "width": tk.StringVar(),
            "height": tk.StringVar(),
        }
        self.current_window_bounds = _normalize_window_bounds(
            self.hunt_cfg.get("window_bounds")
        )
        self.hunt_cfg["window_bounds"] = self.current_window_bounds
        self.window_bounds_display_var = tk.StringVar(value="")

        # Hunt tab widget groups for progressive disclosure
        self.hunt_intermediate_widgets = []  # Shown in intermediate+ modes
        self.hunt_advanced_widgets = []  # Shown only in advanced mode

        if pyautogui is not None:
            pyautogui.FAILSAFE = bool(self.cfg.get("safety", {}).get("failsafe", True))

        self._build_ui()

        # Keyboard shortcuts (Window-focused only)
        self.bind(
            "<Control-k>", lambda e: self._open_skill_manager()
        )  # Ctrl+K: Manage skills
        self.bind("<Alt-Key-1>", lambda e: self._switch_to_tab(0))  # Alt+1: Hunt tab
        self.bind("<Alt-Key-2>", lambda e: self._switch_to_tab(1))  # Alt+2: Setup tab

        # Register global hotkeys (Ctrl+Shift+R/E/L/N) using keyboard module
        self._registered_hotkey_handlers = (
            {}
        )  # key -> handler (as returned by keyboard.add_hotkey)
        self._failed_hotkeys = {}  # key -> exception
        self._hotkeys_registered_ok = False
        if keyboard is not None:
            hotkey_map = {
                "ctrl+shift+r": getattr(self, "on_hunt_start", None),
                "ctrl+shift+e": getattr(self, "on_hunt_stop", None),
                # Map to wrapper handlers (which perform mode checks / scheduling)
                "ctrl+shift+l": getattr(self, "_on_library_manager_hotkey", None),
                "ctrl+shift+n": getattr(self, "_on_setup_wizard_hotkey", None),
                # Vision menu hotkeys (Sprint 22 Phase 1B)
                "ctrl+shift+v": getattr(self, "_open_vision_wizard", None),
                "ctrl+alt+s": getattr(self, "_scan_region", None),
                "ctrl+t": getattr(self, "_add_template", None),
                "ctrl+shift+t": getattr(self, "_manage_templates", None),
                "ctrl+shift+o": getattr(self, "_toggle_overlay", None),
            }
            for hk, callback in hotkey_map.items():
                if callback is None:
                    # No callback available; skip registration but record as skipped
                    self._failed_hotkeys[hk] = "missing-callback"
                    print(f"[Hotkey] Skipping {hk} - no callback available")
                    continue
                try:
                    handler = keyboard.add_hotkey(hk, callback)
                    # handler may be a function to remove or an id; store as-is
                    self._registered_hotkey_handlers[hk] = handler
                    print(f"[Hotkey] Registered {hk} -> {callback.__name__}")
                except Exception as ex:
                    self._failed_hotkeys[hk] = repr(ex)
                    print(f"[Hotkey] Failed to register {hk}: {ex}")
            # Determine overall success
            self._hotkeys_registered_ok = len(self._failed_hotkeys) == 0
            if not self._hotkeys_registered_ok:
                print("[Hotkey] Some hotkeys failed to register:", self._failed_hotkeys)

        # Update hotkeys UI state based on current mode
        self.after(100, self._update_hotkeys_state)
        
        # Update hotkey status UI after registration
        self.after(150, self._update_hotkey_diagnostics_ui)

        # Auto-launch Setup Wizard for new users (after UI is ready)
        self.after(500, self._check_first_time_setup)

        # Auto bring-to-front saved window (after setup check)
        self.after(1000, self._auto_bring_to_front_on_startup)

    def destroy(self):
        # Phase 7: Cleanup monster tracking components
        try:
            if self._overlay_controller is not None:
                self._overlay_controller.stop()
                self._overlay_controller = None
                print("[MonsterTracking] OverlayController cleaned up")
            
            if self._bot_manager is not None:
                self._bot_manager.destroy()
                self._bot_manager = None
                print("[MonsterTracking] BotManager cleaned up")
        except Exception as e:
            print(f"[MonsterTracking] Error during cleanup: {e}")
        
        # Unregister global hotkeys on exit
        if keyboard is not None and hasattr(self, "_registered_hotkey_handlers"):
            for hk, handler in list(self._registered_hotkey_handlers.items()):
                try:
                    # keyboard.remove_hotkey accepts either the hotkey string or the handler id/function
                    keyboard.remove_hotkey(handler)
                except Exception:
                    try:
                        keyboard.remove_hotkey(hk)
                    except Exception:
                        pass
        super().destroy()

    def _icon(
        self, name: str, fallback: str, size: int = 16, color: Optional[str] = None
    ):
        """Fetch an icon image from icon_helper with caching.

        Returns a PhotoImage (when available) or fallback string (emoji) otherwise.
        Keep a reference on self to avoid Tk image garbage collection.

        Args:
            name: Icon name (e.g., 'add', 'locked')
            fallback: Emoji fallback if icon not found
            size: Icon size in pixels
            color: Hex color to tint icon (e.g., '#FFFFFF' for white on gray background)
        """
        try:
            if not hasattr(self, "_icon_cache"):
                self._icon_cache = {}
            key = f"{name}_{size}_{color or 'default'}"
            if key in self._icon_cache:
                return self._icon_cache[key]
            helper = getattr(self, "icon_helper", None)
            if helper is not None:
                try:
                    img = helper.get_icon(
                        name, fallback=fallback, size=size, color=color
                    )
                except Exception:
                    img = fallback
            else:
                img = fallback
            self._icon_cache[key] = img
            return img
        except Exception:
            return fallback

    # -----------------
    # Helper Methods
    # -----------------
    def _create_icon_button(
        self,
        parent,
        icon_emoji,
        command,
        style="compact",
        bg_color=None,
        hover_color=None,
        **kwargs,
    ):
        """Create a standardized icon button following UIStyle guidelines.
        
        **DEPRECATED**: This method now uses the new icon_button component internally.
        For new code, prefer using `from ui.components import create_icon_button` directly.

        Args:
            parent: Parent widget
            icon_emoji: Emoji text for button (e.g., '➕', '↑', '↓') - used as fallback
            command: Button command callback
            style: Size style - 'compact', 'small', 'medium', or 'large'
            bg_color: Background color (uses BTN_ACCENT_BG if not specified)
            hover_color: Hover color (uses BTN_ACCENT_HOVER if not specified)
            **kwargs: Additional button configuration options

        Returns:
            tk.Button: Configured button widget
        """
        # If component available, use it for better icon quality
        if _HAS_ICON_COMPONENT and _create_icon_btn_component is not None:
            # Map emoji to icon names
            emoji_to_icon = {
                '➕': 'add',
                '🗑️': 'delete', 
                '💾': 'save',
                '✖': 'cancel',
                '🔄': 'refresh',
                '↑': 'up',
                '↓': 'down',
                '📁': 'folder',
                '⚙️': 'settings',
                '🔍': 'search',
            }
            
            # Map bg_color to button_type
            button_type_map = {
                UI.BTN_PRIMARY_BG: 'green_light',
                UI.BTN_ACCENT_BG: 'green_light', 
                UI.BTN_DANGER_BG: 'red',
                UI.BTN_INFO_BG: 'blue',
                UI.BTN_NEUTRAL_BG: 'refresh',
            }
            
            icon_name = emoji_to_icon.get(icon_emoji, 'add')
            button_type = button_type_map.get(bg_color or UI.BTN_ACCENT_BG, 'green_light')
            
            # Map style to variant
            variant_map = {
                'compact': 'compact',
                'small': 'small', 
                'medium': 'medium',
                'large': 'large',
            }
            variant = variant_map.get(style, 'compact')
            
            return _create_icon_btn_component(
                parent=parent,
                icon_name=icon_name,
                icon_fallback=icon_emoji,
                command=command,
                button_type=button_type,
                variant=variant,
                icon_size=16,
                **kwargs
            )
        
        # Fallback to old emoji-only method if component not available
        style_configs = {
            "compact": {
                "width": 0,
                "height": 0,
                "padx": UI.BTN_ICON_PADDING_COMPACT,
                "pady": UI.BTN_ICON_PADDING_COMPACT,
            },
            "small": {
                "width": UI.BTN_ICON_WIDTH_SMALL,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_SMALL,
                "pady": UI.BTN_ICON_PADDING_SMALL,
            },
            "medium": {
                "width": UI.BTN_ICON_WIDTH_MEDIUM,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_MEDIUM,
                "pady": UI.BTN_ICON_PADDING_MEDIUM,
            },
            "large": {
                "width": UI.BTN_ICON_WIDTH_LARGE,
                "height": 1,
                "padx": UI.BTN_ICON_PADDING_LARGE,
                "pady": UI.BTN_ICON_PADDING_LARGE,
            },
        }

        config = style_configs.get(style, style_configs["compact"])

        if bg_color is None:
            bg_color = UI.BTN_ACCENT_BG
        if hover_color is None:
            hover_color = UI.BTN_ACCENT_HOVER

        color_map = {
            UI.BTN_PRIMARY_BG: UI.BTN_PRIMARY_FG,
            UI.BTN_ACCENT_BG: UI.BTN_ACCENT_FG,
            UI.BTN_INFO_BG: UI.BTN_INFO_FG,
            UI.BTN_NEUTRAL_BG: UI.BTN_NEUTRAL_FG,
            UI.BTN_DANGER_BG: UI.BTN_DANGER_FG,
        }
        fg_color = color_map.get(bg_color, UI.BTN_ACCENT_FG)

        button_config = {
            "text": icon_emoji,
            "command": command,
            "font": UI.FONT_BUTTON,
            "bg": bg_color,
            "fg": fg_color,
            "activebackground": hover_color,
            "activeforeground": fg_color,
            "relief": UI.BTN_RELIEF_NORMAL,
            "cursor": "hand2",
            **config,
            **kwargs,
        }

        return tk.Button(parent, **button_config)

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=3,
            )
            label.pack()
            # Store tooltip in a central map to avoid setting dynamic attributes on widgets
            try:
                if not hasattr(self, "_tooltips"):
                    self._tooltips = {}
                self._tooltips[id(widget)] = tooltip
            except Exception:
                # Last-resort: attach to widget (legacy)
                try:
                    widget._tooltip = tooltip
                except Exception:
                    pass

        def on_leave(event):
            try:
                # Prefer centralized map
                if hasattr(self, "_tooltips") and id(widget) in self._tooltips:
                    try:
                        self._tooltips[id(widget)].destroy()
                    except Exception:
                        pass
                    try:
                        del self._tooltips[id(widget)]
                    except Exception:
                        pass
                    return
                # Fallback to widget attribute
                tooltip = getattr(widget, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(widget, "_tooltip")
                    except Exception:
                        pass
            except Exception:
                pass

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _destroy_widget_tooltip(self, widget):
        """Safely destroy a tooltip for a widget (central map or widget attribute)."""
        try:
            if hasattr(self, "_tooltips") and id(widget) in self._tooltips:
                try:
                    self._tooltips[id(widget)].destroy()
                except Exception:
                    pass
                try:
                    del self._tooltips[id(widget)]
                except Exception:
                    pass
                return
            tooltip = getattr(widget, "_tooltip", None)
            if tooltip is not None:
                try:
                    tooltip.destroy()
                except Exception:
                    pass
                try:
                    delattr(widget, "_tooltip")
                except Exception:
                    pass
        except Exception:
            pass

    def _show_hotkey_diagnostics_modal(self):
        """Show a user-friendly modal with hotkey fix instructions.

        New design: Focus on "How to Fix" with step-by-step instructions
        instead of technical traceback. Progressive disclosure for advanced details.
        """
        try:
            win = tk.Toplevel(self)
            win.title(
                "How to Fix Hotkey Issues" if self.lang == "en" 
                else "Cách Khắc Phục Lỗi Phím Tắt"
            )
            win.transient(self)
            win.grab_set()
            win.geometry("650x420")
            win.configure(bg="#f5f5f5")

            # Main container with padding
            main_frame = tk.Frame(win, bg="#f5f5f5")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Section 1: What's Wrong?
            section1_label = tk.Label(
                main_frame,
                text="🔍 " + ("What's Wrong?" if self.lang == "en" else "Vấn Đề Là Gì?"),
                font=("Arial", 11, "bold"),
                bg="#f5f5f5",
                anchor="w"
            )
            section1_label.pack(fill="x", pady=(0, 8))

            problem_text = (
                "The 'keyboard' package is not installed in your Python environment.\n"
                "This package is required for global hotkeys to work."
                if self.lang == "en" else
                "Gói 'keyboard' chưa được cài đặt trong Python của bạn.\n"
                "Gói này cần thiết để phím tắt toàn cục hoạt động."
            )
            problem_label = tk.Label(
                main_frame,
                text=problem_text,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#444",
                wraplength=580,
                justify="left"
            )
            problem_label.pack(fill="x", pady=(0, 16))

            # Separator
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 16))

            # Section 2: How to Fix (Step-by-step)
            section2_label = tk.Label(
                main_frame,
                text="📝 " + ("How to Fix (Easy 3-Step Solution)" if self.lang == "en" 
                             else "Cách Sửa (3 Bước Đơn Giản)"),
                font=("Arial", 11, "bold"),
                bg="#f5f5f5",
                anchor="w"
            )
            section2_label.pack(fill="x", pady=(0, 12))

            # Step 1
            step1_text = (
                "Step 1: Open Terminal / Command Prompt\n"
                "         Press Win+R, type 'cmd', press Enter"
                if self.lang == "en" else
                "Bước 1: Mở Terminal / Command Prompt\n"
                "         Nhấn Win+R, gõ 'cmd', nhấn Enter"
            )
            step1_label = tk.Label(
                main_frame,
                text=step1_text,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#333",
                justify="left"
            )
            step1_label.pack(fill="x", pady=(0, 8))

            # Step 2: Command box
            step2_text = (
                "Step 2: Copy and paste this command:"
                if self.lang == "en" else
                "Bước 2: Sao chép và dán lệnh này:"
            )
            step2_label = tk.Label(
                main_frame,
                text=step2_text,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#333",
                justify="left"
            )
            step2_label.pack(fill="x", pady=(0, 4))

            # Command box frame
            cmd_frame = tk.Frame(main_frame, bg="#263238", relief="solid", borderwidth=1)
            cmd_frame.pack(fill="x", pady=(0, 4))

            cmd_text_frame = tk.Frame(cmd_frame, bg="#263238")
            cmd_text_frame.pack(side="left", fill="both", expand=True, padx=12, pady=8)

            cmd = f"{sys.executable} -m pip install keyboard"
            cmd_label = tk.Label(
                cmd_text_frame,
                text=cmd,
                font=("Consolas", 9),
                bg="#263238",
                fg="#4CAF50",
                justify="left"
            )
            cmd_label.pack(anchor="w")

            # Copy button
            copy_status_var = tk.StringVar(value="")
            
            def _copy_cmd():
                try:
                    win.clipboard_clear()
                    win.clipboard_append(cmd)
                    copy_status_var.set("✓ " + ("Copied!" if self.lang == "en" else "Đã sao chép!"))
                    win.after(2000, lambda: copy_status_var.set(""))
                except Exception:
                    pass

            copy_btn_frame = tk.Frame(cmd_frame, bg="#263238")
            copy_btn_frame.pack(side="right", padx=8)
            
            copy_btn = tk.Button(
                copy_btn_frame,
                text="📋 " + ("Copy" if self.lang == "en" else "Sao chép"),
                command=_copy_cmd,
                bg="#37474F",
                fg="white",
                font=("Arial", 8, "bold"),
                relief="flat",
                cursor="hand2"
            )
            copy_btn.pack()

            # Copy status
            copy_status_label = tk.Label(
                main_frame,
                textvariable=copy_status_var,
                font=("Arial", 8, "bold"),
                bg="#f5f5f5",
                fg="#4CAF50"
            )
            copy_status_label.pack(fill="x", pady=(0, 8))

            # Step 3
            step3_text = (
                "Step 3: Press Enter and wait for installation"
                if self.lang == "en" else
                "Bước 3: Nhấn Enter và đợi cài đặt hoàn tất"
            )
            step3_label = tk.Label(
                main_frame,
                text=step3_text,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#333",
                justify="left"
            )
            step3_label.pack(fill="x", pady=(0, 16))

            # Separator
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 16))

            # Advanced details (expandable)
            advanced_frame = tk.Frame(main_frame, bg="#f5f5f5")
            advanced_frame.pack(fill="both", expand=True)

            show_advanced_var = tk.BooleanVar(value=False)
            
            def _toggle_advanced():
                if show_advanced_var.get():
                    details_text.pack(fill="both", expand=True, pady=(8, 0))
                    toggle_advanced_btn.config(text="▼ " + ("Hide Advanced Details" if self.lang == "en" 
                                                             else "Ẩn Chi Tiết Nâng Cao"))
                else:
                    details_text.pack_forget()
                    toggle_advanced_btn.config(text="▶ " + ("Show Advanced Details" if self.lang == "en" 
                                                             else "Hiện Chi Tiết Nâng Cao"))

            # Toggle button
            toggle_advanced_btn = tk.Button(
                advanced_frame,
                text="▶ " + ("Show Advanced Details" if self.lang == "en" 
                             else "Hiện Chi Tiết Nâng Cao"),
                command=lambda: (show_advanced_var.set(not show_advanced_var.get()), _toggle_advanced()),
                bg="#f5f5f5",
                fg="#1976D2",
                font=("Arial", 9, "underline"),
                relief="flat",
                cursor="hand2",
                anchor="w"
            )
            toggle_advanced_btn.pack(fill="x")

            # Advanced details text (hidden by default)
            details_frame = tk.Frame(advanced_frame, bg="#f5f5f5")
            
            details_text = tk.Text(
                details_frame,
                wrap="word",
                height=6,
                font=("Consolas", 8),
                bg="#fff",
                fg="#333"
            )
            
            # Build advanced details
            diag = getattr(self, "_hotkey_import_diag", "") or "No diagnostic information available."
            advanced_info = f"""Python Executable:
{sys.executable}

Import Error:
{diag}

Alternative Solutions:
• Try running as Administrator
• Use: python -m pip install --user keyboard
• Check if you're using a virtual environment"""
            
            details_text.insert("1.0", advanced_info)
            details_text.configure(state="disabled")

            # Bottom buttons
            btn_frame = tk.Frame(win, bg="#f5f5f5")
            btn_frame.pack(fill="x", padx=20, pady=(0, 20))

            def _do_retry():
                try:
                    self._on_retry_global_hotkeys()
                finally:
                    try:
                        win.destroy()
                    except Exception:
                        pass

            # Close button
            close_btn = tk.Button(
                btn_frame,
                text="✕ " + ("Close" if self.lang == "en" else "Đóng"),
                command=win.destroy,
                font=("Arial", 9),
                width=12
            )
            close_btn.pack(side="left")

            # Retry button
            retry_btn = tk.Button(
                btn_frame,
                text="🔄 " + ("Retry Now" if self.lang == "en" else "Thử Lại Ngay"),
                command=_do_retry,
                font=("Arial", 9, "bold"),
                bg="#2196F3",
                fg="white",
                width=15
            )
            retry_btn.pack(side="right")

        except Exception as e:
            try:
                messagebox.showerror("Error", f"Failed to show diagnostics: {e}")
            except Exception:
                pass

    # -----------------
    # UI Construction
    # -----------------
    def _build_ui(self):
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # Topbar with language selector and compact window selection
        top = tk.Frame(self, padx=8, pady=6)
        top.pack(fill="x")

        # Left side: Language selector
        tk.Label(top, text=self._t("language")).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cmb = ttk.Combobox(
            top, textvariable=self.lang_var, state="readonly", width=12
        )
        lang_cmb["values"] = ("en", "vi")
        lang_cmb.pack(side="left", padx=(6, 0))
        lang_cmb.bind("<<ComboboxSelected>>", self.on_language_change)

        # Separator
        tk.Frame(top, width=2, bg="#ccc", relief="sunken").pack(
            side="left", fill="y", padx=12, pady=2
        )

        # Right side: Window Selection Combobox - shortened to half width (20)
        self.win_combo_var = tk.StringVar()
        self.win_combo = ttk.Combobox(
            top, textvariable=self.win_combo_var, state="readonly", width=20
        )
        self.win_combo.pack(side="left", padx=(0, 6))

        # Auto-populate windows when dropdown is clicked
        self.win_combo.bind(
            "<Button-1>",
            lambda e: self.on_hunt_find_windows() if not self.win_items else None,
        )
        # Handle window selection
        self.win_combo.bind("<<ComboboxSelected>>", self.on_window_combo_selected)

        # Attach tooltip to combobox explaining window selection
        attach_i18n_tooltip(
            self.win_combo,
            key="window_select_tooltip",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        # Import button styles for refresh button
        from ui.helpers.button_styles import get_button_config

        # Refresh button with icon (manual window refresh) - size 24, padding 12x8
        refresh_icon = self._icon("refresh", "🔄", size=24)
        # Build kwargs for refresh button to avoid passing None to 'image'
        refresh_kwargs = get_button_config("refresh")
        if not isinstance(refresh_icon, str):
            refresh_text = ""
            refresh_kwargs.update({"image": refresh_icon, "compound": "left"})
        else:
            refresh_text = self._t("refresh_windows")
        
        refresh_btn = tk.Button(
            top,
            text=refresh_text,
            command=self.on_hunt_refresh_windows,  # Keep original function
            padx=12,
            pady=8,
            **refresh_kwargs,
        )
        refresh_btn.pack(side="left", padx=(0, 6))
        
        # Tooltip for refresh button - more specific
        refresh_tooltip = (
            "Refresh Window List\n"
            "Scans for game windows"
            if self.lang == "en" else
            "Làm Mới Danh Sách Cửa Sổ\n"
            "Quét lại các cửa sổ game"
        )
        self._create_tooltip(refresh_btn, refresh_tooltip)

        # Keep reference to prevent garbage collection
        if not isinstance(refresh_icon, str):
            try:
                self._image_refs.append(refresh_icon)
            except Exception:
                pass
        
        # Checkbox to toggle advanced controls (window selectors)
        self.show_advanced_controls_var = tk.BooleanVar(value=False)
        
        def toggle_advanced_controls():
            """Toggle visibility of window position selectors."""
            show = self.show_advanced_controls_var.get()
            
            if hasattr(self, 'app_window_selector'):
                if show:
                    if hasattr(self.app_window_selector, 'show'):
                        self.app_window_selector.show()
                else:
                    if hasattr(self.app_window_selector, 'hide'):
                        self.app_window_selector.hide()
            
            if hasattr(self, 'game_window_selector'):
                if show:
                    if hasattr(self.game_window_selector, 'show'):
                        self.game_window_selector.show()
                else:
                    if hasattr(self.game_window_selector, 'hide'):
                        self.game_window_selector.hide()
        
        advanced_check = tk.Checkbutton(
            top,
            text="",  # No text, just checkbox
            variable=self.show_advanced_controls_var,
            command=toggle_advanced_controls,
            bg=top.cget('bg')
        )
        advanced_check.pack(side="left", padx=(0, 6))
        
        # Tooltip for checkbox
        check_tooltip = (
            "Show Advanced Controls\n"
            "• App window positioning\n"
            "• Game window positioning"
            if self.lang == "en" else
            "Hiện Điều Khiển Nâng Cao\n"
            "• Vị trí cửa sổ ứng dụng\n"
            "• Vị trí cửa sổ game"
        )
        self._create_tooltip(advanced_check, check_tooltip)

        # Separator before hunt controls
        tk.Frame(top, width=2, bg="#ccc", relief="sunken").pack(
            side="left", fill="y", padx=12, pady=2
        )

        # Hunt Control Buttons - Using global button styles for consistency with icons
        # Start Hunt Button - Green (CR: 5.8:1) with start icon (icon only)
        start_config = get_button_config("green")
        start_icon = self._icon("start", "▶️", size=20)

        # Start button - Icon only
        start_kwargs = dict(start_config)
        if not isinstance(start_icon, str):
            start_kwargs.update({"image": start_icon})
        self.hunt_start_btn = tk.Button(
            top,
            text="▶️" if isinstance(start_icon, str) else "",
            command=self.on_hunt_start,
            padx=12,
            pady=8,
            **start_kwargs,
        )
        self.hunt_start_btn.pack(side="left", padx=(0, 6))
        
        # Tooltip for Start button
        start_tooltip = self._t("start_hunt")
        if self.lang == "vi":
            start_tooltip += "\n(Ctrl+F5)"
        else:
            start_tooltip += "\n(Ctrl+F5)"
        self._create_tooltip(self.hunt_start_btn, start_tooltip)

        # Keep reference
        if not isinstance(start_icon, str):
            try:
                self._image_refs.append(start_icon)
            except Exception:
                pass

        # Stop Hunt Button - Red (CR: 6.3:1) with stop icon (icon only)
        stop_config = get_button_config("red")
        stop_icon = self._icon("stop", "⏹️", size=20)

        # Stop button - Icon only
        stop_kwargs = dict(stop_config)
        if not isinstance(stop_icon, str):
            stop_kwargs.update({"image": stop_icon})
        self.hunt_stop_btn = tk.Button(
            top,
            text="⏹️" if isinstance(stop_icon, str) else "",
            command=self.on_hunt_stop,
            state="disabled",
            padx=12,
            pady=8,
            **stop_kwargs,
        )
        self.hunt_stop_btn.pack(side="left")
        
        # Tooltip for Stop button
        stop_tooltip = self._t("stop_hunt")
        if self.lang == "vi":
            stop_tooltip += "\n(Ctrl+F6)"
        else:
            stop_tooltip += "\n(Ctrl+F6)"
        self._create_tooltip(self.hunt_stop_btn, stop_tooltip)
        
        # Add hover effect for Stop button - show forbidden icon and cursor when disabled
        forbidden_icon = self._icon("forbidden", "🚫", size=20)
        
        # Keep references to both icons for the Stop button
        self._stop_normal_icon = stop_icon
        self._stop_forbidden_icon = forbidden_icon
        
        def on_stop_hover(event):
            """Show forbidden icon and cursor when hovering over disabled Stop button."""
            if str(self.hunt_stop_btn['state']) == 'disabled':
                # Change icon and cursor to forbidden
                if not isinstance(forbidden_icon, str):
                    self.hunt_stop_btn.config(image=forbidden_icon, text="", cursor="X_cursor")
                else:
                    self.hunt_stop_btn.config(text="🚫", cursor="X_cursor")
        
        def on_stop_leave(event):
            """Restore stop icon and cursor when leaving Stop button."""
            if str(self.hunt_stop_btn['state']) == 'disabled':
                # Restore original icon and cursor
                if not isinstance(stop_icon, str):
                    self.hunt_stop_btn.config(image=stop_icon, text="", cursor="arrow")
                else:
                    self.hunt_stop_btn.config(text="⏹️", cursor="arrow")
        
        self.hunt_stop_btn.bind("<Enter>", on_stop_hover)
        self.hunt_stop_btn.bind("<Leave>", on_stop_leave)
        
        # Keep reference to forbidden icon
        if not isinstance(forbidden_icon, str):
            try:
                self._image_refs.append(forbidden_icon)
            except Exception:
                pass

        # Separator before window controls
        tk.Frame(top, width=2, bg="#ccc", relief="sunken").pack(
            side="left", fill="y", padx=12, pady=2
        )

        # Window Position Selectors (App + Game) - Hidden by default
        if create_app_window_selector and create_game_window_selector:
            # App window selector
            self.app_window_selector = create_app_window_selector(
                parent=top,
                config_path="lib/data/hunt_config.json",
                on_mode_change=self._on_app_window_mode_change
            )
            self.app_window_selector.pack(side="left", padx=(0, 8))
            
            # Game window selector
            self.game_window_selector = create_game_window_selector(
                parent=top,
                config_path="lib/data/hunt_config.json",
                on_mode_change=self._on_game_window_mode_change
            )
            self.game_window_selector.pack(side="left")
            
            # Hide both selectors by default (toggle with refresh button)
            if hasattr(self.app_window_selector, 'hide'):
                self.app_window_selector.hide()
            if hasattr(self.game_window_selector, 'hide'):
                self.game_window_selector.hide()

        # Store notebook reference for keyboard shortcuts
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, pady=(0, 8))

        # Create 4 tabs: Hunt, Setup, Stats, Help
        tab_hunt = tk.Frame(self.notebook, padx=12, pady=12)
        tab_setup = tk.Frame(self.notebook, padx=12, pady=12)
        tab_stats = tk.Frame(self.notebook, padx=12, pady=12)
        tab_help = tk.Frame(self.notebook, padx=12, pady=12)

        self.notebook.add(tab_hunt, text=self._t("tab_hunt"))
        self.notebook.add(tab_setup, text=self._t("tab_setup"))
        self.notebook.add(tab_stats, text=self._t("tab_stats"))
        self.notebook.add(tab_help, text=self._t("tab_help"))

        self._build_hunt_tab(tab_hunt)
        self._build_setup_tab(tab_setup)
        self._build_stats_tab(tab_stats)
        self._build_help_tab(tab_help)

        # Global Apply Section (below tabs, right-aligned)
        self._build_global_apply_section()

    def _build_global_apply_section(self):
        """Build global apply button section below tabs."""
        # Frame for global apply section (right-aligned)
        apply_frame = tk.Frame(self, relief="sunken", bd=1, bg="#f0f0f0")
        apply_frame.pack(fill="x", padx=8, pady=(0, 8))

        # Unsaved changes indicator (left side)
        indicator_frame = tk.Frame(apply_frame, bg="#f0f0f0")
        indicator_frame.pack(side="left", padx=8, pady=6)

        self.unsaved_indicator_label = tk.Label(
            indicator_frame, text="", fg="#666", font=("Arial", 9), bg="#f0f0f0"
        )
        self.unsaved_indicator_label.pack(side="left")

        # Apply All Settings button (right side) - Using global green_light style with save icon
        # Optimized for: Negative Space, Hierarchy, Contrast Ratio (WCAG AA: 5.26:1)
        from ui.helpers.button_styles import get_button_config

        apply_config = get_button_config("green_light")

        # Load save icon (22px to scale with 11pt font)
        save_icon = self._icon("save", "💾", size=22)

        apply_kwargs = dict(apply_config)
        apply_text = self._t("apply_all_settings")
        if not isinstance(save_icon, str):
            apply_kwargs.update({"image": save_icon, "compound": "left"})
            apply_text = f" {apply_text}"
        else:
            apply_text = f"💾 {apply_text}"
        self.global_apply_btn = tk.Button(
            apply_frame,
            text=apply_text,
            command=self.on_global_apply,
            padx=24,
            pady=10,
            **apply_kwargs,
        )
        self.global_apply_btn.pack(
            side="right", padx=10, pady=6
        )  # Increased external margins

        # Keep reference to prevent garbage collection
        if not isinstance(save_icon, str):
            try:
                self._image_refs.append(save_icon)
            except Exception:
                pass

        # Initialize unsaved state
        self.has_unsaved_changes = False
        self._update_unsaved_indicator()

    # Click Tab removed

    # Hunt Tab (Refactored - Sprint 18 Phase 4 Task #2 + UX Enhancement)
    def _build_hunt_tab(self, frm):
        """Streamlined Hunt tab with only essential controls.

        Window selection moved to topbar for quick access via combobox.
        Beginner-friendly: Monster rotation → Skill slots → Quick actions
        """

        # Initialize mode var for compatibility (actual mode selector is in Setup tab)
        self.hunt_mode_var = tk.StringVar(
            value=self.hunt_cfg.get("ui_mode", "beginner")
        )

        # Initialize vars for compatibility with hunt loop (values read from hunt_cfg)
        self.target_key_var = tk.StringVar(
            value=str(self.hunt_cfg.get("target_key", "TAB"))
        )
        # attack_keys removed: per-skill keys from skill_slots are used instead
        self.attack_press_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_press_ms", 60))
        )
        self.target_cycle_var = tk.StringVar(
            value=str(self.hunt_cfg.get("target_cycle_delay", 0.2))
        )
        self.search_interval_var = tk.StringVar(
            value=str(self.hunt_cfg.get("search_interval", 0.25))
        )
        self.attack_interval_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_interval", 0.15))
        )
        self.lost_timeout_var = tk.StringVar(
            value=str(self.hunt_cfg.get("lost_timeout_sec", 1.2))
        )
        self.attack_duration_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_min_duration_sec", 1.5))
        )
        self.template_var = tk.StringVar(
            value=str(
                self.hunt_cfg.get("template_path", "assets/images/target_frame.png")
            )
        )

        region = self.hunt_cfg.get("region") or ["", "", "", ""]
        self.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")

        self.bring_front_var = tk.BooleanVar(
            value=bool(self.hunt_cfg.get("bring_to_front_each_cycle", False))
        )

        # Section 2: Monster Selection (Phase 3: Multi-Monster Support)
        # Sprint 22 Patch 2: Dynamic title based on training mode
        self.monster_frame = tk.LabelFrame(
            frm, text=self._t("hunt_monsters"), padx=10, pady=8
        )
        self.monster_frame.grid(
            row=1, column=0, columnspan=4, sticky="we", pady=(0, 12)
        )
        self.monster_frame.grid_columnconfigure(0, weight=1)

        # Rotation mode selection
        mode_bar = tk.Frame(self.monster_frame)
        mode_bar.pack(fill="x", pady=(0, 8))
        tk.Label(mode_bar, text=self._t("rotation_mode")).pack(side="left")

        self.rotation_mode_var = tk.StringVar(
            value=self.hunt_cfg.get("rotation_mode", "sequence")
        )
        self.rotation_mode_combo = ttk.Combobox(
            mode_bar,
            textvariable=self.rotation_mode_var,
            state="readonly",
            width=12,
            values=["sequence", "priority"],
        )
        self.rotation_mode_combo.pack(side="left", padx=(6, 0))
        self.rotation_mode_combo.bind(
            "<<ComboboxSelected>>", self._on_rotation_mode_changed
        )

        # Mode description
        self.rotation_desc_var = tk.StringVar()
        tk.Label(
            mode_bar, textvariable=self.rotation_desc_var, fg="#666", font=("Arial", 8)
        ).pack(side="left", padx=(8, 0))

        # Monster list with checkboxes
        list_container = tk.Frame(self.monster_frame)
        list_container.pack(fill="both", expand=True)

        # Listbox frame with scrollbar
        listbox_frame = tk.Frame(list_container)
        listbox_frame.pack(side="left", fill="both", expand=True)

        self.monster_rotation_listbox = tk.Listbox(
            listbox_frame,
            height=5,
            exportselection=False,
            selectmode="single",
            font=("Arial", 9),
        )
        self.monster_rotation_listbox.pack(side="left", fill="both", expand=True)

        monster_scroll = tk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.monster_rotation_listbox.yview,
        )
        monster_scroll.pack(side="right", fill="y")
        self.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)

        # Control buttons (right side) - Using compact icon buttons (all 20px for consistency)
        btn_container = tk.Frame(list_container)
        btn_container.pack(side="right", fill="y", padx=(8, 0))

        # Add monster button - Compact style (20px: 16px icon + 2×2px padding)
        self.btn_add_monster = self._create_icon_button(
            btn_container,
            icon_emoji="➕",
            command=self._on_monster_add_smart,
            style="compact",
            bg_color=UI.BTN_ACCENT_BG,
            hover_color=UI.BTN_ACCENT_HOVER,
        )
        self.btn_add_monster.pack(pady=(0, UI.BTN_SPACING))
        self._create_tooltip(
            self.btn_add_monster, self._t("tooltip_add_monster_normal")
        )

        # Priority reorder buttons - Compact style (20px: 16px icon + 2×2px padding)
        # Both buttons use blue color for consistency
        self.btn_move_up = self._create_icon_button(
            btn_container,
            icon_emoji="↑",
            command=self._on_monster_move_up,
            style="compact",
            bg_color=UI.BTN_INFO_BG,  # Blue for UP
            hover_color=UI.BTN_INFO_HOVER,
        )
        self.btn_move_up.pack(pady=(0, UI.BTN_SPACING // 2))
        self._create_tooltip(self.btn_move_up, self._t("tooltip_move_up"))

        self.btn_move_down = self._create_icon_button(
            btn_container,
            icon_emoji="↓",
            command=self._on_monster_move_down,
            style="compact",
            bg_color=UI.BTN_INFO_BG,  # Blue for DOWN
            hover_color=UI.BTN_INFO_HOVER,
        )
        self.btn_move_down.pack(pady=(0, UI.BTN_SPACING * 1.5))
        self._create_tooltip(self.btn_move_down, self._t("tooltip_move_down"))

        # Library Manager buttons removed per request

        # Current monster status
        self.monster_status_var = tk.StringVar()
        tk.Label(
            self.monster_frame,
            textvariable=self.monster_status_var,
            fg="#2196F3",
            font=("Arial", 8, "bold"),
        ).pack(fill="x", pady=(8, 0))

        # Bind click to toggle checkbox
        self.monster_rotation_listbox.bind("<Double-Button-1>", self._on_monster_toggle)
        self.monster_rotation_listbox.bind(
            "<<ListboxSelect>>", self._on_monster_list_select
        )
        self.monster_rotation_listbox.bind(
            "<Delete>", self._on_monster_delete_from_list
        )  # Sprint 22 Patch 2: Delete key
        self.monster_rotation_listbox.bind(
            "<BackSpace>", self._on_monster_delete_from_list
        )  # Also backspace

        # Sprint 22 Patch 2: Context menu for right-click delete
        self.monster_context_menu = tk.Menu(self.monster_rotation_listbox, tearoff=0)
        self.monster_context_menu.add_command(
            label=self._t("monster_delete"),  # "Delete" / "Xóa"
            command=self._on_monster_delete_from_list,
        )
        self.monster_rotation_listbox.bind(
            "<Button-3>", self._show_monster_context_menu
        )  # Right-click

        # Sprint 22 Patch 2: Hint for switching back to normal mode
        self.training_mode_hint_var = tk.StringVar()
        self.training_mode_hint_label = tk.Label(
            self.monster_frame,
            textvariable=self.training_mode_hint_var,
            fg="#FF6F00",  # Orange
            font=("Arial", 8, "italic"),
            wraplength=400,
            justify="left",
        )
        self.training_mode_hint_label.pack(fill="x", pady=(4, 0))

        # Legacy monster estimate (keep for compatibility)
        self.monster_estimate_var.set("")

        # Section 2.5: Training Mode Toggle (Sprint 22 Patch 2 - Hidden, auto-detect from training_monster_list)
        # NOTE: Training mode checkbox removed to avoid user confusion.
        # System auto-enables training mode when training_monster_list has items.
        # User adds training dummies via normal "Add Monster" dialog (filtered by training_mode flag).

        # Initialize training_mode_var for backward compatibility
        self.training_mode_var = tk.BooleanVar(value=False)  # Will be auto-updated

        # Training mode status indicator (kept for debug info)
        self.training_mode_status_var = tk.StringVar()
        # Status label hidden, only used internally

        # Section 3: Skill slots selection
        skill_frame_outer = tk.LabelFrame(
            frm, text=self._t("skill_slots"), padx=10, pady=8
        )
        skill_frame_outer.grid(row=2, column=0, columnspan=4, sticky="we", pady=(0, 12))

        # Manage skills hint (button hidden, use Ctrl+K shortcut)
        hint_label = tk.Label(
            skill_frame_outer,
            text=f"ℹ️ {self._t('skill_manage_hint')}",
            fg="#666",
            font=("Arial", 8),
            cursor="hand2",
        )
        hint_label.pack(pady=(0, 6))
        hint_label.bind("<Button-1>", lambda e: self._open_skill_manager())

        slot_frame = tk.Frame(skill_frame_outer)
        slot_frame.pack(fill="both", expand=True)
        slot_frame.grid_columnconfigure(1, weight=1)
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_key_labels = []
        for idx in range(self.skill_slot_count):
            var = tk.StringVar()
            self.skill_slot_vars.append(var)
            label = self._t("skill_slot_label").format(i=idx + 1)
            tk.Label(slot_frame, text=label).grid(row=idx, column=0, sticky="e", pady=2)
            cmb = ttk.Combobox(slot_frame, textvariable=var, state="readonly", width=24)
            cmb.grid(row=idx, column=1, sticky="we", padx=(4, 0), pady=2)
            cmb.bind("<<ComboboxSelected>>", self.on_skill_slot_changed)
            # Key label showing which key is assigned to the selected skill
            key_lbl = tk.Label(slot_frame, text="", width=6, anchor="w", fg="#333")
            key_lbl.grid(row=idx, column=2, padx=(6, 0))
            self.skill_slot_key_labels.append(key_lbl)
            # Clear button (moved to column 3)
            tk.Button(
                slot_frame,
                text=self._t("skill_slot_clear"),
                command=lambda v=var: self._clear_skill_slot(v),
            ).grid(row=idx, column=3, padx=(6, 0))
            self.skill_slot_boxes.append(cmb)

        self._refresh_monster_select_options()
        self._load_skill_slots_from_cfg()

        # Phase 3: Populate monster rotation list
        self._refresh_monster_rotation_list()

        # Section 3.5: Skill Performance Statistics (Sprint 22 Patch 1 - Training Mode)
        self.skill_stats_frame = tk.LabelFrame(
            frm, text=self._t("skill_stats_title"), padx=10, pady=8
        )
        self.skill_stats_frame.grid(
            row=2,
            column=4,
            rowspan=1,
            columnspan=4,
            sticky="nswe",
            padx=(12, 0),
            pady=(0, 12),
        )

        # Create Treeview for stats display
        stats_container = tk.Frame(self.skill_stats_frame)
        stats_container.pack(fill="both", expand=True)

        # Define columns
        columns = ("skill", "casts", "last_cast", "cooldown", "success")
        self.skill_stats_tree = ttk.Treeview(
            stats_container, columns=columns, show="headings", height=6
        )

        # Configure column headings
        self.skill_stats_tree.heading("skill", text=self._t("skill_name_col"))
        self.skill_stats_tree.heading("casts", text=self._t("cast_count_col"))
        self.skill_stats_tree.heading("last_cast", text=self._t("last_cast_col"))
        self.skill_stats_tree.heading("cooldown", text=self._t("cooldown_col"))
        self.skill_stats_tree.heading("success", text=self._t("success_rate_col"))

        # Configure column widths
        self.skill_stats_tree.column("skill", width=120)
        self.skill_stats_tree.column("casts", width=60, anchor="center")
        self.skill_stats_tree.column("last_cast", width=80, anchor="center")
        self.skill_stats_tree.column("cooldown", width=80, anchor="center")
        self.skill_stats_tree.column("success", width=80, anchor="center")

        # Add scrollbar
        stats_scroll = tk.Scrollbar(
            stats_container, orient="vertical", command=self.skill_stats_tree.yview
        )
        stats_scroll.pack(side="right", fill="y")
        self.skill_stats_tree.config(yscrollcommand=stats_scroll.set)
        self.skill_stats_tree.pack(side="left", fill="both", expand=True)

        # Configure tags for color coding
        self.skill_stats_tree.tag_configure("excellent", foreground="#4CAF50")  # Green
        self.skill_stats_tree.tag_configure("good", foreground="#FF9800")  # Orange
        self.skill_stats_tree.tag_configure("poor", foreground="#F44336")  # Red

        # Initially hide stats frame (show only when training mode enabled)
        if not self.training_mode_var.get():
            self.skill_stats_frame.grid_remove()

        # Section 4: Status Display (wizard button moved to Setup tab)
        self.hunt_status = tk.StringVar(value=self._t("hunt_idle"))
        status_label = tk.Label(
            frm,
            textvariable=self.hunt_status,
            fg="#666",
            font=("Arial", 9),
            relief="sunken",
            padx=8,
            pady=4,
        )
        status_label.grid(row=3, column=0, columnspan=8, sticky="we")

        # Helper text for beginners
        tk.Label(
            frm, text=self._t("hunt_tab_help_text"), fg="#999", font=("Arial", 8)
        ).grid(row=4, column=0, columnspan=8, pady=(8, 0))

        # Empty widget lists for compatibility (no progressive disclosure in streamlined Hunt tab)
        self.hunt_intermediate_widgets = []
        self.hunt_advanced_widgets = []

        for i in range(4):
            frm.grid_columnconfigure(i, weight=1)
        self._update_window_bounds_display()

        # Auto-populate window selection if config exists (UX FIX #3)
        # This prevents users from having to re-select window every time
        self._auto_populate_saved_window()

    # Click UI and handlers removed

    # -----------------
    # Hunt Handlers
    # -----------------
    def _on_hunt_mode_changed(self):
        """Handle mode toggle - show/hide fields based on selected mode."""
        mode = self.hunt_mode_var.get()

        # Save mode preference
        self.hunt_cfg["ui_mode"] = mode
        try:
            with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")

        # Apply visibility changes
        self._apply_hunt_mode()

        # Update status
        mode_labels = {
            "beginner": self._t("mode_beginner"),
            "intermediate": self._t("mode_intermediate"),
            "advanced": self._t("mode_advanced"),
        }
        self.hunt_status.set(
            f"Mode: {mode_labels.get(mode, mode)} - {self._t('hunt_idle')}"
        )

    def _apply_hunt_mode(self):
        """Show/hide widgets based on current mode setting."""
        mode = (
            self.hunt_mode_var.get() if hasattr(self, "hunt_mode_var") else "beginner"
        )

        if mode == "beginner":
            # Hide intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid_remove()
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()

        elif mode == "intermediate":
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()

        elif mode == "advanced":
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Show advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid(row=row, column=col, **kwargs)

    def _update_window_bounds_display(self):
        if not hasattr(self, "window_bounds_display_var"):
            return
        if self.current_window_bounds:
            bounds_text = "{left},{top},{width},{height}".format(
                **self.current_window_bounds
            )
            self.window_bounds_display_var.set(
                self._t("hunt_window_bounds").format(value=bounds_text)
            )
        else:
            self.window_bounds_display_var.set(self._t("hunt_window_bounds_none"))

    # Setup Tab (Sprint 18 Phase 4)
    def _build_setup_tab(self, parent):
        """Build Setup tab with configuration and library management."""

        # Section 1: Configuration Mode
        mode_frame = tk.LabelFrame(parent, text=self._t("setup_mode"), padx=12, pady=10)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 12))

        mode_desc = tk.Label(
            mode_frame, text=self._t("setup_mode_desc"), fg="#666", font=("Arial", 9)
        )
        mode_desc.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Read current mode from hunt_cfg
        current_mode = self.hunt_cfg.get("ui_mode", "beginner")
        self.setup_mode_var = tk.StringVar(value=current_mode)

        modes = [
            ("beginner", self._t("mode_beginner"), self._t("mode_beginner_desc")),
            (
                "intermediate",
                self._t("mode_intermediate"),
                self._t("mode_intermediate_desc"),
            ),
            ("advanced", self._t("mode_advanced"), self._t("mode_advanced_desc")),
        ]

        for idx, (mode_val, mode_label, mode_desc_text) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=mode_label,
                variable=self.setup_mode_var,
                value=mode_val,
                command=self._on_setup_mode_changed,
                font=("Arial", 9, "bold"),
            )
            rb.grid(row=idx + 1, column=0, sticky="w", pady=2)

            desc_label = tk.Label(
                mode_frame, text=f"  {mode_desc_text}", fg="#666", font=("Arial", 8)
            )
            desc_label.grid(row=idx + 1, column=1, sticky="w", padx=(4, 0), pady=2)

        # Setup Wizard button (only enabled in Beginner mode)
        wizard_frame = tk.Frame(parent)
        wizard_frame.grid(row=0, column=2, sticky="e", padx=(12, 0))

        # Use global blue button style
        # NOTE: Setup Wizard button removed - now accessible via Global Hotkeys (Ctrl+Shift+N)
        # Method on_setup_wizard() is kept for hotkey callback usage

        # Section 2: Global Hotkeys (moved from Advanced tab)
        # Load keyboard icon
        # Section 2: Global Hotkeys with keyboard icon
        hotkey_title = "Global Hotkeys" if self.lang == "en" else "Phím Tắt Toàn Cục"
        hotkey_frame = tk.LabelFrame(parent, text=f"⌨️ {hotkey_title}", padx=12, pady=10)
        hotkey_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))

        # Description
        hotkey_desc_text = (
            "Global hotkeys work even when app is minimized or not focused."
        )
        if self.lang == "vi":
            hotkey_desc_text = (
                "Phím tắt toàn cục hoạt động khi ứng dụng thu nhỏ hoặc không focus."
            )
        tk.Label(
            hotkey_frame,
            text=hotkey_desc_text,
            fg="#666",
            font=("Arial", 8),
            wraplength=500,
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Enable/Disable checkbox
        hotkey_cfg = self.hunt_cfg.get("global_hotkeys", {})
        self.global_hotkey_enabled_var = tk.BooleanVar(
            value=hotkey_cfg.get("enabled", True)
        )

        enable_text = (
            "Enable Global Hotkeys" if self.lang == "en" else "Bật phím tắt toàn cục"
        )
        tk.Checkbutton(
            hotkey_frame,
            text=enable_text,
            variable=self.global_hotkey_enabled_var,
            font=("Arial", 9, "bold"),
            command=self._on_global_hotkey_toggle,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Start hotkey
        start_label = "Start Hunt:" if self.lang == "en" else "Bắt đầu Hunt:"
        tk.Label(hotkey_frame, text=start_label, font=("Arial", 9)).grid(
            row=2, column=0, sticky="e", padx=(0, 8), pady=4
        )

        # Combobox for start key
        start_key = hotkey_cfg.get("start_key", "ctrl+shift+r")
        self.global_hotkey_start_var = tk.StringVar(value=start_key)

        hotkey_options = [
            "ctrl+shift+r",
            "ctrl+shift+s",
            "ctrl+alt+r",
            "ctrl+alt+s",
            "f9",
            "f10",
            "f11",
            "f12",
        ]

        from tkinter import ttk

        start_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_start_var,
            values=hotkey_options,
            width=15,
            state="readonly",
        )
        start_combo.grid(row=2, column=1, sticky="w", pady=4)

        # Stop hotkey
        stop_label = "Stop Hunt:" if self.lang == "en" else "Dừng Hunt:"
        tk.Label(hotkey_frame, text=stop_label, font=("Arial", 9)).grid(
            row=3, column=0, sticky="e", padx=(0, 8), pady=4
        )

        # Combobox for stop key
        stop_key = hotkey_cfg.get("stop_key", "ctrl+shift+e")
        self.global_hotkey_stop_var = tk.StringVar(value=stop_key)

        stop_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_stop_var,
            values=hotkey_options,
            width=15,
            state="readonly",
        )
        stop_combo.grid(row=3, column=1, sticky="w", pady=4)

        # NEW: Setup Wizard hotkey
        wizard_label = "Setup Wizard:" if self.lang == "en" else "Trợ lý Thiết lập:"
        wizard_label_widget = tk.Label(
            hotkey_frame, text=wizard_label, font=("Arial", 9)
        )
        wizard_label_widget.grid(row=4, column=0, sticky="e", padx=(0, 8), pady=4)

        wizard_key = hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n")
        self.global_hotkey_wizard_var = tk.StringVar(value=wizard_key)

        wizard_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_wizard_var,
            values=hotkey_options + ["ctrl+shift+n", "ctrl+alt+n"],
            width=15,
            state="readonly",
        )
        wizard_combo.grid(row=4, column=1, sticky="w", pady=4)

        # Store for enable/disable logic
        self.wizard_hotkey_combo = wizard_combo
        self.wizard_hotkey_label = wizard_label_widget

        # NEW: Library Manager hotkey
        library_label = "Library Manager:" if self.lang == "en" else "Quản lý Thư viện:"
        library_label_widget = tk.Label(
            hotkey_frame, text=library_label, font=("Arial", 9)
        )
        library_label_widget.grid(row=5, column=0, sticky="e", padx=(0, 8), pady=4)

        library_key = hotkey_cfg.get("library_manager_key", "ctrl+shift+l")
        self.global_hotkey_library_var = tk.StringVar(value=library_key)

        library_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_library_var,
            values=hotkey_options + ["ctrl+shift+l", "ctrl+alt+l"],
            width=15,
            state="readonly",
        )
        library_combo.grid(row=5, column=1, sticky="w", pady=4)

        # Store for future use
        self.library_hotkey_combo = library_combo
        self.library_hotkey_label = library_label_widget

        # NEW: Vision Wizard hotkey (Sprint 22)
        vision_label = "Vision Wizard:" if self.lang == "en" else "Trợ lý Vision:"
        vision_label_widget = tk.Label(
            hotkey_frame, text=vision_label, font=("Arial", 9)
        )
        vision_label_widget.grid(row=6, column=0, sticky="e", padx=(0, 8), pady=4)

        vision_key = hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v")
        self.global_hotkey_vision_var = tk.StringVar(value=vision_key)

        vision_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_vision_var,
            values=hotkey_options + ["ctrl+shift+v", "ctrl+alt+v"],
            width=15,
            state="readonly",
        )
        vision_combo.grid(row=6, column=1, sticky="w", pady=4)

        # Store for future use
        self.vision_hotkey_combo = vision_combo
        self.vision_hotkey_label = vision_label_widget

        # Hint: Hotkeys apply automatically
        hint_hotkey = "Hotkeys apply automatically when you click any field outside this section."
        if self.lang == "vi":
            hint_hotkey = "Phím tắt được áp dụng tự động khi bạn click ra ngoài phần này."
        tk.Label(
            hotkey_frame,
            text=hint_hotkey,
            fg="#1976D2",
            font=("Arial", 8),
            wraplength=500,
            justify="left",
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Status indicator - Shows success/warning/error state with icon
        # This replaces the old diagnostic banner with a clearer status-driven design
        self._hotkey_status_var = tk.StringVar(value="")
        self._hotkey_status_label = tk.Label(
            hotkey_frame,
            textvariable=self._hotkey_status_var,
            fg="#4CAF50",  # Default green for success
            font=("Arial", 9, "bold"),
            wraplength=500,
            justify="left",
        )
        self._hotkey_status_label.grid(row=8, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Secondary status info (count, timestamp)
        self._hotkey_status_detail_var = tk.StringVar(value="")
        self._hotkey_status_detail_label = tk.Label(
            hotkey_frame,
            textvariable=self._hotkey_status_detail_var,
            fg="#666",
            font=("Arial", 8),
            wraplength=500,
            justify="left",
        )
        self._hotkey_status_detail_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(2, 0))

        # Action buttons frame (for retry and details buttons)
        buttons_frame = tk.Frame(hotkey_frame)
        buttons_frame.grid(row=10, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Retry button (only visible when needed)
        retry_text = (
            "Retry Global Hotkeys" if self.lang == "en" else "Thử lại phím tắt toàn cục"
        )
        self._hotkey_retry_btn = tk.Button(
            buttons_frame, text=retry_text, command=self._on_retry_global_hotkeys
        )
        # Store reference for show/hide logic
        
        # Details/Fix button (only visible when there are issues)
        details_text = "Show Fix Instructions" if self.lang == "en" else "Hướng Dẫn Khắc Phục"
        self._hotkey_details_btn = tk.Button(
            buttons_frame, text=details_text, command=self._show_hotkey_diagnostics_modal
        )
        
        # Initially hide buttons - they will be shown based on hotkey registration status
        # This is updated by _update_hotkey_status_ui() after registration
        
        # Store old diagnostic var for backward compatibility
        self._hotkey_diag_var = self._hotkey_status_var  # Alias for compatibility

        # Section 3: Advanced Hunt Settings (visible for intermediate/advanced)
        self.adv_frame = tk.LabelFrame(
            parent, text=self._t("setup_advanced"), padx=12, pady=10
        )
        self.adv_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 12))

        # Target/Attack keys
        tk.Label(self.adv_frame, text=self._t("target_key")).grid(
            row=0, column=0, sticky="e", pady=4
        )
        self.setup_target_key_var = tk.StringVar(
            value=str(self.hunt_cfg.get("target_key", "TAB"))
        )
        tk.Entry(self.adv_frame, textvariable=self.setup_target_key_var, width=8).grid(
            row=0, column=1, sticky="w", pady=4
        )

        # Attack keys removed: use per-skill keys from skill_slots instead

        # Timing intervals
        tk.Label(self.adv_frame, text=self._t("press_ms")).grid(
            row=1, column=0, sticky="e", pady=4
        )
        self.setup_press_ms_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_press_ms", 60))
        )
        tk.Entry(self.adv_frame, textvariable=self.setup_press_ms_var, width=8).grid(
            row=1, column=1, sticky="w", pady=4
        )

        tk.Label(self.adv_frame, text=self._t("target_cycle")).grid(
            row=1, column=2, sticky="e", padx=(16, 4), pady=4
        )
        self.setup_target_cycle_var = tk.StringVar(
            value=str(self.hunt_cfg.get("target_cycle_delay", 0.2))
        )
        tk.Entry(
            self.adv_frame, textvariable=self.setup_target_cycle_var, width=8
        ).grid(row=1, column=3, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("search_interval")).grid(
            row=2, column=0, sticky="e", pady=4
        )
        self.setup_search_interval_var = tk.StringVar(
            value=str(self.hunt_cfg.get("search_interval", 0.25))
        )
        tk.Entry(
            self.adv_frame, textvariable=self.setup_search_interval_var, width=8
        ).grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(self.adv_frame, text=self._t("attack_interval")).grid(
            row=2, column=2, sticky="e", padx=(16, 4), pady=4
        )
        self.setup_attack_interval_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_interval", 0.15))
        )
        tk.Entry(
            self.adv_frame, textvariable=self.setup_attack_interval_var, width=8
        ).grid(row=2, column=3, sticky="w", pady=4)

        # Lost timeout & Attack duration
        tk.Label(self.adv_frame, text=self._t("lost_timeout")).grid(
            row=3, column=0, sticky="e", pady=4
        )
        self.setup_lost_timeout_var = tk.StringVar(
            value=str(self.hunt_cfg.get("lost_timeout_sec", 1.2))
        )
        lost_entry = tk.Entry(
            self.adv_frame, textvariable=self.setup_lost_timeout_var, width=8
        )
        lost_entry.grid(row=3, column=1, sticky="w", pady=4)
        attach_i18n_tooltip(
            lost_entry,
            key="tooltip_lost_timeout",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        tk.Label(self.adv_frame, text=self._t("attack_duration")).grid(
            row=3, column=2, sticky="e", padx=(16, 4), pady=4
        )
        self.setup_attack_duration_var = tk.StringVar(
            value=str(self.hunt_cfg.get("attack_min_duration_sec", 1.5))
        )
        attack_entry = tk.Entry(
            self.adv_frame, textvariable=self.setup_attack_duration_var, width=8
        )
        attack_entry.grid(row=3, column=3, sticky="w", pady=4)
        attach_i18n_tooltip(
            attack_entry,
            key="tooltip_attack_duration",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        # Template threshold
        tk.Label(self.adv_frame, text=self._t("template_threshold")).grid(
            row=4, column=0, sticky="e", pady=4
        )
        self.setup_threshold_var = tk.StringVar(
            value=str(self.hunt_cfg.get("template_threshold", 0.8))
        )
        tk.Entry(self.adv_frame, textvariable=self.setup_threshold_var, width=8).grid(
            row=4, column=1, sticky="w", pady=4
        )

        # Section 4: Window Settings (visible for advanced only)
        self.window_frame = tk.LabelFrame(
            parent, text=self._t("setup_window"), padx=12, pady=10
        )
        self.window_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))

        # Template path
        tk.Label(self.window_frame, text=self._t("template")).grid(
            row=0, column=0, sticky="e", pady=4
        )
        self.setup_template_var = tk.StringVar(
            value=str(
                self.hunt_cfg.get("template_path", "assets/images/target_frame.png")
            )
        )
        tk.Entry(
            self.window_frame, textvariable=self.setup_template_var, width=40
        ).grid(row=0, column=1, columnspan=2, sticky="w", pady=4)
        tk.Button(
            self.window_frame,
            text=self._t("browse"),
            command=self.on_hunt_browse_template,
        ).grid(row=0, column=3, padx=(4, 0), pady=4)

        # Region
        tk.Label(self.window_frame, text=self._t("region_l")).grid(
            row=1, column=0, sticky="e", pady=4
        )
        region = self.hunt_cfg.get("region") or ["", "", "", ""]
        self.setup_reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.setup_reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.setup_reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.setup_reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")

        reg_frame = tk.Frame(self.window_frame)
        reg_frame.grid(row=1, column=1, columnspan=3, sticky="w", pady=4)

        tk.Entry(reg_frame, textvariable=self.setup_reg_l, width=6).pack(side="left")
        tk.Label(reg_frame, text=self._t("t")).pack(side="left", padx=(8, 4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_t, width=6).pack(side="left")
        tk.Label(reg_frame, text=self._t("w")).pack(side="left", padx=(8, 4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_w, width=6).pack(side="left")
        tk.Label(reg_frame, text=self._t("h")).pack(side="left", padx=(8, 4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_h, width=6).pack(side="left")

        # Window bounds display
        tk.Label(self.window_frame, text=self._t("hunt_window_bounds_label")).grid(
            row=2, column=0, sticky="e", pady=(8, 4)
        )
        self.setup_bounds_display_var = tk.StringVar(
            value=self._t("hunt_window_bounds_none")
        )
        tk.Label(
            self.window_frame, textvariable=self.setup_bounds_display_var, fg="blue"
        ).grid(row=2, column=1, columnspan=2, sticky="w", pady=(8, 4))
        tk.Button(
            self.window_frame,
            text=self._t("clear_bounds"),
            command=self._clear_window_bounds,
        ).grid(row=2, column=3, padx=(4, 0), pady=(8, 4))

        # Apply button removed - now using global apply button below tabs

        # Initial visibility update based on mode
        self._update_setup_visibility()

    # Stats Tab (Sprint 18 Phase 4)
    def _build_stats_tab(self, parent):
        """Build Stats tab with runtime statistics and performance metrics."""
        # TODO: Implement Stats tab
        placeholder = tk.Label(
            parent,
            text="Stats Tab - Coming Soon\n\nThis tab will contain:\n• Hunt Statistics (runtime, kills, exp/hr)\n• Performance Metrics (FPS, CPU, memory)\n• Rotation History\n• Export controls",
            justify="left",
            padx=20,
            pady=20,
        )
        placeholder.pack()

    # Help Tab (Sprint 18 Phase 4)
    def _build_help_tab(self, parent):
        """Build Help tab with documentation and tutorials."""
        # Scrollable frame for help content
        canvas = tk.Canvas(parent, bg="white")
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Quick Start Guide
        help_frame = tk.LabelFrame(
            scrollable_frame,
            text=self._t("help_quickstart"),
            padx=10,
            pady=8,
            bg="white",
        )
        help_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(
            help_frame, text=self._t("help_quickstart_text"), justify="left", bg="white"
        ).pack(anchor="w")

        # Keyboard Shortcuts
        shortcuts_frame = tk.LabelFrame(
            scrollable_frame,
            text=self._t("help_shortcuts"),
            padx=10,
            pady=8,
            bg="white",
        )
        shortcuts_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(
            shortcuts_frame,
            text=self._t("help_shortcuts_text"),
            justify="left",
            bg="white",
        ).pack(anchor="w")

        # Troubleshooting
        trouble_frame = tk.LabelFrame(
            scrollable_frame,
            text=self._t("help_troubleshooting"),
            padx=10,
            pady=8,
            bg="white",
        )
        trouble_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(
            trouble_frame,
            text=self._t("help_troubleshooting_text"),
            justify="left",
            bg="white",
        ).pack(anchor="w")

        # About
        about_frame = tk.LabelFrame(
            scrollable_frame, text=self._t("help_about"), padx=10, pady=8, bg="white"
        )
        about_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(
            about_frame, text=self._t("help_about_text"), justify="left", bg="white"
        ).pack(anchor="w")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Setup Tab Handlers (Sprint 18 Phase 4)
    def _on_setup_mode_changed(self):
        """Handle mode change in Setup tab and sync with Hunt tab."""
        mode = self.setup_mode_var.get()

        # Save mode preference
        self.hunt_cfg["ui_mode"] = mode
        try:
            with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")

        # Sync Hunt tab mode var if it exists
        if hasattr(self, "hunt_mode_var"):
            self.hunt_mode_var.set(mode)
            self._apply_hunt_mode()

        # Update Setup tab visibility
        self._update_setup_visibility()

        # Update status if exists
        if hasattr(self, "hunt_status"):
            mode_labels = {
                "beginner": self._t("mode_beginner"),
                "intermediate": self._t("mode_intermediate"),
                "advanced": self._t("mode_advanced"),
            }
            self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)}")

        # Re-register hotkeys (wizard hotkey only in beginner mode)
        # This will update the count display (4 vs 5 hotkeys)
        try:
            self._register_global_hotkeys()
        except Exception as e:
            print(f"Warning: Could not re-register hotkeys after mode change: {e}")

    def _on_app_window_mode_change(self, mode: str):
        """Handle app window positioning mode change."""
        try:
            # Apply mode to main app window
            if mode == "topmost":
                self.attributes("-topmost", True)
                self.state("normal")
            elif mode == "minimized":
                self.attributes("-topmost", False)
                self.iconify()
            elif mode == "maximized":
                self.attributes("-topmost", False)
                self.state("zoomed")
            else:  # normal
                self.attributes("-topmost", False)
                self.state("normal")
            
            # Update status
            if hasattr(self, "hunt_status"):
                mode_labels = {
                    "normal": "Normal" if self.lang == "en" else "Bình thường",
                    "topmost": "Always On Top" if self.lang == "en" else "Luôn ở trên",
                    "minimized": "Minimized" if self.lang == "en" else "Thu nhỏ",
                    "maximized": "Maximized" if self.lang == "en" else "Phóng to",
                }
                msg = f"App: {mode_labels.get(mode, mode)}"
                self.hunt_status.set(msg)
        except Exception as e:
            print(f"[App Window] Error applying mode '{mode}': {e}")

    def _on_game_window_mode_change(self, mode: str):
        """Handle game window positioning mode change."""
        try:
            # Save to config
            self.hunt_cfg["game_window_mode"] = mode
            save_hunt_config(self.hunt_cfg)
            
            # Update status
            if hasattr(self, "hunt_status"):
                mode_labels = {
                    "none": "None" if self.lang == "en" else "Không",
                    "below": "Below App" if self.lang == "en" else "Dưới App",
                    "above": "Above All" if self.lang == "en" else "Trên tất cả",
                }
                msg = f"Game: {mode_labels.get(mode, mode)}"
                self.hunt_status.set(msg)
            
            # Apply immediately if hunt is not running
            if not self.hunt_running:
                if mode == "below":
                    self.on_hunt_bring_front_below_app()
                elif mode == "above":
                    self.on_hunt_bring_front()
        except Exception as e:
            print(f"[Game Window] Error applying mode '{mode}': {e}")

    def _on_global_hotkey_toggle(self):
        """Handle enable/disable of global hotkeys checkbox.

        Note: Changes only take effect after clicking Global Apply button.
        This is intentional to avoid accidental hotkey changes during configuration.
        """
        enabled = bool(self.global_hotkey_enabled_var.get())

        # Persist setting immediately and apply
        try:
            self.hunt_cfg.setdefault("global_hotkeys", {})["enabled"] = enabled
            save_hunt_config(self.hunt_cfg)
        except Exception:
            pass

        # Apply immediately (register/unregister hotkeys)
        try:
            if enabled:
                print("[Hotkeys] User enabled global hotkeys via Setup tab")
                self._register_global_hotkeys()
            else:
                print("[Hotkeys] User disabled global hotkeys via Setup tab")
                self._unregister_global_hotkeys()
        except Exception as e:
            print(f"[Hotkeys] Error applying global hotkey toggle: {e}")

        # Update status message
        if hasattr(self, "hunt_status"):
            if enabled:
                msg = "Global hotkeys enabled"
                if self.lang == "vi":
                    msg = "Đã bật phím tắt toàn cục"
            else:
                msg = "Global hotkeys disabled"
                if self.lang == "vi":
                    msg = "Đã tắt phím tắt toàn cục"
            self.hunt_status.set(msg)

    def _update_setup_visibility(self):
        """Show/hide Setup tab sections based on current mode."""
        mode = (
            self.setup_mode_var.get() if hasattr(self, "setup_mode_var") else "beginner"
        )

        # NOTE: Setup Wizard button removed - now accessible via Global Hotkeys
        # Hotkey state is managed by _update_hotkeys_state() instead

        if mode == "beginner":
            # Hide advanced sections
            self.adv_frame.grid_remove()
            self.window_frame.grid_remove()
        elif mode == "intermediate":
            # Show advanced hunt settings, hide window settings
            self.adv_frame.grid()
            self.window_frame.grid_remove()
        elif mode == "advanced":
            # Show all sections
            self.adv_frame.grid()
            self.window_frame.grid()

        # Update hotkeys state based on mode
        self._update_hotkeys_state()

    def _update_hotkeys_state(self):
        """Update Setup Wizard hotkey enable/disable state based on UI mode.

        Called when:
        - UI mode changes (beginner/intermediate/advanced)
        - Global hotkeys are re-registered

        Rules:
        - Setup Wizard hotkey: Only active in beginner mode
        - Library Manager hotkey: Always active
        """
        mode = (
            self.setup_mode_var.get() if hasattr(self, "setup_mode_var") else "beginner"
        )

        # Update Setup Wizard hotkey combo state
        if hasattr(self, "wizard_hotkey_combo"):
            if mode == "beginner":
                self.wizard_hotkey_combo.config(state="readonly")
                if hasattr(self, "wizard_hotkey_label"):
                    self.wizard_hotkey_label.config(fg="black")
            else:
                self.wizard_hotkey_combo.config(state="disabled")
                if hasattr(self, "wizard_hotkey_label"):
                    self.wizard_hotkey_label.config(fg="#999")

        # Library Manager hotkey always enabled (no change needed)
        # But we re-register hotkeys to update wizard hotkey state
        if hasattr(self, "hunt_cfg"):
            self._register_global_hotkeys()

    # --- Helpers to attempt closing other windows while respecting unsaved changes ---
    def try_close_setup_wizard(self) -> bool:
        """Attempt to close the setup wizard if open.

        Returns True if wizard not present or was closed. Returns False if close
        was cancelled (e.g., user declined to discard/save changes).
        """
        try:
            wiz = getattr(self, "_setup_wizard_win", None)
            if wiz is None:
                # Try to find dialog child
                for c in list(self.winfo_children()):
                    if getattr(c, "_is_setup_wizard", False):
                        wiz = getattr(c, "_wizard_ref", None) or c
                        break
            if wiz is None:
                return True
            # If wizard exposes attempt_close_from_external use it
            fn = getattr(wiz, "attempt_close_from_external", None)
            if callable(fn):
                try:
                    return bool(fn())
                except Exception:
                    return False
            # Fallback: call destroy (conservative: do not destroy without user confirmation)
            return False
        except Exception:
            return False

    def try_close_library_manager(self) -> bool:
        """Attempt to close library manager if open. Returns True if closed or not present."""
        try:
            lib = getattr(self, "library_manager_win", None)
            if lib is None:
                # Try to find by flag
                for c in list(self.winfo_children()):
                    try:
                        if getattr(c, "_is_library_manager", False):
                            lib = c
                            break
                    except Exception:
                        pass
            if lib is None:
                return True
            # If it provides _on_window_close for external closing, call it
            fn2 = getattr(lib, "_on_window_close", None)
            if callable(fn2):
                try:
                    fn2()
                except Exception:
                    return False
                # Check if window still exists
                try:
                    if hasattr(lib, "winfo_exists") and not lib.winfo_exists():
                        return True
                    # Some implementations destroy child content rather than the widget
                    # Check for a 'destroyed' flag
                    if getattr(lib, "_destroyed", False):
                        return True
                    return False
                except Exception:
                    return False
            return False
        except Exception:
            return False

    def _open_library_manager(self):
        """
        Open Library Manager window for centralized library management.

        Sprint 19 Task #1: Library Manager Window
        """
        from ui.windows.library_manager import LibraryManagerWindow

        def on_library_changes(changes):
            """Handle changes from Library Manager."""
            # Update monsters if changed
            if changes.get("monsters_changed"):
                self.monsters = changes.get("monsters", self.monsters)
                save_monster_library(self.monsters)
                self._refresh_monster_list()  # Refresh Hunt tab monster dropdown

            # Update skills if changed
            if changes.get("skills_changed"):
                self.skills = changes.get("skills", self.skills)
                save_skill_library(self.skills)
                self._refresh_skill_display()  # Refresh Hunt tab skill display

            # Update hunt config if timing applied
            if changes.get("timing_applied"):
                self.hunt_cfg = changes.get("hunt_cfg", self.hunt_cfg)
                save_hunt_config(self.hunt_cfg)
                self._reload_setup_advanced_settings()  # Refresh Setup tab Advanced Settings

            # Update status
            self.hunt_status.set(self._t("library_updated"))

        # Open Library Manager window (single-instance)
        try:
            # Reuse existing instance if present
            existing = getattr(self, "library_manager_win", None)
            if existing is not None and getattr(existing, "winfo_exists", lambda: False)():
                try:
                    # Simple bring-to-front: deiconify, lift
                    try:
                        existing.deiconify()
                        existing.lift()
                        existing.focus_force()
                    except Exception:
                        try:
                            existing.lift(); existing.focus_force()
                        except Exception:
                            pass
                    return
                except Exception:
                    # fallback to creating a new one
                    try:
                        existing.destroy()
                    except Exception:
                        pass

            manager = LibraryManagerWindow(
                parent=self,
                hunt_cfg=self.hunt_cfg,
                monsters=self.monsters,
                skills=load_skill_library(),
                lang=self.lang,
                on_close_callback=on_library_changes,
            )
            # Keep a reference so subsequent hotkey presses reuse the same window
            try:
                self.library_manager_win = manager
            except Exception:
                setattr(self, "library_manager_win", manager)
            # Ensure we clear the reference when it closes
            try:
                def _on_lib_close():
                    try:
                        # call existing close handler on manager which will invoke on_close_callback
                        manager._on_window_close()
                    except Exception:
                        try:
                            manager.destroy()
                        except Exception:
                            pass
                    try:
                        delattr(self, "library_manager_win")
                    except Exception:
                        try:
                            self.library_manager_win = None
                        except Exception:
                            pass

                # Bind WM_DELETE_WINDOW to clear ref
                try:
                    manager.protocol("WM_DELETE_WINDOW", _on_lib_close)
                except Exception:
                    pass
            except Exception:
                pass
            # After creation, show the manager normally (no forcing)
            try:
                manager.deiconify()
                manager.lift()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"),
                f"Failed to open Library Manager: {e}\n\nPlease check console for details.",
            )
            import traceback

            traceback.print_exc()

    def _refresh_skill_display(self):
        """Refresh skill display in Hunt tab after library changes."""
        # Refresh skill slots dropdown options
        if hasattr(self, "_refresh_skill_slots_options"):
            self._refresh_skill_slots_options()

        # Refresh skill list if in advanced mode
        if hasattr(self, "_refresh_skill_list"):
            self._refresh_skill_list()

    def _reload_setup_advanced_settings(self):
        """Reload Advanced Settings values in Setup tab after timing changes."""
        # Update variables with new values from hunt_cfg
        if hasattr(self, "setup_search_interval_var"):
            self.setup_search_interval_var.set(
                f"{self.hunt_cfg.get('search_interval', 0.25):.2f}"
            )
        if hasattr(self, "setup_attack_interval_var"):
            self.setup_attack_interval_var.set(
                f"{self.hunt_cfg.get('attack_interval', 0.15):.2f}"
            )
        if hasattr(self, "setup_lost_timeout_var"):
            self.setup_lost_timeout_var.set(
                f"{self.hunt_cfg.get('lost_timeout_sec', 0.5):.2f}"
            )
        if hasattr(self, "setup_attack_duration_var"):
            self.setup_attack_duration_var.set(
                f"{self.hunt_cfg.get('attack_min_duration_sec', 5.0):.2f}"
            )

    def _open_monster_library(self):
        """Open Monster Library Manager dialog."""
        # TODO: Integrate with existing monster manager
        messagebox.showinfo(
            self._t("monster_section"),
            f"{self._t('monsters_count')}: {len(self.monsters) if hasattr(self, 'monsters') else 0}\n\n"
            f"Monster library management feature coming soon...",
        )

    def _open_skills_library(self):
        """Open Skills Library Manager dialog."""
        # TODO: Integrate with existing skills manager
        messagebox.showinfo(
            self._t("skill_section"),
            f"{self._t('skills_count')}: {len(self.skills) if hasattr(self, 'skills') else 0}\n\n"
            f"Skills library management feature coming soon...",
        )

    def _clear_window_bounds(self):
        """Clear stored window bounds."""
        self.current_window_bounds = None
        self.setup_bounds_display_var.set(self._t("hunt_window_bounds_none"))
        self.hunt_status.set(
            self._t("hunt_window_bounds_cleared")
            if hasattr(self, "hunt_status")
            else "Window bounds cleared"
        )

    def _apply_setup_settings(self, save_to_file=True):
        """Apply all settings from Setup tab to hunt_config and sync to Hunt tab.

        Args:
            save_to_file: If True, save to hunt_config.json immediately.
                         If False, only update self.hunt_cfg (used by on_global_apply to avoid duplicate writes).
        """
        try:
            # Update hunt_cfg with values from Setup tab
            self.hunt_cfg["target_key"] = self.setup_target_key_var.get()
            # attack_keys removed: attack keys are derived from skill_slots (per-skill key assignments)
            self.hunt_cfg["attack_press_ms"] = int(self.setup_press_ms_var.get())
            self.hunt_cfg["target_cycle_delay"] = float(
                self.setup_target_cycle_var.get()
            )
            self.hunt_cfg["search_interval"] = float(
                self.setup_search_interval_var.get()
            )
            self.hunt_cfg["attack_interval"] = float(
                self.setup_attack_interval_var.get()
            )
            self.hunt_cfg["lost_timeout_sec"] = float(self.setup_lost_timeout_var.get())
            self.hunt_cfg["attack_min_duration_sec"] = float(
                self.setup_attack_duration_var.get()
            )
            self.hunt_cfg["template_threshold"] = float(self.setup_threshold_var.get())
            self.hunt_cfg["template_path"] = self.setup_template_var.get()

            # Region
            try:
                l = int(self.setup_reg_l.get()) if self.setup_reg_l.get() else ""
                t = int(self.setup_reg_t.get()) if self.setup_reg_t.get() else ""
                w = int(self.setup_reg_w.get()) if self.setup_reg_w.get() else ""
                h = int(self.setup_reg_h.get()) if self.setup_reg_h.get() else ""
                self.hunt_cfg["region"] = [l, t, w, h]
            except ValueError:
                self.hunt_cfg["region"] = ["", "", "", ""]

            # Save to file only if requested
            if save_to_file:
                with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)

            # Sync to Hunt tab vars if they exist
            if hasattr(self, "target_key_var"):
                self.target_key_var.set(self.hunt_cfg["target_key"])
            # attack_keys removed: UI reads keys from skill_slots directly
            if hasattr(self, "attack_press_var"):
                self.attack_press_var.set(str(self.hunt_cfg["attack_press_ms"]))
            if hasattr(self, "target_cycle_var"):
                self.target_cycle_var.set(str(self.hunt_cfg["target_cycle_delay"]))
            if hasattr(self, "search_interval_var"):
                self.search_interval_var.set(str(self.hunt_cfg["search_interval"]))
            if hasattr(self, "attack_interval_var"):
                self.attack_interval_var.set(str(self.hunt_cfg["attack_interval"]))
            if hasattr(self, "lost_timeout_var"):
                self.lost_timeout_var.set(str(self.hunt_cfg["lost_timeout_sec"]))
            if hasattr(self, "attack_duration_var"):
                self.attack_duration_var.set(
                    str(self.hunt_cfg["attack_min_duration_sec"])
                )
            if hasattr(self, "template_var"):
                self.template_var.set(self.hunt_cfg["template_path"])
            if hasattr(self, "reg_l"):
                region = self.hunt_cfg["region"]
                self.reg_l.set(str(region[0]) if region[0] != "" else "")
                self.reg_t.set(str(region[1]) if region[1] != "" else "")
                self.reg_w.set(str(region[2]) if region[2] != "" else "")
                self.reg_h.set(str(region[3]) if region[3] != "" else "")

            # Show success feedback only when saving directly (not called from on_global_apply)
            if save_to_file:
                # Update status
                if hasattr(self, "hunt_status"):
                    self.hunt_status.set(self._t("settings_applied_success"))

                # Show success message
                messagebox.showinfo(
                    self._t("success_title"), self._t("settings_applied_message")
                )

        except ValueError as e:
            messagebox.showerror(
                self._t("error_title"),
                self._t("error_invalid_number").format(field=str(e)),
            )
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), f"Failed to apply settings: {e}"
            )

    # Phase 3: Multi-Monster Support Handlers
    def _load_monster_rotation_list(self):
        """Load monster_list from hunt_config into UI."""
        saved_list = self.hunt_cfg.get("monster_list", [])
        self.monster_rotation_list = []

        for item in saved_list:
            if isinstance(item, dict):
                self.monster_rotation_list.append(
                    {
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "enabled": item.get("enabled", True),
                    }
                )

        # If empty, populate from monsters library for convenience
        if not self.monster_rotation_list and self.monsters:
            for idx, monster in enumerate(self.monsters[:5]):  # Top 5 monsters
                self.monster_rotation_list.append(
                    {
                        "name": monster["name"],
                        "priority": idx + 1,
                        "enabled": False,  # Disabled by default
                    }
                )

    def _load_training_monster_list(self):
        """Sprint 22 Patch 2: Load training_monster_list from hunt_config.

        This is a separate list for training dummies (Cọc gỗ, quái bất tử).
        When this list has items, training mode is auto-enabled.

        Migration: Auto-detect and move "Coc go" variants from monster_list to training_monster_list.
        """
        saved_list = self.hunt_cfg.get("training_monster_list", [])
        self.training_monster_list = []

        for item in saved_list:
            if isinstance(item, dict):
                self.training_monster_list.append(
                    {
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "enabled": item.get("enabled", True),
                        "training_mode": True,  # Always true for training list
                    }
                )

        # Migration: Move "Coc go" from monster_rotation_list to training_monster_list
        # Check if monster_rotation_list has "Coc go" variants
        if hasattr(self, "monster_rotation_list"):
            coc_go_items = []
            remaining_items = []

            for monster in self.monster_rotation_list:
                monster_name = monster.get("name", "").lower()
                # Detect "Coc go", "Cọc gỗ", "coc_go", etc. (case-insensitive, với/không dấu)
                if "coc" in monster_name and "go" in monster_name:
                    # Move to training list
                    coc_go_items.append(
                        {
                            "name": monster.get("name", ""),
                            "priority": monster.get("priority", 1),
                            "enabled": monster.get("enabled", True),
                            "training_mode": True,
                        }
                    )
                    print(
                        f"[Migration] Found '{monster.get('name')}' in monster_list → moving to training_monster_list"
                    )
                else:
                    remaining_items.append(monster)

            # Update lists
            if coc_go_items:
                # Add migrated items to training list (avoid duplicates)
                existing_names = {m["name"] for m in self.training_monster_list}
                for item in coc_go_items:
                    if item["name"] not in existing_names:
                        self.training_monster_list.append(item)
                        print(
                            f"[Migration] ➕ Added '{item['name']}' to training_monster_list"
                        )

                # Remove from normal list
                self.monster_rotation_list = remaining_items
                print(
                    f"[Migration] ✂️ Removed {len(coc_go_items)} items from monster_list"
                )

                # Mark config as modified to save migration
                self._config_migrated = True

        # Auto-enable training mode if training list has items
        if hasattr(self, "training_mode_var"):
            self.training_mode_var.set(len(self.training_monster_list) > 0)

    def _refresh_monster_rotation_list(self):
        """Refresh the monster rotation listbox display.

        Sprint 22 Patch 2: Show training_monster_list when training mode active,
        otherwise show monster_rotation_list (normal monsters).
        """
        if not hasattr(self, "monster_rotation_listbox"):
            return

        self.monster_rotation_listbox.delete(0, tk.END)

        # Sprint 22 Patch 2: Auto-detect training mode from training_monster_list
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        # Update frame title to show current mode
        self._update_monster_frame_title(has_training_list)

        # Choose which list to display
        if has_training_list:
            # Training mode: Show training_monster_list
            display_list = self.training_monster_list
        else:
            # Normal mode: Show monster_rotation_list
            display_list = self.monster_rotation_list

        for item in display_list:
            check = "☑" if item["enabled"] else "☐"
            display = f"{check} {item['name']}"
            if self.hunt_cfg.get("rotation_mode") == "priority":
                display += f" (P{item['priority']})"
            # Add training dummy indicator
            if item.get("training_mode", False):
                display += " 🎯"
            self.monster_rotation_listbox.insert(tk.END, display)

        self._update_monster_status()
        self._update_rotation_mode_description()

        # Update button states if in training mode
        if hasattr(self, "training_mode_var"):
            self._update_training_mode_buttons()

    def _update_monster_frame_title(self, is_training_mode: bool):
        """Sprint 22 Patch 2: Update frame title to indicate current mode.

        Args:
            is_training_mode: True if showing training_monster_list
        """
        if not hasattr(self, "monster_frame"):
            return

        if is_training_mode:
            # Training mode: Show with special indicator
            title_en = "🎯 Training Dummies (Practice Mode)"
            title_vi = "🎯 Cọc Gỗ Luyện Tập (Chế độ luyện skill)"
            title = title_vi if self.lang == "vi" else title_en

            # Change listbox background to indicate training mode
            if hasattr(self, "monster_rotation_listbox"):
                self.monster_rotation_listbox.config(bg="#FFF8E1")  # Light amber/yellow

            # Show hint for switching back to normal mode
            if hasattr(self, "training_mode_hint_var"):
                hint_en = "💡 To switch back to normal monsters: Delete all training dummies (select + Del key)"
                hint_vi = "💡 Để chuyển về danh sách quái thường: Xóa hết cọc gỗ (chọn + phím Del)"
                self.training_mode_hint_var.set(
                    hint_vi if self.lang == "vi" else hint_en
                )
        else:
            # Normal mode: Regular monsters
            title = self._t("hunt_monsters")

            # Reset listbox background to default
            if hasattr(self, "monster_rotation_listbox"):
                self.monster_rotation_listbox.config(bg="white")

            # Clear hint
            if hasattr(self, "training_mode_hint_var"):
                self.training_mode_hint_var.set("")

        self.monster_frame.config(text=title)

    def _update_monster_status(self):
        """Update current monster hunting status display.

        Sprint 22 Patch 2: Show different status for training mode.
        """
        if not hasattr(self, "monster_status_var"):
            return

        # Check which mode we're in
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Training mode: Show training list status
            enabled = [m for m in self.training_monster_list if m["enabled"]]
            if not enabled:
                status_en = "🎯 No training dummy selected"
                status_vi = "🎯 Chưa chọn cọc gỗ nào"
                self.monster_status_var.set(
                    status_vi if self.lang == "vi" else status_en
                )
                return

            # Show training mode status
            count = len(enabled)
            status_en = (
                f"🎯 Training Mode: {count} dummy"
                if count == 1
                else f"🎯 Training Mode: {count} dummies"
            )
            status_vi = f"🎯 Chế độ luyện tập: {count} cọc gỗ"
            self.monster_status_var.set(status_vi if self.lang == "vi" else status_en)
        else:
            # Normal mode: Show normal monster status
            enabled = [m for m in self.monster_rotation_list if m["enabled"]]
            if not enabled:
                self.monster_status_var.set(self._t("monster_none_selected"))
                return

            mode = self.hunt_cfg.get("rotation_mode", "sequence")
            current_idx = self.hunt_cfg.get("current_monster_index", 0)

            if mode == "sequence":
                if current_idx < len(enabled):
                    current = enabled[current_idx]
                    self.monster_status_var.set(
                        f"Current: {current['name']} | Sequence: {current_idx+1}/{len(enabled)}"
                    )
                else:
                    self.monster_status_var.set(f"Sequence: {len(enabled)} monsters")
            else:  # priority
                sorted_monsters = sorted(enabled, key=lambda m: m["priority"])
                current = sorted_monsters[0]
                self.monster_status_var.set(
                    f"Priority: {current['name']} (P{current['priority']}) | {len(enabled)} total"
                )

    def _update_rotation_mode_description(self):
        """Update rotation mode description."""
        if not hasattr(self, "rotation_desc_var"):
            return

        mode = self.rotation_mode_var.get()
        if mode == "sequence":
            self.rotation_desc_var.set("Hunt monsters in order, cycle through list")
        elif mode == "priority":
            self.rotation_desc_var.set("Always hunt highest priority (lowest number)")

    def _on_rotation_mode_changed(self, event=None):
        """Handle rotation mode change."""
        mode = self.rotation_mode_var.get()
        self.hunt_cfg["rotation_mode"] = mode
        self._refresh_monster_rotation_list()
        self.hunt_status.set(f"Rotation mode: {mode}")

    def _on_training_mode_toggled(self):
        """Handle training mode checkbox toggle (Sprint 22 Patch 1).

        When enabled:
        - Filter monster list to show only training dummies (training_mode=true)
        - Update status indicator
        - Save state to hunt_config.json

        When disabled:
        - Show all monsters in rotation list
        - Clear status indicator
        """
        is_enabled = self.training_mode_var.get()

        # Update hunt_cfg
        self.hunt_cfg["training_mode_enabled"] = is_enabled

        # Save to config file
        try:
            with open(HUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save training_mode_enabled: {e}")

        # Update UI feedback
        if is_enabled:
            self.training_mode_status_var.set(self._t("training_mode_active"))
            self.hunt_status.set(self._t("training_mode_active"))
        else:
            self.training_mode_status_var.set("")
            self.hunt_status.set(self._t("training_mode_disabled"))

        # Refresh monster rotation list (will filter if training mode is on)
        self._refresh_monster_rotation_list()

        # Show/hide skill stats frame if it exists
        if hasattr(self, "skill_stats_frame"):
            if is_enabled:
                self.skill_stats_frame.grid()
            else:
                self.skill_stats_frame.grid_remove()

        # Update button states and tooltips
        self._update_training_mode_buttons()

    def _update_training_mode_buttons(self):
        """Update monster control buttons based on training mode state.

        Training Mode ON:
        - Add button: Shows finish.ico if dummy set, else add.ico with training tooltip
        - Add button: Disabled if training dummy already in list
        - Up/Down buttons: Disabled (no rotation needed)

        Training Mode OFF:
        - Add button: Shows add.ico with normal tooltip
        - Add button: Always enabled
        - Up/Down buttons: Enabled
        """
        if not hasattr(self, "btn_add_monster"):
            return

        is_training = self.training_mode_var.get()
        has_training_dummy = any(
            m.get("training_mode", False) for m in self.monster_rotation_list
        )

        if is_training:
            # Training mode: Update add button
            if has_training_dummy:
                # Dummy already set - show accept icon and disable
                try:
                    # Use size=16 to match compact button
                    accept_icon = self._icon("accept", "✓", size=16)
                    if isinstance(accept_icon, str):
                        self.btn_add_monster.config(text=accept_icon, state="disabled")
                    else:
                        self.btn_add_monster.config(
                            image=accept_icon, text="", state="disabled"
                        )
                except Exception:
                    self.btn_add_monster.config(text="✓", state="disabled")

                # Update tooltip for locked state
                tooltip_text = self._t("tooltip_add_monster_locked")
                tooltip = getattr(self.btn_add_monster, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(self.btn_add_monster, "_tooltip")
                    except Exception:
                        pass
                self._create_tooltip(self.btn_add_monster, tooltip_text)
            else:
                # No dummy yet - show add icon and enable
                try:
                    # Use size=16 to match compact button
                    add_icon = self._icon("add", "➕", size=16)
                    if isinstance(add_icon, str):
                        self.btn_add_monster.config(text=add_icon, state="normal")
                    else:
                        self.btn_add_monster.config(
                            image=add_icon, text="", state="normal"
                        )
                except Exception:
                    self.btn_add_monster.config(text="➕", state="normal")

                # Update tooltip for training helper
                tooltip_text = self._t("tooltip_add_monster_training")
                tooltip = getattr(self.btn_add_monster, "_tooltip", None)
                if tooltip is not None:
                    try:
                        tooltip.destroy()
                    except Exception:
                        pass
                    try:
                        delattr(self.btn_add_monster, "_tooltip")
                    except Exception:
                        pass
                self._create_tooltip(self.btn_add_monster, tooltip_text)

            # Disable priority reorder buttons with locked icon (white on gray)
            # Use size=16 to match SMALL buttons (36px)
            try:
                locked_icon = self._icon("locked", "🔒", size=16, color="#FFFFFF")
                for btn in [self.btn_move_up, self.btn_move_down]:
                    # IMPORTANT: Keep original bg colors when disabled
                    original_bg = (
                        UI.BTN_NEUTRAL_BG
                        if btn == self.btn_move_up
                        else UI.BTN_NEUTRAL_BG
                    )
                    btn.config(state="disabled", bg=original_bg)
                    if isinstance(locked_icon, str):
                        btn.config(text=locked_icon)
                    else:
                        btn.config(image=locked_icon, text="")
            except Exception:
                self.btn_move_up.config(
                    state="disabled", text="🔒", bg=UI.BTN_NEUTRAL_BG
                )
                self.btn_move_down.config(
                    state="disabled", text="🔒", bg=UI.BTN_NEUTRAL_BG
                )

            # Update tooltips for disabled buttons
            for btn in [self.btn_move_up, self.btn_move_down]:
                # Safely destroy any existing tooltip then create a new one
                try:
                    self._destroy_widget_tooltip(btn)
                except Exception:
                    pass
                self._create_tooltip(btn, self._t("tooltip_reorder_locked"))
        else:
            # Normal mode: Restore defaults
            try:
                # Use size=16 to match compact button
                add_icon = self._icon("add", "➕", size=16)
                if isinstance(add_icon, str):
                    self.btn_add_monster.config(text=add_icon, state="normal")
                else:
                    self.btn_add_monster.config(image=add_icon, text="", state="normal")
            except Exception:
                self.btn_add_monster.config(text="➕", state="normal")

            # Restore normal tooltip
            try:
                self._destroy_widget_tooltip(self.btn_add_monster)
            except Exception:
                pass
            self._create_tooltip(
                self.btn_add_monster, self._t("tooltip_add_monster_normal")
            )

            # Enable priority reorder buttons with original icons and colors (both blue for consistency)
            try:
                # Use size=16 to match SMALL buttons
                up_icon = self._icon("up", "↑", size=16)
                down_icon = self._icon("down", "↓", size=16)

                if isinstance(up_icon, str):
                    self.btn_move_up.config(
                        state="normal",
                        text=up_icon,
                        bg=UI.BTN_INFO_BG,  # Blue for consistency
                        fg=UI.BTN_INFO_FG,
                    )
                else:
                    self.btn_move_up.config(
                        state="normal",
                        image=up_icon,
                        text="",
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG,
                    )

                if isinstance(down_icon, str):
                    self.btn_move_down.config(
                        state="normal",
                        text=down_icon,
                        bg=UI.BTN_INFO_BG,  # Blue for consistency
                        fg=UI.BTN_INFO_FG,
                    )
                else:
                    self.btn_move_down.config(
                        state="normal",
                        image=down_icon,
                        text="",
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG,
                    )
            except Exception:
                self.btn_move_up.config(
                    state="normal",
                    text="↑",
                    bg=UI.BTN_INFO_BG,  # Blue for consistency
                    fg=UI.BTN_INFO_FG,
                )
                self.btn_move_down.config(
                    state="normal",
                    text="↓",
                    bg=UI.BTN_INFO_BG,  # Blue for consistency
                    fg=UI.BTN_INFO_FG,
                )

            # Restore normal tooltips
            try:
                self._destroy_widget_tooltip(self.btn_move_up)
            except Exception:
                pass
            self._create_tooltip(self.btn_move_up, self._t("tooltip_move_up"))

            try:
                self._destroy_widget_tooltip(self.btn_move_down)
            except Exception:
                pass
            self._create_tooltip(self.btn_move_down, self._t("tooltip_move_down"))

    def _on_monster_toggle(self, event=None):
        """Toggle monster enabled state on double-click.

        Sprint 22 Patch 2: Support both normal and training lists.
        """
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Determine which list we're working with
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Toggle in training_monster_list
            if idx < len(self.training_monster_list):
                self.training_monster_list[idx]["enabled"] = (
                    not self.training_monster_list[idx]["enabled"]
                )
        else:
            # Toggle in monster_rotation_list
            if idx < len(self.monster_rotation_list):
                self.monster_rotation_list[idx]["enabled"] = (
                    not self.monster_rotation_list[idx]["enabled"]
                )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx)

    def _on_monster_list_select(self, event=None):
        """Handle monster list selection for preview."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(self.monster_rotation_list):
            monster = self.monster_rotation_list[idx]
            # Optional: Show monster template preview or stats
            pass

    def _show_monster_context_menu(self, event):
        """Sprint 22 Patch 2: Show context menu on right-click.

        Displays menu at mouse position only if an item is selected.
        """
        # Check if there's a selection at the click position
        try:
            self.monster_rotation_listbox.selection_clear(0, tk.END)
            index = self.monster_rotation_listbox.nearest(event.y)
            self.monster_rotation_listbox.selection_set(index)
            self.monster_rotation_listbox.activate(index)

            # Show context menu at mouse position
            self.monster_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Release the grab
            self.monster_context_menu.grab_release()

    def _on_monster_delete_from_list(self, event=None):
        """Sprint 22 Patch 2: Delete selected monster from rotation list.

        Delete key removes item from current list (normal or training).
        If training_monster_list becomes empty, auto-switch to normal mode.
        """
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Determine which list we're working with
        has_training_list = (
            hasattr(self, "training_monster_list")
            and len(self.training_monster_list) > 0
        )

        if has_training_list:
            # Delete from training_monster_list
            if idx < len(self.training_monster_list):
                monster_name = self.training_monster_list[idx]["name"]

                # Confirm deletion
                confirm_en = f"Remove '{monster_name}' from training list?"
                confirm_vi = f"Xóa '{monster_name}' khỏi danh sách luyện tập?"
                confirm_msg = confirm_vi if self.lang == "vi" else confirm_en

                if not messagebox.askyesno(self._t("confirm_title"), confirm_msg):
                    return

                del self.training_monster_list[idx]

                # If training list is now empty, auto-switch to normal mode
                if len(self.training_monster_list) == 0:
                    hint_en = "💡 Training list cleared. Switched back to normal monster list."
                    hint_vi = "💡 Đã xóa hết cọc gỗ. Chuyển về danh sách quái thường."
                    messagebox.showinfo(
                        self._t("info_title"), hint_vi if self.lang == "vi" else hint_en
                    )
        else:
            # Delete from monster_rotation_list
            if idx < len(self.monster_rotation_list):
                monster_name = self.monster_rotation_list[idx]["name"]

                confirm_en = f"Remove '{monster_name}' from rotation list?"
                confirm_vi = f"Xóa '{monster_name}' khỏi danh sách săn?"
                confirm_msg = confirm_vi if self.lang == "vi" else confirm_en

                if not messagebox.askyesno(self._t("confirm_title"), confirm_msg):
                    return

                del self.monster_rotation_list[idx]

        self._refresh_monster_rotation_list()

        # Select next item if available
        if idx < self.monster_rotation_listbox.size():
            self.monster_rotation_listbox.selection_set(idx)
        elif self.monster_rotation_listbox.size() > 0:
            self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_up(self):
        """Move selected monster up in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        # Swap with previous
        self.monster_rotation_list[idx], self.monster_rotation_list[idx - 1] = (
            self.monster_rotation_list[idx - 1],
            self.monster_rotation_list[idx],
        )

        # Update priorities if in priority mode
        if self.hunt_cfg.get("rotation_mode") == "priority":
            (
                self.monster_rotation_list[idx]["priority"],
                self.monster_rotation_list[idx - 1]["priority"],
            ) = (
                self.monster_rotation_list[idx - 1]["priority"],
                self.monster_rotation_list[idx]["priority"],
            )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx - 1)

    def _on_monster_move_down(self):
        """Move selected monster down in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] >= len(self.monster_rotation_list) - 1:
            return

        idx = selection[0]
        # Swap with next
        self.monster_rotation_list[idx], self.monster_rotation_list[idx + 1] = (
            self.monster_rotation_list[idx + 1],
            self.monster_rotation_list[idx],
        )

        # Update priorities if in priority mode
        if self.hunt_cfg.get("rotation_mode") == "priority":
            (
                self.monster_rotation_list[idx]["priority"],
                self.monster_rotation_list[idx + 1]["priority"],
            ) = (
                self.monster_rotation_list[idx + 1]["priority"],
                self.monster_rotation_list[idx]["priority"],
            )

        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx + 1)

    def _on_monster_add_smart(self):
        """Smart add monster with autocomplete and fuzzy matching hints."""
        dialog = tk.Toplevel(self)
        dialog.title(self._t("monster_add_title"))
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        container = tk.Frame(dialog, padx=16, pady=16)
        container.pack(fill="both", expand=True)

        # Title + hint
        title_label = tk.Label(
            container,
            text=self._t("monster_add_instruction"),
            font=("Arial", 10, "bold"),
        )
        title_label.pack(anchor="w", pady=(0, 8))

        hint_text = self._t("monster_add_hint")
        hint_label = tk.Label(
            container,
            text=hint_text,
            fg="#666",
            font=("Arial", 8),
            wraplength=450,
            justify="left",
        )
        hint_label.pack(anchor="w", pady=(0, 12))

        # Search entry with real-time suggestions
        search_frame = tk.Frame(container)
        search_frame.pack(fill="x", pady=(0, 8))

        tk.Label(search_frame, text=self._t("monster_name")).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=(8, 0), fill="x", expand=True)
        search_entry.focus_set()

        # Suggestion listbox
        suggest_frame = tk.LabelFrame(
            container, text=self._t("monster_suggestions"), padx=8, pady=8
        )
        suggest_frame.pack(fill="both", expand=True, pady=(0, 8))

        suggest_listbox = tk.Listbox(suggest_frame, height=10, exportselection=False)
        suggest_listbox.pack(side="left", fill="both", expand=True)

        suggest_scroll = tk.Scrollbar(
            suggest_frame, orient="vertical", command=suggest_listbox.yview
        )
        suggest_scroll.pack(side="right", fill="y")
        suggest_listbox.config(yscrollcommand=suggest_scroll.set)

        # Match info label
        match_info_var = tk.StringVar(value="")
        match_info_label = tk.Label(
            container,
            textvariable=match_info_var,
            fg="#2196F3",
            font=("Arial", 8),
            wraplength=450,
            justify="left",
        )
        match_info_label.pack(fill="x", pady=(0, 8))

        # Populate initial suggestions (filtered by training mode if active)
        def update_suggestions(*args):
            """Update suggestions based on search text with fuzzy matching."""
            import re

            search_text = search_var.get().strip()

            suggest_listbox.delete(0, tk.END)
            match_info_var.set("")

            # Sprint 22 Patch 2: Auto-detect training mode based on training_monster_list
            # Check if training_monster_list exists and has items
            has_training_list = (
                hasattr(self, "training_monster_list")
                and len(self.training_monster_list) > 0
            )
            is_training_mode = (
                has_training_list  # Auto-enable if training list has items
            )

            available_monsters = self.monsters

            if is_training_mode:
                # Training mode: Only show training dummies
                available_monsters = [
                    m for m in self.monsters if m.get("training_mode", False)
                ]
                if not available_monsters:
                    # Sprint 22 Patch 2: Only show warning if training_monster_list is EMPTY
                    # If user already added training dummies to training_monster_list, don't show warning
                    if not has_training_list:
                        debug_msg = f"⚠️ {self._t('no_training_dummies')}"
                        if self.monsters:
                            debug_msg += (
                                f"\n📚 Library has {len(self.monsters)} monsters total"
                            )
                            training_count = sum(
                                1
                                for m in self.monsters
                                if m.get("training_mode", False)
                            )
                            debug_msg += f"\n🎯 Training dummies: {training_count}"
                        match_info_var.set(debug_msg)
                    return

            if not search_text:
                # Show all available monsters (filtered or not)
                for monster in available_monsters:
                    suggest_listbox.insert(tk.END, monster["name"])
                if is_training_mode:
                    match_info_var.set(
                        f"🎯 {self._t('training_dummy_filter')} | {len(available_monsters)} dummy"
                    )
                else:
                    match_info_var.set(
                        f"💡 {self._t('monster_showing_all').format(count=len(available_monsters))}"
                    )
                return

            # Fuzzy search (on filtered list)
            search_clean = re.sub(r"[^a-z0-9\s]", "", search_text.lower()).strip()
            matches = []

            for monster in available_monsters:
                name = monster["name"]
                name_clean = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()

                # Score matches: exact > starts with > contains
                if search_clean == name_clean:
                    matches.append((name, 100))  # Exact match
                elif name_clean.startswith(search_clean):
                    matches.append((name, 80))  # Starts with
                elif search_clean in name_clean:
                    matches.append((name, 60))  # Contains
                elif any(word.startswith(search_clean) for word in name_clean.split()):
                    matches.append((name, 40))  # Word starts with

            # Sort by score (descending)
            matches.sort(key=lambda x: x[1], reverse=True)

            # Display matches
            for name, score in matches:
                suggest_listbox.insert(tk.END, name)

            # Update match info
            if matches:
                match_info_var.set(
                    f"✓ {self._t('monster_found_matches').format(count=len(matches))} | "
                    + self._t("monster_fuzzy_hint")
                )
            else:
                match_info_var.set(
                    f"⚠ {self._t('monster_no_matches')} | "
                    + self._t("monster_try_hint")
                )

        search_var.trace_add("write", update_suggestions)
        update_suggestions()  # Initial population

        # Double-click or Enter to select
        def on_select(event=None):
            selection = suggest_listbox.curselection()
            if not selection:
                return

            monster_name = suggest_listbox.get(selection[0])

            # Sprint 22 Patch 2: Check duplicate based on auto-detected training mode
            has_training_list = (
                hasattr(self, "training_monster_list")
                and len(self.training_monster_list) > 0
            )
            is_training_mode = has_training_list

            # Find monster in library to get training_mode flag
            monster_data = next(
                (m for m in self.monsters if m["name"] == monster_name), None
            )
            training_flag = (
                monster_data.get("training_mode", False) if monster_data else False
            )

            # Determine which list to check and add to
            if training_flag:
                # Training dummy: add to training_monster_list
                check_list = self.training_monster_list
                target_list = "training"
            else:
                # Normal monster: add to monster_rotation_list
                check_list = self.monster_rotation_list
                target_list = "normal"

            if any(m["name"] == monster_name for m in check_list):
                messagebox.showinfo(
                    self._t("info_title"),
                    self._t("monster_already_in_list").format(name=monster_name),
                    parent=dialog,
                )
                return

            # Add to appropriate list
            new_priority = len(check_list) + 1

            if target_list == "training":
                self.training_monster_list.append(
                    {
                        "name": monster_name,
                        "priority": new_priority,
                        "enabled": True,
                        "training_mode": True,
                    }
                )
                # Auto-enable training mode
                if hasattr(self, "training_mode_var"):
                    self.training_mode_var.set(True)
            else:
                self.monster_rotation_list.append(
                    {
                        "name": monster_name,
                        "priority": new_priority,
                        "enabled": True,
                        "training_mode": False,
                    }
                )

            self._refresh_monster_rotation_list()
            dialog.destroy()

        suggest_listbox.bind("<Double-Button-1>", on_select)
        search_entry.bind("<Return>", on_select)

        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame,
            text=self._t("add_button"),
            command=on_select,
            font=("Arial", 9, "bold"),
            fg="#4CAF50",
        ).pack(side="left")
        tk.Button(
            btn_frame, text=self._t("cancel_button"), command=dialog.destroy
        ).pack(side="left", padx=(8, 0))

    def on_hunt_browse_template(self):
        path = filedialog.askopenfilename(
            title="Select template image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if path:
            self.template_var.set(path)

    def on_hunt_pick_corner(self, which: str):
        def do_pick():
            for i in range(3, 0, -1):
                self.hunt_status.set(
                    f"Pick {which.upper()} in {i}... Move mouse to corner"
                )
                time.sleep(1)
            try:
                pg = pyautogui
                if pg is None:
                    raise RuntimeError("pyautogui not available")
                x, y = pg.position()
                if which == "tl":
                    self.reg_l.set(str(x))
                    self.reg_t.set(str(y))
                else:
                    # compute width/height using TL if present
                    try:
                        l = int(self.reg_l.get())
                        t = int(self.reg_t.get())
                        w = max(1, x - l)
                        h = max(1, y - t)
                        self.reg_w.set(str(w))
                        self.reg_h.set(str(h))
                    except Exception:
                        self.reg_w.set("")
                        self.reg_h.set("")
                self.hunt_status.set(f"Picked {which.upper()} at ({x},{y})")
            except Exception as e:
                self.hunt_status.set(f"Pick error: {e!r}")

        threading.Thread(target=do_pick, daemon=True).start()

    def on_hunt_find_windows(self):
        """Find and populate window list in combobox with auto-selection."""
        # Enumerate windows using WinAPI to get hwnd and PID
        items = self._enum_windows()

        # Filter for Cabal windows (check saved window_title or default to 'cabal')
        saved_title = self.hunt_cfg.get("window_title", "cabal").strip().lower()
        candidates = [
            w
            for w in items
            if saved_title in w["title"].lower()
            or "cabal" in w["title"].lower()
            or "cabal" in (w["proc"] or "").lower()
        ]

        # Store window items
        self.win_items = candidates

        # Populate combobox (show only window titles without PID)
        self.win_combo["values"] = [
            w['title'] for w in candidates
        ]

        if not candidates:
            messagebox.showinfo(self._t("find_windows"), self._t("no_windows"))
            return

        # Auto-select window matching saved PID if available
        saved_pid = self.hunt_cfg.get("window_pid")
        selected_idx = 0

        if saved_pid:
            for i, w in enumerate(candidates):
                if w["pid"] == saved_pid:
                    selected_idx = i
                    break

        # Select in combobox WITHOUT triggering bring-to-front
        self._skip_auto_bring = True
        self.win_combo.current(selected_idx)
        self.hunt_selected = candidates[selected_idx]
        self._skip_auto_bring = False

        self.hunt_status.set(
            self._t("selected_window").format(title=candidates[selected_idx]["title"])
        )

    def on_hunt_refresh_windows(self):
        """Refresh window list manually (PATCH 9)."""
        # Clear existing selection
        self.win_items = []
        self.win_combo.set("")

        # Re-enumerate and populate windows
        self.on_hunt_find_windows()

        # Update status
        count = len(self.win_items) if hasattr(self, "win_items") else 0
        self.hunt_status.set(f"🔄 Refreshed: {count} window(s) found")

    def on_hunt_bring_front(self):
        """Bring selected window to front."""
        # Get hwnd from hunt_selected
        hwnd = None
        if hasattr(self, "hunt_selected") and self.hunt_selected:
            hwnd = self.hunt_selected.get("hwnd")

        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            # Fallback to title-based search
            title = self.hunt_cfg.get("window_title", "Cabal").strip()
            ok = self._bring_window_to_front(title)

        self.hunt_status.set(self._t("bring_ok") if ok else self._t("bring_fail"))

    def on_hunt_bring_front_below_app(self):
        """Bring game window to front but keep app on top of it."""
        # Get hwnd from hunt_selected
        hwnd = None
        if hasattr(self, "hunt_selected") and self.hunt_selected:
            hwnd = self.hunt_selected.get("hwnd")

        # First bring game window to front
        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            # Fallback to title-based search
            title = self.hunt_cfg.get("window_title", "Cabal").strip()
            ok = self._bring_window_to_front(title)

        # Then bring app back on top
        if ok:
            time.sleep(0.1)  # Small delay to ensure game window is up
            self.lift()
            self.focus_force()
            self.attributes("-topmost", True)
            self.update()
            self.after(
                100, lambda: self.attributes("-topmost", False)
            )  # Disable topmost after 100ms

        self.hunt_status.set(self._t("bring_ok") if ok else self._t("bring_fail"))

    def on_window_combo_selected(self, _evt=None):
        """Handle window selection from combobox - auto bring to front BELOW app."""
        try:
            # Skip if this is auto-selection from find_windows
            if self._skip_auto_bring:
                return

            idx = self.win_combo.current()
            if idx < 0 or idx >= len(self.win_items):
                return

            item = self.win_items[idx]
            self.hunt_selected = item

            # Auto bring window to front BUT keep app on top
            ok = self._bring_window_to_front_by_hwnd(item["hwnd"])

            if ok:
                # Bring app back on top after game window
                time.sleep(0.1)
                self.lift()
                self.focus_force()
                self.attributes("-topmost", True)
                self.update()
                self.after(100, lambda: self.attributes("-topmost", False))

                self.hunt_status.set(
                    self._t("selected_window").format(title=item["title"])
                )
            else:
                self.hunt_status.set(self._t("bring_fail"))
        except Exception as e:
            print(f"Window combo selection error: {e}")

    def on_window_selected(self, _evt=None):
        """Legacy handler - no longer used since listbox removed."""
        pass

    def _bring_window_to_front(self, title_sub: str) -> bool:
        try:
            import pygetwindow as gw
        except Exception:
            return False
        try:
            wins = [w for w in gw.getAllTitles() if title_sub.lower() in w.lower()]
            if not wins:
                return False
            win = gw.getWindowsWithTitle(wins[0])[0]
            win.activate()
            return True
        except Exception:
            return False

    def _bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        try:
            user32 = ctypes.windll.user32
            hwnd_obj = wintypes.HWND(int(hwnd))
            SW_SHOW = 5
            SW_RESTORE = 9

            if user32.IsIconic(hwnd_obj):
                user32.ShowWindow(hwnd_obj, SW_RESTORE)
            else:
                user32.ShowWindow(hwnd_obj, SW_SHOW)

            res = user32.SetForegroundWindow(hwnd_obj)
            if not res:
                user32.BringWindowToTop(hwnd_obj)
                res = user32.SetForegroundWindow(hwnd_obj)
            time.sleep(0.02)
            return bool(res and user32.GetForegroundWindow() == hwnd_obj.value)
        except Exception:
            return False

    def _bring_window_to_front_by_pid(self, pid: int) -> bool:
        try:
            items = self._enum_windows()
            for w in items:
                try:
                    if int(w["pid"]) == int(pid):
                        return self._bring_window_to_front_by_hwnd(int(w["hwnd"]))
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _enum_windows(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, wintypes.HWND, wintypes.LPARAM
        )
        IsWindowVisible = user32.IsWindowVisible
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId

        results = []
        # optional: process name via psutil
        try:
            import psutil  # type: ignore
        except Exception:
            psutil = None  # type: ignore

        def callback(hwnd, lParam):
            try:
                if not IsWindowVisible(hwnd):
                    return True
                length = GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True
                buf = ctypes.create_unicode_buffer(length + 1)
                GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if not title:
                    return True
                pid = wintypes.DWORD()
                GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                pid_val = int(pid.value)
                proc_name = None
                if psutil is not None:
                    try:
                        p = psutil.Process(pid_val)
                        proc_name = p.name()
                    except Exception:
                        proc_name = None
                results.append(
                    {
                        "hwnd": int(hwnd),
                        "pid": pid_val,
                        "title": title,
                        "proc": proc_name,
                    }
                )
            except Exception:
                pass
            return True

        EnumWindows(EnumWindowsProc(callback), 0)
        return results

    def _hunt_locate_target(self, cfg):
        """
        Try to locate target using templates[] or fallback to template_path.
        Uses template_matcher.locate_template() for accurate confidence tracking with OpenCV.
        Returns tuple (box, match_info) or (None, None).
        """
        # Try new templates[] array first
        templates = cfg.get("templates", [])
        if templates:
            window_bounds = cfg.get("window_bounds")
            for tmpl in templates:
                path = tmpl.get("path", "")
                if not path or not Path(path).exists():
                    continue

                threshold = tmpl.get("threshold", 0.85)

                # Determine region
                region_strategy = tmpl.get("region_strategy", "window")
                if region_strategy == "custom" and tmpl.get("region"):
                    reg_dict = tmpl["region"]
                    region = (
                        reg_dict.get("left", 0),
                        reg_dict.get("top", 0),
                        reg_dict.get("width", 0),
                        reg_dict.get("height", 0),
                    )
                elif window_bounds:
                    wb = window_bounds
                    region = (
                        wb.get("left", 0),
                        wb.get("top", 0),
                        wb.get("width", 0),
                        wb.get("height", 0),
                    )
                else:
                    region = None

                # Use template_matcher for accurate confidence tracking
                box, confidence = locate_template(
                    path, region, threshold, method="auto"
                )
                if box:
                    return box, {
                        "name": tmpl.get("name", ""),
                        "path": path,
                        "threshold": threshold,
                        "confidence": confidence,
                    }

            return None, None

        # Fallback to legacy template_path
        region_list = cfg.get("region")
        region = tuple(region_list) if region_list else None
        template = cfg.get("template_path")
        threshold = cfg.get("confidence", 0.8)
        if not template or not Path(template).exists():
            return None, None

        # Use template_matcher for accurate confidence tracking
        box, confidence = locate_template(template, region, threshold, method="auto")
        return (
            (box, {"path": template, "threshold": threshold, "confidence": confidence})
            if box
            else (None, None)
        )

    def _check_first_time_setup(self):
        """Check if this is first-time user and auto-launch wizard if needed."""
        # Check if user has completed basic setup
        # Must have ALL THREE to be considered configured
        has_window = bool(self.hunt_cfg.get("window_title", "").strip())

        # Phase 3 compatibility: Check both legacy and new monster fields
        has_monster_legacy = bool(
            self.hunt_cfg.get("monster_selected_name", "").strip()
        )
        has_monster_list = (
            bool(self.hunt_cfg.get("monster_list"))
            and len(self.hunt_cfg.get("monster_list", [])) > 0
        )
        has_monster = has_monster_legacy or has_monster_list

        has_skills = (
            bool(self.hunt_cfg.get("skill_slots"))
            and len(self.hunt_cfg.get("skill_slots", [])) > 0
        )

        is_new_user = not (has_window and has_monster and has_skills)

        # Debug log to understand detection
        print(
            f"[First-time check] window={has_window}, monster={has_monster}, skills={has_skills}, is_new={is_new_user}"
        )

        if is_new_user:
            print("[First-time check] Showing messagebox to ask user...")

            # Force main window to front before showing messagebox
            self.lift()
            self.focus_force()
            self.attributes("-topmost", True)
            self.update()

            # Ask user if they want to run setup wizard
            response = messagebox.askyesno(
                self._t("wizard_first_time_title"),
                self._t("wizard_first_time_message"),
                icon="question",
                parent=self,  # Ensure messagebox is child of main window
            )

            # Disable topmost after messagebox
            self.attributes("-topmost", False)

            print(f"[First-time check] User response: {response}")

            if response:
                # User clicked Yes - launch wizard
                print("[First-time check] Launching wizard...")
                self.on_setup_wizard()
            else:
                # User clicked No - auto-detect Cabal window and save
                print(
                    "[First-time check] User skipped wizard - attempting auto PID detection..."
                )
                self._auto_detect_and_save_cabal_window()
                self.hunt_status.set(self._t("wizard_skipped_hint"))

        # Check PIL availability and show one-time warning if missing
        if not self.pil_available:
            print("[PIL Check] PIL/Pillow not available - showing install instructions")
            # Use showinfo (blue icon) instead of showerror (red icon) for less scary UX
            # Don't force window to front - let user dismiss naturally
            messagebox.showinfo(
                self._t("info_title"), self._t("pil_not_installed_message"), parent=self
            )

    def _auto_detect_and_save_cabal_window(self):
        """Auto-detect Cabal window PID and save to config when user skips setup."""
        print("[Auto PID] Starting Cabal window detection...")

        # Find all windows
        items = self._enum_windows()

        # Filter for Cabal windows
        cabal_windows = [
            w
            for w in items
            if "cabal" in w["title"].lower()
            or (w.get("proc") and "cabal" in w["proc"].lower())
        ]

        if not cabal_windows:
            print("[Auto PID] No Cabal windows found")
            messagebox.showwarning(
                self._t("info_title"),
                "No Cabal windows detected.\n\nPlease:\n1. Launch Cabal game first\n2. Click 'Find Windows' button to select manually",
                parent=self,
            )
            return

        # Select first Cabal window
        selected = cabal_windows[0]
        print(
            f"[Auto PID] Found Cabal window: {selected['title']} [PID:{selected['pid']}]"
        )

        # Update hunt_selected
        self.hunt_selected = selected

        # Update UI combobox (show only window title without PID)
        if hasattr(self, "win_combo"):
            self.win_combo["values"] = [selected['title']]
            self.win_combo.current(0)
            self.win_items = [selected]

        # Save to hunt_config.json
        self.hunt_cfg["window_title"] = selected["title"]
        self.hunt_cfg["window_pid"] = selected["pid"]
        self.hunt_cfg["window_hwnd"] = selected["hwnd"]

        try:
            save_hunt_config(self.hunt_cfg)
            print(
                f"[Auto PID] Saved to config: {selected['title']} [PID:{selected['pid']}]"
            )

            # Show success message
            messagebox.showinfo(
                self._t("info_title"),
                f"✅ Auto-detected Cabal window:\n\n{selected['title']}\nPID: {selected['pid']}\n\nYou can change this anytime using 'Find Windows' button.",
                parent=self,
            )
        except Exception as e:
            print(f"[Auto PID] Failed to save config: {e}")

    def on_setup_wizard(self, hide_parent=True):
        """Launch setup wizard to guide user through initial configuration.
        
        Args:
            hide_parent: Whether to hide parent window (default True for startup, False for hotkey)
        """

        def on_wizard_complete(wizard_data):
            """Callback when wizard completes - apply settings to UI."""
            # Show main window again if it was hidden
            if hide_parent:
                self.deiconify()

            # Reload config to get wizard changes
            self.hunt_cfg = load_hunt_config()

            # Populate Hunt tab UI with wizard data
            self._populate_hunt_ui_from_config()

            # Update status message
            lang = wizard_data.get("language", "en")
            self.hunt_status.set(
                f"✅ Wizard completed! Configuration loaded. Ready to hunt. (Language: {lang})"
            )

        def on_wizard_cancel():
            """Callback when wizard is cancelled - restore main window."""
            if hide_parent:
                self.deiconify()

        # Launch wizard - use 'self' instead of 'self.root' (App inherits from tk.Tk)
        if callable(show_setup_wizard):
            show_setup_wizard(
                self,
                config_manager=self.config_mgr,
                on_complete=on_wizard_complete,
                on_cancel=on_wizard_cancel,
                hide_parent=hide_parent,
            )
        else:
            # Fallback: wizard not available
            try:
                messagebox.showinfo(
                    self._t("info_title"),
                    "Setup wizard is not available in this build.",
                    parent=self,
                )
            except Exception:
                pass

    def _populate_hunt_ui_from_config(self):
        """Populate Hunt tab UI elements from hunt_config.json data."""
        # 1. Window selection
        window_title = self.hunt_cfg.get("window_title", "").strip()
        window_pid = self.hunt_cfg.get("window_pid")
        window_hwnd = self.hunt_cfg.get("window_hwnd")

        if window_title:
            # If we have PID/HWND, create hunt_selected object
            if window_pid and window_hwnd:
                self.hunt_selected = {
                    "title": window_title,
                    "pid": window_pid,
                    "hwnd": window_hwnd,
                    "proc": None,  # Process name not saved in config
                }

                # Populate combobox with saved window (show only window title without PID)
                if hasattr(self, "win_combo"):
                    self.win_combo["values"] = [window_title]
                    self.win_combo.current(0)
                    self.win_items = [self.hunt_selected]

        # 2. Monster template (if exists)
        monster_name = self.hunt_cfg.get("monster_selected_name", "").strip()
        template_path = self.hunt_cfg.get("template_path", "").strip()

        if monster_name:
            # Update monster name display (assuming you have a monster_name variable)
            # This will be shown in UI when monster selection is implemented
            pass

        # 3. Skill slots
        skill_slots = self.hunt_cfg.get("skill_slots", [])
        if skill_slots:
            # Update skill UI (assuming skill slot UI variables exist)
            # This will populate skill comboboxes when skill UI is ready
            pass

        # 4. Update any other UI elements that depend on config
        # (Add more as needed based on your UI structure)
        pass

    def _auto_populate_saved_window(self):
        """
        Auto-populate window selection from hunt_config.json on app startup.
        Prevents users from having to re-select window if already configured.
        Users can still use 'Find Windows' to change if needed.
        """
        window_title = self.hunt_cfg.get("window_title", "").strip()
        window_pid = self.hunt_cfg.get("window_pid")
        window_hwnd = self.hunt_cfg.get("window_hwnd")

        # Only auto-populate if we have all required data
        if not (window_title and window_pid and window_hwnd):
            return

        # Create hunt_selected object
        self.hunt_selected = {
            "title": window_title,
            "pid": window_pid,
            "hwnd": window_hwnd,
            "proc": None,  # Process name not saved in config
        }

        # Populate combobox with saved window (show only window title without PID)
        if hasattr(self, "win_combo"):
            self.win_combo["values"] = [window_title]
            self.win_combo.current(0)
            self.win_items = [self.hunt_selected]

        # Update status to inform user
        self.hunt_status.set(
            f"✓ Loaded saved window: {window_title} (PID: {window_pid})"
        )

    def _auto_bring_to_front_on_startup(self):
        """Auto bring saved Cabal window to front BELOW app on startup."""
        try:
            # Check if we have a valid hunt_selected window
            if not hasattr(self, "hunt_selected") or not self.hunt_selected:
                print("[Auto Bring] No saved window to bring to front")
                return

            hwnd = self.hunt_selected.get("hwnd")
            title = self.hunt_selected.get("title", "")
            pid = self.hunt_selected.get("pid", "")

            if not hwnd:
                print(f"[Auto Bring] No HWND for window: {title}")
                return

            print(
                f"[Auto Bring] Bringing window to front (below app): {title} [PID:{pid}]"
            )

            # Bring window to front
            ok = self._bring_window_to_front_by_hwnd(hwnd)

            if ok:
                # Keep app on top of game window
                time.sleep(0.1)
                self.lift()
                self.focus_force()
                self.attributes("-topmost", True)
                self.update()
                self.after(100, lambda: self.attributes("-topmost", False))

                print(f"[Auto Bring] ✓ Window ready (below app): {title}")
                # Update status briefly
                if hasattr(self, "hunt_status"):
                    current_status = self.hunt_status.get()
                    self.hunt_status.set(f"✓ Game window ready: {title}")
                    # Restore previous status after 3 seconds
                    self.after(3000, lambda: self.hunt_status.set(current_status))
            else:
                print(f"[Auto Bring] ✗ Failed to bring window to front: {title}")

        except Exception as e:
            print(f"[Auto Bring] Error: {e}")

    def on_hunt_save(self):
        try:
            cfg = self._hunt_from_ui()
            save_hunt_config(cfg)
            self.hunt_cfg = cfg
            self.hunt_status.set("Saved hunt_config.json")
            self._clear_unsaved_changes()
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), self._t("invalid_hunt").format(e=e)
            )

    def on_global_apply(self):
        """Global apply handler - saves all settings across all tabs.

        NOTE: Save file only ONCE to avoid duplicate writes and preserve field order.
        """
        try:
            # 1. Apply Setup tab settings (updates hunt_cfg in-place, but don't save yet)
            self._apply_setup_settings(save_to_file=False)

            # 2. Update hunt config from Hunt tab UI (in-place update)
            cfg = self._hunt_from_ui()

            # 2.5. Update global hotkeys from Setup tab UI
            if hasattr(self, "global_hotkey_enabled_var"):
                enabled = self.global_hotkey_enabled_var.get()
                start_key = self.global_hotkey_start_var.get()
                stop_key = self.global_hotkey_stop_var.get()
                wizard_key = self.global_hotkey_wizard_var.get()  # NEW
                library_key = self.global_hotkey_library_var.get()  # NEW

                # Validate: all hotkeys must be unique
                all_keys = [start_key, stop_key, wizard_key, library_key]
                if len(all_keys) != len(set(all_keys)):
                    messagebox.showerror(
                        self._t("error_title"),
                        (
                            "All hotkeys must be different!"
                            if self.lang == "en"
                            else "Tất cả phím tắt phải khác nhau!"
                        ),
                    )
                    return

                # Update config
                vision_key = self.global_hotkey_vision_var.get()
                cfg["global_hotkeys"] = {
                    "enabled": enabled,
                    "start_key": start_key,
                    "stop_key": stop_key,
                    "setup_wizard_key": wizard_key,
                    "library_manager_key": library_key,
                    "vision_wizard_key": vision_key,
                }

                # Re-register hotkeys with new settings
                self.hunt_cfg = cfg  # Update instance config first
                self._unregister_global_hotkeys()
                self._register_global_hotkeys()

            # 3. Save to file ONCE (preserves insertion order in Python 3.7+)
            save_hunt_config(cfg)
            self.hunt_cfg = cfg

            # 4. Clear unsaved changes indicator
            self._clear_unsaved_changes()

            # 5. Update status
            self.hunt_status.set(self._t("all_saved"))

            # 6. Show success message
            messagebox.showinfo(
                self._t("success_title"), self._t("settings_applied_message")
            )
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), f"Failed to apply settings: {e}"
            )

    def _mark_unsaved(self, *args):
        """Mark that there are unsaved changes."""
        self.has_unsaved_changes = True
        self._update_unsaved_indicator()

    def _clear_unsaved_changes(self):
        """Clear unsaved changes indicator after successful save."""
        self.has_unsaved_changes = False
        self._update_unsaved_indicator()

    def _update_unsaved_indicator(self):
        """Update unsaved changes indicator UI."""
        if not hasattr(self, "unsaved_indicator_label"):
            return

        if self.has_unsaved_changes:
            self.unsaved_indicator_label.config(
                text=f"● {self._t('unsaved_indicator')}", fg="#FF9800"  # Orange color
            )
        else:
            self.unsaved_indicator_label.config(
                text=f"✓ {self._t('all_saved')}", fg="#4CAF50"  # Green color
            )

    def _switch_to_tab(self, tab_index: int):
        """Switch to specified tab via keyboard shortcut."""
        try:
            if not hasattr(self, "notebook"):
                return

            # Switch to tab
            self.notebook.select(tab_index)

            # Update status with shortcut indicator
            tab_names = ["Hunt", "Setup", "Stats", "Help"]
            if 0 <= tab_index < len(tab_names):
                tab_name = tab_names[tab_index]
                shortcut = f"Alt+{tab_index + 1}"
                if hasattr(self, "hunt_status"):
                    self.hunt_status.set(f"{shortcut}: Switched to {tab_name} tab")
        except Exception as e:
            print(f"Tab switch error: {e}")

    def _on_setup_wizard_hotkey(self):
        """Callback for Setup Wizard hotkey (Ctrl+Shift+N).

        Only executes if ui_mode == 'beginner'.
        Shows confirmation if user is new (no config).
        """
        try:
            print("[Hotkeys] Setup Wizard hotkey pressed")

            # Check mode before opening
            current_mode = self.hunt_cfg.get("ui_mode", "beginner")
            if current_mode != "beginner":
                print(f"[Hotkeys] Setup Wizard blocked - current mode: {current_mode}")
                return

            # Toggle behavior for wizard (only in beginner mode):
            # If wizard is open and viewable -> hide; if hidden -> show; otherwise open.
            existing = getattr(self, "_setup_wizard_win", None) or getattr(self, "setup_wizard_win", None) or getattr(self, "_setup_wizard", None)
            try:
                if existing is not None and getattr(existing, "winfo_exists", lambda: False)():
                    try:
                        # If the stored object is the SetupWizard instance it may expose .dialog
                        win = getattr(existing, "dialog", existing)
                        if win.winfo_viewable():
                            try:
                                win.withdraw()
                            except Exception:
                                try:
                                    win.iconify()
                                except Exception:
                                    pass
                        else:
                            try:
                                win.deiconify()
                                win.lift()
                                win.focus_force()
                                try:
                                    win.attributes("-topmost", True)
                                    win.after(120, lambda: win.attributes("-topmost", False))
                                except Exception:
                                    pass
                            except Exception:
                                try:
                                    win.lift(); win.focus_force()
                                except Exception:
                                    pass
                        return
                    except Exception:
                        try:
                            # fallback: destroy stale reference
                            existing.destroy()
                        except Exception:
                            pass

            except Exception:
                pass

            # No existing wizard - open directly without confirmation
            # (User actively pressed hotkey, no need to ask)
            print('[Hotkeys] Opening Setup Wizard directly from hotkey')
            self.after(0, lambda: self.on_setup_wizard(hide_parent=False))

        except Exception as e:
            print(f"[Hotkeys] Error opening Setup Wizard: {e}")

    def _on_library_manager_hotkey(self):
        """Callback for Library Manager hotkey (Ctrl+Shift+L).

        Always available regardless of UI mode.
        Simple toggle - no mutual exclusion with wizard.
        """
        try:
            print("[Hotkeys] Library Manager hotkey pressed")

            # Toggle behavior: if library manager exists and is visible -> hide it;
            # if exists but hidden -> show it; otherwise create it.
            existing = getattr(self, "library_manager_win", None)
            if existing is not None and getattr(existing, "winfo_exists", lambda: False)():
                try:
                    # If currently viewable, hide (withdraw). If hidden, show again.
                    if existing.winfo_viewable():
                        try:
                            existing.withdraw()
                        except Exception:
                            try:
                                existing.iconify()
                            except Exception:
                                pass
                    else:
                        try:
                            existing.deiconify()
                            existing.lift()
                            existing.focus_force()
                        except Exception:
                            try:
                                existing.lift()
                                existing.focus_force()
                            except Exception:
                                pass
                    return
                except Exception:
                    # fallthrough to open a fresh one
                    try:
                        existing.destroy()
                    except Exception:
                        pass

            # Create or show new manager
            self.after(0, self._open_library_manager)

        except Exception as e:
            print(f"[Hotkeys] Error opening Library Manager: {e}")

    def _on_vision_wizard_hotkey(self):
        """Callback for Vision Wizard hotkey (Ctrl+Shift+V).

        Sprint 22: Opens Vision Wizard for real-time CV debugging.
        Always available regardless of UI mode.
        """
        try:
            print("[Hotkeys] Vision Wizard hotkey pressed")

            # Vision Wizard uses singleton pattern via create_or_show_vision_wizard
            # No need to check existing window - factory handles it
            self.after(0, self._open_vision_wizard)

        except Exception as e:
            print(f"[Hotkeys] Error opening Vision Wizard: {e}")

    def _on_monster_editor_hotkey(self):
        """Callback for Monster Editor hotkey (Ctrl+Shift+M).

        Opens Quick Monster Editor for rapid CRUD operations.
        Always available regardless of UI mode.
        """
        try:
            print("[Hotkeys] Monster Editor hotkey pressed")
            
            # Schedule Monster Editor to open in main thread
            self.after(0, self._open_monster_editor)
            
        except Exception as e:
            print(f"[Hotkeys] Error opening Monster Editor: {e}")

    def _open_monster_editor(self):
        """Open Quick Monster Editor dialog.
        
        Opens the quick monster editor for fast monster CRUD operations.
        Uses singleton pattern to prevent multiple instances.
        """
        try:
            print("[Monster Editor] Opening Quick Monster Editor...")
            
            # Import quick editor (lazy import to avoid circular dependencies)
            try:
                from ui.windows.quick_monster_editor import show_quick_monster_editor
            except ImportError as ie:
                print(f"[Monster Editor] Failed to import quick_monster_editor: {ie}")
                messagebox.showerror(
                    "Import Error",
                    f"Could not load Monster Editor module:\n{ie}"
                )
                return
            
            # Show quick editor (singleton pattern handles existing instances)
            editor = show_quick_monster_editor(
                parent=self,
                monster_id=None,  # None = create new monster
                on_save=self._on_monster_saved
            )
            
            print("[Monster Editor] Quick Monster Editor opened successfully")
            
        except Exception as e:
            print(f"[Monster Editor] Error opening editor: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Monster Editor Error",
                f"Failed to open Monster Editor:\n{e}"
            )

    def _on_monster_saved(self, monster_id: str, monster_data: dict):
        """Callback when monster is saved in Quick Editor.
        
        Args:
            monster_id: ID of saved monster
            monster_data: Monster data dictionary
        """
        try:
            print(f"[Monster Editor] Monster saved: {monster_id}")
            # TODO: Refresh monster list if needed
            # TODO: Update library manager if open
        except Exception as e:
            print(f"[Monster Editor] Error in save callback: {e}")

    def _register_global_hotkeys(self):
        """Register global hotkeys (Ctrl+Shift+R/E) for hunt start/stop.

        This is called in __init__() after config load to ensure hotkeys are
        immediately available, even when app is minimized or not focused.
        """
        print("[Hotkeys] _register_global_hotkeys() called")
        try:
            # Check if keyboard module is available
            if keyboard is None:
                # Provide detailed diagnostics to help troubleshoot environment mismatches
                try:
                    import sys as _sys, importlib, traceback as _tb

                    print(
                        f"[Hotkeys] ⚠️ keyboard module not available in interpreter: {_sys.executable}"
                    )
                    # Try a fresh import to capture the exception text (without changing global state)
                    try:
                        importlib.import_module("keyboard")
                        print(
                            "[Hotkeys] Note: importlib was able to import keyboard unexpectedly"
                        )
                    except Exception as _e:
                        print("[Hotkeys] keyboard import error trace:")
                        _tb.print_exc()
                        # Save diagnostic text for UI/diagnostics dialog
                        try:
                            self._hotkey_import_diag = _tb.format_exc()
                        except Exception:
                            self._hotkey_import_diag = str(_e)
                        # Update UI banner if available
                        try:
                            self._update_hotkey_diagnostics_ui()
                        except Exception:
                            pass
                except Exception:
                    # Fallback minimal diagnostic
                    try:
                        import sys as _sys

                        print(
                            f"[Hotkeys] ⚠️ keyboard module not available (interpreter: {_sys.executable})"
                        )
                    except Exception:
                        print("[Hotkeys] ⚠️ keyboard module not available")

                # Fallback: bind window-focused shortcuts using tkinter so app still responds when focused.
                # These are not global system-wide hotkeys, but provide reasonable functionality if keyboard is missing.
                def _to_tk_seq(hotkey: str) -> Optional[str]:
                    # Very small converter for common patterns like 'ctrl+shift+r', 'ctrl+f8', 'f8'
                    try:
                        hk = (hotkey or "").strip().lower()
                        if not hk:
                            return None
                        parts = hk.split("+")
                        mods = []
                        key = None
                        for p in parts:
                            p = p.strip()
                            if p in ("ctrl", "control"):
                                mods.append("Control")
                            elif p in ("shift",):
                                mods.append("Shift")
                            elif p in ("alt", "menu"):
                                mods.append("Alt")
                            else:
                                key = p
                        if not key:
                            return None
                        # Function keys (f1..f24)
                        if key.startswith("f") and key[1:].isdigit():
                            key_tok = key.upper()
                        else:
                            # single character -> uppercase letter
                            key_tok = key.upper()
                        seq = "<" + "-".join(mods + [key_tok]) + ">"
                        return seq
                    except Exception:
                        return None

                # Bind defaults first, then try to honor configured keys if possible
                cfg = self.hunt_cfg.get("global_hotkeys", {})
                start_key = cfg.get("start_key", "ctrl+shift+r")
                stop_key = cfg.get("stop_key", "ctrl+shift+e")
                wizard_key = cfg.get("setup_wizard_key", "ctrl+shift+n")
                library_key = cfg.get("library_manager_key", "ctrl+shift+l")
                vision_key = cfg.get("vision_wizard_key", "ctrl+shift+v")  # Sprint 22
                monster_key = cfg.get("monster_editor_key", "ctrl+shift+m")  # Monster Editor

                seq_start = _to_tk_seq(start_key) or "<Control-Shift-R>"
                seq_stop = _to_tk_seq(stop_key) or "<Control-Shift-E>"
                seq_wiz = _to_tk_seq(wizard_key) or "<Control-Shift-N>"
                seq_lib = _to_tk_seq(library_key) or "<Control-Shift-L>"
                seq_vision = _to_tk_seq(vision_key) or "<Control-Shift-V>"  # Sprint 22
                seq_monster = _to_tk_seq(monster_key) or "<Control-Shift-M>"  # Monster Editor

                try:
                    # Unbind any previously-bound fallback sequences to avoid duplicates
                    for s in list(self._hotkey_fallback_bound):
                        try:
                            self.unbind_all(s)
                        except Exception:
                            pass
                    self._hotkey_fallback_bound = []

                    # Bind to all widgets (works when app is focused)
                    self.bind_all(seq_start, lambda e: self.on_hunt_start(), add="+")
                    self._hotkey_fallback_bound.append(seq_start)
                    self.bind_all(seq_stop, lambda e: self.on_hunt_stop(), add="+")
                    self._hotkey_fallback_bound.append(seq_stop)
                    # Wizard only meaningful in beginner mode
                    if self.hunt_cfg.get("ui_mode", "beginner") == "beginner":
                        self.bind_all(
                            seq_wiz, lambda e: self._on_setup_wizard_hotkey(), add="+"
                        )
                        self._hotkey_fallback_bound.append(seq_wiz)
                    self.bind_all(
                        seq_lib, lambda e: self._on_library_manager_hotkey(), add="+"
                    )
                    self._hotkey_fallback_bound.append(seq_lib)
                    # Sprint 22: Vision Wizard fallback
                    self.bind_all(
                        seq_vision, lambda e: self._on_vision_wizard_hotkey(), add="+"
                    )
                    self._hotkey_fallback_bound.append(seq_vision)
                    # Monster Editor fallback
                    self.bind_all(
                        seq_monster, lambda e: self._on_monster_editor_hotkey(), add="+"
                    )
                    self._hotkey_fallback_bound.append(seq_monster)
                    print(
                        f"[Hotkeys] Fallback (focused) hotkeys bound: {', '.join(self._hotkey_fallback_bound)}"
                    )
                    try:
                        self._update_hotkey_diagnostics_ui()
                    except Exception:
                        pass
                except Exception as _bind_e:
                    print(
                        f"[Hotkeys] Failed to bind fallback focused hotkeys: {_bind_e}"
                    )

                return

            # Get hotkey config (defaults to Ctrl+Shift+R/E if not set)
            hotkey_cfg = self.hunt_cfg.get("global_hotkeys", {})
            if not hotkey_cfg.get("enabled", True):
                print("[Hotkeys] Global hotkeys disabled by user")
                return  # Global hotkeys disabled by user

            start_key = hotkey_cfg.get("start_key", "ctrl+shift+r")
            stop_key = hotkey_cfg.get("stop_key", "ctrl+shift+e")
            wizard_key = hotkey_cfg.get("setup_wizard_key", "ctrl+shift+n")  # NEW
            library_key = hotkey_cfg.get("library_manager_key", "ctrl+shift+l")  # NEW
            vision_key = hotkey_cfg.get("vision_wizard_key", "ctrl+shift+v")  # NEW Sprint 22
            monster_key = hotkey_cfg.get("monster_editor_key", "ctrl+shift+m")  # NEW Monster Editor

            # Unregister old hotkeys first (in case of re-registration)
            self._unregister_global_hotkeys()

            # Register new hotkeys
            try:
                self._global_start_hotkey = keyboard.add_hotkey(
                    start_key,
                    self.on_hunt_start,
                    suppress=False,  # Don't suppress the key event
                )
            except Exception as e:
                print(f"Failed to register start hotkey '{start_key}': {e}")
                self._global_start_hotkey = None

            try:
                self._global_stop_hotkey = keyboard.add_hotkey(
                    stop_key, self.on_hunt_stop, suppress=False
                )
            except Exception as e:
                print(f"Failed to register stop hotkey '{stop_key}': {e}")
                self._global_stop_hotkey = None

            # NEW: Register Setup Wizard hotkey (only in beginner mode)
            current_mode = self.hunt_cfg.get("ui_mode", "beginner")
            if current_mode == "beginner":
                try:
                    self._global_wizard_hotkey = keyboard.add_hotkey(
                        wizard_key, self._on_setup_wizard_hotkey, suppress=False
                    )
                except Exception as e:
                    print(f"Failed to register wizard hotkey '{wizard_key}': {e}")
                    self._global_wizard_hotkey = None
            else:
                self._global_wizard_hotkey = None

            # NEW: Register Library Manager hotkey (always active)
            try:
                self._global_library_hotkey = keyboard.add_hotkey(
                    library_key, self._on_library_manager_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register library hotkey '{library_key}': {e}")
                self._global_library_hotkey = None

            # NEW Sprint 22: Register Vision Wizard hotkey (always active)
            try:
                self._global_vision_hotkey = keyboard.add_hotkey(
                    vision_key, self._on_vision_wizard_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register vision hotkey '{vision_key}': {e}")
                self._global_vision_hotkey = None

            # NEW: Register Monster Editor hotkey (always active)
            try:
                self._global_monster_hotkey = keyboard.add_hotkey(
                    monster_key, self._on_monster_editor_hotkey, suppress=False
                )
            except Exception as e:
                print(f"Failed to register monster editor hotkey '{monster_key}': {e}")
                self._global_monster_hotkey = None

            # Log successful registration
            registered = []
            if self._global_start_hotkey:
                registered.append(f"Start={start_key}")
            if self._global_stop_hotkey:
                registered.append(f"Stop={stop_key}")
            if self._global_wizard_hotkey:
                registered.append(f"Wizard={wizard_key}")
            if self._global_library_hotkey:
                registered.append(f"Library={library_key}")
            if self._global_vision_hotkey:
                registered.append(f"Vision={vision_key}")
            if self._global_monster_hotkey:
                registered.append(f"Monster={monster_key}")

            if registered:
                print(f"Global hotkeys registered: {', '.join(registered)}")
                # Update new status-driven UI
                try:
                    self.after(150, self._update_hotkey_diagnostics_ui)
                except Exception:
                    pass

        except Exception as e:
            print(f"Error registering global hotkeys: {e}")
            # Update UI to show error state
            try:
                self.after(150, self._update_hotkey_diagnostics_ui)
            except Exception:
                pass

    def _unregister_global_hotkeys(self):
        """Unregister global hotkeys to clean up resources.

        Called when:
        - Re-registering hotkeys with new key combinations
        - Closing the application (in on_close)
        - Disabling global hotkeys via settings
        """
        try:
            if keyboard is None:
                return

            # Unregister start hotkey
            if self._global_start_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_start_hotkey)
                except Exception as e:
                    print(f"Error unregistering start hotkey: {e}")
                finally:
                    self._global_start_hotkey = None

            # Unregister stop hotkey
            if self._global_stop_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_stop_hotkey)
                except Exception as e:
                    print(f"Error unregistering stop hotkey: {e}")
                finally:
                    self._global_stop_hotkey = None

            # NEW: Unregister wizard hotkey
            if self._global_wizard_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_wizard_hotkey)
                except Exception as e:
                    print(f"Error unregistering wizard hotkey: {e}")
                finally:
                    self._global_wizard_hotkey = None

            # NEW: Unregister library hotkey
            if self._global_library_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_library_hotkey)
                except Exception as e:
                    print(f"Error unregistering library hotkey: {e}")
                finally:
                    self._global_library_hotkey = None

            # NEW Sprint 22: Unregister vision hotkey
            if self._global_vision_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_vision_hotkey)
                except Exception as e:
                    print(f"Error unregistering vision hotkey: {e}")
                finally:
                    self._global_vision_hotkey = None

            # NEW: Unregister monster editor hotkey
            if self._global_monster_hotkey is not None:
                try:
                    keyboard.remove_hotkey(self._global_monster_hotkey)
                except Exception as e:
                    print(f"Error unregistering monster editor hotkey: {e}")
                finally:
                    self._global_monster_hotkey = None

        except Exception as e:
            print(f"Error in _unregister_global_hotkeys: {e}")
            try:
                self._hotkey_diag_var.set(str(e))
            except Exception:
                pass

    def _on_retry_global_hotkeys(self):
        """Handler for 'Retry Global Hotkeys' button in Setup tab."""
        try:
            # Clear previous diagnostics
            try:
                self._hotkey_diag_var.set("")
            except Exception:
                pass
            # Unregister then re-register
            try:
                self._unregister_global_hotkeys()
            except Exception:
                pass
            self._register_global_hotkeys()
            # Refresh UI state
            self._update_hotkeys_state()
        except Exception as e:
            print(f"[Hotkeys] Retry action failed: {e}")
            try:
                self._hotkey_diag_var.set(str(e))
            except Exception:
                pass

    def _update_hotkey_diagnostics_ui(self):
        """Update the hotkey status UI based on registration state.
        
        This new implementation uses a status-driven approach:
        - Success state: Show green checkmark, hide action buttons
        - Partial failure: Show orange warning, show retry button
        - Complete failure: Show red error, show both buttons
        """
        try:
            # Determine current state
            has_import_error = hasattr(self, "_hotkey_import_diag") and self._hotkey_import_diag
            has_failed_hotkeys = hasattr(self, "_failed_hotkeys") and self._failed_hotkeys
            hotkeys_enabled = getattr(self, "_hotkeys_registered_ok", False)
            
            # Count actual registered hotkeys (not bindings)
            registered_count = 0
            hotkey_details = []
            
            if getattr(self, "_global_start_hotkey", None):
                registered_count += 1
                hotkey_details.append("Start" if self.lang == "en" else "Bắt đầu")
            if getattr(self, "_global_stop_hotkey", None):
                registered_count += 1
                hotkey_details.append("Stop" if self.lang == "en" else "Dừng")
            if getattr(self, "_global_wizard_hotkey", None):
                registered_count += 1
                hotkey_details.append("Wizard" if self.lang == "en" else "Trợ lý")
            if getattr(self, "_global_library_hotkey", None):
                registered_count += 1
                hotkey_details.append("Library" if self.lang == "en" else "Thư viện")
            if getattr(self, "_global_vision_hotkey", None):
                registered_count += 1
                hotkey_details.append("Vision" if self.lang == "en" else "Thị giác")
            
            # State 1: Success - All hotkeys registered
            if hotkeys_enabled and not has_failed_hotkeys and not has_import_error:
                # Green success state
                success_text = "All hotkeys registered successfully" if self.lang == "en" else "Tất cả phím tắt đã đăng ký thành công"
                self._hotkey_status_var.set(f"✅ {success_text}")
                self._hotkey_status_label.config(fg="#4CAF50")  # Green
                
                # Show count and active hotkeys list
                detail_text = f"{registered_count} hotkeys active" if self.lang == "en" else f"{registered_count} phím tắt đang hoạt động"
                if hotkey_details:
                    detail_text += f": {', '.join(hotkey_details)}"
                self._hotkey_status_detail_var.set(f"   {detail_text}")
                
                # Hide action buttons (not needed)
                if hasattr(self, "_hotkey_retry_btn"):
                    self._hotkey_retry_btn.pack_forget()
                if hasattr(self, "_hotkey_details_btn"):
                    self._hotkey_details_btn.pack_forget()
            
            # State 2: Partial failure - Some hotkeys failed
            elif has_failed_hotkeys and not has_import_error:
                # Orange warning state
                failed_count = len(self._failed_hotkeys)
                warning_text = f"{failed_count} hotkey(s) failed to register" if self.lang == "en" else f"{failed_count} phím tắt đăng ký thất bại"
                self._hotkey_status_var.set(f"⚠️ {warning_text}")
                self._hotkey_status_label.config(fg="#FF9800")  # Orange
                
                # Show guidance
                guidance = "Try changing the conflicting hotkey, then click Apply." if self.lang == "en" else "Thử đổi phím tắt bị xung đột, sau đó nhấn Áp dụng."
                self._hotkey_status_detail_var.set(f"   {guidance}")
                
                # Show retry button only
                if hasattr(self, "_hotkey_retry_btn"):
                    retry_text = "🔄 Retry Registration" if self.lang == "en" else "🔄 Thử Đăng Ký Lại"
                    self._hotkey_retry_btn.config(text=retry_text)
                    self._hotkey_retry_btn.pack(side="left", padx=(0, 8))
                if hasattr(self, "_hotkey_details_btn"):
                    self._hotkey_details_btn.pack_forget()
            
            # State 3: Complete failure - Import error or no hotkeys registered
            else:
                # Red error state
                error_text = "Hotkeys not available" if self.lang == "en" else "Phím tắt không khả dụng"
                self._hotkey_status_var.set(f"❌ {error_text}")
                self._hotkey_status_label.config(fg="#F44336")  # Red
                
                # Show explanation
                if has_import_error:
                    explanation = "The 'keyboard' package is not installed in your Python environment." if self.lang == "en" else "Gói 'keyboard' chưa được cài đặt trong Python của bạn."
                else:
                    explanation = "Failed to register global hotkeys." if self.lang == "en" else "Không thể đăng ký phím tắt toàn cục."
                self._hotkey_status_detail_var.set(f"   {explanation}")
                
                # Show both buttons
                if hasattr(self, "_hotkey_details_btn"):
                    fix_text = "📋 Show Fix Instructions" if self.lang == "en" else "📋 Hướng Dẫn Khắc Phục"
                    self._hotkey_details_btn.config(text=fix_text)
                    self._hotkey_details_btn.pack(side="left", padx=(0, 8))
                if hasattr(self, "_hotkey_retry_btn"):
                    retry_text = "🔄 Retry After Fix" if self.lang == "en" else "🔄 Thử Lại Sau Khi Sửa"
                    self._hotkey_retry_btn.config(text=retry_text)
                    self._hotkey_retry_btn.pack(side="left")
                    
        except Exception as e:
            # Fallback: show basic error
            try:
                self._hotkey_status_var.set(f"⚠️ Error updating status: {e}")
                self._hotkey_status_label.config(fg="#FF9800")
            except Exception:
                pass

    def _hunt_from_ui(self):
        """Extract hunt configuration from UI elements.

        NOTE: This updates self.hunt_cfg in-place to preserve all fields (template_threshold,
        confidence, grayscale, training_mode_enabled, ui_mode, etc.) that are not managed by Hunt tab.
        """
        # Get window title from selected window or config
        title = ""
        if hasattr(self, "hunt_selected") and self.hunt_selected:
            title = self.hunt_selected.get("title", "").strip()
        if not title:
            title = self.hunt_cfg.get("window_title", "Cabal").strip()

        target_key = self.target_key_var.get().strip() or "TAB"

        # Validate numeric inputs
        try:
            press_ms = int(float(self.attack_press_var.get()))
        except ValueError:
            raise ValueError(
                self._t("error_invalid_number").format(field="attack_press_ms")
            )

        try:
            cycle_d = float(self.target_cycle_var.get())
            if cycle_d <= 0:
                raise ValueError(
                    self._t("error_value_must_be_positive").format(
                        field="target_cycle_delay"
                    )
                )
        except ValueError as e:
            if "must be" in str(e):
                raise
            raise ValueError(
                self._t("error_invalid_number").format(field="target_cycle_delay")
            )

        try:
            search_i = float(self.search_interval_var.get())
            if search_i <= 0:
                raise ValueError(
                    self._t("error_value_must_be_positive").format(
                        field="search_interval"
                    )
                )
        except ValueError as e:
            if "must be" in str(e):
                raise
            raise ValueError(
                self._t("error_invalid_number").format(field="search_interval")
            )

        try:
            attack_i = float(self.attack_interval_var.get())
            if attack_i <= 0:
                raise ValueError(
                    self._t("error_value_must_be_positive").format(
                        field="attack_interval"
                    )
                )
        except ValueError as e:
            if "must be" in str(e):
                raise
            raise ValueError(
                self._t("error_invalid_number").format(field="attack_interval")
            )

        try:
            lost_timeout = float(self.lost_timeout_var.get())
            if lost_timeout <= 0:
                raise ValueError(
                    self._t("error_value_must_be_positive").format(field="lost_timeout")
                )
        except ValueError as e:
            if "must be" in str(e):
                raise
            raise ValueError(
                self._t("error_invalid_number").format(field="lost_timeout")
            )

        try:
            attack_min_duration = float(self.attack_duration_var.get())
            if attack_min_duration <= 0:
                raise ValueError(
                    self._t("error_value_must_be_positive").format(
                        field="attack_min_duration"
                    )
                )
        except ValueError as e:
            if "must be" in str(e):
                raise
            raise ValueError(
                self._t("error_invalid_number").format(field="attack_min_duration")
            )

        template = self.template_var.get().strip()
        # Region
        region = None
        if all(
            v.strip() != ""
            for v in (
                self.reg_l.get(),
                self.reg_t.get(),
                self.reg_w.get(),
                self.reg_h.get(),
            )
        ):
            region = [
                int(self.reg_l.get()),
                int(self.reg_t.get()),
                int(self.reg_w.get()),
                int(self.reg_h.get()),
            ]

        # Update hunt_cfg in-place (preserves fields not managed by Hunt tab)
        self.hunt_cfg.update(
            {
                "window_title": title or "Cabal",
                "window_pid": (
                    int(self.hunt_selected["pid"]) if self.hunt_selected else None
                ),
                "target_key": target_key,
                # attack_keys field removed - skill keys are stored in skill_slots
                "attack_press_ms": press_ms,
                "target_cycle_delay": cycle_d,
                "search_interval": search_i,
                "attack_interval": attack_i,
                "template_path": template or "assets/images/target_frame.png",
                "region": region,
                "lost_timeout_sec": lost_timeout,
                "attack_min_duration_sec": attack_min_duration,
                "bring_to_front_each_cycle": bool(self.bring_front_var.get()),
                "window_bounds": self.current_window_bounds,
                # Phase 3: Multi-Monster Support
                "monster_list": self.monster_rotation_list,
                "current_monster_index": self.hunt_cfg.get("current_monster_index", 0),
                # Sprint 22 Patch 2: Save training_monster_list separately
                "training_monster_list": (
                    self.training_monster_list
                    if hasattr(self, "training_monster_list")
                    else []
                ),
            }
        )

        # Update skill slots
        slots = self._collect_skill_slots()
        self.hunt_cfg["skill_slots"] = slots
        # attack_keys removed: keys are saved per-skill inside hunt_cfg['skill_slots']

        return self.hunt_cfg

    # -----------------
    # Monster library helpers
    # -----------------
    def _monster_desc_set(self, text: str):
        if self.monster_description_text:
            self.monster_description_text.delete("1.0", tk.END)
            if text:
                self.monster_description_text.insert("1.0", text)

    def _monster_desc_get(self) -> str:
        if self.monster_description_text:
            return self.monster_description_text.get("1.0", tk.END).strip()
        return ""

    def on_monster_clear_bounds(self):
        for var in self.monster_bounds_vars.values():
            var.set("")

    def _ensure_monster_template_path_trace(self):
        if self._monster_template_path_trace:
            return

        def _trace(*_ignored):
            self._monster_template_update_preview(self.monster_template_path_var.get())

        self._monster_template_path_trace = self.monster_template_path_var.trace_add(
            "write", _trace
        )

    def _monster_template_update_preview(self, path):
        label = getattr(self, "monster_template_preview_label", None)
        if not label:
            return
        path = (path or "").strip()
        if not path:
            label.configure(image="", text=self._t("skill_no_image"))
            self.monster_template_preview_image = None
            return
        if Image is None or ImageTk is None:
            label.configure(image="", text=os.path.basename(path))
            self.monster_template_preview_image = None
            return

        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.configure(image=photo, text="")
            self.monster_template_preview_image = photo
            return

        try:
            img = Image.open(path)
            img.thumbnail(
                (200, 200)
            )  # Increased from 96x96 to 200x200 for better visibility
            photo = ImageTk.PhotoImage(img)
            self._thumbnail_cache[path] = photo  # Cache it
            label.configure(image=photo, text="")
            self.monster_template_preview_image = photo
        except Exception as e:
            # Better error handling with specific message
            error_msg = str(e) if str(e) else self._t("skill_image_error")
            label.configure(image="", text=f"❌ {error_msg[:50]}...")
            self.monster_template_preview_image = None

    def _monster_template_clear_form(self):
        self.monster_template_name_var.set("")
        self.monster_template_path_var.set("")
        self.monster_template_threshold_var.set("0.85")
        for var in self.monster_template_region_vars.values():
            var.set("")
        self._monster_template_update_preview("")

    def _monster_template_fill_form(self, template):
        if not template:
            self._monster_template_clear_form()
            return
        self.monster_template_name_var.set(template.get("name", ""))
        self.monster_template_path_var.set(template.get("path", ""))
        threshold = template.get("threshold", "")
        if threshold == "" or threshold is None:
            self.monster_template_threshold_var.set("0.85")
        else:
            self.monster_template_threshold_var.set(self._format_number(threshold))
        region = (
            template.get("region") if isinstance(template.get("region"), dict) else None
        )
        for key, var in self.monster_template_region_vars.items():
            if region and key in region:
                var.set(str(region.get(key, "")))
            else:
                var.set("")
        self._monster_template_update_preview(template.get("path", ""))

    def _monster_template_read_form(self):
        name = self.monster_template_name_var.get().strip()
        if not name:
            raise ValueError("name required")
        path = self.monster_template_path_var.get().strip()
        if not path:
            raise ValueError("path required")
        try:
            threshold_raw = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_raw or 0.85)
        except Exception as exc:
            raise ValueError(exc)
        if not math.isfinite(threshold):
            threshold = 0.85
        threshold = max(0.0, min(threshold, 1.0))
        region_input = {
            k: v.get().strip() for k, v in self.monster_template_region_vars.items()
        }
        region = None
        if any(region_input.values()):
            if not all(region_input.values()):
                raise ValueError("region requires 4 numbers")
            try:
                region_vals = {
                    k: int(region_input[k]) for k in ("left", "top", "width", "height")
                }
            except ValueError as exc:
                raise ValueError(f"invalid region: {exc}")
            if region_vals["width"] <= 0 or region_vals["height"] <= 0:
                raise ValueError("region width/height must be positive")
            region = region_vals
        data = {
            "name": name,
            "path": path,
            "threshold": threshold,
        }
        if region:
            data["region"] = region
        return data

    def _refresh_monster_template_list(self, select_index: Optional[int] = None):
        listbox = getattr(self, "monster_template_listbox", None)
        if listbox is None:
            return
        listbox.delete(0, tk.END)
        for idx, tmpl in enumerate(self.monster_template_working):
            label = tmpl.get("name") or f"Template {idx + 1}"
            threshold = tmpl.get("threshold")
            if threshold is not None and threshold != "":
                try:
                    label += f" ({float(threshold):.2f})"
                except Exception:
                    pass
            listbox.insert(tk.END, label)
        if self.monster_template_working:
            idx = (
                self.monster_template_selected_index
                if select_index is None
                else select_index
            )
            if idx is None:
                idx = 0
            idx = int(max(0, min(int(idx), len(self.monster_template_working) - 1)))
            select_index = idx
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(select_index)
            listbox.activate(select_index)
            self.monster_template_selected_index = select_index
            self._monster_template_fill_form(
                self.monster_template_working[select_index]
            )
        else:
            self.monster_template_selected_index = None
            self._monster_template_clear_form()
        if self.monster_template_working:
            first_path = self.monster_template_working[0].get("path", "")
            if first_path:
                self.monster_template_var.set(first_path)
            listbox.see(self.monster_template_selected_index)

    def on_monster_template_selected(self, _evt=None):
        listbox = getattr(self, "monster_template_listbox", None)
        if not listbox:
            return
        try:
            idxs = listbox.curselection()
            if not idxs:
                self.monster_template_selected_index = None
                self._monster_template_clear_form()
                return
            idx = idxs[0]
            if idx >= len(self.monster_template_working):
                return
            self.monster_template_selected_index = idx
            self._monster_template_fill_form(self.monster_template_working[idx])
        except Exception:
            pass

    def on_monster_template_import(self):
        """Import template image with option to copy to project assets."""
        path = filedialog.askopenfilename(
            title=self._t("monster_template_browse"),
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if not path:
            return

        # Ask if user wants to copy to project
        copy_to_project = messagebox.askyesno(
            self._t("monster_section"),
            "Copy image to project assets folder?\n\nYes: copy to assets/images/monsters/\nNo: use original path",
            default="yes",
        )

        if copy_to_project:
            try:
                # Create target directory
                assets_dir = Path(__file__).parent / "assets" / "images" / "monsters"
                assets_dir.mkdir(parents=True, exist_ok=True)

                # Generate unique filename
                import time as time_module

                monster_name = self.monster_name_var.get().strip() or "monster"
                # Sanitize monster name for filename
                safe_name = "".join(
                    c if c.isalnum() or c in ("_", "-") else "_"
                    for c in monster_name.lower()
                )
                timestamp = int(time_module.time() * 1000)
                ext = Path(path).suffix or ".png"
                new_filename = f"{safe_name}_{timestamp}{ext}"
                target_path = assets_dir / new_filename

                # Copy file
                import shutil

                shutil.copy2(path, target_path)

                # Use relative path
                try:
                    relative_path = target_path.relative_to(Path(__file__).parent)
                    path = str(relative_path).replace("\\", "/")
                except Exception:
                    path = str(target_path)

            except Exception as exc:
                messagebox.showerror(
                    self._t("monster_section"),
                    self._t("error_copy_image").format(exc=exc),
                )
                return

        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set("template")

    def on_monster_template_capture(self):
        """Capture screenshot using shared helper and update form fields."""
        if capture_region_and_save is None:
            messagebox.showerror(
                self._t("monster_section"),
                self._t("error_missing_library").format(exc="capture_helper"),
            )
            return
        try:
            monster_name = (
                self.monster_name_var.get().strip()
                if hasattr(self, "monster_name_var")
                else "monster"
            )
        except Exception:
            monster_name = "monster"
        parent_win = self.winfo_toplevel()
        # Avoid Tkinter grab conflicts during overlay selection
        had_grab = False
        try:
            try:
                self.grab_release()
                had_grab = True
            except Exception:
                had_grab = False
            result = capture_region_and_save(
                parent_win, Image is not None, monster_name, self.lang
            )
        except Exception as exc:
            try:
                messagebox.showerror(
                    self._t("error_title"),
                    self._t("error_screenshot_failed").format(exc=exc),
                )
            except Exception:
                pass
            return
        finally:
            try:
                if had_grab:
                    self.grab_set()
            except Exception:
                pass
        if not result:
            self.hunt_status.set(self._t("monster_template_capture_cancelled"))
            return
        path, (left, top, width, height) = result
        # Use relative path if under project dir
        try:
            base_dir = Path(__file__).parent
            rel = Path(path).resolve().relative_to(base_dir.resolve())
            path_str = str(rel).replace("\\", "/")
        except Exception:
            path_str = path
        self.monster_template_path_var.set(path_str)
        # Auto-fill name if empty
        if (
            hasattr(self, "monster_template_name_var")
            and not self.monster_template_name_var.get().strip()
        ):
            try:
                self.monster_template_name_var.set(Path(path_str).stem)
            except Exception:
                self.monster_template_name_var.set("template")
        # Ensure default threshold if empty
        if (
            hasattr(self, "monster_template_threshold_var")
            and not self.monster_template_threshold_var.get().strip()
        ):
            self.monster_template_threshold_var.set("0.85")
        # Fill region if blank
        if hasattr(self, "monster_template_region_vars") and not any(
            v.get().strip() for v in self.monster_template_region_vars.values()
        ):
            self.monster_template_region_vars["left"].set(str(left))
            self.monster_template_region_vars["top"].set(str(top))
            self.monster_template_region_vars["width"].set(str(width))
            self.monster_template_region_vars["height"].set(str(height))
        # Status
        try:
            filename = os.path.basename(path_str)
            self.hunt_status.set(
                self._t("monster_template_capture_success").format(filename=filename)
            )
        except Exception:
            pass

    def on_monster_template_add(self):
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError("path required")
        except Exception as exc:
            messagebox.showerror(
                self._t("monster_section"),
                self._t("monster_template_invalid").format(e=exc),
            )
            return
        for existing in self.monster_template_working:
            if existing.get("name", "").lower() == normalized["name"].lower():
                messagebox.showerror(
                    self._t("monster_section"), self._t("monster_template_duplicate")
                )
                return
        self.monster_template_working.append(normalized)
        self.monster_template_selected_index = len(self.monster_template_working) - 1
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t("monster_template_added"))

    def on_monster_template_update(self):
        if (
            self.monster_template_selected_index is None
            or self.monster_template_selected_index
            >= len(self.monster_template_working)
        ):
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_template_not_selected")
            )
            return
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError("path required")
        except Exception as exc:
            messagebox.showerror(
                self._t("monster_section"),
                self._t("monster_template_invalid").format(e=exc),
            )
            return
        for idx, existing in enumerate(self.monster_template_working):
            if idx == self.monster_template_selected_index:
                continue
            if existing.get("name", "").lower() == normalized["name"].lower():
                messagebox.showerror(
                    self._t("monster_section"), self._t("monster_template_duplicate")
                )
                return
        self.monster_template_working[self.monster_template_selected_index] = normalized
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t("monster_template_saved"))

    def on_monster_template_delete(self):
        if (
            self.monster_template_selected_index is None
            or self.monster_template_selected_index
            >= len(self.monster_template_working)
        ):
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_template_not_selected")
            )
            return
        self.monster_template_working.pop(self.monster_template_selected_index)
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self.hunt_status.set(self._t("monster_template_removed"))

    def on_monster_template_quick_add(self):
        path = filedialog.askopenfilename(
            title=self._t("monster_template_browse"),
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if not path:
            return
        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set("template")
        if not self.monster_template_threshold_var.get().strip():
            self.monster_template_threshold_var.set("0.85")

    def on_monster_template_preview_overlay(self):
        """Show preview window with template image, window_bounds and region overlay."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_template_no_image")
            )
            return

        # PIL check - should not reach here if button is disabled, but double-check
        if not self.pil_available:
            # Use showinfo instead of showerror for friendlier UX
            messagebox.showinfo(
                self._t("monster_section"), self._t("pil_not_installed_message")
            )
            return

        try:
            # Load template image
            # For type checkers: ensure PIL modules are available here
            assert Image is not None and ImageDraw is not None and ImageTk is not None
            img = Image.open(template_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            # Draw window_bounds if available
            wb = _normalize_window_bounds(
                {k: v.get().strip() for k, v in self.monster_bounds_vars.items()}
            )
            if wb:
                # Draw window bounds in blue
                left, top = wb.get("left", 0), wb.get("top", 0)
                width, height = wb.get("width", 0), wb.get("height", 0)
                draw.rectangle(
                    [left, top, left + width, top + height], outline="blue", width=2
                )
                draw.text((left + 5, top + 5), "Window Bounds", fill="blue")

            # Draw region if custom
            region_input = {
                k: v.get().strip() for k, v in self.monster_template_region_vars.items()
            }
            region = None
            if any(region_input.values()):
                region = _normalize_window_bounds(
                    region_input
                )  # reuse same normalization
                if region:
                    rl, rt = region.get("left", 0), region.get("top", 0)
                    rw, rh = region.get("width", 0), region.get("height", 0)
                    draw.rectangle([rl, rt, rl + rw, rt + rh], outline="red", width=3)
                    draw.text((rl + 5, rt + 5), "Region", fill="red")

            # Show in new window
            preview_win = tk.Toplevel(self)
            preview_win.title(self._t("monster_template_preview_overlay"))
            preview_win.geometry("800x600")

            # Scale to fit
            img.thumbnail((780, 550))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(preview_win)
            label.configure(image=photo)
            # Keep reference to prevent GC
            self._image_refs.append(photo)
            label.pack(pady=10)

            info_text = f"Template: {Path(template_path).name}"
            if wb:
                info_text += f"\nWindow Bounds: {wb}"
            if region:
                info_text += f"\nRegion: {region}"

            tk.Label(preview_win, text=info_text, justify="left").pack()
            tk.Button(
                preview_win, text=self._t("close"), command=preview_win.destroy
            ).pack(pady=10)

        except Exception as exc:
            messagebox.showerror(
                self._t("monster_section"), self._t("error_preview").format(exc=exc)
            )

    def on_monster_template_test_recognition(self):
        """Test template matching on current screen."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_template_no_image")
            )
            return

        try:
            import pyautogui
            import time as time_module
        except ImportError as exc:
            messagebox.showerror(
                self._t("monster_section"),
                self._t("error_missing_library").format(exc=exc),
            )
            return

        # Get threshold
        try:
            threshold_str = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_str) if threshold_str else 0.85
            threshold = max(0.0, min(threshold, 1.0))
        except ValueError:
            threshold = 0.85

        # Get region if specified
        region_input = {
            k: v.get().strip() for k, v in self.monster_template_region_vars.items()
        }
        region = None
        if all(region_input.values()):
            try:
                l = int(region_input["left"])
                t = int(region_input["top"])
                w = int(region_input["width"])
                h = int(region_input["height"])
                region = (l, t, w, h)
            except (ValueError, KeyError):
                region = None

        # Show status
        self.hunt_status.set(self._t("monster_template_test_running"))
        self.update()

        # Minimize window briefly
        if self.monster_manager_win:
            self.monster_manager_win.iconify()

        time_module.sleep(0.5)  # Brief pause

        try:
            # Try to locate on screen using template_matcher
            result = None
            confidence_val = None

            # Use locate_template for accurate confidence tracking
            box_and_conf = locate_template(
                template_path=template_path, threshold=threshold, region=region
            )

            # Restore window
            if self.monster_manager_win:
                self.monster_manager_win.deiconify()

            if box_and_conf and box_and_conf[0] is not None:
                box, confidence_val = box_and_conf

                # Create a Box-like object for compatibility
                class Box:
                    def __init__(self, left, top, width, height):
                        self.left = left
                        self.top = top
                        self.width = width
                        self.height = height

                assert box is not None
                result = Box(box[0], box[1], box[2], box[3])

                # Get center coordinates
                center_x = result.left + result.width // 2
                center_y = result.top + result.height // 2

                message = self._t("monster_template_test_found").format(
                    x=center_x, y=center_y, conf=confidence_val
                )

                # Show result with visual overlay
                result_win = tk.Toplevel(self)
                result_win.title(self._t("monster_template_test_recognition"))
                result_win.geometry("400x300")

                tk.Label(
                    result_win,
                    text="✅ " + message,
                    fg="green",
                    font=("Arial", 10, "bold"),
                ).pack(pady=10)

                details = f"Box: ({result.left}, {result.top}, {result.width}, {result.height})\n"
                details += f"Center: ({center_x}, {center_y})\n"
                details += f"Threshold: {threshold:.2f}\n"
                if region:
                    details += f"Region: {region}"

                tk.Label(
                    result_win, text=details, justify="left", font=("Courier", 9)
                ).pack(pady=10)

                # Try to capture and show the match
                try:
                    screenshot = pyautogui.screenshot(
                        region=(result.left, result.top, result.width, result.height)
                    )
                    screenshot.thumbnail((200, 200))

                    if ImageTk is not None:
                        photo = ImageTk.PhotoImage(screenshot)
                        img_label = tk.Label(result_win)
                        img_label.configure(image=photo)
                        self._image_refs.append(photo)
                        img_label.pack(pady=10)
                except Exception:
                    pass

                tk.Button(
                    result_win, text=self._t("close"), command=result_win.destroy
                ).pack(pady=10)

                self.hunt_status.set(message)

            else:
                # Restore window
                if self.monster_manager_win:
                    self.monster_manager_win.deiconify()

                message = self._t("monster_template_test_not_found").format(
                    threshold=threshold
                )
                messagebox.showinfo(
                    self._t("monster_template_test_recognition"),
                    message
                    + "\n\nTry:\n• Lower threshold\n• Adjust region\n• Ensure target is visible",
                )
                self.hunt_status.set(message)

        except Exception as exc:
            # Restore window
            if self.monster_manager_win:
                try:
                    self.monster_manager_win.deiconify()
                except Exception:
                    pass

            error_msg = self._t("monster_template_test_error").format(error=str(exc))
            messagebox.showerror(self._t("monster_section"), error_msg)
            self.hunt_status.set(error_msg)

    def _monster_clear_form(self):
        if hasattr(self, "monster_name_var"):
            self.monster_name_var.set("")
        if hasattr(self, "monster_hp_var"):
            self.monster_hp_var.set("")
        if hasattr(self, "monster_damage_var"):
            self.monster_damage_var.set("")
        if hasattr(self, "monster_template_var"):
            self.monster_template_var.set("")
        if hasattr(self, "monster_estimate_var"):
            self.monster_estimate_var.set("")
        self._monster_desc_set("")
        for var in self.monster_bounds_vars.values():
            var.set("")
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self._monster_template_clear_form()
        self._refresh_monster_template_list()

    def _format_number(self, value):
        try:
            num = float(value)
        except (TypeError, ValueError):
            return ""
        if math.isclose(num, round(num), rel_tol=1e-9, abs_tol=1e-9):
            return str(int(round(num)))
        return f"{num:.2f}".rstrip("0").rstrip(".")

    def _monster_fill_form(self, monster):
        if not monster:
            self._monster_clear_form()
            return
        if hasattr(self, "monster_name_var"):
            self.monster_name_var.set(monster.get("name", ""))
        if hasattr(self, "monster_hp_var"):
            self.monster_hp_var.set(self._format_number(monster.get("hp", "")))
        if hasattr(self, "monster_damage_var"):
            self.monster_damage_var.set(
                self._format_number(monster.get("damage_per_hit", ""))
            )
        if hasattr(self, "monster_template_var"):
            self.monster_template_var.set(monster.get("template", ""))
        self._monster_desc_set(monster.get("description", ""))
        bounds = (
            monster.get("window_bounds")
            if isinstance(monster.get("window_bounds"), dict)
            else None
        )
        for key, var in self.monster_bounds_vars.items():
            if bounds and key in bounds:
                var.set(str(bounds.get(key, "")))
            else:
                var.set("")
        self.monster_template_working = copy.deepcopy(
            _sanitize_templates(monster.get("templates"))
        )
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self._update_monster_estimate_label(monster)

    def _open_monster_manager(self):
        if (
            self.monster_manager_win is not None
            and self.monster_manager_win.winfo_exists()
        ):
            try:
                self.monster_manager_win.deiconify()
                self.monster_manager_win.lift()
                self.monster_manager_win.focus_set()
            except Exception:
                pass
            return

        win = tk.Toplevel(self)
        win.title(self._t("monster_section"))
        win.resizable(False, False)
        self.monster_manager_win = win

        def _on_close():
            if self.monster_manager_win is win:
                self.monster_manager_win = None
            self.monster_listbox = None
            self.monster_description_text = None
            self.monster_template_listbox = None
            self.monster_template_preview_label = None
            self.monster_template_preview_image = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)
        container = tk.Frame(win, padx=12, pady=12)
        container.grid(row=0, column=0, sticky="nsew")
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(container)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_rowconfigure(1, weight=1)

        tk.Label(sidebar, text=self._t("monster_list")).grid(
            row=0, column=0, sticky="w"
        )
        self.monster_listbox = tk.Listbox(
            sidebar, height=16, width=26, exportselection=False
        )
        self.monster_listbox.grid(row=1, column=0, sticky="ns")
        monster_scroll = tk.Scrollbar(
            sidebar, orient="vertical", command=self.monster_listbox.yview
        )
        monster_scroll.grid(row=1, column=1, sticky="ns")
        self.monster_listbox.config(yscrollcommand=monster_scroll.set)
        self.monster_listbox.bind("<<ListboxSelect>>", self.on_monster_selected)

        detail = tk.Frame(container)
        detail.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        detail.grid_columnconfigure(1, weight=1)
        detail.grid_rowconfigure(6, weight=1)

        info_frame = tk.Frame(detail)
        info_frame.grid(row=0, column=0, sticky="we")
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)

        tk.Label(info_frame, text=self._t("monster_name")).grid(
            row=0, column=0, sticky="e"
        )
        tk.Entry(info_frame, textvariable=self.monster_name_var, width=24).grid(
            row=0, column=1, sticky="we", padx=(4, 0)
        )
        tk.Button(
            info_frame,
            text=self._t("monster_estimate"),
            command=self.on_monster_estimate,
        ).grid(row=0, column=4, padx=(8, 0))

        tk.Label(info_frame, text=self._t("monster_hp")).grid(
            row=1, column=0, sticky="e", pady=(6, 0)
        )
        tk.Entry(info_frame, textvariable=self.monster_hp_var, width=12).grid(
            row=1, column=1, sticky="we", padx=(4, 0), pady=(6, 0)
        )

        tk.Label(info_frame, text=self._t("monster_damage")).grid(
            row=1, column=2, sticky="e", pady=(6, 0)
        )
        tk.Entry(info_frame, textvariable=self.monster_damage_var, width=12).grid(
            row=1, column=3, sticky="we", padx=(4, 0), pady=(6, 0)
        )

        tk.Button(
            info_frame,
            text=self._t("monster_calculate_timing"),
            command=self.on_monster_calculate_timing,
        ).grid(row=1, column=4, padx=(8, 0), pady=(6, 0))

        desc_label = tk.Label(detail, text=self._t("monster_description"))
        desc_label.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.monster_description_text = tk.Text(detail, width=46, height=4, wrap="word")
        self.monster_description_text.grid(row=2, column=0, sticky="we")
        tk.Label(detail, text=self._t("monster_description_hint"), fg="gray").grid(
            row=3, column=0, sticky="w"
        )

        bounds_frame = tk.Frame(detail)
        bounds_frame.grid(row=4, column=0, sticky="w", pady=(8, 0))
        bounds_label = tk.Label(bounds_frame, text=self._t("monster_bounds"))
        bounds_label.grid(row=0, column=0, columnspan=5, sticky="w")
        attach_i18n_tooltip(
            bounds_label,
            key="tooltip_window_bounds",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )
        headings = ["L", "T", "W", "H"]
        for idx, title in enumerate(headings):
            tk.Label(bounds_frame, text=title).grid(
                row=1, column=idx, padx=(0, 4), sticky="w"
            )
        tk.Entry(
            bounds_frame, textvariable=self.monster_bounds_vars["left"], width=6
        ).grid(row=2, column=0, padx=(0, 4))
        tk.Entry(
            bounds_frame, textvariable=self.monster_bounds_vars["top"], width=6
        ).grid(row=2, column=1, padx=(0, 4))
        tk.Entry(
            bounds_frame, textvariable=self.monster_bounds_vars["width"], width=6
        ).grid(row=2, column=2, padx=(0, 4))
        tk.Entry(
            bounds_frame, textvariable=self.monster_bounds_vars["height"], width=6
        ).grid(row=2, column=3, padx=(0, 10))
        tk.Button(
            bounds_frame,
            text=self._t("monster_bounds_clear"),
            command=self.on_monster_clear_bounds,
        ).grid(row=2, column=4)
        tk.Label(bounds_frame, text=self._t("monster_bounds_hint"), fg="gray").grid(
            row=3, column=0, columnspan=5, sticky="w", pady=(4, 0)
        )

        template_frame = tk.Frame(detail)
        template_frame.grid(row=5, column=0, sticky="we", pady=(8, 0))
        template_frame.grid_columnconfigure(1, weight=1)
        tk.Label(template_frame, text=self._t("monster_template")).grid(
            row=0, column=0, sticky="e"
        )
        tk.Entry(template_frame, textvariable=self.monster_template_var, width=32).grid(
            row=0, column=1, sticky="we", padx=(4, 0)
        )
        tk.Button(
            template_frame,
            text=self._t("browse"),
            command=self.on_monster_browse_template,
        ).grid(row=0, column=2, padx=(6, 0))
        tk.Button(
            template_frame,
            text=self._t("monster_open_templates"),
            command=self.on_monster_template_quick_add,
        ).grid(row=1, column=1, sticky="w", pady=(6, 0))

        templates_panel = tk.LabelFrame(detail, text=self._t("monster_templates"))
        templates_panel.grid(row=6, column=0, sticky="nsew", pady=(8, 0))
        templates_panel.grid_columnconfigure(2, weight=1)
        templates_panel.grid_rowconfigure(0, weight=1)

        self.monster_template_listbox = tk.Listbox(
            templates_panel, height=8, width=26, exportselection=False
        )
        self.monster_template_listbox.grid(row=0, column=0, rowspan=5, sticky="nsw")
        template_scroll = tk.Scrollbar(
            templates_panel,
            orient="vertical",
            command=self.monster_template_listbox.yview,
        )
        template_scroll.grid(row=0, column=1, rowspan=5, sticky="ns")
        self.monster_template_listbox.config(yscrollcommand=template_scroll.set)
        self.monster_template_listbox.bind(
            "<<ListboxSelect>>", self.on_monster_template_selected
        )

        template_form = tk.Frame(templates_panel)
        template_form.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        template_form.grid_columnconfigure(1, weight=1)

        tk.Label(template_form, text=self._t("monster_template_name")).grid(
            row=0, column=0, sticky="e"
        )
        tk.Entry(
            template_form, textvariable=self.monster_template_name_var, width=24
        ).grid(row=0, column=1, sticky="we", padx=(4, 0))

        tk.Label(template_form, text=self._t("monster_template_path")).grid(
            row=1, column=0, sticky="e", pady=(6, 0)
        )
        tk.Entry(
            template_form, textvariable=self.monster_template_path_var, width=24
        ).grid(row=1, column=1, sticky="we", padx=(4, 0), pady=(6, 0))
        self._ensure_monster_template_path_trace()
        path_btn_frame = tk.Frame(template_form)
        path_btn_frame.grid(row=1, column=2, padx=(6, 0), pady=(6, 0))
        tk.Button(
            path_btn_frame,
            text=self._t("monster_template_browse"),
            command=self.on_monster_template_import,
        ).pack(side="left")
        tk.Button(
            path_btn_frame,
            text=self._t("monster_template_capture"),
            command=self.on_monster_template_capture,
        ).pack(side="left", padx=(4, 0))

        tk.Label(template_form, text=self._t("monster_template_threshold")).grid(
            row=2, column=0, sticky="e"
        )
        threshold_entry = tk.Entry(
            template_form, textvariable=self.monster_template_threshold_var, width=8
        )
        threshold_entry.grid(row=2, column=1, sticky="w", padx=(4, 0))
        attach_i18n_tooltip(
            threshold_entry,
            key="tooltip_threshold",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )
        tk.Label(
            template_form, text=self._t("monster_template_threshold_hint"), fg="gray"
        ).grid(row=3, column=0, columnspan=3, sticky="w")

        region_frame = tk.Frame(template_form)
        region_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))
        tk.Label(region_frame, text=self._t("monster_template_region")).grid(
            row=0, column=0, columnspan=5, sticky="w"
        )
        headers = ["L", "T", "W", "H"]
        for idx, title in enumerate(headers):
            tk.Label(region_frame, text=title).grid(
                row=1, column=idx, padx=(0, 4), sticky="w"
            )
        tk.Entry(
            region_frame,
            textvariable=self.monster_template_region_vars["left"],
            width=5,
        ).grid(row=2, column=0, padx=(0, 4))
        tk.Entry(
            region_frame, textvariable=self.monster_template_region_vars["top"], width=5
        ).grid(row=2, column=1, padx=(0, 4))
        tk.Entry(
            region_frame,
            textvariable=self.monster_template_region_vars["width"],
            width=5,
        ).grid(row=2, column=2, padx=(0, 4))
        tk.Entry(
            region_frame,
            textvariable=self.monster_template_region_vars["height"],
            width=5,
        ).grid(row=2, column=3, padx=(0, 8))
        tk.Label(
            region_frame, text=self._t("monster_template_region_hint"), fg="gray"
        ).grid(row=3, column=0, columnspan=5, sticky="w", pady=(4, 0))

        preview_frame = tk.Frame(template_form)
        preview_frame.grid(row=5, column=0, columnspan=3, sticky="w", pady=(8, 0))
        # Increased preview size from 16x6 to 30x12 to accommodate 200x200 thumbnails
        self.monster_template_preview_label = tk.Label(
            preview_frame,
            text=self._t("skill_no_image"),
            width=30,
            height=12,
            relief="groove",
            bg="#f0f0f0",
        )
        self.monster_template_preview_label.pack(side="left")

        preview_btn_frame = tk.Frame(preview_frame)
        preview_btn_frame.pack(side="left", padx=(8, 0))

        # Preview overlay button - disable if PIL not available
        self.monster_preview_overlay_btn = tk.Button(
            preview_btn_frame,
            text=self._t("monster_template_preview_overlay"),
            command=self.on_monster_template_preview_overlay,
        )
        self.monster_preview_overlay_btn.pack(side="top", anchor="w")

        if not self.pil_available:
            self.monster_preview_overlay_btn.config(state="disabled")
            # Add tooltip explaining why disabled
            self._create_tooltip(
                self.monster_preview_overlay_btn, self._t("pil_required_tooltip")
            )

        tk.Button(
            preview_btn_frame,
            text=self._t("monster_template_test_recognition"),
            command=self.on_monster_template_test_recognition,
        ).pack(side="top", anchor="w", pady=(4, 0))

        tmpl_btn_frame = tk.Frame(template_form)
        tmpl_btn_frame.grid(row=6, column=0, columnspan=3, sticky="w", pady=(8, 0))
        tk.Button(
            tmpl_btn_frame,
            text=self._t("monster_template_add"),
            command=self.on_monster_template_add,
        ).pack(side="left")
        tk.Button(
            tmpl_btn_frame,
            text=self._t("monster_template_update"),
            command=self.on_monster_template_update,
        ).pack(side="left", padx=(6, 0))
        tk.Button(
            tmpl_btn_frame,
            text=self._t("monster_template_delete"),
            command=self.on_monster_template_delete,
        ).pack(side="left", padx=(6, 0))

        tk.Label(
            detail,
            textvariable=self.monster_estimate_var,
            fg="gray",
            wraplength=360,
            justify="left",
        ).grid(row=7, column=0, sticky="we", pady=(8, 0))

        btn_frame = tk.Frame(detail)
        btn_frame.grid(row=8, column=0, sticky="w", pady=(12, 0))
        tk.Button(
            btn_frame, text=self._t("monster_new"), command=self.on_monster_new
        ).pack(side="left")
        tk.Button(
            btn_frame, text=self._t("monster_save"), command=self.on_monster_save
        ).pack(side="left", padx=(6, 0))
        tk.Button(
            btn_frame, text=self._t("monster_delete"), command=self.on_monster_delete
        ).pack(side="left", padx=(6, 0))
        tk.Button(
            btn_frame,
            text=self._t("monster_use_template"),
            command=self.on_monster_use_for_hunt,
        ).pack(side="left", padx=(12, 0))

        self._refresh_monster_list(select_name=self.monster_selected_name)

    def _refresh_monster_select_options(self, select_name: Optional[str] = None):
        if select_name is not None:
            self.monster_selected_name = select_name
        names = [monster["name"] for monster in self.monsters]
        combo = getattr(self, "monster_select_combo", None)
        if combo is not None:
            combo["values"] = names
            target_name = self.monster_selected_name or (
                select_name if select_name in names else None
            )
            current = (
                self.monster_select_var.get()
                if hasattr(self, "monster_select_var")
                else ""
            )
            if target_name and target_name in names:
                self.monster_select_var.set(target_name)
            elif current not in names:
                self.monster_select_var.set(names[0] if names else "")
        self.on_monster_select_change()

    def _refresh_monster_list(self, select_name=None):
        if select_name is not None:
            self.monster_selected_name = select_name
        listbox = getattr(self, "monster_listbox", None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for monster in self.monsters:
                listbox.insert(tk.END, monster["name"])
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster["name"] == self.monster_selected_name:
                        idx = i
                        break
            if idx is None and self.monsters and self.monster_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.monsters):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.monster_selected_index = idx
                self.monster_selected_name = self.monsters[idx]["name"]
                self._monster_fill_form(self.monsters[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.monster_selected_index = None
                self._monster_clear_form()
        else:
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster["name"] == self.monster_selected_name:
                        idx = i
                        break
            self.monster_selected_index = idx if idx is not None else None
        self._refresh_monster_select_options(self.monster_selected_name)

    def on_monster_select_change(self, _evt=None):
        """Auto-apply monster config when selected from Hunt tab dropdown."""
        if not hasattr(self, "monster_select_var"):
            return
        name = self.monster_select_var.get().strip()
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster["name"] == name:
                idx = i
                break
        self.monster_selected_index = idx if idx is not None else None
        self.monster_selected_name = name if idx is not None else None

        if idx is not None:
            monster = self.monsters[idx]
            self._update_monster_estimate_label(monster)
            # Auto-apply monster config (templates, window_bounds, timing recommendations)
            self._apply_monster_to_hunt_quick(monster)
        elif hasattr(self, "monster_estimate_var"):
            self.monster_estimate_var.set("")

    def _apply_monster_to_hunt_quick(self, monster):
        """Apply monster templates and recommended settings to hunt config without opening manager."""
        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get("window_bounds"))
        self.current_window_bounds = bounds
        self.hunt_cfg["window_bounds"] = bounds
        self._update_window_bounds_display()

        # Apply templates[] array
        templates = _sanitize_templates(monster.get("templates"))
        if templates:
            self.hunt_cfg["templates"] = templates
            # Set legacy template_path to first template
            try:
                first_path = templates[0].get("path")
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg["template_path"] = first_path
            except Exception:
                pass
        elif monster.get("template"):
            # Fallback to old single template field
            self.template_var.set(monster["template"])
            self.hunt_cfg["template_path"] = monster["template"]
            self.hunt_cfg["templates"] = []

        # Apply recommended timing (if monster has HP/damage stats)
        try:
            stats = self._calculate_monster_estimate(monster)
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            self.attack_duration_var.set(f"{attack_min:.2f}")
            self.lost_timeout_var.set(f"{lost_timeout:.2f}")
        except Exception:
            pass  # Monster may not have complete stats, skip recommendations

        # Show brief notification
        if hasattr(self, "hunt_status"):
            template_count = (
                len(templates) if templates else (1 if monster.get("template") else 0)
            )
            msg = self._t("hunt_monster_auto_applied").format(
                name=monster.get("name", "")
            )
            if template_count > 0:
                msg += (
                    f" ({template_count} template{'s' if template_count > 1 else ''})"
                )
            self.hunt_status.set(msg)

    def on_monster_apply_from_select(self):
        if not hasattr(self, "monster_select_var"):
            return
        name = self.monster_select_var.get().strip()
        if not name:
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster["name"] == name:
                idx = i
                break
        if idx is None:
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        self.monster_selected_index = idx
        self.monster_selected_name = name
        self._update_monster_estimate_label(self.monsters[idx])
        self.on_monster_use_for_hunt()

    def _read_monster_form(self):
        if not hasattr(self, "monster_name_var"):
            raise ValueError("UI not ready")
        name = self.monster_name_var.get().strip()
        if not name:
            raise ValueError("name required")
        try:
            hp = float(self.monster_hp_var.get())
            dmg = float(self.monster_damage_var.get())
        except Exception as exc:
            raise ValueError(exc)
        if hp <= 0 or dmg <= 0:
            raise ValueError("values must be positive")
        template = (
            self.monster_template_var.get().strip()
            if hasattr(self, "monster_template_var")
            else ""
        )
        description = self._monster_desc_get()
        bounds_input = {k: v.get().strip() for k, v in self.monster_bounds_vars.items()}
        window_bounds = None
        if any(bounds_input.values()):
            if not all(bounds_input.values()):
                raise ValueError("window bounds require left/top/width/height")
            try:
                left = int(bounds_input["left"])
                top = int(bounds_input["top"])
                width = int(bounds_input["width"])
                height = int(bounds_input["height"])
            except ValueError as exc:
                raise ValueError(f"invalid window bounds: {exc}")
            if width <= 0 or height <= 0:
                raise ValueError("window bounds width/height must be positive")
            window_bounds = {"left": left, "top": top, "width": width, "height": height}
        templates = copy.deepcopy(_sanitize_templates(self.monster_template_working))
        return {
            "name": name,
            "hp": hp,
            "damage_per_hit": dmg,
            "template": template,
            "description": description,
            "window_bounds": window_bounds,
            "templates": templates,
        }

    def _current_attack_settings(self):
        try:
            press_ms = max(int(float(self.attack_press_var.get() or 0)), 1)
            attack_interval = max(float(self.attack_interval_var.get() or 0), 0.0)
        except Exception as exc:
            raise ValueError(exc)
        # Derive attack keys from skill_slots configured in hunt_cfg
        slots = self.hunt_cfg.get("skill_slots", []) or []
        attack_keys = [slot.get("key") for slot in slots if slot.get("key")]
        if not attack_keys:
            attack_keys = ["1"]
        return press_ms, attack_interval, attack_keys

    def _calculate_monster_estimate(self, monster):
        hp = float(monster.get("hp", 0))
        dmg = float(monster.get("damage_per_hit", 0))
        if hp <= 0 or dmg <= 0:
            raise ValueError("hp/damage must be positive")
        press_ms, attack_interval, attack_keys = self._current_attack_settings()
        per_hit_time = (press_ms / 1000.0) + attack_interval
        per_hit_time = max(per_hit_time, 0.05)
        hits_needed = max(1, math.ceil(hp / dmg))
        key_count = max(len(attack_keys), 1)
        cycles_needed = math.ceil(hits_needed / key_count)
        cycle_overhead = 0.02  # loop sleep between cycles
        kill_time = hits_needed * per_hit_time + cycles_needed * cycle_overhead
        dps = hp / kill_time if kill_time > 0 else 0.0
        return {
            "kill_time": kill_time,
            "dps": dps,
            "hits": hits_needed,
            "per_hit_time": per_hit_time,
            "key_count": key_count,
        }

    def _recommend_attack_settings(self, stats):
        per_hit_time = stats["per_hit_time"]
        kill_time = stats["kill_time"]
        attack_padding = max(per_hit_time, 0.3)
        attack_min = kill_time + attack_padding
        lost_timeout = min(max(per_hit_time * 3.0, 0.6), attack_min)
        return attack_min, lost_timeout

    def _update_monster_estimate_label(self, monster=None, stats=None):
        if not hasattr(self, "monster_estimate_var"):
            return
        try:
            if (
                monster is None
                and self.monster_selected_index is not None
                and self.monster_selected_index < len(self.monsters)
            ):
                monster = self.monsters[self.monster_selected_index]
            if monster is None:
                raise ValueError("no monster")
            if stats is None:
                stats = self._calculate_monster_estimate(monster)
            base = self._t("monster_estimate_result").format(
                time=stats["kill_time"], dps=stats["dps"]
            )
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            text = self._t("monster_estimate_detail").format(
                base=base, attack=attack_min, lost=lost_timeout
            )
        except Exception:
            text = ""
        self.monster_estimate_var.set(text)

    def on_monster_browse_template(self):
        path = filedialog.askopenfilename(
            title="Select template image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if path:
            self.monster_template_var.set(path)

    def on_monster_selected(self, _evt=None):
        if not self.monster_listbox:
            return
        try:
            idxs = self.monster_listbox.curselection()
            if not idxs:
                return
            idx = idxs[0]
            if idx >= len(self.monsters):
                return
            monster = self.monsters[idx]
            self.monster_selected_index = idx
            self.monster_selected_name = monster["name"]
            self._monster_fill_form(monster)
        except Exception:
            pass

    def on_monster_new(self):
        self.monster_selected_index = None
        self.monster_selected_name = None
        if self.monster_listbox:
            self.monster_listbox.selection_clear(0, tk.END)
        self._monster_clear_form()

    def on_monster_save(self):
        try:
            monster = self._read_monster_form()
        except Exception as e:
            messagebox.showerror(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return

        idx = self.monster_selected_index
        if idx is None:
            existing = next(
                (
                    i
                    for i, m in enumerate(self.monsters)
                    if m["name"].lower() == monster["name"].lower()
                ),
                None,
            )
            if existing is not None:
                idx = existing
                self.monsters[idx] = monster
            else:
                self.monsters.append(monster)
                idx = len(self.monsters) - 1
        else:
            for i, data in enumerate(self.monsters):
                if i != idx and data["name"].lower() == monster["name"].lower():
                    messagebox.showerror(
                        self._t("monster_section"), self._t("monster_duplicate")
                    )
                    return
            self.monsters[idx] = monster

        save_monster_library(self.monsters)
        self.monster_selected_index = idx
        self.monster_selected_name = monster["name"]
        self._refresh_monster_list(select_name=monster["name"])
        self.hunt_status.set(self._t("monster_saved"))

    def on_monster_delete(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(
            self.monsters
        ):
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        self.monsters.pop(self.monster_selected_index)
        save_monster_library(self.monsters)
        if self.monsters:
            next_name = self.monsters[
                min(self.monster_selected_index, len(self.monsters) - 1)
            ]["name"]
        else:
            next_name = None
        self.monster_selected_index = None
        self.monster_selected_name = next_name
        self._refresh_monster_list(select_name=next_name)
        self.hunt_status.set(self._t("monster_deleted"))

    def on_monster_calculate_timing(self):
        """Calculate and display timing recommendations based on monster HP and damage."""
        try:
            # Get HP and damage from form
            hp_str = self.monster_hp_var.get().strip()
            damage_str = self.monster_damage_var.get().strip()

            if not hp_str or not damage_str:
                messagebox.showinfo(
                    self._t("monster_timing_title"), self._t("monster_timing_no_stats")
                )
                return

            hp = float(hp_str)
            damage = float(damage_str)

            if hp <= 0 or damage <= 0:
                messagebox.showerror(
                    self._t("monster_timing_title"),
                    "HP and Damage must be greater than 0.",
                )
                return

            # Create dialog for attack speed selection
            dialog = tk.Toplevel(self)
            dialog.title(self._t("monster_timing_title"))
            dialog.geometry("550x550")
            dialog.transient(self)
            dialog.grab_set()

            # Keep dialog on top but below main app
            dialog.attributes("-topmost", False)
            self.lift()  # Keep main app on top

            # Attack speed selection
            speed_frame = tk.LabelFrame(
                dialog, text="Attack Speed Source", padx=10, pady=10
            )
            speed_frame.pack(fill="x", padx=10, pady=10)

            speed_var = tk.StringVar(value="from_skills")
            presets = get_timing_presets()

            # NEW: From Skills option (Recommended) - with visual indicator
            from_skills_frame = tk.Frame(
                speed_frame, bg="#E3F2FD", relief="solid", borderwidth=1
            )
            from_skills_frame.pack(fill="x", pady=2, padx=2)

            from_skills_rb = tk.Radiobutton(
                from_skills_frame,
                text="✓ From Skills (Recommended)",
                variable=speed_var,
                value="from_skills",
                font=("Arial", 9, "bold"),
                bg="#E3F2FD",
                activebackground="#BBDEFB",
                selectcolor="#2196F3",
                indicatoron=True,
                command=lambda: None,  # Will set after defining update_recommendations
            )
            from_skills_rb.pack(anchor="w", padx=5, pady=5)

            # Skill info label (will update dynamically)
            skill_info_label = tk.Label(
                from_skills_frame,
                text="",
                fg="#1976D2",
                font=("Arial", 8),
                bg="#E3F2FD",
                justify="left",
            )
            skill_info_label.pack(anchor="w", padx=(25, 5), pady=(0, 5))

            # Calculate from CONFIGURED skills (from hunt_config skill_slots)
            configured_skills = self.hunt_cfg.get("skill_slots", [])
            skills_data = load_skill_library()
            skill_dict = {s["name"]: s for s in skills_data}

            # Filter to get only ATTACK skills from configured skills
            attack_skill_names = []
            buff_skill_names = []
            for skill_slot in configured_skills:
                # Extract skill name from dict (skill_slots stores full skill objects)
                if isinstance(skill_slot, dict):
                    skill_name = skill_slot.get("name", "")
                    skill_type = skill_slot.get("type", "attack").lower()
                else:
                    # Fallback: if it's already a string
                    skill_name = skill_slot
                    # Look up type from library
                    if skill_name in skill_dict:
                        skill_type = (
                            skill_dict[skill_name].get("type", "attack").lower()
                        )
                    else:
                        skill_type = "attack"

                if skill_type == "attack":
                    attack_skill_names.append(skill_name)
                else:
                    buff_skill_names.append(skill_name)

            if attack_skill_names:
                aps, avg_cd, count = calculate_attack_speed_from_skills(
                    attack_skill_names
                )
                if aps is not None:
                    skill_details = (
                        f"✓ {count} attack skill(s) | Avg CD: {avg_cd:.2f}s | APS: {aps:.2f} hits/sec"
                        if self.lang == "en"
                        else f"✓ {count} kỹ năng tấn công | CD TB: {avg_cd:.2f}s | TĐ: {aps:.2f} đòn/giây"
                    )
                    if buff_skill_names:
                        buff_count = len(buff_skill_names)
                        skill_details += (
                            f"\n  ({buff_count} buff skill(s) excluded from calculation)"
                            if self.lang == "en"
                            else f"\n  ({buff_count} kỹ năng buff không tính vào)"
                        )
                    skill_info_label.config(text=skill_details)
                else:
                    skill_info_label.config(
                        text=(
                            "⚠ No valid attack skills found"
                            if self.lang == "en"
                            else "⚠ Không tìm thấy kỹ năng tấn công hợp lệ"
                        )
                    )
            else:
                no_skills_msg = (
                    "⚠ No attack skills configured\n  Please add skills in Hunt tab first"
                    if self.lang == "en"
                    else "⚠ Chưa thiết lập kỹ năng tấn công\n  Vui lòng thêm kỹ năng ở tab Hunt trước"
                )
                skill_info_label.config(text=no_skills_msg)

            # Separator
            ttk.Separator(speed_frame, orient="horizontal").pack(fill="x", pady=(8, 8))

            # Manual presets header
            preset_label = tk.Label(
                speed_frame,
                text=self._t("timing_manual_presets"),
                font=("Arial", 9),
                fg="#666",
            )
            preset_label.pack(anchor="w", pady=(0, 4))

            for preset_name, (aps, desc) in presets.items():
                rb = tk.Radiobutton(
                    speed_frame,
                    text=f"  {preset_name.replace('_', ' ').title()}: {desc}",
                    variable=speed_var,
                    value=preset_name,
                    command=lambda: update_recommendations(),
                )
                rb.pack(anchor="w", pady=2)

            # Custom speed
            custom_frame = tk.Frame(speed_frame)
            custom_frame.pack(fill="x", pady=(10, 0))
            tk.Radiobutton(
                custom_frame,
                text=self._t("custom_label"),
                variable=speed_var,
                value="custom",
                command=lambda: update_recommendations(),
            ).pack(side="left")
            custom_speed_var = tk.StringVar(value="2.0")
            custom_entry = tk.Entry(
                custom_frame, textvariable=custom_speed_var, width=8
            )
            custom_entry.pack(side="left", padx=5)
            custom_entry.bind(
                "<KeyRelease>",
                lambda e: (
                    update_recommendations() if speed_var.get() == "custom" else None
                ),
            )
            tk.Label(custom_frame, text=self._t("attacks_per_sec")).pack(side="left")

            # Result text
            result_frame = tk.LabelFrame(
                dialog, text=self._t("timing_results_title"), padx=10, pady=10
            )
            result_frame.pack(fill="both", expand=True, padx=10, pady=10)

            result_text = tk.Text(
                result_frame, width=65, height=15, wrap="word", font=("Consolas", 9)
            )
            result_text.pack(fill="both", expand=True)

            # Store current recommendation for Apply button
            current_rec: Dict[str, Any] = {"rec": None}

            def update_recommendations():
                """Calculate and display recommendations."""
                try:
                    preset = speed_var.get()

                    # Debug: Log preset value and type
                    print(f"DEBUG: preset = {preset!r}, type = {type(preset)}")

                    # NEW: Handle "from_skills" option
                    if preset == "from_skills":
                        # Get configured skills from hunt_config
                        configured_skills = self.hunt_cfg.get("skill_slots", [])
                        skills_data = load_skill_library()
                        skill_dict = {s["name"]: s for s in skills_data}

                        # Separate attack and buff skills
                        attack_skill_names = []
                        buff_skill_names = []
                        for skill_slot in configured_skills:
                            # Extract skill name from dict (skill_slots stores full skill objects)
                            if isinstance(skill_slot, dict):
                                skill_name = skill_slot.get("name", "")
                                skill_type = skill_slot.get("type", "attack").lower()
                            else:
                                # Fallback: if it's already a string
                                skill_name = skill_slot
                                # Look up type from library
                                if skill_name in skill_dict:
                                    skill_type = (
                                        skill_dict[skill_name]
                                        .get("type", "attack")
                                        .lower()
                                    )
                                else:
                                    skill_type = "attack"

                            if skill_type == "attack":
                                attack_skill_names.append(skill_name)
                            else:
                                buff_skill_names.append(skill_name)

                        aps, avg_cd, count = calculate_attack_speed_from_skills(
                            attack_skill_names
                        )

                        if aps is None or count == 0:
                            result_text.delete("1.0", tk.END)
                            error_msg = self._t("timing_no_attack_skills_configured")
                            result_text.insert("1.0", error_msg)
                            current_rec["rec"] = None
                            return

                        # Show detailed skill-based info with breakdown
                        skill_info = self._t("timing_from_skills_title")
                        skill_info += self._t("timing_attack_skills_list").format(
                            count=count, names=", ".join(attack_skill_names)
                        )
                        if buff_skill_names:
                            skill_info += self._t("timing_buff_skills_list").format(
                                count=len(buff_skill_names),
                                names=", ".join(buff_skill_names),
                            )
                        skill_info += "\n"
                        skill_info += self._t("timing_attack_calc_header")
                        skill_info += self._t("timing_avg_cooldown").format(avg=avg_cd)
                        skill_info += self._t("timing_effective_aps").format(aps=aps)
                        skill_info += "\n"

                    elif preset == "custom":
                        aps = float(custom_speed_var.get())
                        skill_info = ""
                    else:
                        # Debug: Check presets dict
                        print(f"DEBUG: presets keys = {list(presets.keys())}")
                        print(f"DEBUG: Looking for preset '{preset}' in presets")
                        if preset not in presets:
                            raise ValueError(f"Invalid preset: {preset!r}")
                        aps = presets[preset][0]
                        skill_info = ""

                    # Calculate timing
                    rec = calculate_timing(hp, damage, aps)
                    current_rec["rec"] = rec  # Store for Apply button
                    formatted = format_timing_recommendation(rec, self.lang)

                    # Display results
                    result_text.delete("1.0", tk.END)
                    if skill_info:
                        result_text.insert("1.0", skill_info)
                    result_text.insert(tk.END, f"{rec}\n\n")
                    result_text.insert(tk.END, "=" * 60 + "\n")
                    result_text.insert(tk.END, formatted["summary"])

                except Exception as e:
                    import traceback

                    error_trace = traceback.format_exc()
                    print(f"ERROR in update_recommendations:\n{error_trace}")
                    result_text.delete("1.0", tk.END)
                    result_text.insert(
                        "1.0", f"Error: {e}\n\nFull traceback:\n{error_trace}"
                    )
                    current_rec["rec"] = None

            def apply_to_hunt_config():
                """Apply current recommendations to hunt_config.json."""
                if current_rec["rec"] is None:
                    messagebox.showwarning(
                        self._t("monster_timing_title"),
                        self._t("timing_calculate_first"),
                    )
                    return

                try:
                    rec = current_rec["rec"]

                    # Update hunt config
                    self.hunt_cfg["lost_timeout_sec"] = rec.lost_timeout_sec
                    self.hunt_cfg["attack_min_duration_sec"] = (
                        rec.attack_min_duration_sec
                    )

                    # Update UI
                    self.lost_timeout_var.set(f"{rec.lost_timeout_sec:.2f}")
                    self.attack_duration_var.set(f"{rec.attack_min_duration_sec:.2f}")

                    # Save to file
                    save_hunt_config(self.hunt_cfg)

                    # Show success message
                    msg = self._t("timing_applied_message").format(
                        lost=rec.lost_timeout_sec, attack=rec.attack_min_duration_sec
                    )

                    messagebox.showinfo(self._t("monster_timing_title"), msg)

                    self.hunt_status.set(
                        f"Timing applied: lost={rec.lost_timeout_sec:.2f}s, attack={rec.attack_min_duration_sec:.2f}s"
                    )

                except Exception as e:
                    messagebox.showerror(
                        self._t("error_title"), f"Failed to apply: {e}"
                    )

            # Buttons
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(fill="x", padx=10, pady=(0, 10))

            from ui.helpers.button_styles import get_button_config

            tk.Button(
                btn_frame,
                text=self._t("btn_calculate"),
                command=update_recommendations,
                **get_button_config("blue"),
            ).pack(side="left", padx=5)

            tk.Button(
                btn_frame,
                text=self._t("btn_apply_to_hunt_config"),
                command=apply_to_hunt_config,
                **get_button_config("green"),
            ).pack(side="left", padx=5)

            tk.Button(btn_frame, text=self._t("close"), command=dialog.destroy).pack(
                side="left", padx=5
            )

            # Set callback for from_skills radio button (now that update_recommendations is defined)
            from_skills_rb.config(command=update_recommendations)

            # Initial calculation
            update_recommendations()

        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(f"ERROR in on_monster_calculate_timing:\n{error_trace}")
            messagebox.showerror(
                self._t("monster_timing_title"),
                f"Error: {e}\n\nCheck terminal for details.",
            )

    def on_monster_estimate(self):
        try:
            monster = self._read_monster_form()
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return
        self._update_monster_estimate_label(monster, stats)
        base = self._t("monster_estimate_result").format(
            time=stats["kill_time"], dps=stats["dps"]
        )
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        detail = self._t("monster_estimate_detail").format(
            base=base, attack=attack_min, lost=lost_timeout
        )
        self.hunt_status.set(detail)

    def on_monster_use_for_hunt(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(
            self.monsters
        ):
            messagebox.showinfo(
                self._t("monster_section"), self._t("monster_not_selected")
            )
            return
        monster = self.monsters[self.monster_selected_index]

        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get("window_bounds"))
        self.current_window_bounds = bounds
        self.hunt_cfg["window_bounds"] = bounds
        self._update_window_bounds_display()

        # Apply templates[] array to config
        templates = _sanitize_templates(monster.get("templates"))
        if templates:
            self.hunt_cfg["templates"] = templates
            # Also set legacy template_path to first template for backward compat
            try:
                first_path = templates[0].get("path")
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg["template_path"] = first_path
            except Exception:
                pass
        elif monster.get("template"):
            # Fallback to old single template field
            self.template_var.set(monster["template"])
            self.hunt_cfg["template_path"] = monster["template"]
            self.hunt_cfg["templates"] = []

        try:
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(
                self._t("monster_section"), self._t("monster_invalid").format(e=e)
            )
            return
        kill_time = stats["kill_time"]
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        self.attack_duration_var.set(f"{attack_min:.2f}")
        self.lost_timeout_var.set(f"{lost_timeout:.2f}")
        base = self._t("monster_estimate_result").format(
            time=kill_time, dps=stats["dps"]
        )
        detail = self._t("monster_estimate_detail").format(
            base=base, attack=attack_min, lost=lost_timeout
        )
        self.monster_estimate_var.set(detail)
        self.hunt_status.set(self._t("monster_applied"))

    # -----------------
    # Skill library helpers
    # -----------------
    def _skill_type_label(self, code: str) -> str:
        return (
            self._t("skill_type_buff")
            if code == "buff"
            else self._t("skill_type_attack")
        )

    def _skill_type_from_label(self, label: str) -> str:
        label = label.strip().lower()
        if label in (self._t("skill_type_buff").lower(), "buff"):
            return "buff"
        return "attack"

    def _ensure_skill_image_trace(self):
        if self._skill_image_trace:
            return

        def _trace(*_ignored):
            self._update_skill_preview(self.skill_image_var.get())

        self._skill_image_trace = self.skill_image_var.trace_add("write", _trace)
        # Sync immediately for current value
        self._update_skill_preview(self.skill_image_var.get())

    def _skill_clear_form(self):
        if hasattr(self, "skill_name_var"):
            self.skill_name_var.set("")
        if hasattr(self, "skill_key_var"):
            self.skill_key_var.set("")
        if hasattr(self, "skill_type_var"):
            self.skill_type_var.set(self._t("skill_type_attack"))
        if hasattr(self, "skill_cooldown_var"):
            self.skill_cooldown_var.set("")
        if hasattr(self, "skill_cast_time_var"):
            self.skill_cast_time_var.set("")
        if hasattr(self, "skill_duration_var"):
            self.skill_duration_var.set("")
        if hasattr(self, "skill_pre_refresh_var"):
            self.skill_pre_refresh_var.set("")
        if hasattr(self, "skill_image_var"):
            self.skill_image_var.set("")
        self._update_skill_preview("")
        self._toggle_buff_fields()

    def _skill_fill_form(self, skill):
        if not skill:
            self._skill_clear_form()
            return
        if hasattr(self, "skill_name_var"):
            self.skill_name_var.set(skill.get("name", ""))
        if hasattr(self, "skill_key_var"):
            self.skill_key_var.set(skill.get("key", ""))
        if hasattr(self, "skill_type_var"):
            self.skill_type_var.set(self._skill_type_label(skill.get("type", "attack")))
        if hasattr(self, "skill_cooldown_var"):
            self.skill_cooldown_var.set(self._format_number(skill.get("cooldown", "")))
        if hasattr(self, "skill_cast_time_var"):
            self.skill_cast_time_var.set(
                self._format_number(skill.get("cast_time", ""))
            )
        if hasattr(self, "skill_duration_var"):
            self.skill_duration_var.set(
                self._format_number(skill.get("duration_sec", ""))
            )
        if hasattr(self, "skill_pre_refresh_var"):
            self.skill_pre_refresh_var.set(
                self._format_number(skill.get("pre_refresh_sec", ""))
            )
        if hasattr(self, "skill_image_var"):
            self.skill_image_var.set(skill.get("image", ""))
        self._update_skill_preview(skill.get("image", ""))
        self._toggle_buff_fields()

    def _refresh_skill_list(self, select_name=None):
        if select_name is not None:
            self.skill_selected_name = select_name
        listbox = getattr(self, "skill_listbox", None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for skill in self.skills:
                listbox.insert(tk.END, skill["name"])
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill["name"] == self.skill_selected_name:
                        idx = i
                        break
            if idx is None and self.skills and self.skill_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.skills):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.skill_selected_index = idx
                self.skill_selected_name = self.skills[idx]["name"]
                self._skill_fill_form(self.skills[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.skill_selected_index = None
                self._skill_clear_form()
        else:
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill["name"] == self.skill_selected_name:
                        idx = i
                        break
            self.skill_selected_index = idx if idx is not None else None
        self._refresh_skill_slots_options()

    def _open_skill_manager(self):
        if self.skill_manager_win is not None and self.skill_manager_win.winfo_exists():
            try:
                self.skill_manager_win.deiconify()
                self.skill_manager_win.lift()
                self.skill_manager_win.focus_set()
            except Exception:
                pass
            return

        win = tk.Toplevel(self)
        win.title(self._t("skill_section"))
        win.resizable(False, False)
        self.skill_manager_win = win

        def _on_close():
            if self.skill_manager_win is win:
                self.skill_manager_win = None
            self.skill_listbox = None
            self.skill_preview_label = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)
        container = tk.Frame(win, padx=10, pady=10)
        container.grid(row=0, column=0, sticky="nsew")
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(4, weight=1)
        container.grid_rowconfigure(1, weight=1)

        tk.Label(container, text=self._t("skill_list")).grid(
            row=0, column=0, sticky="w"
        )
        self.skill_listbox = tk.Listbox(container, height=10, exportselection=False)
        self.skill_listbox.grid(row=1, column=0, rowspan=6, sticky="nswe", padx=(0, 4))
        skill_scroll = tk.Scrollbar(
            container, orient="vertical", command=self.skill_listbox.yview
        )
        skill_scroll.grid(row=1, column=1, rowspan=6, sticky="ns")
        self.skill_listbox.config(yscrollcommand=skill_scroll.set)
        self.skill_listbox.bind("<<ListboxSelect>>", self.on_skill_selected)

        tk.Label(container, text=self._t("skill_name")).grid(
            row=0, column=2, sticky="e"
        )
        tk.Entry(container, textvariable=self.skill_name_var, width=24).grid(
            row=0, column=3, sticky="we", padx=(4, 0)
        )

        tk.Label(container, text=self._t("skill_key")).grid(
            row=1, column=2, sticky="e", pady=(2, 0)
        )
        tk.Entry(container, textvariable=self.skill_key_var, width=12).grid(
            row=1, column=3, sticky="w", padx=(4, 0), pady=(2, 0)
        )
        # Capture key convenience: set key by pressing it while capture is active
        cap_btn = tk.Button(
            container,
            text=self._t("capture_key"),
            command=lambda: self._start_key_capture_for_skill(win),
        )
        cap_btn.grid(row=1, column=4, sticky="w", padx=(6, 0), pady=(2, 0))
        self._skill_key_capture_active = False

        tk.Label(container, text=self._t("skill_type")).grid(
            row=2, column=2, sticky="e"
        )
        self.skill_type_combo = ttk.Combobox(
            container, textvariable=self.skill_type_var, state="readonly", width=14
        )
        self.skill_type_combo["values"] = (
            self._t("skill_type_attack"),
            self._t("skill_type_buff"),
        )
        self.skill_type_combo.grid(row=2, column=3, sticky="w", padx=(4, 0))
        self.skill_type_combo.bind("<<ComboboxSelected>>", self._on_skill_type_changed)
        current_type = self._skill_type_from_label(
            self.skill_type_var.get() or self._t("skill_type_attack")
        )
        self.skill_type_var.set(self._skill_type_label(current_type))

        tk.Label(container, text=self._t("skill_cooldown")).grid(
            row=3, column=2, sticky="e"
        )
        tk.Entry(container, textvariable=self.skill_cooldown_var, width=12).grid(
            row=3, column=3, sticky="w", padx=(4, 0)
        )

        tk.Label(container, text=self._t("skill_cast_time")).grid(
            row=4, column=2, sticky="e"
        )
        tk.Entry(container, textvariable=self.skill_cast_time_var, width=12).grid(
            row=4, column=3, sticky="w", padx=(4, 0)
        )

        # Buff-specific fields (will be shown/hidden based on skill type)
        self.skill_duration_label = tk.Label(container, text=self._t("skill_duration"))
        self.skill_duration_entry = tk.Entry(
            container, textvariable=self.skill_duration_var, width=12
        )
        attach_i18n_tooltip(
            self.skill_duration_entry,
            key="skill_duration_hint",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        self.skill_pre_refresh_label = tk.Label(
            container, text=self._t("skill_pre_refresh")
        )
        self.skill_pre_refresh_entry = tk.Entry(
            container, textvariable=self.skill_pre_refresh_var, width=12
        )
        attach_i18n_tooltip(
            self.skill_pre_refresh_entry,
            key="skill_pre_refresh_hint",
            ns=I18N_GLOBAL,
            lang_provider=lambda: self.lang,
        )

        tk.Label(container, text=self._t("skill_image")).grid(
            row=7, column=2, sticky="e"
        )
        tk.Entry(container, textvariable=self.skill_image_var, width=24).grid(
            row=7, column=3, sticky="we", padx=(4, 0)
        )
        tk.Button(
            container, text=self._t("browse"), command=self.on_skill_browse_image
        ).grid(row=7, column=4, padx=(8, 0))

        # Increased preview size from 16x6 to 30x12 to accommodate 200x200 thumbnails
        self.skill_preview_label = tk.Label(
            container,
            text=self._t("skill_no_image"),
            width=30,
            height=12,
            relief="groove",
            bg="#f0f0f0",
        )
        self.skill_preview_label.grid(
            row=1, column=4, rowspan=6, sticky="nswe", padx=(8, 0)
        )
        self._ensure_skill_image_trace()

        btn_frame = tk.Frame(container)
        btn_frame.grid(row=8, column=2, columnspan=3, sticky="w", pady=(8, 0))
        tk.Button(btn_frame, text=self._t("skill_new"), command=self.on_skill_new).pack(
            side="left"
        )
        tk.Button(
            btn_frame, text=self._t("skill_save"), command=self.on_skill_save
        ).pack(side="left", padx=(6, 0))
        tk.Button(
            btn_frame, text=self._t("skill_delete"), command=self.on_skill_delete
        ).pack(side="left", padx=(6, 0))

        self._refresh_skill_list(select_name=self.skill_selected_name)

        # Initialize buff fields visibility
        self._toggle_buff_fields()

    def _start_key_capture_for_skill(self, win):
        """Enable a one-shot key capture for skill key assignment.

        Binds to the skill manager window and waits for a single Key press to set the
        `self.skill_key_var` value. Shows a small prompt in the window title while active.
        """
        if not win or not win.winfo_exists():
            return
        if getattr(self, "_skill_key_capture_active", False):
            return
        self._skill_key_capture_active = True
        original_title = win.title()
        win.title(self._t("press_any_key"))

        def _on_key(event):
            try:
                key = event.keysym or event.char
                if not key:
                    return
                # Normalize key to upper-case string, single character where appropriate
                key_str = str(key).upper()
                self.skill_key_var.set(key_str)
            finally:
                # Unbind and restore title
                try:
                    win.unbind("<Key>")
                except Exception:
                    pass
                win.title(original_title)
                self._skill_key_capture_active = False

        # Bind to Key events on the skill manager window
        win.bind("<Key>", _on_key)

    def _on_skill_type_changed(self, event=None):
        """Handle skill type change to show/hide buff-specific fields."""
        self._toggle_buff_fields()

    def _toggle_buff_fields(self):
        """Show/hide buff duration fields based on skill type."""
        if not hasattr(self, "skill_duration_label"):
            return

        skill_type = self._skill_type_from_label(self.skill_type_var.get())
        is_buff = skill_type == "buff"

        if is_buff:
            # Show buff fields
            self.skill_duration_label.grid(row=5, column=2, sticky="e")
            self.skill_duration_entry.grid(row=5, column=3, sticky="w", padx=(4, 0))
            self.skill_pre_refresh_label.grid(row=6, column=2, sticky="e")
            self.skill_pre_refresh_entry.grid(row=6, column=3, sticky="w", padx=(4, 0))
        else:
            # Hide buff fields
            self.skill_duration_label.grid_forget()
            self.skill_duration_entry.grid_forget()
            self.skill_pre_refresh_label.grid_forget()
            self.skill_pre_refresh_entry.grid_forget()

    def _refresh_skill_slots_options(self):
        if not hasattr(self, "skill_slot_boxes"):
            return
        names = []
        for skill in self.skills:
            if skill["name"] not in names:
                names.append(skill["name"])
        for saved in getattr(self, "skill_slot_saved_names", []):
            if saved and saved not in names:
                names.append(saved)
        values = [""] + names
        for cmb in self.skill_slot_boxes:
            cmb["values"] = values
        # Also refresh key labels next to each slot
        try:
            self._refresh_slot_key_labels()
        except Exception:
            pass

    def _load_skill_slots_from_cfg(self):
        saved = (
            self.hunt_cfg.get("skill_slots", []) if hasattr(self, "hunt_cfg") else []
        )

        # Handle both formats: list of strings (old) and list of dicts (new)
        normalized_slots = []
        for slot in saved:
            if isinstance(slot, dict):
                # New format: {"name": "skill_name"}
                normalized_slots.append(slot.get("name", ""))
            elif isinstance(slot, str):
                # Old format: "skill_name"
                normalized_slots.append(slot)
            else:
                normalized_slots.append("")

        # Extract non-empty names for saved skills
        self.skill_slot_saved_names = [name for name in normalized_slots if name]

        self._refresh_skill_slots_options()

        # Load saved slots into UI
        for idx, var in enumerate(self.skill_slot_vars):
            name = ""
            if idx < len(normalized_slots):
                name = normalized_slots[idx]
            var.set(name)

        self._update_attack_keys_from_slots()

    def _collect_skill_slots(self):
        if not self.skill_slot_vars:
            self.skill_slot_saved_names = []
            return []
        mapping = {skill["name"]: skill for skill in self.skills}
        slots = []
        saved_names = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            saved_names.append(name)
            slots.append(
                {
                    "name": skill["name"],
                    "key": skill["key"],
                    "type": skill.get("type", "attack"),
                    "cooldown": float(skill.get("cooldown", 0.0)),
                    "cast_time": float(skill.get("cast_time", 0.0)),
                    "image": skill.get("image", ""),
                }
            )
        self.skill_slot_saved_names = saved_names
        return slots

    def _refresh_slot_key_labels(self):
        """Update the small labels next to each skill slot to show the assigned key for the selected skill."""
        if not hasattr(self, "skill_slot_key_labels") or not hasattr(
            self, "skill_slot_vars"
        ):
            return
        # Build a mapping from skill name -> key
        name_to_key = {s.get("name", ""): s.get("key", "") for s in self.skills}
        for i, var in enumerate(self.skill_slot_vars):
            name = var.get().strip()
            key = name_to_key.get(name, "")
            lbl = (
                self.skill_slot_key_labels[i]
                if i < len(self.skill_slot_key_labels)
                else None
            )
            if lbl:
                lbl.config(text=(key or ""))

    def _clear_skill_slot(self, var):
        var.set("")
        self._update_attack_keys_from_slots()

    def _update_skill_preview(self, path):
        label = getattr(self, "skill_preview_label", None)
        if not label:
            return
        path = (path or "").strip()
        if not path:
            label.config(image="", text=self._t("skill_no_image"))
            self.skill_preview_image = None
            return

        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.config(image=photo, text="")
            self.skill_preview_image = photo
            return

        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(path)
                img.thumbnail(
                    (200, 200)
                )  # Increased from 96x96 to 200x200 for better visibility
                photo = ImageTk.PhotoImage(img)
            else:
                # Fallback to tk.PhotoImage if PIL not available
                photo = tk.PhotoImage(file=path)
            self._thumbnail_cache[path] = photo  # Cache it
            label.config(image=photo, text="")
            self.skill_preview_image = photo
        except Exception as e:
            # Better error handling with specific message
            error_msg = str(e) if str(e) else self._t("skill_image_error")
            label.config(image="", text=f"❌ {error_msg[:50]}...")
            self.skill_preview_image = None

    def _update_attack_keys_from_slots(self):
        # attack_keys removed: update saved slot names and refresh options
        self.skill_slot_saved_names = [
            v.get().strip() for v in self.skill_slot_vars if v.get().strip()
        ]
        self._refresh_skill_slots_options()

    def on_skill_browse_image(self):
        path = filedialog.askopenfilename(
            title="Select skill image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
        )
        if path:
            self.skill_image_var.set(path)

    def on_skill_selected(self, _evt=None):
        if not self.skill_listbox:
            return
        try:
            idxs = self.skill_listbox.curselection()
            if not idxs:
                return
            idx = idxs[0]
            if idx >= len(self.skills):
                return
            skill = self.skills[idx]
            self.skill_selected_index = idx
            self.skill_selected_name = skill["name"]
            self._skill_fill_form(skill)
        except Exception:
            pass

    def _read_skill_form(self):
        if not hasattr(self, "skill_name_var"):
            raise ValueError("UI not ready")
        name = self.skill_name_var.get().strip()
        if not name:
            raise ValueError("name required")
        key = self.skill_key_var.get().strip().upper()
        if not key:
            raise ValueError("key required")
        type_label = (
            self.skill_type_var.get().strip()
            if hasattr(self, "skill_type_var")
            else self._t("skill_type_attack")
        )
        skill_type = self._skill_type_from_label(type_label)
        try:
            cooldown = float(self.skill_cooldown_var.get() or 0)
            cast_time = float(self.skill_cast_time_var.get() or 0)

            # Buff-specific fields
            duration_sec = 0.0
            pre_refresh_sec = 0.0

            if skill_type == "buff":
                # Validate buff duration is required for buff skills
                duration_str = (
                    self.skill_duration_var.get().strip()
                    if hasattr(self, "skill_duration_var")
                    else ""
                )
                if not duration_str:
                    raise ValueError("Buff duration is required for buff skills")
                duration_sec = float(duration_str)
                if duration_sec <= 0:
                    raise ValueError("Buff duration must be greater than 0")

                # Pre-refresh is optional but should be validated if provided
                pre_refresh_str = (
                    self.skill_pre_refresh_var.get().strip()
                    if hasattr(self, "skill_pre_refresh_var")
                    else ""
                )
                if pre_refresh_str:
                    pre_refresh_sec = float(pre_refresh_str)
                    if pre_refresh_sec < 0:
                        raise ValueError("Pre-refresh time cannot be negative")
                    if pre_refresh_sec >= duration_sec:
                        raise ValueError(
                            "Pre-refresh time must be less than buff duration"
                        )

        except ValueError as exc:
            raise exc
        except Exception as exc:
            raise ValueError(exc)

        image = (
            self.skill_image_var.get().strip()
            if hasattr(self, "skill_image_var")
            else ""
        )
        return {
            "name": name,
            "key": key,
            "type": skill_type,
            "cooldown": max(cooldown, 0.0),
            "cast_time": max(cast_time, 0.0),
            "duration_sec": duration_sec,
            "pre_refresh_sec": pre_refresh_sec,
            "hold_ms": None,  # Keep existing schema field
            "image": image,
        }

    def on_skill_new(self):
        self.skill_selected_index = None
        self.skill_selected_name = None
        if self.skill_listbox:
            self.skill_listbox.selection_clear(0, tk.END)
        self._skill_clear_form()

    def on_skill_save(self):
        try:
            skill = self._read_skill_form()
        except Exception as e:
            messagebox.showerror(
                self._t("skill_section"), self._t("skill_invalid").format(e=e)
            )
            return

        idx = self.skill_selected_index
        if idx is None:
            existing = next(
                (
                    i
                    for i, s in enumerate(self.skills)
                    if s["name"].lower() == skill["name"].lower()
                ),
                None,
            )
            if existing is not None:
                idx = existing
                self.skills[idx] = skill
            else:
                self.skills.append(skill)
                idx = len(self.skills) - 1
        else:
            for i, data in enumerate(self.skills):
                if i != idx and data["name"].lower() == skill["name"].lower():
                    messagebox.showerror(
                        self._t("skill_section"), self._t("skill_duplicate")
                    )
                    return
            self.skills[idx] = skill

        save_skill_library(self.skills)
        self.skill_selected_index = idx
        self.skill_selected_name = skill["name"]
        self._refresh_skill_list(select_name=skill["name"])
        self._update_attack_keys_from_slots()
        try:
            self._refresh_slot_key_labels()
        except Exception:
            pass
        # Validate duplicate keys across skill library and slots
        try:
            self._validate_slot_key_duplicates()
        except Exception:
            pass
        self.hunt_status.set(self._t("skill_saved"))

    def on_skill_delete(self):
        if self.skill_selected_index is None or self.skill_selected_index >= len(
            self.skills
        ):
            messagebox.showinfo(self._t("skill_section"), self._t("skill_not_selected"))
            return
        removed = self.skills.pop(self.skill_selected_index)
        save_skill_library(self.skills)
        for var in self.skill_slot_vars:
            if var.get().strip() == removed["name"]:
                var.set("")
        self.skill_slot_saved_names = [
            v.get().strip() for v in self.skill_slot_vars if v.get().strip()
        ]
        self.skill_selected_index = None
        self.skill_selected_name = None
        self._refresh_skill_list()
        self._update_attack_keys_from_slots()
        try:
            self._refresh_slot_key_labels()
        except Exception:
            pass
        try:
            self._validate_slot_key_duplicates()
        except Exception:
            pass
        self.hunt_status.set(self._t("skill_deleted"))

    def on_skill_slot_changed(self, _evt=None):
        self._update_attack_keys_from_slots()
        try:
            self._refresh_slot_key_labels()
        except Exception:
            pass
        try:
            self._validate_slot_key_duplicates()
        except Exception:
            pass

    def _validate_slot_key_duplicates(self):
        """Detect duplicate assigned keys across selected slots and update UI warnings.

        - Highlights slot key labels in red when duplicated.
        - Updates `hunt_status` with a concise warning message when duplicates exist.
        """
        if not hasattr(self, "skill_slot_vars") or not hasattr(
            self, "skill_slot_key_labels"
        ):
            return
        # map skill name -> key
        name_to_key = {s.get("name", ""): s.get("key", "") for s in self.skills}
        # collect keys for each slot
        keys = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            key = name_to_key.get(name, "")
            keys.append(key)

        # reverse mapping: key -> list of slot indices
        dup_map = {}
        for i, k in enumerate(keys):
            if not k:
                continue
            dup_map.setdefault(k, []).append(i + 1)  # 1-based slot index for display

        duplicates = {k: v for k, v in dup_map.items() if len(v) > 1}

        # Update label colors
        for i, lbl in enumerate(self.skill_slot_key_labels):
            k = keys[i] if i < len(keys) else ""
            if k and k in duplicates:
                lbl.config(fg="#D32F2F")  # red
            else:
                lbl.config(fg="#333")

        # Update status message
        if duplicates:
            msgs = []
            for k, idxs in duplicates.items():
                msgs.append(f"{k}: slots {', '.join(map(str, idxs))}")
            self.hunt_status.set("⚠️ Duplicate skill keys - " + "; ".join(msgs))
        else:
            # restore idle or previous short status
            # keep a short message to not overwrite more important status
            self.hunt_status.set(self._t("hunt_idle"))

    def update_skill_stats_display(self, stats_dict):
        """Update skill performance statistics display (Sprint 22 Patch 1).

        Args:
            stats_dict: Dictionary from SkillStats.get_all_stats() containing:
                {
                    'Skill Name': {
                        'cast_count': int,
                        'last_cast': float (timestamp) or None,
                        'time_since_last_cast': float (seconds) or None,
                        'success_rate': float (percentage)
                    },
                    ...
                }
        """
        if not hasattr(self, "skill_stats_tree"):
            return

        # Clear existing rows
        for item in self.skill_stats_tree.get_children():
            self.skill_stats_tree.delete(item)

        # Populate with current stats
        for skill_name, data in stats_dict.items():
            cast_count = data.get("cast_count", 0)
            time_since = data.get("time_since_last_cast")
            success_rate = data.get("success_rate", 0.0)

            # Format last cast time
            if time_since is None:
                last_cast_str = "Never"
            else:
                last_cast_str = self._t("time_ago_format").format(time=time_since)

            # Format cooldown status (simplified - just show "Ready" for now)
            # TODO: Integrate with actual skill cooldown data from skills.json
            cooldown_str = self._t("cooldown_ready")

            # Format success rate
            success_str = f"{success_rate:.1f}%"

            # Determine color tag based on success rate
            if success_rate >= 90:
                tag = "excellent"
            elif success_rate >= 70:
                tag = "good"
            else:
                tag = "poor"

            # Insert row
            self.skill_stats_tree.insert(
                "",
                "end",
                values=(
                    skill_name,
                    cast_count,
                    last_cast_str,
                    cooldown_str,
                    success_str,
                ),
                tags=(tag,),
            )

    def _prepare_skill_runtime(self, cfg):
        runtime = []
        slots = cfg.get("skill_slots") or []
        default_press = int(cfg.get("attack_press_ms", 60))
        for slot in slots:
            key = str(slot.get("key", "")).strip().upper()
            if not key:
                continue
            cooldown = max(float(slot.get("cooldown", 0.0)), 0.0)
            cast_time = max(float(slot.get("cast_time", 0.0)), 0.0)
            press_ms = max(int(cast_time * 1000), 30)
            if press_ms < default_press:
                press_ms = default_press
            press_ms = min(press_ms, 2000)
            runtime.append(
                {
                    "name": slot.get("name", ""),
                    "key": key,
                    "type": slot.get("type", "attack"),
                    "cooldown": cooldown,
                    "cast_time": cast_time,
                    "press_ms": press_ms,
                    "next_ready": 0.0,
                }
            )
        return runtime

    def _try_cast_skills(
        self, runtime, now, target_available, attack_phase, skill_stats=None
    ):
        """Cast skills based on runtime configuration.

        Args:
            runtime: List of skill configurations
            now: Current timestamp
            target_available: Whether target is available
            attack_phase: Whether in attack phase
            skill_stats: SkillStats instance for training mode tracking (optional)

        Sprint 22 Patch 1: Added skill_stats parameter for training mode.
        """
        if not runtime:
            return

        # Debug log
        ready_skills = [s for s in runtime if now >= s["next_ready"]]
        if ready_skills:
            print(
                f"[Skills] Ready skills: {[s['name'] for s in ready_skills]}, target={target_available}, attack_phase={attack_phase}"
            )

        for skill in runtime:
            if now < skill["next_ready"]:
                continue
            skill_type = skill.get("type", "attack")
            if skill_type == "attack" and not (attack_phase and target_available):
                continue
            if skill_type == "buff" and attack_phase:
                # allow buffs even during attack phase, but no extra gating
                pass

            # Attempt to cast skill
            cast_success = False
            try:
                print(
                    f"[Skills] Casting {skill['name']} (key={skill['key']}, press_ms={skill['press_ms']})"
                )
                tap(skill["key"], skill["press_ms"])
                cast_success = True
                print(f"[Skills] ✓ Cast successful: {skill['name']}")
            except Exception as e:
                print(f"[Skills] ✗ Cast failed: {skill['name']} - {e}")
                pass

            # Sprint 22 Patch 1: Record skill cast in training mode
            if skill_stats and skill.get("name"):
                skill_stats.record_cast(skill["name"], success=cast_success)

            if not cast_success:
                continue

            cooldown = skill.get("cooldown", 0.0)
            skill["next_ready"] = time.time() + cooldown if cooldown > 0 else now
            sleep_extra = max(
                skill.get("cast_time", 0.0) - (skill["press_ms"] / 1000.0), 0.0
            )
            if sleep_extra > 0:
                end = time.time() + min(sleep_extra, 0.5)
                while time.time() < end and self.hunt_running:
                    time.sleep(0.02)

    def _validate_hunt_prerequisites(self) -> Optional[str]:
        """
        Validate prerequisites before starting hunt (PATCH 6).

        Returns:
            None if all checks pass, otherwise error message string.
        """
        errors = []

        # 1. Check window selected
        has_window = hasattr(self, "hunt_selected") and self.hunt_selected
        if not has_window:
            window_title = self.hunt_cfg.get("window_title", "").strip()
            if not window_title:
                errors.append("❌ No game window selected")
                errors.append("   → Click 'Find Windows' button to select your game")

        # 2. Check monster templates exist
        templates = self.hunt_cfg.get("templates", [])
        monster_list = self.hunt_cfg.get("monster_list", [])
        has_templates = len(templates) > 0
        has_monsters = len(monster_list) > 0

        if not has_templates and not has_monsters:
            errors.append("❌ No monster templates configured")
            errors.append("   → Go to Setup tab and add monster templates")
            errors.append("   → Or run Setup Wizard for guided configuration")

        # 3. Check skills configured (at least 1 attack skill)
        skill_slots = self.hunt_cfg.get("skill_slots", [])
        attack_skills = [
            s
            for s in skill_slots
            if s.get("enabled", True) and s.get("type", "attack") == "attack"
        ]

        if len(attack_skills) == 0:
            errors.append("❌ No attack skills configured")
            errors.append("   → Configure at least 1 attack skill in Setup tab")
            errors.append("   → Or press Ctrl+K to open Skill Manager")

        # 4. Check target key configured
        target_key = self.hunt_cfg.get("target_key", "").strip()
        if not target_key:
            errors.append("⚠️ No target key configured (will use default 'z')")

        if errors:
            return "\n".join(errors) + "\n\n💡 Fix these issues before starting hunt."

        return None

    def on_hunt_start(self):
        if self.hunt_running:
            return

        # ✅ PATCH 6: Prerequisites validation
        validation_error = self._validate_hunt_prerequisites()
        if validation_error:
            messagebox.showerror(self._t("error_title"), validation_error, parent=self)
            return

        try:
            cfg = self._hunt_from_ui()
        except Exception as e:
            messagebox.showerror(
                self._t("error_title"), self._t("invalid_hunt").format(e=e)
            )
            return
        save_hunt_config(cfg)
        self.hunt_cfg = cfg
        self.hunt_running = True

        # Update button states with enhanced visual feedback
        self.hunt_start_btn.config(
            state="disabled",
            bg="#A5D6A7",  # Light green when disabled
            relief="sunken",
            cursor="arrow",
        )
        self.hunt_stop_btn.config(
            state="normal",
            bg="#C62828",  # Bright red when active
            relief="raised",
            cursor="hand2",
        )
        self.hunt_status.set(self._t("hunt_running"))

        def worker():
            logger = get_hunt_logger()
            try:
                # Focus the target window; minimize GUI only if focus succeeded
                try:
                    focused = False
                    if self.hunt_selected and self.hunt_selected.get("hwnd"):
                        focused = self._bring_window_to_front_by_hwnd(
                            int(self.hunt_selected["hwnd"])
                        )
                    elif cfg.get("window_pid"):
                        focused = self._bring_window_to_front_by_pid(
                            int(cfg["window_pid"])
                        )
                    if not focused:
                        focused = self._bring_window_to_front(
                            cfg.get("window_title", "Cabal")
                        )
                    if focused:
                        try:
                            self.iconify()
                        except Exception:
                            pass
                    time.sleep(0.15)
                except Exception:
                    pass

                # Note: Global hotkeys (Ctrl+Shift+R/E) are registered in __init__()
                # No need to register hotkeys here anymore

                # Start logging
                logger.log_hunt_start(cfg)

                last_search = 0.0
                have_target = False
                mode = "search"
                last_seen = 0.0
                attack_started = 0.0
                lost_timeout = float(cfg.get("lost_timeout_sec", 0.8))
                attack_min_duration = float(cfg.get("attack_min_duration_sec", 1.5))
                skill_runtime = self._prepare_skill_runtime(cfg)
                has_attack_skills = any(
                    skill.get("type", "attack") != "buff" for skill in skill_runtime
                )
                last_match_info = None

                # Sprint 22 Patch 2: Training mode should NOT cycle targets (no Tab spam)
                training_mode_active = cfg.get("training_mode_enabled", False)
                skill_stats = SkillStats() if training_mode_active else None
                last_stats_update = 0.0
                stats_update_interval = 0.5  # Update UI every 0.5 seconds

                while self.hunt_running:
                    now = time.time()
                    if cfg.get("bring_to_front_each_cycle"):
                        ok = False
                        try:
                            if self.hunt_selected and self.hunt_selected.get("hwnd"):
                                ok = self._bring_window_to_front_by_hwnd(
                                    int(self.hunt_selected["hwnd"])
                                )
                            elif cfg.get("window_pid"):
                                ok = self._bring_window_to_front_by_pid(
                                    int(cfg["window_pid"])
                                )
                        except Exception:
                            ok = False
                        if not ok:
                            self._bring_window_to_front(
                                cfg.get("window_title", "Cabal")
                            )

                    # periodic detection with multi-template support
                    if now - last_search >= float(cfg["search_interval"]):
                        box, match_info = self._hunt_locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                            # Log template match with accurate confidence from template_matcher
                            if match_info and last_match_info != match_info:
                                # Log match details
                                template_name = (
                                    match_info.get("name")
                                    or Path(match_info.get("path", "")).stem
                                )
                                threshold = match_info.get("threshold", 0.8)
                                confidence = match_info.get("confidence", 0.0)
                                monster_name = match_info.get("monster_name", "")
                                logger.log_match(
                                    template_name,
                                    box,
                                    threshold,
                                    confidence,
                                    monster_name,
                                )

                                status_msg = (
                                    f"Target: {template_name} (conf: {confidence:.3f})"
                                )
                                self.hunt_status.set(status_msg)
                                last_match_info = match_info
                        else:
                            have_target = False
                            if last_match_info:
                                # Log target lost
                                duration = (
                                    now - attack_started if mode == "attack" else 0
                                )
                                template_name = (
                                    last_match_info.get("name")
                                    or Path(last_match_info.get("path", "")).stem
                                )
                                monster_name = last_match_info.get("monster_name", "")
                                logger.log_lost(template_name, monster_name, duration)

                                self.hunt_status.set(self._t("hunt_running"))
                                last_match_info = None
                        last_search = now

                    # Sprint 22 Patch 1: Update skill stats display periodically
                    if (
                        skill_stats
                        and (now - last_stats_update) >= stats_update_interval
                    ):
                        try:
                            all_stats = skill_stats.get_all_stats()
                            self.after(
                                0, lambda: self.update_skill_stats_display(all_stats)
                            )
                            last_stats_update = now
                        except Exception:
                            pass  # Ignore stats update errors

                    if skill_runtime:
                        print(
                            f"[Hunt] Search mode - Casting buffs only (have_target={have_target})"
                        )
                        self._try_cast_skills(
                            skill_runtime,
                            now,
                            have_target,
                            attack_phase=False,
                            skill_stats=skill_stats,
                        )

                    if mode == "search":
                        if have_target:
                            logger.log_state_change("search", "attack", "target_found")
                            mode = "attack"
                            attack_started = now
                            continue

                        # Sprint 22 Patch 2: Training mode SKIP target cycling
                        # Training dummy is stationary - no need to spam Tab/Z key
                        if not training_mode_active:
                            tap(cfg["target_key"])
                            time.sleep(float(cfg["target_cycle_delay"]))
                        else:
                            # Training mode: Just wait for template detection
                            time.sleep(0.1)
                        continue

                    # mode == 'attack'
                    if (
                        have_target
                        or (now - last_seen) <= lost_timeout
                        or (now - attack_started) <= attack_min_duration
                    ):
                        target_active = (
                            have_target
                            or (now - last_seen) <= lost_timeout
                            or (now - attack_started) <= attack_min_duration
                        )
                        print(
                            f"[Hunt] Attack mode - target_active={target_active}, have_target={have_target}, has_attack_skills={has_attack_skills}"
                        )
                        if skill_runtime and has_attack_skills:
                            # Ensure target is selected before casting attack skills
                            if target_active:
                                tap(
                                    cfg["target_key"]
                                )  # Press Z to ensure target locked
                                time.sleep(0.05)  # Small delay for target lock
                            self._try_cast_skills(
                                skill_runtime,
                                now,
                                target_active,
                                attack_phase=True,
                                skill_stats=skill_stats,
                            )
                            if not target_active:
                                logger.log_state_change(
                                    "attack", "search", "lost_timeout"
                                )
                                mode = "search"
                                time.sleep(0.05)
                                continue
                            time.sleep(float(cfg["attack_interval"]))
                            continue
                        # Fallback: if no skill_runtime (no skills), derive keys from skill_slots
                        fallback_keys = [
                            s.get("key")
                            for s in cfg.get("skill_slots", [])
                            if s.get("key")
                        ]
                        if not fallback_keys:
                            fallback_keys = ["1"]
                        for k in fallback_keys:
                            if not self.hunt_running:
                                break
                            try:
                                tap(k, int(cfg["attack_press_ms"]))
                            except Exception:
                                pass
                            time.sleep(float(cfg["attack_interval"]))
                    else:
                        logger.log_state_change("attack", "search", "lost_timeout")
                        mode = "search"
                        time.sleep(0.05)
                    time.sleep(0.02)
            except Exception as e:
                logger.log_error("hunt_loop", f"Hunt error: {str(e)}", e)
                logger.log_hunt_stop("error")
            finally:
                try:
                    already_logged = bool(getattr(logger, "_stop_logged", False))
                except Exception:
                    already_logged = False
                if not already_logged:
                    logger.log_hunt_stop("manual_stop")
                    try:
                        setattr(logger, "_stop_logged", True)
                    except Exception:
                        pass
                self.hunt_running = False
                self.after(0, self._after_hunt_stop)

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def _after_hunt_stop(self):
        # Update button states with enhanced visual feedback
        self.hunt_start_btn.config(
            state="normal",
            bg="#2E7D32",  # Restore green when active
            relief="raised",
            cursor="hand2",
        )
        self.hunt_stop_btn.config(
            state="disabled",
            bg="#FFCDD2",  # Light red when disabled
            relief="sunken",
            cursor="arrow",
        )

        # Note: Global hotkeys cleanup will be handled in on_close()

        # restore GUI
        try:
            self.deiconify()
            self.lift()
        except Exception:
            pass
        self.hunt_status.set(self._t("hunt_stopped"))

    def on_hunt_stop(self):
        self.hunt_running = False

    # -----------------
    # Close
    # -----------------
    def on_close(self):
        self.click_running = False
        self.hunt_running = False

        # Unregister global hotkeys before closing
        self._unregister_global_hotkeys()

        self.destroy()

    # -----------------
    # Language helpers
    # ========================================================================
    # Vision Menu Callbacks (Sprint 22 Phase 1B)
    # ========================================================================
    
    def _open_vision_wizard(self):
        """
        Open Vision Wizard window (Ctrl+Shift+V).
        Uses singleton pattern - only one instance at a time.
        """
        try:
            from ui.windows.setup_wizard_vision import create_or_show_vision_wizard
            
            wizard = create_or_show_vision_wizard(
                self, # type: ignore
                config_path=str(CONFIG_PATH),  # Use global CONFIG_PATH
                on_close=self._on_vision_wizard_closed
            )
            print(f"[Vision] Wizard opened/focused: {wizard}")
            
        except Exception as e:
            print(f"[Vision] Error opening wizard: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                self._t("error"),
                f"Cannot open Vision Wizard:\n{e}"
            )
    
    def _on_vision_wizard_closed(self):
        """Callback when Vision Wizard is closed"""
        print("[Vision] Wizard closed")
        # TODO Phase 2: Refresh templates or update UI if needed
    
    def _scan_region(self):
        """
        Scan region for template matching (Ctrl+Alt+S).
        TODO Phase 2: Implement region scanning with overlay.
        """
        print("[Vision] Scan region - TODO Phase 2")
        messagebox.showinfo(
            "Vision - Scan Region",
            "Scan Region feature will be available in Phase 2.\n\n"
            "This will allow you to:\n"
            "• Select a region on screen\n"
            "• Scan for templates in real-time\n"
            "• Save ROI coordinates"
        )
    
    def _add_template(self):
        """
        Quick add template (Ctrl+T).
        Opens file dialog to select template image.
        TODO Phase 2: Add to config and Vision Wizard list.
        """
        print("[Vision] Add template")
        
        try:
            filetypes = [
                ('Image files', '*.png *.jpg *.jpeg *.bmp'),
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg *.jpeg'),
                ('All files', '*.*')
            ]
            
            file_path = filedialog.askopenfilename(
                parent=self,
                title=self._t("vision_add_template") if hasattr(self, '_t') else "Add Template",
                filetypes=filetypes
            )
            
            if file_path:
                print(f"[Vision] Selected template: {file_path}")
                
                # TODO Phase 2: Add to config
                # For now, just show success message
                messagebox.showinfo(
                    "Vision - Add Template",
                    f"Template selected:\n{file_path}\n\n"
                    "Full integration will be available in Phase 2.\n"
                    "Use Vision Wizard (Ctrl+Shift+V) to manage templates."
                )
                
        except Exception as e:
            print(f"[Vision] Error adding template: {e}")
            messagebox.showerror(
                self._t("error") if hasattr(self, '_t') else "Error",
                f"Cannot add template:\n{e}"
            )
    
    def _manage_templates(self):
        """
        Open template management (Ctrl+Shift+T).
        Shortcut to Vision Wizard.
        """
        print("[Vision] Manage templates - opening wizard")
        self._open_vision_wizard()
    
    def _toggle_overlay(self):
        """
        Toggle overlay display (Ctrl+Shift+O).
        Phase 5: Show/hide transparent overlay on game window.
        """
        print("[Vision] Toggle overlay - Starting...")
        
        try:
            # Import PyWin32 overlay module (Phase 5 refactor)
            try:
                print("[Overlay] Attempting to import OverlayWindowPyWin32...")
                from ui.windows.overlay_window import OverlayWindowPyWin32
                print("[Overlay] ✅ Import successful!")
            except ImportError as import_err:
                # PyWin32 not installed - show translated error
                print(f"[Overlay] ❌ ImportError caught: {import_err}")
                print(f"[Overlay] Error type: {type(import_err)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    self._t("overlay_missing_dependency_title"),
                    self._t("overlay_missing_dependency_message")
                )
                self._overlay_enabled = False
                return
            except Exception as other_err:
                # Other errors during import
                print(f"[Overlay] ❌ Unexpected error during import: {other_err}")
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    self._t("error"),
                    f"Cannot import overlay module:\n{other_err}"
                )
                self._overlay_enabled = False
                return
            
            # Toggle state
            self._overlay_enabled = not self._overlay_enabled
            
            if self._overlay_enabled:
                # ========================================
                # STEP 1: ALWAYS REFRESH LIVE POSITION FIRST
                # ========================================
                target_hwnd = self.hunt_cfg.get('window_hwnd')
                window_bounds = None
                
                # Get CURRENT window position from LIVE game window (not from config cache)
                if target_hwnd:
                    try:
                        from lib.system.window_manager import WindowManager
                        wm = WindowManager()
                        current_window = wm.get_window_info(target_hwnd)
                        
                        if current_window:
                            # Update with LIVE position
                            window_bounds = current_window.rect
                            
                            # Handle minimized window
                            if current_window.is_minimized:
                                print(f"[Overlay] ⚠️ Game is minimized, restoring...")
                                wm.restore(target_hwnd)
                                time.sleep(0.3)
                                
                                # Get updated position after restore
                                current_window = wm.get_window_info(target_hwnd)
                                if current_window:
                                    window_bounds = current_window.rect
                                    print(f"[Overlay] ✅ Window restored to: {window_bounds}")
                            
                            # Validate rect is not minimized position
                            if window_bounds and (window_bounds.get('left', 0) < -30000 or window_bounds.get('top', 0) < -30000):
                                print(f"[Overlay] ⚠️ Detected minimized rect, clearing: {window_bounds}")
                                window_bounds = None
                            
                            if window_bounds:
                                # Save LIVE position to config
                                self.hunt_cfg['window_bounds'] = window_bounds
                                save_hunt_config(self.hunt_cfg)
                                print(f"[Overlay] ✅ Refreshed LIVE position: {window_bounds}")
                        else:
                            print(f"[Overlay] ⚠️ Could not get current window info for HWND:{target_hwnd}")
                    except Exception as e:
                        print(f"[Overlay] ❌ Error refreshing position: {e}")
                
                # ========================================
                # STEP 2: AUTO-DETECT IF NO VALID POSITION
                # ========================================
                if window_bounds is None:
                    print("[Overlay] No valid window position, attempting auto-detect...")
                    
                    # Try to find CABAL window
                    try:
                        from lib.system.window_manager import WindowManager
                        wm = WindowManager()
                        
                        # Search for CABAL window
                        windows = wm.list_windows()
                        cabal_window = None
                        
                        for w in windows:
                            if 'CABAL' in w.title.upper():
                                cabal_window = w
                                print(f"[Overlay] Found CABAL window: {w.title} [HWND:{w.hwnd}]")
                                break
                        
                        if cabal_window:
                            # Bring game window to foreground FIRST if minimized/hidden
                            try:
                                if cabal_window.is_minimized:
                                    print(f"[Overlay] Game is minimized, restoring...")
                                    wm.restore(cabal_window.hwnd)
                                    time.sleep(0.3)  # Wait for window to restore
                                    
                                    # Get updated window info after restore
                                    restored_window = wm.get_window_info(cabal_window.hwnd)
                                    if restored_window:
                                        cabal_window = restored_window
                                        print(f"[Overlay] Window restored, new rect: {cabal_window.rect}")
                                    else:
                                        print(f"[Overlay] ⚠️ Could not get window info after restore")
                                
                                if not cabal_window.is_foreground:
                                    print(f"[Overlay] Bringing game window to foreground...")
                                    wm.set_foreground(cabal_window.hwnd)
                                    print(f"[Overlay] ✅ Game window focused")
                            except Exception as e:
                                print(f"[Overlay] Failed to restore/foreground window: {e}")
                            
                            # Use detected window (after restore)
                            window_bounds = cabal_window.rect
                            target_hwnd = cabal_window.hwnd
                            
                            # Validate rect is not minimized position
                            if window_bounds['left'] < -30000 or window_bounds['top'] < -30000:
                                messagebox.showerror(
                                    "Invalid Window Position",
                                    f"Game window appears to be minimized or invalid.\n\n"
                                    f"Current position: {window_bounds}\n\n"
                                    f"Please restore the game window and try again.",
                                    parent=self
                                )
                                self._overlay_enabled = False
                                return
                            
                            # Save to config for next time
                            self.hunt_cfg['window_bounds'] = window_bounds
                            self.hunt_cfg['window_hwnd'] = target_hwnd
                            self.hunt_cfg['window_title'] = cabal_window.title
                            
                            # save_hunt_config is already defined at module level (line 566)
                            save_hunt_config(self.hunt_cfg)
                            
                            print(f"[Overlay] Auto-configured window: {cabal_window.title}")
                                
                        else:
                            # Still no window found - show warning
                            messagebox.showwarning(
                                self._t("overlay_no_window_title"),
                                self._t("overlay_no_window_message") + "\n\n💡 Tip: Open CABAL game window first!"
                            )
                            self._overlay_enabled = False
                            return
                            
                    except Exception as e:
                        print(f"[Overlay] Auto-detect failed: {e}")
                        import traceback
                        traceback.print_exc()
                        # Show original warning
                        messagebox.showwarning(
                            self._t("overlay_no_window_title"),
                            self._t("overlay_no_window_message")
                        )
                        self._overlay_enabled = False
                        return
                
                # ========================================
                # STEP 3: VALIDATE WE HAVE VALID POSITION
                # ========================================
                if window_bounds is None:
                    messagebox.showwarning(
                        self._t("overlay_no_window_title"),
                        self._t("overlay_no_window_message")
                    )
                    self._overlay_enabled = False
                    return
                
                # ========================================
                # STEP 4: CREATE OR UPDATE OVERLAY
                # ========================================
                # Get overlay config from hunt_cfg (or use defaults)
                overlay_cfg = self.hunt_cfg.get('overlay', {})
                alpha = float(overlay_cfg.get('alpha', 0.7))  # Default 70% for testing (more visible)
                fps_limit = int(overlay_cfg.get('fps_limit', 15))
                
                # Create overlay if not exists
                if self._overlay_window is None:
                    print(f"[Overlay] Creating NEW overlay with alpha={alpha}, fps={fps_limit}")
                    print(f"[Overlay] Target rect: {window_bounds}")
                    print(f"[Overlay] Target HWND: {target_hwnd}")
                    
                    # Create PyWin32 overlay window
                    self._overlay_window = OverlayWindowPyWin32(
                        target_rect=window_bounds,
                        alpha=alpha,
                        fps_limit=fps_limit,
                        enable_click_through=True
                    )
                    
                    # Create window
                    self._overlay_window.create()
                    
                    print(f"[Overlay] Window created with HWND: {self._overlay_window.hwnd}")
                    print(f"[Overlay] {self._t('overlay_created').format(hwnd=target_hwnd, rect=window_bounds)}")
                else:
                    # Overlay already exists, just update position
                    print(f"[Overlay] Overlay exists, updating to LIVE position: {window_bounds}")
                    self._overlay_window.update_target_rect(window_bounds)
                
                # Show overlay
                self._overlay_window.show()
                
                # ========================================
                # PHASE 7: Initialize Monster Tracking
                # ========================================
                try:
                    # Initialize VisionEngine if needed
                    if self._vision_engine is None:
                        from lib.vision.vision_engine import VisionEngine
                        self._vision_engine = VisionEngine()
                        print("[MonsterTracking] VisionEngine initialized")
                    
                    # Initialize ScreenCapture if needed
                    if self._screen_capture is None:
                        from lib.system.screen_capture import ScreenCapture
                        self._screen_capture = ScreenCapture()
                        print("[MonsterTracking] ScreenCapture initialized")
                    
                    # Initialize BotManager if needed
                    if self._bot_manager is None:
                        # Get configuration from hunt_cfg
                        tracking_cfg = self.hunt_cfg.get('monster_tracking', {})
                        stable_frames = int(tracking_cfg.get('stable_frames', 3))
                        lost_timeout = float(tracking_cfg.get('lost_timeout', 3.0))
                        auto_start = bool(tracking_cfg.get('auto_start_with_hunt', False))
                        
                        self._bot_manager = BotManager(
                            vision_engine=self._vision_engine,
                            screen_capture=self._screen_capture,
                            stable_frames=stable_frames,
                            lost_timeout=lost_timeout,
                            enable_auto_start=auto_start
                        )
                        print(f"[MonsterTracking] BotManager initialized (stable_frames={stable_frames}, lost_timeout={lost_timeout})")
                    
                    # Start detection to create detector instance
                    if not self._bot_manager.is_detection_running():
                        tracking_cfg = self.hunt_cfg.get('monster_tracking', {})
                        confidence = float(tracking_cfg.get('confidence_threshold', 0.7))
                        
                        success = self._bot_manager.start_detection(
                            confidence_threshold=confidence,
                            target_rect=window_bounds
                        )
                        if success:
                            print(f"[MonsterTracking] Detection started (confidence={confidence})")
                        else:
                            print("[MonsterTracking] Failed to start detection")
                    
                    # Create OverlayController to connect detector → overlay
                    # Only create if we have a detector instance
                    if self._overlay_controller is None and self._bot_manager._detector is not None:
                        # Get configuration
                        tracking_cfg = self.hunt_cfg.get('monster_tracking', {})
                        max_boxes = int(tracking_cfg.get('max_detections_display', 20))
                        show_stats = bool(tracking_cfg.get('show_stats', True))
                        stats_interval = float(tracking_cfg.get('stats_update_interval', 0.5))
                        
                        # Get window tracker if available
                        window_tracker = getattr(self, '_window_tracker', None)
                        
                        self._overlay_controller = OverlayController(
                            overlay=self._overlay_window,
                            detector=self._bot_manager._detector,
                            max_boxes=max_boxes,
                            show_stats=show_stats,
                            stats_update_interval=stats_interval,
                            window_tracker=window_tracker
                        )
                        
                        # Start controller to activate callbacks
                        self._overlay_controller.start()
                        print(f"[MonsterTracking] OverlayController started (max_boxes={max_boxes}, show_stats={show_stats})")
                    
                    print("[MonsterTracking] Monster tracking active")
                    
                except Exception as e:
                    print(f"[MonsterTracking] Error initializing tracking: {e}")
                    import traceback
                    traceback.print_exc()
                
                # ALWAYS re-add test detection boxes to fix white screen issue
                from ui.windows.overlay_window import DetectionBox
                test_boxes = [
                    DetectionBox(
                        x=100, y=100, w=200, h=150,
                        label="TEST OVERLAY - Visible?",
                        color=(255, 0, 0),  # Red
                        confidence=1.0
                    ),
                    DetectionBox(
                        x=350, y=250, w=150, h=100,
                        label="Detection Test",
                        color=(0, 255, 0),  # Green
                        confidence=0.95
                    )
                ]
                self._overlay_window.update_detections(test_boxes)
                print(f"[Overlay] Test detection boxes updated")
                
                # Start window tracker instead of position sync
                self._start_overlay_window_tracker()
                
                # Update menu/config
                self.hunt_cfg.setdefault('overlay', {})['enabled'] = True
                save_hunt_config(self.hunt_cfg)
                
                print(f"[Overlay] {self._t('overlay_enabled')}")
                
            else:
                # ========================================
                # PHASE 7: Stop Monster Tracking
                # ========================================
                try:
                    # Stop overlay controller
                    if self._overlay_controller is not None:
                        self._overlay_controller.stop()
                        self._overlay_controller = None
                        print("[MonsterTracking] OverlayController stopped")
                    
                    # Stop detection
                    if self._bot_manager is not None:
                        self._bot_manager.stop_detection()
                        print("[MonsterTracking] Detection stopped")
                    
                except Exception as e:
                    print(f"[MonsterTracking] Error stopping tracking: {e}")
                
                # Hide overlay
                if self._overlay_window is not None:
                    self._overlay_window.hide()
                
                # Stop window tracker
                self._stop_overlay_window_tracker()
                
                # Update config
                self.hunt_cfg.setdefault('overlay', {})['enabled'] = False
                save_hunt_config(self.hunt_cfg)
                
                print(f"[Overlay] {self._t('overlay_disabled')}")
                
        except Exception as e:
            print(f"[Overlay] Toggle error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                self._t("overlay_error_title"),
                self._t("overlay_toggle_failed").format(error=str(e))
            )
            self._overlay_enabled = False
    
    def _start_overlay_window_tracker(self):
        """Start real-time window tracker for overlay sync."""
        if hasattr(self, '_window_tracker') and self._window_tracker and self._window_tracker.is_running():
            return  # Already running
        
        target_hwnd = self.hunt_cfg.get('window_hwnd')
        if target_hwnd is None:
            print("[Overlay] No target hwnd for window tracker")
            return
        
        try:
            from ui.utils.window_tracker import WindowTracker, WindowState
            
            # Define callbacks for window changes
            def on_position_change(rect):
                try:
                    if self._overlay_window:
                        self._overlay_window.update_target_rect(rect)
                except Exception as e:
                    print(f"[Overlay] ❌ Error in on_position_change: {e}")
                    import traceback
                    traceback.print_exc()
            
            def on_size_change(rect):
                try:
                    if self._overlay_window:
                        self._overlay_window.update_target_rect(rect)
                except Exception as e:
                    print(f"[Overlay] ❌ Error in on_size_change: {e}")
                    import traceback
                    traceback.print_exc()
            
            def on_visibility_change(visible):
                try:
                    if self._overlay_window:
                        if visible:
                            self._overlay_window.show()
                        else:
                            self._overlay_window.hide()
                        print(f"[Overlay] Visibility: {visible}")
                except Exception as e:
                    print(f"[Overlay] ❌ Error in on_visibility_change: {e}")
                    import traceback
                    traceback.print_exc()
            
            def on_state_change(state):
                try:
                    if state == WindowState.MINIMIZED:
                        if self._overlay_window:
                            self._overlay_window.hide()
                    elif state == WindowState.NORMAL or state == WindowState.MAXIMIZED:
                        if self._overlay_window and self._overlay_enabled:
                            self._overlay_window.show()
                    print(f"[Overlay] State: {state.value}")
                except Exception as e:
                    print(f"[Overlay] ❌ Error in on_state_change: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Create and start tracker
            self._window_tracker = WindowTracker(
                target_hwnd=target_hwnd,
                poll_rate=60,  # 60 FPS for smooth tracking
                on_position_change=on_position_change,
                on_size_change=on_size_change,
                on_visibility_change=on_visibility_change,
                on_state_change=on_state_change
            )
            self._window_tracker.start()
            
            print(f"[Overlay] Window tracker started (60 FPS)")
            
        except Exception as e:
            print(f"[Overlay] Failed to start window tracker: {e}")
            import traceback
            traceback.print_exc()
    
    def _stop_overlay_window_tracker(self):
        """Stop window tracker."""
        if hasattr(self, '_window_tracker') and self._window_tracker:
            self._window_tracker.stop()
            self._window_tracker = None
            print("[Overlay] Window tracker stopped")
    
    def _start_overlay_position_sync(self):
        """Start background thread to sync overlay position with game window."""
        if self._overlay_update_thread is not None and self._overlay_update_thread.is_alive():
            return  # Already running
        
        self._overlay_stop_event.clear()
        
        def position_sync_loop():
            """Update overlay position at 15 FPS."""
            try:
                # Import WindowManager for position tracking
                from lib.system.window_manager import WindowManager
                
                window_manager = WindowManager()
                target_hwnd = self.hunt_cfg.get('window_hwnd')
                
                if target_hwnd is None:
                    print("[Overlay] No target hwnd for position sync")
                    return
                
                print(f"[Overlay] Position sync loop started for HWND: {target_hwnd}")
                last_rect = None
                update_count = 0
                force_topmost_counter = 0  # Force topmost every 30 frames (~2 seconds)
                
                while not self._overlay_stop_event.is_set():
                    try:
                        # Get current window position
                        window_info = window_manager.get_window_info(target_hwnd)
                        
                        if window_info is not None and self._overlay_window is not None:
                            new_rect = window_info.rect
                            
                            # Check if window rect changed (position or size)
                            if last_rect is None or (
                                new_rect['left'] != last_rect['left'] or
                                new_rect['top'] != last_rect['top'] or
                                new_rect['width'] != last_rect['width'] or
                                new_rect['height'] != last_rect['height']
                            ):
                                # Update overlay position/size
                                self._overlay_window.update_target_rect(new_rect)
                                last_rect = new_rect
                                update_count += 1
                                print(f"[Overlay] Update #{update_count}: pos=({new_rect['left']},{new_rect['top']}) size=({new_rect['width']}x{new_rect['height']})")
                                
                                # Force overlay to stay on top after position update
                                try:
                                    import win32gui, win32con
                                    win32gui.SetWindowPos(
                                        self._overlay_window.hwnd,
                                        win32con.HWND_TOPMOST,
                                        0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                                    )
                                except Exception as e:
                                    print(f"[Overlay] Failed to force topmost: {e}")
                            
                            # Periodically force topmost even if no position change
                            force_topmost_counter += 1
                            if force_topmost_counter >= 30:  # Every ~2 seconds
                                force_topmost_counter = 0
                                try:
                                    import win32gui, win32con
                                    win32gui.SetWindowPos(
                                        self._overlay_window.hwnd,
                                        win32con.HWND_TOPMOST,
                                        0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                                    )
                                except Exception:
                                    pass
                        
                    except Exception as e:
                        print(f"[Overlay] Position sync error: {e}")
                    
                    # 15 FPS = ~67ms per frame
                    self._overlay_stop_event.wait(timeout=0.067)
                    
            except Exception as e:
                print(f"[Overlay] Position sync loop error: {e}")
        
        self._overlay_update_thread = threading.Thread(
            target=position_sync_loop,
            name="OverlayPositionSync",
            daemon=True
        )
        self._overlay_update_thread.start()
        print("[Overlay] Position sync started")
    
    def _stop_overlay_position_sync(self):
        """Stop the overlay position sync thread."""
        if self._overlay_update_thread is None:
            return
        
        self._overlay_stop_event.set()
        
        if self._overlay_update_thread.is_alive():
            self._overlay_update_thread.join(timeout=1.0)
        
        self._overlay_update_thread = None
        print("[Overlay] Position sync stopped")
    
    def _open_overlay_settings(self):
        """Open overlay settings dialog."""
        print("[Overlay] Opening settings dialog")
        
        try:
            from ui.utils.overlay_settings import OverlaySettingsDialog
            
            # Get current overlay config
            overlay_config = self.hunt_cfg.get('overlay', {})
            
            def on_apply(new_config: Dict[str, Any]):
                """Apply new overlay settings."""
                print("[Overlay] Applying new settings")
                
                # Update hunt config
                self.hunt_cfg['overlay'] = new_config
                save_hunt_config(self.hunt_cfg)
                
                # Update existing overlay if active
                if self._overlay_window is not None:
                    try:
                        # Update alpha
                        alpha = float(new_config.get('alpha', 0.7))
                        self._overlay_window.set_alpha(alpha)
                        
                        # Update FPS limit (requires recreating overlay)
                        fps_limit = int(new_config.get('fps_limit', 15))
                        if fps_limit != self._overlay_window.fps_limit:
                            # Recreate overlay with new FPS
                            was_visible = self._overlay_window.is_visible()
                            self._overlay_window.destroy()
                            self._overlay_window = None
                            
                            if was_visible:
                                # Re-toggle to recreate
                                self._overlay_enabled = False
                                self._toggle_overlay()
                        
                        print(f"[Overlay] Settings updated: alpha={alpha}, fps={fps_limit}")
                    except Exception as e:
                        print(f"[Overlay] Error updating settings: {e}")
                
                messagebox.showinfo(
                    self._t("overlay_settings_title"),
                    self._t("overlay_settings_applied")
                )
            
            # Show settings dialog
            dialog = OverlaySettingsDialog(
                parent=self,
                current_config=overlay_config,
                lang=self.lang,
                on_apply=on_apply
            )
            dialog.show()
            
        except Exception as e:
            print(f"[Overlay] Settings dialog error: {e}")
            messagebox.showerror(
                self._t("overlay_settings_error_title"),
                self._t("overlay_settings_error").format(error=str(e))
            )

    # -----------------
    def _t(self, key: str) -> str:
        try:
            return i18n_t(key, ns=I18N_GLOBAL, lang=self.lang)
        except Exception:
            return GLOBAL_TRANSLATIONS.get(
                self.lang, GLOBAL_TRANSLATIONS.get("en", {})
            ).get(key, key)

    def on_language_change(self, _evt=None):
        self.lang = self.lang_var.get()
        self.cfg.setdefault("ui", {})
        self.cfg["ui"]["language"] = self.lang
        save_config(self.cfg)
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        try:
            i18n_set_lang(self.lang)
        except Exception:
            pass
        # Rebuild UI with new language
        self.title(self._t("app_title"))
        self._build_ui()


def main():
    """Main entry point with single instance lock."""
    # Check critical dependencies (pywin32 for overlay)
    try:
        import win32gui  # Test pywin32 availability
    except ImportError:
        # Show warning but don't block - overlay will show error when toggled
        print("⚠️ WARNING: pywin32 not installed - overlay feature will not work")
        print("   Run: pip install pywin32")
        print("   Or: python scripts/check_dependencies.py --install")
    
    # Create single instance lock (using mutex on Windows, file lock on Unix)
    instance_lock = SingleInstanceLock("CabalAutoHunt_v1")

    # Try to acquire lock
    if not instance_lock.acquire():
        # Another instance is already running - show error in both languages
        root = tk.Tk()
        root.withdraw()  # Hide main window

        messagebox.showerror(
            "⚠️ Application Already Running | Ứng dụng đã chạy",
            "❌ CANNOT START: Another instance is already running!\n\n"
            "📌 Only ONE instance can run at a time.\n"
            "🔄 Please close the existing application first, then try again.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ KHÔNG THỂ KHỞI ĐỘNG: Ứng dụng đã đang chạy!\n\n"
            "📌 Chỉ được phép chạy 1 ứng dụng tại một thời điểm.\n"
            "🔄 Vui lòng tắt ứng dụng đang chạy trước, sau đó thử lại.",
            parent=root,
        )

        root.destroy()
        sys.exit(1)

    try:
        # Start application
        app = App()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()
    finally:
        # Always release lock on exit
        instance_lock.release()


if __name__ == "__main__":
    main()




