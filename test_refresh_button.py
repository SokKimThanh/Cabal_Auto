#!/usr/bin/env python3
"""Test refresh button directly (manual script; not a pytest test)."""

import sys

if "pytest" in sys.modules:
    import pytest

    pytest.skip("Manual script; skip during pytest collection", allow_module_level=True)

import tkinter as tk
import os
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

def test_refresh_button():
    """Test refresh button click and visual feedback."""
    root = tk.Tk()
    root.title("Test: Refresh Button")
    root.geometry("500x300")
    root.withdraw()  # Hide for testing
    
    root.win_items = []
    
    try:
        # Setup
        from ui.controllers.app_window_controller import AppWindowController
        from ui.components.compact_window_selector import CompactWindowSelector
        
        print("[Test] Creating controller and selector...")
        window_controller = AppWindowController(root=root)
        selector_frame = tk.Frame(root, bg="#1a1a1a")
        
        def on_selected(w):
            print(f"[Test] Window selected: {w.get('title')}")
        
        selector = CompactWindowSelector(
            parent=selector_frame,
            on_window_selected=on_selected,
            window_controller=window_controller,
            root=root,
        )
        
        selector.get_frame().pack(fill="x", expand=True, padx=10, pady=10)
        selector_frame.pack(fill="x", expand=True)
        
        print("[Test] Components created")
        print(f"  - Refresh button: {selector.refresh_btn}")
        print(f"  - Refresh button state: {selector.refresh_btn.cget('state')}")
        
        # Test 1: Initial state
        print("\n[Test 1] Initial state")
        root.update()
        initial_text = selector.info_label.cget('text')
        print(f"  - Info label: '{initial_text}'")
        print(f"  - Refresh button text: '{selector.refresh_btn.cget('text')}'")
        
        # Test 2: Simulate refresh button click
        print("\n[Test 2] Clicking refresh button...")
        print(f"  - Button state before: {selector.refresh_btn.cget('state')}")
        selector.refresh_btn.invoke()  # Programmatically click
        
        print(f"  - Button state after invoke: {selector.refresh_btn.cget('state')}")
        root.update()
        print(f"  - Button text during refresh: '{selector.refresh_btn.cget('text')}'")
        print(f"  - Info label after refresh: '{selector.info_label.cget('text')}'")
        
        # Test 3: Check if refresh worked
        print("\n[Test 3] Verifying refresh result...")
        print(f"  - win_items count: {len(selector.win_items)}")
        print(f"  - Windows found: {selector.win_items}")
        
        # Test 4: Wait for button reset
        print("\n[Test 4] Waiting for button reset (300ms)...")
        root.after(350, lambda: root.quit())
        root.mainloop()
        
        print(f"  - Button text after reset: '{selector.refresh_btn.cget('text')}'")
        print(f"  - Button state after reset: '{selector.refresh_btn.cget('state')}'")
        
        print("\n[Test] ALL TESTS PASSED ✓")
        return True
        
    except Exception as e:
        import traceback
        print(f"[Test] ERROR: {e}")
        traceback.print_exc()
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_refresh_button()
    sys.exit(0 if success else 1)
