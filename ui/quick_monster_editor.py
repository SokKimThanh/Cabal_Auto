"""
Quick Monster Editor - Modal dialog for quick monster editing.

Lightweight modal window that opens with Ctrl+Shift+M hotkey.
Provides quick access to basic monster editing features.

Features:
- Topmost modal window
- Basic fields (name, level, threshold)
- Quick capture button
- Save/Cancel buttons
- All labels use lib.i18n
- All tooltips use lib.ui.tooltip

Author: SokKimThanh
Created: 2025-10-24
Status: Skeleton
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable

# TODO: Import lib modules
# from lib.i18n import t as i18n_t, get_lang
# from lib.ui.tooltip import attach_i18n_tooltip
# from lib.ui_style import UIStyle as UI
# from lib.features.monster_manager import get_monster_manager
# from lib.features.worker import get_worker


class QuickMonsterEditor(tk.Toplevel):
    """
    Quick monster editor modal dialog.
    
    Features:
    - Lightweight UI
    - Quick monster edit
    - Hotkey access (Ctrl+Shift+M)
    - Topmost window
    - Non-blocking operations
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        monster_id: Optional[str] = None,
        on_save: Optional[Callable] = None
    ):
        """
        Initialize QuickMonsterEditor.
        
        Args:
            parent: Parent widget
            monster_id: Monster to edit (None for new monster)
            on_save: Callback when monster is saved
        """
        super().__init__(parent)
        
        self.parent = parent
        self.monster_id = monster_id
        self.on_save_callback = on_save
        
        # Window configuration
        self.title("Quick Monster Editor")  # TODO: Use i18n
        self.geometry("400x300")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Data
        self.monster_data: Dict[str, Any] = {}
        
        # Widgets (will be created in setup_ui)
        self.name_entry: Optional[tk.Entry] = None
        self.level_spinbox: Optional[tk.Spinbox] = None
        self.threshold_scale: Optional[tk.Scale] = None
        
        # Setup
        self._load_monster()
        self._setup_ui()
        self._bind_events()
    
    def _load_monster(self) -> None:
        """Load monster data if editing existing monster."""
        # TODO: Implement monster loading
        # If monster_id is not None:
        #   Load from monster_manager
        #   Populate self.monster_data
        pass
    
    def _setup_ui(self) -> None:
        """Create UI components."""
        # TODO: Implement UI setup
        # Create form fields
        # Add buttons
        # Add tooltips
        pass
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        # TODO: Implement event binding
        # Bind save button
        # Bind cancel button
        # Bind window close
        pass
    
    def _on_save(self) -> None:
        """Handle save button click."""
        # TODO: Implement save logic
        # Validate input
        # Save to monster_manager
        # Call on_save_callback
        # Close window
        pass
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        # TODO: Implement cancel logic
        self.destroy()
    
    def _on_capture(self) -> None:
        """Handle capture button click."""
        # TODO: Implement capture logic
        # Start capture in worker thread
        # Show progress
        # Add template to monster
        pass


# Singleton instance
_quick_editor_instance: Optional[QuickMonsterEditor] = None


def show_quick_monster_editor(
    parent: tk.Widget,
    monster_id: Optional[str] = None,
    on_save: Optional[Callable] = None
) -> QuickMonsterEditor:
    """
    Show quick monster editor (singleton).
    
    Args:
        parent: Parent widget
        monster_id: Monster to edit (None for new)
        on_save: Callback when saved
    
    Returns:
        QuickMonsterEditor: Editor instance
    """
    global _quick_editor_instance
    
    if _quick_editor_instance is not None and _quick_editor_instance.winfo_exists():
        _quick_editor_instance.lift()
        _quick_editor_instance.focus_force()
        return _quick_editor_instance
    else:
        _quick_editor_instance = QuickMonsterEditor(parent, monster_id, on_save)
        return _quick_editor_instance
