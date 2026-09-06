#!/usr/bin/env python3
"""Debug test: Check if refresh button click event is firing."""

import tkinter as tk
import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s - %(message)s'
)

def main():
    root = tk.Tk()
    root.title("Refresh Button Debug Test")
    root.geometry("600x400")
    root.win_items = []
    
    # Setup
    from ui.controllers.app_window_controller import AppWindowController
    from ui.components.compact_window_selector import CompactWindowSelector
    
    print("\n" + "="*60)
    print("TEST: Refresh Button Event Firing")
    print("="*60)
    print("\nInstructions:")
    print("1. A window selector UI will appear")
    print("2. CLICK THE REFRESH BUTTON (🔄)")
    print("3. Check if you see: >>> [REFRESH BUTTON CLICKED] <<<")
    print("4. If you don't see it in console, the command is NOT firing")
    print("="*60 + "\n")
    
    # Create main frame
    main_frame = tk.Frame(root, bg="#1a1a1a")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Status label
    status_label = tk.Label(
        main_frame,
        text="Click the REFRESH button (🔄) and check console output",
        fg="#4ade80",
        bg="#1a1a1a",
        font=("Arial", 10, "bold")
    )
    status_label.pack(pady=10)
    
    # Window controller
    window_controller = AppWindowController(root=root)
    
    # Callback
    def on_window_selected(w):
        print(f"[on_window_selected] Selected: {w.get('title')}")
    
    # Create selector
    selector = CompactWindowSelector(
        parent=main_frame,
        on_window_selected=on_window_selected,
        window_controller=window_controller,
        root=root,
    )
    
    selector.get_frame().pack(fill="x", expand=False, padx=5, pady=5)
    
    # Info panel
    info_frame = tk.Frame(main_frame, bg="#111111", relief="sunken", bd=1)
    info_frame.pack(fill="both", expand=True, pady=(10, 0), padx=5)
    
    info_text = tk.Text(
        info_frame,
        bg="#111111",
        fg="#d1d5db",
        font=("Courier New", 9),
        height=10
    )
    info_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Redirect print to both console and text widget
    original_print = print
    def custom_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        original_print(text, **kwargs)
        info_text.insert(tk.END, text + "\n")
        info_text.see(tk.END)
        root.update()
    
    import builtins
    builtins.print = custom_print
    
    print("[READY] Click the REFRESH button...")
    
    root.mainloop()

if __name__ == "__main__":
    main()
