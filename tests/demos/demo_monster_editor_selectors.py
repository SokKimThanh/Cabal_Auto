"""
Demo: Monster Editor with Window Position Selectors

Demonstrates:
1. Monster Editor with updated window selectors
2. No labels on selectors (icon + combobox only)
3. Optimal widths (app: 10, game: 8)
4. Toggle visibility methods

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

# Import Monster Editor
try:
    from ui.windows.monster_manager_win import show_monster_manager_win
except ImportError as e:
    print(f"Error importing Monster Editor: {e}")
    sys.exit(1)


def create_demo_window():
    """Create demo window to launch Monster Editor."""
    root = tk.Tk()
    root.title("Monster Editor Selector Demo")
    root.geometry("600x400")
    
    # Main container
    main_frame = tk.Frame(root, bg='#f5f5f5', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Title
    title = tk.Label(
        main_frame,
        text="👹 Monster Editor Window Selectors Demo",
        font=('Segoe UI', 14, 'bold'),
        bg='#f5f5f5',
        fg='#333'
    )
    title.pack(pady=(0, 20))
    
    # Description
    desc = tk.Label(
        main_frame,
        text="Click button below to open Monster Editor with updated window selectors",
        font=('Segoe UI', 9),
        bg='#f5f5f5',
        fg='#666'
    )
    desc.pack(pady=(0, 30))
    
    # Launch button
    launch_btn = tk.Button(
        main_frame,
        text="🚀 Launch Monster Editor",
        font=('Segoe UI', 12, 'bold'),
        bg='#2196F3',
        fg='white',
        activebackground='#1976D2',
        activeforeground='white',
        relief='raised',
        bd=3,
        cursor='hand2',
        padx=30,
        pady=15,
        command=lambda: show_monster_manager_win(
            parent=root,
            on_save=lambda data: print(f"[Demo] Saved: {data}")
        )
    )
    launch_btn.pack(pady=10)
    
    # Features list
    features_frame = tk.LabelFrame(
        main_frame,
        text="✨ Updated Features",
        font=('Segoe UI', 10, 'bold'),
        bg='#f5f5f5',
        fg='#333',
        padx=15,
        pady=10
    )
    features_frame.pack(fill='both', expand=True, pady=(20, 0))
    
    features = [
        "✅ No labels on selectors (cleaner UI)",
        "✅ App selector: width optimized (10 chars)",
        "✅ Game selector: width reduced (8 chars)",
        "✅ Detailed tooltips explain each mode",
        "✅ Icon indicators for visual feedback",
        "✅ Auto-save to hunt_config.json",
        "✅ Show/hide/toggle methods available",
        "✅ Callbacks update window state instantly"
    ]
    
    for feature in features:
        feature_label = tk.Label(
            features_frame,
            text=feature,
            font=('Segoe UI', 9),
            bg='#f5f5f5',
            fg='#333',
            anchor='w',
            justify='left'
        )
        feature_label.pack(fill='x', pady=2)
    
    # Instructions
    instructions_frame = tk.Frame(main_frame, bg='#fff3cd', relief='solid', bd=1, padx=10, pady=10)
    instructions_frame.pack(fill='x', pady=(15, 0))
    
    instructions_title = tk.Label(
        instructions_frame,
        text="📝 How to Use:",
        font=('Segoe UI', 9, 'bold'),
        bg='#fff3cd',
        fg='#856404'
    )
    instructions_title.pack(anchor='w')
    
    instructions_text = tk.Label(
        instructions_frame,
        text="1. Click 'Launch Monster Editor' button\n"
             "2. Look at top panel - you'll see 2 selectors (combobox + icon)\n"
             "3. Hover over combobox to see detailed tooltip\n"
             "4. Select different modes to test functionality\n"
             "5. App selector: controls Monster Editor window\n"
             "6. Game selector: controls game window positioning",
        font=('Segoe UI', 8),
        bg='#fff3cd',
        fg='#856404',
        justify='left'
    )
    instructions_text.pack(anchor='w', pady=(5, 0))
    
    # Keyboard shortcut info
    shortcut_frame = tk.Frame(main_frame, bg='#e3f2fd', relief='solid', bd=1, padx=10, pady=10)
    shortcut_frame.pack(fill='x', pady=(10, 0))
    
    shortcut_label = tk.Label(
        shortcut_frame,
        text="⌨️ Keyboard Shortcut: Ctrl+Shift+M (from main app)",
        font=('Segoe UI', 9, 'bold'),
        bg='#e3f2fd',
        fg='#0d47a1'
    )
    shortcut_label.pack()
    
    root.mainloop()


if __name__ == "__main__":
    print("=" * 70)
    print("Monster Editor Window Selectors Demo")
    print("=" * 70)
    print("\nUpdated Features:")
    print("  • No labels on selectors (icon + combobox only)")
    print("  • App selector width: optimized to 10 characters")
    print("  • Game selector width: reduced to 8 characters")
    print("  • Detailed tooltips with mode explanations")
    print("  • Methods: show(), hide(), toggle(), is_visible()")
    print("\nSelectors Position:")
    print("  [Title] [🪟↓][⬇️↓] [💾][✖]")
    print("           App  Game   Save Cancel")
    print("\nStarting demo...")
    print("=" * 70)
    
    create_demo_window()
