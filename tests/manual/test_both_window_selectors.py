"""
Quick Test: App & Game Window Selectors

Test both selectors working together.

Run: python tests/manual/test_both_window_selectors.py
"""
import sys
import tkinter as tk
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ui.components.window_position_selector import (
    create_app_window_selector,
    create_game_window_selector
)


def main():
    """Test app and game window selectors."""
    root = tk.Tk()
    root.title("Test: App & Game Window Selectors")
    root.geometry("500x300")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Window Position Selectors Test",
        font=('Segoe UI', 12, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Status
    status_frame = tk.Frame(root, bg='#F5F5F5')
    status_frame.pack(pady=10)
    
    app_status = tk.Label(
        status_frame,
        text="App: normal",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#2196F3',
        width=25
    )
    app_status.pack()
    
    game_status = tk.Label(
        status_frame,
        text="Game: none",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#4CAF50',
        width=25
    )
    game_status.pack()
    
    # Callbacks
    def on_app_change(mode: str):
        app_status.config(text=f"App: {mode}")
        print(f"[App] Mode: {mode}")
        
        # Apply to window
        if mode == 'topmost':
            root.attributes('-topmost', True)
        elif mode == 'normal':
            root.attributes('-topmost', False)
        elif mode == 'minimized':
            root.iconify()
    
    def on_game_change(mode: str):
        game_status.config(text=f"Game: {mode}")
        print(f"[Game] Mode: {mode}")
    
    # Selectors
    selector_frame = tk.Frame(root, bg='#F5F5F5')
    selector_frame.pack(pady=20)
    
    # App selector
    app_sel = create_app_window_selector(
        parent=selector_frame,
        config_path="tests/tmp/test_app_config.json",
        on_mode_change=on_app_change
    )
    app_sel.pack(pady=5)
    
    # Game selector
    game_sel = create_game_window_selector(
        parent=selector_frame,
        config_path="tests/tmp/test_game_config.json",
        on_mode_change=on_game_change
    )
    game_sel.pack(pady=5)
    
    # Info
    info = tk.Label(
        root,
        text="Change modes and see the effects\n"
             "App modes affect this window\n"
             "Game modes are logged to console",
        font=('Segoe UI', 8),
        bg='#F5F5F5',
        fg='#666',
        justify='center'
    )
    info.pack(pady=20)
    
    print("[Test] App & Game Window Selectors loaded")
    print("[Test] Try changing both modes")
    
    root.mainloop()


if __name__ == '__main__':
    main()
