# -*- coding: utf-8 -*-
"""
Icon Helper - Load icons with fallback to Unicode emoji.

This module provides a centralized way to load icons from files,
with automatic fallback to Unicode emoji if icons are not available.

Usage:
    from ui.helpers.icon_helper import IconHelper
    
    icon_helper = IconHelper()
    add_icon = icon_helper.get_icon('add', fallback='➕')
"""

import os
import sys
import json
import logging
from pathlib import Path
from tkinter import PhotoImage
try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
from typing import Optional, Union, Any


class IconHelper:
    """
    Helper class for loading icons with emoji fallback.
    
    Features:
    - Load PNG icons from images/icons/ directory
    - Automatic fallback to Unicode emoji
    - Caching for performance
    - UTF-8 support
    """
    
    def __init__(self):
        """Initialize icon helper and set up paths."""
        # Get project root
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = Path(sys.executable).parent
        else:
            # Running from source: project root is three levels up (ui/helpers/* -> project root)
            # __file__ = <project>/ui/helpers/icon_helper.py
            # parents[0]=helpers, [1]=ui, [2]=<project>
            try:
                base_dir = Path(__file__).resolve().parents[2]
            except Exception:
                # Fallback to previous behavior (may be lib folder)
                base_dir = Path(__file__).parent.parent
        
        # Icon directories (prefer new assets path, fallback to legacy images/icons)
        self.icon_dirs = [
            base_dir / 'assets' / 'images' / 'icons',
            base_dir / 'images' / 'icons',
        ]
        # Ensure primary icon directory exists
        self.icon_dirs[0].mkdir(parents=True, exist_ok=True)
        
        # Icon cache
        self._cache = {}
        
        # Load icon mappings from JSON or use fallback
        self.icon_map = {}
        icons_json_path = Path(__file__).parent / 'icons.json'

        try:
            if icons_json_path.exists():
                with open(icons_json_path, 'r', encoding='utf-8') as f:
                    self.icon_map = json.load(f)
            else:
                self._load_fallback_mappings()
        except Exception as e:
            logging.warning(f"Failed to load icons.json: {e}. Using fallback mappings.")
            self._load_fallback_mappings()

    def _load_fallback_mappings(self):
        """Load default fallback icon mappings if JSON file is unavailable."""
        self.icon_map = {
            'add': ['add', '➕'],
            'accept': ['accept', '✔️'],
            'locked': ['locked', '🔒'],
            'edit': ['edit', '✏️'],
            'delete': ['delete', '🗑️'],
            'save': ['save', '💾'],
            'cancel': ['cancel', '✖'],
            'folder': ['folder', '📁'],
            'capture': ['capture', '📸'],
            'search': ['search', '🔍'],
            'refresh': ['refresh', '🔄'],
            'start': ['start', '▶️'],
            'stop': ['stop', '⏹️'],
            'pause': ['pause', '⏸️'],
            'minimize': ['minimize', '➖'],
            'support': ['support', '🧙'],
            'next': ['next', '→'],
            'previous': ['previous', '←'],
            'preview': ['preview', '👁️'],
            'monster': ['monster', '👹'],
            'skill': ['skill', '⚔️'],
            'template': ['template', '🖼️'],
            'list': ['list', '🗂️'],
            'info': ['info', '📋'],
            'time': ['time', '⏱️'],
            'hp': ['hp', '❤️'],
            'damage': ['damage', '⚔️'],
            'priority': ['priority', '🎯'],
            'question': ['question_mark', '❓'],
            'up': ['up', '↑'],
            'id': ['id', '🔑'],
            'speed': ['speed', '⚡'],
            'shield': ['shield', '🛡️'],
            'aim': ['aim', '🎯'],
            'dungeon': ['dungeon', '🏰'],
            'boss': ['boss', '👑'],
            'down': ['down', '↓'],
            'browse': ['folder', '📂'],
            'clear': ['delete', '🗑️'],
            'close': ['cancel', '✖'],
            'new': ['add', '➕'],
            'calculate': ['info', '🔢'],
            'apply': ['save', '✔️'],
            'test': ['question_mark', '🧪'],
            'use': ['start', '📌'],
            'library': ['list', '📚'],
            'check': ['check', '✓'],
            'warning': ['warning', '⚠️'],
            'settings': ['setting', '⚙️'],
            'hotkey': ['hotkey', '⌨️'],
            'forbidden': ['prohibition', '🚫']
        }
    
    def _apply_color_tint(self, img: Any, hex_color: str) -> Any:
        """
        Apply color tint to icon while preserving alpha channel.
        Works best with monochrome icons. If the icon has significant color variance,
        it will skip tinting to preserve full-color icons.
        
        Args:
            img: PIL Image in RGBA mode
            hex_color: Hex color string (e.g., '#FFFFFF')
        
        Returns:
            Tinted PIL Image (or original if full-color)
        """
        if Image is None:
            return img
        
        # Parse hex color to RGB
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        else:
            return img  # Invalid color format
        
        # Split channels
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        data = list(img.getdata())
        
        # Check if the icon is full-color by measuring color variance
        is_full_color = False
        color_pixels = 0
        total_opaque_pixels = 0

        for item in data:
            if item[3] > 10:  # If pixel is somewhat opaque
                total_opaque_pixels += 1
                # Check variance between RGB channels (grayscale pixels have R ≈ G ≈ B)
                r_orig, g_orig, b_orig = item[0], item[1], item[2]
                variance = max(abs(r_orig - g_orig), abs(g_orig - b_orig), abs(r_orig - b_orig))
                if variance > 30: # Threshold for considering it a "color" pixel
                    color_pixels += 1

        # If more than 10% of opaque pixels are colored, consider it a full-color icon
        if total_opaque_pixels > 0 and (color_pixels / total_opaque_pixels) > 0.1:
            return img

        new_data = []
        # Recolor each pixel: replace RGB but keep alpha
        for item in data:
            # item = (R, G, B, A)
            if item[3] > 0:  # If pixel has any opacity
                # Use the luminance of original pixel to determine brightness
                luminance = (item[0] + item[1] + item[2]) / 3.0 / 255.0
                new_data.append((
                    int(r * luminance),
                    int(g * luminance),
                    int(b * luminance),
                    item[3]  # Preserve alpha
                ))
            else:
                new_data.append(item)  # Fully transparent - keep as is
        
        img.putdata(new_data)
        return img
    
    def get_icon(self, name: str, fallback: Optional[str] = None, size: int = 24, color: Optional[str] = None) -> Union[Any, str]:
        """
        Get icon by name, with fallback to emoji.
        
        Args:
            name: Icon name (e.g., 'add', 'edit', 'delete')
            fallback: Fallback emoji character (optional)
            size: Icon size in pixels (default: 24)
            color: Hex color to tint icon (e.g., '#FFFFFF' for white). Only works with PIL installed.
        
        Returns:
            PhotoImage object if icon file exists, otherwise emoji string
        """
        # Check cache (include color in cache key)
        cache_key = f"{name}_{size}_{color or 'default'}"
        if cache_key in self._cache:
            cached_val = self._cache[cache_key]
            # Verify cached image is still valid in current tk root
            if not isinstance(cached_val, str):
                try:
                    import tkinter as tk
                    root = tk._default_root
                    if root is not None:
                        root.tk.call('image', 'height', str(cached_val))
                    return cached_val
                except Exception:
                    # Invalidate stale image reference from previous tk root
                    del self._cache[cache_key]
            else:
                return cached_val
        else:
            # Clean up stale image references from previous Tk root instances
            stale_keys = []
            for k, val in self._cache.items():
                if not isinstance(val, str):
                    try:
                        import tkinter as tk
                        root = tk._default_root
                        if root is not None:
                            root.tk.call('image', 'height', str(val))
                    except Exception:
                        stale_keys.append(k)
            for k in stale_keys:
                del self._cache[k]
        
        # Get icon info
        if name not in self.icon_map:
            # Return fallback or generic emoji
            return fallback or '❓'
        
        icon_stem, emoji = self.icon_map[name]
        # Resolve first existing icon path across known dirs
        # Priority: .png > .ico > emoji (always try .png first)
        icon_path = None
        extensions = ['.png', '.ico']  # Always prioritize .png over .ico
        
        for d in self.icon_dirs:
            for ext in extensions:
                p = d / f"{icon_stem}{ext}"
                if p.exists():
                    icon_path = p
                    break
            if icon_path:
                break
        
        # Try to load icon file
        try:
            if icon_path and icon_path.exists():
                # Prefer PIL resize if available for crisp icons
                if Image is not None and ImageTk is not None and size > 0:
                    try:
                        img = Image.open(icon_path)
                        
                        # Convert to RGBA if needed for color manipulation
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        # Apply color tint if requested
                        if color:
                            img = self._apply_color_tint(img, color)
                        
                        # Resize if needed
                        if img.width != size or img.height != size:
                            # Handle PIL v10+ and older
                            resampling = None
                            try:
                                # PIL >= 10
                                resampling = getattr(Image, 'Resampling').LANCZOS  # type: ignore[attr-defined]
                            except Exception:
                                resampling = getattr(Image, 'LANCZOS', getattr(Image, 'ANTIALIAS', None))
                            if resampling is not None:
                                img = img.resize((size, size), resampling)
                            else:
                                img = img.resize((size, size))
                        
                        icon = ImageTk.PhotoImage(img)
                        self._cache[cache_key] = icon
                        return icon
                    except Exception as e:
                        logging.warning(f"Could not process icon '{name}' with PIL: {e}")
                        # Fallback to tkinter PhotoImage without resizing/coloring
                        icon = PhotoImage(file=str(icon_path))
                        self._cache[cache_key] = icon
                        return icon
                else:
                    icon = PhotoImage(file=str(icon_path))
                    self._cache[cache_key] = icon
                    return icon
        except Exception as e:
            logging.warning(f"Could not load icon '{name}': {e}")
        
        # Fallback to emoji
        result = fallback or emoji
        self._cache[cache_key] = result
        return result
    
    def get_text(self, name: str, text: str = '', fallback: Optional[str] = None) -> str:
        """
        Get icon as text (emoji) with optional label.
        
        Args:
            name: Icon name
            text: Text label to append after emoji
            fallback: Fallback emoji
        
        Returns:
            Formatted string with emoji and text
        """
        emoji = self.icon_map.get(name, (None, fallback or '❓'))[1]
        
        if text:
            return f"{emoji} {text}"
        return emoji
    
    def has_icon_file(self, name: str) -> bool:
        """
        Check if icon file exists (.png or .ico).
        
        Args:
            name: Icon name
        
        Returns:
            True if icon file exists, False otherwise
        """
        if name not in self.icon_map:
            return False
        
        icon_stem = self.icon_map[name][0]
        extensions = ['.png', '.ico']

        for d in self.icon_dirs:
            for ext in extensions:
                p = d / f"{icon_stem}{ext}"
                if p.exists():
                    return True
        return False


# Global instance
_icon_helper = None


def get_icon_helper() -> IconHelper:
    """Get global IconHelper instance."""
    global _icon_helper
    if _icon_helper is None:
        _icon_helper = IconHelper()
    return _icon_helper
