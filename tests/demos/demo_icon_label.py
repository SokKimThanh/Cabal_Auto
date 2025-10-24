"""
Demo: Icon Label Component

Demonstrates the use of create_icon_label() component.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import tkinter as tk
from ui.components import create_icon_label

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    class UIStyle:
        FONT_TITLE = ('Segoe UI', 12, 'bold')
        FONT_SECTION = ('Segoe UI', 11, 'bold')
        FONT_LABEL = ('Segoe UI', 10)
        COLOR_PRIMARY_TEXT = '#0D47A1'
        COLOR_TEXT = '#333'
        BG_DEFAULT = '#FFFFFF'
        BG_PANEL = '#F5F5F5'
    UI = UIStyle


def create_demo():
    """Create demo window."""
    root = tk.Tk()
    root.title("Icon Label Component Demo")
    root.geometry("500x600")
    root.configure(bg=UI.BG_DEFAULT)
    
    # Title
    title = tk.Label(
        root,
        text="Icon Label Component Demo",
        font=UI.FONT_TITLE,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_DEFAULT
    )
    title.pack(pady=(20, 10))
    
    # Section 1: Basic labels
    section1_frame = tk.Frame(root, bg=UI.BG_PANEL)
    section1_frame.pack(fill='x', padx=20, pady=10)
    
    section1_title = create_icon_label(
        section1_frame,
        icon_name='list',
        text='Basic Labels',
        icon_fallback='🗂️',
        icon_size=16,
        font=UI.FONT_SECTION,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_PANEL
    )
    section1_title.pack(anchor='w', padx=10, pady=(10, 5))
    
    # Monster label
    monster_label = create_icon_label(
        section1_frame,
        icon_name='monster',
        text='Monster Name:',
        icon_fallback='👹',
        icon_size=16,
        tooltip_text='Enter the monster name',
        bg=UI.BG_PANEL
    )
    monster_label.pack(anchor='w', padx=20, pady=5)
    
    # Level label
    level_label = create_icon_label(
        section1_frame,
        icon_name='up',
        text='Level:',
        icon_fallback='↑',
        icon_size=16,
        tooltip_text='Monster level',
        bg=UI.BG_PANEL
    )
    level_label.pack(anchor='w', padx=20, pady=5)
    
    # HP label
    hp_label = create_icon_label(
        section1_frame,
        icon_name='hp',
        text='HP:',
        icon_fallback='❤️',
        icon_size=16,
        tooltip_text='Health points',
        bg=UI.BG_PANEL
    )
    hp_label.pack(anchor='w', padx=20, pady=(5, 10))
    
    # Section 2: Info labels
    section2_frame = tk.Frame(root, bg=UI.BG_PANEL)
    section2_frame.pack(fill='x', padx=20, pady=10)
    
    section2_title = create_icon_label(
        section2_frame,
        icon_name='info',
        text='Information Labels',
        icon_fallback='📋',
        icon_size=16,
        font=UI.FONT_SECTION,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_PANEL
    )
    section2_title.pack(anchor='w', padx=10, pady=(10, 5))
    
    # Priority label
    priority_label = create_icon_label(
        section2_frame,
        icon_name='priority',
        text='Priority:',
        icon_fallback='🎯',
        icon_size=16,
        tooltip_text='Monster priority',
        bg=UI.BG_PANEL
    )
    priority_label.pack(anchor='w', padx=20, pady=5)
    
    # Damage label
    damage_label = create_icon_label(
        section2_frame,
        icon_name='damage',
        text='Damage:',
        icon_fallback='⚔️',
        icon_size=16,
        tooltip_text='Damage per hit',
        bg=UI.BG_PANEL
    )
    damage_label.pack(anchor='w', padx=20, pady=5)
    
    # Settings label
    settings_label = create_icon_label(
        section2_frame,
        icon_name='settings',
        text='Settings:',
        icon_fallback='⚙️',
        icon_size=16,
        tooltip_text='Configuration settings',
        bg=UI.BG_PANEL
    )
    settings_label.pack(anchor='w', padx=20, pady=(5, 10))
    
    # Section 3: Action labels
    section3_frame = tk.Frame(root, bg=UI.BG_PANEL)
    section3_frame.pack(fill='x', padx=20, pady=10)
    
    section3_title = create_icon_label(
        section3_frame,
        icon_name='folder',
        text='Action Labels',
        icon_fallback='📁',
        icon_size=16,
        font=UI.FONT_SECTION,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_PANEL
    )
    section3_title.pack(anchor='w', padx=10, pady=(10, 5))
    
    # Save label
    save_label = create_icon_label(
        section3_frame,
        icon_name='save',
        text='Saved successfully',
        icon_fallback='💾',
        icon_size=16,
        fg='#2E7D32',
        bg=UI.BG_PANEL
    )
    save_label.pack(anchor='w', padx=20, pady=5)
    
    # Warning label
    warning_label = create_icon_label(
        section3_frame,
        icon_name='warning',
        text='Unsaved changes',
        icon_fallback='⚠️',
        icon_size=16,
        fg='#FF9800',
        bg=UI.BG_PANEL
    )
    warning_label.pack(anchor='w', padx=20, pady=5)
    
    # Delete label
    delete_label = create_icon_label(
        section3_frame,
        icon_name='delete',
        text='Item deleted',
        icon_fallback='🗑️',
        icon_size=16,
        fg='#C62828',
        bg=UI.BG_PANEL
    )
    delete_label.pack(anchor='w', padx=20, pady=(5, 10))
    
    # Section 4: Icon only
    section4_frame = tk.Frame(root, bg=UI.BG_PANEL)
    section4_frame.pack(fill='x', padx=20, pady=10)
    
    section4_title = tk.Label(
        section4_frame,
        text='Icon Only',
        font=UI.FONT_SECTION,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_PANEL
    )
    section4_title.pack(anchor='w', padx=10, pady=(10, 5))
    
    icon_frame = tk.Frame(section4_frame, bg=UI.BG_PANEL)
    icon_frame.pack(anchor='w', padx=20, pady=(5, 10))
    
    # Icon only labels
    icons = [
        ('add', '➕', 'Add'),
        ('edit', '✏️', 'Edit'),
        ('delete', '🗑️', 'Delete'),
        ('search', '🔍', 'Search'),
        ('refresh', '🔄', 'Refresh'),
        ('check', '✓', 'Check'),
    ]
    
    for icon_name, fallback, tooltip in icons:
        icon_label = create_icon_label(
            icon_frame,
            icon_name=icon_name,
            text='',
            icon_fallback=fallback,
            icon_size=20,
            tooltip_text=tooltip,
            bg=UI.BG_PANEL
        )
        icon_label.pack(side='left', padx=5)
    
    root.mainloop()


if __name__ == '__main__':
    create_demo()
