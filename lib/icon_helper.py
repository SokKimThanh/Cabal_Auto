# -*- coding: utf-8 -*-
"""
Icon Helper - Load icons with fallback to Unicode emoji.

This module provides a centralized way to load icons from files,
with automatic fallback to Unicode emoji if icons are not available.

Usage:
    from lib.icon_helper import IconHelper
    
    icon_helper = IconHelper()
    add_icon = icon_helper.get_icon('add', fallback='➕')
"""

import os
import sys
from pathlib import Path
from tkinter import PhotoImage
from typing import Optional, Union


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
            self.root_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.root_dir = Path(__file__).parent.parent
        
        # Icon directory
        self.icon_dir = self.root_dir / 'images' / 'icons'
        
        # Create directory if it doesn't exist
        self.icon_dir.mkdir(parents=True, exist_ok=True)
        
        # Icon cache
        self._cache = {}
        
        # Default icon mappings
        self.icon_map = {
            'add': ('add.png', '➕'),
            'edit': ('edit.png', '✏️'),
            'delete': ('delete.png', '🗑️'),
            'save': ('save.png', '💾'),
            'cancel': ('cancel.png', '✖'),
            'folder': ('folder.png', '📁'),
            'capture': ('capture.png', '📸'),
            'search': ('search.png', '🔍'),
            'monster': ('monster.png', '👹'),
            'skill': ('skill.png', '⚔️'),
            'template': ('template.png', '🖼️'),
            'list': ('list.png', '🗂️'),
            'info': ('info.png', '📋'),
            'time': ('time.png', '⏱️'),
            'hp': ('hp.png', '❤️'),
            'damage': ('damage.png', '⚔️'),
            'priority': ('priority.png', '🎯'),
        }
    
    def get_icon(self, name: str, fallback: Optional[str] = None, size: int = 24) -> Union[PhotoImage, str]:
        """
        Get icon by name, with fallback to emoji.
        
        Args:
            name: Icon name (e.g., 'add', 'edit', 'delete')
            fallback: Fallback emoji character (optional)
            size: Icon size in pixels (default: 24)
        
        Returns:
            PhotoImage object if icon file exists, otherwise emoji string
        """
        # Check cache
        cache_key = f"{name}_{size}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get icon info
        if name not in self.icon_map:
            # Return fallback or generic emoji
            return fallback or '❓'
        
        icon_file, emoji = self.icon_map[name]
        icon_path = self.icon_dir / icon_file
        
        # Try to load icon file
        try:
            if icon_path.exists():
                icon = PhotoImage(file=str(icon_path))
                # Resize if needed (tkinter doesn't support direct resize, use subsample)
                if size != 24:
                    # Simple scaling (not ideal but works)
                    factor = 24 // size if size < 24 else 1
                    if factor > 1:
                        icon = icon.subsample(factor, factor)
                
                # Cache and return
                self._cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"Warning: Could not load icon '{name}': {e}")
        
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
        Check if icon file exists.
        
        Args:
            name: Icon name
        
        Returns:
            True if icon file exists, False otherwise
        """
        if name not in self.icon_map:
            return False
        
        icon_file = self.icon_map[name][0]
        icon_path = self.icon_dir / icon_file
        return icon_path.exists()


# Global instance
_icon_helper = None


def get_icon_helper() -> IconHelper:
    """Get global IconHelper instance."""
    global _icon_helper
    if _icon_helper is None:
        _icon_helper = IconHelper()
    return _icon_helper
