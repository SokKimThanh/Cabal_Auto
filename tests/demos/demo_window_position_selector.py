"""
Demo: Window Position Selector - Universal Component

Demonstrates the universal window position selector for both app and game windows.

Run: python tests/demos/demo_window_position_selector.py
"""
import sys
import tkinter as tk
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ui.components.window_position_selector import (
    create_window_position_selector,
    create_app_window_selector,
    create_game_window_selector
)


def demo_app_and_game():
    """Demo: App and Game window selectors side by side."""
    root = tk.Tk()
    root.title("Demo: App & Game Window Selectors")
    root.geometry("600x400")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Window Position Selectors",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Status display
    status_frame = tk.Frame(root, bg='#F5F5F5')
    status_frame.pack(pady=10)
    
    app_status = tk.Label(
        status_frame,
        text="App: normal",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#2196F3',
        width=20
    )
    app_status.pack(side='left', padx=10)
    
    game_status = tk.Label(
        status_frame,
        text="Game: none",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#4CAF50',
        width=20
    )
    game_status.pack(side='left', padx=10)
    
    # Callbacks
    def on_app_change(mode: str):
        app_status.config(text=f"App: {mode}")
        log_text.insert('end', f"[App] Mode: {mode}\n")
        log_text.see('end')
    
    def on_game_change(mode: str):
        game_status.config(text=f"Game: {mode}")
        log_text.insert('end', f"[Game] Mode: {mode}\n")
        log_text.see('end')
    
    # Selectors frame
    selectors_frame = tk.LabelFrame(
        root,
        text="Window Controls",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=15
    )
    selectors_frame.pack(pady=10, padx=20, fill='x')
    
    # App selector
    app_frame = tk.Frame(selectors_frame, bg='#F5F5F5')
    app_frame.pack(pady=5)
    
    app_selector = create_app_window_selector(
        parent=app_frame,
        config_path="tests/tmp/app_config.json",
        on_mode_change=on_app_change
    )
    app_selector.pack()
    
    # Game selector
    game_frame = tk.Frame(selectors_frame, bg='#F5F5F5')
    game_frame.pack(pady=5)
    
    game_selector = create_game_window_selector(
        parent=game_frame,
        config_path="tests/tmp/game_config.json",
        on_mode_change=on_game_change
    )
    game_selector.pack()
    
    # Log
    log_frame = tk.LabelFrame(
        root,
        text="Event Log",
        font=('Segoe UI', 9),
        bg='#F5F5F5',
        padx=10,
        pady=5
    )
    log_frame.pack(pady=10, padx=20, fill='both', expand=True)
    
    log_text = tk.Text(
        log_frame,
        height=8,
        font=('Consolas', 9),
        bg='#FFFFFF'
    )
    log_text.pack(fill='both', expand=True)
    
    log_text.insert('end', "[Info] Select modes to see changes\n")
    log_text.insert('end', "[Info] App config: tests/tmp/app_config.json\n")
    log_text.insert('end', "[Info] Game config: tests/tmp/game_config.json\n\n")
    
    root.mainloop()


def demo_custom_modes():
    """Demo: Custom window selector with custom modes."""
    root = tk.Tk()
    root.title("Demo: Custom Modes")
    root.geometry("500x400")
    root.configure(bg='#F5F5F5')
    
    title = tk.Label(
        root,
        text="Custom Window Selector",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Status
    status = tk.Label(
        root,
        text="Mode: normal",
        font=('Segoe UI', 11),
        bg='#F5F5F5',
        fg='#FF5722'
    )
    status.pack(pady=10)
    
    def on_change(mode: str):
        status.config(text=f"Mode: {mode}")
        desc_text = {
            'fullscreen': 'Window fills entire screen',
            'center': 'Window centered on screen',
            'left': 'Window on left side',
            'right': 'Window on right side',
            'topmost': 'Window always on top',
            'normal': 'Normal window behavior'
        }
        info.config(text=desc_text.get(mode, ''))
    
    # Custom selector with all positioning modes
    frame = tk.LabelFrame(
        root,
        text="Select Position",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=15
    )
    frame.pack(pady=10, padx=20)
    
    selector = create_window_position_selector(
        parent=frame,
        config_path="tests/tmp/custom_config.json",
        config_key="custom_window_mode",
        modes=['normal', 'topmost', 'fullscreen', 'center', 'left', 'right'],
        label_text="Position:",
        tooltip_text="Choose window position on screen",
        window_type="window",
        on_mode_change=on_change
    )
    selector.pack()
    
    # Info label
    info = tk.Label(
        root,
        text="Normal window behavior",
        font=('Segoe UI', 9, 'italic'),
        bg='#F5F5F5',
        fg='#666',
        wraplength=400
    )
    info.pack(pady=20)
    
    root.mainloop()


def demo_multiple_windows():
    """Demo: Multiple window selectors."""
    root = tk.Tk()
    root.title("Demo: Multiple Windows")
    root.geometry("700x500")
    root.configure(bg='#F5F5F5')
    
    title = tk.Label(
        root,
        text="Multiple Window Selectors",
        font=('Segoe UI', 14, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Main app window
    frame1 = tk.LabelFrame(
        root,
        text="Main Application Window",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame1.pack(pady=5, padx=20, fill='x')
    
    sel1 = create_app_window_selector(
        parent=frame1,
        config_path="tests/tmp/main_app_config.json"
    )
    sel1.pack()
    
    # Game window
    frame2 = tk.LabelFrame(
        root,
        text="Game Window",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame2.pack(pady=5, padx=20, fill='x')
    
    sel2 = create_game_window_selector(
        parent=frame2,
        config_path="tests/tmp/game_window_config.json"
    )
    sel2.pack()
    
    # Overlay window
    frame3 = tk.LabelFrame(
        root,
        text="Overlay Window",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame3.pack(pady=5, padx=20, fill='x')
    
    sel3 = create_window_position_selector(
        parent=frame3,
        config_path="tests/tmp/overlay_config.json",
        config_key="overlay_mode",
        modes=['hidden', 'topmost', 'normal'],
        label_text="Overlay:",
        tooltip_text="Control overlay window visibility"
    )
    sel3.pack()
    
    # Debug window
    frame4 = tk.LabelFrame(
        root,
        text="Debug Console",
        font=('Segoe UI', 10, 'bold'),
        bg='#F5F5F5',
        padx=20,
        pady=10
    )
    frame4.pack(pady=5, padx=20, fill='x')
    
    sel4 = create_window_position_selector(
        parent=frame4,
        config_path="tests/tmp/debug_config.json",
        config_key="debug_mode",
        modes=['hidden', 'minimized', 'normal'],
        label_text="Console:",
        tooltip_text="Control debug console"
    )
    sel4.pack()
    
    info = tk.Label(
        root,
        text="Each selector manages its own config file independently",
        font=('Segoe UI', 8),
        bg='#F5F5F5',
        fg='#666'
    )
    info.pack(pady=10)
    
    root.mainloop()


if __name__ == '__main__':
    print("Window Position Selector - Universal Component Demo")
    print("=" * 60)
    print("Choose a demo:")
    print("1. App & Game selectors")
    print("2. Custom modes")
    print("3. Multiple windows")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        demo_app_and_game()
    elif choice == '2':
        demo_custom_modes()
    elif choice == '3':
        demo_multiple_windows()
    else:
        print("Running default demo (App & Game)...")
        demo_app_and_game()
