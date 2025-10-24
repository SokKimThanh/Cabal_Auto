"""
Visual comparison test: Emoji vs Icon Files

This test creates two windows side-by-side:
1. Using app_gui emoji approach
2. Using demo icon file approach
"""
import sys
from pathlib import Path
import tkinter as tk

# Add project to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ui.components import create_icon_button
from lib.ui_style import UIStyle as UI

def test_comparison():
    """Create comparison window."""
    root = tk.Tk()
    root.title("Icon Comparison: Emoji vs Icon Files")
    root.geometry("800x400")
    root.configure(bg='#f0f0f0')
    
    # Title
    title = tk.Label(
        root,
        text="Icon Display Comparison",
        font=('Arial', 16, 'bold'),
        bg='#f0f0f0'
    )
    title.pack(pady=10)
    
    # Container for both sides
    container = tk.Frame(root, bg='#f0f0f0')
    container.pack(fill='both', expand=True, padx=20, pady=10)
    
    # === LEFT SIDE: app_gui emoji approach ===
    left_frame = tk.LabelFrame(
        container,
        text="app_gui Approach (Emoji Text Only)",
        font=('Arial', 12, 'bold'),
        bg='#f0f0f0',
        padx=20,
        pady=20
    )
    left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    tk.Label(
        left_frame,
        text="Uses plain Unicode emoji text",
        font=('Arial', 10),
        bg='#f0f0f0'
    ).pack(pady=(0, 10))
    
    # Emoji buttons (app_gui style)
    emoji_buttons = [
        ("Add", "➕", UI.BTN_ACCENT_BG),
        ("Delete", "🗑️", UI.BTN_DANGER_BG),
        ("Save", "💾", UI.BTN_PRIMARY_BG),
        ("Cancel", "✖", UI.BTN_NEUTRAL_BG),
        ("Refresh", "🔄", UI.BTN_INFO_BG),
        ("Search", "🔍", UI.BTN_INFO_BG),
    ]
    
    for label, emoji, bg_color in emoji_buttons:
        btn_frame = tk.Frame(left_frame, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=5)
        
        tk.Label(
            btn_frame,
            text=f"{label}:",
            font=('Arial', 10),
            bg='#f0f0f0',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        # Emoji button
        tk.Button(
            btn_frame,
            text=emoji,
            font=('Arial', 12),
            bg=bg_color,
            fg='white',
            width=3,
            height=1,
            relief='raised',
            bd=2
        ).pack(side='left', padx=5)
        
        tk.Label(
            btn_frame,
            text=f"'{emoji}' (Unicode emoji)",
            font=('Arial', 9),
            fg='#666',
            bg='#f0f0f0'
        ).pack(side='left', padx=5)
    
    # === RIGHT SIDE: demo icon file approach ===
    right_frame = tk.LabelFrame(
        container,
        text="Demo Approach (Icon Files)",
        font=('Arial', 12, 'bold'),
        bg='#f0f0f0',
        padx=20,
        pady=20
    )
    right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
    
    tk.Label(
        right_frame,
        text="Loads .ico files via IconHelper",
        font=('Arial', 10),
        bg='#f0f0f0'
    ).pack(pady=(0, 10))
    
    # Icon file buttons (demo style)
    icon_buttons = [
        ("Add", "add", "➕", "green_light"),
        ("Delete", "delete", "🗑️", "red"),
        ("Save", "save", "💾", "green_light"),
        ("Cancel", "cancel", "✖", "refresh"),
        ("Refresh", "refresh", "🔄", "blue"),
        ("Search", "search", "🔍", "blue"),
    ]
    
    for label, icon_name, fallback, button_type in icon_buttons:
        btn_frame = tk.Frame(right_frame, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=5)
        
        tk.Label(
            btn_frame,
            text=f"{label}:",
            font=('Arial', 10),
            bg='#f0f0f0',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        # Icon file button
        create_icon_button(
            btn_frame,
            icon_name=icon_name,
            icon_fallback=fallback,
            icon_size=16,
            command=lambda: None,
            button_type=button_type,
            variant='compact',
            width=3
        ).pack(side='left', padx=5)
        
        tk.Label(
            btn_frame,
            text=f"{icon_name}.ico (PhotoImage)",
            font=('Arial', 9),
            fg='#666',
            bg='#f0f0f0'
        ).pack(side='left', padx=5)
    
    # Bottom info
    info_frame = tk.Frame(root, bg='#f0f0f0')
    info_frame.pack(side='bottom', fill='x', padx=20, pady=10)
    
    tk.Label(
        info_frame,
        text="Notice: Icon files (right) are higher quality and consistent. Emojis (left) depend on system fonts.",
        font=('Arial', 9, 'italic'),
        fg='#666',
        bg='#f0f0f0',
        wraplength=700
    ).pack()
    
    root.mainloop()

if __name__ == '__main__':
    test_comparison()
