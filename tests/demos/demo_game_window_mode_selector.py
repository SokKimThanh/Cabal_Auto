"""
Demo: Game Window Mode Selector Component

Demonstrates usage of GameWindowModeSelector component.

Run this file to see the component in action:
    python tests/demos/demo_game_window_mode_selector.py

Author: SokKimThanh
Created: 2025-10-24
"""
import sys
import tkinter as tk
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ui.components.game_window_mode_selector import create_game_window_mode_selector


def demo_basic():
    """Demo 1: Basic usage without callback."""
    root = tk.Tk()
    root.title("Demo: Game Window Mode Selector - Basic")
    root.geometry("400x200")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Demo 1: Basic Selector",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Frame for selector
    frame = tk.Frame(root, bg='#F5F5F5')
    frame.pack(pady=10)
    
    # Create selector (basic)
    selector = create_game_window_mode_selector(
        parent=frame,
        config_path="tests/tmp/demo_config.json"
    )
    selector.pack()
    
    # Info label
    info = tk.Label(
        root,
        text="Change mode and check tests/tmp/demo_config.json",
        font=('Segoe UI', 9),
        bg='#F5F5F5',
        fg='#666'
    )
    info.pack(pady=10)
    
    root.mainloop()


def demo_with_callback():
    """Demo 2: With callback function."""
    root = tk.Tk()
    root.title("Demo: Game Window Mode Selector - With Callback")
    root.geometry("500x300")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Demo 2: Selector with Callback",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Status label
    status_label = tk.Label(
        root,
        text="Current mode: none",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#2196F3'
    )
    status_label.pack(pady=10)
    
    # Log text widget
    log_frame = tk.Frame(root, bg='#F5F5F5')
    log_frame.pack(pady=10, padx=20, fill='both', expand=True)
    
    log_text = tk.Text(
        log_frame,
        height=8,
        width=50,
        font=('Consolas', 9),
        bg='#FFFFFF',
        fg='#333333'
    )
    log_text.pack(fill='both', expand=True)
    
    def log_message(msg: str):
        """Add message to log."""
        log_text.insert('end', f"{msg}\n")
        log_text.see('end')
    
    # Callback function
    def on_mode_changed(mode: str):
        """Handle mode change."""
        status_label.config(text=f"Current mode: {mode}")
        log_message(f"[Callback] Mode changed to: {mode}")
        
        if mode == "none":
            log_message("  → Game window will not be launched")
        elif mode == "below":
            log_message("  → Game window will appear below app")
        elif mode == "above":
            log_message("  → Game window will appear above app (topmost)")
    
    # Frame for selector
    selector_frame = tk.Frame(root, bg='#F5F5F5')
    selector_frame.pack(pady=10)
    
    # Create selector with callback
    selector = create_game_window_mode_selector(
        parent=selector_frame,
        config_path="tests/tmp/demo_config.json",
        on_mode_change=on_mode_changed,
        initial_mode="none",
        show_label=True,
        label_text="Game Window:"
    )
    selector.pack()
    
    # Initial log
    log_message("[Info] Select a mode from the dropdown")
    log_message("[Info] Config saved to: tests/tmp/demo_config.json")
    
    root.mainloop()


def demo_multiple_selectors():
    """Demo 3: Multiple selectors in same window."""
    root = tk.Tk()
    root.title("Demo: Multiple Selectors")
    root.geometry("600x400")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Demo 3: Multiple Selectors",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Selector 1 - With label
    frame1 = tk.LabelFrame(
        root,
        text="Selector 1: Full (with label)",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame1.pack(pady=10, padx=20, fill='x')
    
    selector1 = create_game_window_mode_selector(
        parent=frame1,
        config_path="tests/tmp/demo_config1.json",
        show_label=True,
        label_text="Main Game:"
    )
    selector1.pack()
    
    # Selector 2 - Without label
    frame2 = tk.LabelFrame(
        root,
        text="Selector 2: Compact (no label)",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame2.pack(pady=10, padx=20, fill='x')
    
    selector2 = create_game_window_mode_selector(
        parent=frame2,
        config_path="tests/tmp/demo_config2.json",
        show_label=False,
        icon_size=14
    )
    selector2.pack()
    
    # Selector 3 - Custom label
    frame3 = tk.LabelFrame(
        root,
        text="Selector 3: Custom label",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame3.pack(pady=10, padx=20, fill='x')
    
    selector3 = create_game_window_mode_selector(
        parent=frame3,
        config_path="tests/tmp/demo_config3.json",
        show_label=True,
        label_text="Secondary:",
        tooltip_text="Choose display mode for secondary window"
    )
    selector3.pack()
    
    root.mainloop()


def demo_programmatic_control():
    """Demo 4: Programmatic control of selector."""
    root = tk.Tk()
    root.title("Demo: Programmatic Control")
    root.geometry("500x300")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Demo 4: Programmatic Control",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Frame for selector
    selector_frame = tk.Frame(root, bg='#F5F5F5')
    selector_frame.pack(pady=10)
    
    # Create selector
    selector = create_game_window_mode_selector(
        parent=selector_frame,
        config_path="tests/tmp/demo_config.json",
        show_label=True
    )
    selector.pack()
    
    # Control buttons
    button_frame = tk.Frame(root, bg='#F5F5F5')
    button_frame.pack(pady=20)
    
    def set_none():
        selector.set_mode('none')
    
    def set_below():
        selector.set_mode('below')
    
    def set_above():
        selector.set_mode('above')
    
    def get_current():
        mode = selector.get_mode()
        status.config(text=f"Current mode: {mode}")
    
    tk.Button(
        button_frame,
        text="Set: None",
        command=set_none,
        width=12
    ).pack(side='left', padx=5)
    
    tk.Button(
        button_frame,
        text="Set: Below",
        command=set_below,
        width=12
    ).pack(side='left', padx=5)
    
    tk.Button(
        button_frame,
        text="Set: Above",
        command=set_above,
        width=12
    ).pack(side='left', padx=5)
    
    tk.Button(
        button_frame,
        text="Get Current",
        command=get_current,
        width=12
    ).pack(side='left', padx=5)
    
    # Status
    status = tk.Label(
        root,
        text="Use buttons to control selector programmatically",
        font=('Segoe UI', 9),
        bg='#F5F5F5',
        fg='#666'
    )
    status.pack(pady=10)
    
    root.mainloop()


if __name__ == '__main__':
    print("Game Window Mode Selector - Demo")
    print("=" * 50)
    print("Choose a demo to run:")
    print("1. Basic usage")
    print("2. With callback")
    print("3. Multiple selectors")
    print("4. Programmatic control")
    print()
    
    choice = input("Enter choice (1-4, or 'all' to run all): ").strip()
    
    if choice == '1':
        demo_basic()
    elif choice == '2':
        demo_with_callback()
    elif choice == '3':
        demo_multiple_selectors()
    elif choice == '4':
        demo_programmatic_control()
    elif choice.lower() == 'all':
        print("\nRunning all demos sequentially...")
        print("Close each window to see the next demo\n")
        demo_basic()
        demo_with_callback()
        demo_multiple_selectors()
        demo_programmatic_control()
    else:
        print("Invalid choice. Running demo 2 (with callback)...")
        demo_with_callback()
