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
from lib.i18n.translations import GLOBAL_TRANSLATIONS
from lib.ui.tooltip import attach_i18n_tooltip
from lib.i18n import register_bulk as i18n_register_bulk, t as i18n_t, set_default_lang as i18n_set_lang, GLOBAL_NS as I18N_GLOBAL

try:
    from lib.ui.capture_helper import capture_region_and_save
except Exception:
    capture_region_and_save = None  # type: ignore

from lib.system.win_input import tap
from lib.system.hunt_logger import get_hunt_logger
from lib.features.timing.calculator import calculate_timing, format_timing_recommendation, get_timing_presets
from lib.features.skills.skill_stats import SkillStats  # Sprint 22 Patch 1: Training Mode
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
        if sys.platform != 'win32':
            lock_dir = Path(__file__).parent / 'tmp'
            lock_dir.mkdir(parents=True, exist_ok=True)
            self.lock_file_path = lock_dir / f'{app_name}.lock'
    
    def acquire(self) -> bool:
        """Acquire the lock. Returns True if successful, False if another instance is running.
        
        Returns:
            bool: True if lock acquired successfully, False if another instance holds the lock.
        """
        try:
            if sys.platform == 'win32':
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
                    self.lock_file = open(self.lock_file_path, 'w')
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
            if sys.platform == 'win32':
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
    from ui.setup_wizard import show_setup_wizard  # type: ignore
except Exception:
    show_setup_wizard = None  # type: ignore

# Local ToolTip class removed; using centralized attach_i18n_tooltip from lib.tooltip

# All data files centralized in lib/data/ for consistency
_LIB_DATA_DIR = Path(__file__).parent / 'lib' / 'data'
CONFIG_PATH = _LIB_DATA_DIR / 'config.json'
HUNT_CONFIG_PATH = _LIB_DATA_DIR / 'hunt_config.json'
MONSTER_DB_PATH = _LIB_DATA_DIR / 'monsters.json'
SKILL_DB_PATH = _LIB_DATA_DIR / 'skills.json'


def _normalize_window_bounds(value):
    keys = ('left', 'top', 'width', 'height')
    if isinstance(value, dict):
        try:
            normalized = {k: int(value.get(k, 0)) for k in keys}
        except (TypeError, ValueError):
            return None
        if normalized['width'] <= 0 or normalized['height'] <= 0:
            return None
        return normalized
    if isinstance(value, (list, tuple)) and len(value) == 4:
        try:
            left, top, width, height = [int(v) for v in value]
        except (TypeError, ValueError):
            return None
        if width <= 0 or height <= 0:
            return None
        return {'left': left, 'top': top, 'width': width, 'height': height}
    return None


def _normalize_template_entry(item):
    if not isinstance(item, dict):
        return None
    path = str(item.get('path', '') or '').strip()
    if not path:
        return None
    name = str(item.get('name', '') or '').strip()
    if not name:
        try:
            name = Path(path).stem
        except Exception:
            name = 'template'
    try:
        threshold = float(item.get('threshold', 0.85))
    except (TypeError, ValueError):
        threshold = 0.85
    if not math.isfinite(threshold):
        threshold = 0.85
    threshold = max(0.0, min(threshold, 1.0))
    region = _normalize_window_bounds(item.get('region'))
    region_strategy = str(item.get('region_strategy', '') or '').strip()
    grayscale = item.get('grayscale')
    tmpl = {
        'name': name,
        'path': path,
        'threshold': threshold,
        'region': region,
    }
    if region_strategy:
        tmpl['region_strategy'] = region_strategy
    if grayscale is not None:
        tmpl['grayscale'] = bool(grayscale)
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
        with open(MONSTER_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        monsters = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                if not name:
                    continue
                try:
                    hp = float(item.get('hp', 0))
                    dmg = float(item.get('damage_per_hit', 0))
                except (TypeError, ValueError):
                    continue
                if hp <= 0 or dmg <= 0:
                    continue
                template = str(item.get('template', '') or '').strip()
                description = str(item.get('description', '') or '').strip()
                training_mode = bool(item.get('training_mode', False))
                window_bounds = _normalize_window_bounds(item.get('window_bounds'))
                templates = _sanitize_templates(item.get('templates'))
                monsters.append({
                    'name': name,
                    'hp': hp,
                    'damage_per_hit': dmg,
                    'template': template,
                    'description': description,
                    'training_mode': training_mode,
                    'window_bounds': window_bounds,
                    'templates': templates,
                })
        return monsters
    except Exception:
        return []


def save_monster_library(monsters):
    safe = []
    for item in monsters:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()
        if not name:
            continue
        try:
            hp = float(item.get('hp', 0))
            dmg = float(item.get('damage_per_hit', 0))
        except (TypeError, ValueError):
            continue
        template = str(item.get('template', '') or '').strip()
        description = str(item.get('description', '') or '').strip()
        training_mode = bool(item.get('training_mode', False))
        window_bounds = _normalize_window_bounds(item.get('window_bounds'))
        templates = _sanitize_templates(item.get('templates'))
        safe.append({
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
            'description': description,
            'training_mode': training_mode,
            'window_bounds': window_bounds,
            'templates': templates,
        })
    with open(MONSTER_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def load_skill_library():
    if not SKILL_DB_PATH.exists():
        return []
    try:
        with open(SKILL_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        skills = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                key = str(item.get('key', '')).strip().upper()
                if not name or not key:
                    continue
                skill_type = str(item.get('type', 'attack')).strip().lower()
                if skill_type not in ('attack', 'buff'):
                    skill_type = 'attack'
                try:
                    cooldown = float(item.get('cooldown', 0.0))
                    cast_time = float(item.get('cast_time', 0.0))
                except (TypeError, ValueError):
                    cooldown = 0.0
                    cast_time = 0.0
                image = str(item.get('image', '') or '').strip()
                skills.append({
                    'name': name,
                    'key': key,
                    'type': skill_type,
                    'cooldown': max(cooldown, 0.0),
                    'cast_time': max(cast_time, 0.0),
                    'image': image,
                })
        return skills
    except Exception:
        return []


def save_skill_library(skills):
    safe = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()
        key = str(item.get('key', '')).strip().upper()
        if not name or not key:
            continue
        skill_type = str(item.get('type', 'attack')).strip().lower()
        if skill_type not in ('attack', 'buff'):
            skill_type = 'attack'
        try:
            cooldown = float(item.get('cooldown', 0.0))
            cast_time = float(item.get('cast_time', 0.0))
        except (TypeError, ValueError):
            continue
        image = str(item.get('image', '') or '').strip()
        safe.append({
            'name': name,
            'key': key,
            'type': skill_type,
            'cooldown': max(cooldown, 0.0),
            'cast_time': max(cast_time, 0.0),
            'image': image,
        })
    with open(SKILL_DB_PATH, 'w', encoding='utf-8') as f:
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
    skill_dict = {s['name']: s for s in skills_data}
    
    # Collect cooldowns for selected skills
    total_cooldown = 0.0
    valid_count = 0
    
    for skill_name in skill_names:
        if skill_name in skill_dict:
            skill = skill_dict[skill_name]
            # Only count attack skills for attack speed calculation
            if skill.get('type', 'attack').lower() == 'attack':
                cooldown = float(skill.get('cooldown', 1.0))
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
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "click": {"x": 500, "y": 400, "interval_sec": 2.0},
        "hotkeys": {"toggle": "f8", "exit": "f8"},
        "safety": {"failsafe": True, "pause_key": "f7"},
        "ui": {"topmost": False}
    }


def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_hunt_config():
    # Default hunt config if file missing
    default = {
        "window_title": "Cabal",
        "target_key": "Z",  # Changed from TAB to Z (more common for target cycling)
        "attack_keys": ["1", "2", "3"],
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
        "monster_list": [],           # [{"name": "Coc Go 2", "priority": 1}, ...]
        "rotation_mode": "sequence",  # "sequence" or "priority"
        "current_monster_index": 0,   # For sequence rotation
    }
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            default.update(data)
        except Exception:
            pass
    default.setdefault('skill_slots', [])
    
    # Backward compatibility: migrate monster_selected_name → monster_list
    if 'monster_selected_name' in default and default['monster_selected_name']:
        if not default.get('monster_list'):
            default['monster_list'] = [{"name": default['monster_selected_name'], "priority": 1}]
    
    # Ensure monster_list exists
    default.setdefault('monster_list', [])
    default.setdefault('rotation_mode', 'sequence')
    default.setdefault('current_monster_index', 0)
    
    # Ensure global_hotkeys section exists
    default.setdefault('global_hotkeys', {
        'enabled': True,
        'start_key': 'ctrl+shift+r',
        'stop_key': 'ctrl+shift+e'
    })
    
    return default


def save_hunt_config(cfg):
    with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class ConfigManager:
    """Wrapper class for config management to interface with SetupWizard."""
    def __init__(self, cfg, hunt_cfg):
        self.cfg = cfg
        self.hunt_cfg = hunt_cfg
    
    def set(self, section, key, value):
        """Set a configuration value."""
        if section == 'hunt_config':
            self.hunt_cfg[key] = value
        elif section == 'config':
            self.cfg[key] = value
        else:
            # Handle other sections if needed
            if section not in self.cfg:
                self.cfg[section] = {}
            self.cfg[section][key] = value
    
    def get(self, section, key, default=None):
        """Get a configuration value."""
        if section == 'hunt_config':
            return self.hunt_cfg.get(key, default)
        elif section == 'config':
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
        self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))
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
            from lib.ui.icon_helper import get_icon_helper
            self.icon_helper = get_icon_helper()
        except Exception:
            self.icon_helper = None
        
        # Create config manager for wizard
        self.config_mgr = ConfigManager(self.cfg, self.hunt_cfg)

        self.title(self._t('app_title'))
        self.resizable(False, False)

        # Check PIL availability (for image preview features)
        self.pil_available = (Image is not None and ImageTk is not None and ImageDraw is not None)
        
        # State
        self.click_running = False
        self.click_thread = None
        self.hunt_running = False
        self.hunt_thread = None
        self.win_items = []  # list of {'hwnd','pid','title','proc'}
        self.hunt_selected = None  # currently selected window info
        self._skip_auto_bring = False  # Flag to prevent double bring-to-front
        
        # Global hotkeys (Ctrl+Shift+R/E) - registered after config load
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        
        self.monsters = load_monster_library()
        self.monster_selected_index = None
        self.monster_selected_name = self.monsters[0]['name'] if self.monsters else None
        
        # Phase 3: Multi-Monster Support
        self.monster_rotation_list = []  # [{"name": "Coc Go 2", "priority": 1, "enabled": True}, ...]
        self._load_monster_rotation_list()
        self.skills = load_skill_library()
        self.skill_selected_index = None
        self.skill_selected_name = self.skills[0]['name'] if self.skills else None
        self.skill_preview_image = None
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self.skill_slot_saved_names = [slot.get('name', '') for slot in self.hunt_cfg.get('skill_slots', []) if isinstance(slot, dict) and slot.get('name')]
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
        self.monster_estimate_var = tk.StringVar(value='')
        self.skill_listbox = None
        self.skill_name_var = tk.StringVar()
        self.skill_key_var = tk.StringVar()
        self.skill_type_var = tk.StringVar(value=self._t('skill_type_attack'))
        self.skill_cooldown_var = tk.StringVar()
        self.skill_cast_time_var = tk.StringVar()
        self.skill_duration_var = tk.StringVar()
        # Keep references to images (PhotoImage) to prevent GC
        self._image_refs = []  # type: List[Any]
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
        self.monster_template_threshold_var = tk.StringVar(value='0.85')
        self.monster_template_region_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        self.monster_template_preview_label = None
        self.monster_template_preview_image = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}  # path -> PhotoImage cache
        self.monster_bounds_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        self.current_window_bounds = _normalize_window_bounds(self.hunt_cfg.get('window_bounds'))
        self.hunt_cfg['window_bounds'] = self.current_window_bounds
        self.window_bounds_display_var = tk.StringVar(value='')
        
        # Hunt tab widget groups for progressive disclosure
        self.hunt_intermediate_widgets = []  # Shown in intermediate+ modes
        self.hunt_advanced_widgets = []      # Shown only in advanced mode

        if pyautogui is not None:
            pyautogui.FAILSAFE = bool(self.cfg.get('safety', {}).get('failsafe', True))

        self._build_ui()
        
        # Keyboard shortcuts (Window-focused only)
        self.bind('<Control-k>', lambda e: self._open_skill_manager())  # Ctrl+K: Manage skills
        self.bind('<Alt-Key-1>', lambda e: self._switch_to_tab(0))  # Alt+1: Hunt tab
        self.bind('<Alt-Key-2>', lambda e: self._switch_to_tab(1))  # Alt+2: Setup tab
        
        # Register global hotkeys (Ctrl+Shift+R to start, Ctrl+Shift+E to stop)
        self._register_global_hotkeys()
        
        # Auto-launch Setup Wizard for new users (after UI is ready)
        self.after(500, self._check_first_time_setup)
        
        # Auto bring-to-front saved window (after setup check)
        self.after(1000, self._auto_bring_to_front_on_startup)
    
    def _icon(self, name: str, fallback: str, size: int = 16, color: str = None):
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
            if not hasattr(self, '_icon_cache'):
                self._icon_cache = {}
            key = f"{name}_{size}_{color or 'default'}"
            if key in self._icon_cache:
                return self._icon_cache[key]
            helper = getattr(self, 'icon_helper', None)
            if helper is not None:
                try:
                    img = helper.get_icon(name, fallback=fallback, size=size, color=color)
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
    def _create_icon_button(self, parent, icon_emoji, command, style='compact', 
                           bg_color=None, hover_color=None, **kwargs):
        """Create a standardized icon button following UIStyle guidelines.
        
        Args:
            parent: Parent widget
            icon_emoji: Emoji text for button (e.g., '➕', '↑', '↓')
            command: Button command callback
            style: Size style - 'compact', 'small', 'medium', or 'large'
            bg_color: Background color (uses BTN_ACCENT_BG if not specified)
            hover_color: Hover color (uses BTN_ACCENT_HOVER if not specified)
            **kwargs: Additional button configuration options
            
        Returns:
            tk.Button: Configured button widget
        """
        # Style presets based on UIStyle constants
        style_configs = {
            'compact': {
                'width': 0,
                'height': 0,
                'padx': UI.BTN_ICON_PADDING_COMPACT,
                'pady': UI.BTN_ICON_PADDING_COMPACT
            },
            'small': {
                'width': UI.BTN_ICON_WIDTH_SMALL,
                'height': 1,
                'padx': UI.BTN_ICON_PADDING_SMALL,
                'pady': UI.BTN_ICON_PADDING_SMALL
            },
            'medium': {
                'width': UI.BTN_ICON_WIDTH_MEDIUM,
                'height': 1,
                'padx': UI.BTN_ICON_PADDING_MEDIUM,
                'pady': UI.BTN_ICON_PADDING_MEDIUM
            },
            'large': {
                'width': UI.BTN_ICON_WIDTH_LARGE,
                'height': 1,
                'padx': UI.BTN_ICON_PADDING_LARGE,
                'pady': UI.BTN_ICON_PADDING_LARGE
            }
        }
        
        # Get style config
        config = style_configs.get(style, style_configs['compact'])
        
        # Default colors
        if bg_color is None:
            bg_color = UI.BTN_ACCENT_BG
        if hover_color is None:
            hover_color = UI.BTN_ACCENT_HOVER
        
        # Determine foreground color based on background color
        # Map background colors to their corresponding foreground colors
        color_map = {
            UI.BTN_PRIMARY_BG: UI.BTN_PRIMARY_FG,
            UI.BTN_ACCENT_BG: UI.BTN_ACCENT_FG,
            UI.BTN_INFO_BG: UI.BTN_INFO_FG,
            UI.BTN_NEUTRAL_BG: UI.BTN_NEUTRAL_FG,
            UI.BTN_DANGER_BG: UI.BTN_DANGER_FG,
        }
        fg_color = color_map.get(bg_color, UI.BTN_ACCENT_FG)  # Default to white
        
        # Merge with user kwargs
        button_config = {
            'text': icon_emoji,
            'command': command,
            'font': UI.FONT_BUTTON,
            'bg': bg_color,
            'fg': fg_color,
            'activebackground': hover_color,
            'activeforeground': fg_color,
            'relief': UI.BTN_RELIEF_NORMAL,
            'cursor': 'hand2',
            **config,
            **kwargs  # User kwargs override defaults
        }
        
        return tk.Button(parent, **button_config)
    
    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1, padx=5, pady=3)
            label.pack()
            widget._tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                delattr(widget, '_tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    # -----------------
    # UI Construction
    # -----------------
    def _build_ui(self):
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # Topbar with language selector and compact window selection
        top = tk.Frame(self, padx=8, pady=6)
        top.pack(fill='x')
        
        # Left side: Language selector
        tk.Label(top, text=self._t('language')).pack(side='left')
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cmb = ttk.Combobox(top, textvariable=self.lang_var, state='readonly', width=12)
        lang_cmb['values'] = ('en', 'vi')
        lang_cmb.pack(side='left', padx=(6,0))
        lang_cmb.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Separator
        tk.Frame(top, width=2, bg='#ccc', relief='sunken').pack(side='left', fill='y', padx=12, pady=2)
        
        # Right side: Window Selection Combobox with auto find & bring-to-front
        self.win_combo_var = tk.StringVar()
        self.win_combo = ttk.Combobox(top, textvariable=self.win_combo_var, state='readonly', width=40)
        self.win_combo.pack(side='left', padx=(0,6))
        
        # Auto-populate windows when dropdown is clicked
        self.win_combo.bind('<Button-1>', lambda e: self.on_hunt_find_windows() if not self.win_items else None)
        # Handle window selection
        self.win_combo.bind('<<ComboboxSelected>>', self.on_window_combo_selected)
        
        # Attach tooltip to combobox explaining window selection
        attach_i18n_tooltip(self.win_combo, key='window_select_tooltip', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        
        # Import button styles for refresh button
        from lib.ui.button_styles import get_button_config
        
        # Refresh button with icon (manual window refresh)
        refresh_icon = self._icon('refresh', '🔄', size=16)
        refresh_btn = tk.Button(
            top,
            text=self._t('refresh_windows') if isinstance(refresh_icon, str) else '',
            image=refresh_icon if not isinstance(refresh_icon, str) else None,
            compound='left' if not isinstance(refresh_icon, str) else 'none',
            command=self.on_hunt_refresh_windows,
            **get_button_config('refresh')
        )
        refresh_btn.pack(side='left', padx=(0,6))
        
        # Keep reference to prevent garbage collection
        if not isinstance(refresh_icon, str):
            refresh_btn.image = refresh_icon
        
        # Separator before hunt controls
        tk.Frame(top, width=2, bg='#ccc', relief='sunken').pack(side='left', fill='y', padx=12, pady=2)
        
        # Hunt Control Buttons - Using global button styles for consistency with icons
        # Start Hunt Button - Green (CR: 5.8:1) with start icon
        start_config = get_button_config('green')
        start_icon = self._icon('start', '▶️', size=18)
        
        self.hunt_start_btn = tk.Button(
            top, 
            text=f" {self._t('start_hunt')}" if not isinstance(start_icon, str) else self._t('start_hunt'),
            image=start_icon if not isinstance(start_icon, str) else None,
            compound='left' if not isinstance(start_icon, str) else 'none',
            command=self.on_hunt_start,
            **start_config,
            padx=16,
            pady=6
        )
        self.hunt_start_btn.pack(side='left', padx=(0, 6))
        
        # Keep reference
        if not isinstance(start_icon, str):
            self.hunt_start_btn.image = start_icon
        
        # Stop Hunt Button - Red (CR: 6.3:1) with stop icon
        stop_config = get_button_config('red')
        stop_icon = self._icon('stop', '⏹️', size=18)
        
        self.hunt_stop_btn = tk.Button(
            top,
            text=f" {self._t('stop_hunt')}" if not isinstance(stop_icon, str) else self._t('stop_hunt'),
            image=stop_icon if not isinstance(stop_icon, str) else None,
            compound='left' if not isinstance(stop_icon, str) else 'none',
            command=self.on_hunt_stop,
            state='disabled',
            **stop_config,
            padx=16,
            pady=6
        )
        self.hunt_stop_btn.pack(side='left')

        # Store notebook reference for keyboard shortcuts
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, pady=(0,8))

        # Create 4 tabs: Hunt, Setup, Stats, Help
        tab_hunt = tk.Frame(self.notebook, padx=12, pady=12)
        tab_setup = tk.Frame(self.notebook, padx=12, pady=12)
        tab_stats = tk.Frame(self.notebook, padx=12, pady=12)
        tab_help = tk.Frame(self.notebook, padx=12, pady=12)
        
        self.notebook.add(tab_hunt, text=self._t('tab_hunt'))
        self.notebook.add(tab_setup, text=self._t('tab_setup'))
        self.notebook.add(tab_stats, text=self._t('tab_stats'))
        self.notebook.add(tab_help, text=self._t('tab_help'))
        
        self._build_hunt_tab(tab_hunt)
        self._build_setup_tab(tab_setup)
        self._build_stats_tab(tab_stats)
        self._build_help_tab(tab_help)
        
        # Global Apply Section (below tabs, right-aligned)
        self._build_global_apply_section()

    def _build_global_apply_section(self):
        """Build global apply button section below tabs."""
        # Frame for global apply section (right-aligned)
        apply_frame = tk.Frame(self, relief='sunken', bd=1, bg='#f0f0f0')
        apply_frame.pack(fill='x', padx=8, pady=(0,8))
        
        # Unsaved changes indicator (left side)
        indicator_frame = tk.Frame(apply_frame, bg='#f0f0f0')
        indicator_frame.pack(side='left', padx=8, pady=6)
        
        self.unsaved_indicator_label = tk.Label(
            indicator_frame,
            text='',
            fg='#666',
            font=('Arial', 9),
            bg='#f0f0f0'
        )
        self.unsaved_indicator_label.pack(side='left')
        
        # Apply All Settings button (right side) - Using global green_light style with save icon
        # Optimized for: Negative Space, Hierarchy, Contrast Ratio (WCAG AA: 5.26:1)
        from lib.ui.button_styles import get_button_config
        apply_config = get_button_config('green_light')
        
        # Load save icon (22px to scale with 11pt font)
        save_icon = self._icon('save', '💾', size=22)
        
        self.global_apply_btn = tk.Button(
            apply_frame,
            text=f" {self._t('apply_all_settings')}" if not isinstance(save_icon, str) else f"💾 {self._t('apply_all_settings')}",
            image=save_icon if not isinstance(save_icon, str) else None,
            compound='left' if not isinstance(save_icon, str) else 'none',
            command=self.on_global_apply,
            **apply_config,
            padx=24,  # Increased from 20px for better negative space
            pady=10   # Increased from 8px for better touch target (48px height)
        )
        self.global_apply_btn.pack(side='right', padx=10, pady=6)  # Increased external margins
        
        # Keep reference to prevent garbage collection
        if not isinstance(save_icon, str):
            self.global_apply_btn.image = save_icon
        
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
        self.hunt_mode_var = tk.StringVar(value=self.hunt_cfg.get('ui_mode', 'beginner'))
        
        # Initialize vars for compatibility with hunt loop (values read from hunt_cfg)
        self.target_key_var = tk.StringVar(value=str(self.hunt_cfg.get('target_key', 'TAB')))
        self.attack_keys_var = tk.StringVar(value=','.join(self.hunt_cfg.get('attack_keys', ['1','2','3'])))
        self.attack_press_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_press_ms', 60)))
        self.target_cycle_var = tk.StringVar(value=str(self.hunt_cfg.get('target_cycle_delay', 0.2)))
        self.search_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('search_interval', 0.25)))
        self.attack_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_interval', 0.15)))
        self.lost_timeout_var = tk.StringVar(value=str(self.hunt_cfg.get('lost_timeout_sec', 1.2)))
        self.attack_duration_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_min_duration_sec', 1.5)))
        self.template_var = tk.StringVar(value=str(self.hunt_cfg.get('template_path', 'assets/images/target_frame.png')))
        
        region = self.hunt_cfg.get('region') or ["", "", "", ""]
        self.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")
        
        self.bring_front_var = tk.BooleanVar(value=bool(self.hunt_cfg.get('bring_to_front_each_cycle', False)))
        
        # Section 2: Monster Selection (Phase 3: Multi-Monster Support)
        monster_frame = tk.LabelFrame(frm, text=self._t('hunt_monsters'), padx=10, pady=8)
        monster_frame.grid(row=1, column=0, columnspan=4, sticky='we', pady=(0,12))
        monster_frame.grid_columnconfigure(0, weight=1)
        
        # Rotation mode selection
        mode_bar = tk.Frame(monster_frame)
        mode_bar.pack(fill='x', pady=(0,8))
        tk.Label(mode_bar, text=self._t('rotation_mode')).pack(side='left')
        
        self.rotation_mode_var = tk.StringVar(value=self.hunt_cfg.get('rotation_mode', 'sequence'))
        self.rotation_mode_combo = ttk.Combobox(mode_bar, textvariable=self.rotation_mode_var, 
                                                 state='readonly', width=12, values=['sequence', 'priority'])
        self.rotation_mode_combo.pack(side='left', padx=(6,0))
        self.rotation_mode_combo.bind('<<ComboboxSelected>>', self._on_rotation_mode_changed)
        
        # Mode description
        self.rotation_desc_var = tk.StringVar()
        tk.Label(mode_bar, textvariable=self.rotation_desc_var, fg='#666', font=('Arial', 8)).pack(side='left', padx=(8,0))
        
        # Monster list with checkboxes
        list_container = tk.Frame(monster_frame)
        list_container.pack(fill='both', expand=True)
        
        # Listbox frame with scrollbar
        listbox_frame = tk.Frame(list_container)
        listbox_frame.pack(side='left', fill='both', expand=True)
        
        self.monster_rotation_listbox = tk.Listbox(listbox_frame, height=5, exportselection=False, 
                                                    selectmode='single', font=('Arial', 9))
        self.monster_rotation_listbox.pack(side='left', fill='both', expand=True)
        
        monster_scroll = tk.Scrollbar(listbox_frame, orient='vertical', command=self.monster_rotation_listbox.yview)
        monster_scroll.pack(side='right', fill='y')
        self.monster_rotation_listbox.config(yscrollcommand=monster_scroll.set)
        
        # Control buttons (right side) - Using compact icon buttons (all 20px for consistency)
        btn_container = tk.Frame(list_container)
        btn_container.pack(side='right', fill='y', padx=(8,0))
        
        # Add monster button - Compact style (20px: 16px icon + 2×2px padding)
        self.btn_add_monster = self._create_icon_button(
            btn_container,
            icon_emoji="➕",
            command=self._on_monster_add_smart,
            style='compact',
            bg_color=UI.BTN_ACCENT_BG,
            hover_color=UI.BTN_ACCENT_HOVER
        )
        self.btn_add_monster.pack(pady=(0, UI.BTN_SPACING))
        self._create_tooltip(self.btn_add_monster, self._t('tooltip_add_monster_normal'))
        
        # Priority reorder buttons - Compact style (20px: 16px icon + 2×2px padding)
        # Both buttons use blue color for consistency
        self.btn_move_up = self._create_icon_button(
            btn_container,
            icon_emoji="↑",
            command=self._on_monster_move_up,
            style='compact',
            bg_color=UI.BTN_INFO_BG,         # Blue for UP
            hover_color=UI.BTN_INFO_HOVER
        )
        self.btn_move_up.pack(pady=(0, UI.BTN_SPACING // 2))
        self._create_tooltip(self.btn_move_up, self._t('tooltip_move_up'))
        
        self.btn_move_down = self._create_icon_button(
            btn_container,
            icon_emoji="↓",
            command=self._on_monster_move_down,
            style='compact',
            bg_color=UI.BTN_INFO_BG,         # Blue for DOWN
            hover_color=UI.BTN_INFO_HOVER
        )
        self.btn_move_down.pack(pady=(0, UI.BTN_SPACING * 1.5))
        self._create_tooltip(self.btn_move_down, self._t('tooltip_move_down'))
        
        # Library Manager buttons removed per request
        
        # Current monster status
        self.monster_status_var = tk.StringVar()
        tk.Label(monster_frame, textvariable=self.monster_status_var, fg='#2196F3', 
                 font=('Arial', 8, 'bold')).pack(fill='x', pady=(8,0))
        
        # Bind click to toggle checkbox
        self.monster_rotation_listbox.bind('<Double-Button-1>', self._on_monster_toggle)
        self.monster_rotation_listbox.bind('<<ListboxSelect>>', self._on_monster_list_select)
        
        # Legacy monster estimate (keep for compatibility)
        self.monster_estimate_var.set('')

        # Section 2.5: Training Mode Toggle (Sprint 22 Patch 1)
        training_frame = tk.Frame(frm)
        training_frame.grid(row=1, column=4, columnspan=4, sticky='we', pady=(0,12), padx=(12,0))
        
        self.training_mode_var = tk.BooleanVar(value=bool(self.hunt_cfg.get('training_mode_enabled', False)))
        training_check = tk.Checkbutton(
            training_frame, 
            text=self._t('enable_training_mode'),
            variable=self.training_mode_var,
            command=self._on_training_mode_toggled,
            font=('Arial', 9, 'bold')
        )
        training_check.pack(anchor='w')
        
        # Training mode description
        training_desc = tk.Label(
            training_frame,
            text=self._t('training_mode_desc'),
            fg='#666',
            font=('Arial', 8),
            wraplength=250,
            justify='left'
        )
        training_desc.pack(anchor='w', pady=(2,0))
        
        # Training mode status indicator
        self.training_mode_status_var = tk.StringVar()
        training_status = tk.Label(
            training_frame,
            textvariable=self.training_mode_status_var,
            fg='#FF9800',
            font=('Arial', 8, 'bold')
        )
        training_status.pack(anchor='w', pady=(4,0))

        # Section 3: Skill slots selection
        skill_frame_outer = tk.LabelFrame(frm, text=self._t('skill_slots'), padx=10, pady=8)
        skill_frame_outer.grid(row=2, column=0, columnspan=4, sticky='we', pady=(0,12))
        
        # Manage skills hint (button hidden, use Ctrl+K shortcut)
        hint_label = tk.Label(skill_frame_outer, text=f"ℹ️ {self._t('skill_manage_hint')}", 
                             fg='#666', font=('Arial', 8), cursor='hand2')
        hint_label.pack(pady=(0,6))
        hint_label.bind('<Button-1>', lambda e: self._open_skill_manager())

        slot_frame = tk.Frame(skill_frame_outer)
        slot_frame.pack(fill='both', expand=True)
        slot_frame.grid_columnconfigure(1, weight=1)
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        for idx in range(self.skill_slot_count):
            var = tk.StringVar()
            self.skill_slot_vars.append(var)
            label = self._t('skill_slot_label').format(i=idx + 1)
            tk.Label(slot_frame, text=label).grid(row=idx, column=0, sticky='e', pady=2)
            cmb = ttk.Combobox(slot_frame, textvariable=var, state='readonly', width=24)
            cmb.grid(row=idx, column=1, sticky='we', padx=(4,0), pady=2)
            cmb.bind('<<ComboboxSelected>>', self.on_skill_slot_changed)
            tk.Button(slot_frame, text=self._t('skill_slot_clear'), command=lambda v=var: self._clear_skill_slot(v)).grid(row=idx, column=2, padx=(6,0))
            self.skill_slot_boxes.append(cmb)

        self._refresh_monster_select_options()
        self._load_skill_slots_from_cfg()
        
        # Phase 3: Populate monster rotation list
        self._refresh_monster_rotation_list()

        # Section 3.5: Skill Performance Statistics (Sprint 22 Patch 1 - Training Mode)
        self.skill_stats_frame = tk.LabelFrame(frm, text=self._t('skill_stats_title'), padx=10, pady=8)
        self.skill_stats_frame.grid(row=2, column=4, rowspan=1, columnspan=4, sticky='nswe', padx=(12,0), pady=(0,12))
        
        # Create Treeview for stats display
        stats_container = tk.Frame(self.skill_stats_frame)
        stats_container.pack(fill='both', expand=True)
        
        # Define columns
        columns = ('skill', 'casts', 'last_cast', 'cooldown', 'success')
        self.skill_stats_tree = ttk.Treeview(stats_container, columns=columns, show='headings', height=6)
        
        # Configure column headings
        self.skill_stats_tree.heading('skill', text=self._t('skill_name_col'))
        self.skill_stats_tree.heading('casts', text=self._t('cast_count_col'))
        self.skill_stats_tree.heading('last_cast', text=self._t('last_cast_col'))
        self.skill_stats_tree.heading('cooldown', text=self._t('cooldown_col'))
        self.skill_stats_tree.heading('success', text=self._t('success_rate_col'))
        
        # Configure column widths
        self.skill_stats_tree.column('skill', width=120)
        self.skill_stats_tree.column('casts', width=60, anchor='center')
        self.skill_stats_tree.column('last_cast', width=80, anchor='center')
        self.skill_stats_tree.column('cooldown', width=80, anchor='center')
        self.skill_stats_tree.column('success', width=80, anchor='center')
        
        # Add scrollbar
        stats_scroll = tk.Scrollbar(stats_container, orient='vertical', command=self.skill_stats_tree.yview)
        stats_scroll.pack(side='right', fill='y')
        self.skill_stats_tree.config(yscrollcommand=stats_scroll.set)
        self.skill_stats_tree.pack(side='left', fill='both', expand=True)
        
        # Configure tags for color coding
        self.skill_stats_tree.tag_configure('excellent', foreground='#4CAF50')  # Green
        self.skill_stats_tree.tag_configure('good', foreground='#FF9800')      # Orange
        self.skill_stats_tree.tag_configure('poor', foreground='#F44336')      # Red
        
        # Initially hide stats frame (show only when training mode enabled)
        if not self.training_mode_var.get():
            self.skill_stats_frame.grid_remove()

        # Section 4: Status Display (wizard button moved to Setup tab)
        self.hunt_status = tk.StringVar(value=self._t('hunt_idle'))
        status_label = tk.Label(frm, textvariable=self.hunt_status, fg='#666', font=('Arial', 9), 
                               relief='sunken', padx=8, pady=4)
        status_label.grid(row=3, column=0, columnspan=8, sticky='we')

        # Helper text for beginners
        tk.Label(frm, text=self._t('hunt_tab_help_text'), fg='#999', font=('Arial', 8)).grid(row=4, column=0, columnspan=8, pady=(8,0))

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
        self.hunt_cfg['ui_mode'] = mode
        try:
            with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")
        
        # Apply visibility changes
        self._apply_hunt_mode()
        
        # Update status
        mode_labels = {
            'beginner': self._t('mode_beginner'),
            'intermediate': self._t('mode_intermediate'),
            'advanced': self._t('mode_advanced')
        }
        self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)} - {self._t('hunt_idle')}")
    
    def _apply_hunt_mode(self):
        """Show/hide widgets based on current mode setting."""
        mode = self.hunt_mode_var.get() if hasattr(self, 'hunt_mode_var') else 'beginner'
        
        if mode == 'beginner':
            # Hide intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid_remove()
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()
                
        elif mode == 'intermediate':
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()
                
        elif mode == 'advanced':
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Show advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid(row=row, column=col, **kwargs)
    
    def _update_window_bounds_display(self):
        if not hasattr(self, 'window_bounds_display_var'):
            return
        if self.current_window_bounds:
            bounds_text = '{left},{top},{width},{height}'.format(**self.current_window_bounds)
            self.window_bounds_display_var.set(self._t('hunt_window_bounds').format(value=bounds_text))
        else:
            self.window_bounds_display_var.set(self._t('hunt_window_bounds_none'))
    
    # Setup Tab (Sprint 18 Phase 4)
    def _build_setup_tab(self, parent):
        """Build Setup tab with configuration and library management."""
        
        # Section 1: Configuration Mode
        mode_frame = tk.LabelFrame(parent, text=self._t('setup_mode'), padx=12, pady=10)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky='we', pady=(0,12))
        
        mode_desc = tk.Label(mode_frame, text=self._t('setup_mode_desc'), fg='#666', font=('Arial', 9))
        mode_desc.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0,8))
        
        # Read current mode from hunt_cfg
        current_mode = self.hunt_cfg.get('ui_mode', 'beginner')
        self.setup_mode_var = tk.StringVar(value=current_mode)
        
        modes = [
            ('beginner', self._t('mode_beginner'), self._t('mode_beginner_desc')),
            ('intermediate', self._t('mode_intermediate'), self._t('mode_intermediate_desc')),
            ('advanced', self._t('mode_advanced'), self._t('mode_advanced_desc'))
        ]
        
        for idx, (mode_val, mode_label, mode_desc_text) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=mode_label,
                variable=self.setup_mode_var,
                value=mode_val,
                command=self._on_setup_mode_changed,
                font=('Arial', 9, 'bold')
            )
            rb.grid(row=idx+1, column=0, sticky='w', pady=2)
            
            desc_label = tk.Label(mode_frame, text=f"  {mode_desc_text}", fg='#666', font=('Arial', 8))
            desc_label.grid(row=idx+1, column=1, sticky='w', padx=(4,0), pady=2)
        
        # Setup Wizard button (only enabled in Beginner mode)
        wizard_frame = tk.Frame(parent)
        wizard_frame.grid(row=0, column=2, sticky='e', padx=(12,0))
        
        # Use global blue button style
        from lib.ui.button_styles import get_button_config
        wizard_config = get_button_config('blue')
        
        # Load support icon for Setup Wizard button
        support_icon = self._icon('support', '🧙', size=20)
        
        self.setup_wizard_btn = tk.Button(
            wizard_frame,
            text=f" {self._t('setup_wizard')}" if not isinstance(support_icon, str) else f"🧙 {self._t('setup_wizard')}",
            image=support_icon if not isinstance(support_icon, str) else None,
            compound='left' if not isinstance(support_icon, str) else 'none',
            command=self.on_setup_wizard,
            **wizard_config,
            padx=16,
            pady=8
        )
        self.setup_wizard_btn.pack()
        
        # Keep reference to prevent garbage collection
        if not isinstance(support_icon, str):
            self.setup_wizard_btn.image = support_icon
        
        # Tooltip will be attached in _update_setup_visibility()
        
        # Section 2: Libraries
        lib_frame = tk.LabelFrame(parent, text=self._t('setup_libraries'), padx=12, pady=10)
        lib_frame.grid(row=1, column=0, columnspan=2, sticky='we', pady=(0,12))
        
        # Description
        lib_desc = tk.Label(lib_frame, text=self._t('setup_libraries_desc'), fg='#666', font=('Arial', 9))
        lib_desc.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,8))
        
        # Library Manager button (restored)
        tk.Button(
            lib_frame,
            text=f"🗂️ {self._t('open_library_manager')}",
            command=self._open_library_manager,
            padx=10, pady=6
        ).grid(row=1, column=1, sticky='e')
        
        # Status info
        monster_count = len(self.monsters) if hasattr(self, 'monsters') else 0
        skills_count = len(load_skill_library()) if hasattr(self, 'skills') else 0
        
        # Use i18n for counts label
        try:
            status_text = f"{monster_count} {self._t('monsters_count')} • {skills_count} {self._t('skills_count')}"
        except Exception:
            status_text = f"{monster_count} monsters • {skills_count} skills" if self.lang == 'en' else f"{monster_count} quái vật • {skills_count} kỹ năng"
        tk.Label(
            lib_frame,
            text=status_text,
            fg='#666',
            font=('Arial', 9)
        ).grid(row=1, column=0, sticky='w', pady=(0,8))
        
        # Hint
        hint_text = self._t('library_manager_hint')
        tk.Label(
            lib_frame,
            text=f"💡 {hint_text}",
            fg='#1976D2',
            font=('Arial', 8),
            wraplength=500,
            justify='left'
        ).grid(row=2, column=0, columnspan=2, sticky='w', pady=(8,0))
        
        # Section 2.5: Global Hotkeys
        hotkey_frame = tk.LabelFrame(parent, text="⌨️ Global Hotkeys", padx=12, pady=10)
        hotkey_frame.grid(row=1, column=2, rowspan=2, sticky='nwe', padx=(12,0), pady=(0,12))
        
        # Description
        hotkey_desc_text = "Global hotkeys work even when app is minimized or not focused."
        if self.lang == 'vi':
            hotkey_desc_text = "Phím tắt toàn cục hoạt động khi ứng dụng thu nhỏ hoặc không focus."
        tk.Label(
            hotkey_frame,
            text=hotkey_desc_text,
            fg='#666',
            font=('Arial', 8),
            wraplength=280,
            justify='left'
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,8))
        
        # Enable/Disable checkbox
        hotkey_cfg = self.hunt_cfg.get('global_hotkeys', {})
        self.global_hotkey_enabled_var = tk.BooleanVar(value=hotkey_cfg.get('enabled', True))
        
        enable_text = "Enable Global Hotkeys" if self.lang == 'en' else "Bật phím tắt toàn cục"
        tk.Checkbutton(
            hotkey_frame,
            text=enable_text,
            variable=self.global_hotkey_enabled_var,
            font=('Arial', 9, 'bold'),
            command=self._on_global_hotkey_toggle
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0,8))
        
        # Start hotkey
        start_label = "Start Hunt:" if self.lang == 'en' else "Bắt đầu Hunt:"
        tk.Label(hotkey_frame, text=start_label, font=('Arial', 9)).grid(row=2, column=0, sticky='e', padx=(0,8), pady=4)
        
        # Combobox for start key
        start_key = hotkey_cfg.get('start_key', 'ctrl+shift+r')
        self.global_hotkey_start_var = tk.StringVar(value=start_key)
        
        hotkey_options = [
            'ctrl+shift+r',
            'ctrl+shift+s',
            'ctrl+alt+r',
            'ctrl+alt+s',
            'f9',
            'f10',
            'f11',
            'f12'
        ]
        
        from tkinter import ttk
        start_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_start_var,
            values=hotkey_options,
            width=15,
            state='readonly'
        )
        start_combo.grid(row=2, column=1, sticky='w', pady=4)
        
        # Stop hotkey
        stop_label = "Stop Hunt:" if self.lang == 'en' else "Dừng Hunt:"
        tk.Label(hotkey_frame, text=stop_label, font=('Arial', 9)).grid(row=3, column=0, sticky='e', padx=(0,8), pady=4)
        
        # Combobox for stop key
        stop_key = hotkey_cfg.get('stop_key', 'ctrl+shift+e')
        self.global_hotkey_stop_var = tk.StringVar(value=stop_key)
        
        stop_combo = ttk.Combobox(
            hotkey_frame,
            textvariable=self.global_hotkey_stop_var,
            values=hotkey_options,
            width=15,
            state='readonly'
        )
        stop_combo.grid(row=3, column=1, sticky='w', pady=4)
        
        # Hint
        hint_hotkey = "💡 Press 'Global Apply' button below to activate new hotkeys."
        if self.lang == 'vi':
            hint_hotkey = "💡 Nhấn nút 'Global Apply' phía dưới để kích hoạt phím tắt mới."
        tk.Label(
            hotkey_frame,
            text=hint_hotkey,
            fg='#1976D2',
            font=('Arial', 8),
            wraplength=280,
            justify='left'
        ).grid(row=4, column=0, columnspan=2, sticky='w', pady=(8,0))
        
        # Section 3: Advanced Hunt Settings (visible for intermediate/advanced)
        self.adv_frame = tk.LabelFrame(parent, text=self._t('setup_advanced'), padx=12, pady=10)
        self.adv_frame.grid(row=2, column=0, columnspan=2, sticky='we', pady=(0,12))
        
        # Target/Attack keys
        tk.Label(self.adv_frame, text=self._t('target_key')).grid(row=0, column=0, sticky='e', pady=4)
        self.setup_target_key_var = tk.StringVar(value=str(self.hunt_cfg.get('target_key', 'TAB')))
        tk.Entry(self.adv_frame, textvariable=self.setup_target_key_var, width=8).grid(row=0, column=1, sticky='w', pady=4)
        
        tk.Label(self.adv_frame, text=self._t('attack_keys')).grid(row=0, column=2, sticky='e', padx=(16,4), pady=4)
        self.setup_attack_keys_var = tk.StringVar(value=','.join(self.hunt_cfg.get('attack_keys', ['1','2','3'])))
        tk.Entry(self.adv_frame, textvariable=self.setup_attack_keys_var, width=18).grid(row=0, column=3, sticky='w', pady=4)
        
        # Timing intervals
        tk.Label(self.adv_frame, text=self._t('press_ms')).grid(row=1, column=0, sticky='e', pady=4)
        self.setup_press_ms_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_press_ms', 60)))
        tk.Entry(self.adv_frame, textvariable=self.setup_press_ms_var, width=8).grid(row=1, column=1, sticky='w', pady=4)
        
        tk.Label(self.adv_frame, text=self._t('target_cycle')).grid(row=1, column=2, sticky='e', padx=(16,4), pady=4)
        self.setup_target_cycle_var = tk.StringVar(value=str(self.hunt_cfg.get('target_cycle_delay', 0.2)))
        tk.Entry(self.adv_frame, textvariable=self.setup_target_cycle_var, width=8).grid(row=1, column=3, sticky='w', pady=4)
        
        tk.Label(self.adv_frame, text=self._t('search_interval')).grid(row=2, column=0, sticky='e', pady=4)
        self.setup_search_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('search_interval', 0.25)))
        tk.Entry(self.adv_frame, textvariable=self.setup_search_interval_var, width=8).grid(row=2, column=1, sticky='w', pady=4)
        
        tk.Label(self.adv_frame, text=self._t('attack_interval')).grid(row=2, column=2, sticky='e', padx=(16,4), pady=4)
        self.setup_attack_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_interval', 0.15)))
        tk.Entry(self.adv_frame, textvariable=self.setup_attack_interval_var, width=8).grid(row=2, column=3, sticky='w', pady=4)
        
        # Lost timeout & Attack duration
        tk.Label(self.adv_frame, text=self._t('lost_timeout')).grid(row=3, column=0, sticky='e', pady=4)
        self.setup_lost_timeout_var = tk.StringVar(value=str(self.hunt_cfg.get('lost_timeout_sec', 1.2)))
        lost_entry = tk.Entry(self.adv_frame, textvariable=self.setup_lost_timeout_var, width=8)
        lost_entry.grid(row=3, column=1, sticky='w', pady=4)
        attach_i18n_tooltip(lost_entry, key='tooltip_lost_timeout', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        
        tk.Label(self.adv_frame, text=self._t('attack_duration')).grid(row=3, column=2, sticky='e', padx=(16,4), pady=4)
        self.setup_attack_duration_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_min_duration_sec', 1.5)))
        attack_entry = tk.Entry(self.adv_frame, textvariable=self.setup_attack_duration_var, width=8)
        attack_entry.grid(row=3, column=3, sticky='w', pady=4)
        attach_i18n_tooltip(attack_entry, key='tooltip_attack_duration', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        
        # Template threshold
        tk.Label(self.adv_frame, text=self._t('template_threshold')).grid(row=4, column=0, sticky='e', pady=4)
        self.setup_threshold_var = tk.StringVar(value=str(self.hunt_cfg.get('template_threshold', 0.8)))
        tk.Entry(self.adv_frame, textvariable=self.setup_threshold_var, width=8).grid(row=4, column=1, sticky='w', pady=4)
        
        # Section 4: Window Settings (visible for advanced only)
        self.window_frame = tk.LabelFrame(parent, text=self._t('setup_window'), padx=12, pady=10)
        self.window_frame.grid(row=3, column=0, columnspan=2, sticky='we', pady=(0,12))
        
        # Template path
        tk.Label(self.window_frame, text=self._t('template')).grid(row=0, column=0, sticky='e', pady=4)
        self.setup_template_var = tk.StringVar(value=str(self.hunt_cfg.get('template_path', 'assets/images/target_frame.png')))
        tk.Entry(self.window_frame, textvariable=self.setup_template_var, width=40).grid(row=0, column=1, columnspan=2, sticky='w', pady=4)
        tk.Button(self.window_frame, text=self._t('browse'), command=self.on_hunt_browse_template).grid(row=0, column=3, padx=(4,0), pady=4)
        
        # Region
        tk.Label(self.window_frame, text=self._t('region_l')).grid(row=1, column=0, sticky='e', pady=4)
        region = self.hunt_cfg.get('region') or ["", "", "", ""]
        self.setup_reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.setup_reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.setup_reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.setup_reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")
        
        reg_frame = tk.Frame(self.window_frame)
        reg_frame.grid(row=1, column=1, columnspan=3, sticky='w', pady=4)
        
        tk.Entry(reg_frame, textvariable=self.setup_reg_l, width=6).pack(side='left')
        tk.Label(reg_frame, text=self._t('t')).pack(side='left', padx=(8,4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_t, width=6).pack(side='left')
        tk.Label(reg_frame, text=self._t('w')).pack(side='left', padx=(8,4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_w, width=6).pack(side='left')
        tk.Label(reg_frame, text=self._t('h')).pack(side='left', padx=(8,4))
        tk.Entry(reg_frame, textvariable=self.setup_reg_h, width=6).pack(side='left')
        
        # Window bounds display
        tk.Label(self.window_frame, text=self._t('hunt_window_bounds_label')).grid(row=2, column=0, sticky='e', pady=(8,4))
        self.setup_bounds_display_var = tk.StringVar(value=self._t('hunt_window_bounds_none'))
        tk.Label(self.window_frame, textvariable=self.setup_bounds_display_var, fg='blue').grid(row=2, column=1, columnspan=2, sticky='w', pady=(8,4))
        tk.Button(self.window_frame, text=self._t('clear_bounds'), command=self._clear_window_bounds).grid(row=2, column=3, padx=(4,0), pady=(8,4))
        
        # Apply button removed - now using global apply button below tabs
        
        # Initial visibility update based on mode
        self._update_setup_visibility()
    
    # Stats Tab (Sprint 18 Phase 4)
    def _build_stats_tab(self, parent):
        """Build Stats tab with runtime statistics and performance metrics."""
        # TODO: Implement Stats tab
        placeholder = tk.Label(parent, text="Stats Tab - Coming Soon\n\nThis tab will contain:\n• Hunt Statistics (runtime, kills, exp/hr)\n• Performance Metrics (FPS, CPU, memory)\n• Rotation History\n• Export controls", 
                              justify='left', padx=20, pady=20)
        placeholder.pack()
    
    # Help Tab (Sprint 18 Phase 4)
    def _build_help_tab(self, parent):
        """Build Help tab with documentation and tutorials."""
        # Scrollable frame for help content
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Quick Start Guide
        help_frame = tk.LabelFrame(scrollable_frame, text=self._t('help_quickstart'), padx=10, pady=8, bg='white')
        help_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(help_frame, text=self._t('help_quickstart_text'), justify='left', bg='white').pack(anchor='w')
        
        # Keyboard Shortcuts
        shortcuts_frame = tk.LabelFrame(scrollable_frame, text=self._t('help_shortcuts'), padx=10, pady=8, bg='white')
        shortcuts_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(shortcuts_frame, text=self._t('help_shortcuts_text'), justify='left', bg='white').pack(anchor='w')
        
        # Troubleshooting
        trouble_frame = tk.LabelFrame(scrollable_frame, text=self._t('help_troubleshooting'), padx=10, pady=8, bg='white')
        trouble_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(trouble_frame, text=self._t('help_troubleshooting_text'), justify='left', bg='white').pack(anchor='w')
        
        # About
        about_frame = tk.LabelFrame(scrollable_frame, text=self._t('help_about'), padx=10, pady=8, bg='white')
        about_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(about_frame, text=self._t('help_about_text'), justify='left', bg='white').pack(anchor='w')
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    # Setup Tab Handlers (Sprint 18 Phase 4)
    def _on_setup_mode_changed(self):
        """Handle mode change in Setup tab and sync with Hunt tab."""
        mode = self.setup_mode_var.get()
        
        # Save mode preference
        self.hunt_cfg['ui_mode'] = mode
        try:
            with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")
        
        # Sync Hunt tab mode var if it exists
        if hasattr(self, 'hunt_mode_var'):
            self.hunt_mode_var.set(mode)
            self._apply_hunt_mode()
        
        # Update Setup tab visibility
        self._update_setup_visibility()
        
        # Update status if exists
        if hasattr(self, 'hunt_status'):
            mode_labels = {
                'beginner': self._t('mode_beginner'),
                'intermediate': self._t('mode_intermediate'),
                'advanced': self._t('mode_advanced')
            }
            self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)}")
    
    def _on_global_hotkey_toggle(self):
        """Handle enable/disable of global hotkeys checkbox.
        
        Note: Changes only take effect after clicking Global Apply button.
        This is intentional to avoid accidental hotkey changes during configuration.
        """
        enabled = self.global_hotkey_enabled_var.get()
        
        # Update status message
        if hasattr(self, 'hunt_status'):
            if enabled:
                msg = "Global hotkeys will be enabled after clicking 'Global Apply'"
                if self.lang == 'vi':
                    msg = "Phím tắt toàn cục sẽ được bật sau khi nhấn 'Global Apply'"
            else:
                msg = "Global hotkeys will be disabled after clicking 'Global Apply'"
                if self.lang == 'vi':
                    msg = "Phím tắt toàn cục sẽ bị tắt sau khi nhấn 'Global Apply'"
            self.hunt_status.set(msg)
    
    def _update_setup_visibility(self):
        """Show/hide Setup tab sections based on current mode."""
        mode = self.setup_mode_var.get() if hasattr(self, 'setup_mode_var') else 'beginner'
        
        # Update wizard button state based on mode
        if hasattr(self, 'setup_wizard_btn'):
            if mode == 'beginner':
                self.setup_wizard_btn.config(state='normal', cursor='hand2')
                # Attach enabled tooltip
                from lib.ui.tooltip import attach_i18n_tooltip
                attach_i18n_tooltip(self.setup_wizard_btn, key='wizard_enabled_tooltip', 
                                   ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
            else:
                self.setup_wizard_btn.config(state='disabled', cursor='arrow')
                # Attach disabled tooltip
                from lib.ui.tooltip import attach_i18n_tooltip
                attach_i18n_tooltip(self.setup_wizard_btn, key='wizard_disabled_tooltip', 
                                   ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        
        if mode == 'beginner':
            # Hide advanced sections
            self.adv_frame.grid_remove()
            self.window_frame.grid_remove()
        elif mode == 'intermediate':
            # Show advanced hunt settings, hide window settings
            self.adv_frame.grid()
            self.window_frame.grid_remove()
        elif mode == 'advanced':
            # Show all sections
            self.adv_frame.grid()
            self.window_frame.grid()
    
    def _open_library_manager(self):
        """
        Open Library Manager window for centralized library management.
        
        Sprint 19 Task #1: Library Manager Window
        """
        from lib.ui.library_manager import LibraryManagerWindow
        
        def on_library_changes(changes):
            """Handle changes from Library Manager."""
            # Update monsters if changed
            if changes.get('monsters_changed'):
                self.monsters = changes.get('monsters', self.monsters)
                save_monster_library(self.monsters)
                self._refresh_monster_list()  # Refresh Hunt tab monster dropdown
                
            # Update skills if changed
            if changes.get('skills_changed'):
                self.skills = changes.get('skills', self.skills)
                save_skill_library(self.skills)
                self._refresh_skill_display()  # Refresh Hunt tab skill display
                
            # Update hunt config if timing applied
            if changes.get('timing_applied'):
                self.hunt_cfg = changes.get('hunt_cfg', self.hunt_cfg)
                save_hunt_config(self.hunt_cfg)
                self._reload_setup_advanced_settings()  # Refresh Setup tab Advanced Settings
                
            # Update status
            self.hunt_status.set(self._t('library_updated'))
        
        # Open Library Manager window
        try:
            manager = LibraryManagerWindow(
                parent=self,
                hunt_cfg=self.hunt_cfg,
                monsters=self.monsters,
                skills=load_skill_library(),
                lang=self.lang,
                on_close_callback=on_library_changes
            )
        except Exception as e:
            messagebox.showerror(
                self._t('error_title'),
                f"Failed to open Library Manager: {e}\n\nPlease check console for details."
            )
            import traceback
            traceback.print_exc()
    
    def _refresh_skill_display(self):
        """Refresh skill display in Hunt tab after library changes."""
        # Refresh skill slots dropdown options
        if hasattr(self, '_refresh_skill_slots_options'):
            self._refresh_skill_slots_options()
        
        # Refresh skill list if in advanced mode
        if hasattr(self, '_refresh_skill_list'):
            self._refresh_skill_list()
    
    def _reload_setup_advanced_settings(self):
        """Reload Advanced Settings values in Setup tab after timing changes."""
        # Update variables with new values from hunt_cfg
        if hasattr(self, 'setup_search_interval_var'):
            self.setup_search_interval_var.set(f"{self.hunt_cfg.get('search_interval', 0.25):.2f}")
        if hasattr(self, 'setup_attack_interval_var'):
            self.setup_attack_interval_var.set(f"{self.hunt_cfg.get('attack_interval', 0.15):.2f}")
        if hasattr(self, 'setup_lost_timeout_var'):
            self.setup_lost_timeout_var.set(f"{self.hunt_cfg.get('lost_timeout_sec', 0.5):.2f}")
        if hasattr(self, 'setup_attack_duration_var'):
            self.setup_attack_duration_var.set(f"{self.hunt_cfg.get('attack_min_duration_sec', 5.0):.2f}")
    
    def _open_monster_library(self):
        """Open Monster Library Manager dialog."""
        # TODO: Integrate with existing monster manager
        messagebox.showinfo(
            self._t('monster_section'),
            f"{self._t('monsters_count')}: {len(self.monsters) if hasattr(self, 'monsters') else 0}\n\n"
            f"Monster library management feature coming soon..."
        )
    
    def _open_skills_library(self):
        """Open Skills Library Manager dialog."""
        # TODO: Integrate with existing skills manager
        messagebox.showinfo(
            self._t('skill_section'),
            f"{self._t('skills_count')}: {len(self.skills) if hasattr(self, 'skills') else 0}\n\n"
            f"Skills library management feature coming soon..."
        )
    
    def _clear_window_bounds(self):
        """Clear stored window bounds."""
        self.current_window_bounds = None
        self.setup_bounds_display_var.set(self._t('hunt_window_bounds_none'))
        self.hunt_status.set(self._t('hunt_window_bounds_cleared') if hasattr(self, 'hunt_status') else 'Window bounds cleared')
    
    def _apply_setup_settings(self, save_to_file=True):
        """Apply all settings from Setup tab to hunt_config and sync to Hunt tab.
        
        Args:
            save_to_file: If True, save to hunt_config.json immediately.
                         If False, only update self.hunt_cfg (used by on_global_apply to avoid duplicate writes).
        """
        try:
            # Update hunt_cfg with values from Setup tab
            self.hunt_cfg['target_key'] = self.setup_target_key_var.get()
            self.hunt_cfg['attack_keys'] = [k.strip() for k in self.setup_attack_keys_var.get().split(',') if k.strip()]
            self.hunt_cfg['attack_press_ms'] = int(self.setup_press_ms_var.get())
            self.hunt_cfg['target_cycle_delay'] = float(self.setup_target_cycle_var.get())
            self.hunt_cfg['search_interval'] = float(self.setup_search_interval_var.get())
            self.hunt_cfg['attack_interval'] = float(self.setup_attack_interval_var.get())
            self.hunt_cfg['lost_timeout_sec'] = float(self.setup_lost_timeout_var.get())
            self.hunt_cfg['attack_min_duration_sec'] = float(self.setup_attack_duration_var.get())
            self.hunt_cfg['template_threshold'] = float(self.setup_threshold_var.get())
            self.hunt_cfg['template_path'] = self.setup_template_var.get()
            
            # Region
            try:
                l = int(self.setup_reg_l.get()) if self.setup_reg_l.get() else ""
                t = int(self.setup_reg_t.get()) if self.setup_reg_t.get() else ""
                w = int(self.setup_reg_w.get()) if self.setup_reg_w.get() else ""
                h = int(self.setup_reg_h.get()) if self.setup_reg_h.get() else ""
                self.hunt_cfg['region'] = [l, t, w, h]
            except ValueError:
                self.hunt_cfg['region'] = ["", "", "", ""]
            
            # Save to file only if requested
            if save_to_file:
                with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
            
            # Sync to Hunt tab vars if they exist
            if hasattr(self, 'target_key_var'):
                self.target_key_var.set(self.hunt_cfg['target_key'])
            if hasattr(self, 'attack_keys_var'):
                self.attack_keys_var.set(','.join(self.hunt_cfg['attack_keys']))
            if hasattr(self, 'attack_press_var'):
                self.attack_press_var.set(str(self.hunt_cfg['attack_press_ms']))
            if hasattr(self, 'target_cycle_var'):
                self.target_cycle_var.set(str(self.hunt_cfg['target_cycle_delay']))
            if hasattr(self, 'search_interval_var'):
                self.search_interval_var.set(str(self.hunt_cfg['search_interval']))
            if hasattr(self, 'attack_interval_var'):
                self.attack_interval_var.set(str(self.hunt_cfg['attack_interval']))
            if hasattr(self, 'lost_timeout_var'):
                self.lost_timeout_var.set(str(self.hunt_cfg['lost_timeout_sec']))
            if hasattr(self, 'attack_duration_var'):
                self.attack_duration_var.set(str(self.hunt_cfg['attack_min_duration_sec']))
            if hasattr(self, 'template_var'):
                self.template_var.set(self.hunt_cfg['template_path'])
            if hasattr(self, 'reg_l'):
                region = self.hunt_cfg['region']
                self.reg_l.set(str(region[0]) if region[0] != "" else "")
                self.reg_t.set(str(region[1]) if region[1] != "" else "")
                self.reg_w.set(str(region[2]) if region[2] != "" else "")
                self.reg_h.set(str(region[3]) if region[3] != "" else "")
            
            # Show success feedback only when saving directly (not called from on_global_apply)
            if save_to_file:
                # Update status
                if hasattr(self, 'hunt_status'):
                    self.hunt_status.set(self._t('settings_applied_success'))
                
                # Show success message
                messagebox.showinfo(
                    self._t('success_title'),
                    self._t('settings_applied_message')
                )
            
        except ValueError as e:
            messagebox.showerror(
                self._t('error_title'),
                self._t('error_invalid_number').format(field=str(e))
            )
        except Exception as e:
            messagebox.showerror(
                self._t('error_title'),
                f"Failed to apply settings: {e}"
            )
    
    # Phase 3: Multi-Monster Support Handlers
    def _load_monster_rotation_list(self):
        """Load monster_list from hunt_config into UI."""
        saved_list = self.hunt_cfg.get('monster_list', [])
        self.monster_rotation_list = []
        
        for item in saved_list:
            if isinstance(item, dict):
                self.monster_rotation_list.append({
                    'name': item.get('name', ''),
                    'priority': item.get('priority', 1),
                    'enabled': item.get('enabled', True)
                })
        
        # If empty, populate from monsters library for convenience
        if not self.monster_rotation_list and self.monsters:
            for idx, monster in enumerate(self.monsters[:5]):  # Top 5 monsters
                self.monster_rotation_list.append({
                    'name': monster['name'],
                    'priority': idx + 1,
                    'enabled': False  # Disabled by default
                })
    
    def _refresh_monster_rotation_list(self):
        """Refresh the monster rotation listbox display.
        
        Sprint 22 Patch 1: If training_mode_enabled, filter to show only training dummies.
        """
        if not hasattr(self, 'monster_rotation_listbox'):
            return
        
        self.monster_rotation_listbox.delete(0, tk.END)
        
        # Filter monsters based on training mode
        is_training_mode = self.training_mode_var.get() if hasattr(self, 'training_mode_var') else False
        
        display_list = self.monster_rotation_list
        if is_training_mode:
            # Filter to show only training dummies
            display_list = [m for m in self.monster_rotation_list if m.get('training_mode', False)]
            
            # Update status if no training dummies found
            if not display_list and hasattr(self, 'training_mode_status_var'):
                self.training_mode_status_var.set(f"⚠️ {self._t('no_training_dummies')}")
        
        for item in display_list:
            check = "☑" if item['enabled'] else "☐"
            display = f"{check} {item['name']}"
            if self.hunt_cfg.get('rotation_mode') == 'priority':
                display += f" (P{item['priority']})"
            # Add training dummy indicator
            if item.get('training_mode', False):
                display += " 🎯"
            self.monster_rotation_listbox.insert(tk.END, display)
        
        self._update_monster_status()
        self._update_rotation_mode_description()
        
        # Update button states if in training mode
        if hasattr(self, 'training_mode_var'):
            self._update_training_mode_buttons()
    
    def _update_monster_status(self):
        """Update current monster hunting status display."""
        if not hasattr(self, 'monster_status_var'):
            return
        
        enabled = [m for m in self.monster_rotation_list if m['enabled']]
        if not enabled:
            self.monster_status_var.set(self._t('monster_none_selected'))
            return
        
        mode = self.hunt_cfg.get('rotation_mode', 'sequence')
        current_idx = self.hunt_cfg.get('current_monster_index', 0)
        
        if mode == 'sequence':
            if current_idx < len(enabled):
                current = enabled[current_idx]
                self.monster_status_var.set(f"Current: {current['name']} | Sequence: {current_idx+1}/{len(enabled)}")
            else:
                self.monster_status_var.set(f"Sequence: {len(enabled)} monsters")
        else:  # priority
            sorted_monsters = sorted(enabled, key=lambda m: m['priority'])
            current = sorted_monsters[0]
            self.monster_status_var.set(f"Priority: {current['name']} (P{current['priority']}) | {len(enabled)} total")
    
    def _update_rotation_mode_description(self):
        """Update rotation mode description."""
        if not hasattr(self, 'rotation_desc_var'):
            return
        
        mode = self.rotation_mode_var.get()
        if mode == 'sequence':
            self.rotation_desc_var.set("Hunt monsters in order, cycle through list")
        elif mode == 'priority':
            self.rotation_desc_var.set("Always hunt highest priority (lowest number)")
    
    def _on_rotation_mode_changed(self, event=None):
        """Handle rotation mode change."""
        mode = self.rotation_mode_var.get()
        self.hunt_cfg['rotation_mode'] = mode
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
        self.hunt_cfg['training_mode_enabled'] = is_enabled
        
        # Save to config file
        try:
            with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save training_mode_enabled: {e}")
        
        # Update UI feedback
        if is_enabled:
            self.training_mode_status_var.set(self._t('training_mode_active'))
            self.hunt_status.set(self._t('training_mode_active'))
        else:
            self.training_mode_status_var.set('')
            self.hunt_status.set(self._t('training_mode_disabled'))
        
        # Refresh monster rotation list (will filter if training mode is on)
        self._refresh_monster_rotation_list()
        
        # Show/hide skill stats frame if it exists
        if hasattr(self, 'skill_stats_frame'):
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
        if not hasattr(self, 'btn_add_monster'):
            return
        
        is_training = self.training_mode_var.get()
        has_training_dummy = any(m.get('training_mode', False) for m in self.monster_rotation_list)
        
        if is_training:
            # Training mode: Update add button
            if has_training_dummy:
                # Dummy already set - show accept icon and disable
                try:
                    # Use size=16 to match compact button
                    accept_icon = self._icon('accept', '✓', size=16)
                    if isinstance(accept_icon, str):
                        self.btn_add_monster.config(text=accept_icon, state='disabled')
                    else:
                        self.btn_add_monster.config(image=accept_icon, text='', state='disabled')
                except Exception:
                    self.btn_add_monster.config(text='✓', state='disabled')
                
                # Update tooltip
                tooltip_text = self._t('tooltip_add_monster_locked')
                if hasattr(self.btn_add_monster, '_tooltip'):
                    self.btn_add_monster._tooltip.destroy()
                self._create_tooltip(self.btn_add_monster, tooltip_text)
            else:
                # No dummy yet - show add icon and enable
                try:
                    # Use size=16 to match compact button
                    add_icon = self._icon('add', '➕', size=16)
                    if isinstance(add_icon, str):
                        self.btn_add_monster.config(text=add_icon, state='normal')
                    else:
                        self.btn_add_monster.config(image=add_icon, text='', state='normal')
                except Exception:
                    self.btn_add_monster.config(text='➕', state='normal')
                
                # Update tooltip
                tooltip_text = self._t('tooltip_add_monster_training')
                if hasattr(self.btn_add_monster, '_tooltip'):
                    self.btn_add_monster._tooltip.destroy()
                self._create_tooltip(self.btn_add_monster, tooltip_text)
            
            # Disable priority reorder buttons with locked icon (white on gray)
            # Use size=16 to match SMALL buttons (36px)
            try:
                locked_icon = self._icon('locked', '🔒', size=16, color='#FFFFFF')
                for btn in [self.btn_move_up, self.btn_move_down]:
                    # IMPORTANT: Keep original bg colors when disabled
                    original_bg = UI.BTN_NEUTRAL_BG if btn == self.btn_move_up else UI.BTN_NEUTRAL_BG
                    btn.config(state='disabled', bg=original_bg)
                    if isinstance(locked_icon, str):
                        btn.config(text=locked_icon)
                    else:
                        btn.config(image=locked_icon, text='')
            except Exception:
                self.btn_move_up.config(state='disabled', text='🔒', bg=UI.BTN_NEUTRAL_BG)
                self.btn_move_down.config(state='disabled', text='🔒', bg=UI.BTN_NEUTRAL_BG)
            
            # Update tooltips for disabled buttons
            for btn in [self.btn_move_up, self.btn_move_down]:
                if hasattr(btn, '_tooltip'):
                    btn._tooltip.destroy()
                self._create_tooltip(btn, self._t('tooltip_reorder_locked'))
        else:
            # Normal mode: Restore defaults
            try:
                # Use size=16 to match compact button
                add_icon = self._icon('add', '➕', size=16)
                if isinstance(add_icon, str):
                    self.btn_add_monster.config(text=add_icon, state='normal')
                else:
                    self.btn_add_monster.config(image=add_icon, text='', state='normal')
            except Exception:
                self.btn_add_monster.config(text='➕', state='normal')
            
            # Restore normal tooltip
            if hasattr(self.btn_add_monster, '_tooltip'):
                self.btn_add_monster._tooltip.destroy()
            self._create_tooltip(self.btn_add_monster, self._t('tooltip_add_monster_normal'))
            
            # Enable priority reorder buttons with original icons and colors (both blue for consistency)
            try:
                # Use size=16 to match SMALL buttons
                up_icon = self._icon('up', '↑', size=16)
                down_icon = self._icon('down', '↓', size=16)
                
                if isinstance(up_icon, str):
                    self.btn_move_up.config(
                        state='normal', 
                        text=up_icon,
                        bg=UI.BTN_INFO_BG,         # Blue for consistency
                        fg=UI.BTN_INFO_FG
                    )
                else:
                    self.btn_move_up.config(
                        state='normal', 
                        image=up_icon, 
                        text='',
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG
                    )
                
                if isinstance(down_icon, str):
                    self.btn_move_down.config(
                        state='normal', 
                        text=down_icon,
                        bg=UI.BTN_INFO_BG,         # Blue for consistency
                        fg=UI.BTN_INFO_FG
                    )
                else:
                    self.btn_move_down.config(
                        state='normal', 
                        image=down_icon, 
                        text='',
                        bg=UI.BTN_INFO_BG,
                        fg=UI.BTN_INFO_FG
                    )
            except Exception:
                self.btn_move_up.config(
                    state='normal', 
                    text='↑',
                    bg=UI.BTN_INFO_BG,            # Blue for consistency
                    fg=UI.BTN_INFO_FG
                )
                self.btn_move_down.config(
                    state='normal', 
                    text='↓',
                    bg=UI.BTN_INFO_BG,            # Blue for consistency
                    fg=UI.BTN_INFO_FG
                )
            
            # Restore normal tooltips
            if hasattr(self.btn_move_up, '_tooltip'):
                self.btn_move_up._tooltip.destroy()
            self._create_tooltip(self.btn_move_up, self._t('tooltip_move_up'))
            
            if hasattr(self.btn_move_down, '_tooltip'):
                self.btn_move_down._tooltip.destroy()
            self._create_tooltip(self.btn_move_down, self._t('tooltip_move_down'))
    
    def _on_monster_toggle(self, event=None):
        """Toggle monster enabled state on double-click."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx < len(self.monster_rotation_list):
            self.monster_rotation_list[idx]['enabled'] = not self.monster_rotation_list[idx]['enabled']
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
    
    def _on_monster_move_up(self):
        """Move selected monster up in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        # Swap with previous
        self.monster_rotation_list[idx], self.monster_rotation_list[idx-1] = \
            self.monster_rotation_list[idx-1], self.monster_rotation_list[idx]
        
        # Update priorities if in priority mode
        if self.hunt_cfg.get('rotation_mode') == 'priority':
            self.monster_rotation_list[idx]['priority'], self.monster_rotation_list[idx-1]['priority'] = \
                self.monster_rotation_list[idx-1]['priority'], self.monster_rotation_list[idx]['priority']
        
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx-1)
    
    def _on_monster_move_down(self):
        """Move selected monster down in rotation order."""
        selection = self.monster_rotation_listbox.curselection()
        if not selection or selection[0] >= len(self.monster_rotation_list) - 1:
            return
        
        idx = selection[0]
        # Swap with next
        self.monster_rotation_list[idx], self.monster_rotation_list[idx+1] = \
            self.monster_rotation_list[idx+1], self.monster_rotation_list[idx]
        
        # Update priorities if in priority mode
        if self.hunt_cfg.get('rotation_mode') == 'priority':
            self.monster_rotation_list[idx]['priority'], self.monster_rotation_list[idx+1]['priority'] = \
                self.monster_rotation_list[idx+1]['priority'], self.monster_rotation_list[idx]['priority']
        
        self._refresh_monster_rotation_list()
        self.monster_rotation_listbox.selection_set(idx+1)
    
    def _on_monster_add_smart(self):
        """Smart add monster with autocomplete and fuzzy matching hints."""
        dialog = tk.Toplevel(self)
        dialog.title(self._t('monster_add_title'))
        dialog.geometry('500x400')
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        container = tk.Frame(dialog, padx=16, pady=16)
        container.pack(fill='both', expand=True)
        
        # Title + hint
        title_label = tk.Label(container, text=self._t('monster_add_instruction'), 
                               font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w', pady=(0,8))
        
        hint_text = self._t('monster_add_hint')
        hint_label = tk.Label(container, text=hint_text, fg='#666', 
                              font=('Arial', 8), wraplength=450, justify='left')
        hint_label.pack(anchor='w', pady=(0,12))
        
        # Search entry with real-time suggestions
        search_frame = tk.Frame(container)
        search_frame.pack(fill='x', pady=(0,8))
        
        tk.Label(search_frame, text=self._t('monster_name')).pack(side='left')
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side='left', padx=(8,0), fill='x', expand=True)
        search_entry.focus_set()
        
        # Suggestion listbox
        suggest_frame = tk.LabelFrame(container, text=self._t('monster_suggestions'), padx=8, pady=8)
        suggest_frame.pack(fill='both', expand=True, pady=(0,8))
        
        suggest_listbox = tk.Listbox(suggest_frame, height=10, exportselection=False)
        suggest_listbox.pack(side='left', fill='both', expand=True)
        
        suggest_scroll = tk.Scrollbar(suggest_frame, orient='vertical', command=suggest_listbox.yview)
        suggest_scroll.pack(side='right', fill='y')
        suggest_listbox.config(yscrollcommand=suggest_scroll.set)
        
        # Match info label
        match_info_var = tk.StringVar(value='')
        match_info_label = tk.Label(container, textvariable=match_info_var, fg='#2196F3', 
                                     font=('Arial', 8), wraplength=450, justify='left')
        match_info_label.pack(fill='x', pady=(0,8))
        
        # Populate initial suggestions (filtered by training mode if active)
        def update_suggestions(*args):
            """Update suggestions based on search text with fuzzy matching."""
            import re
            search_text = search_var.get().strip()
            
            suggest_listbox.delete(0, tk.END)
            match_info_var.set('')
            
            # Filter monsters based on training mode
            is_training_mode = self.training_mode_var.get() if hasattr(self, 'training_mode_var') else False
            available_monsters = self.monsters
            
            if is_training_mode:
                # Training mode: Only show training dummies
                available_monsters = [m for m in self.monsters if m.get('training_mode', False)]
                if not available_monsters:
                    match_info_var.set(f"⚠️ {self._t('no_training_dummies')}")
                    return
            
            if not search_text:
                # Show all available monsters (filtered or not)
                for monster in available_monsters:
                    suggest_listbox.insert(tk.END, monster['name'])
                if is_training_mode:
                    match_info_var.set(f"🎯 {self._t('training_dummy_filter')} | {len(available_monsters)} dummy")
                else:
                    match_info_var.set(f"💡 {self._t('monster_showing_all').format(count=len(available_monsters))}")
                return
            
            # Fuzzy search (on filtered list)
            search_clean = re.sub(r'[^a-z0-9\s]', '', search_text.lower()).strip()
            matches = []
            
            for monster in available_monsters:
                name = monster['name']
                name_clean = re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()
                
                # Score matches: exact > starts with > contains
                if search_clean == name_clean:
                    matches.append((name, 100))  # Exact match
                elif name_clean.startswith(search_clean):
                    matches.append((name, 80))   # Starts with
                elif search_clean in name_clean:
                    matches.append((name, 60))   # Contains
                elif any(word.startswith(search_clean) for word in name_clean.split()):
                    matches.append((name, 40))   # Word starts with
            
            # Sort by score (descending)
            matches.sort(key=lambda x: x[1], reverse=True)
            
            # Display matches
            for name, score in matches:
                suggest_listbox.insert(tk.END, name)
            
            # Update match info
            if matches:
                match_info_var.set(f"✓ {self._t('monster_found_matches').format(count=len(matches))} | " +
                                   self._t('monster_fuzzy_hint'))
            else:
                match_info_var.set(f"⚠ {self._t('monster_no_matches')} | " +
                                   self._t('monster_try_hint'))
        
        search_var.trace_add('write', update_suggestions)
        update_suggestions()  # Initial population
        
        # Double-click or Enter to select
        def on_select(event=None):
            selection = suggest_listbox.curselection()
            if not selection:
                return
            
            monster_name = suggest_listbox.get(selection[0])
            
            # Check if already in rotation list
            if any(m['name'] == monster_name for m in self.monster_rotation_list):
                messagebox.showinfo(self._t('info_title'), 
                                    self._t('monster_already_in_list').format(name=monster_name),
                                    parent=dialog)
                return
            
            # Add to rotation list
            new_priority = len(self.monster_rotation_list) + 1
            self.monster_rotation_list.append({
                'name': monster_name,
                'priority': new_priority,
                'enabled': True
            })
            
            self._refresh_monster_rotation_list()
            dialog.destroy()
        
        suggest_listbox.bind('<Double-Button-1>', on_select)
        search_entry.bind('<Return>', on_select)
        
        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text=self._t('add_button'), command=on_select, 
                  font=('Arial', 9, 'bold'), fg='#4CAF50').pack(side='left')
        tk.Button(btn_frame, text=self._t('cancel_button'), command=dialog.destroy).pack(side='left', padx=(8,0))

    def on_hunt_browse_template(self):
        path = filedialog.askopenfilename(title='Select template image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if path:
            self.template_var.set(path)

    def on_hunt_pick_corner(self, which: str):
        def do_pick():
            for i in range(3, 0, -1):
                self.hunt_status.set(f'Pick {which.upper()} in {i}... Move mouse to corner')
                time.sleep(1)
            try:
                pg = pyautogui
                if pg is None:
                    raise RuntimeError('pyautogui not available')
                x, y = pg.position()
                if which == 'tl':
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
                        self.reg_w.set('')
                        self.reg_h.set('')
                self.hunt_status.set(f'Picked {which.upper()} at ({x},{y})')
            except Exception as e:
                self.hunt_status.set(f'Pick error: {e!r}')

        threading.Thread(target=do_pick, daemon=True).start()

    def on_hunt_find_windows(self):
        """Find and populate window list in combobox with auto-selection."""
        # Enumerate windows using WinAPI to get hwnd and PID
        items = self._enum_windows()
        
        # Filter for Cabal windows (check saved window_title or default to 'cabal')
        saved_title = self.hunt_cfg.get('window_title', 'cabal').strip().lower()
        candidates = [w for w in items if saved_title in w['title'].lower() or 
                     'cabal' in w['title'].lower() or 
                     'cabal' in (w['proc'] or '').lower()]
        
        # Store window items
        self.win_items = candidates
        
        # Populate combobox
        self.win_combo['values'] = [
            f"{w['title']}  [PID:{w['pid']}]" for w in candidates
        ]
        
        if not candidates:
            messagebox.showinfo(self._t('find_windows'), self._t('no_windows'))
            return
        
        # Auto-select window matching saved PID if available
        saved_pid = self.hunt_cfg.get('window_pid')
        selected_idx = 0
        
        if saved_pid:
            for i, w in enumerate(candidates):
                if w['pid'] == saved_pid:
                    selected_idx = i
                    break
        
        # Select in combobox WITHOUT triggering bring-to-front
        self._skip_auto_bring = True
        self.win_combo.current(selected_idx)
        self.hunt_selected = candidates[selected_idx]
        self._skip_auto_bring = False
        
        self.hunt_status.set(self._t('selected_window').format(title=candidates[selected_idx]['title']))
    
    def on_hunt_refresh_windows(self):
        """Refresh window list manually (PATCH 9)."""
        # Clear existing selection
        self.win_items = []
        self.win_combo.set('')
        
        # Re-enumerate and populate windows
        self.on_hunt_find_windows()
        
        # Update status
        count = len(self.win_items) if hasattr(self, 'win_items') else 0
        self.hunt_status.set(f"🔄 Refreshed: {count} window(s) found")

    def on_hunt_bring_front(self):
        """Bring selected window to front."""
        # Get hwnd from hunt_selected
        hwnd = None
        if hasattr(self, 'hunt_selected') and self.hunt_selected:
            hwnd = self.hunt_selected.get('hwnd')
        
        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            # Fallback to title-based search
            title = self.hunt_cfg.get('window_title', 'Cabal').strip()
            ok = self._bring_window_to_front(title)
        
        self.hunt_status.set(self._t('bring_ok') if ok else self._t('bring_fail'))

    def on_hunt_bring_front_below_app(self):
        """Bring game window to front but keep app on top of it."""
        # Get hwnd from hunt_selected
        hwnd = None
        if hasattr(self, 'hunt_selected') and self.hunt_selected:
            hwnd = self.hunt_selected.get('hwnd')
        
        # First bring game window to front
        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            # Fallback to title-based search
            title = self.hunt_cfg.get('window_title', 'Cabal').strip()
            ok = self._bring_window_to_front(title)
        
        # Then bring app back on top
        if ok:
            time.sleep(0.1)  # Small delay to ensure game window is up
            self.lift()
            self.focus_force()
            self.attributes('-topmost', True)
            self.update()
            self.after(100, lambda: self.attributes('-topmost', False))  # Disable topmost after 100ms
        
        self.hunt_status.set(self._t('bring_ok') if ok else self._t('bring_fail'))

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
            ok = self._bring_window_to_front_by_hwnd(item['hwnd'])
            
            if ok:
                # Bring app back on top after game window
                time.sleep(0.1)
                self.lift()
                self.focus_force()
                self.attributes('-topmost', True)
                self.update()
                self.after(100, lambda: self.attributes('-topmost', False))
                
                self.hunt_status.set(self._t('selected_window').format(title=item['title']))
            else:
                self.hunt_status.set(self._t('bring_fail'))
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
                    if int(w['pid']) == int(pid):
                        return self._bring_window_to_front_by_hwnd(int(w['hwnd']))
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _enum_windows(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
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
                results.append({'hwnd': int(hwnd), 'pid': pid_val, 'title': title, 'proc': proc_name})
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
        templates = cfg.get('templates', [])
        if templates:
            window_bounds = cfg.get('window_bounds')
            for tmpl in templates:
                path = tmpl.get('path', '')
                if not path or not Path(path).exists():
                    continue
                
                threshold = tmpl.get('threshold', 0.85)
                
                # Determine region
                region_strategy = tmpl.get('region_strategy', 'window')
                if region_strategy == 'custom' and tmpl.get('region'):
                    reg_dict = tmpl['region']
                    region = (reg_dict.get('left', 0), reg_dict.get('top', 0), 
                             reg_dict.get('width', 0), reg_dict.get('height', 0))
                elif window_bounds:
                    wb = window_bounds
                    region = (wb.get('left', 0), wb.get('top', 0), 
                             wb.get('width', 0), wb.get('height', 0))
                else:
                    region = None
                
                # Use template_matcher for accurate confidence tracking
                box, confidence = locate_template(path, region, threshold, method='auto')
                if box:
                    return box, {
                        'name': tmpl.get('name', ''), 
                        'path': path, 
                        'threshold': threshold,
                        'confidence': confidence
                    }
            
            return None, None
        
        # Fallback to legacy template_path
        region_list = cfg.get('region')
        region = tuple(region_list) if region_list else None
        template = cfg.get('template_path')
        threshold = cfg.get('confidence', 0.8)
        if not template or not Path(template).exists():
            return None, None
        
        # Use template_matcher for accurate confidence tracking
        box, confidence = locate_template(template, region, threshold, method='auto')
        return (box, {'path': template, 'threshold': threshold, 'confidence': confidence}) if box else (None, None)

    def _check_first_time_setup(self):
        """Check if this is first-time user and auto-launch wizard if needed."""
        # Check if user has completed basic setup
        # Must have ALL THREE to be considered configured
        has_window = bool(self.hunt_cfg.get('window_title', '').strip())
        
        # Phase 3 compatibility: Check both legacy and new monster fields
        has_monster_legacy = bool(self.hunt_cfg.get('monster_selected_name', '').strip())
        has_monster_list = bool(self.hunt_cfg.get('monster_list')) and len(self.hunt_cfg.get('monster_list', [])) > 0
        has_monster = has_monster_legacy or has_monster_list
        
        has_skills = bool(self.hunt_cfg.get('skill_slots')) and len(self.hunt_cfg.get('skill_slots', [])) > 0
        
        is_new_user = not (has_window and has_monster and has_skills)
        
        # Debug log to understand detection
        print(f"[First-time check] window={has_window}, monster={has_monster}, skills={has_skills}, is_new={is_new_user}")
        
        if is_new_user:
            print("[First-time check] Showing messagebox to ask user...")
            
            # Force main window to front before showing messagebox
            self.lift()
            self.focus_force()
            self.attributes('-topmost', True)
            self.update()
            
            # Ask user if they want to run setup wizard
            response = messagebox.askyesno(
                self._t('wizard_first_time_title'),
                self._t('wizard_first_time_message'),
                icon='question',
                parent=self  # Ensure messagebox is child of main window
            )
            
            # Disable topmost after messagebox
            self.attributes('-topmost', False)
            
            print(f"[First-time check] User response: {response}")
            
            if response:
                # User clicked Yes - launch wizard
                print("[First-time check] Launching wizard...")
                self.on_setup_wizard()
            else:
                # User clicked No - auto-detect Cabal window and save
                print("[First-time check] User skipped wizard - attempting auto PID detection...")
                self._auto_detect_and_save_cabal_window()
                self.hunt_status.set(self._t('wizard_skipped_hint'))
        
        # Check PIL availability and show one-time warning if missing
        if not self.pil_available:
            print("[PIL Check] PIL/Pillow not available - showing install instructions")
            # Use showinfo (blue icon) instead of showerror (red icon) for less scary UX
            # Don't force window to front - let user dismiss naturally
            messagebox.showinfo(
                self._t('info_title'),
                self._t('pil_not_installed_message'),
                parent=self
            )
    
    def _auto_detect_and_save_cabal_window(self):
        """Auto-detect Cabal window PID and save to config when user skips setup."""
        print("[Auto PID] Starting Cabal window detection...")
        
        # Find all windows
        items = self._enum_windows()
        
        # Filter for Cabal windows
        cabal_windows = [w for w in items if 
                        'cabal' in w['title'].lower() or 
                        (w.get('proc') and 'cabal' in w['proc'].lower())]
        
        if not cabal_windows:
            print("[Auto PID] No Cabal windows found")
            messagebox.showwarning(
                self._t('info_title'),
                "No Cabal windows detected.\n\nPlease:\n1. Launch Cabal game first\n2. Click 'Find Windows' button to select manually",
                parent=self
            )
            return
        
        # Select first Cabal window
        selected = cabal_windows[0]
        print(f"[Auto PID] Found Cabal window: {selected['title']} [PID:{selected['pid']}]")
        
        # Update hunt_selected
        self.hunt_selected = selected
        
        # Update UI combobox
        if hasattr(self, 'win_combo'):
            self.win_combo['values'] = [f"{selected['title']}  [PID:{selected['pid']}]"]
            self.win_combo.current(0)
            self.win_items = [selected]
        
        # Save to hunt_config.json
        self.hunt_cfg['window_title'] = selected['title']
        self.hunt_cfg['window_pid'] = selected['pid']
        self.hunt_cfg['window_hwnd'] = selected['hwnd']
        
        try:
            save_hunt_config(self.hunt_cfg)
            print(f"[Auto PID] Saved to config: {selected['title']} [PID:{selected['pid']}]")
            
            # Show success message
            messagebox.showinfo(
                self._t('info_title'),
                f"✅ Auto-detected Cabal window:\n\n{selected['title']}\nPID: {selected['pid']}\n\nYou can change this anytime using 'Find Windows' button.",
                parent=self
            )
        except Exception as e:
            print(f"[Auto PID] Failed to save config: {e}")
    
    def on_setup_wizard(self):
        """Launch setup wizard to guide user through initial configuration."""
        def on_wizard_complete(wizard_data):
            """Callback when wizard completes - apply settings to UI."""
            # Show main window again
            self.deiconify()
            
            # Reload config to get wizard changes
            self.hunt_cfg = load_hunt_config()
            
            # Populate Hunt tab UI with wizard data
            self._populate_hunt_ui_from_config()
            
            # Update status message
            lang = wizard_data.get('language', 'en')
            self.hunt_status.set(f"✅ Wizard completed! Configuration loaded. Ready to hunt. (Language: {lang})")
        
        def on_wizard_cancel():
            """Callback when wizard is cancelled - restore main window."""
            self.deiconify()
        
        # Launch wizard - use 'self' instead of 'self.root' (App inherits from tk.Tk)
        # Note: Wizard will hide main window after setup to avoid transient() issues
        if callable(show_setup_wizard):
            show_setup_wizard(self, config_manager=self.config_mgr, on_complete=on_wizard_complete, on_cancel=on_wizard_cancel)
        else:
            # Fallback: wizard not available
            try:
                messagebox.showinfo(self._t('info_title'), 'Setup wizard is not available in this build.', parent=self)
            except Exception:
                pass
    
    def _populate_hunt_ui_from_config(self):
        """Populate Hunt tab UI elements from hunt_config.json data."""
        # 1. Window selection
        window_title = self.hunt_cfg.get('window_title', '').strip()
        window_pid = self.hunt_cfg.get('window_pid')
        window_hwnd = self.hunt_cfg.get('window_hwnd')
        
        if window_title:
            # If we have PID/HWND, create hunt_selected object
            if window_pid and window_hwnd:
                self.hunt_selected = {
                    'title': window_title,
                    'pid': window_pid,
                    'hwnd': window_hwnd,
                    'proc': None  # Process name not saved in config
                }
                
                # Populate combobox with saved window
                if hasattr(self, 'win_combo'):
                    self.win_combo['values'] = [f"{window_title}  [PID:{window_pid}]"]
                    self.win_combo.current(0)
                    self.win_items = [self.hunt_selected]
        
        # 2. Monster template (if exists)
        monster_name = self.hunt_cfg.get('monster_selected_name', '').strip()
        template_path = self.hunt_cfg.get('template_path', '').strip()
        
        if monster_name:
            # Update monster name display (assuming you have a monster_name variable)
            # This will be shown in UI when monster selection is implemented
            pass
        
        # 3. Skill slots
        skill_slots = self.hunt_cfg.get('skill_slots', [])
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
        window_title = self.hunt_cfg.get('window_title', '').strip()
        window_pid = self.hunt_cfg.get('window_pid')
        window_hwnd = self.hunt_cfg.get('window_hwnd')
        
        # Only auto-populate if we have all required data
        if not (window_title and window_pid and window_hwnd):
            return
        
        # Create hunt_selected object
        self.hunt_selected = {
            'title': window_title,
            'pid': window_pid,
            'hwnd': window_hwnd,
            'proc': None  # Process name not saved in config
        }
        
        # Populate combobox with saved window
        if hasattr(self, 'win_combo'):
            self.win_combo['values'] = [f"{window_title}  [PID:{window_pid}]"]
            self.win_combo.current(0)
            self.win_items = [self.hunt_selected]
        
        # Update status to inform user
        self.hunt_status.set(f"✓ Loaded saved window: {window_title} (PID: {window_pid})")
    
    def _auto_bring_to_front_on_startup(self):
        """Auto bring saved Cabal window to front BELOW app on startup."""
        try:
            # Check if we have a valid hunt_selected window
            if not hasattr(self, 'hunt_selected') or not self.hunt_selected:
                print("[Auto Bring] No saved window to bring to front")
                return
            
            hwnd = self.hunt_selected.get('hwnd')
            title = self.hunt_selected.get('title', '')
            pid = self.hunt_selected.get('pid', '')
            
            if not hwnd:
                print(f"[Auto Bring] No HWND for window: {title}")
                return
            
            print(f"[Auto Bring] Bringing window to front (below app): {title} [PID:{pid}]")
            
            # Bring window to front
            ok = self._bring_window_to_front_by_hwnd(hwnd)
            
            if ok:
                # Keep app on top of game window
                time.sleep(0.1)
                self.lift()
                self.focus_force()
                self.attributes('-topmost', True)
                self.update()
                self.after(100, lambda: self.attributes('-topmost', False))
                
                print(f"[Auto Bring] ✓ Window ready (below app): {title}")
                # Update status briefly
                if hasattr(self, 'hunt_status'):
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
            self.hunt_status.set('Saved hunt_config.json')
            self._clear_unsaved_changes()
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('invalid_hunt').format(e=e))
    
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
            if hasattr(self, 'global_hotkey_enabled_var'):
                enabled = self.global_hotkey_enabled_var.get()
                start_key = self.global_hotkey_start_var.get()
                stop_key = self.global_hotkey_stop_var.get()
                
                # Validate: start and stop keys must be different
                if start_key == stop_key:
                    messagebox.showerror(
                        self._t('error_title'),
                        "Start and Stop hotkeys must be different!" if self.lang == 'en' 
                        else "Phím tắt Start và Stop phải khác nhau!"
                    )
                    return
                
                # Update config
                cfg['global_hotkeys'] = {
                    'enabled': enabled,
                    'start_key': start_key,
                    'stop_key': stop_key
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
            self.hunt_status.set(self._t('all_saved'))
            
            # 6. Show success message
            messagebox.showinfo(
                self._t('success_title'),
                self._t('settings_applied_message')
            )
        except Exception as e:
            messagebox.showerror(
                self._t('error_title'),
                f"Failed to apply settings: {e}"
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
        if not hasattr(self, 'unsaved_indicator_label'):
            return
        
        if self.has_unsaved_changes:
            self.unsaved_indicator_label.config(
                text=f"● {self._t('unsaved_indicator')}",
                fg='#FF9800'  # Orange color
            )
        else:
            self.unsaved_indicator_label.config(
                text=f"✓ {self._t('all_saved')}",
                fg='#4CAF50'  # Green color
            )
    
    def _switch_to_tab(self, tab_index: int):
        """Switch to specified tab via keyboard shortcut."""
        try:
            if not hasattr(self, 'notebook'):
                return
            
            # Switch to tab
            self.notebook.select(tab_index)
            
            # Update status with shortcut indicator
            tab_names = ['Hunt', 'Setup', 'Stats', 'Help']
            if 0 <= tab_index < len(tab_names):
                tab_name = tab_names[tab_index]
                shortcut = f"Alt+{tab_index + 1}"
                if hasattr(self, 'hunt_status'):
                    self.hunt_status.set(f"{shortcut}: Switched to {tab_name} tab")
        except Exception as e:
            print(f"Tab switch error: {e}")

    def _register_global_hotkeys(self):
        """Register global hotkeys (Ctrl+Shift+R/E) for hunt start/stop.
        
        This is called in __init__() after config load to ensure hotkeys are
        immediately available, even when app is minimized or not focused.
        """
        print("[Hotkeys] _register_global_hotkeys() called")
        try:
            # Check if keyboard module is available
            if keyboard is None:
                print("[Hotkeys] ⚠️ keyboard module not available")
                return
            
            # Get hotkey config (defaults to Ctrl+Shift+R/E if not set)
            hotkey_cfg = self.hunt_cfg.get('global_hotkeys', {})
            if not hotkey_cfg.get('enabled', True):
                print("[Hotkeys] Global hotkeys disabled by user")
                return  # Global hotkeys disabled by user
            
            start_key = hotkey_cfg.get('start_key', 'ctrl+shift+r')
            stop_key = hotkey_cfg.get('stop_key', 'ctrl+shift+e')
            
            # Unregister old hotkeys first (in case of re-registration)
            self._unregister_global_hotkeys()
            
            # Register new hotkeys
            try:
                self._global_start_hotkey = keyboard.add_hotkey(
                    start_key,
                    self.on_hunt_start,
                    suppress=False  # Don't suppress the key event
                )
            except Exception as e:
                print(f"Failed to register start hotkey '{start_key}': {e}")
                self._global_start_hotkey = None
            
            try:
                self._global_stop_hotkey = keyboard.add_hotkey(
                    stop_key,
                    self.on_hunt_stop,
                    suppress=False
                )
            except Exception as e:
                print(f"Failed to register stop hotkey '{stop_key}': {e}")
                self._global_stop_hotkey = None
            
            # Log successful registration
            if self._global_start_hotkey or self._global_stop_hotkey:
                print(f"Global hotkeys registered: Start={start_key}, Stop={stop_key}")
        
        except Exception as e:
            print(f"Error registering global hotkeys: {e}")
    
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
        
        except Exception as e:
            print(f"Error in _unregister_global_hotkeys: {e}")

    def _hunt_from_ui(self):
        """Extract hunt configuration from UI elements.
        
        NOTE: This updates self.hunt_cfg in-place to preserve all fields (template_threshold,
        confidence, grayscale, training_mode_enabled, ui_mode, etc.) that are not managed by Hunt tab.
        """
        # Get window title from selected window or config
        title = ''
        if hasattr(self, 'hunt_selected') and self.hunt_selected:
            title = self.hunt_selected.get('title', '').strip()
        if not title:
            title = self.hunt_cfg.get('window_title', 'Cabal').strip()
        
        target_key = self.target_key_var.get().strip() or 'TAB'
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        
        # Validate numeric inputs
        try:
            press_ms = int(float(self.attack_press_var.get()))
        except ValueError:
            raise ValueError(self._t('error_invalid_number').format(field='attack_press_ms'))
        
        try:
            cycle_d = float(self.target_cycle_var.get())
            if cycle_d <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='target_cycle_delay'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='target_cycle_delay'))
        
        try:
            search_i = float(self.search_interval_var.get())
            if search_i <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='search_interval'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='search_interval'))
        
        try:
            attack_i = float(self.attack_interval_var.get())
            if attack_i <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='attack_interval'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='attack_interval'))
        
        try:
            lost_timeout = float(self.lost_timeout_var.get())
            if lost_timeout <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='lost_timeout'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='lost_timeout'))
        
        try:
            attack_min_duration = float(self.attack_duration_var.get())
            if attack_min_duration <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='attack_min_duration'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='attack_min_duration'))
        
        template = self.template_var.get().strip()
        # Region
        region = None
        if all(v.strip() != '' for v in (self.reg_l.get(), self.reg_t.get(), self.reg_w.get(), self.reg_h.get())):
            region = [int(self.reg_l.get()), int(self.reg_t.get()), int(self.reg_w.get()), int(self.reg_h.get())]
        
        # Update hunt_cfg in-place (preserves fields not managed by Hunt tab)
        self.hunt_cfg.update({
            "window_title": title or 'Cabal',
            "window_pid": int(self.hunt_selected['pid']) if self.hunt_selected else None,
            "target_key": target_key,
            "attack_keys": attack_keys or ['1','2','3'],
            "attack_press_ms": press_ms,
            "target_cycle_delay": cycle_d,
            "search_interval": search_i,
            "attack_interval": attack_i,
            "template_path": template or 'assets/images/target_frame.png',
            "region": region,
            "lost_timeout_sec": lost_timeout,
            "attack_min_duration_sec": attack_min_duration,
            "bring_to_front_each_cycle": bool(self.bring_front_var.get()),
            "window_bounds": self.current_window_bounds,
            # Phase 3: Multi-Monster Support
            "monster_list": self.monster_rotation_list,
            "current_monster_index": self.hunt_cfg.get('current_monster_index', 0),
        })
        
        # Update skill slots
        slots = self._collect_skill_slots()
        self.hunt_cfg['skill_slots'] = slots
        if slots:
            self.hunt_cfg['attack_keys'] = [slot['key'] for slot in slots if slot.get('key')]
        
        return self.hunt_cfg

    # -----------------
    # Monster library helpers
    # -----------------
    def _monster_desc_set(self, text: str):
        if self.monster_description_text:
            self.monster_description_text.delete('1.0', tk.END)
            if text:
                self.monster_description_text.insert('1.0', text)

    def _monster_desc_get(self) -> str:
        if self.monster_description_text:
            return self.monster_description_text.get('1.0', tk.END).strip()
        return ''

    def on_monster_clear_bounds(self):
        for var in self.monster_bounds_vars.values():
            var.set('')

    def _ensure_monster_template_path_trace(self):
        if self._monster_template_path_trace:
            return

        def _trace(*_ignored):
            self._monster_template_update_preview(self.monster_template_path_var.get())

        self._monster_template_path_trace = self.monster_template_path_var.trace_add('write', _trace)

    def _monster_template_update_preview(self, path):
        label = getattr(self, 'monster_template_preview_label', None)
        if not label:
            return
        path = (path or '').strip()
        if not path:
            label.configure(image='', text=self._t('skill_no_image'))
            self.monster_template_preview_image = None
            return
        if Image is None or ImageTk is None:
            label.configure(image='', text=os.path.basename(path))
            self.monster_template_preview_image = None
            return
        
        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.configure(image=photo, text='')
            self.monster_template_preview_image = photo
            return
        
        try:
            img = Image.open(path)
            img.thumbnail((200, 200))  # Increased from 96x96 to 200x200 for better visibility
            photo = ImageTk.PhotoImage(img)
            self._thumbnail_cache[path] = photo  # Cache it
            label.configure(image=photo, text='')
            self.monster_template_preview_image = photo
        except Exception as e:
            # Better error handling with specific message
            error_msg = str(e) if str(e) else self._t('skill_image_error')
            label.configure(image='', text=f"❌ {error_msg[:50]}...")
            self.monster_template_preview_image = None

    def _monster_template_clear_form(self):
        self.monster_template_name_var.set('')
        self.monster_template_path_var.set('')
        self.monster_template_threshold_var.set('0.85')
        for var in self.monster_template_region_vars.values():
            var.set('')
        self._monster_template_update_preview('')

    def _monster_template_fill_form(self, template):
        if not template:
            self._monster_template_clear_form()
            return
        self.monster_template_name_var.set(template.get('name', ''))
        self.monster_template_path_var.set(template.get('path', ''))
        threshold = template.get('threshold', '')
        if threshold == '' or threshold is None:
            self.monster_template_threshold_var.set('0.85')
        else:
            self.monster_template_threshold_var.set(self._format_number(threshold))
        region = template.get('region') if isinstance(template.get('region'), dict) else None
        for key, var in self.monster_template_region_vars.items():
            if region and key in region:
                var.set(str(region.get(key, '')))
            else:
                var.set('')
        self._monster_template_update_preview(template.get('path', ''))

    def _monster_template_read_form(self):
        name = self.monster_template_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        path = self.monster_template_path_var.get().strip()
        if not path:
            raise ValueError('path required')
        try:
            threshold_raw = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_raw or 0.85)
        except Exception as exc:
            raise ValueError(exc)
        if not math.isfinite(threshold):
            threshold = 0.85
        threshold = max(0.0, min(threshold, 1.0))
        region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
        region = None
        if any(region_input.values()):
            if not all(region_input.values()):
                raise ValueError('region requires 4 numbers')
            try:
                region_vals = {k: int(region_input[k]) for k in ('left', 'top', 'width', 'height')}
            except ValueError as exc:
                raise ValueError(f'invalid region: {exc}')
            if region_vals['width'] <= 0 or region_vals['height'] <= 0:
                raise ValueError('region width/height must be positive')
            region = region_vals
        data = {
            'name': name,
            'path': path,
            'threshold': threshold,
        }
        if region:
            data['region'] = region
        return data

    def _refresh_monster_template_list(self, select_index: Optional[int] = None):
        listbox = getattr(self, 'monster_template_listbox', None)
        if listbox is None:
            return
        listbox.delete(0, tk.END)
        for idx, tmpl in enumerate(self.monster_template_working):
            label = tmpl.get('name') or f'Template {idx + 1}'
            threshold = tmpl.get('threshold')
            if threshold is not None and threshold != '':
                try:
                    label += f" ({float(threshold):.2f})"
                except Exception:
                    pass
            listbox.insert(tk.END, label)
        if self.monster_template_working:
            idx = self.monster_template_selected_index if select_index is None else select_index
            if idx is None:
                idx = 0
            idx = int(max(0, min(int(idx), len(self.monster_template_working) - 1)))
            select_index = idx
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(select_index)
            listbox.activate(select_index)
            self.monster_template_selected_index = select_index
            self._monster_template_fill_form(self.monster_template_working[select_index])
        else:
            self.monster_template_selected_index = None
            self._monster_template_clear_form()
        if self.monster_template_working:
            first_path = self.monster_template_working[0].get('path', '')
            if first_path:
                self.monster_template_var.set(first_path)
            listbox.see(self.monster_template_selected_index)

    def on_monster_template_selected(self, _evt=None):
        listbox = getattr(self, 'monster_template_listbox', None)
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
        path = filedialog.askopenfilename(title=self._t('monster_template_browse'), filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if not path:
            return
        
        # Ask if user wants to copy to project
        copy_to_project = messagebox.askyesno(
            self._t('monster_section'),
            'Copy image to project assets folder?\n\nYes: copy to assets/images/monsters/\nNo: use original path',
            default='yes'
        )
        
        if copy_to_project:
            try:
                # Create target directory
                assets_dir = Path(__file__).parent / 'assets' / 'images' / 'monsters'
                assets_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate unique filename
                import time as time_module
                monster_name = self.monster_name_var.get().strip() or 'monster'
                # Sanitize monster name for filename
                safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in monster_name.lower())
                timestamp = int(time_module.time() * 1000)
                ext = Path(path).suffix or '.png'
                new_filename = f"{safe_name}_{timestamp}{ext}"
                target_path = assets_dir / new_filename
                
                # Copy file
                import shutil
                shutil.copy2(path, target_path)
                
                # Use relative path
                try:
                    relative_path = target_path.relative_to(Path(__file__).parent)
                    path = str(relative_path).replace('\\', '/')
                except Exception:
                    path = str(target_path)
                    
            except Exception as exc:
                messagebox.showerror(self._t('monster_section'), self._t('error_copy_image').format(exc=exc))
                return
        
        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set('template')

    def on_monster_template_capture(self):
        """Capture screenshot using shared helper and update form fields."""
        if capture_region_and_save is None:
            messagebox.showerror(self._t('monster_section'), self._t('error_missing_library').format(exc='capture_helper'))
            return
        try:
            monster_name = self.monster_name_var.get().strip() if hasattr(self, 'monster_name_var') else 'monster'
        except Exception:
            monster_name = 'monster'
        parent_win = self.winfo_toplevel()
        # Avoid Tkinter grab conflicts during overlay selection
        had_grab = False
        try:
            try:
                self.grab_release()
                had_grab = True
            except Exception:
                had_grab = False
            result = capture_region_and_save(parent_win, Image is not None, monster_name, self.lang)
        except Exception as exc:
            try:
                messagebox.showerror(self._t('error_title'), self._t('error_screenshot_failed').format(exc=exc))
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
            self.hunt_status.set(self._t('monster_template_capture_cancelled'))
            return
        path, (left, top, width, height) = result
        # Use relative path if under project dir
        try:
            base_dir = Path(__file__).parent
            rel = Path(path).resolve().relative_to(base_dir.resolve())
            path_str = str(rel).replace('\\', '/')
        except Exception:
            path_str = path
        self.monster_template_path_var.set(path_str)
        # Auto-fill name if empty
        if hasattr(self, 'monster_template_name_var') and not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path_str).stem)
            except Exception:
                self.monster_template_name_var.set('template')
        # Ensure default threshold if empty
        if hasattr(self, 'monster_template_threshold_var') and not self.monster_template_threshold_var.get().strip():
            self.monster_template_threshold_var.set('0.85')
        # Fill region if blank
        if hasattr(self, 'monster_template_region_vars') and not any(v.get().strip() for v in self.monster_template_region_vars.values()):
            self.monster_template_region_vars['left'].set(str(left))
            self.monster_template_region_vars['top'].set(str(top))
            self.monster_template_region_vars['width'].set(str(width))
            self.monster_template_region_vars['height'].set(str(height))
        # Status
        try:
            filename = os.path.basename(path_str)
            self.hunt_status.set(self._t('monster_template_capture_success').format(filename=filename))
        except Exception:
            pass

    def on_monster_template_add(self):
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError('path required')
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('monster_template_invalid').format(e=exc))
            return
        for existing in self.monster_template_working:
            if existing.get('name', '').lower() == normalized['name'].lower():
                messagebox.showerror(self._t('monster_section'), self._t('monster_template_duplicate'))
                return
        self.monster_template_working.append(normalized)
        self.monster_template_selected_index = len(self.monster_template_working) - 1
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t('monster_template_added'))

    def on_monster_template_update(self):
        if self.monster_template_selected_index is None or self.monster_template_selected_index >= len(self.monster_template_working):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_not_selected'))
            return
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError('path required')
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('monster_template_invalid').format(e=exc))
            return
        for idx, existing in enumerate(self.monster_template_working):
            if idx == self.monster_template_selected_index:
                continue
            if existing.get('name', '').lower() == normalized['name'].lower():
                messagebox.showerror(self._t('monster_section'), self._t('monster_template_duplicate'))
                return
        self.monster_template_working[self.monster_template_selected_index] = normalized
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t('monster_template_saved'))

    def on_monster_template_delete(self):
        if self.monster_template_selected_index is None or self.monster_template_selected_index >= len(self.monster_template_working):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_not_selected'))
            return
        self.monster_template_working.pop(self.monster_template_selected_index)
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self.hunt_status.set(self._t('monster_template_removed'))

    def on_monster_template_quick_add(self):
        path = filedialog.askopenfilename(title=self._t('monster_template_browse'), filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if not path:
            return
        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set('template')
        if not self.monster_template_threshold_var.get().strip():
            self.monster_template_threshold_var.set('0.85')

    def on_monster_template_preview_overlay(self):
        """Show preview window with template image, window_bounds and region overlay."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_no_image'))
            return
        
        # PIL check - should not reach here if button is disabled, but double-check
        if not self.pil_available:
            # Use showinfo instead of showerror for friendlier UX
            messagebox.showinfo(
                self._t('monster_section'), 
                self._t('pil_not_installed_message')
            )
            return

        try:
            # Load template image
            # For type checkers: ensure PIL modules are available here
            assert Image is not None and ImageDraw is not None and ImageTk is not None
            img = Image.open(template_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Draw window_bounds if available
            wb = _normalize_window_bounds({
                k: v.get().strip() for k, v in self.monster_bounds_vars.items()
            })
            if wb:
                # Draw window bounds in blue
                left, top = wb.get('left', 0), wb.get('top', 0)
                width, height = wb.get('width', 0), wb.get('height', 0)
                draw.rectangle([left, top, left + width, top + height], outline='blue', width=2)
                draw.text((left + 5, top + 5), 'Window Bounds', fill='blue')
            
            # Draw region if custom
            region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
            region = None
            if any(region_input.values()):
                region = _normalize_window_bounds(region_input)  # reuse same normalization
                if region:
                    rl, rt = region.get('left', 0), region.get('top', 0)
                    rw, rh = region.get('width', 0), region.get('height', 0)
                    draw.rectangle([rl, rt, rl + rw, rt + rh], outline='red', width=3)
                    draw.text((rl + 5, rt + 5), 'Region', fill='red')
            
            # Show in new window
            preview_win = tk.Toplevel(self)
            preview_win.title(self._t('monster_template_preview_overlay'))
            preview_win.geometry('800x600')
            
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
            
            tk.Label(preview_win, text=info_text, justify='left').pack()
            tk.Button(preview_win, text=self._t('close'), command=preview_win.destroy).pack(pady=10)
            
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('error_preview').format(exc=exc))

    def on_monster_template_test_recognition(self):
        """Test template matching on current screen."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_no_image'))
            return
        
        try:
            import pyautogui
            import time as time_module
        except ImportError as exc:
            messagebox.showerror(self._t('monster_section'), self._t('error_missing_library').format(exc=exc))
            return
        
        # Get threshold
        try:
            threshold_str = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_str) if threshold_str else 0.85
            threshold = max(0.0, min(threshold, 1.0))
        except ValueError:
            threshold = 0.85
        
        # Get region if specified
        region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
        region = None
        if all(region_input.values()):
            try:
                l = int(region_input['left'])
                t = int(region_input['top'])
                w = int(region_input['width'])
                h = int(region_input['height'])
                region = (l, t, w, h)
            except (ValueError, KeyError):
                region = None
        
        # Show status
        self.hunt_status.set(self._t('monster_template_test_running'))
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
                template_path=template_path,
                threshold=threshold,
                region=region
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
                
                message = self._t('monster_template_test_found').format(
                    x=center_x, 
                    y=center_y, 
                    conf=confidence_val
                )
                
                # Show result with visual overlay
                result_win = tk.Toplevel(self)
                result_win.title(self._t('monster_template_test_recognition'))
                result_win.geometry('400x300')
                
                tk.Label(result_win, text="✅ " + message, fg='green', font=('Arial', 10, 'bold')).pack(pady=10)
                
                details = f"Box: ({result.left}, {result.top}, {result.width}, {result.height})\n"
                details += f"Center: ({center_x}, {center_y})\n"
                details += f"Threshold: {threshold:.2f}\n"
                if region:
                    details += f"Region: {region}"
                
                tk.Label(result_win, text=details, justify='left', font=('Courier', 9)).pack(pady=10)
                
                # Try to capture and show the match
                try:
                    screenshot = pyautogui.screenshot(region=(result.left, result.top, result.width, result.height))
                    screenshot.thumbnail((200, 200))
                    
                    if ImageTk is not None:
                        photo = ImageTk.PhotoImage(screenshot)
                        img_label = tk.Label(result_win)
                        img_label.configure(image=photo)
                        self._image_refs.append(photo)
                        img_label.pack(pady=10)
                except Exception:
                    pass
                
                tk.Button(result_win, text=self._t('close'), command=result_win.destroy).pack(pady=10)
                
                self.hunt_status.set(message)
                
            else:
                # Restore window
                if self.monster_manager_win:
                    self.monster_manager_win.deiconify()
                
                message = self._t('monster_template_test_not_found').format(threshold=threshold)
                messagebox.showinfo(
                    self._t('monster_template_test_recognition'),
                    message + "\n\nTry:\n• Lower threshold\n• Adjust region\n• Ensure target is visible"
                )
                self.hunt_status.set(message)
                
        except Exception as exc:
            # Restore window
            if self.monster_manager_win:
                try:
                    self.monster_manager_win.deiconify()
                except Exception:
                    pass
            
            error_msg = self._t('monster_template_test_error').format(error=str(exc))
            messagebox.showerror(self._t('monster_section'), error_msg)
            self.hunt_status.set(error_msg)

    def _monster_clear_form(self):
        if hasattr(self, 'monster_name_var'):
            self.monster_name_var.set('')
        if hasattr(self, 'monster_hp_var'):
            self.monster_hp_var.set('')
        if hasattr(self, 'monster_damage_var'):
            self.monster_damage_var.set('')
        if hasattr(self, 'monster_template_var'):
            self.monster_template_var.set('')
        if hasattr(self, 'monster_estimate_var'):
            self.monster_estimate_var.set('')
        self._monster_desc_set('')
        for var in self.monster_bounds_vars.values():
            var.set('')
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self._monster_template_clear_form()
        self._refresh_monster_template_list()

    def _format_number(self, value):
        try:
            num = float(value)
        except (TypeError, ValueError):
            return ''
        if math.isclose(num, round(num), rel_tol=1e-9, abs_tol=1e-9):
            return str(int(round(num)))
        return f'{num:.2f}'.rstrip('0').rstrip('.')

    def _monster_fill_form(self, monster):
        if not monster:
            self._monster_clear_form()
            return
        if hasattr(self, 'monster_name_var'):
            self.monster_name_var.set(monster.get('name', ''))
        if hasattr(self, 'monster_hp_var'):
            self.monster_hp_var.set(self._format_number(monster.get('hp', '')))
        if hasattr(self, 'monster_damage_var'):
            self.monster_damage_var.set(self._format_number(monster.get('damage_per_hit', '')))
        if hasattr(self, 'monster_template_var'):
            self.monster_template_var.set(monster.get('template', ''))
        self._monster_desc_set(monster.get('description', ''))
        bounds = monster.get('window_bounds') if isinstance(monster.get('window_bounds'), dict) else None
        for key, var in self.monster_bounds_vars.items():
            if bounds and key in bounds:
                var.set(str(bounds.get(key, '')))
            else:
                var.set('')
        self.monster_template_working = copy.deepcopy(_sanitize_templates(monster.get('templates')))
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self._update_monster_estimate_label(monster)

    def _open_monster_manager(self):
        if self.monster_manager_win is not None and self.monster_manager_win.winfo_exists():
            try:
                self.monster_manager_win.deiconify()
                self.monster_manager_win.lift()
                self.monster_manager_win.focus_set()
            except Exception:
                pass
            return

        win = tk.Toplevel(self)
        win.title(self._t('monster_section'))
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

        win.protocol('WM_DELETE_WINDOW', _on_close)
        container = tk.Frame(win, padx=12, pady=12)
        container.grid(row=0, column=0, sticky='nsew')
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(container)
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_rowconfigure(1, weight=1)

        tk.Label(sidebar, text=self._t('monster_list')).grid(row=0, column=0, sticky='w')
        self.monster_listbox = tk.Listbox(sidebar, height=16, width=26, exportselection=False)
        self.monster_listbox.grid(row=1, column=0, sticky='ns')
        monster_scroll = tk.Scrollbar(sidebar, orient='vertical', command=self.monster_listbox.yview)
        monster_scroll.grid(row=1, column=1, sticky='ns')
        self.monster_listbox.config(yscrollcommand=monster_scroll.set)
        self.monster_listbox.bind('<<ListboxSelect>>', self.on_monster_selected)

        detail = tk.Frame(container)
        detail.grid(row=0, column=1, sticky='nsew', padx=(16,0))
        detail.grid_columnconfigure(1, weight=1)
        detail.grid_rowconfigure(6, weight=1)

        info_frame = tk.Frame(detail)
        info_frame.grid(row=0, column=0, sticky='we')
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)

        tk.Label(info_frame, text=self._t('monster_name')).grid(row=0, column=0, sticky='e')
        tk.Entry(info_frame, textvariable=self.monster_name_var, width=24).grid(row=0, column=1, sticky='we', padx=(4,0))
        tk.Button(info_frame, text=self._t('monster_estimate'), command=self.on_monster_estimate).grid(row=0, column=4, padx=(8,0))

        tk.Label(info_frame, text=self._t('monster_hp')).grid(row=1, column=0, sticky='e', pady=(6,0))
        tk.Entry(info_frame, textvariable=self.monster_hp_var, width=12).grid(row=1, column=1, sticky='we', padx=(4,0), pady=(6,0))

        tk.Label(info_frame, text=self._t('monster_damage')).grid(row=1, column=2, sticky='e', pady=(6,0))
        tk.Entry(info_frame, textvariable=self.monster_damage_var, width=12).grid(row=1, column=3, sticky='we', padx=(4,0), pady=(6,0))
        
        tk.Button(info_frame, text=self._t('monster_calculate_timing'), command=self.on_monster_calculate_timing).grid(row=1, column=4, padx=(8,0), pady=(6,0))

        desc_label = tk.Label(detail, text=self._t('monster_description'))
        desc_label.grid(row=1, column=0, sticky='w', pady=(8,0))
        self.monster_description_text = tk.Text(detail, width=46, height=4, wrap='word')
        self.monster_description_text.grid(row=2, column=0, sticky='we')
        tk.Label(detail, text=self._t('monster_description_hint'), fg='gray').grid(row=3, column=0, sticky='w')

        bounds_frame = tk.Frame(detail)
        bounds_frame.grid(row=4, column=0, sticky='w', pady=(8,0))
        bounds_label = tk.Label(bounds_frame, text=self._t('monster_bounds'))
        bounds_label.grid(row=0, column=0, columnspan=5, sticky='w')
        attach_i18n_tooltip(bounds_label, key='tooltip_window_bounds', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        headings = ['L', 'T', 'W', 'H']
        for idx, title in enumerate(headings):
            tk.Label(bounds_frame, text=title).grid(row=1, column=idx, padx=(0,4), sticky='w')
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['left'], width=6).grid(row=2, column=0, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['top'], width=6).grid(row=2, column=1, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['width'], width=6).grid(row=2, column=2, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['height'], width=6).grid(row=2, column=3, padx=(0,10))
        tk.Button(bounds_frame, text=self._t('monster_bounds_clear'), command=self.on_monster_clear_bounds).grid(row=2, column=4)
        tk.Label(bounds_frame, text=self._t('monster_bounds_hint'), fg='gray').grid(row=3, column=0, columnspan=5, sticky='w', pady=(4,0))

        template_frame = tk.Frame(detail)
        template_frame.grid(row=5, column=0, sticky='we', pady=(8,0))
        template_frame.grid_columnconfigure(1, weight=1)
        tk.Label(template_frame, text=self._t('monster_template')).grid(row=0, column=0, sticky='e')
        tk.Entry(template_frame, textvariable=self.monster_template_var, width=32).grid(row=0, column=1, sticky='we', padx=(4,0))
        tk.Button(template_frame, text=self._t('browse'), command=self.on_monster_browse_template).grid(row=0, column=2, padx=(6,0))
        tk.Button(template_frame, text=self._t('monster_open_templates'), command=self.on_monster_template_quick_add).grid(row=1, column=1, sticky='w', pady=(6,0))

        templates_panel = tk.LabelFrame(detail, text=self._t('monster_templates'))
        templates_panel.grid(row=6, column=0, sticky='nsew', pady=(8,0))
        templates_panel.grid_columnconfigure(2, weight=1)
        templates_panel.grid_rowconfigure(0, weight=1)

        self.monster_template_listbox = tk.Listbox(templates_panel, height=8, width=26, exportselection=False)
        self.monster_template_listbox.grid(row=0, column=0, rowspan=5, sticky='nsw')
        template_scroll = tk.Scrollbar(templates_panel, orient='vertical', command=self.monster_template_listbox.yview)
        template_scroll.grid(row=0, column=1, rowspan=5, sticky='ns')
        self.monster_template_listbox.config(yscrollcommand=template_scroll.set)
        self.monster_template_listbox.bind('<<ListboxSelect>>', self.on_monster_template_selected)

        template_form = tk.Frame(templates_panel)
        template_form.grid(row=0, column=2, sticky='nsew', padx=(12,0))
        template_form.grid_columnconfigure(1, weight=1)

        tk.Label(template_form, text=self._t('monster_template_name')).grid(row=0, column=0, sticky='e')
        tk.Entry(template_form, textvariable=self.monster_template_name_var, width=24).grid(row=0, column=1, sticky='we', padx=(4,0))

        tk.Label(template_form, text=self._t('monster_template_path')).grid(row=1, column=0, sticky='e', pady=(6,0))
        tk.Entry(template_form, textvariable=self.monster_template_path_var, width=24).grid(row=1, column=1, sticky='we', padx=(4,0), pady=(6,0))
        self._ensure_monster_template_path_trace()
        path_btn_frame = tk.Frame(template_form)
        path_btn_frame.grid(row=1, column=2, padx=(6,0), pady=(6,0))
        tk.Button(path_btn_frame, text=self._t('monster_template_browse'), command=self.on_monster_template_import).pack(side='left')
        tk.Button(path_btn_frame, text=self._t('monster_template_capture'), command=self.on_monster_template_capture).pack(side='left', padx=(4,0))

        tk.Label(template_form, text=self._t('monster_template_threshold')).grid(row=2, column=0, sticky='e')
        threshold_entry = tk.Entry(template_form, textvariable=self.monster_template_threshold_var, width=8)
        threshold_entry.grid(row=2, column=1, sticky='w', padx=(4,0))
        attach_i18n_tooltip(threshold_entry, key='tooltip_threshold', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        tk.Label(template_form, text=self._t('monster_template_threshold_hint'), fg='gray').grid(row=3, column=0, columnspan=3, sticky='w')

        region_frame = tk.Frame(template_form)
        region_frame.grid(row=4, column=0, columnspan=3, sticky='w', pady=(8,0))
        tk.Label(region_frame, text=self._t('monster_template_region')).grid(row=0, column=0, columnspan=5, sticky='w')
        headers = ['L', 'T', 'W', 'H']
        for idx, title in enumerate(headers):
            tk.Label(region_frame, text=title).grid(row=1, column=idx, padx=(0,4), sticky='w')
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['left'], width=5).grid(row=2, column=0, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['top'], width=5).grid(row=2, column=1, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['width'], width=5).grid(row=2, column=2, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['height'], width=5).grid(row=2, column=3, padx=(0,8))
        tk.Label(region_frame, text=self._t('monster_template_region_hint'), fg='gray').grid(row=3, column=0, columnspan=5, sticky='w', pady=(4,0))

        preview_frame = tk.Frame(template_form)
        preview_frame.grid(row=5, column=0, columnspan=3, sticky='w', pady=(8,0))
        # Increased preview size from 16x6 to 30x12 to accommodate 200x200 thumbnails
        self.monster_template_preview_label = tk.Label(preview_frame, text=self._t('skill_no_image'), 
                                                        width=30, height=12, relief='groove', bg='#f0f0f0')
        self.monster_template_preview_label.pack(side='left')
        
        preview_btn_frame = tk.Frame(preview_frame)
        preview_btn_frame.pack(side='left', padx=(8,0))
        
        # Preview overlay button - disable if PIL not available
        self.monster_preview_overlay_btn = tk.Button(
            preview_btn_frame, 
            text=self._t('monster_template_preview_overlay'), 
            command=self.on_monster_template_preview_overlay
        )
        self.monster_preview_overlay_btn.pack(side='top', anchor='w')
        
        if not self.pil_available:
            self.monster_preview_overlay_btn.config(state='disabled')
            # Add tooltip explaining why disabled
            self._create_tooltip(self.monster_preview_overlay_btn, self._t('pil_required_tooltip'))
        
        tk.Button(preview_btn_frame, text=self._t('monster_template_test_recognition'), command=self.on_monster_template_test_recognition).pack(side='top', anchor='w', pady=(4,0))

        tmpl_btn_frame = tk.Frame(template_form)
        tmpl_btn_frame.grid(row=6, column=0, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_add'), command=self.on_monster_template_add).pack(side='left')
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_update'), command=self.on_monster_template_update).pack(side='left', padx=(6,0))
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_delete'), command=self.on_monster_template_delete).pack(side='left', padx=(6,0))

        tk.Label(detail, textvariable=self.monster_estimate_var, fg='gray', wraplength=360, justify='left').grid(row=7, column=0, sticky='we', pady=(8,0))

        btn_frame = tk.Frame(detail)
        btn_frame.grid(row=8, column=0, sticky='w', pady=(12,0))
        tk.Button(btn_frame, text=self._t('monster_new'), command=self.on_monster_new).pack(side='left')
        tk.Button(btn_frame, text=self._t('monster_save'), command=self.on_monster_save).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_delete'), command=self.on_monster_delete).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_use_template'), command=self.on_monster_use_for_hunt).pack(side='left', padx=(12,0))

        self._refresh_monster_list(select_name=self.monster_selected_name)

    def _refresh_monster_select_options(self, select_name: Optional[str] = None):
        if select_name is not None:
            self.monster_selected_name = select_name
        names = [monster['name'] for monster in self.monsters]
        combo = getattr(self, 'monster_select_combo', None)
        if combo is not None:
            combo['values'] = names
            target_name = self.monster_selected_name or (select_name if select_name in names else None)
            current = self.monster_select_var.get() if hasattr(self, 'monster_select_var') else ''
            if target_name and target_name in names:
                self.monster_select_var.set(target_name)
            elif current not in names:
                self.monster_select_var.set(names[0] if names else '')
        self.on_monster_select_change()

    def _refresh_monster_list(self, select_name=None):
        if select_name is not None:
            self.monster_selected_name = select_name
        listbox = getattr(self, 'monster_listbox', None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for monster in self.monsters:
                listbox.insert(tk.END, monster['name'])
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster['name'] == self.monster_selected_name:
                        idx = i
                        break
            if idx is None and self.monsters and self.monster_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.monsters):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.monster_selected_index = idx
                self.monster_selected_name = self.monsters[idx]['name']
                self._monster_fill_form(self.monsters[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.monster_selected_index = None
                self._monster_clear_form()
        else:
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster['name'] == self.monster_selected_name:
                        idx = i
                        break
            self.monster_selected_index = idx if idx is not None else None
        self._refresh_monster_select_options(self.monster_selected_name)

    def on_monster_select_change(self, _evt=None):
        """Auto-apply monster config when selected from Hunt tab dropdown."""
        if not hasattr(self, 'monster_select_var'):
            return
        name = self.monster_select_var.get().strip()
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster['name'] == name:
                idx = i
                break
        self.monster_selected_index = idx if idx is not None else None
        self.monster_selected_name = name if idx is not None else None
        
        if idx is not None:
            monster = self.monsters[idx]
            self._update_monster_estimate_label(monster)
            # Auto-apply monster config (templates, window_bounds, timing recommendations)
            self._apply_monster_to_hunt_quick(monster)
        elif hasattr(self, 'monster_estimate_var'):
            self.monster_estimate_var.set('')

    def _apply_monster_to_hunt_quick(self, monster):
        """Apply monster templates and recommended settings to hunt config without opening manager."""
        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get('window_bounds'))
        self.current_window_bounds = bounds
        self.hunt_cfg['window_bounds'] = bounds
        self._update_window_bounds_display()
        
        # Apply templates[] array
        templates = _sanitize_templates(monster.get('templates'))
        if templates:
            self.hunt_cfg['templates'] = templates
            # Set legacy template_path to first template
            try:
                first_path = templates[0].get('path')
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg['template_path'] = first_path
            except Exception:
                pass
        elif monster.get('template'):
            # Fallback to old single template field
            self.template_var.set(monster['template'])
            self.hunt_cfg['template_path'] = monster['template']
            self.hunt_cfg['templates'] = []
        
        # Apply recommended timing (if monster has HP/damage stats)
        try:
            stats = self._calculate_monster_estimate(monster)
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            self.attack_duration_var.set(f'{attack_min:.2f}')
            self.lost_timeout_var.set(f'{lost_timeout:.2f}')
        except Exception:
            pass  # Monster may not have complete stats, skip recommendations
        
        # Show brief notification
        if hasattr(self, 'hunt_status'):
            template_count = len(templates) if templates else (1 if monster.get('template') else 0)
            msg = self._t('hunt_monster_auto_applied').format(name=monster.get('name', ''))
            if template_count > 0:
                msg += f" ({template_count} template{'s' if template_count > 1 else ''})"
            self.hunt_status.set(msg)

    def on_monster_apply_from_select(self):
        if not hasattr(self, 'monster_select_var'):
            return
        name = self.monster_select_var.get().strip()
        if not name:
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster['name'] == name:
                idx = i
                break
        if idx is None:
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        self.monster_selected_index = idx
        self.monster_selected_name = name
        self._update_monster_estimate_label(self.monsters[idx])
        self.on_monster_use_for_hunt()

    def _read_monster_form(self):
        if not hasattr(self, 'monster_name_var'):
            raise ValueError('UI not ready')
        name = self.monster_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        try:
            hp = float(self.monster_hp_var.get())
            dmg = float(self.monster_damage_var.get())
        except Exception as exc:
            raise ValueError(exc)
        if hp <= 0 or dmg <= 0:
            raise ValueError('values must be positive')
        template = self.monster_template_var.get().strip() if hasattr(self, 'monster_template_var') else ''
        description = self._monster_desc_get()
        bounds_input = {k: v.get().strip() for k, v in self.monster_bounds_vars.items()}
        window_bounds = None
        if any(bounds_input.values()):
            if not all(bounds_input.values()):
                raise ValueError('window bounds require left/top/width/height')
            try:
                left = int(bounds_input['left'])
                top = int(bounds_input['top'])
                width = int(bounds_input['width'])
                height = int(bounds_input['height'])
            except ValueError as exc:
                raise ValueError(f'invalid window bounds: {exc}')
            if width <= 0 or height <= 0:
                raise ValueError('window bounds width/height must be positive')
            window_bounds = {'left': left, 'top': top, 'width': width, 'height': height}
        templates = copy.deepcopy(_sanitize_templates(self.monster_template_working))
        return {
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
            'description': description,
            'window_bounds': window_bounds,
            'templates': templates,
        }

    def _current_attack_settings(self):
        try:
            press_ms = max(int(float(self.attack_press_var.get() or 0)), 1)
            attack_interval = max(float(self.attack_interval_var.get() or 0), 0.0)
        except Exception as exc:
            raise ValueError(exc)
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        if not attack_keys:
            attack_keys = ['1']
        return press_ms, attack_interval, attack_keys

    def _calculate_monster_estimate(self, monster):
        hp = float(monster.get('hp', 0))
        dmg = float(monster.get('damage_per_hit', 0))
        if hp <= 0 or dmg <= 0:
            raise ValueError('hp/damage must be positive')
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
            'kill_time': kill_time,
            'dps': dps,
            'hits': hits_needed,
            'per_hit_time': per_hit_time,
            'key_count': key_count,
        }

    def _recommend_attack_settings(self, stats):
        per_hit_time = stats['per_hit_time']
        kill_time = stats['kill_time']
        attack_padding = max(per_hit_time, 0.3)
        attack_min = kill_time + attack_padding
        lost_timeout = min(max(per_hit_time * 3.0, 0.6), attack_min)
        return attack_min, lost_timeout

    def _update_monster_estimate_label(self, monster=None, stats=None):
        if not hasattr(self, 'monster_estimate_var'):
            return
        try:
            if monster is None and self.monster_selected_index is not None and self.monster_selected_index < len(self.monsters):
                monster = self.monsters[self.monster_selected_index]
            if monster is None:
                raise ValueError('no monster')
            if stats is None:
                stats = self._calculate_monster_estimate(monster)
            base = self._t('monster_estimate_result').format(time=stats['kill_time'], dps=stats['dps'])
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            text = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        except Exception:
            text = ''
        self.monster_estimate_var.set(text)

    def on_monster_browse_template(self):
        path = filedialog.askopenfilename(title='Select template image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
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
            self.monster_selected_name = monster['name']
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
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return

        idx = self.monster_selected_index
        if idx is None:
            existing = next((i for i, m in enumerate(self.monsters) if m['name'].lower() == monster['name'].lower()), None)
            if existing is not None:
                idx = existing
                self.monsters[idx] = monster
            else:
                self.monsters.append(monster)
                idx = len(self.monsters) - 1
        else:
            for i, data in enumerate(self.monsters):
                if i != idx and data['name'].lower() == monster['name'].lower():
                    messagebox.showerror(self._t('monster_section'), self._t('monster_duplicate'))
                    return
            self.monsters[idx] = monster

        save_monster_library(self.monsters)
        self.monster_selected_index = idx
        self.monster_selected_name = monster['name']
        self._refresh_monster_list(select_name=monster['name'])
        self.hunt_status.set(self._t('monster_saved'))

    def on_monster_delete(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(self.monsters):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        self.monsters.pop(self.monster_selected_index)
        save_monster_library(self.monsters)
        if self.monsters:
            next_name = self.monsters[min(self.monster_selected_index, len(self.monsters) - 1)]['name']
        else:
            next_name = None
        self.monster_selected_index = None
        self.monster_selected_name = next_name
        self._refresh_monster_list(select_name=next_name)
        self.hunt_status.set(self._t('monster_deleted'))

    def on_monster_calculate_timing(self):
        """Calculate and display timing recommendations based on monster HP and damage."""
        try:
            # Get HP and damage from form
            hp_str = self.monster_hp_var.get().strip()
            damage_str = self.monster_damage_var.get().strip()
            
            if not hp_str or not damage_str:
                messagebox.showinfo(
                    self._t('monster_timing_title'),
                    self._t('monster_timing_no_stats')
                )
                return
            
            hp = float(hp_str)
            damage = float(damage_str)
            
            if hp <= 0 or damage <= 0:
                messagebox.showerror(
                    self._t('monster_timing_title'),
                    'HP and Damage must be greater than 0.'
                )
                return
            
            # Create dialog for attack speed selection
            dialog = tk.Toplevel(self)
            dialog.title(self._t('monster_timing_title'))
            dialog.geometry('550x550')
            dialog.transient(self)
            dialog.grab_set()
            
            # Keep dialog on top but below main app
            dialog.attributes('-topmost', False)
            self.lift()  # Keep main app on top
            
            # Attack speed selection
            speed_frame = tk.LabelFrame(dialog, text='Attack Speed Source', padx=10, pady=10)
            speed_frame.pack(fill='x', padx=10, pady=10)
            
            speed_var = tk.StringVar(value='from_skills')
            presets = get_timing_presets()
            
            # NEW: From Skills option (Recommended) - with visual indicator
            from_skills_frame = tk.Frame(speed_frame, bg='#E3F2FD', relief='solid', borderwidth=1)
            from_skills_frame.pack(fill='x', pady=2, padx=2)
            
            from_skills_rb = tk.Radiobutton(
                from_skills_frame,
                text='✓ From Skills (Recommended)',
                variable=speed_var,
                value='from_skills',
                font=('Arial', 9, 'bold'),
                bg='#E3F2FD',
                activebackground='#BBDEFB',
                selectcolor='#2196F3',
                indicatoron=True,
                command=lambda: None  # Will set after defining update_recommendations
            )
            from_skills_rb.pack(anchor='w', padx=5, pady=5)
            
            # Skill info label (will update dynamically)
            skill_info_label = tk.Label(
                from_skills_frame, 
                text='', 
                fg='#1976D2', 
                font=('Arial', 8),
                bg='#E3F2FD',
                justify='left'
            )
            skill_info_label.pack(anchor='w', padx=(25, 5), pady=(0, 5))
            
            # Calculate from CONFIGURED skills (from hunt_config skill_slots)
            configured_skills = self.hunt_cfg.get('skill_slots', [])
            skills_data = load_skill_library()
            skill_dict = {s['name']: s for s in skills_data}
            
            # Filter to get only ATTACK skills from configured skills
            attack_skill_names = []
            buff_skill_names = []
            for skill_slot in configured_skills:
                # Extract skill name from dict (skill_slots stores full skill objects)
                if isinstance(skill_slot, dict):
                    skill_name = skill_slot.get('name', '')
                    skill_type = skill_slot.get('type', 'attack').lower()
                else:
                    # Fallback: if it's already a string
                    skill_name = skill_slot
                    # Look up type from library
                    if skill_name in skill_dict:
                        skill_type = skill_dict[skill_name].get('type', 'attack').lower()
                    else:
                        skill_type = 'attack'
                
                if skill_type == 'attack':
                    attack_skill_names.append(skill_name)
                else:
                    buff_skill_names.append(skill_name)
            
            if attack_skill_names:
                aps, avg_cd, count = calculate_attack_speed_from_skills(attack_skill_names)
                if aps is not None:
                    skill_details = (
                        f"✓ {count} attack skill(s) | Avg CD: {avg_cd:.2f}s | APS: {aps:.2f} hits/sec"
                        if self.lang == 'en' else
                        f"✓ {count} kỹ năng tấn công | CD TB: {avg_cd:.2f}s | TĐ: {aps:.2f} đòn/giây"
                    )
                    if buff_skill_names:
                        buff_count = len(buff_skill_names)
                        skill_details += (
                            f"\n  ({buff_count} buff skill(s) excluded from calculation)"
                            if self.lang == 'en' else
                            f"\n  ({buff_count} kỹ năng buff không tính vào)"
                        )
                    skill_info_label.config(text=skill_details)
                else:
                    skill_info_label.config(
                        text=(
                            "⚠ No valid attack skills found"
                            if self.lang == 'en' else
                            "⚠ Không tìm thấy kỹ năng tấn công hợp lệ"
                        )
                    )
            else:
                no_skills_msg = (
                    "⚠ No attack skills configured\n  Please add skills in Hunt tab first"
                    if self.lang == 'en' else
                    "⚠ Chưa thiết lập kỹ năng tấn công\n  Vui lòng thêm kỹ năng ở tab Hunt trước"
                )
                skill_info_label.config(text=no_skills_msg)
            
            # Separator
            ttk.Separator(speed_frame, orient='horizontal').pack(fill='x', pady=(8,8))
            
            # Manual presets header
            preset_label = tk.Label(
                speed_frame,
                text=self._t('timing_manual_presets'),
                font=('Arial', 9),
                fg='#666'
            )
            preset_label.pack(anchor='w', pady=(0,4))
            
            for preset_name, (aps, desc) in presets.items():
                rb = tk.Radiobutton(
                    speed_frame,
                    text=f"  {preset_name.replace('_', ' ').title()}: {desc}",
                    variable=speed_var,
                    value=preset_name,
                    command=lambda: update_recommendations()
                )
                rb.pack(anchor='w', pady=2)
            
            # Custom speed
            custom_frame = tk.Frame(speed_frame)
            custom_frame.pack(fill='x', pady=(10,0))
            tk.Radiobutton(
                custom_frame,
                text=self._t('custom_label'),
                variable=speed_var,
                value='custom',
                command=lambda: update_recommendations()
            ).pack(side='left')
            custom_speed_var = tk.StringVar(value='2.0')
            custom_entry = tk.Entry(custom_frame, textvariable=custom_speed_var, width=8)
            custom_entry.pack(side='left', padx=5)
            custom_entry.bind('<KeyRelease>', lambda e: update_recommendations() if speed_var.get() == 'custom' else None)
            tk.Label(custom_frame, text=self._t('attacks_per_sec')).pack(side='left')
            
            # Result text
            result_frame = tk.LabelFrame(dialog, text=self._t('timing_results_title'), padx=10, pady=10)
            result_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            result_text = tk.Text(result_frame, width=65, height=15, wrap='word', font=('Consolas', 9))
            result_text.pack(fill='both', expand=True)
            
            # Store current recommendation for Apply button
            current_rec: Dict[str, Any] = {'rec': None}
            
            def update_recommendations():
                """Calculate and display recommendations."""
                try:
                    preset = speed_var.get()
                    
                    # Debug: Log preset value and type
                    print(f"DEBUG: preset = {preset!r}, type = {type(preset)}")
                    
                    # NEW: Handle "from_skills" option
                    if preset == 'from_skills':
                        # Get configured skills from hunt_config
                        configured_skills = self.hunt_cfg.get('skill_slots', [])
                        skills_data = load_skill_library()
                        skill_dict = {s['name']: s for s in skills_data}
                        
                        # Separate attack and buff skills
                        attack_skill_names = []
                        buff_skill_names = []
                        for skill_slot in configured_skills:
                            # Extract skill name from dict (skill_slots stores full skill objects)
                            if isinstance(skill_slot, dict):
                                skill_name = skill_slot.get('name', '')
                                skill_type = skill_slot.get('type', 'attack').lower()
                            else:
                                # Fallback: if it's already a string
                                skill_name = skill_slot
                                # Look up type from library
                                if skill_name in skill_dict:
                                    skill_type = skill_dict[skill_name].get('type', 'attack').lower()
                                else:
                                    skill_type = 'attack'
                            
                            if skill_type == 'attack':
                                attack_skill_names.append(skill_name)
                            else:
                                buff_skill_names.append(skill_name)
                        
                        aps, avg_cd, count = calculate_attack_speed_from_skills(attack_skill_names)
                        
                        if aps is None or count == 0:
                            result_text.delete('1.0', tk.END)
                            error_msg = self._t('timing_no_attack_skills_configured')
                            result_text.insert('1.0', error_msg)
                            current_rec['rec'] = None
                            return
                        
                        # Show detailed skill-based info with breakdown
                        skill_info = self._t('timing_from_skills_title')
                        skill_info += self._t('timing_attack_skills_list').format(count=count, names=', '.join(attack_skill_names))
                        if buff_skill_names:
                            skill_info += self._t('timing_buff_skills_list').format(count=len(buff_skill_names), names=', '.join(buff_skill_names))
                        skill_info += "\n"
                        skill_info += self._t('timing_attack_calc_header')
                        skill_info += self._t('timing_avg_cooldown').format(avg=avg_cd)
                        skill_info += self._t('timing_effective_aps').format(aps=aps)
                        skill_info += "\n"
                        
                    elif preset == 'custom':
                        aps = float(custom_speed_var.get())
                        skill_info = ''
                    else:
                        # Debug: Check presets dict
                        print(f"DEBUG: presets keys = {list(presets.keys())}")
                        print(f"DEBUG: Looking for preset '{preset}' in presets")
                        if preset not in presets:
                            raise ValueError(f"Invalid preset: {preset!r}")
                        aps = presets[preset][0]
                        skill_info = ''
                    
                    # Calculate timing
                    rec = calculate_timing(hp, damage, aps)
                    current_rec['rec'] = rec  # Store for Apply button
                    formatted = format_timing_recommendation(rec, self.lang)
                    
                    # Display results
                    result_text.delete('1.0', tk.END)
                    if skill_info:
                        result_text.insert('1.0', skill_info)
                    result_text.insert(tk.END, f"{rec}\n\n")
                    result_text.insert(tk.END, "=" * 60 + "\n")
                    result_text.insert(tk.END, formatted['summary'])
                    
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"ERROR in update_recommendations:\n{error_trace}")
                    result_text.delete('1.0', tk.END)
                    result_text.insert('1.0', f'Error: {e}\n\nFull traceback:\n{error_trace}')
                    current_rec['rec'] = None
            
            def apply_to_hunt_config():
                """Apply current recommendations to hunt_config.json."""
                if current_rec['rec'] is None:
                    messagebox.showwarning(
                        self._t('monster_timing_title'),
                        self._t('timing_calculate_first')
                    )
                    return
                
                try:
                    rec = current_rec['rec']
                    
                    # Update hunt config
                    self.hunt_cfg['lost_timeout_sec'] = rec.lost_timeout_sec
                    self.hunt_cfg['attack_min_duration_sec'] = rec.attack_min_duration_sec
                    
                    # Update UI
                    self.lost_timeout_var.set(f'{rec.lost_timeout_sec:.2f}')
                    self.attack_duration_var.set(f'{rec.attack_min_duration_sec:.2f}')
                    
                    # Save to file
                    save_hunt_config(self.hunt_cfg)
                    
                    # Show success message
                    msg = self._t('timing_applied_message').format(
                        lost=rec.lost_timeout_sec,
                        attack=rec.attack_min_duration_sec
                    )
                    
                    messagebox.showinfo(
                        self._t('monster_timing_title'),
                        msg
                    )
                    
                    self.hunt_status.set(
                        f'Timing applied: lost={rec.lost_timeout_sec:.2f}s, attack={rec.attack_min_duration_sec:.2f}s'
                    )
                    
                except Exception as e:
                    messagebox.showerror(
                        self._t('error_title'),
                        f'Failed to apply: {e}'
                    )
            
            # Buttons
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(fill='x', padx=10, pady=(0,10))
            
            from lib.ui.button_styles import get_button_config
            tk.Button(btn_frame, text=self._t('btn_calculate'), command=update_recommendations, **get_button_config('blue')).pack(side='left', padx=5)
            
            tk.Button(btn_frame, text=self._t('btn_apply_to_hunt_config'), command=apply_to_hunt_config, **get_button_config('green')).pack(side='left', padx=5)
            
            tk.Button(btn_frame, text=self._t('close'), command=dialog.destroy).pack(side='left', padx=5)
            
            # Set callback for from_skills radio button (now that update_recommendations is defined)
            from_skills_rb.config(command=update_recommendations)
            
            # Initial calculation
            update_recommendations()
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in on_monster_calculate_timing:\n{error_trace}")
            messagebox.showerror(self._t('monster_timing_title'), f'Error: {e}\n\nCheck terminal for details.')

    def on_monster_estimate(self):
        try:
            monster = self._read_monster_form()
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return
        self._update_monster_estimate_label(monster, stats)
        base = self._t('monster_estimate_result').format(time=stats['kill_time'], dps=stats['dps'])
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        detail = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        self.hunt_status.set(detail)

    def on_monster_use_for_hunt(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(self.monsters):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        monster = self.monsters[self.monster_selected_index]
        
        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get('window_bounds'))
        self.current_window_bounds = bounds
        self.hunt_cfg['window_bounds'] = bounds
        self._update_window_bounds_display()
        
        # Apply templates[] array to config
        templates = _sanitize_templates(monster.get('templates'))
        if templates:
            self.hunt_cfg['templates'] = templates
            # Also set legacy template_path to first template for backward compat
            try:
                first_path = templates[0].get('path')
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg['template_path'] = first_path
            except Exception:
                pass
        elif monster.get('template'):
            # Fallback to old single template field
            self.template_var.set(monster['template'])
            self.hunt_cfg['template_path'] = monster['template']
            self.hunt_cfg['templates'] = []
        
        try:
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return
        kill_time = stats['kill_time']
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        self.attack_duration_var.set(f'{attack_min:.2f}')
        self.lost_timeout_var.set(f'{lost_timeout:.2f}')
        base = self._t('monster_estimate_result').format(time=kill_time, dps=stats['dps'])
        detail = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        self.monster_estimate_var.set(detail)
        self.hunt_status.set(self._t('monster_applied'))

    # -----------------
    # Skill library helpers
    # -----------------
    def _skill_type_label(self, code: str) -> str:
        return self._t('skill_type_buff') if code == 'buff' else self._t('skill_type_attack')

    def _skill_type_from_label(self, label: str) -> str:
        label = label.strip().lower()
        if label in (self._t('skill_type_buff').lower(), 'buff'):
            return 'buff'
        return 'attack'

    def _ensure_skill_image_trace(self):
        if self._skill_image_trace:
            return

        def _trace(*_ignored):
            self._update_skill_preview(self.skill_image_var.get())

        self._skill_image_trace = self.skill_image_var.trace_add('write', _trace)
        # Sync immediately for current value
        self._update_skill_preview(self.skill_image_var.get())

    def _skill_clear_form(self):
        if hasattr(self, 'skill_name_var'):
            self.skill_name_var.set('')
        if hasattr(self, 'skill_key_var'):
            self.skill_key_var.set('')
        if hasattr(self, 'skill_type_var'):
            self.skill_type_var.set(self._t('skill_type_attack'))
        if hasattr(self, 'skill_cooldown_var'):
            self.skill_cooldown_var.set('')
        if hasattr(self, 'skill_cast_time_var'):
            self.skill_cast_time_var.set('')
        if hasattr(self, 'skill_duration_var'):
            self.skill_duration_var.set('')
        if hasattr(self, 'skill_pre_refresh_var'):
            self.skill_pre_refresh_var.set('')
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set('')
        self._update_skill_preview('')
        self._toggle_buff_fields()

    def _skill_fill_form(self, skill):
        if not skill:
            self._skill_clear_form()
            return
        if hasattr(self, 'skill_name_var'):
            self.skill_name_var.set(skill.get('name', ''))
        if hasattr(self, 'skill_key_var'):
            self.skill_key_var.set(skill.get('key', ''))
        if hasattr(self, 'skill_type_var'):
            self.skill_type_var.set(self._skill_type_label(skill.get('type', 'attack')))
        if hasattr(self, 'skill_cooldown_var'):
            self.skill_cooldown_var.set(self._format_number(skill.get('cooldown', '')))
        if hasattr(self, 'skill_cast_time_var'):
            self.skill_cast_time_var.set(self._format_number(skill.get('cast_time', '')))
        if hasattr(self, 'skill_duration_var'):
            self.skill_duration_var.set(self._format_number(skill.get('duration_sec', '')))
        if hasattr(self, 'skill_pre_refresh_var'):
            self.skill_pre_refresh_var.set(self._format_number(skill.get('pre_refresh_sec', '')))
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set(skill.get('image', ''))
        self._update_skill_preview(skill.get('image', ''))
        self._toggle_buff_fields()

    def _refresh_skill_list(self, select_name=None):
        if select_name is not None:
            self.skill_selected_name = select_name
        listbox = getattr(self, 'skill_listbox', None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for skill in self.skills:
                listbox.insert(tk.END, skill['name'])
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill['name'] == self.skill_selected_name:
                        idx = i
                        break
            if idx is None and self.skills and self.skill_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.skills):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.skill_selected_index = idx
                self.skill_selected_name = self.skills[idx]['name']
                self._skill_fill_form(self.skills[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.skill_selected_index = None
                self._skill_clear_form()
        else:
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill['name'] == self.skill_selected_name:
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
        win.title(self._t('skill_section'))
        win.resizable(False, False)
        self.skill_manager_win = win

        def _on_close():
            if self.skill_manager_win is win:
                self.skill_manager_win = None
            self.skill_listbox = None
            self.skill_preview_label = None
            win.destroy()

        win.protocol('WM_DELETE_WINDOW', _on_close)
        container = tk.Frame(win, padx=10, pady=10)
        container.grid(row=0, column=0, sticky='nsew')
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(4, weight=1)
        container.grid_rowconfigure(1, weight=1)

        tk.Label(container, text=self._t('skill_list')).grid(row=0, column=0, sticky='w')
        self.skill_listbox = tk.Listbox(container, height=10, exportselection=False)
        self.skill_listbox.grid(row=1, column=0, rowspan=6, sticky='nswe', padx=(0,4))
        skill_scroll = tk.Scrollbar(container, orient='vertical', command=self.skill_listbox.yview)
        skill_scroll.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.skill_listbox.config(yscrollcommand=skill_scroll.set)
        self.skill_listbox.bind('<<ListboxSelect>>', self.on_skill_selected)

        tk.Label(container, text=self._t('skill_name')).grid(row=0, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_name_var, width=24).grid(row=0, column=3, sticky='we', padx=(4,0))

        tk.Label(container, text=self._t('skill_key')).grid(row=1, column=2, sticky='e', pady=(2,0))
        tk.Entry(container, textvariable=self.skill_key_var, width=12).grid(row=1, column=3, sticky='w', padx=(4,0), pady=(2,0))

        tk.Label(container, text=self._t('skill_type')).grid(row=2, column=2, sticky='e')
        self.skill_type_combo = ttk.Combobox(container, textvariable=self.skill_type_var, state='readonly', width=14)
        self.skill_type_combo['values'] = (self._t('skill_type_attack'), self._t('skill_type_buff'))
        self.skill_type_combo.grid(row=2, column=3, sticky='w', padx=(4,0))
        self.skill_type_combo.bind('<<ComboboxSelected>>', self._on_skill_type_changed)
        current_type = self._skill_type_from_label(self.skill_type_var.get() or self._t('skill_type_attack'))
        self.skill_type_var.set(self._skill_type_label(current_type))

        tk.Label(container, text=self._t('skill_cooldown')).grid(row=3, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_cooldown_var, width=12).grid(row=3, column=3, sticky='w', padx=(4,0))

        tk.Label(container, text=self._t('skill_cast_time')).grid(row=4, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_cast_time_var, width=12).grid(row=4, column=3, sticky='w', padx=(4,0))

        # Buff-specific fields (will be shown/hidden based on skill type)
        self.skill_duration_label = tk.Label(container, text=self._t('skill_duration'))
        self.skill_duration_entry = tk.Entry(container, textvariable=self.skill_duration_var, width=12)
        attach_i18n_tooltip(self.skill_duration_entry, key='skill_duration_hint', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
        
        self.skill_pre_refresh_label = tk.Label(container, text=self._t('skill_pre_refresh'))
        self.skill_pre_refresh_entry = tk.Entry(container, textvariable=self.skill_pre_refresh_var, width=12)
        attach_i18n_tooltip(self.skill_pre_refresh_entry, key='skill_pre_refresh_hint', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)

        tk.Label(container, text=self._t('skill_image')).grid(row=7, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_image_var, width=24).grid(row=7, column=3, sticky='we', padx=(4,0))
        tk.Button(container, text=self._t('browse'), command=self.on_skill_browse_image).grid(row=7, column=4, padx=(8,0))

        # Increased preview size from 16x6 to 30x12 to accommodate 200x200 thumbnails
        self.skill_preview_label = tk.Label(container, text=self._t('skill_no_image'), 
                                            width=30, height=12, relief='groove', bg='#f0f0f0')
        self.skill_preview_label.grid(row=1, column=4, rowspan=6, sticky='nswe', padx=(8,0))
        self._ensure_skill_image_trace()

        btn_frame = tk.Frame(container)
        btn_frame.grid(row=8, column=2, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(btn_frame, text=self._t('skill_new'), command=self.on_skill_new).pack(side='left')
        tk.Button(btn_frame, text=self._t('skill_save'), command=self.on_skill_save).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('skill_delete'), command=self.on_skill_delete).pack(side='left', padx=(6,0))

        self._refresh_skill_list(select_name=self.skill_selected_name)
        
        # Initialize buff fields visibility
        self._toggle_buff_fields()

    def _on_skill_type_changed(self, event=None):
        """Handle skill type change to show/hide buff-specific fields."""
        self._toggle_buff_fields()
    
    def _toggle_buff_fields(self):
        """Show/hide buff duration fields based on skill type."""
        if not hasattr(self, 'skill_duration_label'):
            return
        
        skill_type = self._skill_type_from_label(self.skill_type_var.get())
        is_buff = (skill_type == 'buff')
        
        if is_buff:
            # Show buff fields
            self.skill_duration_label.grid(row=5, column=2, sticky='e')
            self.skill_duration_entry.grid(row=5, column=3, sticky='w', padx=(4,0))
            self.skill_pre_refresh_label.grid(row=6, column=2, sticky='e')
            self.skill_pre_refresh_entry.grid(row=6, column=3, sticky='w', padx=(4,0))
        else:
            # Hide buff fields
            self.skill_duration_label.grid_forget()
            self.skill_duration_entry.grid_forget()
            self.skill_pre_refresh_label.grid_forget()
            self.skill_pre_refresh_entry.grid_forget()

    def _refresh_skill_slots_options(self):
        if not hasattr(self, 'skill_slot_boxes'):
            return
        names = []
        for skill in self.skills:
            if skill['name'] not in names:
                names.append(skill['name'])
        for saved in getattr(self, 'skill_slot_saved_names', []):
            if saved and saved not in names:
                names.append(saved)
        values = [''] + names
        for cmb in self.skill_slot_boxes:
            cmb['values'] = values

    def _load_skill_slots_from_cfg(self):
        saved = self.hunt_cfg.get('skill_slots', []) if hasattr(self, 'hunt_cfg') else []
        
        # Handle both formats: list of strings (old) and list of dicts (new)
        normalized_slots = []
        for slot in saved:
            if isinstance(slot, dict):
                # New format: {"name": "skill_name"}
                normalized_slots.append(slot.get('name', ''))
            elif isinstance(slot, str):
                # Old format: "skill_name"
                normalized_slots.append(slot)
            else:
                normalized_slots.append('')
        
        # Extract non-empty names for saved skills
        self.skill_slot_saved_names = [name for name in normalized_slots if name]
        
        self._refresh_skill_slots_options()
        
        # Load saved slots into UI
        for idx, var in enumerate(self.skill_slot_vars):
            name = ''
            if idx < len(normalized_slots):
                name = normalized_slots[idx]
            var.set(name)
        
        self._update_attack_keys_from_slots()

    def _collect_skill_slots(self):
        if not self.skill_slot_vars:
            self.skill_slot_saved_names = []
            return []
        mapping = {skill['name']: skill for skill in self.skills}
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
            slots.append({
                'name': skill['name'],
                'key': skill['key'],
                'type': skill.get('type', 'attack'),
                'cooldown': float(skill.get('cooldown', 0.0)),
                'cast_time': float(skill.get('cast_time', 0.0)),
                'image': skill.get('image', ''),
            })
        self.skill_slot_saved_names = saved_names
        return slots

    def _clear_skill_slot(self, var):
        var.set('')
        self._update_attack_keys_from_slots()

    def _update_skill_preview(self, path):
        label = getattr(self, 'skill_preview_label', None)
        if not label:
            return
        path = (path or '').strip()
        if not path:
            label.config(image='', text=self._t('skill_no_image'))
            self.skill_preview_image = None
            return
        
        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.config(image=photo, text='')
            self.skill_preview_image = photo
            return
        
        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(path)
                img.thumbnail((200, 200))  # Increased from 96x96 to 200x200 for better visibility
                photo = ImageTk.PhotoImage(img)
            else:
                # Fallback to tk.PhotoImage if PIL not available
                photo = tk.PhotoImage(file=path)
            self._thumbnail_cache[path] = photo  # Cache it
            label.config(image=photo, text='')
            self.skill_preview_image = photo
        except Exception as e:
            # Better error handling with specific message
            error_msg = str(e) if str(e) else self._t('skill_image_error')
            label.config(image='', text=f"❌ {error_msg[:50]}...")
            self.skill_preview_image = None

    def _update_attack_keys_from_slots(self):
        if not hasattr(self, 'attack_keys_var'):
            return
        mapping = {skill['name']: skill for skill in self.skills}
        keys = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            keys.append(skill['key'])
        if keys:
            self.attack_keys_var.set(','.join(keys))
        self.skill_slot_saved_names = [v.get().strip() for v in self.skill_slot_vars if v.get().strip()]
        self._refresh_skill_slots_options()

    def on_skill_browse_image(self):
        path = filedialog.askopenfilename(title='Select skill image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
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
            self.skill_selected_name = skill['name']
            self._skill_fill_form(skill)
        except Exception:
            pass

    def _read_skill_form(self):
        if not hasattr(self, 'skill_name_var'):
            raise ValueError('UI not ready')
        name = self.skill_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        key = self.skill_key_var.get().strip().upper()
        if not key:
            raise ValueError('key required')
        type_label = self.skill_type_var.get().strip() if hasattr(self, 'skill_type_var') else self._t('skill_type_attack')
        skill_type = self._skill_type_from_label(type_label)
        try:
            cooldown = float(self.skill_cooldown_var.get() or 0)
            cast_time = float(self.skill_cast_time_var.get() or 0)
            
            # Buff-specific fields
            duration_sec = 0.0
            pre_refresh_sec = 0.0
            
            if skill_type == 'buff':
                # Validate buff duration is required for buff skills
                duration_str = self.skill_duration_var.get().strip() if hasattr(self, 'skill_duration_var') else ''
                if not duration_str:
                    raise ValueError('Buff duration is required for buff skills')
                duration_sec = float(duration_str)
                if duration_sec <= 0:
                    raise ValueError('Buff duration must be greater than 0')
                
                # Pre-refresh is optional but should be validated if provided
                pre_refresh_str = self.skill_pre_refresh_var.get().strip() if hasattr(self, 'skill_pre_refresh_var') else ''
                if pre_refresh_str:
                    pre_refresh_sec = float(pre_refresh_str)
                    if pre_refresh_sec < 0:
                        raise ValueError('Pre-refresh time cannot be negative')
                    if pre_refresh_sec >= duration_sec:
                        raise ValueError('Pre-refresh time must be less than buff duration')
            
        except ValueError as exc:
            raise exc
        except Exception as exc:
            raise ValueError(exc)
        
        image = self.skill_image_var.get().strip() if hasattr(self, 'skill_image_var') else ''
        return {
            'name': name,
            'key': key,
            'type': skill_type,
            'cooldown': max(cooldown, 0.0),
            'cast_time': max(cast_time, 0.0),
            'duration_sec': duration_sec,
            'pre_refresh_sec': pre_refresh_sec,
            'hold_ms': None,  # Keep existing schema field
            'image': image,
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
            messagebox.showerror(self._t('skill_section'), self._t('skill_invalid').format(e=e))
            return

        idx = self.skill_selected_index
        if idx is None:
            existing = next((i for i, s in enumerate(self.skills) if s['name'].lower() == skill['name'].lower()), None)
            if existing is not None:
                idx = existing
                self.skills[idx] = skill
            else:
                self.skills.append(skill)
                idx = len(self.skills) - 1
        else:
            for i, data in enumerate(self.skills):
                if i != idx and data['name'].lower() == skill['name'].lower():
                    messagebox.showerror(self._t('skill_section'), self._t('skill_duplicate'))
                    return
            self.skills[idx] = skill

        save_skill_library(self.skills)
        self.skill_selected_index = idx
        self.skill_selected_name = skill['name']
        self._refresh_skill_list(select_name=skill['name'])
        self._update_attack_keys_from_slots()
        self.hunt_status.set(self._t('skill_saved'))

    def on_skill_delete(self):
        if self.skill_selected_index is None or self.skill_selected_index >= len(self.skills):
            messagebox.showinfo(self._t('skill_section'), self._t('skill_not_selected'))
            return
        removed = self.skills.pop(self.skill_selected_index)
        save_skill_library(self.skills)
        for var in self.skill_slot_vars:
            if var.get().strip() == removed['name']:
                var.set('')
        self.skill_slot_saved_names = [v.get().strip() for v in self.skill_slot_vars if v.get().strip()]
        self.skill_selected_index = None
        self.skill_selected_name = None
        self._refresh_skill_list()
        self._update_attack_keys_from_slots()
        self.hunt_status.set(self._t('skill_deleted'))

    def on_skill_slot_changed(self, _evt=None):
        self._update_attack_keys_from_slots()
    
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
        if not hasattr(self, 'skill_stats_tree'):
            return
        
        # Clear existing rows
        for item in self.skill_stats_tree.get_children():
            self.skill_stats_tree.delete(item)
        
        # Populate with current stats
        for skill_name, data in stats_dict.items():
            cast_count = data.get('cast_count', 0)
            time_since = data.get('time_since_last_cast')
            success_rate = data.get('success_rate', 0.0)
            
            # Format last cast time
            if time_since is None:
                last_cast_str = 'Never'
            else:
                last_cast_str = self._t('time_ago_format').format(time=time_since)
            
            # Format cooldown status (simplified - just show "Ready" for now)
            # TODO: Integrate with actual skill cooldown data from skills.json
            cooldown_str = self._t('cooldown_ready')
            
            # Format success rate
            success_str = f"{success_rate:.1f}%"
            
            # Determine color tag based on success rate
            if success_rate >= 90:
                tag = 'excellent'
            elif success_rate >= 70:
                tag = 'good'
            else:
                tag = 'poor'
            
            # Insert row
            self.skill_stats_tree.insert('', 'end', values=(
                skill_name,
                cast_count,
                last_cast_str,
                cooldown_str,
                success_str
            ), tags=(tag,))

    def _prepare_skill_runtime(self, cfg):
        runtime = []
        slots = cfg.get('skill_slots') or []
        default_press = int(cfg.get('attack_press_ms', 60))
        for slot in slots:
            key = str(slot.get('key', '')).strip().upper()
            if not key:
                continue
            cooldown = max(float(slot.get('cooldown', 0.0)), 0.0)
            cast_time = max(float(slot.get('cast_time', 0.0)), 0.0)
            press_ms = max(int(cast_time * 1000), 30)
            if press_ms < default_press:
                press_ms = default_press
            press_ms = min(press_ms, 2000)
            runtime.append({
                'name': slot.get('name', ''),
                'key': key,
                'type': slot.get('type', 'attack'),
                'cooldown': cooldown,
                'cast_time': cast_time,
                'press_ms': press_ms,
                'next_ready': 0.0,
            })
        return runtime

    def _try_cast_skills(self, runtime, now, target_available, attack_phase, skill_stats=None):
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
        ready_skills = [s for s in runtime if now >= s['next_ready']]
        if ready_skills:
            print(f"[Skills] Ready skills: {[s['name'] for s in ready_skills]}, target={target_available}, attack_phase={attack_phase}")
        
        for skill in runtime:
            if now < skill['next_ready']:
                continue
            skill_type = skill.get('type', 'attack')
            if skill_type == 'attack' and not (attack_phase and target_available):
                continue
            if skill_type == 'buff' and attack_phase:
                # allow buffs even during attack phase, but no extra gating
                pass
            
            # Attempt to cast skill
            cast_success = False
            try:
                print(f"[Skills] Casting {skill['name']} (key={skill['key']}, press_ms={skill['press_ms']})")
                tap(skill['key'], skill['press_ms'])
                cast_success = True
                print(f"[Skills] ✓ Cast successful: {skill['name']}")
            except Exception as e:
                print(f"[Skills] ✗ Cast failed: {skill['name']} - {e}")
                pass
            
            # Sprint 22 Patch 1: Record skill cast in training mode
            if skill_stats and skill.get('name'):
                skill_stats.record_cast(skill['name'], success=cast_success)
            
            if not cast_success:
                continue
            
            cooldown = skill.get('cooldown', 0.0)
            skill['next_ready'] = time.time() + cooldown if cooldown > 0 else now
            sleep_extra = max(skill.get('cast_time', 0.0) - (skill['press_ms'] / 1000.0), 0.0)
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
        has_window = hasattr(self, 'hunt_selected') and self.hunt_selected
        if not has_window:
            window_title = self.hunt_cfg.get('window_title', '').strip()
            if not window_title:
                errors.append("❌ No game window selected")
                errors.append("   → Click 'Find Windows' button to select your game")
        
        # 2. Check monster templates exist
        templates = self.hunt_cfg.get('templates', [])
        monster_list = self.hunt_cfg.get('monster_list', [])
        has_templates = len(templates) > 0
        has_monsters = len(monster_list) > 0
        
        if not has_templates and not has_monsters:
            errors.append("❌ No monster templates configured")
            errors.append("   → Go to Setup tab and add monster templates")
            errors.append("   → Or run Setup Wizard for guided configuration")
        
        # 3. Check skills configured (at least 1 attack skill)
        skill_slots = self.hunt_cfg.get('skill_slots', [])
        attack_skills = [s for s in skill_slots if s.get('enabled', True) and s.get('type', 'attack') == 'attack']
        
        if len(attack_skills) == 0:
            errors.append("❌ No attack skills configured")
            errors.append("   → Configure at least 1 attack skill in Setup tab")
            errors.append("   → Or press Ctrl+K to open Skill Manager")
        
        # 4. Check target key configured
        target_key = self.hunt_cfg.get('target_key', '').strip()
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
            messagebox.showerror(
                self._t('error_title'),
                validation_error,
                parent=self
            )
            return
        
        try:
            cfg = self._hunt_from_ui()
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('invalid_hunt').format(e=e))
            return
        save_hunt_config(cfg)
        self.hunt_cfg = cfg
        self.hunt_running = True
        
        # Update button states with enhanced visual feedback
        self.hunt_start_btn.config(
            state='disabled',
            bg='#A5D6A7',              # Light green when disabled
            relief='sunken',
            cursor='arrow'
        )
        self.hunt_stop_btn.config(
            state='normal',
            bg='#C62828',              # Bright red when active
            relief='raised',
            cursor='hand2'
        )
        self.hunt_status.set(self._t('hunt_running'))

        def worker():
            logger = get_hunt_logger()
            try:
                # Focus the target window; minimize GUI only if focus succeeded
                try:
                    focused = False
                    if self.hunt_selected and self.hunt_selected.get('hwnd'):
                        focused = self._bring_window_to_front_by_hwnd(int(self.hunt_selected['hwnd']))
                    elif cfg.get('window_pid'):
                        focused = self._bring_window_to_front_by_pid(int(cfg['window_pid']))
                    if not focused:
                        focused = self._bring_window_to_front(cfg.get('window_title', 'Cabal'))
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
                mode = 'search'
                last_seen = 0.0
                attack_started = 0.0
                lost_timeout = float(cfg.get('lost_timeout_sec', 0.8))
                attack_min_duration = float(cfg.get('attack_min_duration_sec', 1.5))
                skill_runtime = self._prepare_skill_runtime(cfg)
                has_attack_skills = any(skill.get('type', 'attack') != 'buff' for skill in skill_runtime)
                last_match_info = None
                
                # Sprint 22 Patch 2: Training mode should NOT cycle targets (no Tab spam)
                training_mode_active = cfg.get('training_mode_enabled', False)
                skill_stats = SkillStats() if training_mode_active else None
                last_stats_update = 0.0
                stats_update_interval = 0.5  # Update UI every 0.5 seconds
                
                while self.hunt_running:
                    now = time.time()
                    if cfg.get('bring_to_front_each_cycle'):
                        ok = False
                        try:
                            if self.hunt_selected and self.hunt_selected.get('hwnd'):
                                ok = self._bring_window_to_front_by_hwnd(int(self.hunt_selected['hwnd']))
                            elif cfg.get('window_pid'):
                                ok = self._bring_window_to_front_by_pid(int(cfg['window_pid']))
                        except Exception:
                            ok = False
                        if not ok:
                            self._bring_window_to_front(cfg.get('window_title', 'Cabal'))

                    # periodic detection with multi-template support
                    if now - last_search >= float(cfg['search_interval']):
                        box, match_info = self._hunt_locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                            # Log template match with accurate confidence from template_matcher
                            if match_info and last_match_info != match_info:
                                # Log match details
                                template_name = match_info.get('name') or Path(match_info.get('path', '')).stem
                                threshold = match_info.get('threshold', 0.8)
                                confidence = match_info.get('confidence', 0.0)
                                monster_name = match_info.get('monster_name', '')
                                logger.log_match(template_name, box, threshold, confidence, monster_name)
                                
                                status_msg = f"Target: {template_name} (conf: {confidence:.3f})"
                                self.hunt_status.set(status_msg)
                                last_match_info = match_info
                        else:
                            have_target = False
                            if last_match_info:
                                # Log target lost
                                duration = now - attack_started if mode == 'attack' else 0
                                template_name = last_match_info.get('name') or Path(last_match_info.get('path', '')).stem
                                monster_name = last_match_info.get('monster_name', '')
                                logger.log_lost(template_name, monster_name, duration)
                                
                                self.hunt_status.set(self._t('hunt_running'))
                                last_match_info = None
                        last_search = now

                    # Sprint 22 Patch 1: Update skill stats display periodically
                    if skill_stats and (now - last_stats_update) >= stats_update_interval:
                        try:
                            all_stats = skill_stats.get_all_stats()
                            self.after(0, lambda: self.update_skill_stats_display(all_stats))
                            last_stats_update = now
                        except Exception:
                            pass  # Ignore stats update errors

                    if skill_runtime:
                        print(f"[Hunt] Search mode - Casting buffs only (have_target={have_target})")
                        self._try_cast_skills(skill_runtime, now, have_target, attack_phase=False, skill_stats=skill_stats)

                    if mode == 'search':
                        if have_target:
                            logger.log_state_change('search', 'attack', 'target_found')
                            mode = 'attack'
                            attack_started = now
                            continue
                        
                        # Sprint 22 Patch 2: Training mode SKIP target cycling
                        # Training dummy is stationary - no need to spam Tab/Z key
                        if not training_mode_active:
                            tap(cfg['target_key'])
                            time.sleep(float(cfg['target_cycle_delay']))
                        else:
                            # Training mode: Just wait for template detection
                            time.sleep(0.1)
                        continue

                    # mode == 'attack'
                    if have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration:
                        target_active = have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration
                        print(f"[Hunt] Attack mode - target_active={target_active}, have_target={have_target}, has_attack_skills={has_attack_skills}")
                        if skill_runtime and has_attack_skills:
                            # Ensure target is selected before casting attack skills
                            if target_active:
                                tap(cfg['target_key'])  # Press Z to ensure target locked
                                time.sleep(0.05)  # Small delay for target lock
                            self._try_cast_skills(skill_runtime, now, target_active, attack_phase=True, skill_stats=skill_stats)
                            if not target_active:
                                logger.log_state_change('attack', 'search', 'lost_timeout')
                                mode = 'search'
                                time.sleep(0.05)
                                continue
                            time.sleep(float(cfg['attack_interval']))
                            continue
                        for k in cfg['attack_keys']:
                            if not self.hunt_running:
                                break
                            try:
                                tap(k, int(cfg['attack_press_ms']))
                            except Exception:
                                pass
                            time.sleep(float(cfg['attack_interval']))
                    else:
                        logger.log_state_change('attack', 'search', 'lost_timeout')
                        mode = 'search'
                        time.sleep(0.05)
                    time.sleep(0.02)
            except Exception as e:
                logger.log_error('hunt_loop', f'Hunt error: {str(e)}', e)
                logger.log_hunt_stop('error')
            finally:
                try:
                    already_logged = bool(getattr(logger, '_stop_logged', False))
                except Exception:
                    already_logged = False
                if not already_logged:
                    logger.log_hunt_stop('manual_stop')
                    try:
                        setattr(logger, '_stop_logged', True)
                    except Exception:
                        pass
                self.hunt_running = False
                self.after(0, self._after_hunt_stop)

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def _after_hunt_stop(self):
        # Update button states with enhanced visual feedback
        self.hunt_start_btn.config(
            state='normal',
            bg='#2E7D32',              # Restore green when active
            relief='raised',
            cursor='hand2'
        )
        self.hunt_stop_btn.config(
            state='disabled',
            bg='#FFCDD2',              # Light red when disabled
            relief='sunken',
            cursor='arrow'
        )
        
        # Note: Global hotkeys cleanup will be handled in on_close()
        
        # restore GUI
        try:
            self.deiconify()
            self.lift()
        except Exception:
            pass
        self.hunt_status.set(self._t('hunt_stopped'))

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
    # -----------------
    def _t(self, key: str) -> str:
        try:
            return i18n_t(key, ns=I18N_GLOBAL, lang=self.lang)
        except Exception:
            return GLOBAL_TRANSLATIONS.get(self.lang, GLOBAL_TRANSLATIONS.get('en', {})).get(key, key)

    def on_language_change(self, _evt=None):
        self.lang = self.lang_var.get()
        self.cfg.setdefault('ui', {})
        self.cfg['ui']['language'] = self.lang
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
        self.title(self._t('app_title'))
        self._build_ui()


def main():
    """Main entry point with single instance lock."""
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
            parent=root
        )
        
        root.destroy()
        sys.exit(1)
    
    try:
        # Start application
        app = App()
        app.protocol('WM_DELETE_WINDOW', app.on_close)
        app.mainloop()
    finally:
        # Always release lock on exit
        instance_lock.release()


if __name__ == '__main__':
    main()
