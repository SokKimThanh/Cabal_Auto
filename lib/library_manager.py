# -*- coding: utf-8 -*-
"""
Library Manager Window - Centralized management for Monsters, Skills, and Timing.

This module provides a dedicated window for managing game libraries:
- Monster Library: CRUD operations for monsters, templates, priorities
- Skill Library: CRUD operations for skills, cooldowns, types
- Timing Calculator: Auto-calculate and apply recommended timing settings

Sprint 19 - Task #1: Library Manager Window
Date: October 18, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional, Dict, Any
import json
import shutil
from pathlib import Path
import time
import re
import sys
import os
import ctypes
from ctypes import wintypes
from typing import Optional

# Optional PIL imports for capture
try:
    from PIL import ImageGrab, Image, ImageTk  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    ImageGrab = None  # type: ignore
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import icon helper
try:
    from lib.icon_helper import get_icon_helper
    icon_helper = get_icon_helper()
except ImportError:
    icon_helper = None

# Shared capture helper
try:
    from lib.capture_helper import capture_region_and_save
except Exception:
    capture_region_and_save = None  # type: ignore

# Import existing utilities (will be available when integrated)
# Use importlib to avoid static unresolved-import issues in editors/linters
try:
    import importlib
    timing_mod = importlib.import_module('lib.timing_calculator')
    calculate_timing = getattr(timing_mod, 'calculate_timing')
    format_timing_recommendation = getattr(timing_mod, 'format_timing_recommendation')
    skills_mod = importlib.import_module('lib.skills')
    load_skill_library = getattr(skills_mod, 'load_skill_library')
    save_skill_library = getattr(skills_mod, 'save_skill_library')
except Exception:
    # Fallback for standalone testing
    def calculate_timing(*args, **kwargs):
        return None
    def format_timing_recommendation(*args, **kwargs):
        return {}
    def load_skill_library():
        return []
    def save_skill_library(*args):
        pass


class LibraryManagerWindow(tk.Toplevel):
    """
    Centralized library management window with 3 tabs.
    
    This window provides a unified interface for:
    1. Monster Library Management (CRUD monsters, templates)
    2. Skill Library Management (CRUD skills, types, cooldowns)
    3. Timing Calculator (Auto-calculate recommendations)
    
    Usage:
        manager = LibraryManagerWindow(
            parent=main_app,
            hunt_cfg=hunt_config_dict,
            lang='vi',
            on_close_callback=lambda changes: handle_changes(changes)
        )
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        hunt_cfg: Dict[str, Any],
        monsters: list,
        skills: list,
        lang: str = 'vi',
        on_close_callback: Optional[Callable] = None
    ):
        """
        Initialize Library Manager Window.
        
        Args:
            parent: Main application window
            hunt_cfg: Current hunt configuration dictionary
            monsters: List of monster dictionaries
            skills: List of skill dictionaries
            lang: Language code ('en' or 'vi')
            on_close_callback: Function to call when window closes with changes
                              Signature: callback(changes: dict)
                              changes = {
                                  'monsters_changed': bool,
                                  'skills_changed': bool,
                                  'timing_applied': bool,
                                  'hunt_cfg': dict  # Updated config if timing applied
                              }
        """
        super().__init__(parent)
        
        # Store parameters
        self.parent = parent
        self.hunt_cfg = hunt_cfg.copy()  # Work on copy, apply on close
        self.monsters = monsters.copy()
        self.skills = skills.copy()
        self.lang = lang
        self.on_close_callback = on_close_callback
        # PIL availability for capture feature
        # Only require core PIL Image for the shared capture helper (pyautogui uses PIL internally).
        # Do NOT require ImageGrab here, since the shared helper can work without it.
        self.pil_available = (Image is not None)
        # Thumbnail image cache to prevent GC
        self._thumb_cache = {}
        # Project paths
        self.project_root = Path(os.path.dirname(os.path.dirname(__file__)))
        self.assets_mon_dir = self.project_root / 'assets' / 'images' / 'monsters'
        self.assets_mon_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_capture_dir = self.project_root / 'tmp' / 'captures'
        self.tmp_capture_dir.mkdir(parents=True, exist_ok=True)
        # Track session temporary images (absolute paths)
        self._session_temp_images = set()
        # Common UI fonts/sizes for consistent look
        self.ui_font_title = ('Segoe UI', 12, 'bold')
        self.ui_font_section = ('Segoe UI', 11, 'bold')
        self.ui_font_label = ('Segoe UI', 10)
        self.ui_font_text = ('Segoe UI', 10)
        self.ui_font_button = ('Segoe UI', 10)
        self.ui_btn_padx = 12
        self.ui_btn_pady = 4
        
        # Track changes
        self.changes_made = {
            'monsters_changed': False,
            'skills_changed': False,
            'timing_applied': False
        }
        
        # Configure window - Normal window (no forced full screen)
        self.title(self._t('library_manager_title'))
        # Use a comfortable default size; keep resizable
        try:
            self.geometry("1200x800")
        except Exception:
            pass
        self.resizable(True, True)
        self.minsize(1200, 700)  # Minimum size constraint
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self._center_window()
        
        # Build UI
        self._build_ui()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    # --------- Path helpers ---------
    def _normalize_to_abs(self, p: str) -> Path:
        try:
            pp = Path(p)
            if not pp.is_absolute():
                pp = (self.project_root / pp).resolve()
            return pp
        except Exception:
            return Path(p)

    def _is_under(self, path: Path, base: Path) -> bool:
        try:
            path = path.resolve()
            base = base.resolve()
            return base in path.parents or path == base
        except Exception:
            return False

    def _is_temp_capture(self, p: str) -> bool:
        try:
            return self._is_under(self._normalize_to_abs(p), self.tmp_capture_dir)
        except Exception:
            return False

    def _make_rel_to_project(self, p: Path) -> str:
        try:
            rel = p.resolve().relative_to(self.project_root.resolve())
            return rel.as_posix()
        except Exception:
            return str(p)

    def _unique_asset_name(self, monster_name: str, template_name: str, ext: str) -> str:
        base_mon = self._sanitize_filename(monster_name or 'monster')
        base_tpl = self._sanitize_filename(template_name or 'template')
        ts = int(time.time() * 1000)
        ext = ext if ext else '.png'
        return f"{base_mon}__{base_tpl}_{ts}{ext}"

    # --------- Unsaved indicator ---------
    def _mark_unsaved(self, state: bool):
        try:
            if hasattr(self, 'unsaved_badge') and self.unsaved_badge:
                if state:
                    text = 'CHƯA LƯU' if self.lang == 'vi' else 'UNSAVED'
                    self.unsaved_badge.config(text=text)
                    # ensure visible
                    self.unsaved_badge.place(relx=1.0, x=-12, rely=0.5, anchor='e')
                else:
                    self.unsaved_badge.config(text='')
                    self.unsaved_badge.place_forget()
        except Exception:
            pass

    # --------- Window activation helpers ---------
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

    def _enum_windows(self) -> list:
        """Enumerate top-level windows with pid and hwnd; returns list of dicts {hwnd, pid, title}."""
        results = []
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            def enum_proc(hWnd, lParam):
                try:
                    if not user32.IsWindowVisible(hWnd):
                        return True
                    length = user32.GetWindowTextLengthW(hWnd)
                    if length == 0:
                        return True
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hWnd, buff, length + 1)
                    title = buff.value
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hWnd, ctypes.byref(pid))
                    results.append({'hwnd': int(hWnd), 'pid': int(pid.value), 'title': title})
                    return True
                except Exception:
                    return True

            user32.EnumWindows(enum_proc, 0)
        except Exception:
            return []
        return results

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

    # --------- Temp capture lifecycle ---------
    def _finalize_template_assets(self):
        """Move any temp-captured images into assets and make paths project-relative before saving."""
        try:
            for m in self.monsters:
                templates = m.get('templates', []) or []
                for t in templates:
                    p = (t.get('path') or '').strip()
                    if not p:
                        continue
                    abs_p = self._normalize_to_abs(p)
                    if self._is_under(abs_p, self.tmp_capture_dir):
                        # Move to assets with unique name
                        dest_name = self._unique_asset_name(m.get('name',''), t.get('name',''), abs_p.suffix)
                        dest = self.assets_mon_dir / dest_name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            shutil.move(str(abs_p), str(dest))
                        except Exception:
                            shutil.copy2(str(abs_p), str(dest))
                            try:
                                abs_p.unlink()
                            except Exception:
                                pass
                        # Update path to project-relative
                        t['path'] = self._make_rel_to_project(dest)
                        try:
                            self._session_temp_images.discard(str(abs_p))
                        except Exception:
                            pass
                    elif self._is_under(abs_p, self.project_root):
                        # Ensure project assets keep relative paths
                        t['path'] = self._make_rel_to_project(abs_p)
        except Exception:
            # Do not fail apply on asset move errors; saving may still proceed
            pass

    def _cleanup_temp_captures(self):
        """Delete any session temporary captures when user discards changes."""
        try:
            for p in list(self._session_temp_images):
                try:
                    pp = Path(p)
                    if pp.exists():
                        pp.unlink()
                except Exception:
                    pass
            self._session_temp_images.clear()
            # Also scan current in-memory templates for temp paths
            for m in self.monsters:
                for t in m.get('templates', []) or []:
                    p = (t.get('path') or '').strip()
                    if not p:
                        continue
                    abs_p = self._normalize_to_abs(p)
                    if self._is_under(abs_p, self.tmp_capture_dir) and abs_p.exists():
                        try:
                            abs_p.unlink()
                        except Exception:
                            pass
        except Exception:
            pass

    # --------- Utility: sanitize filenames ---------
    def _sanitize_filename(self, name: str) -> str:
        name = name.strip().lower()
        name = re.sub(r"[^a-z0-9\-_. ]+", "", name)
        name = name.replace(" ", "_")
        return name or "template"

    # --------- Overlay for region selection ---------
    class _RegionCaptureOverlay(tk.Toplevel):
        def __init__(self, parent, restrict_bbox: Optional[tuple[int,int,int,int]] = None):
            super().__init__(parent)
            self.parent = parent
            self.withdraw()
            self.overrideredirect(True)
            self.attributes('-topmost', True)
            try:
                self.attributes('-alpha', 0.25)
            except Exception:
                pass
            self.configure(bg='black')
            # Fullscreen size
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            # Canvas to draw selection
            # Use a valid background color; empty string can raise 'unknown color name'
            self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, cursor='crosshair')
            self.canvas.pack(fill='both', expand=True)
            # State
            self._start = None
            self._rect = None
            self._bbox = None
            self._restrict = restrict_bbox  # screen-coord bbox restriction
            self._guide = None
            self._size_text = None
            # Bindings
            self.canvas.bind('<ButtonPress-1>', self._on_press)
            self.canvas.bind('<B1-Motion>', self._on_drag)
            self.canvas.bind('<ButtonRelease-1>', self._on_release)
            self.bind('<Escape>', lambda e: self._cancel())

            # Draw restriction guide if provided
            if self._restrict:
                x0, y0, x1, y1 = self._restrict
                self._guide = self.canvas.create_rectangle(x0, y0, x1, y1, outline='#FFA000', width=2)

        def show_modal(self):
            self.deiconify()
            self.grab_set()
            self.focus_force()
            self.wait_window(self)
            return self._bbox

        def _on_press(self, event):
            self._start = (event.x, event.y, event.x_root, event.y_root)
            if self._rect is not None:
                self.canvas.delete(self._rect)
                self._rect = None
            self._rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='#00E5FF', width=2)
            if self._size_text:
                self.canvas.delete(self._size_text)
                self._size_text = None

        def _on_drag(self, event):
            if self._start and self._rect:
                x0, y0, _, _ = self._start
                x1, y1 = event.x, event.y
                # Clamp to restriction if any
                if self._restrict:
                    rx0, ry0, rx1, ry1 = self._restrict
                    x1 = max(rx0, min(rx1, x1))
                    y1 = max(ry0, min(ry1, y1))
                    x0 = max(rx0, min(rx1, x0))
                    y0 = max(ry0, min(ry1, y0))
                self.canvas.coords(self._rect, x0, y0, x1, y1)
                # Live size label
                w = abs(x1 - x0)
                h = abs(y1 - y0)
                label = f"{w} x {h}"
                if self._size_text:
                    self.canvas.delete(self._size_text)
                self._size_text = self.canvas.create_text(x1 + 10, y1 + 10, text=label, fill='white', anchor='nw')

        def _on_release(self, event):
            if not self._start:
                self.destroy()
                return
            x0, y0, xr0, yr0 = self._start
            x1, y1 = event.x, event.y
            # Convert to screen coords using root deltas
            dx = xr0 - x0
            dy = yr0 - y0
            sx0 = x0 + dx
            sy0 = y0 + dy
            sx1 = x1 + dx
            sy1 = y1 + dy
            # Clamp to restriction if provided
            if self._restrict:
                rx0, ry0, rx1, ry1 = self._restrict
                sx0 = max(rx0, min(rx1, sx0))
                sy0 = max(ry0, min(ry1, sy0))
                sx1 = max(rx0, min(rx1, sx1))
                sy1 = max(ry0, min(ry1, sy1))
            left = int(min(sx0, sx1))
            top = int(min(sy0, sy1))
            right = int(max(sx0, sx1))
            bottom = int(max(sy0, sy1))
            # Minimum size safeguard
            if right - left < 5 or bottom - top < 5:
                self._bbox = None
            else:
                self._bbox = (left, top, right, bottom)
            self.destroy()

        def _cancel(self):
            self._bbox = None
            self.destroy()
    
    def _t(self, key: str) -> str:
        """
        Get translated string for current language.
        
        Args:
            key: Translation key
            
        Returns:
            Translated string, or key if not found
        """
        translations = {
            'en': {
                'library_manager_title': 'Library Manager',
                'tab_monsters': 'Monster Library',
                'tab_skills': 'Skill Library',
                'tab_timing': 'Timing Calculator',
                'btn_apply_all': 'Apply All Changes',
                'btn_close': 'Close',
                'btn_calculate': 'Calculate Timing',
                'changes_pending': 'You have unsaved changes. Apply them?',
                'confirm_title': 'Unsaved Changes',
                'changes_applied': 'All changes have been applied successfully!',
                'success_title': 'Success',
            },
            'vi': {
                'library_manager_title': 'Quản Lý Thư Viện',
                'tab_monsters': 'Thư Viện Quái Vật',
                'tab_skills': 'Thư Viện Kỹ Năng',
                'tab_timing': 'Tính Toán Thời Gian',
                'btn_apply_all': 'Áp Dụng Tất Cả',
                'btn_close': 'Đóng',
                'btn_calculate': 'Tính Toán Thời Gian',
                'changes_pending': 'Bạn có thay đổi chưa lưu. Áp dụng chúng?',
                'confirm_title': 'Thay Đổi Chưa Lưu',
                'changes_applied': 'Tất cả thay đổi đã được áp dụng thành công!',
                'success_title': 'Thành Công',
            }
        }
        return translations.get(self.lang, {}).get(key, key)
    
    def _center_window(self):
        """Center window on parent."""
        self.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get window size
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        """Build the main UI with tabs and buttons."""
        # Main container
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Global top action bar (outside tabs) - top-right Apply All / Cancel
        top_bar = tk.Frame(main_frame, bg='#F5F5F5', height=44)
        top_bar.pack(fill='x', side='top', pady=(0, 8))
        top_bar.pack_propagate(False)
        # Spacer label left as title
        tk.Label(top_bar, text=self._t('library_manager_title'), bg='#F5F5F5', fg='#424242', font=('Segoe UI', 12, 'bold')).pack(side='left', padx=8)
        # Right-aligned actions
        tk.Button(top_bar, text=self._t('btn_close'), command=self._on_window_close, bg='#757575', fg='white', relief='flat', padx=12, pady=6).pack(side='right', padx=(6, 10), pady=6)
        tk.Button(top_bar, text=self._t('btn_apply_all'), command=self._apply_all_changes, bg='#2E7D32', fg='white', relief='flat', padx=12, pady=6).pack(side='right', padx=6, pady=6)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Tab 1: Monster Library
        self.monster_tab = tk.Frame(self.notebook)
        self.notebook.add(self.monster_tab, text=self._t('tab_monsters'))
        self._build_monster_tab(self.monster_tab)
        
        # Tab 2: Skill Library
        self.skill_tab = tk.Frame(self.notebook)
        self.notebook.add(self.skill_tab, text=self._t('tab_skills'))
        self._build_skill_tab(self.skill_tab)
        
        # Tab 3: Timing Calculator
        self.timing_tab = tk.Frame(self.notebook)
        self.notebook.add(self.timing_tab, text=self._t('tab_timing'))
        self._build_timing_tab(self.timing_tab)
        
        # Bottom buttons removed per new UX (actions moved to form title bar)
    
    def _build_monster_tab(self, parent: tk.Frame):
        """
        Build Monster Library tab with left list, inline edit form, and template manager.
        """
        # Main container
        main_container = tk.Frame(parent, bg='#F5F5F5')
        main_container.pack(fill='both', expand=True)

        # Layout: left list (2) | right area (10)
        main_container.grid_columnconfigure(0, weight=2, uniform='column')
        main_container.grid_columnconfigure(1, weight=10, uniform='column')
        main_container.grid_rowconfigure(0, weight=1)

        # Left: Monster List
        left_frame = tk.Frame(main_container, bg='#FFFFFF')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)

        # Header for the left list: remove title/icon, keep only the Add button.
        # Use a contrasting light background so the green Add button stands out.
        header = tk.Frame(left_frame, bg='#FFFDE7', height=44)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Button(
            header,
            text=('Add' if self.lang=='en' else 'Thêm'),
            command=self._add_monster,
            bg='#4CAF50', fg='white', relief='flat',
            font=self.ui_font_button, padx=self.ui_btn_padx, pady=self.ui_btn_pady,
            cursor='hand2'
        ).pack(side='right', padx=10, pady=6)

        # Search bar
        search_frame = tk.Frame(left_frame, bg='#FFFFFF', pady=12, padx=15)
        search_frame.pack(fill='x')
        search_container = tk.Frame(search_frame, bg='#F5F5F5', highlightbackground='#E0E0E0', highlightthickness=1)
        search_container.pack(fill='x')
        search_icon = icon_helper.get_text('search', '') if icon_helper else '🔍'
        tk.Label(search_container, text=search_icon, font=('Segoe UI', 11), bg='#F5F5F5', fg='#757575').pack(side='left', padx=(10, 5))
        self.monster_search_var = tk.StringVar()
        self.monster_search_var.trace('w', lambda *args: self._filter_monster_list())
        tk.Entry(search_container, textvariable=self.monster_search_var, font=('Segoe UI', 10), border=0, bg='#F5F5F5', fg='#212121').pack(side='left', fill='x', expand=True, pady=10, padx=(0, 10))

        # Treeview (name only)
        list_frame = tk.Frame(left_frame, bg='#FFFFFF')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 12))
        vsb = tk.Scrollbar(list_frame, orient='vertical')
        hsb = tk.Scrollbar(list_frame, orient='horizontal')
        self.monster_tree = ttk.Treeview(list_frame, columns=(), show='tree', yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode='browse')
        vsb.config(command=self.monster_tree.yview)
        hsb.config(command=self.monster_tree.xview)
        self.monster_tree.heading('#0', text='Name' if self.lang == 'en' else 'Tên')
        self.monster_tree.column('#0', width=240, minwidth=150)
        self.monster_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        self.monster_tree.bind('<<TreeviewSelect>>', self._on_monster_select)

        # Right composite area: row1 details/edit, row2 template list/editor
        right_area = tk.Frame(main_container, bg='#FFFFFF')
        right_area.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        right_area.grid_rowconfigure(0, weight=1)
        right_area.grid_rowconfigure(1, weight=1)
        right_area.grid_columnconfigure(0, weight=1)

        # Row1: details (top-right actions moved to global top bar)
        row1 = tk.Frame(right_area, bg='#FFFFFF')
        row1.grid(row=0, column=0, sticky='nsew')
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_rowconfigure(1, weight=1)
        # Title bar (no actions here)
        action_bar = tk.Frame(row1, bg='#E3F2FD', height=44)
        action_bar.grid(row=0, column=0, sticky='ew')
        action_bar.grid_propagate(False)
        tk.Label(action_bar, text=('Monster Editor' if self.lang=='en' else 'Chỉnh Sửa Quái'), bg='#E3F2FD', fg='#0D47A1', font=self.ui_font_title).pack(side='left', padx=12)
        # Details panel
        self.details_panel = tk.Frame(row1, bg='#FFFFFF')
        self.details_panel.grid(row=1, column=0, sticky='nsew', padx=0)

        row2 = tk.Frame(right_area, bg='#FFFFFF')
        row2.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        # Three columns: list | preview | edit (weights: 2 | 4 | 6)
        row2.grid_columnconfigure(0, weight=2, uniform='row2')
        row2.grid_columnconfigure(1, weight=4, uniform='row2')
        row2.grid_columnconfigure(2, weight=6, uniform='row2')
        row2.grid_rowconfigure(0, weight=1)
        self.template_list_panel = tk.Frame(row2, bg='#FFFFFF')
        self.template_list_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        self.template_preview_panel = tk.Frame(row2, bg='#FFFFFF')
        self.template_preview_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 5))
        self.template_edit_panel = tk.Frame(row2, bg='#FFFFFF')
        self.template_edit_panel.grid(row=0, column=2, sticky='nsew', padx=(5, 0))

        # Initial renders: populate list then auto-select first monster and its first template
        self._refresh_monster_tree()
        # Auto-select first monster if available
        try:
            first = self.monster_tree.get_children()
            if first:
                self.monster_tree.selection_set(first[0])
                self.monster_tree.focus(first[0])
                self._on_monster_select(None)
            else:
                self._show_monster_details(None)
                self._show_template_editor(None)
        except Exception:
            # Fallback to empty state
            self._show_monster_details(None)
            self._show_template_editor(None)
    
    def _filter_monster_list(self):
        """Filter monster list based on search text."""
        search_text = self.monster_search_var.get().lower()
        
        # Clear tree
        for item in self.monster_tree.get_children():
            self.monster_tree.delete(item)
        
        # Re-add filtered monsters
        for monster in self.monsters:
            name = monster.get('name', '')
            if search_text in name.lower():
                self._add_monster_to_tree(monster)
    
    def _refresh_monster_tree(self):
        """Refresh the monster tree with current data."""
        # Clear tree
        for item in self.monster_tree.get_children():
            self.monster_tree.delete(item)
        
        # Add all monsters
        for monster in self.monsters:
            self._add_monster_to_tree(monster)
    
    def _add_monster_to_tree(self, monster: dict):
        """Add a single monster to the tree."""
        name = monster.get('name', 'Unknown')
        self.monster_tree.insert(
            '',
            'end',
            text=f"  {name}",
            tags=('monster',)
        )
    
    def _on_monster_select(self, event):
        """Handle monster selection in tree."""
        selection = self.monster_tree.selection()
        if not selection:
            self._show_monster_details(None)
            return
        
        # Get selected item index
        item = selection[0]
        item_index = self.monster_tree.index(item)
        
        # Always show edit form for selected monster
        if 0 <= item_index < len(self.monsters):
            self._monster_edit_open = True
            self._show_monster_details(self.monsters[item_index])
    
    def _show_monster_details(self, monster: Optional[dict]):
        """
        Show monster information in a clean label/value grid (no card).
        Includes an inline Edit button that opens the inline form.
        """
        # Clear current content
        if hasattr(self, 'details_panel'):
            for w in self.details_panel.winfo_children():
                w.destroy()

        if monster is None:
            tk.Label(self.details_panel, text='← ' + ('Select a monster to edit' if self.lang=='en' else 'Chọn quái để sửa'),
                     bg='#FFFFFF', fg='#9E9E9E', font=self.ui_font_label).pack(padx=18, pady=18, anchor='w')
            return

        # Store current and render edit form directly
        self.current_monster = monster
        self._render_monster_edit_form(self.details_panel)
        # Keep template editor in sync (right panel)
        self._show_template_editor(monster)

    def _render_monster_edit_form(self, parent: tk.Frame):
        """Render the inline monster edit form directly under details (middle column)."""
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            return
        form = tk.Frame(parent, bg='#E3F2FD', highlightbackground='#2196F3', highlightthickness=2)
        form.pack(fill='both', expand=False, pady=(12, 0))

        # Title
        title = tk.Frame(form, bg='#2196F3', height=36)
        title.pack(fill='x')
        title.pack_propagate(False)
        tk.Label(
            title,
            text='✏️ ' + ('Edit Monster' if self.lang=='en' else 'Sửa Quái'),
            bg='#2196F3',
            fg='white',
            font=self.ui_font_section
        ).pack(padx=10, pady=6)

        body = tk.Frame(form, bg='#E3F2FD')
        body.pack(fill='both', expand=True, padx=14, pady=12)

        # Fields (store on self for header actions)
        self.mon_name_var = tk.StringVar(value=self.current_monster.get('name',''))
        self.mon_hp_var = tk.StringVar(value=str(self.current_monster.get('hp',0)))
        self.mon_dmg_var = tk.StringVar(value=str(self.current_monster.get('damage_per_hit',0)))
        self.mon_prio_var = tk.StringVar(value=str(self.current_monster.get('priority',1)))

        tk.Label(body, text=('Name' if self.lang=='en' else 'Tên'), bg='#E3F2FD', font=self.ui_font_label).grid(row=0, column=0, sticky='w', pady=(0,6))
        tk.Entry(body, textvariable=self.mon_name_var, font=self.ui_font_text).grid(row=0, column=1, sticky='ew', pady=(0,6))

        tk.Label(body, text='HP', bg='#E3F2FD', font=self.ui_font_label).grid(row=1, column=0, sticky='w')
        tk.Entry(body, textvariable=self.mon_hp_var, width=12, font=self.ui_font_text).grid(row=1, column=1, sticky='w')

        tk.Label(body, text=('Damage' if self.lang=='en' else 'Sát thương'), bg='#E3F2FD', font=self.ui_font_label).grid(row=1, column=2, sticky='w', padx=(12,0))
        tk.Entry(body, textvariable=self.mon_dmg_var, width=12, font=self.ui_font_text).grid(row=1, column=3, sticky='w')

        tk.Label(body, text=('Priority' if self.lang=='en' else 'Ưu tiên'), bg='#E3F2FD', font=self.ui_font_label).grid(row=2, column=0, sticky='w', pady=(6,0))
        tk.Entry(body, textvariable=self.mon_prio_var, width=8, font=self.ui_font_text).grid(row=2, column=1, sticky='w', pady=(6,0))

        tk.Label(body, text=('Description' if self.lang=='en' else 'Mô tả'), bg='#E3F2FD', font=self.ui_font_label).grid(row=3, column=0, sticky='w', pady=(8,0))
        self.mon_desc_text = tk.Text(body, height=4, font=self.ui_font_text)
        self.mon_desc_text.grid(row=3, column=1, columnspan=3, sticky='ew')
        self.mon_desc_text.insert('1.0', self.current_monster.get('description',''))

        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(3, weight=0)

        # No inline buttons here; use header actions (Apply/Delete/Cancel/Apply All)
    
    def _estimate_kill_time(self, monster: dict) -> str:
        """Estimate time to kill monster based on HP and damage."""
        hp = monster.get('hp', 0)
        damage = monster.get('damage_per_hit', 500)  # Assume player damage
        
        if hp <= 0 or damage <= 0:
            return 'N/A'
        
        hits = hp / damage
        seconds = hits * 1.5  # Assume 1.5s per hit
        
        if seconds < 60:
            return f"{seconds:.0f}s"
        else:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
    
    def _add_monster(self):
        """Open dialog to add new monster."""
        dialog = MonsterDialog(self, self.lang, mode='add')
        
        if dialog.result:
            # Add new monster
            self.monsters.append(dialog.result)
            self.changes_made['monsters_changed'] = True
            
            # Refresh tree
            self._refresh_monster_tree()
            
            # Status message
            messagebox.showinfo(
                'Added' if self.lang == 'en' else 'Đã Thêm',
                f"Monster '{dialog.result.get('name', 'Unknown')}' has been added." if self.lang == 'en'
                else f"Quái '{dialog.result.get('name', 'Unknown')}' đã được thêm."
            )
    
    def _edit_monster(self):
        """Open dialog to edit selected monster."""
        selection = self.monster_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a monster to edit.' if self.lang == 'en' else 'Vui lòng chọn quái để sửa.'
            )
            return
        
        item_index = self.monster_tree.index(selection[0])
        monster = self.monsters[item_index]
        
        # Open edit dialog
        dialog = MonsterDialog(self, self.lang, mode='edit', monster=monster)
        
        if dialog.result:
            # Update monster
            self.monsters[item_index] = dialog.result
            self.changes_made['monsters_changed'] = True
            
            # Refresh tree
            self._refresh_monster_tree()
            
            # Status message
            messagebox.showinfo(
                'Updated' if self.lang == 'en' else 'Đã Cập Nhật',
                f"Monster '{dialog.result.get('name', 'Unknown')}' has been updated." if self.lang == 'en'
                else f"Quái '{dialog.result.get('name', 'Unknown')}' đã được cập nhật."
            )
    
    def _edit_monster_inline(self):
        """Edit selected monster inline (no popup dialog)."""
        selection = self.monster_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a monster to edit.' if self.lang == 'en' else 'Vui lòng chọn quái để sửa.'
            )
            return
        # Ensure current monster is set based on selection
        item_index = self.monster_tree.index(selection[0])
        if 0 <= item_index < len(self.monsters):
            self.current_monster = self.monsters[item_index]
        # Show inline form
        self._show_monster_edit_inline()
    
    def _lighten_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Lighten a hex color by a factor (0-1)."""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _delete_monster(self):
        """Delete selected monster."""
        selection = self.monster_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a monster to delete.' if self.lang == 'en' else 'Vui lòng chọn quái để xóa.'
            )
            return
        
        item_index = self.monster_tree.index(selection[0])
        monster = self.monsters[item_index]
        
        # Confirm deletion
        response = messagebox.askyesno(
            'Confirm Delete' if self.lang == 'en' else 'Xác Nhận Xóa',
            f"Delete monster '{monster.get('name', 'Unknown')}'?\n\nThis cannot be undone." if self.lang == 'en' 
            else f"Xóa quái '{monster.get('name', 'Unknown')}'?\n\nHành động này không thể hoàn tác."
        )
        
        if response:
            # Delete monster
            del self.monsters[item_index]
            self.changes_made['monsters_changed'] = True
            
            # Refresh tree
            name_var = tk.StringVar(value=self.current_monster.get('name', ''))
            hp_var = tk.StringVar(value=str(self.current_monster.get('hp', 0)))
            dmg_var = tk.StringVar(value=str(self.current_monster.get('damage_per_hit', 0)))
            prio_var = tk.StringVar(value=str(self.current_monster.get('priority', 1)))
            
            # Status message
            messagebox.showinfo(
                'Deleted' if self.lang == 'en' else 'Đã Xóa',
                f"Monster '{monster.get('name', 'Unknown')}' has been deleted." if self.lang == 'en'
                else f"Quái '{monster.get('name', 'Unknown')}' đã được xóa."
            )
    
    def _duplicate_monster(self):
        """Duplicate selected monster."""
        selection = self.monster_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a monster to duplicate.' if self.lang == 'en' else 'Vui lòng chọn quái để nhân bản.'
            )
            return
        
        item_index = self.monster_tree.index(selection[0])
        original = self.monsters[item_index]
        
        # Create copy
        import copy
        duplicate = copy.deepcopy(original)
        duplicate['name'] = f"{original.get('name', 'Unknown')} (Copy)"
        
        # Add to list
        self.monsters.append(duplicate)
        self.changes_made['monsters_changed'] = True
        
        # Refresh tree
        self._refresh_monster_tree()
        
        # Status message
        messagebox.showinfo(
            'Duplicated' if self.lang == 'en' else 'Đã Nhân Bản',
            f"Monster '{original.get('name', 'Unknown')}' has been duplicated." if self.lang == 'en'
            else f"Quái '{original.get('name', 'Unknown')}' đã được nhân bản."
        )
    
    # ==================== Template Management Methods ====================
    
    def _show_template_editor(self, monster: Optional[dict]):
        """
        Row 2 layout:
        - Left column: template list + actions
        - Right column: template edit form and preview/info (preview width fixed to 200)
        """
        # Clear panels
        if hasattr(self, 'template_list_panel'):
            for w in self.template_list_panel.winfo_children():
                w.destroy()
        if hasattr(self, 'template_preview_panel'):
            for w in self.template_preview_panel.winfo_children():
                w.destroy()
        if hasattr(self, 'template_edit_panel'):
            for w in self.template_edit_panel.winfo_children():
                w.destroy()

        if monster is None:
            # Show empty hints
            tk.Label(self.template_list_panel, text='👈', font=('Arial', 36), bg='#FFFFFF', fg='#DDD').pack(pady=(40, 6))
            tk.Label(self.template_list_panel, text=('Select a monster to view templates' if self.lang=='en' else 'Chọn quái để xem template'), bg='#FFFFFF', fg='#999').pack()
            return

        self.current_monster = monster
        templates = monster.get('templates', [])

        # Left: header + list + buttons
        header_frame = tk.Frame(self.template_list_panel, bg='#FFFFFF')
        header_frame.pack(fill='x', padx=10, pady=(5, 5))
        tk.Label(header_frame, text=f"{len(templates)} " + ('Templates' if self.lang=='en' else 'Mẫu hình'), font=('Arial', 10, 'bold'), bg='#FFFFFF', fg='#424242').pack(side='left')

        list_frame = tk.Frame(self.template_list_panel, bg='#FFFFFF')
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 8))
        vsb = tk.Scrollbar(list_frame, orient='vertical')
        # Only show thumbnail + name; use #0 for thumbnail image, one column for name
        columns = ('name',)
        try:
            style = ttk.Style(self)
            style.configure('Template.Treeview', rowheight=32)
        except Exception:
            pass
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', yscrollcommand=vsb.set, selectmode='browse', height=8, style='Template.Treeview')
        vsb.config(command=self.template_tree.yview)
        # Thumbnail column (#0) fixed width ~40px, and name column flexible
        self.template_tree.heading('#0', text='')
        self.template_tree.heading('name', text='Template' if self.lang=='en' else 'Template')
        self.template_tree.column('#0', width=40, minwidth=40, stretch=False)
        self.template_tree.column('name', width=200, minwidth=120)
        self.template_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        for idx, template in enumerate(templates):
            name = template.get('name', f'Template {idx+1}')
            image_obj = None
            full_path = template.get('path')
            # Resolve relative to project root if needed
            if full_path and not os.path.isabs(full_path):
                full_path = str((self.project_root / full_path).resolve())
            if full_path and os.path.exists(full_path) and self.pil_available:
                try:
                    photo = self._thumb_cache.get(full_path)
                    if photo is None:
                        img = Image.open(full_path)  # type: ignore[attr-defined]
                        img.thumbnail((32, 32))
                        photo = ImageTk.PhotoImage(img)  # type: ignore[attr-defined]
                        self._thumb_cache[full_path] = photo
                    image_obj = photo
                except Exception:
                    image_obj = None
            if image_obj is not None:
                self.template_tree.insert('', 'end', text='', image=image_obj, values=(name,))
            else:
                self.template_tree.insert('', 'end', text='', values=(name,))

        self.template_tree.bind('<<TreeviewSelect>>', self._on_template_tree_select)

        # No buttons in list panel per spec; moved to edit panel
        # Guidance under list header
        tk.Label(self.template_list_panel, text=(
            'Nhấp để chọn template. Kéo danh sách để xem thêm.' if self.lang=='vi' else 'Click to select a template. Scroll to see more.'
        ), bg='#FFFFFF', fg='#757575', font=('Arial', 8), anchor='w').pack(fill='x', padx=10, pady=(0,4))

        # Middle: preview (fixed height 300) + template name only
        preview_frame = tk.Frame(self.template_preview_panel, bg='#FFFFFF')
        preview_frame.pack(fill='both', expand=True)
        self.template_name_label = tk.Label(preview_frame, text='', font=('Arial', 10, 'bold'), bg='#FFFFFF', fg='#424242')
        self.template_name_label.pack(anchor='n', padx=10, pady=(10, 6))
        self.template_preview_label = tk.Label(preview_frame, bg='#FAFAFA', relief='solid')
        self.template_preview_label.pack(anchor='n', padx=10, pady=(0, 8))

        # Right: edit panel with toolbar + inline form (created but not packed until used)
        edit_toolbar = tk.Frame(self.template_edit_panel, bg='#F5F5F5')
        edit_toolbar.pack(fill='x', padx=10, pady=(10, 0))
        # Right-align with 4px margins
        tk.Button(edit_toolbar, text='🗑️ ' + ('Delete' if self.lang=='en' else 'Xóa'), command=self._delete_template_inline, bg='#F44336', fg='white', relief='flat', padx=12, pady=6, font=('Arial', 9, 'bold')).pack(side='right', padx=4, pady=4)
        tk.Button(edit_toolbar, text='✏️ ' + ('Edit' if self.lang=='en' else 'Sửa'), command=self._edit_template_inline, bg='#1976D2', fg='white', relief='flat', padx=12, pady=6, font=('Arial', 9, 'bold')).pack(side='right', padx=4, pady=4)
        tk.Button(edit_toolbar, text='➕ ' + ('Add' if self.lang=='en' else 'Thêm'), command=self._add_template_inline, bg='#4CAF50', fg='white', relief='flat', padx=12, pady=6, font=('Arial', 9, 'bold')).pack(side='right', padx=4, pady=4)

        # Small guidance hint below toolbar
        hint_txt = ('Chọn một template để xem trước và sửa. Dùng Thêm/Sửa/Xóa ở góc phải.' if self.lang=='vi' else 'Select a template to preview and edit. Use Add/Edit/Delete on the top-right.')
        tk.Label(self.template_edit_panel, text=hint_txt, bg='#FFFFFF', fg='#757575', font=('Arial', 8)).pack(fill='x', padx=12, pady=(4, 0))

        # Inline template form
        self.template_form_frame = tk.Frame(self.template_edit_panel, bg='#E3F2FD', relief='flat', borderwidth=0, highlightbackground='#2196F3', highlightthickness=2)

        # Title
        form_title_frame = tk.Frame(self.template_form_frame, bg='#2196F3', height=45)
        form_title_frame.pack(fill='x')
        form_title_frame.pack_propagate(False)
        self.form_title_label = tk.Label(form_title_frame, text='', font=('Arial', 11, 'bold'), bg='#2196F3', fg='white')
        self.form_title_label.pack(pady=12, padx=15, side='left')
        # Unsaved badge (initially hidden)
        try:
            self.unsaved_badge = tk.Label(form_title_frame, text='', bg='#FF7043', fg='white', font=('Arial', 9, 'bold'))
            self.unsaved_badge.place_forget()
        except Exception:
            self.unsaved_badge = None

        form_body = tk.Frame(self.template_form_frame, bg='#E3F2FD')
        form_body.pack(fill='both', expand=True, padx=20, pady=15)
        name_frame = tk.Frame(form_body, bg='#E3F2FD'); name_frame.pack(fill='x', pady=(0, 12))
        tk.Label(name_frame, text=('Template Name' if self.lang=='en' else 'Tên Template'), bg='#E3F2FD', font=('Arial', 9, 'bold'), fg='#424242', anchor='w').pack(fill='x', pady=(0,4))
        self.template_name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.template_name_var, font=('Arial', 10), relief='solid', borderwidth=1).pack(fill='x', ipady=6)
        # Guidance for name
        tk.Label(name_frame, text=('Tên hiển thị của mẫu hình.' if self.lang=='vi' else 'Display name for this template.'), bg='#E3F2FD', fg='#757575', font=('Arial', 8), anchor='w').pack(fill='x', pady=(4,0))

        path_frame = tk.Frame(form_body, bg='#E3F2FD'); path_frame.pack(fill='x', pady=(0, 12))
        tk.Label(path_frame, text=('Image Path' if self.lang=='en' else 'Đường Dẫn Ảnh'), bg='#E3F2FD', font=('Arial', 9, 'bold'), fg='#424242', anchor='w').pack(fill='x', pady=(0,4))
        path_input_frame = tk.Frame(path_frame, bg='#E3F2FD'); path_input_frame.pack(fill='x')
        self.template_path_var = tk.StringVar()
        tk.Entry(path_input_frame, textvariable=self.template_path_var, font=('Arial', 9), state='readonly', fg='#666', relief='solid', borderwidth=1).pack(side='left', fill='x', expand=True, ipady=6)
        # Browse and Capture inline
        tools_frame = tk.Frame(path_input_frame, bg='#E3F2FD')
        tools_frame.pack(side='right')
        tk.Button(tools_frame, text='📁 ' + ('Browse' if self.lang=='en' else 'Chọn'), command=self._browse_template_image, font=('Arial', 9), bg='#757575', fg='white', relief='flat', padx=10, pady=6, cursor='hand2').pack(side='left', padx=(5,0))
        # Keep only screenshot capture per spec
        tk.Button(tools_frame, text='📸 ' + ('Capture' if self.lang=='en' else 'Chụp'), command=lambda: self._capture_into_path_var(window=False), font=('Arial', 9), bg='#9C27B0', fg='white', relief='flat', padx=10, pady=6, cursor='hand2').pack(side='left', padx=(5,0))
        # Guidance for path/capture
        tk.Label(path_frame, text=('Chọn file ảnh hoặc bấm Chụp để lấy ảnh từ màn hình.' if self.lang=='vi' else 'Pick an image file or use Capture to grab from screen.'), bg='#E3F2FD', fg='#757575', font=('Arial', 8), anchor='w').pack(fill='x', pady=(4,0))

        threshold_frame = tk.Frame(form_body, bg='#E3F2FD'); threshold_frame.pack(fill='x', pady=(0,12))
        tk.Label(threshold_frame, text=('Match Threshold' if self.lang=='en' else 'Ngưỡng Khớp'), bg='#E3F2FD', font=('Arial', 9, 'bold'), fg='#424242', anchor='w').pack(fill='x', pady=(0,4))
        threshold_input_frame = tk.Frame(threshold_frame, bg='#E3F2FD'); threshold_input_frame.pack(fill='x')
        self.template_threshold_var = tk.StringVar(value='0.85')
        tk.Entry(threshold_input_frame, textvariable=self.template_threshold_var, font=('Arial', 10), width=12, relief='solid', borderwidth=1).pack(side='left', ipady=6)
        tk.Label(threshold_input_frame, text='  (0.0 - 1.0)', bg='#E3F2FD', fg='#757575', font=('Arial', 8)).pack(side='left', padx=5)
        # Guidance for threshold
        tk.Label(threshold_frame, text=(
            'Gợi ý: 0.80 - 0.90. Cao hơn -> ít nhận nhầm, nhưng khó khớp.' if self.lang=='vi' else 
            'Tip: 0.80 - 0.90. Higher = less false positives, but harder to match.'
        ), bg='#E3F2FD', fg='#757575', font=('Arial', 8), anchor='w').pack(fill='x', pady=(4,0))

        # No Save/Cancel buttons; changes are applied immediately and persisted with Apply All (top-right)

        # Bind auto-apply traces for form fields
        self._suspend_template_var_traces = False
        try:
            self.template_name_var.trace('w', lambda *args: self._on_template_name_change())
            self.template_path_var.trace('w', lambda *args: self._on_template_path_change())
            self.template_threshold_var.trace('w', lambda *args: self._on_template_threshold_change())
        except Exception:
            pass

        # Initial empty preview
        self._update_template_preview(None)
        # Auto-select first template if exists
        try:
            items = self.template_tree.get_children()
            if items:
                self.template_tree.selection_set(items[0])
                self.template_tree.focus(items[0])
                self._on_template_tree_select(None)
        except Exception:
            pass
    
    def _on_template_tree_select(self, event):
        """Handle template selection: show preview and open inline edit immediately."""
        selection = self.template_tree.selection()
        if not selection:
            self._update_template_preview(None)
            return
        item = selection[0]
        idx = self.template_tree.index(item)
        templates = self.current_monster.get('templates', []) if hasattr(self, 'current_monster') else []
        if idx >= len(templates):
            self._update_template_preview(None)
            return
        template = templates[idx]
        self._update_template_preview(template)
        # Immediately populate inline edit form
        self.template_form_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        self.form_title_label.config(text='✏️ ' + ('Edit Template' if self.lang == 'en' else 'Sửa Template'))
        # Suspend traces while populating fields
        self._suspend_template_var_traces = True
        try:
            self.template_name_var.set(template.get('name', ''))
            self.template_path_var.set(template.get('path', ''))
            self.template_threshold_var.set(str(template.get('threshold', 0.85)))
        finally:
            self._suspend_template_var_traces = False
        self.template_form_mode = 'edit'
        self.template_form_edit_index = idx
        # Reset unsaved badge view based on current change state
        try:
            self._mark_unsaved(any(self.changes_made.values()))
        except Exception:
            pass

    # === Auto-apply bindings for template form ===
    def _get_current_template_ref(self) -> Optional[dict]:
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            return None
        templates = self.current_monster.get('templates', [])
        if not templates:
            return None
        # Prefer selected index if available; else use first
        try:
            sel = self.template_tree.selection()
            if sel:
                idx = self.template_tree.index(sel[0])
                if 0 <= idx < len(templates):
                    return templates[idx]
        except Exception:
            pass
        return templates[0]

    def _on_template_name_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        tmpl['name'] = self.template_name_var.get().strip()
        self.changes_made['monsters_changed'] = True
        try:
            self._mark_unsaved(True)
        except Exception:
            pass
        # Update name label and tree text
        if hasattr(self, 'template_name_label'):
            self.template_name_label.config(text=tmpl['name'])
        try:
            sel = self.template_tree.selection()
            if sel:
                self.template_tree.set(sel[0], 'name', tmpl['name'])
        except Exception:
            pass

    def _on_template_path_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        tmpl['path'] = self.template_path_var.get().strip()
        self.changes_made['monsters_changed'] = True
        try:
            self._mark_unsaved(True)
        except Exception:
            pass
        # Refresh preview
        self._update_template_preview(tmpl)

    def _on_template_threshold_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        val = self.template_threshold_var.get().strip()
        try:
            tmpl['threshold'] = float(val)
            self.changes_made['monsters_changed'] = True
            try:
                self._mark_unsaved(True)
            except Exception:
                pass
        except Exception:
            # Ignore invalid while typing
            pass

    # Header actions for Monster editor
    def _save_current_monster_inline(self):
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            return
        try:
            self.current_monster['name'] = self.mon_name_var.get().strip()
            self.current_monster['hp'] = int(self.mon_hp_var.get())
            self.current_monster['damage_per_hit'] = int(self.mon_dmg_var.get())
            self.current_monster['priority'] = int(self.mon_prio_var.get())
            self.current_monster['description'] = self.mon_desc_text.get('1.0','end').strip()
        except Exception as e:
            messagebox.showerror('Invalid Input', str(e))
            return
        self.changes_made['monsters_changed'] = True
        self._refresh_monster_tree()
        # Keep focus on same monster
        self._show_monster_details(self.current_monster)

    def _delete_current_monster_inline(self):
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            return
        name = self.current_monster.get('name', 'Unknown')
        title = 'Confirm Delete' if self.lang=='en' else 'Xác Nhận Xóa'
        msg = f"Delete monster '{name}'?" if self.lang=='en' else f"Xóa quái '{name}'?"
        if messagebox.askyesno(title, msg, parent=self):
            try:
                idx = self.monsters.index(self.current_monster)
            except ValueError:
                idx = -1
            if idx >= 0:
                del self.monsters[idx]
                self.changes_made['monsters_changed'] = True
                self._refresh_monster_tree()
                self._show_monster_details(None)
                self._show_template_editor(None)

    # Capture helper that fills path field (does not auto-append template)
    def _capture_into_path_var(self, window: bool = False):
        """Use shared capture helper to capture and fill the template path/name, keeping UX consistent.

        The 'window' parameter is kept for signature compatibility but currently unused by the shared helper.
        """
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            messagebox.showwarning('No Monster' if self.lang=='en' else 'Chưa Chọn Quái',
                                   'Please select a monster first.' if self.lang=='en' else 'Vui lòng chọn một quái trước.')
            return
        if capture_region_and_save is None:
            messagebox.showerror('Error' if self.lang=='en' else 'Lỗi', 'Capture helper not available.')
            return
        # Prepare a silent pre-wait hook to bring game window to front after user presses OK
        def _pre_wait_bring():
            try:
                pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
                hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
                brought = False
                if pid:
                    try:
                        brought = self._bring_window_to_front_by_pid(int(pid))
                    except Exception:
                        brought = False
                if not brought and hwnd_cfg:
                    try:
                        brought = self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
                    except Exception:
                        brought = False
            except Exception:
                pass
        parent: tk.Toplevel = self
        # Release our modal grab temporarily to avoid Tkinter grab conflicts during overlay selection
        had_grab = False
        try:
            try:
                self.grab_release()
                had_grab = True
            except Exception:
                had_grab = False
            result = capture_region_and_save(parent, self.pil_available, self.current_monster.get('name',''), self.lang, pre_wait_hook=_pre_wait_bring)
        except Exception as exc:
            messagebox.showerror('Error' if self.lang=='en' else 'Lỗi', str(exc))
            return
        finally:
            # Restore modal grab if we had one
            try:
                if had_grab:
                    self.grab_set()
            except Exception:
                pass
        if not result:
            return
        path, bbox = result
        # Stage captured image to tmp/captures (treat as temporary until Apply All)
        try:
            src = Path(path)
            current_name = self.template_name_var.get().strip() or src.stem
            temp_name = self._unique_asset_name(self.current_monster.get('name',''), current_name, src.suffix)
            dest = self.tmp_capture_dir / temp_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
            except Exception:
                shutil.copy2(str(src), str(dest))
                try:
                    src.unlink()
                except Exception:
                    pass
            path = str(dest)
            self._session_temp_images.add(str(dest))
        except Exception:
            pass
        # Update form fields
        self._suspend_template_var_traces = True
        try:
            self.template_path_var.set(path)
            if not self.template_name_var.get().strip():
                try:
                    self.template_name_var.set(Path(path).stem)
                except Exception:
                    self.template_name_var.set(os.path.basename(path))
        finally:
            self._suspend_template_var_traces = False
        # Persist to current template record (or create one if none selected)
        tmpl_ref = self._get_current_template_ref()
        if tmpl_ref is None:
            # Initialize templates and add a new one
            if not hasattr(self, 'current_monster') or self.current_monster is None:
                return
            templates = self.current_monster.setdefault('templates', [])
            new_tmpl = {
                'name': self.template_name_var.get().strip() or Path(path).stem,
                'path': path,
                'threshold': float(self.template_threshold_var.get() or 0.85)
            }
            templates.append(new_tmpl)
        else:
            tmpl_ref['name'] = self.template_name_var.get().strip() or Path(path).stem
            tmpl_ref['path'] = path
            try:
                tmpl_ref['threshold'] = float(self.template_threshold_var.get() or 0.85)
            except Exception:
                pass
        # Trigger preview and mark change
        self._update_template_preview({'name': self.template_name_var.get(), 'path': path, 'threshold': float(self.template_threshold_var.get() or 0.85)})
        self.changes_made['monsters_changed'] = True
        try:
            self._mark_unsaved(True)
        except Exception:
            pass

    def _update_template_preview(self, template: Optional[dict]):
        """Update the middle preview column: show name and a single image scaled to height=300."""
        # Ensure preview widgets exist
        if not hasattr(self, 'template_preview_label') or not hasattr(self, 'template_name_label'):
            return
        # Default state
        if not template:
            self.template_name_label.config(text='')
            self.template_preview_label.config(image='', text='No preview', font=('Arial', 10), fg='#999')
            return
        # Set name label
        self.template_name_label.config(text=template.get('name', ''))
        # Handle image
        path = template.get('path')
        # Resolve relative to project root if needed
        if path and not os.path.isabs(path):
            path = str((self.project_root / path).resolve())
        if path and os.path.exists(path) and self.pil_available:
            try:
                img = Image.open(path)  # type: ignore[attr-defined]
                # Scale to fixed height 300, preserve aspect ratio (auto width)
                w, h = img.size
                if w > 0 and h > 0:
                    target_h = 300
                    target_w = int(w * (target_h / float(h)))
                    img = img.resize((max(1, target_w), target_h), Image.LANCZOS)  # type: ignore[attr-defined]
                photo = ImageTk.PhotoImage(img)  # type: ignore[attr-defined]
                # cache to avoid GC
                self._thumb_cache[path + '_preview_h300'] = photo
                self.template_preview_label.config(image=photo, text='')
            except Exception:
                self.template_preview_label.config(image='', text='Preview not available', font=('Arial', 10), fg='#999')
        else:
            self.template_preview_label.config(image='', text='No image', font=('Arial', 10), fg='#999')

    # === Inline Monster Edit (reuse template form style) ===
    def _show_monster_edit_inline(self):
        """Toggle inline monster edit form under the details in column 2."""
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            return
        self._monster_edit_open = True
        self._show_monster_details(self.current_monster)
    
    # Removed obsolete _on_template_select (listbox-based). Using treeview selection instead.
    
    # === INLINE Template Editing Methods (NO POPUPS!) ===
    
    def _add_template_inline(self):
        """Show inline form to add new template."""
        if not hasattr(self, 'current_monster'):
            return
        # Ensure template list exists
        templates = self.current_monster.setdefault('templates', [])
        # Create a new empty template and append
        new_tmpl = {'name': 'New Template', 'path': '', 'threshold': 0.85}
        templates.append(new_tmpl)
        self.changes_made['monsters_changed'] = True
        try:
            self._mark_unsaved(True)
        except Exception:
            pass
        # Refresh the template editor to show the new item
        self._show_template_editor(self.current_monster)
        # Select the newly added item (last)
        try:
            items = self.template_tree.get_children()
            if items:
                self.template_tree.selection_set(items[-1])
                self.template_tree.focus(items[-1])
                self._on_template_tree_select(None)
        except Exception:
            pass
    
    def _edit_template_inline(self):
        """Show inline form to edit selected template."""
        if not hasattr(self, 'current_monster'):
            return
        
        # Get selection from treeview
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a template to edit.' if self.lang == 'en'
                else 'Vui lòng chọn template để sửa.'
            )
            return
        
        # Get index
        item = selection[0]
        idx = self.template_tree.index(item)
        templates = self.current_monster.get('templates', [])
        
        if idx >= len(templates):
            return
        
        template = templates[idx]
        
        # Show form (if not visible) and let selection handler populate; traces will auto-apply changes
        self.template_form_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        self.form_title_label.config(text='✏️ ' + ('Edit Template' if self.lang == 'en' else 'Sửa Template'))
    
    def _delete_template_inline(self):
        """Delete selected template (with confirmation)."""
        if not hasattr(self, 'current_monster'):
            return
        
        # Get selection
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning(
                'No Selection' if self.lang == 'en' else 'Chưa Chọn',
                'Please select a template to delete.' if self.lang == 'en'
                else 'Vui lòng chọn template để xóa.'
            )
            return
        
        # Get index
        item = selection[0]
        idx = self.template_tree.index(item)
        templates = self.current_monster.get('templates', [])
        
        if idx >= len(templates):
            return
        
        template = templates[idx]
        
        # Confirm
        response = messagebox.askyesno(
            'Confirm Delete' if self.lang == 'en' else 'Xác Nhận Xóa',
            f"Delete template '{template.get('name', 'Unknown')}'?" if self.lang == 'en'
            else f"Xóa template '{template.get('name', 'Unknown')}'?"
        )
        
        if response:
            # Remove from list
            img_path = template.get('path') or ''
            templates.pop(idx)
            self.changes_made['monsters_changed'] = True
            try:
                self._mark_unsaved(True)
            except Exception:
                pass
            # Safe delete image if not referenced elsewhere and under project dirs
            try:
                still_used = False
                if img_path:
                    for m in self.monsters:
                        for t in m.get('templates', []) or []:
                            if t is template:
                                continue
                            if (t.get('path') or '') == img_path:
                                still_used = True
                                break
                        if still_used:
                            break
                if img_path and not still_used:
                    abs_p = self._normalize_to_abs(img_path)
                    if self._is_under(abs_p, self.assets_mon_dir) or self._is_under(abs_p, self.tmp_capture_dir):
                        if abs_p.exists():
                            abs_p.unlink()
                        # Remove from temp tracking if present
                        try:
                            self._session_temp_images.discard(str(abs_p))
                        except Exception:
                            pass
            except Exception:
                pass
            
            # Refresh display
            self._show_template_editor(self.current_monster)
            self._refresh_monster_tree()
            
            # Success message
            messagebox.showinfo(
                'Deleted' if self.lang == 'en' else 'Đã Xóa',
                'Template deleted successfully.' if self.lang == 'en'
                else 'Đã xóa template.'
            )
    
    def _browse_template_image(self):
        """Browse for template image file."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title='Select Template Image' if self.lang == 'en' else 'Chọn Ảnh Template',
            filetypes=[
                ('Image files', '*.png *.jpg *.jpeg *.bmp'),
                ('All files', '*.*')
            ]
        )
        
        if file_path:
            self.template_path_var.set(file_path)
            # Auto-fill name if empty
            if not self.template_name_var.get():
                self.template_name_var.set(os.path.basename(file_path))
    
    def _save_template_form(self):
        """Save template form (add or edit mode)."""
        if not hasattr(self, 'current_monster'):
            return
        
        # Validate fields
        name = self.template_name_var.get().strip()
        path = self.template_path_var.get().strip()
        threshold_str = self.template_threshold_var.get().strip()
        
        if not name:
            messagebox.showwarning(
                'Missing Name' if self.lang == 'en' else 'Thiếu Tên',
                'Please enter a template name.' if self.lang == 'en'
                else 'Vui lòng nhập tên template.'
            )
            return
        
        if not path:
            messagebox.showwarning(
                'Missing Path' if self.lang == 'en' else 'Thiếu Đường Dẫn',
                'Please select an image file.' if self.lang == 'en'
                else 'Vui lòng chọn file ảnh.'
            )
            return
        
        # Validate threshold
        try:
            threshold = float(threshold_str)
            if not 0.0 <= threshold <= 1.0:
                raise ValueError()
        except (ValueError, TypeError):
            messagebox.showerror(
                'Invalid Threshold' if self.lang == 'en' else 'Ngưỡng Không Hợp Lệ',
                'Threshold must be between 0.0 and 1.0' if self.lang == 'en'
                else 'Ngưỡng phải từ 0.0 đến 1.0'
            )
            return
        
        # Create/update template
        template_data = {
            'name': name,
            'path': path,
            'threshold': threshold
        }
        
        if self.template_form_mode == 'add':
            # Add new template
            if 'templates' not in self.current_monster:
                self.current_monster['templates'] = []
            self.current_monster['templates'].append(template_data)
            
            messagebox.showinfo(
                'Added' if self.lang == 'en' else 'Đã Thêm',
                f"Template '{name}' added successfully." if self.lang == 'en'
                else f"Đã thêm template '{name}'."
            )
        
        elif self.template_form_mode == 'edit':
            # Update existing template
            templates = self.current_monster.get('templates', [])
            if self.template_form_edit_index is not None and self.template_form_edit_index < len(templates):
                templates[self.template_form_edit_index] = template_data
            
            messagebox.showinfo(
                'Updated' if self.lang == 'en' else 'Đã Cập Nhật',
                f"Template '{name}' updated successfully." if self.lang == 'en'
                else f"Đã cập nhật template '{name}'."
            )
        
        # Mark changes
        self.changes_made['monsters_changed'] = True
        
        # Hide form and refresh
        self._cancel_template_form()
        self._show_template_editor(self.current_monster)
        self._show_monster_details(self.current_monster)  # Refresh monster info
        self._refresh_monster_tree()
    
    def _cancel_template_form(self):
        """Cancel template form editing."""
        self.template_form_frame.pack_forget()
        self.template_form_mode = None
        self.template_form_edit_index = None
    
    # === OLD Methods (keep for compatibility) ===
    
    def _add_template(self):
        """DEPRECATED: Use _add_template_inline instead."""
        self._add_template_inline()
    
    def _edit_template(self):
        """DEPRECATED: Use _edit_template_inline instead."""
        self._edit_template_inline()
    
    def _delete_template(self):
        """DEPRECATED: Use _delete_template_inline instead."""
        self._delete_template_inline()
    
    def _capture_template(self):
        """Capture template image from a selected screen region and attach to current monster."""
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            messagebox.showwarning(
                'No Monster' if self.lang == 'en' else 'Chưa Chọn Quái',
                'Please select a monster first.' if self.lang == 'en' else 'Vui lòng chọn một quái trước.'
            )
            return
        # Check PIL availability
        if not self.pil_available:
            message = (
                'This feature requires Pillow. Please install with:\n\n'
                'pip install pillow'
            ) if self.lang == 'en' else (
                'Tính năng này cần Pillow. Vui lòng cài đặt bằng:\n\n'
                'pip install pillow'
            )
            messagebox.showerror('Pillow Required', message)
            return
        # Hide our window to capture cleanly
        try:
            self.withdraw()
            self.update_idletasks()
            time.sleep(0.15)
        except Exception:
            pass
        # Region selection overlay
        try:
            overlay = self._RegionCaptureOverlay(self)
            bbox = overlay.show_modal()
        except Exception as e:
            bbox = None
        finally:
            # Restore window
            try:
                self.deiconify()
                self.lift()
                self.focus_force()
            except Exception:
                pass
        if not bbox:
            # User canceled or invalid selection
            return
        # Capture and save
        try:
            img = ImageGrab.grab(bbox=bbox)  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror(
                'Capture Failed' if self.lang == 'en' else 'Chụp Thất Bại',
                f"Error during capture: {e}"
            )
            return
        # Build save path
        templates_dir = Path(os.path.dirname(os.path.dirname(__file__))) / 'images' / 'templates'
        templates_dir.mkdir(parents=True, exist_ok=True)
        base = self._sanitize_filename(self.current_monster.get('name', 'monster'))
        ts = int(time.time())
        filename = f"{base}_{ts}.png"
        save_path = templates_dir / filename
        try:
            img.save(save_path)
        except Exception as e:
            messagebox.showerror(
                'Save Failed' if self.lang == 'en' else 'Lưu Thất Bại',
                f"Cannot save image: {e}"
            )
            return
        # Append to monster templates
        tmpl = {
            'name': filename,
            'path': str(save_path),
            'threshold': 0.85,
        }
        templates = self.current_monster.setdefault('templates', [])
        templates.append(tmpl)
        self.changes_made['monsters_changed'] = True
        # Refresh UI
        self._show_template_editor(self.current_monster)
        self._show_monster_details(self.current_monster)
        self._refresh_monster_tree()
        # Notify
        messagebox.showinfo(
            'Captured' if self.lang == 'en' else 'Đã Chụp',
            'Template captured and saved.' if self.lang == 'en' else 'Đã chụp và lưu template.'
        )

    # --------- Windows helpers to get target window rect ---------
    def _get_game_hwnd(self) -> Optional[int]:
        # Prefer hwnd saved in hunt config if present
        try:
            hwnd = self.hunt_cfg.get('window_hwnd')
            if hwnd:
                return int(hwnd)
        except Exception:
            pass
        # Fallback: foreground window
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            return int(hwnd) if hwnd else None
        except Exception:
            return None

    def _get_window_rect(self, hwnd: int) -> Optional[tuple[int,int,int,int]]:
        try:
            user32 = ctypes.windll.user32
            rect = wintypes.RECT()
            ok = user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect))
            if not ok:
                return None
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _capture_template_window(self):
        """Capture template restricted to the game window region."""
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            messagebox.showwarning(
                'No Monster' if self.lang == 'en' else 'Chưa Chọn Quái',
                'Please select a monster first.' if self.lang == 'en' else 'Vui lòng chọn một quái trước.'
            )
            return
        if not self.pil_available:
            message = (
                'This feature requires Pillow. Please install with:\n\n'
                'pip install pillow'
            ) if self.lang == 'en' else (
                'Tính năng này cần Pillow. Vui lòng cài đặt bằng:\n\n'
                'pip install pillow'
            )
            messagebox.showerror('Pillow Required', message)
            return
        hwnd = self._get_game_hwnd()
        if not hwnd:
            messagebox.showwarning(
                'Window Not Found' if self.lang == 'en' else 'Không Tìm Thấy Cửa Sổ',
                'Cannot determine game window. Make it active or set it in setup.' if self.lang == 'en' else 'Không xác định được cửa sổ game. Hãy kích hoạt cửa sổ game hoặc cấu hình trong wizard.'
            )
            return
        rect = self._get_window_rect(hwnd)
        if not rect:
            messagebox.showwarning(
                'Window Rect Error' if self.lang == 'en' else 'Lỗi Tọa Độ Cửa Sổ',
                'Unable to get window bounds.' if self.lang == 'en' else 'Không lấy được kích thước cửa sổ.'
            )
            return
        # Hide our window and show restricted overlay within rect
        try:
            self.withdraw()
            self.update_idletasks()
            time.sleep(0.15)
        except Exception:
            pass
        try:
            overlay = self._RegionCaptureOverlay(self, restrict_bbox=rect)
            bbox = overlay.show_modal()
        except Exception:
            bbox = None
        finally:
            try:
                self.deiconify()
                self.lift()
                self.focus_force()
            except Exception:
                pass
        if not bbox:
            return
        # Capture region
        try:
            img = ImageGrab.grab(bbox=bbox)  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror(
                'Capture Failed' if self.lang == 'en' else 'Chụp Thất Bại',
                f"Error during capture: {e}"
            )
            return
        # Save and update
        templates_dir = Path(os.path.dirname(os.path.dirname(__file__))) / 'images' / 'templates'
        templates_dir.mkdir(parents=True, exist_ok=True)
        base = self._sanitize_filename(self.current_monster.get('name', 'monster'))
        ts = int(time.time())
        filename = f"{base}_{ts}.png"
        save_path = templates_dir / filename
        try:
            img.save(save_path)
        except Exception as e:
            messagebox.showerror(
                'Save Failed' if self.lang == 'en' else 'Lưu Thất Bại',
                f"Cannot save image: {e}"
            )
            return
        tmpl = {'name': filename, 'path': str(save_path), 'threshold': 0.85}
        self.current_monster.setdefault('templates', []).append(tmpl)
        self.changes_made['monsters_changed'] = True
        self._show_template_editor(self.current_monster)
        self._show_monster_details(self.current_monster)
        self._refresh_monster_tree()
        messagebox.showinfo(
            'Captured' if self.lang == 'en' else 'Đã Chụp',
            'Template captured and saved.' if self.lang == 'en' else 'Đã chụp và lưu template.'
        )
    
    # ==================== End Template Management ====================
    
    def _build_skill_tab(self, parent: tk.Frame):
        """
        Build Skill Library tab with CRUD operations.
        
        TODO Sprint 19 Task #3: Implement full skill management
        - List view with columns: Name, Key, Type, Cooldown, Cast Time
        - Add/Edit/Delete buttons
        - Type filter (attack/buff)
        - Cooldown and cast time editor
        - Skill image capture
        """
        # Placeholder for now
        placeholder = tk.Label(
            parent,
            text="⚔️ Skill Library Tab\n\nComing in Task #3:\n"
                 "• List all skills with details\n"
                 "• Add/Edit/Delete skills\n"
                 "• Filter by type (attack/buff)\n"
                 "• Edit cooldown and cast time\n"
                 "• Import skill icons from game",
            justify='left',
            padx=20,
            pady=20,
            font=('Arial', 10)
        )
        placeholder.pack(expand=True)
    
    def _build_timing_tab(self, parent: tk.Frame):
        """
        Build Timing Calculator tab with auto-calculation and recommendations.
        
        TODO Sprint 19 Task #4: Implement timing calculator
        - Auto-calculate from configured skills
        - Show breakdown: "3 attack skills, avg cooldown 2.1s → APS 1.43"
        - Display recommendations: "Recommended attack_interval: 0.7s"
        - Button: "Apply to Advanced Settings"
        - Real-time preview of timing impact
        """
        # Placeholder for now
        placeholder = tk.Label(
            parent,
            text="⏱️ Timing Calculator Tab\n\nComing in Task #4:\n"
                 "• Auto-calculate from configured skills\n"
                 "• Show attack speed breakdown\n"
                 "• Display recommended timings\n"
                 "• One-click apply to Advanced Settings\n"
                 "• Preview timing impact on hunt performance",
            justify='left',
            padx=20,
            pady=20,
            font=('Arial', 10)
        )
        placeholder.pack(expand=True)
    
    def _apply_all_changes(self):
        """
        Apply all pending changes to configuration files.
        
        This will:
        1. Save monsters to monsters.json (if changed)
        2. Save skills to skills.json (if changed)
        3. Save hunt_cfg to hunt_config.json (if timing applied)
        4. Show success message
        """
        try:
            changes = self.changes_made.copy()
            if not any(changes.values()):
                messagebox.showinfo(self._t('success_title'), "No changes to apply." if self.lang == 'en' else "Không có thay đổi để áp dụng.")
                return
            root_dir = Path(os.path.dirname(os.path.dirname(__file__)))
            data_dir = root_dir / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            # Before saving, finalize any temp-captured assets and normalize paths
            if changes.get('monsters_changed'):
                self._finalize_template_assets()
            # Save monsters
            if changes.get('monsters_changed'):
                monsters_path = data_dir / 'monsters.json'
                with monsters_path.open('w', encoding='utf-8') as f:
                    json.dump(self.monsters, f, ensure_ascii=False, indent=2)
            # Save skills
            if changes.get('skills_changed'):
                skills_path = data_dir / 'skills.json'
                with skills_path.open('w', encoding='utf-8') as f:
                    json.dump(self.skills, f, ensure_ascii=False, indent=2)
            # Save hunt config if timing applied
            if changes.get('timing_applied'):
                hunt_path = data_dir / 'hunt_config.json'
                with hunt_path.open('w', encoding='utf-8') as f:
                    json.dump(self.hunt_cfg, f, ensure_ascii=False, indent=2)
            # Report and close
            messagebox.showinfo(self._t('success_title'), self._t('changes_applied'))
            self._on_window_close(force_apply=True)
        except Exception as e:
            messagebox.showerror('Error' if self.lang == 'en' else 'Lỗi', f"Failed to apply changes: {e}")
    
    def _on_window_close(self, force_apply: bool = False):
        """
        Handle window close event.
        
        Args:
            force_apply: If True, apply changes without asking
        """
        # Check if there are unsaved changes
        has_changes = any(self.changes_made.values())
        
        if has_changes and not force_apply:
            # Ask user if they want to apply changes
            response = messagebox.askyesnocancel(
                self._t('confirm_title'),
                self._t('changes_pending')
            )
            
            if response is None:  # Cancel
                return
            elif response:  # Yes - Apply changes
                self._apply_all_changes()
                return  # _apply_all_changes will close window
            else:
                # No - discard changes: cleanup temp captures
                try:
                    self._cleanup_temp_captures()
                except Exception:
                    pass
        
        # Call callback if provided
        if self.on_close_callback and has_changes:
            self.on_close_callback({
                **self.changes_made,
                'hunt_cfg': self.hunt_cfg,
                'monsters': self.monsters,
                'skills': self.skills
            })
        
    # Destroy window
        self.grab_release()
        self.destroy()


class MonsterDialog:
    """
    Dialog for adding or editing a monster.
    
    Provides form fields for:
    - Name (required)
    - HP (integer, required)
    - Damage per hit (integer, required)
    - Description (optional)
    - Priority (integer, optional, default=1)
    - Templates (readonly list for now)
    
    Args:
        parent: Parent window
        lang: Language ('en' or 'vi')
        mode: 'add' or 'edit'
        monster: Monster dict (for edit mode)
    
    Returns:
        result: New/updated monster dict, or None if cancelled
    """
    
    def __init__(self, parent: tk.Toplevel, lang: str = 'en', mode: str = 'add', monster: Optional[dict] = None):
        self.parent = parent
        self.lang = lang
        self.mode = mode
        self.monster = monster or {}
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(
            'Add Monster' if mode == 'add' and lang == 'en' else
            'Thêm Quái' if mode == 'add' else
            'Edit Monster' if lang == 'en' else
            'Sửa Quái'
        )
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Build form
        self._build_form()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _build_form(self):
        """Build form fields."""
        # Main container with padding
        container = tk.Frame(self.dialog, padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Title
        title = tk.Label(
            container,
            text='🐉 Monster Information' if self.lang == 'en' else '🐉 Thông Tin Quái Vật',
            font=('Arial', 12, 'bold')
        )
        title.pack(pady=(0, 15))
        
        # Form fields
        form_frame = tk.Frame(container)
        form_frame.pack(fill='both', expand=True)
        
        # Name field (required)
        tk.Label(
            form_frame,
            text='Name:' if self.lang == 'en' else 'Tên:',
            font=('Arial', 9, 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.name_var = tk.StringVar(value=self.monster.get('name', ''))
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, width=40, font=('Arial', 9))
        name_entry.grid(row=0, column=1, pady=5, sticky='ew')
        name_entry.focus()
        
        # HP field (required)
        tk.Label(
            form_frame,
            text='HP:',
            font=('Arial', 9, 'bold')
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.hp_var = tk.StringVar(value=str(self.monster.get('hp', '')))
        hp_entry = tk.Entry(form_frame, textvariable=self.hp_var, width=40, font=('Arial', 9))
        hp_entry.grid(row=1, column=1, pady=5, sticky='ew')
        
        # Damage field (required)
        tk.Label(
            form_frame,
            text='Damage per hit:' if self.lang == 'en' else 'Sát thương mỗi đòn:',
            font=('Arial', 9, 'bold')
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.damage_var = tk.StringVar(value=str(self.monster.get('damage_per_hit', '')))
        damage_entry = tk.Entry(form_frame, textvariable=self.damage_var, width=40, font=('Arial', 9))
        damage_entry.grid(row=2, column=1, pady=5, sticky='ew')
        
        # Priority field (optional)
        tk.Label(
            form_frame,
            text='Priority:' if self.lang == 'en' else 'Độ ưu tiên:',
            font=('Arial', 9)
        ).grid(row=3, column=0, sticky='w', pady=5)
        
        self.priority_var = tk.StringVar(value=str(self.monster.get('priority', '1')))
        priority_entry = tk.Entry(form_frame, textvariable=self.priority_var, width=40, font=('Arial', 9))
        priority_entry.grid(row=3, column=1, pady=5, sticky='ew')
        
        # Description field (optional)
        tk.Label(
            form_frame,
            text='Description:' if self.lang == 'en' else 'Mô tả:',
            font=('Arial', 9)
        ).grid(row=4, column=0, sticky='nw', pady=5)
        
        desc_frame = tk.Frame(form_frame)
        desc_frame.grid(row=4, column=1, pady=5, sticky='ew')
        
        self.desc_text = tk.Text(desc_frame, width=40, height=4, font=('Arial', 9))
        self.desc_text.pack(side='left', fill='both', expand=True)
        self.desc_text.insert('1.0', self.monster.get('description', ''))
        
        desc_scroll = tk.Scrollbar(desc_frame, command=self.desc_text.yview)
        desc_scroll.pack(side='right', fill='y')
        self.desc_text.config(yscrollcommand=desc_scroll.set)
        
        # Templates info (readonly)
        tk.Label(
            form_frame,
            text='Templates:' if self.lang == 'en' else 'Templates:',
            font=('Arial', 9)
        ).grid(row=5, column=0, sticky='w', pady=5)
        
        template_count = len(self.monster.get('templates', []))
        tk.Label(
            form_frame,
            text=f"{template_count} template(s)" if self.lang == 'en' else f"{template_count} template",
            font=('Arial', 9),
            fg='gray'
        ).grid(row=5, column=1, sticky='w', pady=5)
        
        # Configure column weights
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(container)
        button_frame.pack(pady=(15, 0))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text='💾 Save' if self.lang == 'en' else '💾 Lưu',
            command=self._save,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=20,
            pady=5,
            cursor='hand2'
        )
        save_btn.pack(side='left', padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text='❌ Cancel' if self.lang == 'en' else '❌ Hủy',
            command=self._cancel,
            bg='#f44336',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=20,
            pady=5,
            cursor='hand2'
        )
        cancel_btn.pack(side='left', padx=5)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _validate(self) -> bool:
        """Validate form fields."""
        # Check name
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter monster name.' if self.lang == 'en' else 'Vui lòng nhập tên quái.',
                parent=self.dialog
            )
            return False
        
        # Check HP
        try:
            hp = int(self.hp_var.get().strip())
            if hp <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter valid HP (positive integer).' if self.lang == 'en' 
                else 'Vui lòng nhập HP hợp lệ (số nguyên dương).',
                parent=self.dialog
            )
            return False
        
        # Check damage
        try:
            damage = int(self.damage_var.get().strip())
            if damage <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter valid damage (positive integer).' if self.lang == 'en'
                else 'Vui lòng nhập sát thương hợp lệ (số nguyên dương).',
                parent=self.dialog
            )
            return False
        
        # Check priority
        try:
            priority = int(self.priority_var.get().strip())
        except ValueError:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter valid priority (integer).' if self.lang == 'en'
                else 'Vui lòng nhập độ ưu tiên hợp lệ (số nguyên).',
                parent=self.dialog
            )
            return False
        
        return True
    
    def _save(self):
        """Save and close dialog."""
        if not self._validate():
            return
        
        # Build result dict
        self.result = {
            'name': self.name_var.get().strip(),
            'hp': int(self.hp_var.get().strip()),
            'damage_per_hit': int(self.damage_var.get().strip()),
            'priority': int(self.priority_var.get().strip()),
            'description': self.desc_text.get('1.0', 'end-1c').strip(),
            'templates': self.monster.get('templates', [])  # Preserve existing templates
        }
        
        self.dialog.grab_release()
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.dialog.grab_release()
        self.dialog.destroy()


# Example usage / Testing
if __name__ == '__main__':
    # Create test window
    root = tk.Tk()
    root.title("Test Main App")
    root.geometry("600x400")
    
    # Sample data
    test_hunt_cfg = {
        'skill_slots': [
            {'name': 'Dark Explosion', 'key': '1', 'type': 'attack', 'cooldown': 1.9},
            {'name': 'Bone Javelin', 'key': '2', 'type': 'attack', 'cooldown': 2.4},
            {'name': 'Skull Shooter', 'key': '3', 'type': 'attack', 'cooldown': 2.2},
            {'name': 'Regeneration', 'key': '4', 'type': 'buff', 'cooldown': 2.2}
        ],
        'attack_interval': 0.15,
        'lost_timeout_sec': 0.5
    }
    
    test_monsters = [
        {'name': 'Coc Go', 'hp': 10000, 'damage_per_hit': 500, 'priority': 1}
    ]
    
    test_skills = [
        {'name': 'Dark Explosion', 'key': '1', 'type': 'attack', 'cooldown': 1.9},
        {'name': 'Bone Javelin', 'key': '2', 'type': 'attack', 'cooldown': 2.4}
    ]
    
    def on_changes(changes):
        print("Changes received from Library Manager:")
        print(f"  Monsters changed: {changes['monsters_changed']}")
        print(f"  Skills changed: {changes['skills_changed']}")
        print(f"  Timing applied: {changes['timing_applied']}")
    
    # Button to open Library Manager
    def open_library_manager():
        manager = LibraryManagerWindow(
            parent=root,
            hunt_cfg=test_hunt_cfg,
            monsters=test_monsters,
            skills=test_skills,
            lang='vi',
            on_close_callback=on_changes
        )
    
    tk.Button(
        root,
        text="📚 Open Library Manager",
        command=open_library_manager,
        font=('Arial', 12, 'bold'),
        bg='#2196F3',
        fg='white',
        padx=20,
        pady=10
    ).pack(expand=True)
    
    root.mainloop()
