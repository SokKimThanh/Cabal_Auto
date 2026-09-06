#!/usr/bin/env python3
"""Detailed test of CompactWindowSelector UI behavior (manual script; not a pytest test)."""

import sys

if "pytest" in sys.modules:
    import pytest

    pytest.skip("Manual script; skip during pytest collection", allow_module_level=True)

import tkinter as tk
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_selector_ui():
    """Test the window selector UI."""
    root = tk.Tk()
    root.title("Test: CompactWindowSelector")
    root.geometry("600x400")
    root.withdraw()  # Hide for testing
    
    # Mock hunt config
    root.win_items = []
    
    try:
        # Setup mock i18n
        import lib.i18n
        lib.i18n.i18n_set_lang = lambda x: None
        lib.i18n.i18n_get = lambda x, default="": default
    except:
        pass
    
    try:
        from ui.controllers.app_window_controller import AppWindowController
        from ui.components.compact_window_selector import CompactWindowSelector
        
        print("[Test] Creating AppWindowController...")
        window_controller = AppWindowController(root=root)
        
        print("[Test] Creating selector frame...")
        selector_frame = tk.Frame(root, bg="#1a1a1a")
        
        def on_window_selected(win_dict):
            print(f"[Test] Window selected: {win_dict.get('title', 'Unknown')}")
        
        print("[Test] Creating CompactWindowSelector...")
        selector = CompactWindowSelector(
            parent=selector_frame,
            on_window_selected=on_window_selected,
            window_controller=window_controller,
            root=root,
        )
        
        # Pack into test frame
        selector.get_frame().pack(fill="x", expand=True, padx=10, pady=10)
        selector_frame.pack(fill="x", expand=True)
        
        print("[Test] Component created successfully")
        print(f"  - Frame: {selector.frame}")
        print(f"  - Info label: {selector.info_label}")
        print(f"  - Search entry: {selector.search_entry}")
        print(f"  - Refresh button: {selector.refresh_btn}")
        print(f"  - Close button: {selector.close_btn}")
        print(f"  - Listbox: {selector.listbox}")
        
        # Test refresh
        print("[Test] Calling _on_refresh()...")
        selector._on_refresh()
        root.update()  # Process one event
        
        print(f"[Test] After refresh:")
        print(f"  - win_items count: {len(selector.win_items)}")
        print(f"  - Info label text: '{selector.info_label.cget('text')}'")
        print(f"  - Info label color: '{selector.info_label.cget('fg')}'")
        
        # Test toggle
        print("[Test] Toggling listbox open...")
        selector._toggle_listbox()
        root.update()
        print(f"  - is_open: {selector.is_open}")
        print(f"  - listbox height: {selector.listbox.cget('height')}")
        print(f"  - listbox count: {selector.listbox.size()}")
        
        # List items
        if selector.listbox.size() > 0:
            print(f"  - Items in listbox:")
            for i in range(selector.listbox.size()):
                print(f"      [{i}] {selector.listbox.get(i)}")
        
        # Test search
        print("[Test] Testing search (type 'cabal')...")
        selector.search_var.set("cabal")
        selector._on_search_text_changed()
        root.update()
        print(f"  - Filtered count: {len(selector.filtered_windows)}")
        print(f"  - Listbox count after filter: {selector.listbox.size()}")
        
        # Test close
        print("[Test] Closing listbox...")
        selector._close_listbox()
        root.update()
        print(f"  - is_open: {selector.is_open}")
        print(f"  - listbox height: {selector.listbox.cget('height')}")
        
        print("\n[Test] ALL TESTS PASSED ✓")
        return True
        
    except Exception as e:
        import traceback
        print(f"[Test] ERROR: {e}")
        traceback.print_exc()
        return False
    finally:
        root.after(1000, root.destroy)
        root.mainloop()

if __name__ == "__main__":
    success = test_selector_ui()
    sys.exit(0 if success else 1)
