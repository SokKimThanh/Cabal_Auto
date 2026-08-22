import os
import time
import re
from pathlib import Path
from typing import Optional, Tuple, Any, Callable

try:
    import pyautogui  # type: ignore
except Exception:
    pyautogui = None  # type: ignore

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

import tkinter as tk
from tkinter import messagebox

# Get project root by going up from ui/helpers/capture_helper.py
_current_file = Path(__file__).resolve()  # ui/helpers/capture_helper.py
_project_root = _current_file.parents[2]   # project root

# Default ASSETS_DIR for monsters (backward compatibility)
ASSETS_DIR = _project_root / 'assets' / 'images' / 'monsters'
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Skills directory
ASSETS_SKILLS_DIR = _project_root / 'assets' / 'images' / 'skills'
ASSETS_SKILLS_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9\-_. ]+", "", name)
    return name.replace(' ', '_') or 'capture'


class RegionSelector(tk.Toplevel):
    def __init__(self, parent: tk.Misc, screenshot_image):
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        try:
            self.attributes('-alpha', 0.2)
        except Exception:
            pass
        self.configure(bg='black')
        # Fullscreen canvas overlay to select region
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        # Use a valid background color; empty string can raise 'unknown color name'
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, cursor='crosshair')
        self.canvas.pack(fill='both', expand=True)
        self._start = None
        self._rect = None
        self._bbox = None
        self.canvas.bind('<ButtonPress-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Escape>', lambda e: self._cancel())

    def _on_press(self, event):
        self._start = (event.x, event.y, event.x_root, event.y_root)
        if self._rect is not None:
            self.canvas.delete(self._rect)
            self._rect = None
        self._rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='#00E5FF', width=2)

    def _on_drag(self, event):
        if self._start and self._rect:
            x0, y0, _, _ = self._start
            x1, y1 = event.x, event.y
            self.canvas.coords(self._rect, x0, y0, x1, y1)

    def _on_release(self, event):
        if not self._start:
            self.destroy(); return
        x0, y0, xr0, yr0 = self._start
        x1, y1 = event.x, event.y
        dx = xr0 - x0
        dy = yr0 - y0
        left = int(min(x0 + dx, x1 + dx))
        top = int(min(y0 + dy, y1 + dy))
        right = int(max(x0 + dx, x1 + dx))
        bottom = int(max(y0 + dy, y1 + dy))
        if right - left < 5 or bottom - top < 5:
            self._bbox = None
        else:
            self._bbox = (left, top, right - left, bottom - top)
        self.destroy()

    def _cancel(self):
        self._bbox = None
        self.destroy()

    def show_modal(self) -> Optional[Tuple[int,int,int,int]]:
        self.deiconify()
        self.grab_set()
        self.focus_force()
        self.wait_window(self)
        return self._bbox


def capture_region_and_save(
    parent: Any, 
    pil_available: bool, 
    monster_name: str, 
    lang: str = 'vi', 
    pre_wait_hook: Optional[Callable[[], None]] = None,
    capture_type: str = 'monster'
) -> Optional[Tuple[str, Tuple[int,int,int,int]]]:
    """Implements the shared capture flow: wait 3s, screenshot, region select, crop and save.
    
    Args:
        parent: Parent widget
        pil_available: Whether PIL is available
        monster_name: Name for the image file (works for both monsters and skills)
        lang: Language ('vi' or 'en')
        pre_wait_hook: Optional callback before screenshot
        capture_type: 'monster' or 'skill' - determines save directory
    
    Returns (path, bbox) where bbox is (left, top, width, height), or None if cancelled/failed.
    """
    if pyautogui is None:
        message = 'pyautogui is required for screenshot.' if lang == 'en' else 'Cần pyautogui để chụp màn hình.'
        messagebox.showerror('Error', message, parent=parent)
        return None
    if not pil_available or Image is None:
        message = 'Pillow is required for image operations.' if lang == 'en' else 'Cần Pillow để xử lý ảnh.'
        messagebox.showerror('Error', message, parent=parent)
        return None

    # Optional: small instruction
    hint = (
        'Instructions:\n1. Click and wait 3s\n2. Drag to select region\n3. Image will be saved automatically'
        if lang == 'en' else
        'Hướng dẫn:\n1. Nhấn và đợi 3 giây\n2. Kéo để chọn vùng\n3. Ảnh sẽ tự động lưu'
    )
    try:
        messagebox.showinfo('Capture', hint, parent=parent)
    except Exception:
        pass

    # Allow caller to bring target window to front now (after user pressed OK)
    try:
        if callable(pre_wait_hook):
            pre_wait_hook()
    except Exception:
        pass

    # Wait 3 seconds like app_gui
    try:
        if hasattr(parent, 'withdraw'):
            parent.withdraw()
            parent.update_idletasks()
        time.sleep(3)
    finally:
        try:
            if hasattr(parent, 'deiconify'):
                parent.deiconify(); parent.lift(); parent.focus_force()
        except Exception:
            pass

    # Take full screenshot
    try:
        screenshot = pyautogui.screenshot()  # PIL Image
    except Exception as exc:
        msg = 'Screenshot failed: {exc}'.format(exc=exc) if lang == 'en' else f'Chụp màn hình thất bại: {exc}'
        messagebox.showerror('Error', msg, parent=parent)
        return None

    # Region selection overlay
    selector = RegionSelector(parent, screenshot)
    bbox = selector.show_modal()  # (left, top, width, height) or None
    if not bbox:
        try:
            messagebox.showinfo('Cancelled', 'Capture cancelled' if lang=='en' else 'Đã hủy chụp', parent=parent)
        except Exception:
            pass
        return None
    left, top, width, height = bbox

    # Crop
    try:
        cropped = screenshot.crop((left, top, left + width, top + height))
    except Exception as exc:
        msg = 'Crop failed: {exc}'.format(exc=exc) if lang=='en' else f'Cắt ảnh thất bại: {exc}'
        messagebox.showerror('Error', msg, parent=parent)
        return None

    # Determine save directory based on capture type
    if capture_type == 'skill':
        save_dir = ASSETS_SKILLS_DIR
        default_name = 'skill'
    else:  # default to 'monster'
        save_dir = ASSETS_DIR
        default_name = 'monster'
    
    # Save under appropriate directory
    slug = _slugify(monster_name or default_name)
    ts = int(time.time())
    filename = f"{slug}_capture_{ts}.png"
    path = save_dir / filename
    try:
        cropped.save(path)
    except Exception as exc:
        msg = 'Save failed: {exc}'.format(exc=exc) if lang=='en' else f'Lưu ảnh thất bại: {exc}'
        messagebox.showerror('Error', msg, parent=parent)
        return None

    try:
        message = 'Screenshot saved: {filename}'.format(filename=filename) if lang=='en' else f'Đã lưu ảnh: {filename}'
        messagebox.showinfo('Success', message, parent=parent)
    except Exception:
        pass

    return (str(path), (left, top, width, height))
