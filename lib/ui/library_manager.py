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
from lib.i18n import register_bulk as i18n_register_bulk, t as i18n_t
from lib.ui_style import UIStyle as UI
from lib.i18n.translations import LIBRARY_MANAGER_TRANSLATIONS
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

# Add parent directory to path for imports (project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Optional PIL imports for capture and previews
try:
    from PIL import ImageGrab, Image, ImageTk  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    ImageGrab = None  # type: ignore
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

# Icon helper
try:
    from lib.ui.icon_helper import get_icon_helper
    icon_helper = get_icon_helper()
except Exception:
    icon_helper = None

from lib.ui.tooltip import attach_i18n_tooltip

# Shared capture helper
try:
    from lib.ui.capture_helper import capture_region_and_save
except Exception:
    capture_region_and_save = None  # type: ignore

# Template matcher for Test Recognition and Auto-Detect Region
try:
    from lib.vision.template_matcher import locate_template  # type: ignore
except Exception:
    locate_template = None  # type: ignore

# Import existing utilities (will be available when integrated)
# Use importlib to avoid static unresolved-import issues in editors/linters
try:
    import importlib
    timing_mod = importlib.import_module('lib.timing_calculator')
    calculate_timing = getattr(timing_mod, 'calculate_timing')
    format_timing_recommendation = getattr(timing_mod, 'format_timing_recommendation')
    # skills module may not be present yet; provide fallbacks
    try:
        skills_mod = importlib.import_module('lib.skills')
        load_skill_library = getattr(skills_mod, 'load_skill_library')
        save_skill_library = getattr(skills_mod, 'save_skill_library')
    except Exception:
        raise
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

    # --- Small icon cache ---
    def _icon(self, name: str, fallback: str, size: int = 16):
        try:
            if not hasattr(self, '_icon_cache'):
                self._icon_cache = {}
            key = f"{name}_{size}"
            if key in self._icon_cache:
                return self._icon_cache[key]
            # If icon helper is unavailable, do not pass a text fallback to Tk 'image' option
            if not icon_helper:
                self._icon_cache[key] = ''
                return ''
            img = icon_helper.get_icon(name, fallback=fallback, size=size)
            # Ensure we never return a text emoji for the Tk 'image' parameter
            if isinstance(img, str):
                img = ''
            self._icon_cache[key] = img
            return img
        except Exception:
            # On any error, return empty image name to avoid TclError
            return ''

    def _make_icon_button(self, parent, icon_name: str, fallback_text: str, tooltip_key: str, command: Optional[Callable[[], Any] | str] = None, **kwargs):
        """Create an icon-only button with hand cursor and localized tooltip.

        If icon image is unavailable, falls back to emoji/text label while keeping cursor and tooltip.
        """
        img = None
        try:
            img = self._icon(icon_name, fallback_text)
        except Exception:
            img = None
        # Do not pass emoji to image param; use text only when image missing
        btn_kwargs = dict(kwargs)
        # Ensure command is not None (Tk requires a callable or string)
        cmd = command if command is not None else (lambda: None)
        if img:
            btn = tk.Button(parent, image=img, command=cmd, cursor='hand2', **btn_kwargs)
            try:
                # Keep a reference on the window to avoid GC
                if not hasattr(self, '_image_refs'):
                    self._image_refs = []
                self._image_refs.append(img)  # type: ignore[attr-defined]
            except Exception:
                pass
        else:
            # Emoji/text fallback if icon image missing
            try:
                text_fb = self._icon_text(icon_name, fallback_text)
            except Exception:
                text_fb = fallback_text
            btn = tk.Button(parent, text=text_fb, command=cmd, cursor='hand2', **btn_kwargs)
        try:
            attach_i18n_tooltip(btn, key=tooltip_key, ns='library_manager', lang_provider=lambda: self.lang)
        except Exception:
            pass
        return btn

    def _icon_text(self, name: str, fallback: str) -> str:
        """Return a text/emoji fallback for non-image contexts using icon_helper when available."""
        try:
            if not icon_helper:
                return fallback
            ic = icon_helper.get_icon(name, fallback=fallback, size=16)
            return ic if isinstance(ic, str) and ic else fallback
        except Exception:
            return fallback

    def _on_template_region_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        vals = {k: self.template_region_vars[k].get().strip() for k in ('left','top','width','height')}
        if any(vals.values()):
            try:
                region_vals = {k: int(vals[k]) for k in vals}
                if region_vals['width'] <= 0 or region_vals['height'] <= 0:
                    return
                tmpl['region_strategy'] = 'custom'
                tmpl['region'] = region_vals
            except Exception:
                # ignore until valid
                return
        else:
            # No override → use window strategy
            tmpl.pop('region', None)
            tmpl['region_strategy'] = 'window'
        self.changes_made['monsters_changed'] = True
        # Badge already shown by unlock action - no need to mark unsaved here

    # ============================================================================
    # Setup Wizard Vision - Modern replacement for legacy vision tools
    # ============================================================================
    
    def _open_setup_wizard_vision(self):
        """Open Setup Wizard Vision dialog - shows upcoming feature upgrades."""
        dialog = tk.Toplevel(self)
        dialog.title('Setup Wizard Vision' if self.lang == 'en' else 'Thiết Lập Vision Nâng Cao')
        dialog.geometry('700x600')
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f'+{x}+{y}')
        
        # Header
        header_frame = tk.Frame(dialog, bg='#66BB6A', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, 
            text='🔮 Setup Wizard Vision - Coming Soon!',
            bg='#66BB6A', fg='white', 
            font=('Arial', 14, 'bold')).pack(pady=15)
        
        # Content frame
        content_frame = tk.Frame(dialog, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        if self.lang == 'vi':
            title_text = '📋 Các Tính Năng Sắp Được Nâng Cấp'
            content_text = """
🎯 TỔNG QUAN

Chúng tôi đang phát triển hệ thống Setup Wizard Vision hoàn toàn mới để thay thế 
các công cụ cũ (Chọn vùng, Kiểm tra nhận diện, Tự động dò vùng).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ CÁC TÍNH NĂNG MỚI

1. 🎨 Semi-Transparent Overlay
   • Nhìn thấy game khi kéo vùng chọn
   • Không còn bị "mù" với overlay đen đục
   • Hiển thị kích thước real-time khi kéo

2. 🎯 Auto-Numbering & Visual Feedback
   • Tự động đánh số các đối tượng phát hiện được (#1, #2, #3...)
   • Hiển thị bounding box với màu sắc rõ ràng
   • Hiển thị confidence score cho mỗi detection

3. 📹 Real-time Tracking
   • Theo dõi chuyển động của monsters trên màn hình
   • Hybrid tracking: OpenCV Tracker + Template Matching
   • Re-verify định kỳ để tránh lost track

4. 🔍 Scale-Invariant Detection
   • Tự động handle camera zoom in/out
   • Multi-scale template matching
   • Feature-based matching (SIFT/ORB) cho robust detection

5. 🧙 Step-by-Step Wizard UI
   • Hướng dẫn từng bước rõ ràng
   • Live preview cho mỗi bước
   • Validation và feedback tức thì

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CẢI TIẾN UX

Before (Cũ):
❌ Overlay đen đục → không thấy gì
❌ Không biết kéo từ đâu đến đâu
❌ Không biết đã phát hiện được gì
❌ Không có feedback khi zoom

After (Mới):
✅ Semi-transparent → nhìn thấy game
✅ Live dimension display
✅ Auto-numbering với bounding boxes
✅ Real-time tracking với scale handling
✅ Wizard hướng dẫn step-by-step

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 TIMELINE (DỰ KIẾN)

Week 1-2: UI/UX improvements
  • Semi-transparent overlay
  • Live dimension display  
  • Auto-numbering

Week 3-4: Tracking system
  • Basic template matching loop
  • Hybrid tracker implementation

Week 5-6: Advanced features
  • Multi-scale matching
  • Feature-based detection
  • Final wizard polish

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TẠI SAO CẦN NÂNG CẤP?

1. Người dùng mới khó hiểu cách dùng công cụ cũ
2. Không có visual feedback → bối rối
3. Không handle camera zoom → detection fail
4. Không track movement → phải re-detect liên tục

→ Wizard mới sẽ giải quyết TẤT CẢ vấn đề này!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 TÀI LIỆU THAM KHẢO

Xem thêm chi tiết kỹ thuật trong:
• docs/sprints/sprint20/VISION_WIZARD_DESIGN.md
• docs/ADVANCED_VISION_FEATURES.md

Theo dõi tiến độ tại:
• GitHub Issues: #vision-wizard
• Sprint Board: Sprint 20
"""
        else:
            title_text = '📋 Upcoming Feature Upgrades'
            content_text = """
🎯 OVERVIEW

We are developing a completely new Setup Wizard Vision system to replace the 
old tools (Pick Region, Test Recognition, Auto-Detect Region).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ NEW FEATURES

1. 🎨 Semi-Transparent Overlay
   • See the game while selecting region
   • No more "blind" with opaque black overlay
   • Real-time dimension display while dragging

2. 🎯 Auto-Numbering & Visual Feedback
   • Automatically number detected objects (#1, #2, #3...)
   • Display bounding boxes with clear colors
   • Show confidence score for each detection

3. 📹 Real-time Tracking
   • Track monster movement on screen
   • Hybrid tracking: OpenCV Tracker + Template Matching
   • Periodic re-verify to avoid lost track

4. 🔍 Scale-Invariant Detection
   • Automatically handle camera zoom in/out
   • Multi-scale template matching
   • Feature-based matching (SIFT/ORB) for robust detection

5. 🧙 Step-by-Step Wizard UI
   • Clear step-by-step guidance
   • Live preview for each step
   • Instant validation and feedback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 UX IMPROVEMENTS

Before (Old):
❌ Opaque black overlay → can't see anything
❌ Don't know where to drag
❌ Don't know what was detected
❌ No feedback when zooming

After (New):
✅ Semi-transparent → see the game
✅ Live dimension display
✅ Auto-numbering with bounding boxes
✅ Real-time tracking with scale handling
✅ Step-by-step wizard guidance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 TIMELINE (ESTIMATED)

Week 1-2: UI/UX improvements
  • Semi-transparent overlay
  • Live dimension display  
  • Auto-numbering

Week 3-4: Tracking system
  • Basic template matching loop
  • Hybrid tracker implementation

Week 5-6: Advanced features
  • Multi-scale matching
  • Feature-based detection
  • Final wizard polish

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHY UPGRADE?

1. New users find old tools confusing
2. No visual feedback → confusion
3. No camera zoom handling → detection fails
4. No movement tracking → must re-detect constantly

→ New wizard will solve ALL these issues!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION

See technical details in:
• docs/sprints/sprint20/VISION_WIZARD_DESIGN.md
• docs/ADVANCED_VISION_FEATURES.md

Track progress at:
• GitHub Issues: #vision-wizard
• Sprint Board: Sprint 20
"""
        
        tk.Label(content_frame,
            text=title_text,
            bg='white', fg='#424242',
            font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Scrollable text area
        text_frame = tk.Frame(content_frame, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(text_frame,
            wrap='word',
            bg='#F5F5F5',
            fg='#212121',
            font=('Consolas', 9),
            padx=15, pady=15,
            yscrollcommand=scrollbar.set,
            relief='flat',
            borderwidth=1)
        text_widget.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        # Insert content
        text_widget.insert('1.0', content_text)
        text_widget.config(state='disabled')  # Read-only
        
        # Bottom button frame
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        close_btn = tk.Button(btn_frame,
            text='Close' if self.lang == 'en' else 'Đóng',
            command=dialog.destroy,
            bg='#757575', fg='white',
            font=('Arial', 10, 'bold'),
            padx=20, pady=8,
            relief='flat',
            cursor='hand2')
        close_btn.pack(side='right')
    
    # ============================================================================
    # LEGACY VISION METHODS - Preserved for backward compatibility
    # These will be migrated to new Setup Wizard Vision system
    # ============================================================================

    def _pick_template_region(self):
        """Let user pick a region from screen for current template; fill fields and persist."""
        if not hasattr(self, 'current_monster') or self.current_monster is None:
            messagebox.showwarning('No Monster' if self.lang=='en' else 'Chưa Chọn Quái',
                                   'Please select a monster first.' if self.lang=='en' else 'Vui lòng chọn một quái trước.')
            return
        # Bring game window to front before overlay
        try:
            pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
            hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
            if pid:
                self._bring_window_to_front_by_pid(int(pid))
            elif hwnd_cfg:
                self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
        except Exception:
            pass
        # Iconify our window to avoid covering game
        try:
            self.iconify()
        except Exception:
            pass
        self.update()
        # Optionally restrict to game window bounds if available
        restrict = None
        try:
            wb = self.hunt_cfg.get('window_bounds') if isinstance(self.hunt_cfg, dict) else None
            if wb and all(k in wb for k in ('left','top','width','height')):
                l,t,w,h = int(wb['left']), int(wb['top']), int(wb['width']), int(wb['height'])
                restrict = (l, t, l + w, t + h)
        except Exception:
            restrict = None
        try:
            overlay = self._RegionCaptureOverlay(self, restrict_bbox=restrict)
            bbox = overlay.show_modal()  # returns (left, top, right, bottom)
        finally:
            try:
                self.deiconify()
                self.lift()
            except Exception:
                pass
        if not bbox:
            return
        l, t, r, b = bbox
        w = max(0, int(r - l))
        h = max(0, int(b - t))
        self._suspend_template_var_traces = True
        try:
            self.template_region_vars['left'].set(str(l))
            self.template_region_vars['top'].set(str(t))
            self.template_region_vars['width'].set(str(w))
            self.template_region_vars['height'].set(str(h))
        finally:
            self._suspend_template_var_traces = False
        self._on_template_region_change()

    def _resolve_current_template_params(self) -> Optional[tuple[str, float, Optional[tuple[int,int,int,int]]]]:
        """Collect (path, threshold, region) for current template based on UI fields."""
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return None
        path = (self.template_path_var.get() or tmpl.get('path','')).strip()
        if not path:
            return None
        # Threshold
        try:
            th = float((self.template_threshold_var.get() or tmpl.get('threshold', 0.85)))
            th = max(0.0, min(th, 1.0))
        except Exception:
            th = float(tmpl.get('threshold', 0.85))
        # Region
        vals = {k: self.template_region_vars[k].get().strip() for k in ('left','top','width','height')} if hasattr(self, 'template_region_vars') else {'left':'','top':'','width':'','height':''}
        region = None
        if all(vals.values()):
            try:
                region = (int(vals['left']), int(vals['top']), int(vals['width']), int(vals['height']))
            except Exception:
                region = None
        elif isinstance(self.hunt_cfg, dict) and self.hunt_cfg.get('window_bounds'):
            wb = self.hunt_cfg['window_bounds']
            region = (int(wb.get('left',0)), int(wb.get('top',0)), int(wb.get('width',0)), int(wb.get('height',0)))
        return (path, th, region)

    def _test_template_recognition(self):
        """Test match for current template on screen; minimize app to avoid covering game."""
        if locate_template is None:
            messagebox.showerror('Error', 'template_matcher not available')
            return
        params = self._resolve_current_template_params()
        if not params:
            messagebox.showinfo('Info' if self.lang=='en' else 'Thông báo', 'No template selected' if self.lang=='en' else 'Chưa chọn ảnh mẫu')
            return
        path, th, region = params
        # Bring to front and minimize
        try:
            pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
            hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
            if pid:
                self._bring_window_to_front_by_pid(int(pid))
            elif hwnd_cfg:
                self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
        except Exception:
            pass
        try:
            self.iconify()
        except Exception:
            pass
        self.update()
        time.sleep(0.4)
        try:
            box, conf = locate_template(path, region, th, method='auto')
        except Exception as exc:
            try:
                self.deiconify(); self.lift()
            except Exception:
                pass
            messagebox.showerror('Error' if self.lang=='en' else 'Lỗi', str(exc))
            return
        # Restore
        try:
            self.deiconify(); self.lift()
        except Exception:
            pass
        if box:
            x = int(box[0] + box[2]//2)
            y = int(box[1] + box[3]//2)
            if conf is None:
                msg = (f"Match found at ({x}, {y})" if self.lang=='en' else f"Tìm thấy tại ({x}, {y})")
            else:
                msg = (f"Match found at ({x}, {y}) - Confidence: {conf:.2f}" if self.lang=='en' else f"Tìm thấy tại ({x}, {y}) - Độ khớp: {conf:.2f}")
            messagebox.showinfo('Test Recognition', msg)
        else:
            messagebox.showinfo('Test Recognition', 'No match found' if self.lang=='en' else 'Không tìm thấy')

    def _auto_detect_template_region(self):
        """Auto-detect region by locating template on current screen and filling region with the match bbox."""
        if locate_template is None:
            messagebox.showerror('Error', 'template_matcher not available')
            return
        params = self._resolve_current_template_params()
        if not params:
            messagebox.showinfo('Info' if self.lang=='en' else 'Thông báo', 'No template selected' if self.lang=='en' else 'Chưa chọn ảnh mẫu')
            return
        path, th, region = params
        # Prefer searching within window bounds even if region empty
        if region is None and isinstance(self.hunt_cfg, dict) and self.hunt_cfg.get('window_bounds'):
            wb = self.hunt_cfg['window_bounds']
            region = (int(wb.get('left',0)), int(wb.get('top',0)), int(wb.get('width',0)), int(wb.get('height',0)))
        # Bring game up and minimize
        try:
            pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
            hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
            if pid:
                self._bring_window_to_front_by_pid(int(pid))
            elif hwnd_cfg:
                self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
        except Exception:
            pass
        try:
            self.iconify()
        except Exception:
            pass
        self.update(); time.sleep(0.4)
        try:
            box, conf = locate_template(path, region, th, method='auto')
        except Exception as exc:
            try:
                self.deiconify(); self.lift()
            except Exception:
                pass
            messagebox.showerror('Error' if self.lang=='en' else 'Lỗi', str(exc))
            return
        try:
            self.deiconify(); self.lift()
        except Exception:
            pass
        if not box:
            messagebox.showinfo('Auto-Detect', 'No match found to derive region' if self.lang=='en' else 'Không tìm thấy ảnh để suy ra vùng')
            return
        l,t,w,h = box
        # Fill fields and persist
        self._suspend_template_var_traces = True
        try:
            self.template_region_vars['left'].set(str(l))
            self.template_region_vars['top'].set(str(t))
            self.template_region_vars['width'].set(str(w))
            self.template_region_vars['height'].set(str(h))
        finally:
            self._suspend_template_var_traces = False
        self._on_template_region_change()
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
        # Project paths - library_manager.py is in lib/ui/, need 3 levels up to reach project root
        _current_file = Path(__file__).resolve()     # lib/ui/library_manager.py
        _lib_ui_dir = _current_file.parent           # lib/ui/
        _lib_dir = _lib_ui_dir.parent                # lib/
        self.project_root = _lib_dir.parent          # project root
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
        
        # Initialize common attributes to avoid unknown-attribute issues
        self.unsaved_badge = None  # Global badge in top bar (for all tabs)
        self.template_badge = None  # Template-specific badge in monster tab
        self.details_panel = None
        self.monster_tree = None
        self.template_list_panel = None
        self.template_preview_panel = None
        self.template_edit_panel = None
        self.template_tree = None
        # Initialize form variables (non-optional)
        self.template_name_var = tk.StringVar()
        self.template_path_var = tk.StringVar()
        self.template_threshold_var = tk.StringVar(value='0.85')
        self.template_region_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        # Template edit state
        self.template_locked = True  # Start locked
        self.template_name_entry = None
        self.template_threshold_entry = None
        self.template_region_entries = {}
        self.template_toggle_btn = None  # Edit/Save toggle button
        self.template_temp_saved = False  # Track if template was temporarily saved

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

    # --------- Unsaved indicator (global badge in top bar) ---------
    def _mark_unsaved(self, state: bool):
        """Show/hide global unsaved badge in top bar (tracks all 3 tabs)."""
        try:
            if hasattr(self, 'unsaved_badge') and self.unsaved_badge:
                if state:
                    text = 'CHƯA LƯU' if self.lang == 'vi' else 'UNSAVED'
                    self.unsaved_badge.config(text=text)
                    # Show badge (already packed in top_bar)
                    self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
                else:
                    self.unsaved_badge.config(text='')
                    self.unsaved_badge.pack_forget()
            
            # Update save button tooltip to reflect state
            self._update_save_button_tooltip(state)
        except Exception:
            pass
    
    def _update_save_button_tooltip(self, has_unsaved: bool):
        """Update save button tooltip based on unsaved state."""
        try:
            if not hasattr(self, 'save_btn') or not self.save_btn:
                return
            
            # Determine tooltip key based on state
            tooltip_key = 'tip_apply_all_unsaved' if has_unsaved else 'tip_apply_all_saved'
            
            # Remove old tooltip if exists
            if hasattr(self.save_btn, '_i18n_tooltip'):
                old_tooltip = getattr(self.save_btn, '_i18n_tooltip')
                try:
                    # Unbind events from old tooltip
                    self.save_btn.unbind('<Enter>')
                    self.save_btn.unbind('<Leave>')
                    self.save_btn.unbind('<ButtonPress>')
                except Exception:
                    pass
            
            # Attach new tooltip with updated key
            attach_i18n_tooltip(
                self.save_btn, 
                key=tooltip_key, 
                ns='library_manager', 
                lang_provider=lambda: self.lang
            )
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
        """Translate using central i18n with local fallback."""
        translations = LIBRARY_MANAGER_TRANSLATIONS
        try:
            # Register once; cheap if already registered (dict.update no-op for same keys)
            i18n_register_bulk('library_manager', translations)
            return i18n_t(key, ns='library_manager', lang=self.lang)
        except Exception:
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
        tk.Label(top_bar, text=self._t('library_manager_title'), bg=UI.BG_PANEL, fg=UI.COLOR_PRIMARY_TEXT, font=UI.FONT_TITLE).pack(side='left', padx=8)
        # Right-aligned actions
        self._make_icon_button(top_bar, 'cancel', '✖', 'tip_close_manager', command=self._on_window_close, bg=UI.BTN_NEUTRAL_BG, fg=UI.BTN_NEUTRAL_FG, relief='flat', padx=12, pady=6).pack(side='right', padx=(6, 10), pady=6)
        
        # Global unsaved badge (for all tabs) - right of Save button
        self.unsaved_badge = tk.Label(top_bar, text='', bg=UI.COLOR_WARNING, fg='#FFFFFF', font=(UI.FONT_FAMILY, 9, 'bold'), padx=8, pady=4)
        self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
        self.unsaved_badge.pack_forget()  # Initially hidden
        
        # Save button with dynamic tooltip based on unsaved state
        self.save_btn = self._make_icon_button(top_bar, 'save', '💾', 'tip_apply_all', command=self._apply_all_changes, bg=UI.BTN_PRIMARY_BG, fg=UI.BTN_PRIMARY_FG, relief='flat', padx=12, pady=6)
        self.save_btn.pack(side='right', padx=6, pady=6)
        
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
        
        # Tab 3: Skill Rotation Builder (formerly Tab 4)
        self.rotation_tab = tk.Frame(self.notebook)
        self.notebook.add(self.rotation_tab, text="🎮 " + ("Skill Rotation" if self.lang == 'en' else "Chu Kỳ Chiêu"))
        self._build_rotation_tab(self.rotation_tab)
        
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

        self._make_icon_button(
            header, 'add', '➕', 'tip_add_monster',
            command=self._add_monster,
            bg='#4CAF50', fg='white', relief='flat',
            font=UI.FONT_BUTTON, padx=self.ui_btn_padx, pady=self.ui_btn_pady
        ).pack(side='right', padx=10, pady=6)

        # Search bar
        search_frame = tk.Frame(left_frame, bg=UI.BG_DEFAULT, pady=12, padx=15)
        search_frame.pack(fill='x')
        search_container = tk.Frame(search_frame, bg=UI.BG_PANEL, highlightbackground='#E0E0E0', highlightthickness=1)
        search_container.pack(fill='x')
        search_img = self._icon('search', '🔍')
        search_txt = self._icon_text('search', '🔍')
        if search_img:
            try:
                tk.Label(search_container, image=search_img, text='', bg='#F5F5F5').pack(side='left', padx=(10, 5))
            except Exception:
                tk.Label(search_container, text=search_txt, font=('Segoe UI', 11), bg='#F5F5F5', fg='#757575').pack(side='left', padx=(10, 5))
        else:
            tk.Label(search_container, text=search_txt, font=(UI.FONT_FAMILY, 11), bg=UI.BG_PANEL, fg=UI.COLOR_HINT).pack(side='left', padx=(10, 5))
        self.monster_search_var = tk.StringVar()
        self.monster_search_var.trace('w', lambda *args: self._filter_monster_list())
        tk.Entry(search_container, textvariable=self.monster_search_var, font=UI.FONT_TEXT, border=0, bg=UI.BG_PANEL, fg=UI.COLOR_TEXT).pack(side='left', fill='x', expand=True, pady=10, padx=(0, 10))

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
        tk.Label(action_bar, text=('Monster Editor' if self.lang=='en' else 'Chỉnh Sửa Quái'), bg=UI.BG_SECTION, fg=UI.COLOR_PRIMARY_TEXT, font=UI.FONT_TITLE).pack(side='left', padx=12)
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
        if not self.monster_tree:
            return
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
        if not self.monster_tree:
            return
        for item in self.monster_tree.get_children():
            self.monster_tree.delete(item)
        
        # Add all monsters
        for monster in self.monsters:
            self._add_monster_to_tree(monster)
    
    def _add_monster_to_tree(self, monster: dict):
        """Add a single monster to the tree."""
        name = monster.get('name', 'Unknown')
        if not self.monster_tree:
            return
        self.monster_tree.insert(
            '',
            'end',
            text=f"  {name}",
            tags=('monster',)
        )
    
    def _on_monster_select(self, event):
        """Handle monster selection in tree."""
        if not self.monster_tree:
            return
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
        if hasattr(self, 'details_panel') and self.details_panel:
            try:
                for w in self.details_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass

        if monster is None:
            if not self.details_panel:
                return
            tk.Label(self.details_panel, text='← ' + ('Select a monster to edit' if self.lang=='en' else 'Chọn quái để sửa'),
                     bg='#FFFFFF', fg='#9E9E9E', font=self.ui_font_label).pack(padx=18, pady=18, anchor='w')
            return

        # Store current and render edit form directly
        self.current_monster = monster
        if self.details_panel:
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
        dialog = MonsterDialog(self, self.lang, mode='add', icon_helper=icon_helper, i18n_registry=i18n_t)
        
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
        if not self.monster_tree:
            return
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
        dialog = MonsterDialog(self, self.lang, mode='edit', monster=monster, icon_helper=icon_helper, i18n_registry=i18n_t)
        
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
        if not self.monster_tree:
            return
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
        if not self.monster_tree:
            return
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
        if not self.monster_tree:
            return
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
        if hasattr(self, 'template_list_panel') and self.template_list_panel:
            try:
                for w in self.template_list_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass
        if hasattr(self, 'template_preview_panel') and self.template_preview_panel:
            try:
                for w in self.template_preview_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass
        if hasattr(self, 'template_edit_panel') and self.template_edit_panel:
            try:
                for w in self.template_edit_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass

        if monster is None:
            # Show empty hints
            if self.template_list_panel:
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
        # Path + Browse + Capture row (moved here under preview for compact UX)
        preview_tools_row = tk.Frame(preview_frame, bg='#FFFFFF')
        preview_tools_row.pack(fill='x', padx=10, pady=(0, 8))
        # Path entry (readonly)
        path_entry = tk.Entry(preview_tools_row, textvariable=self.template_path_var, font=UI.FONT_TEXT, state='readonly', fg=UI.COLOR_SUBTEXT, relief='solid', borderwidth=1)
        path_entry.pack(side='left', fill='x', expand=True, ipady=6)
        # Buttons inline
        self._make_icon_button(preview_tools_row, 'folder', '📁', 'tip_browse_image', command=self._browse_template_image, font=UI.FONT_BUTTON, bg=UI.BTN_NEUTRAL_BG, fg=UI.BTN_NEUTRAL_FG, relief='flat', padx=10, pady=6).pack(side='left', padx=(6,0))
        self._make_icon_button(preview_tools_row, 'capture', '📸', 'tip_capture_image', command=lambda: self._capture_into_path_var(window=False), font=UI.FONT_BUTTON, bg='#9C27B0', fg='#FFFFFF', relief='flat', padx=10, pady=6).pack(side='left', padx=(6,0))

        # Right: edit panel with toolbar + inline form (created but not packed until used)
        edit_toolbar = tk.Frame(self.template_edit_panel, bg=UI.BG_PANEL)
        edit_toolbar.pack(fill='x', padx=10, pady=(10, 0))
        # Right-align with 4px margins
        self._make_icon_button(edit_toolbar, 'delete', '🗑️', 'tip_template_delete', command=self._delete_template_inline, bg=UI.BTN_DANGER_BG, fg=UI.BTN_DANGER_FG, relief='flat', padx=12, pady=6, font=(UI.FONT_FAMILY, 9, 'bold')).pack(side='right', padx=4, pady=4)
        # Toggle button (edit ↔ save) - Store reference for dynamic icon change
        self.template_toggle_btn = self._make_icon_button(edit_toolbar, 'edit', '✏️', 'tip_template_edit', command=self._toggle_template_edit, bg=UI.BTN_INFO_BG, fg=UI.BTN_INFO_FG, relief='flat', padx=12, pady=6, font=(UI.FONT_FAMILY, 9, 'bold'))
        self.template_toggle_btn.pack(side='right', padx=4, pady=4)
        self._make_icon_button(edit_toolbar, 'add', '➕', 'tip_template_add', command=self._add_template_inline, bg=UI.COLOR_ACCENT, fg='#FFFFFF', relief='flat', padx=12, pady=6, font=(UI.FONT_FAMILY, 9, 'bold')).pack(side='right', padx=4, pady=4)

        # Small guidance hint below toolbar
        hint_txt = ('Chọn một template để xem trước và sửa. Dùng Thêm/Sửa/Xóa ở góc phải.' if self.lang=='vi' else 'Select a template to preview and edit. Use Add/Edit/Delete on the top-right.')
        tk.Label(self.template_edit_panel, text=hint_txt, bg='#FFFFFF', fg='#757575', font=('Arial', 8)).pack(fill='x', padx=12, pady=(4, 0))

        # Inline template form
        self.template_form_frame = tk.Frame(self.template_edit_panel, bg=UI.BG_SECTION, relief='flat', borderwidth=0, highlightbackground=UI.COLOR_PRIMARY, highlightthickness=2)

        # Title
        form_title_frame = tk.Frame(self.template_form_frame, bg=UI.BG_TITLE, height=45)
        form_title_frame.pack(fill='x')
        form_title_frame.pack_propagate(False)
        self.form_title_label = tk.Label(form_title_frame, text='', font=(UI.FONT_FAMILY, 11, 'bold'), bg=UI.BG_TITLE, fg='#FFFFFF')
        self.form_title_label.pack(pady=12, padx=15, side='left')
        # Template-specific badge for template editing (initially hidden)
        try:
            self.template_badge = tk.Label(form_title_frame, text='', bg=UI.COLOR_WARNING, fg='#FFFFFF', font=(UI.FONT_FAMILY, 9, 'bold'))
            self.template_badge.place_forget()
        except Exception:
            self.template_badge = None

        form_body = tk.Frame(self.template_form_frame, bg=UI.BG_SECTION)
        form_body.pack(fill='both', expand=True, padx=20, pady=15)
        # Top row: Template Name (4) | Threshold (8)
        top_row = tk.Frame(form_body, bg='#E3F2FD')
        top_row.pack(fill='x', pady=(0, 12))
        top_row.grid_columnconfigure(0, weight=4, uniform='top')
        top_row.grid_columnconfigure(1, weight=8, uniform='top')
        # Name column
        name_col = tk.Frame(top_row, bg=UI.BG_SECTION)
        name_col.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        tk.Label(name_col, text=('Template Name' if self.lang=='en' else 'Tên Template'), bg=UI.BG_SECTION, font=(UI.FONT_FAMILY, 9, 'bold'), fg=UI.COLOR_PRIMARY_TEXT, anchor='w').pack(fill='x', pady=(0,4))
        self.template_name_var = tk.StringVar()
        self.template_name_entry = tk.Entry(name_col, textvariable=self.template_name_var, font=UI.FONT_TEXT, relief='solid', borderwidth=1, state='readonly')
        self.template_name_entry.pack(fill='x', ipady=6)
        tk.Label(name_col, text=('Tên hiển thị của mẫu hình.' if self.lang=='vi' else 'Display name for this template.'), bg=UI.BG_SECTION, fg=UI.COLOR_HINT, font=UI.FONT_SMALL, anchor='w').pack(fill='x', pady=(4,0))
        # Threshold column
        th_col = tk.Frame(top_row, bg=UI.BG_SECTION)
        th_col.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
        tk.Label(th_col, text=('Match Threshold' if self.lang=='en' else 'Ngưỡng Khớp'), bg=UI.BG_SECTION, font=(UI.FONT_FAMILY, 9, 'bold'), fg=UI.COLOR_PRIMARY_TEXT, anchor='w').pack(fill='x', pady=(0,4))
        th_input = tk.Frame(th_col, bg=UI.BG_SECTION)
        th_input.pack(fill='x')
        self.template_threshold_var = tk.StringVar(value='0.85')
        self.template_threshold_entry = tk.Entry(th_input, textvariable=self.template_threshold_var, font=UI.FONT_TEXT, width=12, relief='solid', borderwidth=1, state='readonly')
        self.template_threshold_entry.pack(side='left', ipady=6)
        tk.Label(th_input, text='  (0.0 - 1.0)', bg=UI.BG_SECTION, fg=UI.COLOR_HINT, font=UI.FONT_SMALL).pack(side='left', padx=5)
        tk.Label(th_col, text=(
            'Gợi ý: 0.80 - 0.90. Cao hơn -> ít nhận nhầm, nhưng khó khớp.' if self.lang=='vi' else 
            'Tip: 0.80 - 0.90. Higher = less false positives, but harder to match.'
        ), bg=UI.BG_SECTION, fg=UI.COLOR_HINT, font=UI.FONT_SMALL, anchor='w').pack(fill='x', pady=(4,0))

    # Path inputs moved to preview column above; guidance removed for compactness

        # Threshold moved to top_row with name

        # ============================================================================
        # LEGACY REGION OVERRIDE SECTION - TEMPORARILY HIDDEN FOR WIZARD VISION UPGRADE
        # TODO: Will be replaced by new Setup Wizard Vision feature
        # Keeping code structure for future reference and migration
        # ============================================================================
        
        # HIDDEN: Region override section - preserved for future upgrade
        # region_frame = tk.Frame(form_body, bg='#E3F2FD'); region_frame.pack(fill='x', pady=(0,12))
        # tk.Label(region_frame, text=('Region Override (L,T,W,H)' if self.lang=='en' else 'Vùng ghi đè (L,T,R,D)'), bg='#E3F2FD', font=('Arial', 9, 'bold'), fg='#424242', anchor='w').pack(fill='x', pady=(0,4))
        # region_inputs = tk.Frame(region_frame, bg='#E3F2FD'); region_inputs.pack(fill='x')
        
        # Initialize region vars even when hidden (for backward compatibility)
        self.template_region_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        self.template_region_entries = {}
        
        # HIDDEN: Region input fields - preserved structure
        # for key, lbl in [('left','L'),('top','T'),('width','W'),('height','H')]:
        #     tk.Label(region_inputs, text=f"{lbl}:", bg='#E3F2FD').pack(side='left')
        #     entry = tk.Entry(region_inputs, textvariable=self.template_region_vars[key], width=6, font=('Arial', 10), relief='solid', borderwidth=1, state='readonly')
        #     entry.pack(side='left', padx=(2,8), ipady=4)
        #     self.template_region_entries[key] = entry
        
        # HIDDEN: Helper text - preserved
        # tk.Label(region_frame, text=(
        #     'Để trống để dùng biên cửa sổ game.' if self.lang=='vi' else 'Leave blank to use game window bounds.'
        # ), bg='#E3F2FD', fg='#757575', font=('Arial', 8), anchor='w').pack(fill='x', pady=(4,6))
        
        # HIDDEN: Legacy action buttons - preserved for migration
        # region_btns = tk.Frame(region_frame, bg='#E3F2FD'); region_btns.pack(fill='x')
        # self._make_icon_button(region_btns, 'template', '🖼️', 'tip_pick_region', command=self._pick_template_region, bg='#1976D2', fg='white', relief='flat', padx=10, pady=6, font=('Arial', 9, 'bold')).pack(side='left')
        # self._make_icon_button(region_btns, 'search', '🔍', 'tip_test_recognition', command=self._test_template_recognition, bg='#455A64', fg='white', relief='flat', padx=10, pady=6, font=('Arial', 9, 'bold')).pack(side='left', padx=(8,0))
        # self._make_icon_button(region_btns, 'info', '📋', 'tip_auto_detect', command=self._auto_detect_template_region, bg='#00897B', fg='white', relief='flat', padx=10, pady=6, font=('Arial', 9, 'bold')).pack(side='left', padx=(8,0))
        
        # ============================================================================
        # NEW: Setup Wizard Vision - Modern replacement for legacy region tools
        # ============================================================================
        
        wizard_frame = tk.Frame(form_body, bg='#E8F5E9', relief='solid', borderwidth=1)
        wizard_frame.pack(fill='x', pady=(0,12), padx=2)
        
        # Hint text above button
        hint_text = (
            'Xem thêm về các chức năng sắp được nâng cấp bằng cách nhấp vào nút bên dưới'
            if self.lang == 'vi' else
            'Click the button below to learn about upcoming feature upgrades'
        )
        tk.Label(wizard_frame, text=hint_text, bg='#E8F5E9', fg='#558B2F', 
                font=('Arial', 8, 'italic'), anchor='w', wraplength=400).pack(fill='x', padx=10, pady=(8,4))
        
        # Setup Wizard Vision button
        wizard_btn_frame = tk.Frame(wizard_frame, bg='#E8F5E9')
        wizard_btn_frame.pack(fill='x', padx=10, pady=(0,8))
        
        wizard_btn_text = '🔮 Setup Wizard Vision' if self.lang == 'en' else '🔮 Thiết Lập Vision Nâng Cao'
        wizard_btn = tk.Button(
            wizard_btn_frame,
            text=wizard_btn_text,
            command=self._open_setup_wizard_vision,
            bg='#66BB6A', fg='white', relief='flat',
            padx=15, pady=8, font=('Arial', 10, 'bold'),
            cursor='hand2'
        )
        wizard_btn.pack(side='left')

        # No Save/Cancel buttons; changes are applied immediately and persisted with Apply All (top-right)

        # Bind auto-apply traces for form fields
        self._suspend_template_var_traces = False
        try:
            self.template_name_var.trace('w', lambda *args: self._on_template_name_change())
            self.template_path_var.trace('w', lambda *args: self._on_template_path_change())
            self.template_threshold_var.trace('w', lambda *args: self._on_template_threshold_change())
            # Region change traces
            for v in self.template_region_vars.values():
                v.trace('w', lambda *args: self._on_template_region_change())
        except Exception:
            pass

        # Initial empty preview
        self._update_template_preview(None)
        # Auto-select first template if exists
        try:
            if not self.template_tree:
                return
            items = self.template_tree.get_children()
            if items:
                self.template_tree.selection_set(items[0])
                self.template_tree.focus(items[0])
                self._on_template_tree_select(None)
        except Exception:
            pass
    
    def _on_template_tree_select(self, event):
        """Handle template selection: show preview and open inline edit immediately."""
        if not self.template_tree:
            return
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
            # Region fields
            region = template.get('region') or {}
            try:
                l = str(int(region.get('left', ''))) if isinstance(region, dict) and str(region.get('left', '')).strip() != '' else ''
                t = str(int(region.get('top', ''))) if isinstance(region, dict) and str(region.get('top', '')).strip() != '' else ''
                w = str(int(region.get('width', ''))) if isinstance(region, dict) and str(region.get('width', '')).strip() != '' else ''
                h = str(int(region.get('height', ''))) if isinstance(region, dict) and str(region.get('height', '')).strip() != '' else ''
            except Exception:
                l = t = w = h = ''
            if hasattr(self, 'template_region_vars'):
                self.template_region_vars['left'].set(l)
                self.template_region_vars['top'].set(t)
                self.template_region_vars['width'].set(w)
                self.template_region_vars['height'].set(h)
        finally:
            self._suspend_template_var_traces = False
        self.template_form_mode = 'edit'
        self.template_form_edit_index = idx
        # Lock fields after selection
        self._lock_template_fields()
        # Hide badge when just viewing (locked state) - no editing yet
        self._hide_template_badge()

    # === Template Lock/Unlock Management ===
    def _lock_template_fields(self):
        """Lock all template edit fields."""
        self.template_locked = True
        try:
            if self.template_name_entry:
                self.template_name_entry.config(state='readonly')
            if self.template_threshold_entry:
                self.template_threshold_entry.config(state='readonly')
            for entry in self.template_region_entries.values():
                entry.config(state='readonly')
        except Exception:
            pass
    
    def _unlock_template_fields(self):
        """Unlock all template edit fields for editing."""
        self.template_locked = False
        self.template_temp_saved = False  # Reset temp save status
        try:
            if self.template_name_entry:
                self.template_name_entry.config(state='normal')
            if self.template_threshold_entry:
                self.template_threshold_entry.config(state='normal')
            for entry in self.template_region_entries.values():
                entry.config(state='normal')
            
            # Show "Đang chỉnh sửa" badge (orange)
            self._show_editing_badge()
        except Exception:
            pass
    
    def _toggle_template_edit(self):
        """Toggle between locked (view) and unlocked (edit) mode."""
        if self.template_locked:
            # Unlock for editing
            self._unlock_template_fields()
            # Update button icon to save.ico
            self._update_toggle_button_icon('save', '💾', 'tip_template_save_temp')
        else:
            # Save mode - save immediately
            self._save_template_immediately()
    
    def _update_toggle_button_icon(self, icon_name: str, fallback: str, tooltip_key: str):
        """Update toggle button icon and tooltip."""
        if not self.template_toggle_btn:
            return
        try:
            # Get new icon
            new_icon = self._icon(icon_name, fallback)
            if new_icon:
                self.template_toggle_btn.config(image=new_icon)
                # Keep reference
                if not hasattr(self, '_toggle_btn_icons'):
                    self._toggle_btn_icons = []
                self._toggle_btn_icons.append(new_icon)
            else:
                # Fallback to text
                self.template_toggle_btn.config(text=fallback)
            
            # Update tooltip
            try:
                from lib.ui.tooltip import attach_i18n_tooltip
                # Unbind old tooltip
                if hasattr(self.template_toggle_btn, '_i18n_tooltip'):
                    old_tooltip = getattr(self.template_toggle_btn, '_i18n_tooltip')
                    try:
                        self.template_toggle_btn.unbind('<Enter>')
                        self.template_toggle_btn.unbind('<Leave>')
                        self.template_toggle_btn.unbind('<ButtonPress>')
                    except Exception:
                        pass
                # Attach new tooltip
                attach_i18n_tooltip(
                    self.template_toggle_btn,
                    tooltip_key,
                    'library_manager',
                    lambda: self.lang
                )
            except Exception:
                pass
        except Exception:
            pass
    
    def _save_template_immediately(self):
        """Save current template data immediately to lib/data/monsters.json and copy images to assets."""
        try:
            # Get current template
            tmpl = self._get_current_template_ref()
            if not tmpl:
                return
            
            # Copy image from tmp to assets if needed
            img_path = tmpl.get('path', '')
            if img_path and 'tmp' in img_path.lower():
                # Copy from tmp/captures/ to assets/images/monsters/
                src_path = Path(img_path)
                if src_path.exists():
                    # Create destination directory
                    dest_dir = self.assets_mon_dir
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate destination filename
                    dest_filename = src_path.name
                    dest_path = dest_dir / dest_filename
                    
                    # Copy file
                    try:
                        shutil.copy2(src_path, dest_path)
                        # Update path in template to use relative path
                        rel_path = f"assets/images/monsters/{dest_filename}"
                        tmpl['path'] = rel_path
                    except Exception as e:
                        print(f"Failed to copy image: {e}")
            
            # Save monsters to lib/data/monsters.json
            data_dir = self.project_root / 'lib' / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            monsters_path = data_dir / 'monsters.json'
            
            with open(monsters_path, 'w', encoding='utf-8') as f:
                json.dump(self.monsters, f, indent=2, ensure_ascii=False)
            
            # Lock fields again and switch back to edit icon
            self._lock_template_fields()
            self._update_toggle_button_icon('edit', '✏️', 'tip_template_edit')
            
            # Show "Đã lưu" badge (green) - will auto-hide after 3s
            self._show_saved_badge()
            
            # Mark as saved (no more changes)
            self.template_temp_saved = True
            
        except Exception as e:
            messagebox.showerror(
                'Save Error' if self.lang == 'en' else 'Lỗi Lưu',
                f"Failed to save template: {e}" if self.lang == 'en'
                else f"Không thể lưu template: {e}"
            )
    
    def _show_editing_badge(self):
        """Show 'Đang chỉnh sửa' badge (orange background) for template editing."""
        try:
            if not self.template_badge:
                return
            
            badge_text = 'Editing' if self.lang == 'en' else 'Đang chỉnh sửa'
            self.template_badge.config(text=f'  {badge_text}  ', bg='#FF9800')  # Orange
            self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')
            
        except Exception:
            pass
    
    def _show_saved_badge(self):
        """Show 'Đã lưu' badge (green background) for template save."""
        try:
            if not self.template_badge:
                return
            
            badge_text = 'Saved' if self.lang == 'en' else 'Đã lưu'
            self.template_badge.config(text=f'  {badge_text}  ', bg='#4CAF50')  # Green
            self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')
            
            # Hide after 3 seconds
            def hide_badge():
                try:
                    if self.template_badge:
                        self.template_badge.place_forget()
                except Exception:
                    pass
            
            self.after(3000, hide_badge)
            
        except Exception:
            pass
    
    def _hide_template_badge(self):
        """Hide template badge (used when viewing locked template)."""
        try:
            if self.template_badge:
                self.template_badge.place_forget()
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
            if not self.template_tree:
                raise Exception('template_tree not ready')
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
        # Don't apply changes if template is locked
        if getattr(self, 'template_locked', True):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        tmpl['name'] = self.template_name_var.get().strip()
        self.changes_made['monsters_changed'] = True
        # Badge already shown by unlock action - no need to mark unsaved here
        # Update name label and tree text
        if hasattr(self, 'template_name_label'):
            self.template_name_label.config(text=tmpl['name'])
        try:
            if not self.template_tree:
                return
            sel = self.template_tree.selection()
            if sel:
                self.template_tree.set(sel[0], 'name', tmpl['name'])
        except Exception:
            pass

    def _on_template_path_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        # Don't apply changes if template is locked
        if getattr(self, 'template_locked', True):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        tmpl['path'] = self.template_path_var.get().strip()
        self.changes_made['monsters_changed'] = True
        # Badge already shown by unlock action - no need to mark unsaved here
        # Refresh preview
        self._update_template_preview(tmpl)

    def _on_template_threshold_change(self):
        if getattr(self, '_suspend_template_var_traces', False):
            return
        # Don't apply changes if template is locked
        if getattr(self, 'template_locked', True):
            return
        tmpl = self._get_current_template_ref()
        if tmpl is None:
            return
        val = self.template_threshold_var.get().strip()
        try:
            tmpl['threshold'] = float(val)
            self.changes_made['monsters_changed'] = True
            # Badge already shown by unlock action - no need to mark unsaved here
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
        # Fill region from capture bbox if region fields are blank
        try:
            if bbox and hasattr(self, 'template_region_vars') and not any(v.get().strip() for v in self.template_region_vars.values()):
                l,t,w,h = bbox
                self.template_region_vars['left'].set(str(l))
                self.template_region_vars['top'].set(str(t))
                self.template_region_vars['width'].set(str(w))
                self.template_region_vars['height'].set(str(h))
                self._on_template_region_change()
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
            # Always show a fixed 300x300 placeholder
            try:
                ph_key = '__blank_300x300'
                photo = self._thumb_cache.get(ph_key)
                if photo is None:
                    if self.pil_available and Image is not None and ImageTk is not None:  # type: ignore[attr-defined]
                        bg = Image.new('RGBA', (300, 300), (250, 250, 250, 255))  # type: ignore[attr-defined]
                        photo = ImageTk.PhotoImage(bg)  # type: ignore[attr-defined]
                    else:
                        # Fallback to Tk blank image
                        photo = tk.PhotoImage(width=300, height=300)
                    self._thumb_cache[ph_key] = photo
                self.template_preview_label.config(image=photo, text='')
            except Exception:
                self.template_preview_label.config(image='', text='')
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
                cache_key = path + '_preview_300x300'
                photo = self._thumb_cache.get(cache_key)
                if photo is None:
                    img = Image.open(path)  # type: ignore[attr-defined]
                    # Ensure RGB/RGBA
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA')
                    w, h = img.size
                    # Fit into 300x300 preserving aspect ratio
                    if w > 0 and h > 0:
                        scale = min(300 / float(w), 300 / float(h))
                        new_w = max(1, int(round(w * scale)))
                        new_h = max(1, int(round(h * scale)))
                    else:
                        new_w, new_h = 300, 300
                    img_resized = img.resize((new_w, new_h), Image.LANCZOS)  # type: ignore[attr-defined]
                    # Compose on 300x300 background (match preview bg #FAFAFA)
                    bg = Image.new('RGBA', (300, 300), (250, 250, 250, 255))  # type: ignore[attr-defined]
                    off_x = (300 - new_w) // 2
                    off_y = (300 - new_h) // 2
                    try:
                        bg.paste(img_resized, (off_x, off_y), img_resized)
                    except Exception:
                        bg.paste(img_resized, (off_x, off_y))
                    photo = ImageTk.PhotoImage(bg)  # type: ignore[attr-defined]
                    self._thumb_cache[cache_key] = photo
                self.template_preview_label.config(image=photo, text='')
            except Exception:
                # On failure, show blank placeholder 300x300
                try:
                    ph_key = '__blank_300x300'
                    photo = self._thumb_cache.get(ph_key)
                    if photo is None:
                        if self.pil_available and Image is not None and ImageTk is not None:  # type: ignore[attr-defined]
                            bg = Image.new('RGBA', (300, 300), (250, 250, 250, 255))  # type: ignore[attr-defined]
                            photo = ImageTk.PhotoImage(bg)  # type: ignore[attr-defined]
                        else:
                            photo = tk.PhotoImage(width=300, height=300)
                        self._thumb_cache[ph_key] = photo
                    self.template_preview_label.config(image=photo, text='')
                except Exception:
                    self.template_preview_label.config(image='', text='')
        else:
            # No path or PIL not available: show fixed placeholder
            try:
                ph_key = '__blank_300x300'
                photo = self._thumb_cache.get(ph_key)
                if photo is None:
                    if self.pil_available and Image is not None and ImageTk is not None:  # type: ignore[attr-defined]
                        bg = Image.new('RGBA', (300, 300), (250, 250, 250, 255))  # type: ignore[attr-defined]
                        photo = ImageTk.PhotoImage(bg)  # type: ignore[attr-defined]
                    else:
                        photo = tk.PhotoImage(width=300, height=300)
                    self._thumb_cache[ph_key] = photo
                self.template_preview_label.config(image=photo, text='')
            except Exception:
                self.template_preview_label.config(image='', text='')

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
            if not self.template_tree:
                return
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
        if not self.template_tree:
            return
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
        if not self.template_tree:
            return
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
        Build Skill Library tab with left list, inline edit form, and image preview.
        Pattern matches Monster Tab structure for consistency.
        """
        # Main container
        main_container = tk.Frame(parent, bg='#F5F5F5')
        main_container.pack(fill='both', expand=True)

        # Layout: left list (2) | right area (10)
        main_container.grid_columnconfigure(0, weight=2, uniform='column')
        main_container.grid_columnconfigure(1, weight=10, uniform='column')
        main_container.grid_rowconfigure(0, weight=1)

        # Left: Skill List
        left_frame = tk.Frame(main_container, bg='#FFFFFF')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)

        # Header with Add button
        header = tk.Frame(left_frame, bg='#FFFDE7', height=44)
        header.pack(fill='x')
        header.pack_propagate(False)

        self._make_icon_button(
            header, 'add', '➕', 'tip_add_skill',
            command=self._add_skill,
            bg='#4CAF50', fg='white', relief='flat',
            font=UI.FONT_BUTTON, padx=self.ui_btn_padx, pady=self.ui_btn_pady
        ).pack(side='right', padx=10, pady=6)

        # Search bar
        search_frame = tk.Frame(left_frame, bg=UI.BG_DEFAULT, pady=12, padx=15)
        search_frame.pack(fill='x')
        search_container = tk.Frame(search_frame, bg=UI.BG_PANEL, highlightbackground='#E0E0E0', highlightthickness=1)
        search_container.pack(fill='x')
        search_img = self._icon('search', '🔍')
        search_txt = self._icon_text('search', '🔍')
        if search_img:
            try:
                tk.Label(search_container, image=search_img, text='', bg='#F5F5F5').pack(side='left', padx=(10, 5))
            except Exception:
                tk.Label(search_container, text=search_txt, font=('Segoe UI', 11), bg='#F5F5F5', fg='#757575').pack(side='left', padx=(10, 5))
        else:
            tk.Label(search_container, text=search_txt, font=(UI.FONT_FAMILY, 11), bg=UI.BG_PANEL, fg=UI.COLOR_HINT).pack(side='left', padx=(10, 5))
        self.skill_search_var = tk.StringVar()
        self.skill_search_var.trace('w', lambda *args: self._filter_skill_list())
        tk.Entry(search_container, textvariable=self.skill_search_var, font=UI.FONT_TEXT, border=0, bg=UI.BG_PANEL, fg=UI.COLOR_TEXT).pack(side='left', fill='x', expand=True, pady=10, padx=(0, 10))

        # Type filter
        filter_frame = tk.Frame(left_frame, bg='#FFFFFF', pady=8, padx=15)
        filter_frame.pack(fill='x')
        tk.Label(filter_frame, text='Type:' if self.lang=='en' else 'Loại:', bg='#FFFFFF', font=UI.FONT_LABEL).pack(side='left', padx=(0,6))
        self.skill_type_filter_var = tk.StringVar(value='all')
        type_combo = ttk.Combobox(filter_frame, textvariable=self.skill_type_filter_var, state='readonly', width=12, 
                                   values=['all', 'attack', 'buff'])
        type_combo.pack(side='left')
        type_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_skill_list())

        # Treeview with columns
        list_frame = tk.Frame(left_frame, bg='#FFFFFF')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 12))
        vsb = tk.Scrollbar(list_frame, orient='vertical')
        hsb = tk.Scrollbar(list_frame, orient='horizontal')
        
        # Columns: Name, Key, Type
        self.skill_tree = ttk.Treeview(list_frame, columns=('key', 'type'), show='tree headings', 
                                       yscrollcommand=vsb.set, xscrollcommand=hsb.set, selectmode='browse')
        vsb.config(command=self.skill_tree.yview)
        hsb.config(command=self.skill_tree.xview)
        
        self.skill_tree.heading('#0', text='Name' if self.lang == 'en' else 'Tên')
        self.skill_tree.heading('key', text='Key' if self.lang == 'en' else 'Phím')
        self.skill_tree.heading('type', text='Type' if self.lang == 'en' else 'Loại')
        
        self.skill_tree.column('#0', width=160, minwidth=100)
        self.skill_tree.column('key', width=50, minwidth=40, anchor='center')
        self.skill_tree.column('type', width=70, minwidth=60, anchor='center')
        
        self.skill_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        self.skill_tree.bind('<<TreeviewSelect>>', self._on_skill_select)

        # Right: Details and Image Preview
        right_area = tk.Frame(main_container, bg='#FFFFFF')
        right_area.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        right_area.grid_rowconfigure(0, weight=3)  # Edit form takes 3
        right_area.grid_rowconfigure(1, weight=2)  # Image preview takes 2
        right_area.grid_columnconfigure(0, weight=1)

        # Top: Edit Form
        form_container = tk.Frame(right_area, bg='#FFFFFF')
        form_container.grid(row=0, column=0, sticky='nsew')
        form_container.grid_columnconfigure(0, weight=1)
        form_container.grid_rowconfigure(1, weight=1)
        
        # Title bar
        action_bar = tk.Frame(form_container, bg='#E3F2FD', height=44)
        action_bar.grid(row=0, column=0, sticky='ew')
        action_bar.grid_propagate(False)
        tk.Label(action_bar, text=('Skill Editor' if self.lang=='en' else 'Chỉnh Sửa Kỹ Năng'), 
                bg=UI.BG_SECTION, fg=UI.COLOR_PRIMARY_TEXT, font=UI.FONT_TITLE).pack(side='left', padx=12)
        
        # Details panel
        self.skill_details_panel = tk.Frame(form_container, bg='#FFFFFF')
        self.skill_details_panel.grid(row=1, column=0, sticky='nsew', padx=0)

        # Bottom: Image Preview
        preview_container = tk.Frame(right_area, bg='#FFFFFF')
        preview_container.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(1, weight=1)
        
        preview_bar = tk.Frame(preview_container, bg='#FFF3E0', height=36)
        preview_bar.grid(row=0, column=0, sticky='ew')
        preview_bar.grid_propagate(False)
        tk.Label(preview_bar, text=('Skill Image' if self.lang=='en' else 'Hình Ảnh Kỹ Năng'), 
                bg='#FFF3E0', fg='#E65100', font=UI.FONT_SECTION).pack(side='left', padx=12, pady=6)
        
        self.skill_preview_panel = tk.Frame(preview_container, bg='#FAFAFA')
        self.skill_preview_panel.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        # Initial population
        self._refresh_skill_tree()
        
        # Auto-select first skill if available
        try:
            first = self.skill_tree.get_children()
            if first:
                self.skill_tree.selection_set(first[0])
                self.skill_tree.focus(first[0])
                self._on_skill_select(None)
            else:
                self._show_skill_details(None)
        except Exception:
            self._show_skill_details(None)
    
    # -----------------
    # Skill Tab Handlers
    # -----------------
    
    def _filter_skill_list(self):
        """Filter skill list based on search text and type filter."""
        search_text = self.skill_search_var.get().lower()
        skill_type = self.skill_type_filter_var.get()
        
        # Clear tree
        if not self.skill_tree:
            return
        for item in self.skill_tree.get_children():
            self.skill_tree.delete(item)
        
        # Re-add filtered skills
        for skill in self.skills:
            name = skill.get('name', '')
            stype = skill.get('type', 'attack')
            
            # Apply filters
            if search_text and search_text not in name.lower():
                continue
            if skill_type != 'all' and stype != skill_type:
                continue
                
            self._add_skill_to_tree(skill)
    
    def _refresh_skill_tree(self):
        """Refresh the skill tree with current data."""
        # Clear tree
        if not self.skill_tree:
            return
        for item in self.skill_tree.get_children():
            self.skill_tree.delete(item)
        
        # Add all skills (respect current filters)
        self._filter_skill_list()
    
    def _add_skill_to_tree(self, skill: dict):
        """Add a single skill to the tree."""
        name = skill.get('name', 'Unknown')
        key = skill.get('key', '')
        skill_type = skill.get('type', 'attack')
        
        # Type display
        type_display = '⚔️' if skill_type == 'attack' else '🛡️'
        if self.lang == 'en':
            type_text = skill_type.capitalize()
        else:
            type_text = 'Tấn công' if skill_type == 'attack' else 'Buff'
        
        if not self.skill_tree:
            return
        self.skill_tree.insert(
            '',
            'end',
            text=f"  {name}",
            values=(key, f"{type_display} {type_text}"),
            tags=('skill',)
        )
    
    def _on_skill_select(self, event):
        """Handle skill selection in tree."""
        if not self.skill_tree:
            return
        selection = self.skill_tree.selection()
        if not selection:
            self._show_skill_details(None)
            return
        
        # Get selected item index
        item = selection[0]
        item_index = self.skill_tree.index(item)
        
        # Get filtered skills list (matching tree order)
        search_text = self.skill_search_var.get().lower()
        skill_type = self.skill_type_filter_var.get()
        filtered_skills = []
        for skill in self.skills:
            name = skill.get('name', '')
            stype = skill.get('type', 'attack')
            if search_text and search_text not in name.lower():
                continue
            if skill_type != 'all' and stype != skill_type:
                continue
            filtered_skills.append(skill)
        
        # Show details for selected skill
        if 0 <= item_index < len(filtered_skills):
            self._skill_edit_open = True
            self._show_skill_details(filtered_skills[item_index])
    
    def _show_skill_details(self, skill: Optional[dict]):
        """Show skill information in edit form and image preview."""
        # Clear current content
        if hasattr(self, 'skill_details_panel') and self.skill_details_panel:
            try:
                for w in self.skill_details_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass

        if skill is None:
            if not self.skill_details_panel:
                return
            tk.Label(self.skill_details_panel, text='← ' + ('Select a skill to edit' if self.lang=='en' else 'Chọn kỹ năng để sửa'),
                     bg='#FFFFFF', fg='#9E9E9E', font=self.ui_font_label).pack(padx=18, pady=18, anchor='w')
            # Clear preview
            self._show_skill_image_preview(None)
            return

        # Store current and render edit form
        self.current_skill = skill
        if self.skill_details_panel:
            self._render_skill_edit_form(self.skill_details_panel)
        # Show image preview
        self._show_skill_image_preview(skill)
    
    def _render_skill_edit_form(self, parent: tk.Frame):
        """Render the inline skill edit form."""
        if not hasattr(self, 'current_skill') or self.current_skill is None:
            return
            
        form = tk.Frame(parent, bg='#E3F2FD', highlightbackground='#2196F3', highlightthickness=2)
        form.pack(fill='both', expand=False, pady=(12, 0))

        # Title
        title = tk.Frame(form, bg='#2196F3', height=36)
        title.pack(fill='x')
        title.pack_propagate(False)
        tk.Label(
            title,
            text='✏️ ' + ('Edit Skill' if self.lang=='en' else 'Sửa Kỹ Năng'),
            bg='#2196F3',
            fg='white',
            font=self.ui_font_section
        ).pack(padx=10, pady=6)

        body = tk.Frame(form, bg='#E3F2FD')
        body.pack(fill='both', expand=True, padx=14, pady=12)

        # Fields
        self.skill_name_var = tk.StringVar(value=self.current_skill.get('name',''))
        self.skill_key_var = tk.StringVar(value=self.current_skill.get('key',''))
        self.skill_type_var = tk.StringVar(value=self.current_skill.get('type','attack'))
        self.skill_cooldown_var = tk.StringVar(value=str(self.current_skill.get('cooldown',0.0)))
        self.skill_cast_time_var = tk.StringVar(value=str(self.current_skill.get('cast_time',0.0)))

        # Row 0: Name
        tk.Label(body, text=('Name' if self.lang=='en' else 'Tên'), bg='#E3F2FD', font=self.ui_font_label).grid(row=0, column=0, sticky='w', pady=(0,6))
        tk.Entry(body, textvariable=self.skill_name_var, font=self.ui_font_text).grid(row=0, column=1, columnspan=3, sticky='ew', pady=(0,6))

        # Row 1: Key & Type
        tk.Label(body, text=('Key' if self.lang=='en' else 'Phím'), bg='#E3F2FD', font=self.ui_font_label).grid(row=1, column=0, sticky='w', pady=(0,6))
        tk.Entry(body, textvariable=self.skill_key_var, width=8, font=self.ui_font_text).grid(row=1, column=1, sticky='w', pady=(0,6))

        tk.Label(body, text=('Type' if self.lang=='en' else 'Loại'), bg='#E3F2FD', font=self.ui_font_label).grid(row=1, column=2, sticky='w', padx=(12,0), pady=(0,6))
        type_combo = ttk.Combobox(body, textvariable=self.skill_type_var, state='readonly', width=12, values=['attack', 'buff'])
        type_combo.grid(row=1, column=3, sticky='w', pady=(0,6))

        # Row 2: Cooldown & Cast Time
        tk.Label(body, text=('Cooldown (s)' if self.lang=='en' else 'Hồi chiêu (s)'), bg='#E3F2FD', font=self.ui_font_label).grid(row=2, column=0, sticky='w', pady=(0,6))
        tk.Entry(body, textvariable=self.skill_cooldown_var, width=12, font=self.ui_font_text).grid(row=2, column=1, sticky='w', pady=(0,6))

        tk.Label(body, text=('Cast Time (s)' if self.lang=='en' else 'Thời gian thi (s)'), bg='#E3F2FD', font=self.ui_font_label).grid(row=2, column=2, sticky='w', padx=(12,0), pady=(0,6))
        tk.Entry(body, textvariable=self.skill_cast_time_var, width=12, font=self.ui_font_text).grid(row=2, column=3, sticky='w', pady=(0,6))

        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(3, weight=0)
    
    def _show_skill_image_preview(self, skill: Optional[dict]):
        """Show skill image preview in bottom panel."""
        # Clear preview panel
        if hasattr(self, 'skill_preview_panel') and self.skill_preview_panel:
            try:
                for w in self.skill_preview_panel.winfo_children():
                    w.destroy()
            except Exception:
                pass
        
        if skill is None or not self.skill_preview_panel:
            return
        
        image_path = skill.get('image', '')
        if not image_path or not Path(image_path).exists():
            tk.Label(self.skill_preview_panel, 
                    text='📷 ' + ('No image captured' if self.lang=='en' else 'Chưa có hình ảnh'),
                    bg='#FAFAFA', fg='#9E9E9E', font=self.ui_font_label).pack(expand=True)
            
            # Add capture button
            btn_frame = tk.Frame(self.skill_preview_panel, bg='#FAFAFA')
            btn_frame.pack(side='bottom', pady=10)
            self._make_icon_button(
                btn_frame, 'capture', '📸', 'tip_capture_skill_image',
                command=self._capture_skill_image,
                bg='#2196F3', fg='white', relief='flat',
                font=UI.FONT_BUTTON, padx=self.ui_btn_padx, pady=self.ui_btn_pady
            ).pack()
            return
        
        # Show image
        try:
            if Image:
                img = Image.open(image_path)
                # Resize to fit preview (max 400x300)
                max_w, max_h = 400, 300
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(self.skill_preview_panel, image=photo, bg='#FAFAFA')
                try:
                    if not hasattr(self, '_image_refs'):
                        self._image_refs = []
                    self._image_refs.append(photo)
                except Exception:
                    pass
                label.pack(expand=True, pady=10)
                
                # Action buttons
                btn_frame = tk.Frame(self.skill_preview_panel, bg='#FAFAFA')
                btn_frame.pack(side='bottom', pady=10)
                
                self._make_icon_button(
                    btn_frame, 'capture', '📸', 'tip_recapture_skill_image',
                    command=self._capture_skill_image,
                    bg='#2196F3', fg='white', relief='flat',
                    font=UI.FONT_BUTTON, padx=self.ui_btn_padx, pady=self.ui_btn_pady
                ).pack(side='left', padx=4)
                
                self._make_icon_button(
                    btn_frame, 'delete', '🗑️', 'tip_delete_skill_image',
                    command=self._delete_skill_image,
                    bg='#f44336', fg='white', relief='flat',
                    font=UI.FONT_BUTTON, padx=self.ui_btn_padx, pady=self.ui_btn_pady
                ).pack(side='left', padx=4)
            else:
                tk.Label(self.skill_preview_panel, text=f"Image: {Path(image_path).name}",
                        bg='#FAFAFA', fg='#666', font=self.ui_font_label).pack(expand=True)
        except Exception as e:
            tk.Label(self.skill_preview_panel, text=f"Error loading image: {e}",
                    bg='#FAFAFA', fg='#f44336', font=self.ui_font_label).pack(expand=True)
    
    def _add_skill(self):
        """Open dialog to add new skill."""
        dialog = SkillDialog(self, self.lang, mode='add', icon_helper=icon_helper, i18n_registry=i18n_t)
        
        if dialog.result:
            # Add new skill
            self.skills.append(dialog.result)
            self.changes_made['skills_changed'] = True
            self._mark_unsaved(True)
            
            # Refresh tree
            self._refresh_skill_tree()
            
            # Status message
            messagebox.showinfo(
                'Added' if self.lang == 'en' else 'Đã Thêm',
                f"Skill '{dialog.result.get('name', 'Unknown')}' has been added." if self.lang == 'en'
                else f"Kỹ năng '{dialog.result.get('name', 'Unknown')}' đã được thêm."
            )
    
    def _capture_skill_image(self):
        """Capture skill image from screen."""
        if not hasattr(self, 'current_skill') or self.current_skill is None:
            messagebox.showwarning(
                'No Skill' if self.lang=='en' else 'Chưa Chọn Kỹ Năng',
                'Please select a skill first.' if self.lang=='en' else 'Vui lòng chọn một kỹ năng trước.'
            )
            return
        
        # Bring game window to front
        try:
            pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
            hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
            if pid:
                self._bring_window_to_front_by_pid(int(pid))
            elif hwnd_cfg:
                self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
        except Exception:
            pass
        
        # Use capture helper
        if capture_region_and_save:
            try:
                # Pre-wait hook to bring window forward
                def _pre_wait_bring():
                    try:
                        pid = self.hunt_cfg.get('window_pid') if isinstance(self.hunt_cfg, dict) else None
                        hwnd_cfg = self.hunt_cfg.get('window_hwnd') if isinstance(self.hunt_cfg, dict) else None
                        if pid:
                            self._bring_window_to_front_by_pid(int(pid))
                        elif hwnd_cfg:
                            self._bring_window_to_front_by_hwnd(int(hwnd_cfg))
                    except Exception:
                        pass
                
                result = capture_region_and_save(
                    self, 
                    self.pil_available, 
                    self.current_skill.get('name', ''), 
                    self.lang, 
                    pre_wait_hook=_pre_wait_bring,
                    capture_type='skill'  # Save to assets/images/skills/
                )
                
                if result:
                    # result is (path, bbox) tuple
                    image_path, bbox = result
                    # Update current skill
                    self.current_skill['image'] = image_path
                    self.changes_made['skills_changed'] = True
                    self._mark_unsaved(True)
                    
                    # Refresh preview
                    self._show_skill_image_preview(self.current_skill)
            except Exception as e:
                messagebox.showerror(
                    'Capture Error' if self.lang == 'en' else 'Lỗi Chụp Ảnh',
                    f"Failed to capture image: {e}"
                )
    
    def _delete_skill_image(self):
        """Delete skill image."""
        if not hasattr(self, 'current_skill') or self.current_skill is None:
            return
        
        # Confirm
        if not messagebox.askyesno(
            'Confirm' if self.lang == 'en' else 'Xác Nhận',
            'Delete this skill image?' if self.lang == 'en' else 'Xóa hình ảnh kỹ năng này?'
        ):
            return
        
        # Remove image
        self.current_skill['image'] = ''
        self.changes_made['skills_changed'] = True
        self._mark_unsaved(True)
        
        # Refresh preview
        self._show_skill_image_preview(self.current_skill)
    
    def _save_current_skill_inline(self):
        """Save current skill changes from inline form."""
        if not hasattr(self, 'current_skill') or self.current_skill is None:
            return
        
        try:
            # Validate and update current_skill
            self.current_skill['name'] = self.skill_name_var.get().strip()
            self.current_skill['key'] = self.skill_key_var.get().strip().upper()
            self.current_skill['type'] = self.skill_type_var.get()
            self.current_skill['cooldown'] = float(self.skill_cooldown_var.get())
            self.current_skill['cast_time'] = float(self.skill_cast_time_var.get())
            
            # Validate values
            if not self.current_skill['name']:
                raise ValueError('Name cannot be empty' if self.lang=='en' else 'Tên không được để trống')
            if not self.current_skill['key']:
                raise ValueError('Key cannot be empty' if self.lang=='en' else 'Phím không được để trống')
            if self.current_skill['cooldown'] < 0:
                raise ValueError('Cooldown must be non-negative' if self.lang=='en' else 'Thời gian hồi chiêu phải không âm')
            if self.current_skill['cast_time'] < 0:
                raise ValueError('Cast time must be non-negative' if self.lang=='en' else 'Thời gian thi triển phải không âm')
                
        except ValueError as e:
            messagebox.showerror('Invalid Input' if self.lang=='en' else 'Dữ Liệu Không Hợp Lệ', str(e))
            return
        except Exception as e:
            messagebox.showerror('Error' if self.lang=='en' else 'Lỗi', str(e))
            return
        
        self.changes_made['skills_changed'] = True
        self._mark_unsaved(True)
        self._refresh_skill_tree()
        
        # Keep focus on same skill
        self._show_skill_details(self.current_skill)
    
    def _delete_current_skill_inline(self):
        """Delete current skill."""
        if not hasattr(self, 'current_skill') or self.current_skill is None:
            return
        
        name = self.current_skill.get('name', 'Unknown')
        title = 'Confirm Delete' if self.lang=='en' else 'Xác Nhận Xóa'
        msg = f"Delete skill '{name}'?" if self.lang=='en' else f"Xóa kỹ năng '{name}'?"
        
        if messagebox.askyesno(title, msg, parent=self):
            try:
                idx = self.skills.index(self.current_skill)
            except ValueError:
                idx = -1
            
            if idx >= 0:
                del self.skills[idx]
                self.changes_made['skills_changed'] = True
                self._mark_unsaved(True)
                self._refresh_skill_tree()
                self._show_skill_details(None)
    
    def _build_rotation_tab(self, parent: tk.Frame):
        """
        Build Skill Rotation Builder tab
        
        Sprint 19 Task #5: Skill Rotation Builder with precise timing
        - Select skills from hunt_config
        - Arrange in specific order
        - Calculate precise rotation with cooldown tracking
        - Save rotation sequence to hunt_config
        """
        try:
            from lib.features.skill_rotation.ui_integration import SkillRotationUI
            
            # Create rotation UI
            self.rotation_ui = SkillRotationUI(parent, self)
            
        except ImportError as e:
            # Fallback if module not available
            error_frame = tk.Frame(parent, bg='white')
            error_frame.pack(fill='both', expand=True)
            
            tk.Label(
                error_frame,
                text=f"⚠️ Skill Rotation module not available\n\n{str(e)}",
                font=('Arial', 12),
                fg='#F44336',
                bg='white',
                justify='center'
            ).pack(expand=True)
    
    def _apply_all_changes(self):
        """Refresh monster dropdown in timing tab"""
        try:
            # Use self.monsters instead of data_manager
            names = [m['name'] for m in self.monsters]
            self.timing_monster_combo['values'] = names
            if names:
                self.timing_monster_combo.current(0)
                self._on_timing_monster_select(None)
        except Exception as e:
            print(f"Error loading monsters for timing tab: {e}")
    
    def _refresh_timing_skills(self):
        """Refresh skill dropdown in timing tab"""
        try:
            # Use self.skills instead of data_manager
            # Filter attack skills only
            attack_skills = [s for s in self.skills if s.get('type') == 'attack']
            names = [s['name'] for s in attack_skills]
            self.timing_skill_combo['values'] = names
            if names:
                self.timing_skill_combo.current(0)
                self._on_timing_skill_select(None)
        except Exception as e:
            print(f"Error loading skills for timing tab: {e}")
    
    def _update_text_widget(self, widget, text):
        """Helper to update read-only text widget"""
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', text)
        widget.config(state='disabled')
    
    def _on_timing_monster_select(self, event):
        """Handle monster selection in timing tab"""
        name = self.timing_monster_var.get()
        if not name:
            return
        
        try:
            # Use self.monsters instead of data_manager
            monster = next((m for m in self.monsters if m['name'] == name), None)
            
            if monster:
                hp = monster.get('hp', 'N/A')
                damage = monster.get('damage_per_hit', 'N/A')
                desc = monster.get('description', 'N/A')
                
                info = (
                    f"HP: {hp:,}\n" if isinstance(hp, (int, float)) else f"HP: {hp}\n"
                    f"{'Damage per hit' if self.lang == 'en' else 'Sát thương/đòn'}: {damage:,}\n" if isinstance(damage, (int, float)) else f"Damage: {damage}\n"
                    f"{'Description' if self.lang == 'en' else 'Mô tả'}: {desc}"
                )
                self._update_text_widget(self.timing_monster_info, info)
                self.selected_timing_monster = monster
        except Exception as e:
            print(f"Error displaying monster info: {e}")
    
    def _on_timing_skill_select(self, event):
        """Handle skill selection in timing tab"""
        name = self.timing_skill_var.get()
        if not name:
            return
        
        try:
            # Use self.skills instead of data_manager
            skill = next((s for s in self.skills if s['name'] == name), None)
            
            if skill:
                cooldown = skill.get('cooldown', 'N/A')
                cast_time = skill.get('cast_time', 'N/A')
                skill_type = skill.get('type', 'N/A')
                
                info = (
                    f"{'Cooldown' if self.lang == 'en' else 'Hồi chiêu'}: {cooldown}s\n"
                    f"{'Cast time' if self.lang == 'en' else 'Thời gian thi triển'}: {cast_time}s\n"
                    f"{'Type' if self.lang == 'en' else 'Loại'}: {skill_type}"
                )
                self._update_text_widget(self.timing_skill_info, info)
                self.selected_timing_skill = skill
        except Exception as e:
            print(f"Error displaying skill info: {e}")
    
    def _on_timing_preset_change(self):
        """Handle attack speed preset change"""
        preset = self.timing_preset_var.get()
        
        preset_values = {
            'slow': 1.0,
            'normal': 2.0,
            'fast': 3.0,
            'very_fast': 4.0
        }
        
        if preset in preset_values:
            self.timing_aps_var.set(str(preset_values[preset]))
    
    def _calculate_timing(self):
        """Calculate optimal timing based on selections"""
        # Validate selections
        if not hasattr(self, 'selected_timing_monster'):
            messagebox.showwarning(
                self._t('error_title'),
                self._t('timing_no_monster')
            )
            return
        
        if not hasattr(self, 'selected_timing_skill'):
            messagebox.showwarning(
                self._t('error_title'),
                self._t('timing_no_skill')
            )
            return
        
        # Get attack speed
        try:
            aps = float(self.timing_aps_var.get())
            if aps <= 0:
                raise ValueError("APS must be positive")
        except ValueError:
            messagebox.showerror(
                self._t('error_title'),
                "Invalid attack speed value" if self.lang == 'en' 
                else "Giá trị tốc độ đánh không hợp lệ"
            )
            return
        
        # Calculate
        try:
            from lib.features.timing.calculator import calculate_timing_from_monster
            
            # Get skill rotation from hunt_cfg (attack skills only)
            skill_rotation = []
            if hasattr(self, 'hunt_cfg') and 'skill_slots' in self.hunt_cfg:
                skill_rotation = [s for s in self.hunt_cfg['skill_slots'] if s.get('type') == 'attack']
            
            # Calculate with skill rotation if available
            if skill_rotation:
                result = calculate_timing_from_monster(
                    self.selected_timing_monster,
                    attacks_per_second=aps,  # Fallback if no skills
                    skill_rotation=skill_rotation  # Use actual skills!
                )
            else:
                # Fallback to generic APS
                result = calculate_timing_from_monster(
                    self.selected_timing_monster,
                    attacks_per_second=aps
                )
            
            if result is None:
                messagebox.showerror(
                    self._t('error_title'),
                    self._t('timing_no_data')
                )
                return
            
            # Format and display results
            self._display_timing_results(result)
            self.timing_calculation_result = result
            self.timing_apply_btn.config(state='normal')
            
            messagebox.showinfo(
                self._t('success_title'),
                self._t('timing_calc_success')
            )
            
        except Exception as e:
            messagebox.showerror(
                self._t('error_title'),
                f"{'Calculation error' if self.lang == 'en' else 'Lỗi tính toán'}: {str(e)}"
            )
    
    def _display_timing_results(self, result):
        """Display calculation results in text widget"""
        if self.lang == 'vi':
            text = (
                f"{'='*50}\n"
                f"📊 {self._t('timing_analysis')}\n"
                f"{'='*50}\n\n"
                f"• {self._t('timing_hits_to_kill')}: {result.hits_to_kill} đòn\n"
                f"• {self._t('timing_time_per_hit')}: {1.0/result.attacks_per_second:.2f}s\n"
                f"• {self._t('timing_kill_time')}: {result.estimated_kill_time_sec:.2f}s\n\n"
                f"{'='*50}\n"
                f"⚙️ {self._t('timing_recommendations')}\n"
                f"{'='*50}\n\n"
                f"• {self._t('timing_lost_timeout')}: {result.lost_timeout_sec:.2f}s\n"
                f"  (Thời gian chờ giữa các đòn + {result.lost_timeout_margin*100:.0f}% an toàn)\n\n"
                f"• {self._t('timing_attack_duration')}: {result.attack_min_duration_sec:.2f}s\n"
                f"  (Thời gian hạ gục + {result.attack_duration_margin*100:.0f}% an toàn)\n\n"
                f"{'='*50}\n"
                f"🎯 {self._t('timing_confidence')}: "
            )
        else:
            text = (
                f"{'='*50}\n"
                f"📊 {self._t('timing_analysis')}\n"
                f"{'='*50}\n\n"
                f"• {self._t('timing_hits_to_kill')}: {result.hits_to_kill} hits\n"
                f"• {self._t('timing_time_per_hit')}: {1.0/result.attacks_per_second:.2f}s\n"
                f"• {self._t('timing_kill_time')}: {result.estimated_kill_time_sec:.2f}s\n\n"
                f"{'='*50}\n"
                f"⚙️ {self._t('timing_recommendations')}\n"
                f"{'='*50}\n\n"
                f"• {self._t('timing_lost_timeout')}: {result.lost_timeout_sec:.2f}s\n"
                f"  (Time between hits + {result.lost_timeout_margin*100:.0f}% safety margin)\n\n"
                f"• {self._t('timing_attack_duration')}: {result.attack_min_duration_sec:.2f}s\n"
                f"  (Kill time + {result.attack_duration_margin*100:.0f}% safety margin)\n\n"
                f"{'='*50}\n"
                f"🎯 {self._t('timing_confidence')}: "
            )
        
        # Add confidence
        confidence = self._get_timing_confidence(result)
        text += self._t(f'timing_confidence_{confidence}')
        text += f"\n{'='*50}\n"
        
        self._update_text_widget(self.timing_results, text)
        
        # Update preview
        self._update_timing_preview(result)
    
    def _update_timing_preview(self, result):
        """Update preview section with settings to be applied"""
        # Calculate base values for formula display
        time_per_hit = 1.0 / result.attacks_per_second
        
        if self.lang == 'vi':
            preview_text = (
                f"📋 CÁC CON SỐ SẼ ĐƯỢC LƯU VÀO MÁY:\n"
                f"{'─'*60}\n"
                f"📊 THÔNG TIN QUÁI VẬT:\n"
                f"  • Máu quái: {result.monster_hp:,.0f} HP\n"
                f"  • Sát thương 1 đòn: {result.damage_per_hit:,.0f}\n"
                f"  • Tốc độ đánh: {result.attacks_per_second:.2f} đòn/giây\n"
                f"  • Thời gian 1 đòn: {time_per_hit:.2f} giây\n"
                f"  • Cần đánh: {result.hits_to_kill} đòn\n"
                f"  • Tổng thời gian: {result.estimated_kill_time_sec:.2f} giây\n\n"
                f"⏱️  CÁC SỐ QUAN TRỌNG:\n\n"
                f"1️⃣ Nhấn phím giữ bao lâu?\n"
                f"   → {result.attack_press_ms} mili-giây (0.{result.attack_press_ms} giây)\n"
                f"   � Giống như bấm nút giữ rồi thả ra\n\n"
                f"2️⃣ Đổi quái sau bao lâu?\n"
                f"   → {result.target_cycle_delay:.2f} giây\n"
                f"   � Đợi lâu hơn 1 đòn đánh, tránh đổi lung tung\n\n"
                f"3️⃣ Tìm quái sau bao lâu?\n"
                f"   → {result.search_interval:.2f} giây\n"
                f"   � Tìm nhanh để phát hiện quái kịp thời\n\n"
                f"4️⃣ Đánh sau bao lâu?\n"
                f"   → {result.attack_interval:.2f} giây\n"
                f"   💡 Đánh nhanh hơn bình thường một chút\n\n"
                f"5️⃣ Quái mất bao lâu thì dừng?\n"
                f"   → {result.lost_timeout_sec:.2f} giây\n"
                f"   � Nếu không thấy quái quá lâu, nghĩa là chết rồi\n\n"
                f"6️⃣ Đánh tối thiểu bao lâu?\n"
                f"   → {result.attack_min_duration_sec:.2f} giây\n"
                f"   💡 Đánh đủ lâu, dù có lúc không thấy quái\n\n"
                f"{'─'*60}\n"
                f"🤖 AUTO SẼ LÀM GÌ KHI CHẠY?\n"
                f"{'─'*60}\n"
                f"1️⃣ TÌM QUÁI (cứ {result.search_interval:.2f} giây tìm 1 lần):\n"
                f"   • Nhìn màn hình tìm hình quái vật\n"
                f"   • Thấy quái → chuyển sang bước 2\n\n"
                f"2️⃣ CHỌN QUÁI:\n"
                f"   • Bấm phím Z để chọn quái\n"
                f"   • Đợi {result.target_cycle_delay:.2f} giây\n"
                f"   • Không chọn quái khác khi đang đánh\n\n"
                f"3️⃣ BẮT ĐẦU ĐÁNH (đánh {result.hits_to_kill} đòn):\n"
                f"   • Bấm phím tấn công giữ {result.attack_press_ms} mili-giây\n"
                f"   • Thả phím ra\n"
                f"   • Đợi {result.attack_interval:.2f} giây\n"
                f"   • Lặp lại: Đánh → Chờ → Đánh → Chờ...\n"
                f"   • Dự kiến hết ~{result.estimated_kill_time_sec:.1f} giây\n\n"
                f"4️⃣ KIỂM TRA QUÁI:\n"
                f"   • Nếu không thấy quái quá {result.lost_timeout_sec:.2f} giây:\n"
                f"     ❌ Dừng đánh (quái chết hoặc mất rồi)\n"
                f"   • Nếu còn thấy quái:\n"
                f"     ✅ Đánh tiếp tối thiểu {result.attack_min_duration_sec:.2f} giây\n\n"
                f"5️⃣ QUÁI CHẾT RỒI:\n"
                f"   • Quay lại bước 1 (tìm quái mới)\n"
                f"   • Cứ thế lặp lại mãi mãi\n"
                f"{'─'*60}\n"
                f"💡 Bấm nút 'Apply' bên dưới để lưu các số này"
            )
        else:
            preview_text = (
                f"📋 SETTINGS TO BE APPLIED:\n"
                f"{'─'*60}\n"
                f"📊 INPUT DATA:\n"
                f"  • Monster HP: {result.monster_hp:,.0f}\n"
                f"  • Damage/hit: {result.damage_per_hit:,.0f}\n"
                f"  • Attack Speed: {result.attacks_per_second:.2f} hits/s\n"
                f"  • Time/hit: {time_per_hit:.2f}s (= 1 / {result.attacks_per_second:.2f})\n"
                f"  • Hits to kill: {result.hits_to_kill} hits (= HP / Damage)\n"
                f"  • Kill time: {result.estimated_kill_time_sec:.2f}s (= {result.hits_to_kill} / {result.attacks_per_second:.2f})\n\n"
                f"⏱️  BASIC TIMING:\n"
                f"  • attack_press_ms: {result.attack_press_ms} ms\n"
                f"    📐 Formula: max(50, min(100, 500/APS))\n"
                f"    💡 Higher APS → shorter press\n\n"
                f"  • target_cycle_delay: {result.target_cycle_delay:.2f}s\n"
                f"    📐 Formula: max(0.15, time_per_hit × 1.2)\n"
                f"    💡 Wait longer than 1 hit to avoid mid-attack switching\n\n"
                f"  • search_interval: {result.search_interval:.2f}s\n"
                f"    📐 Formula: max(0.1, min(0.3, time_per_hit × 0.5))\n"
                f"    💡 Search faster than hit time for responsive detection\n\n"
                f"  • attack_interval: {result.attack_interval:.2f}s\n"
                f"    📐 Formula: max(0.1, time_per_hit × 0.8)\n"
                f"    💡 Attack slightly faster than natural rhythm\n\n"
                f"🎯 TIMEOUT & DURATION:\n"
                f"  • lost_timeout_sec: {result.lost_timeout_sec:.2f}s\n"
                f"    📐 Formula: time_per_hit × (1 + {result.lost_timeout_margin:.0%} margin)\n"
                f"    💡 Allow detection lag between hits\n\n"
                f"  • attack_min_duration_sec: {result.attack_min_duration_sec:.2f}s\n"
                f"    📐 Formula: kill_time × (1 + {result.attack_duration_margin:.0%} margin)\n"
                f"    💡 Ensure attacking long enough even if template temporarily lost\n\n"
                f"{'─'*60}\n"
                f"🤖 AUTO BEHAVIOR EXPLANATION:\n"
                f"{'─'*60}\n"
                f"1️⃣ SEARCH PHASE (Every {result.search_interval:.2f}s):\n"
                f"   → Scan screen to find monster template\n"
                f"   → Fast search = Quick response when monster appears\n\n"
                f"2️⃣ TARGET LOCK:\n"
                f"   → Press 'Z' key to target monster\n"
                f"   → Wait {result.target_cycle_delay:.2f}s before next target attempt\n"
                f"   → This prevents target switching during combat\n\n"
                f"3️⃣ ATTACK CYCLE (Every {result.attack_interval:.2f}s):\n"
                f"   → Press attack key for {result.attack_press_ms}ms\n"
                f"   → Release and wait {result.attack_interval:.2f}s\n"
                f"   → Repeat rhythm: Attack → Wait → Attack → Wait\n"
                f"   → Expected: {result.hits_to_kill} hits in ~{result.estimated_kill_time_sec:.1f}s to kill\n\n"
                f"4️⃣ TEMPLATE MONITORING:\n"
                f"   → If monster disappears for > {result.lost_timeout_sec:.2f}s:\n"
                f"      ❌ Stop attacking (target lost/dead)\n"
                f"   → If monster visible:\n"
                f"      ✅ Keep attacking for at least {result.attack_min_duration_sec:.2f}s\n"
                f"      (Even if template flickers, continue attacking)\n\n"
                f"5️⃣ KILL CONFIRMATION:\n"
                f"   → After {result.attack_min_duration_sec:.2f}s OR target lost:\n"
                f"   → Return to SEARCH PHASE (step 1)\n"
                f"   → Loop continues automatically\n"
                f"{'─'*60}\n"
                f"💡 Click 'Apply' to save to Hunt Config"
            )
        
        self._update_text_widget(self.timing_preview, preview_text)

    
    def _get_timing_confidence(self, result) -> str:
        """Determine confidence level of calculation"""
        if result.monster_hp > 0 and result.damage_per_hit > 0 and result.attacks_per_second > 0:
            return 'high'
        elif result.monster_hp > 0 and result.damage_per_hit > 0:
            return 'medium'
        else:
            return 'low'
    
    def _apply_timing_to_config(self):
        """Apply calculated timing to hunt config"""
        if not hasattr(self, 'timing_calculation_result') or self.timing_calculation_result is None:
            messagebox.showwarning(
                self._t('error_title'),
                'Please calculate timing first' if self.lang == 'en' else 'Vui lòng tính toán timing trước'
            )
            return
        
        result = self.timing_calculation_result
        
        # Confirm before applying
        confirm_msg = (
            f"Apply ALL timing settings to Hunt Config?\n\n"
            f"⏱️  Basic Timing:\n"
            f"• attack_press_ms: {result.attack_press_ms} ms\n"
            f"• target_cycle_delay: {result.target_cycle_delay:.2f}s\n"
            f"• search_interval: {result.search_interval:.2f}s\n"
            f"• attack_interval: {result.attack_interval:.2f}s\n\n"
            f"🎯 Timeout & Duration:\n"
            f"• lost_timeout_sec: {result.lost_timeout_sec:.2f}s\n"
            f"• attack_min_duration_sec: {result.attack_min_duration_sec:.2f}s"
        ) if self.lang == 'en' else (
            f"Áp dụng TẤT CẢ cài đặt timing vào Hunt Config?\n\n"
            f"⏱️  Timing Cơ Bản:\n"
            f"• attack_press_ms: {result.attack_press_ms} ms\n"
            f"• target_cycle_delay: {result.target_cycle_delay:.2f}s\n"
            f"• search_interval: {result.search_interval:.2f}s\n"
            f"• attack_interval: {result.attack_interval:.2f}s\n\n"
            f"🎯 Timeout & Duration:\n"
            f"• lost_timeout_sec: {result.lost_timeout_sec:.2f}s\n"
            f"• attack_min_duration_sec: {result.attack_min_duration_sec:.2f}s"
        )
        
        if not messagebox.askyesno(self._t('confirm_title'), confirm_msg):
            return
        
        # Store old values for comparison
        old_values = {
            'attack_press_ms': self.hunt_cfg.get('attack_press_ms', 0),
            'target_cycle_delay': self.hunt_cfg.get('target_cycle_delay', 0),
            'search_interval': self.hunt_cfg.get('search_interval', 0),
            'attack_interval': self.hunt_cfg.get('attack_interval', 0),
            'lost_timeout_sec': self.hunt_cfg.get('lost_timeout_sec', 0),
            'attack_min_duration_sec': self.hunt_cfg.get('attack_min_duration_sec', 0)
        }
        
        # Update hunt config with ALL timing values
        self.hunt_cfg['attack_press_ms'] = result.attack_press_ms
        self.hunt_cfg['target_cycle_delay'] = result.target_cycle_delay
        self.hunt_cfg['search_interval'] = result.search_interval
        self.hunt_cfg['attack_interval'] = result.attack_interval
        self.hunt_cfg['lost_timeout_sec'] = result.lost_timeout_sec
        self.hunt_cfg['attack_min_duration_sec'] = result.attack_min_duration_sec
        
        # Mark as changed
        self.changes_made['timing_applied'] = True
        self._mark_unsaved(True)
        
        # Show success with what changed
        success_msg = (
            f"✅ All timing settings applied successfully!\n\n"
            f"⏱️  Basic Timing:\n"
            f"• attack_press_ms: {old_values['attack_press_ms']} → {result.attack_press_ms} ms\n"
            f"• target_cycle_delay: {old_values['target_cycle_delay']:.2f}s → {result.target_cycle_delay:.2f}s\n"
            f"• search_interval: {old_values['search_interval']:.2f}s → {result.search_interval:.2f}s\n"
            f"• attack_interval: {old_values['attack_interval']:.2f}s → {result.attack_interval:.2f}s\n\n"
            f"🎯 Timeout & Duration:\n"
            f"• lost_timeout_sec: {old_values['lost_timeout_sec']:.2f}s → {result.lost_timeout_sec:.2f}s\n"
            f"• attack_min_duration_sec: {old_values['attack_min_duration_sec']:.2f}s → {result.attack_min_duration_sec:.2f}s\n\n"
            f"💾 Remember to save changes!"
        ) if self.lang == 'en' else (
            f"✅ Đã áp dụng tất cả cài đặt timing thành công!\n\n"
            f"⏱️  Timing Cơ Bản:\n"
            f"• attack_press_ms: {old_values['attack_press_ms']} → {result.attack_press_ms} ms\n"
            f"• target_cycle_delay: {old_values['target_cycle_delay']:.2f}s → {result.target_cycle_delay:.2f}s\n"
            f"• search_interval: {old_values['search_interval']:.2f}s → {result.search_interval:.2f}s\n"
            f"• attack_interval: {old_values['attack_interval']:.2f}s → {result.attack_interval:.2f}s\n\n"
            f"🎯 Timeout & Duration:\n"
            f"• lost_timeout_sec: {old_values['lost_timeout_sec']:.2f}s → {result.lost_timeout_sec:.2f}s\n"
            f"• attack_min_duration_sec: {old_values['attack_min_duration_sec']:.2f}s → {result.attack_min_duration_sec:.2f}s\n\n"
            f"💾 Nhớ lưu thay đổi!"
        )
        
        messagebox.showinfo(self._t('success_title'), success_msg)
        
        # === SAVE TO HUNT CONFIG AND SHOW INLINE CONFIRMATION ===
        try:
            # Save hunt_cfg to file immediately (local save)
            hunt_config_path = Path(__file__).parent.parent / 'lib' / 'data' / 'hunt_config.json'
            with open(hunt_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
            
            # Show inline confirmation (not popup)
            self._show_timing_execution_inline()
            
        except Exception as e:
            messagebox.showerror(
                self._t('error_title'),
                f"Failed to save hunt config: {str(e)}"
            )
    
    def _show_timing_execution_inline(self):
        """Show inline preview of how auto will execute with saved settings"""
        result = self.timing_calculation_result
        
        if self.lang == 'vi':
            preview_msg = (
                f"{'='*60}\n"
                f"✅ ĐÃ LƯU VÀO MÁY TÍNH RỒI!\n"
                f"{'='*60}\n\n"
                f"📂 LƯU Ở ĐÂU: lib/data/hunt_config.json\n\n"
                f"🔧 CÁC SỐ ĐÃ LƯU:\n"
                f"  • Giữ phím: {result.attack_press_ms} mili-giây\n"
                f"  • Đợi đổi quái: {result.target_cycle_delay:.2f} giây\n"
                f"  • Tìm quái: mỗi {result.search_interval:.2f} giây\n"
                f"  • Đánh: mỗi {result.attack_interval:.2f} giây\n"
                f"  • Quái mất quá: {result.lost_timeout_sec:.2f} giây thì dừng\n"
                f"  • Đánh tối thiểu: {result.attack_min_duration_sec:.2f} giây\n\n"
                f"{'─'*60}\n"
                f"🤖 KHI BẤM NÚT CHẠY AUTO, NÓ SẼ LÀM GÌ?\n"
                f"{'─'*60}\n\n"
                f"BƯỚC 1: Đọc file hunt_config.json\n"
                f"  → Lấy các con số vừa lưu ra dùng\n\n"
                f"BƯỚC 2: Tìm quái (cứ {result.search_interval:.2f} giây tìm 1 lần)\n"
                f"  → Nhìn màn hình, tìm hình quái vật\n"
                f"  → Nếu thấy → chuyển sang BƯỚC 3\n\n"
                f"BƯỚC 3: Bấm phím Z chọn quái\n"
                f"  → Giữ phím Z trong {result.attack_press_ms} mili-giây\n"
                f"  → Đợi {result.target_cycle_delay:.2f} giây\n\n"
                f"BƯỚC 4: Bắt đầu đánh (đánh {result.hits_to_kill} đòn)\n"
                f"  → Bấm phím tấn công, giữ {result.attack_press_ms} mili-giây\n"
                f"  → Thả phím ra\n"
                f"  → Đợi {result.attack_interval:.2f} giây\n"
                f"  → Lặp lại khoảng {result.hits_to_kill} lần (tầm {result.estimated_kill_time_sec:.1f} giây)\n\n"
                f"BƯỚC 5: Kiểm tra quái còn không\n"
                f"  → Nếu không thấy quái quá {result.lost_timeout_sec:.2f} giây:\n"
                f"     ❌ Quái chết rồi! Dừng đánh\n"
                f"  → Nếu vẫn thấy quái:\n"
                f"     ✅ Đánh tiếp tối thiểu {result.attack_min_duration_sec:.2f} giây nữa\n\n"
                f"BƯỚC 6: Quái chết rồi, tìm quái mới\n"
                f"  → Quay lại BƯỚC 2\n"
                f"  → Cứ thế lặp đi lặp lại mãi mãi\n\n"
                f"{'─'*60}\n"
                f"🔑 MÁY TÍNH SẼ BẤM PHÍM NHƯ THẾ NÀO?\n"
                f"{'─'*60}\n\n"
                f"  1. Chương trình gọi hàm tap()\n"
                f"  2. Hàm tap() gọi key_down() → Nhấn phím xuống\n"
                f"  3. Đợi {result.attack_press_ms} mili-giây\n"
                f"  4. Gọi key_up() → Thả phím lên\n"
                f"  5. Windows gửi tín hiệu cho Game Cabal\n"
                f"  6. Game Cabal nhận được → Nhân vật đánh quái!\n\n"
                f"{'='*60}\n"
                f"✅ KẾT LUẬN: AUTO SẼ BẤM PHÍM THẬT!\n"
                f"   (Giống như bạn ngồi bấm, nhưng máy làm giúp)\n"
                f"{'='*60}\n"
            )
        else:
            preview_msg = (
                f"{'='*60}\n"
                f"✅ SAVED TO hunt_config.json\n"
                f"{'='*60}\n\n"
                f"🤖 CONFIRMATION: AUTO WILL EXECUTE AS FOLLOWS:\n"
                f"{'─'*60}\n\n"
                f"📂 FILE: lib/data/hunt_config.json\n"
                f"🔧 SAVED PARAMETERS:\n\n"
                f"  attack_press_ms: {result.attack_press_ms}\n"
                f"  target_cycle_delay: {result.target_cycle_delay}\n"
                f"  search_interval: {result.search_interval}\n"
                f"  attack_interval: {result.attack_interval}\n"
                f"  lost_timeout_sec: {result.lost_timeout_sec}\n"
                f"  attack_min_duration_sec: {result.attack_min_duration_sec}\n\n"
                f"{'─'*60}\n"
                f"⚡ EXECUTION FLOW WHEN AUTO RUNS:\n"
                f"{'─'*60}\n\n"
                f"1. auto_hunt.py READS hunt_config.json\n"
                f"   → Loads saved timing parameters\n\n"
                f"2. SEARCH FOR MONSTER (every {result.search_interval:.2f}s):\n"
                f"   → while True:\n"
                f"       template_matcher.locate_template()\n"
                f"       time.sleep({result.search_interval:.2f})\n\n"
                f"3. PRESS Z TO TARGET:\n"
                f"   → tap('z', {result.attack_press_ms})\n"
                f"   → time.sleep({result.target_cycle_delay:.2f})\n\n"
                f"4. ATTACK (every {result.attack_interval:.2f}s):\n"
                f"   → tap(attack_key, {result.attack_press_ms})  # HOLD {result.attack_press_ms}ms\n"
                f"   → time.sleep({result.attack_interval:.2f})     # WAIT {result.attack_interval:.2f}s\n"
                f"   → Repeat ~{result.hits_to_kill} times (est. {result.estimated_kill_time_sec:.1f}s)\n\n"
                f"5. CHECK TARGET LOST:\n"
                f"   → if template_lost > {result.lost_timeout_sec:.2f}s:\n"
                f"       break  # STOP ATTACKING\n\n"
                f"6. ENSURE MINIMUM DURATION:\n"
                f"   → if attack_duration >= {result.attack_min_duration_sec:.2f}s:\n"
                f"       # OK, ATTACKED LONG ENOUGH\n"
                f"   → else: continue attacking\n\n"
                f"{'─'*60}\n"
                f"🔑 ACTUAL API CALLS:\n"
                f"{'─'*60}\n\n"
                f"  lib/system/win_input.py:\n"
                f"    def tap(key, press_ms):\n"
                f"        key_down(key)                    # ⬇️ PRESS\n"
                f"        time.sleep(press_ms/1000.0)      # ⏱️ HOLD\n"
                f"        key_up(key)                      # ⬆️ RELEASE\n\n"
                f"  Windows API:\n"
                f"    user32.SendInput(...)                # 🪟 WINDOWS\n"
                f"    → CABAL Game receives input         # 🎮 GAME\n\n"
                f"{'='*60}\n"
                f"✅ CONFIRMED: AUTO WILL PRESS REAL KEYS!\n"
                f"{'='*60}\n"
            )
        
        # Display inline in confirmation frame
        self._update_text_widget(self.timing_confirmation_text, preview_msg)
        
        # Show the confirmation frame inline
        self.timing_confirmation_frame.pack(fill='both', expand=True, padx=10, pady=(10, 15))
    
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
            data_dir = root_dir / 'lib' / 'data'
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
            # Clear unsaved state after successful save
            self.changes_made = {'monsters_changed': False, 'skills_changed': False, 'timing_applied': False}
            self._mark_unsaved(False)
            
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
    
    def __init__(self, parent: tk.Toplevel, lang: str = 'en', mode: str = 'add', monster: Optional[dict] = None, icon_helper=None, i18n_registry=None):
        self.parent = parent
        self.lang = lang
        self.mode = mode
        self.monster = monster or {}
        self.result = None
        self.icon_helper = icon_helper
        self.i18n_registry = i18n_registry
        
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
        
        # Save button - Use icon if icon_helper available
        if self.icon_helper:
            save_icon = self.icon_helper.get_icon('save', fallback='💾')
            # If icon is a string (emoji fallback), use as text; otherwise use as image
            if isinstance(save_icon, str):
                save_btn = tk.Button(
                    button_frame,
                    text=f"{save_icon} {'Save' if self.lang == 'en' else 'Lưu'}",
                    command=self._save,
                    bg='#4CAF50',
                    fg='white',
                    font=('Arial', 9, 'bold'),
                    padx=20,
                    pady=5,
                    cursor='hand2'
                )
            else:
                save_btn = tk.Button(
                    button_frame,
                    image=save_icon,
                    command=self._save,
                    bg='#4CAF50',
                    fg='white',
                    font=('Arial', 9, 'bold'),
                    padx=20,
                    pady=5,
                    cursor='hand2'
                )
                try:
                    if not hasattr(self, '_image_refs'):
                        self._image_refs = []
                    self._image_refs.append(save_icon)
                except Exception:
                    pass
            
            # Add i18n tooltip if registry available
            if self.i18n_registry:
                from lib.ui.tooltip import attach_i18n_tooltip
                attach_i18n_tooltip(
                    save_btn, 
                    'tip_save_monster', 
                    'library_manager',
                    lambda: self.lang
                )
        else:
            # Fallback to text-only button
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


class SkillDialog:
    """
    Dialog for adding or editing a skill.
    
    Provides form fields for:
    - Name (required)
    - Key (required)
    - Type (attack/buff, required)
    - Cooldown (float, required)
    - Cast Time (float, required)
    - Image path (optional, readonly for now)
    
    Args:
        parent: Parent window
        lang: Language ('en' or 'vi')
        mode: 'add' or 'edit'
        skill: Skill dict (for edit mode)
    
    Returns:
        result: New/updated skill dict, or None if cancelled
    """
    
    def __init__(self, parent: tk.Toplevel, lang: str = 'en', mode: str = 'add', skill: Optional[dict] = None, icon_helper=None, i18n_registry=None):
        self.parent = parent
        self.lang = lang
        self.mode = mode
        self.skill = skill or {}
        self.result = None
        self.icon_helper = icon_helper
        self.i18n_registry = i18n_registry
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(
            'Add Skill' if mode == 'add' and lang == 'en' else
            'Thêm Kỹ Năng' if mode == 'add' else
            'Edit Skill' if lang == 'en' else
            'Sửa Kỹ Năng'
        )
        self.dialog.geometry("500x400")
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
            text='⚔️ Skill Information' if self.lang == 'en' else '⚔️ Thông Tin Kỹ Năng',
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
        
        self.name_var = tk.StringVar(value=self.skill.get('name', ''))
        name_entry = tk.Entry(form_frame, textvariable=self.name_var, width=40, font=('Arial', 9))
        name_entry.grid(row=0, column=1, pady=5, sticky='ew')
        name_entry.focus()
        
        # Key field (required)
        tk.Label(
            form_frame,
            text='Key:' if self.lang == 'en' else 'Phím:',
            font=('Arial', 9, 'bold')
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.key_var = tk.StringVar(value=self.skill.get('key', ''))
        key_entry = tk.Entry(form_frame, textvariable=self.key_var, width=40, font=('Arial', 9))
        key_entry.grid(row=1, column=1, pady=5, sticky='ew')
        
        # Type field (required)
        tk.Label(
            form_frame,
            text='Type:' if self.lang == 'en' else 'Loại:',
            font=('Arial', 9, 'bold')
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.type_var = tk.StringVar(value=self.skill.get('type', 'attack'))
        type_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.type_var, 
            state='readonly',
            width=37,
            values=['attack', 'buff'],
            font=('Arial', 9)
        )
        type_combo.grid(row=2, column=1, pady=5, sticky='ew')
        
        # Cooldown field (required)
        tk.Label(
            form_frame,
            text='Cooldown (s):' if self.lang == 'en' else 'Hồi chiêu (s):',
            font=('Arial', 9, 'bold')
        ).grid(row=3, column=0, sticky='w', pady=5)
        
        self.cooldown_var = tk.StringVar(value=str(self.skill.get('cooldown', '0.0')))
        cooldown_entry = tk.Entry(form_frame, textvariable=self.cooldown_var, width=40, font=('Arial', 9))
        cooldown_entry.grid(row=3, column=1, pady=5, sticky='ew')
        
        # Cast time field (required)
        tk.Label(
            form_frame,
            text='Cast Time (s):' if self.lang == 'en' else 'Thời gian thi (s):',
            font=('Arial', 9, 'bold')
        ).grid(row=4, column=0, sticky='w', pady=5)
        
        self.cast_time_var = tk.StringVar(value=str(self.skill.get('cast_time', '0.0')))
        cast_time_entry = tk.Entry(form_frame, textvariable=self.cast_time_var, width=40, font=('Arial', 9))
        cast_time_entry.grid(row=4, column=1, pady=5, sticky='ew')
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Button frame at bottom
        button_frame = tk.Frame(container)
        button_frame.pack(side='bottom', pady=(20, 0))
        
        # Save button - Use icon if icon_helper available
        if self.icon_helper:
            save_icon = self.icon_helper.get_icon('save', fallback='💾')
            # If icon is a string (emoji fallback), use as text; otherwise use as image
            if isinstance(save_icon, str):
                save_btn = tk.Button(
                    button_frame,
                    text=f"{save_icon} {'Save' if self.lang == 'en' else 'Lưu'}",
                    command=self._save,
                    bg='#4CAF50',
                    fg='white',
                    font=('Arial', 9, 'bold'),
                    padx=20,
                    pady=5,
                    cursor='hand2'
                )
            else:
                save_btn = tk.Button(
                    button_frame,
                    image=save_icon,
                    command=self._save,
                    bg='#4CAF50',
                    fg='white',
                    font=('Arial', 9, 'bold'),
                    padx=20,
                    pady=5,
                    cursor='hand2'
                )
                try:
                    if not hasattr(self, '_image_refs'):
                        self._image_refs = []
                    self._image_refs.append(save_icon)
                except Exception:
                    pass
            
            # Add i18n tooltip if registry available
            if self.i18n_registry:
                from lib.ui.tooltip import attach_i18n_tooltip
                attach_i18n_tooltip(
                    save_btn, 
                    'tip_save_skill', 
                    'library_manager',
                    lambda: self.lang
                )
        else:
            # Fallback to text-only button
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
                'Please enter skill name.' if self.lang == 'en' else 'Vui lòng nhập tên kỹ năng.',
                parent=self.dialog
            )
            return False
        
        # Check key
        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter key binding.' if self.lang == 'en' else 'Vui lòng nhập phím tắt.',
                parent=self.dialog
            )
            return False
        
        # Check cooldown
        try:
            cooldown = float(self.cooldown_var.get().strip())
            if cooldown < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter valid cooldown (non-negative number).' if self.lang == 'en' 
                else 'Vui lòng nhập thời gian hồi chiêu hợp lệ (số không âm).',
                parent=self.dialog
            )
            return False
        
        # Check cast time
        try:
            cast_time = float(self.cast_time_var.get().strip())
            if cast_time < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                'Validation Error' if self.lang == 'en' else 'Lỗi Xác Thực',
                'Please enter valid cast time (non-negative number).' if self.lang == 'en'
                else 'Vui lòng nhập thời gian thi triển hợp lệ (số không âm).',
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
            'key': self.key_var.get().strip().upper(),
            'type': self.type_var.get(),
            'cooldown': float(self.cooldown_var.get().strip()),
            'cast_time': float(self.cast_time_var.get().strip()),
            'image': self.skill.get('image', '')  # Preserve existing image
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
