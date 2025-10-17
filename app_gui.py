import ctypes
import json
import math
import os
import threading
import time
from ctypes import wintypes
from pathlib import Path
from typing import Dict, List, Optional

import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from win_input import tap

try:
    import keyboard  # type: ignore
except Exception:
    keyboard = None  # type: ignore

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
# Simple i18n dictionary
LANG = {
    'en': {
        'app_title': 'Cabal Auto GUI',
        'tab_click': 'Click',
        'tab_hunt': 'Hunt',
        'language': 'Language',
        'lang_en': 'English',
        'lang_vi': 'Tiếng Việt',
        'x': 'X',
        'y': 'Y',
        'interval': 'Interval (s)',
        'pick': 'Pick (3s)',
        'always_on_top': 'Always on top',
        'start': 'Start',
        'stop': 'Stop',
        'save_config': 'Save Config',
        'ready': 'Ready',
        'stopped': 'Stopped',
        'failsafe_stopped': 'FAILSAFE triggered. Stopped.',
        'pick_in': 'Pick in {i}... Move mouse to target',
        'picked': 'Picked: ({x}, {y})',
        'pick_error': 'Pick error: {e}',
        'window_title_contains': 'Window title contains:',
        'find_windows': 'Find Windows',
        'bring_to_front': 'Bring To Front',
        'bring_each_cycle': 'Force focus every cycle (use only if needed)',
        'target_key': 'Target key:',
        'attack_keys': 'Attack keys (, sep):',
        'press_ms': 'Press ms:',
        'target_cycle': 'Target cycle (s):',
        'search_interval': 'Search interval (s):',
        'attack_interval': 'Attack interval (s):',
        'lost_timeout': 'Keep attacking for (s) after target lost:',
        'attack_duration': 'Minimum attack duration (s):',
        'template': 'Template:',
        'browse': 'Browse',
        'region_l': 'Region: L',
        't': 'T',
        'w': 'W',
        'h': 'H',
        'pick_tl': 'Pick TL (3s)',
        'pick_br': 'Pick BR (3s)',
        'save_hunt': 'Save Hunt Config',
        'start_hunt': 'Start Hunt',
        'stop_hunt': 'Stop Hunt',
        'hunt_idle': 'Hunt idle',
        'hunt_running': 'Hunt running',
        'hunt_stopped': 'Hunt stopped',
        'selected_window': 'Selected window: {title}',
        'bring_ok': 'Brought to front',
        'bring_fail': 'Bring to front failed',
        'invalid_input': 'Invalid input: {e}',
        'invalid_hunt': 'Invalid hunt config: {e}',
        'no_windows': 'No matching windows found',
        'warn_pygetwindow': 'pygetwindow not available',
        'win_list_label': 'Windows (filtered):',
        'monster_section': 'Monster Library',
        'monster_list': 'Saved monsters:',
        'monster_name': 'Name:',
        'monster_hp': 'HP:',
        'monster_damage': 'Damage per hit:',
        'monster_template': 'Template image:',
        'monster_new': 'New',
        'monster_save': 'Save monster',
        'monster_delete': 'Delete',
        'monster_use_template': 'Use for hunt',
        'monster_estimate': 'Estimate kill time',
        'monster_estimate_result': 'Estimated kill time: {time:.2f}s (DPS {dps:.1f})',
    'monster_estimate_detail': '{base} -> attack {attack:.2f}s, lost {lost:.2f}s',
        'monster_saved': 'Monster saved',
        'monster_deleted': 'Monster deleted',
        'monster_invalid': 'Invalid monster data: {e}',
        'monster_not_selected': 'Select a monster first',
    'monster_applied': 'Applied monster to hunt config',
    'monster_duplicate': 'Monster name already exists',
    'skill_section': 'Skill Library',
    'skill_list': 'Skills:',
    'skill_name': 'Name:',
    'skill_key': 'Key:',
    'skill_type': 'Type:',
    'skill_type_attack': 'Attack',
    'skill_type_buff': 'Buff',
    'skill_cooldown': 'Cooldown (s):',
    'skill_cast_time': 'Cast time (s):',
    'skill_image': 'Image path:',
    'skill_no_image': 'No preview',
    'skill_image_error': 'Preview failed',
    'skill_new': 'New skill',
    'skill_save': 'Save skill',
    'skill_delete': 'Delete skill',
    'skill_saved': 'Skill saved',
    'skill_deleted': 'Skill deleted',
    'skill_invalid': 'Invalid skill data: {e}',
    'skill_not_selected': 'Select a skill first',
    'skill_slots': 'Skill rotation',
    'skill_slot_label': 'Slot {i}:',
    'skill_slot_clear': 'Clear',
    'skill_estimate_missing': 'Missing skill data',
    'skill_duplicate': 'Skill name already exists',
    },
    'vi': {
        'app_title': 'Cabal Auto GUI',
        'tab_click': 'Click',
        'tab_hunt': 'Săn quái',
        'language': 'Ngôn ngữ',
        'lang_en': 'English',
        'lang_vi': 'Tiếng Việt',
        'x': 'X',
        'y': 'Y',
        'interval': 'Khoảng (giây)',
        'pick': 'Lấy tọa độ (3s)',
        'always_on_top': 'Luôn nổi (Always on top)',
        'start': 'Bắt đầu',
        'stop': 'Dừng',
        'save_config': 'Lưu cấu hình',
        'ready': 'Sẵn sàng',
        'stopped': 'Đã dừng',
        'failsafe_stopped': 'Đã dừng (FAILSAFE)',
        'pick_in': 'Lấy sau {i}s... Di chuột đến vị trí',
        'picked': 'Đã lấy: ({x}, {y})',
        'pick_error': 'Lỗi lấy tọa độ: {e}',
        'window_title_contains': 'Tiêu đề cửa sổ chứa:',
        'find_windows': 'Tìm cửa sổ',
        'bring_to_front': 'Đưa lên trước',
        'bring_each_cycle': 'Đưa cửa sổ lên mỗi vòng (chỉ dùng khi cần)',
        'target_key': 'Phím chọn mục tiêu:',
        'attack_keys': 'Phím đánh (cách nhau bằng dấu phẩy):',
        'press_ms': 'Giữ phím (ms):',
        'target_cycle': 'Chu kỳ đổi mục tiêu (s):',
        'search_interval': 'Chu kỳ tìm (s):',
        'attack_interval': 'Chu kỳ đánh (s):',
        'lost_timeout': 'Giữ đánh thêm (giây) sau khi mất dấu:',
        'attack_duration': 'Thời gian đánh tối thiểu (giây):',
        'template': 'Ảnh mẫu:',
        'browse': 'Chọn ảnh',
        'region_l': 'Vùng tìm: L',
        't': 'T',
        'w': 'R',
        'h': 'D',
        'pick_tl': 'Chọn góc TL (3s)',
        'pick_br': 'Chọn góc BR (3s)',
        'save_hunt': 'Lưu cấu hình săn',
        'start_hunt': 'Chạy săn',
        'stop_hunt': 'Dừng săn',
        'hunt_idle': 'Sẵn sàng săn',
        'hunt_running': 'Đang săn',
        'hunt_stopped': 'Đã dừng săn',
        'selected_window': 'Đã chọn cửa sổ: {title}',
        'bring_ok': 'Đã đưa lên trước',
        'bring_fail': 'Không đưa lên trước được',
        'invalid_input': 'Dữ liệu không hợp lệ: {e}',
        'invalid_hunt': 'Cấu hình săn không hợp lệ: {e}',
        'no_windows': 'Không tìm thấy cửa sổ phù hợp',
        'warn_pygetwindow': 'Chưa có pygetwindow',
        'win_list_label': 'Danh sách cửa sổ (đã lọc):',
        'monster_section': 'Thư viện quái',
        'monster_list': 'Danh sách quái:',
        'monster_name': 'Tên:',
        'monster_hp': 'HP:',
        'monster_damage': 'Sát thương mỗi đòn:',
        'monster_template': 'Ảnh template:',
        'monster_new': 'Tạo mới',
        'monster_save': 'Lưu quái',
        'monster_delete': 'Xóa',
        'monster_use_template': 'Dùng cho săn',
        'monster_estimate': 'Tính thời gian hạ',
        'monster_estimate_result': 'Thời gian ước tính: {time:.2f}s (DPS {dps:.1f})',
    'monster_estimate_detail': '{base} -> đánh tối thiểu {attack:.2f}s, giữ thêm {lost:.2f}s',
        'monster_saved': 'Đã lưu quái',
        'monster_deleted': 'Đã xóa quái',
        'monster_invalid': 'Thông tin quái không hợp lệ: {e}',
        'monster_not_selected': 'Hãy chọn một quái trước',
    'monster_applied': 'Đã áp dụng vào cấu hình săn',
    'monster_duplicate': 'Tên quái đã tồn tại',
    'skill_section': 'Thư viện kỹ năng',
    'skill_list': 'Danh sách kỹ năng:',
    'skill_name': 'Tên kỹ năng:',
    'skill_key': 'Phím:',
    'skill_type': 'Loại:',
    'skill_type_attack': 'Tấn công',
    'skill_type_buff': 'Buff',
    'skill_cooldown': 'Hồi chiêu (giây):',
    'skill_cast_time': 'Thi triển (giây):',
    'skill_image': 'Ảnh kỹ năng:',
    'skill_no_image': 'Chưa có ảnh',
    'skill_image_error': 'Không xem được ảnh',
    'skill_new': 'Tạo kỹ năng',
    'skill_save': 'Lưu kỹ năng',
    'skill_delete': 'Xóa kỹ năng',
    'skill_saved': 'Đã lưu kỹ năng',
    'skill_deleted': 'Đã xóa kỹ năng',
    'skill_invalid': 'Thông tin kỹ năng không hợp lệ: {e}',
    'skill_not_selected': 'Hãy chọn một kỹ năng trước',
    'skill_slots': 'Thiết lập kỹ năng',
    'skill_slot_label': 'Ô {i}:',
    'skill_slot_clear': 'Xóa',
    'skill_estimate_missing': 'Thiếu thông tin kỹ năng',
    'skill_duplicate': 'Tên kỹ năng đã tồn tại',
    }
}

CONFIG_PATH = Path(__file__).with_name('config.json')
HUNT_CONFIG_PATH = Path(__file__).with_name('hunt_config.json')
MONSTER_DB_PATH = Path(__file__).with_name('monsters.json')
SKILL_DB_PATH = Path(__file__).with_name('skills.json')


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
                monsters.append({
                    'name': name,
                    'hp': hp,
                    'damage_per_hit': dmg,
                    'template': template,
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
        safe.append({
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
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


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "click": {"x": 500, "y": 400, "interval_sec": 2.0},
        "hotkeys": {"toggle": "f8", "exit": "f9"},
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
        "target_key": "TAB",
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
        "skill_slots": []
    }
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            default.update(data)
        except Exception:
            pass
    default.setdefault('skill_slots', [])
    return default


def save_hunt_config(cfg):
    with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load config and language
        self.cfg = load_config()
        self.hunt_cfg = load_hunt_config()
        self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))

        self.title(self._t('app_title'))
        self.resizable(False, False)

        # State
        self.click_running = False
        self.click_thread = None
        self.hunt_running = False
        self.hunt_thread = None
        self.win_items = []  # list of {'hwnd','pid','title','proc'}
        self.hunt_selected = None  # currently selected window info
        self._stop_hotkey = None
        self.monsters = load_monster_library()
        self.monster_selected_index = None
        self.monster_selected_name = self.monsters[0]['name'] if self.monsters else None
        self.skills = load_skill_library()
        self.skill_selected_index = None
        self.skill_selected_name = self.skills[0]['name'] if self.skills else None
        self.skill_preview_image = None
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self.skill_slot_saved_names = [slot.get('name', '') for slot in self.hunt_cfg.get('skill_slots', []) if isinstance(slot, dict) and slot.get('name')]

        pyautogui.FAILSAFE = bool(self.cfg.get('safety', {}).get('failsafe', True))

        self._build_ui()
        # ESC to stop hunt quickly
        self.bind('<Escape>', lambda e: self.on_hunt_stop())

    # -----------------
    # UI Construction
    # -----------------
    def _build_ui(self):
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # Topbar with language selector
        top = tk.Frame(self, padx=8, pady=6)
        top.pack(fill='x')
        tk.Label(top, text=self._t('language')).pack(side='left')
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cmb = ttk.Combobox(top, textvariable=self.lang_var, state='readonly', width=12)
        lang_cmb['values'] = ('en', 'vi')
        lang_cmb.pack(side='left', padx=(6,0))
        lang_cmb.bind('<<ComboboxSelected>>', self.on_language_change)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        # Hunt tab
        tab_hunt = tk.Frame(nb, padx=12, pady=12)
        nb.add(tab_hunt, text=self._t('tab_hunt'))
        self._build_hunt_tab(tab_hunt)

    # Click Tab removed

    # Hunt Tab
    def _build_hunt_tab(self, frm):
        # Window title
        tk.Label(frm, text=self._t('window_title_contains')).grid(row=0, column=0, sticky='e')
        self.win_title_var = tk.StringVar(value=str(self.hunt_cfg.get('window_title', 'Cabal')))
        tk.Entry(frm, textvariable=self.win_title_var, width=24).grid(row=0, column=1, sticky='w')

        tk.Button(frm, text=self._t('find_windows'), command=self.on_hunt_find_windows).grid(row=0, column=2, padx=(8,0))
        tk.Button(frm, text=self._t('bring_to_front'), command=self.on_hunt_bring_front).grid(row=0, column=3)

        # Window list (filtered)
        tk.Label(frm, text=self._t('win_list_label')).grid(row=1, column=0, columnspan=4, sticky='w', pady=(6,0))
        self.win_listbox = tk.Listbox(frm, height=6, exportselection=False)
        self.win_listbox.grid(row=2, column=0, columnspan=4, sticky='we')
        self.win_listbox.bind('<<ListboxSelect>>', self.on_window_selected)

        # Target/Attack keys
        tk.Label(frm, text=self._t('target_key')).grid(row=3, column=0, sticky='e', pady=(8,0))
        self.target_key_var = tk.StringVar(value=str(self.hunt_cfg.get('target_key', 'TAB')))
        tk.Entry(frm, textvariable=self.target_key_var, width=8).grid(row=3, column=1, sticky='w', pady=(8,0))

        tk.Label(frm, text=self._t('attack_keys')).grid(row=3, column=2, sticky='e', pady=(8,0))
        self.attack_keys_var = tk.StringVar(value=','.join(self.hunt_cfg.get('attack_keys', ['1','2','3'])))
        tk.Entry(frm, textvariable=self.attack_keys_var, width=18).grid(row=3, column=3, sticky='w', pady=(8,0))

        # Timing
        tk.Label(frm, text=self._t('press_ms')).grid(row=4, column=0, sticky='e')
        self.attack_press_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_press_ms', 60)))
        tk.Entry(frm, textvariable=self.attack_press_var, width=8).grid(row=4, column=1, sticky='w')

        tk.Label(frm, text=self._t('target_cycle')).grid(row=4, column=2, sticky='e')
        self.target_cycle_var = tk.StringVar(value=str(self.hunt_cfg.get('target_cycle_delay', 0.2)))
        tk.Entry(frm, textvariable=self.target_cycle_var, width=8).grid(row=4, column=3, sticky='w')

        tk.Label(frm, text=self._t('search_interval')).grid(row=5, column=0, sticky='e')
        self.search_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('search_interval', 0.25)))
        tk.Entry(frm, textvariable=self.search_interval_var, width=8).grid(row=5, column=1, sticky='w')

        tk.Label(frm, text=self._t('attack_interval')).grid(row=5, column=2, sticky='e')
        self.attack_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_interval', 0.15)))
        tk.Entry(frm, textvariable=self.attack_interval_var, width=8).grid(row=5, column=3, sticky='w')

        tk.Label(frm, text=self._t('lost_timeout')).grid(row=6, column=0, sticky='e', pady=(8,0))
        self.lost_timeout_var = tk.StringVar(value=str(self.hunt_cfg.get('lost_timeout_sec', 1.2)))
        tk.Entry(frm, textvariable=self.lost_timeout_var, width=8).grid(row=6, column=1, sticky='w', pady=(8,0))

        tk.Label(frm, text=self._t('attack_duration')).grid(row=6, column=2, sticky='e', pady=(8,0))
        self.attack_duration_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_min_duration_sec', 1.5)))
        tk.Entry(frm, textvariable=self.attack_duration_var, width=8).grid(row=6, column=3, sticky='w', pady=(8,0))

        # Template & Region
        tk.Label(frm, text=self._t('template')).grid(row=7, column=0, sticky='e')
        self.template_var = tk.StringVar(value=str(self.hunt_cfg.get('template_path', 'assets/images/target_frame.png')))
        tk.Entry(frm, textvariable=self.template_var, width=36).grid(row=7, column=1, columnspan=2, sticky='w')
        tk.Button(frm, text=self._t('browse'), command=self.on_hunt_browse_template).grid(row=7, column=3)

        tk.Label(frm, text=self._t('region_l')).grid(row=8, column=0, sticky='e')
        region = self.hunt_cfg.get('region') or ["", "", "", ""]
        self.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")
        tk.Entry(frm, textvariable=self.reg_l, width=6).grid(row=8, column=1, sticky='w')
        tk.Label(frm, text=self._t('t')).grid(row=8, column=1, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_t, width=6).grid(row=8, column=2, sticky='w')
        tk.Label(frm, text=self._t('w')).grid(row=8, column=2, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_w, width=6).grid(row=8, column=3, sticky='w')
        tk.Label(frm, text=self._t('h')).grid(row=8, column=3, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_h, width=6).grid(row=8, column=3, sticky='e', padx=(24,0))

        self.bring_front_var = tk.BooleanVar(value=bool(self.hunt_cfg.get('bring_to_front_each_cycle', False)))
        tk.Checkbutton(frm, text=self._t('bring_each_cycle'), variable=self.bring_front_var).grid(row=9, column=0, columnspan=4, sticky='w', pady=(6,0))

        pick_frame = tk.Frame(frm)
        pick_frame.grid(row=10, column=0, columnspan=4, pady=(6,0))
        tk.Button(pick_frame, text=self._t('pick_tl'), command=lambda: self.on_hunt_pick_corner('tl')).pack(side='left')
        tk.Button(pick_frame, text=self._t('pick_br'), command=lambda: self.on_hunt_pick_corner('br')).pack(side='left', padx=(8,0))

        # Hunt buttons
        hbtn = tk.Frame(frm)
        hbtn.grid(row=11, column=0, columnspan=4, pady=(12,0))
        tk.Button(hbtn, text=self._t('save_hunt'), command=self.on_hunt_save).pack(side='left')
        self.hunt_start_btn = tk.Button(hbtn, text=self._t('start_hunt'), command=self.on_hunt_start)
        self.hunt_start_btn.pack(side='left', padx=(8,0))
        self.hunt_stop_btn = tk.Button(hbtn, text=self._t('stop_hunt'), command=self.on_hunt_stop, state='disabled')
        self.hunt_stop_btn.pack(side='left', padx=(8,0))

        # Monster library
        monster_frame = tk.LabelFrame(frm, text=self._t('monster_section'), padx=8, pady=6)
        monster_frame.grid(row=12, column=0, columnspan=4, sticky='we', pady=(12,0))
        monster_frame.grid_columnconfigure(0, weight=1)
        monster_frame.grid_columnconfigure(3, weight=1)
        monster_frame.grid_rowconfigure(1, weight=1)

        tk.Label(monster_frame, text=self._t('monster_list')).grid(row=0, column=0, sticky='w')
        self.monster_listbox = tk.Listbox(monster_frame, height=6, exportselection=False)
        self.monster_listbox.grid(row=1, column=0, rowspan=5, sticky='nswe', padx=(0,4))
        monster_scroll = tk.Scrollbar(monster_frame, orient='vertical', command=self.monster_listbox.yview)
        monster_scroll.grid(row=1, column=1, rowspan=5, sticky='ns')
        self.monster_listbox.config(yscrollcommand=monster_scroll.set)
        self.monster_listbox.bind('<<ListboxSelect>>', self.on_monster_selected)

        tk.Label(monster_frame, text=self._t('monster_name')).grid(row=0, column=2, sticky='e')
        self.monster_name_var = tk.StringVar()
        tk.Entry(monster_frame, textvariable=self.monster_name_var, width=24).grid(row=0, column=3, sticky='we', padx=(4,0))

        tk.Label(monster_frame, text=self._t('monster_hp')).grid(row=1, column=2, sticky='e', pady=(2,0))
        self.monster_hp_var = tk.StringVar()
        tk.Entry(monster_frame, textvariable=self.monster_hp_var, width=14).grid(row=1, column=3, sticky='we', padx=(4,0), pady=(2,0))

        tk.Label(monster_frame, text=self._t('monster_damage')).grid(row=2, column=2, sticky='e')
        self.monster_damage_var = tk.StringVar()
        tk.Entry(monster_frame, textvariable=self.monster_damage_var, width=14).grid(row=2, column=3, sticky='we', padx=(4,0))
        tk.Button(monster_frame, text=self._t('monster_estimate'), command=self.on_monster_estimate).grid(row=2, column=4, padx=(8,0))

        self.monster_estimate_var = tk.StringVar(value='')
        tk.Label(monster_frame, textvariable=self.monster_estimate_var, fg='gray').grid(row=3, column=2, columnspan=3, sticky='w', pady=(4,0))

        tk.Label(monster_frame, text=self._t('monster_template')).grid(row=4, column=2, sticky='e')
        self.monster_template_var = tk.StringVar()
        tk.Entry(monster_frame, textvariable=self.monster_template_var, width=24).grid(row=4, column=3, sticky='we', padx=(4,0))
        tk.Button(monster_frame, text=self._t('browse'), command=self.on_monster_browse_template).grid(row=4, column=4, padx=(8,0))

        btn_frame = tk.Frame(monster_frame)
        btn_frame.grid(row=5, column=2, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(btn_frame, text=self._t('monster_new'), command=self.on_monster_new).pack(side='left')
        tk.Button(btn_frame, text=self._t('monster_save'), command=self.on_monster_save).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_delete'), command=self.on_monster_delete).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_use_template'), command=self.on_monster_use_for_hunt).pack(side='left', padx=(12,0))

        self._refresh_monster_list()

        # Skill library
        skill_frame = tk.LabelFrame(frm, text=self._t('skill_section'), padx=8, pady=6)
        skill_frame.grid(row=13, column=0, columnspan=4, sticky='we', pady=(12,0))
        skill_frame.grid_columnconfigure(0, weight=1)
        skill_frame.grid_columnconfigure(3, weight=1)
        skill_frame.grid_rowconfigure(1, weight=1)

        tk.Label(skill_frame, text=self._t('skill_list')).grid(row=0, column=0, sticky='w')
        self.skill_listbox = tk.Listbox(skill_frame, height=6, exportselection=False)
        self.skill_listbox.grid(row=1, column=0, rowspan=5, sticky='nswe', padx=(0,4))
        skill_scroll = tk.Scrollbar(skill_frame, orient='vertical', command=self.skill_listbox.yview)
        skill_scroll.grid(row=1, column=1, rowspan=5, sticky='ns')
        self.skill_listbox.config(yscrollcommand=skill_scroll.set)
        self.skill_listbox.bind('<<ListboxSelect>>', self.on_skill_selected)

        tk.Label(skill_frame, text=self._t('skill_name')).grid(row=0, column=2, sticky='e')
        self.skill_name_var = tk.StringVar()
        tk.Entry(skill_frame, textvariable=self.skill_name_var, width=24).grid(row=0, column=3, sticky='we', padx=(4,0))

        tk.Label(skill_frame, text=self._t('skill_key')).grid(row=1, column=2, sticky='e', pady=(2,0))
        self.skill_key_var = tk.StringVar()
        tk.Entry(skill_frame, textvariable=self.skill_key_var, width=12).grid(row=1, column=3, sticky='w', padx=(4,0), pady=(2,0))

        tk.Label(skill_frame, text=self._t('skill_type')).grid(row=2, column=2, sticky='e')
        self.skill_type_var = tk.StringVar()
        self.skill_type_var.set(self._t('skill_type_attack'))
        self.skill_type_combo = ttk.Combobox(skill_frame, textvariable=self.skill_type_var, state='readonly', width=14)
        self.skill_type_combo['values'] = (self._t('skill_type_attack'), self._t('skill_type_buff'))
        self.skill_type_combo.grid(row=2, column=3, sticky='w', padx=(4,0))

        tk.Label(skill_frame, text=self._t('skill_cooldown')).grid(row=3, column=2, sticky='e')
        self.skill_cooldown_var = tk.StringVar()
        tk.Entry(skill_frame, textvariable=self.skill_cooldown_var, width=12).grid(row=3, column=3, sticky='w', padx=(4,0))

        tk.Label(skill_frame, text=self._t('skill_cast_time')).grid(row=4, column=2, sticky='e')
        self.skill_cast_time_var = tk.StringVar()
        tk.Entry(skill_frame, textvariable=self.skill_cast_time_var, width=12).grid(row=4, column=3, sticky='w', padx=(4,0))

        tk.Label(skill_frame, text=self._t('skill_image')).grid(row=5, column=2, sticky='e')
        self.skill_image_var = tk.StringVar()
        tk.Entry(skill_frame, textvariable=self.skill_image_var, width=24).grid(row=5, column=3, sticky='we', padx=(4,0))
        tk.Button(skill_frame, text=self._t('browse'), command=self.on_skill_browse_image).grid(row=5, column=4, padx=(8,0))

        self.skill_preview_label = tk.Label(skill_frame, text=self._t('skill_no_image'), width=16, height=6, relief='groove')
        self.skill_preview_label.grid(row=1, column=4, rowspan=4, sticky='nswe', padx=(8,0))
        self.skill_image_var.trace_add('write', lambda *_: self._update_skill_preview(self.skill_image_var.get()))

        skill_btn_frame = tk.Frame(skill_frame)
        skill_btn_frame.grid(row=6, column=2, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(skill_btn_frame, text=self._t('skill_new'), command=self.on_skill_new).pack(side='left')
        tk.Button(skill_btn_frame, text=self._t('skill_save'), command=self.on_skill_save).pack(side='left', padx=(6,0))
        tk.Button(skill_btn_frame, text=self._t('skill_delete'), command=self.on_skill_delete).pack(side='left', padx=(6,0))

        # Skill slots
        slot_frame = tk.LabelFrame(frm, text=self._t('skill_slots'), padx=8, pady=6)
        slot_frame.grid(row=14, column=0, columnspan=4, sticky='we', pady=(12,0))
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

        self._refresh_skill_list()
        self._load_skill_slots_from_cfg()

        # Status
        self.hunt_status = tk.StringVar(value=self._t('hunt_idle'))
        tk.Label(frm, textvariable=self.hunt_status, fg='gray').grid(row=15, column=0, columnspan=4, pady=(8,0))

        for i in range(4):
            frm.grid_columnconfigure(i, weight=1)

    # Click UI and handlers removed

    # -----------------
    # Hunt Handlers
    # -----------------
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
                x, y = pyautogui.position()
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
        # Enumerate windows using WinAPI to get hwnd and PID
        items = self._enum_windows()
        sub = (self.win_title_var.get() or 'cabal').strip().lower()
        candidates = [w for w in items if sub in w['title'].lower() or sub in (w['proc'] or '').lower()]
        # Populate listbox
        self.win_items = candidates
        self.win_listbox.delete(0, tk.END)
        for w in candidates:
            label = f"{w['title']}  [PID:{w['pid']}]"
            if w.get('proc'):
                label += f" ({w['proc']})"
            self.win_listbox.insert(tk.END, label)
        if not candidates:
            messagebox.showinfo(self._t('find_windows'), self._t('no_windows'))
            return
        # Select first
        self.win_listbox.selection_clear(0, tk.END)
        self.win_listbox.selection_set(0)
        self.win_listbox.activate(0)
        self.hunt_selected = candidates[0]
        self.win_title_var.set(candidates[0]['title'])
        self.hunt_status.set(self._t('selected_window').format(title=candidates[0]['title']))

    def on_hunt_bring_front(self):
        # Prefer selected item in list
        hwnd = None
        try:
            idx = self.win_listbox.curselection()
            if idx:
                hwnd = self.win_items[idx[0]]['hwnd']
                self.hunt_selected = self.win_items[idx[0]]
        except Exception:
            hwnd = None
        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            ok = self._bring_window_to_front(self.win_title_var.get().strip())
        self.hunt_status.set(self._t('bring_ok') if ok else self._t('bring_fail'))

    def on_window_selected(self, _evt=None):
        try:
            idx = self.win_listbox.curselection()
            if not idx:
                return
            item = self.win_items[idx[0]] if idx[0] < len(self.win_items) else None
            if not item:
                return
            self.hunt_selected = item
            self.win_title_var.set(item['title'])
            self.hunt_status.set(self._t('selected_window').format(title=item['title']))
        except Exception:
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
        region = cfg.get('region')
        template = cfg.get('template_path')
        grayscale = bool(cfg.get('grayscale', True))
        if not template or not Path(template).exists():
            return None
        try:
            if region:
                box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale, confidence=cfg.get('confidence', None))
            else:
                box = pyautogui.locateOnScreen(template, grayscale=grayscale, confidence=cfg.get('confidence', None))
            return box
        except TypeError:
            # Retry without confidence when OpenCV absent
            try:
                if region:
                    box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale)
                else:
                    box = pyautogui.locateOnScreen(template, grayscale=grayscale)
                return box
            except Exception:
                return None
        except Exception:
            return None

    def on_hunt_save(self):
        try:
            cfg = self._hunt_from_ui()
            save_hunt_config(cfg)
            self.hunt_cfg = cfg
            self.hunt_status.set('Saved hunt_config.json')
        except Exception as e:
            messagebox.showerror('Error', self._t('invalid_hunt').format(e=e))

    def _hunt_from_ui(self):
        title = self.win_title_var.get().strip()
        target_key = self.target_key_var.get().strip() or 'TAB'
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        press_ms = int(float(self.attack_press_var.get()))
        cycle_d = float(self.target_cycle_var.get())
        search_i = float(self.search_interval_var.get())
        attack_i = float(self.attack_interval_var.get())
        lost_timeout = float(self.lost_timeout_var.get())
        attack_min_duration = float(self.attack_duration_var.get())
        template = self.template_var.get().strip()
        # Region
        region = None
        if all(v.strip() != '' for v in (self.reg_l.get(), self.reg_t.get(), self.reg_w.get(), self.reg_h.get())):
            region = [int(self.reg_l.get()), int(self.reg_t.get()), int(self.reg_w.get()), int(self.reg_h.get())]
        cfg = {
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
            "confidence": float(self.hunt_cfg.get('confidence', 0.85)),
            "grayscale": bool(self.hunt_cfg.get('grayscale', True)),
            "lost_timeout_sec": lost_timeout,
            "attack_min_duration_sec": attack_min_duration,
            "bring_to_front_each_cycle": bool(self.bring_front_var.get())
        }
        slots = self._collect_skill_slots()
        cfg['skill_slots'] = slots
        if slots:
            cfg['attack_keys'] = [slot['key'] for slot in slots if slot.get('key')]
        return cfg

    # -----------------
    # Monster library helpers
    # -----------------
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
        self._update_monster_estimate_label(monster)

    def _refresh_monster_list(self, select_name=None):
        if select_name is not None:
            self.monster_selected_name = select_name
        if not hasattr(self, 'monster_listbox'):
            return
        self.monster_listbox.delete(0, tk.END)
        for monster in self.monsters:
            self.monster_listbox.insert(tk.END, monster['name'])
        idx = None
        if self.monster_selected_name:
            for i, monster in enumerate(self.monsters):
                if monster['name'] == self.monster_selected_name:
                    idx = i
                    break
        if idx is None and self.monsters and self.monster_selected_name is None:
            idx = 0
        if idx is not None and idx < len(self.monsters):
            self.monster_listbox.selection_clear(0, tk.END)
            self.monster_listbox.selection_set(idx)
            self.monster_listbox.activate(idx)
            self.monster_selected_index = idx
            self.monster_selected_name = self.monsters[idx]['name']
            self._monster_fill_form(self.monsters[idx])
        else:
            self.monster_listbox.selection_clear(0, tk.END)
            self.monster_selected_index = None
            self._monster_clear_form()

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
        return {
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
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
        if hasattr(self, 'monster_listbox'):
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
        if monster.get('template'):
            self.template_var.set(monster['template'])
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
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set('')
        self._update_skill_preview('')

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
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set(skill.get('image', ''))
        self._update_skill_preview(skill.get('image', ''))

    def _refresh_skill_list(self, select_name=None):
        if select_name is not None:
            self.skill_selected_name = select_name
        if not hasattr(self, 'skill_listbox'):
            return
        self.skill_listbox.delete(0, tk.END)
        for skill in self.skills:
            self.skill_listbox.insert(tk.END, skill['name'])
        idx = None
        if self.skill_selected_name:
            for i, skill in enumerate(self.skills):
                if skill['name'] == self.skill_selected_name:
                    idx = i
                    break
        if idx is None and self.skills and self.skill_selected_name is None:
            idx = 0
        if idx is not None and idx < len(self.skills):
            self.skill_listbox.selection_clear(0, tk.END)
            self.skill_listbox.selection_set(idx)
            self.skill_listbox.activate(idx)
            self.skill_selected_index = idx
            self.skill_selected_name = self.skills[idx]['name']
            self._skill_fill_form(self.skills[idx])
        else:
            self.skill_listbox.selection_clear(0, tk.END)
            self.skill_selected_index = None
            self._skill_clear_form()
        self._refresh_skill_slots_options()

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
        self.skill_slot_saved_names = [slot.get('name', '') for slot in saved if slot.get('name')]
        self._refresh_skill_slots_options()
        for idx, var in enumerate(self.skill_slot_vars):
            name = ''
            if idx < len(saved):
                name = saved[idx].get('name', '')
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
        if not hasattr(self, 'skill_preview_label'):
            return
        path = (path or '').strip()
        if not path:
            self.skill_preview_label.config(image='', text=self._t('skill_no_image'))
            self.skill_preview_image = None
            return
        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(path)
                img.thumbnail((96, 96))
                photo = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=path)
            self.skill_preview_label.config(image=photo, text='')
            self.skill_preview_image = photo
        except Exception:
            self.skill_preview_label.config(image='', text=self._t('skill_image_error'))
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
        except Exception as exc:
            raise ValueError(exc)
        image = self.skill_image_var.get().strip() if hasattr(self, 'skill_image_var') else ''
        return {
            'name': name,
            'key': key,
            'type': skill_type,
            'cooldown': max(cooldown, 0.0),
            'cast_time': max(cast_time, 0.0),
            'image': image,
        }

    def on_skill_new(self):
        self.skill_selected_index = None
        self.skill_selected_name = None
        if hasattr(self, 'skill_listbox'):
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

    def _try_cast_skills(self, runtime, now, target_available, attack_phase):
        if not runtime:
            return
        for skill in runtime:
            if now < skill['next_ready']:
                continue
            skill_type = skill.get('type', 'attack')
            if skill_type == 'attack' and not (attack_phase and target_available):
                continue
            if skill_type == 'buff' and attack_phase:
                # allow buffs even during attack phase, but no extra gating
                pass
            try:
                tap(skill['key'], skill['press_ms'])
            except Exception:
                continue
            cooldown = skill.get('cooldown', 0.0)
            skill['next_ready'] = time.time() + cooldown if cooldown > 0 else now
            sleep_extra = max(skill.get('cast_time', 0.0) - (skill['press_ms'] / 1000.0), 0.0)
            if sleep_extra > 0:
                end = time.time() + min(sleep_extra, 0.5)
                while time.time() < end and self.hunt_running:
                    time.sleep(0.02)

    def on_hunt_start(self):
        if self.hunt_running:
            return
        try:
            cfg = self._hunt_from_ui()
        except Exception as e:
            messagebox.showerror('Error', f'Invalid hunt config: {e!r}')
            return
        save_hunt_config(cfg)
        self.hunt_cfg = cfg
        self.hunt_running = True
        self.hunt_start_btn.config(state='disabled')
        self.hunt_stop_btn.config(state='normal')
        self.hunt_status.set(self._t('hunt_running'))

        def worker():
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

                # Optional global stop hotkey (F9)
                if keyboard is not None and self._stop_hotkey is None:
                    try:
                        self._stop_hotkey = keyboard.add_hotkey('f9', lambda: setattr(self, 'hunt_running', False))
                    except Exception:
                        self._stop_hotkey = None

                last_search = 0.0
                have_target = False
                mode = 'search'
                last_seen = 0.0
                attack_started = 0.0
                lost_timeout = float(cfg.get('lost_timeout_sec', 0.8))
                attack_min_duration = float(cfg.get('attack_min_duration_sec', 1.5))
                skill_runtime = self._prepare_skill_runtime(cfg)
                has_attack_skills = any(skill.get('type', 'attack') != 'buff' for skill in skill_runtime)
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

                    # periodic detection
                    if now - last_search >= float(cfg['search_interval']):
                        box = self._hunt_locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                        else:
                            have_target = False
                        last_search = now

                    if skill_runtime:
                        self._try_cast_skills(skill_runtime, now, have_target, attack_phase=False)

                    if mode == 'search':
                        if have_target:
                            mode = 'attack'
                            attack_started = now
                            continue
                        tap(cfg['target_key'])
                        time.sleep(float(cfg['target_cycle_delay']))
                        continue

                    # mode == 'attack'
                    if have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration:
                        target_active = have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration
                        if skill_runtime and has_attack_skills:
                            self._try_cast_skills(skill_runtime, now, target_active, attack_phase=True)
                            if not target_active:
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
                        mode = 'search'
                        time.sleep(0.05)
                    time.sleep(0.02)
            finally:
                self.hunt_running = False
                self.after(0, self._after_hunt_stop)

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def _after_hunt_stop(self):
        self.hunt_start_btn.config(state='normal')
        self.hunt_stop_btn.config(state='disabled')
        # remove global hotkey if registered
        if hasattr(self, '_stop_hotkey') and self._stop_hotkey is not None:
            try:
                if 'keyboard' in globals() and keyboard is not None:
                    keyboard.remove_hotkey(self._stop_hotkey)
            except Exception:
                pass
            self._stop_hotkey = None
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
        self.destroy()

    # -----------------
    # Language helpers
    # -----------------
    def _t(self, key: str) -> str:
        return LANG.get(self.lang, LANG['en']).get(key, key)

    def on_language_change(self, _evt=None):
        self.lang = self.lang_var.get()
        self.cfg.setdefault('ui', {})
        self.cfg['ui']['language'] = self.lang
        save_config(self.cfg)
        # Rebuild UI with new language
        self.title(self._t('app_title'))
        self._build_ui()


def main():
    app = App()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()


if __name__ == '__main__':
    main()
