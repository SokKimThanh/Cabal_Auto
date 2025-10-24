"""
Demo: Window Position Selector Toggle

Demonstrates:
1. Show/hide selectors individually
2. Width adjustments for game window selector
3. Toggle buttons to control visibility

Author: SokKimThanh
Created: 2025-10-25
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk

# Import window selectors
try:
    from ui.components.window_position_selector import (
        create_app_window_selector,
        create_game_window_selector
    )
except ImportError as e:
    print(f"Error importing window selectors: {e}")
    sys.exit(1)


def create_demo_window():
    """Create demo window with toggle controls."""
    root = tk.Tk()
    root.title("Window Selector Toggle Demo")
    root.geometry("600x300")
    
    # Main container
    main_frame = tk.Frame(root, bg='#f5f5f5', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Title
    title = tk.Label(
        main_frame,
        text="🪟 Window Position Selector Toggle Demo",
        font=('Segoe UI', 14, 'bold'),
        bg='#f5f5f5',
        fg='#333'
    )
    title.pack(pady=(0, 20))
    
    # Info label
    info = tk.Label(
        main_frame,
        text="Sử dụng các nút toggle để bật/tắt từng selector",
        font=('Segoe UI', 9),
        bg='#f5f5f5',
        fg='#666'
    )
    info.pack(pady=(0, 20))
    
    # Selectors frame
    selectors_frame = tk.Frame(main_frame, bg='#e0e0e0', relief='sunken', bd=2, padx=10, pady=10)
    selectors_frame.pack(fill='x', pady=(0, 20))
    
    selector_label = tk.Label(
        selectors_frame,
        text="Selectors:",
        font=('Segoe UI', 10, 'bold'),
        bg='#e0e0e0',
        fg='#333'
    )
    selector_label.pack(side='left', padx=(0, 10))
    
    # Create selectors
    app_selector = create_app_window_selector(
        parent=selectors_frame,
        config_path="lib/data/hunt_config.json",
        on_mode_change=lambda mode: print(f"[Demo] App mode: {mode}")
    )
    app_selector.pack(side='left', padx=(0, 8))
    
    game_selector = create_game_window_selector(
        parent=selectors_frame,
        config_path="lib/data/hunt_config.json",
        on_mode_change=lambda mode: print(f"[Demo] Game mode: {mode}")
    )
    game_selector.pack(side='left')
    
    # Control buttons frame
    controls_frame = tk.Frame(main_frame, bg='#f5f5f5')
    controls_frame.pack(fill='x')
    
    # App selector toggle
    app_toggle_btn = tk.Button(
        controls_frame,
        text="🪟 Toggle App Selector",
        font=('Segoe UI', 10),
        bg='#2196F3',
        fg='white',
        activebackground='#1976D2',
        activeforeground='white',
        relief='raised',
        bd=2,
        cursor='hand2',
        padx=12,
        pady=8,
        command=app_selector.toggle
    )
    app_toggle_btn.pack(side='left', padx=(0, 10))
    
    # Game selector toggle
    game_toggle_btn = tk.Button(
        controls_frame,
        text="⬇️ Toggle Game Selector",
        font=('Segoe UI', 10),
        bg='#FF9800',
        fg='white',
        activebackground='#F57C00',
        activeforeground='white',
        relief='raised',
        bd=2,
        cursor='hand2',
        padx=12,
        pady=8,
        command=game_selector.toggle
    )
    game_toggle_btn.pack(side='left', padx=(0, 10))
    
    # Hide both button
    hide_both_btn = tk.Button(
        controls_frame,
        text="🚫 Hide Both",
        font=('Segoe UI', 10),
        bg='#757575',
        fg='white',
        activebackground='#616161',
        activeforeground='white',
        relief='raised',
        bd=2,
        cursor='hand2',
        padx=12,
        pady=8,
        command=lambda: (app_selector.hide(), game_selector.hide())
    )
    hide_both_btn.pack(side='left', padx=(0, 10))
    
    # Show both button
    show_both_btn = tk.Button(
        controls_frame,
        text="✅ Show Both",
        font=('Segoe UI', 10),
        bg='#2E7D32',
        fg='white',
        activebackground='#1B5E20',
        activeforeground='white',
        relief='raised',
        bd=2,
        cursor='hand2',
        padx=12,
        pady=8,
        command=lambda: (app_selector.show(), game_selector.show())
    )
    show_both_btn.pack(side='left')
    
    # Status frame
    status_frame = tk.Frame(main_frame, bg='#f5f5f5')
    status_frame.pack(fill='x', pady=(20, 0))
    
    status_label = tk.Label(
        status_frame,
        text="Status:",
        font=('Segoe UI', 9, 'bold'),
        bg='#f5f5f5',
        fg='#333'
    )
    status_label.pack(side='left', padx=(0, 10))
    
    # Update status function
    def update_status():
        app_visible = "✅ Visible" if app_selector.is_visible() else "❌ Hidden"
        game_visible = "✅ Visible" if game_selector.is_visible() else "❌ Hidden"
        app_mode = app_selector.get_mode()
        game_mode = game_selector.get_mode()
        
        status_text.config(
            text=f"App: {app_visible} (mode: {app_mode}) | Game: {game_visible} (mode: {game_mode})"
        )
        root.after(500, update_status)  # Update every 500ms
    
    status_text = tk.Label(
        status_frame,
        text="...",
        font=('Segoe UI', 9),
        bg='#f5f5f5',
        fg='#666'
    )
    status_text.pack(side='left')
    
    # Start status updates
    update_status()
    
    # Instructions
    instructions_frame = tk.Frame(main_frame, bg='#fff3cd', relief='solid', bd=1, padx=10, pady=10)
    instructions_frame.pack(fill='x', pady=(20, 0))
    
    instructions_title = tk.Label(
        instructions_frame,
        text="💡 Instructions:",
        font=('Segoe UI', 9, 'bold'),
        bg='#fff3cd',
        fg='#856404'
    )
    instructions_title.pack(anchor='w')
    
    instructions_text = tk.Label(
        instructions_frame,
        text="• Click 'Toggle' buttons to show/hide individual selectors\n"
             "• Use 'Hide Both' to hide all selectors\n"
             "• Use 'Show Both' to show all selectors\n"
             "• Status updates automatically every 500ms\n"
             "• Game selector width reduced from 10 to 8 for better spacing",
        font=('Segoe UI', 8),
        bg='#fff3cd',
        fg='#856404',
        justify='left'
    )
    instructions_text.pack(anchor='w', pady=(5, 0))
    
    root.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("Window Position Selector Toggle Demo")
    print("=" * 60)
    print("\nFeatures:")
    print("  1. Show/hide app window selector")
    print("  2. Show/hide game window selector")
    print("  3. Width optimization (game: 10 → 8)")
    print("  4. Real-time status updates")
    print("\nStarting demo...")
    print("=" * 60)
    
    create_demo_window()
