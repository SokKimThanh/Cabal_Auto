"""
Quick Test: Game Window Mode Selector

Simple test to verify component works correctly.

Run: python tests/manual/test_game_window_mode_selector.py
"""
import sys
import tkinter as tk
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from ui.components.game_window_mode_selector import create_game_window_mode_selector


def main():
    """Quick test of game window mode selector."""
    root = tk.Tk()
    root.title("Test: Game Window Mode Selector")
    root.geometry("400x200")
    root.configure(bg='#F5F5F5')
    
    # Title
    title = tk.Label(
        root,
        text="Game Window Mode Selector Test",
        font=('Segoe UI', 12, 'bold'),
        bg='#F5F5F5'
    )
    title.pack(pady=20)
    
    # Status display
    status = tk.Label(
        root,
        text="Mode: none",
        font=('Segoe UI', 10),
        bg='#F5F5F5',
        fg='#2196F3'
    )
    status.pack(pady=10)
    
    # Callback
    def on_change(mode: str):
        status.config(text=f"Mode: {mode}")
        print(f"[Test] Mode changed to: {mode}")
    
    # Create selector
    frame = tk.Frame(root, bg='#F5F5F5')
    frame.pack(pady=20)
    
    selector = create_game_window_mode_selector(
        parent=frame,
        config_path="tests/tmp/test_config.json",
        on_mode_change=on_change
    )
    selector.pack()
    
    # Instructions
    info = tk.Label(
        root,
        text="Select a mode and check console output",
        font=('Segoe UI', 8),
        bg='#F5F5F5',
        fg='#666'
    )
    info.pack(pady=10)
    
    print("[Test] Game Window Mode Selector loaded")
    print("[Test] Change mode using dropdown")
    print("[Test] Config will be saved to: tests/tmp/test_config.json")
    
    root.mainloop()


if __name__ == '__main__':
    main()
