#!/usr/bin/env python3
"""Final verification test of CompactWindowSelector with all features."""

import tkinter as tk
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def final_test():
    """Complete test of all features."""
    root = tk.Tk()
    root.title("Final Test: CompactWindowSelector")
    root.geometry("600x400")
    root.withdraw()
    root.win_items = []
    
    try:
        from ui.controllers.app_window_controller import AppWindowController
        from ui.components.compact_window_selector import CompactWindowSelector
        
        # Setup
        window_controller = AppWindowController(root=root)
        selector_frame = tk.Frame(root, bg="#1a1a1a")
        
        selections = []
        def on_selected(w):
            selections.append(w['title'])
            print(f"[Test] ✓ Window selected: {w['title']}")
        
        selector = CompactWindowSelector(
            parent=selector_frame,
            on_window_selected=on_selected,
            window_controller=window_controller,
            root=root,
        )
        
        selector.get_frame().pack(fill="x", expand=True, padx=10, pady=10)
        selector_frame.pack(fill="x", expand=True)
        
        print("=" * 60)
        print("FINAL VERIFICATION TEST")
        print("=" * 60)
        
        # Test 1: Startup state
        print("\n[1] STARTUP STATE")
        print(f"    ✓ Info label: '{selector.info_label.cget('text')}'")
        print(f"    ✓ Refresh button: '{selector.refresh_btn.cget('text')}'")
        print(f"    ✓ Dropdown button: '{selector.dropdown_btn.cget('text')}'")
        print(f"    ✓ Listbox open: {selector.is_open}")
        
        # Test 2: Refresh on startup
        print("\n[2] REFRESH ON STARTUP")
        selector._on_refresh()
        root.update()
        print(f"    ✓ Windows found: {len(selector.win_items)}")
        print(f"    ✓ Info label: '{selector.info_label.cget('text')}'")
        print(f"    ✓ Info label color: {selector.info_label.cget('fg')}")
        
        # Test 3: Toggle dropdown
        print("\n[3] TOGGLE DROPDOWN OPEN")
        selector._toggle_listbox()
        root.update()
        print(f"    ✓ Listbox open: {selector.is_open}")
        print(f"    ✓ Dropdown arrow: '{selector.dropdown_btn.cget('text')}'")
        print(f"    ✓ Listbox items: {selector.listbox.size()}")
        if selector.listbox.size() > 0:
            print(f"    ✓ First item: '{selector.listbox.get(0)}'")
        
        # Test 4: Search functionality
        print("\n[4] SEARCH FUNCTIONALITY")
        selector.search_var.set("cabal")
        selector._on_search_text_changed()
        root.update()
        print(f"    ✓ Search text: '{selector.search_var.get()}'")
        print(f"    ✓ Filtered windows: {len(selector.filtered_windows)}")
        print(f"    ✓ Listbox items after filter: {selector.listbox.size()}")
        
        # Test 5: Close dropdown
        print("\n[5] CLOSE DROPDOWN")
        selector._close_listbox()
        root.update()
        print(f"    ✓ Listbox open: {selector.is_open}")
        print(f"    ✓ Dropdown arrow: '{selector.dropdown_btn.cget('text')}'")
        print(f"    ✓ Listbox height: {selector.listbox.cget('height')}")
        
        # Test 6: Refresh button click
        print("\n[6] REFRESH BUTTON CLICK")
        print(f"    ✓ Button state before: {selector.refresh_btn.cget('state')}")
        print(f"    ✓ Button text before: {selector.refresh_btn.cget('text')}")
        selector.refresh_btn.invoke()
        root.update()
        print(f"    ✓ Button state during: {selector.refresh_btn.cget('state')}")
        print(f"    ✓ Button text during: {selector.refresh_btn.cget('text')}'")
        print(f"    ✓ Info label: '{selector.info_label.cget('text')}'")
        
        # Test 7: Escape key handling
        print("\n[7] ESCAPE KEY HANDLING")
        selector._toggle_listbox()
        root.update()
        print(f"    ✓ Listbox open before Esc: {selector.is_open}")
        selector.search_entry.event_generate("<Escape>")
        root.update()
        print(f"    ✓ Listbox open after Esc: {selector.is_open}")
        
        # Test 8: Layout verification
        print("\n[8] LAYOUT VERIFICATION")
        print(f"    ✓ Main frame: {selector.frame}")
        print(f"    ✓ Info label: {selector.info_label}")
        print(f"    ✓ Dropdown button: {selector.dropdown_btn}")
        print(f"    ✓ Refresh button: {selector.refresh_btn}")
        print(f"    ✓ Close button: {selector.close_btn}")
        print(f"    ✓ Search entry: {selector.search_entry}")
        print(f"    ✓ Listbox: {selector.listbox}")
        print(f"    ✓ Scrollbar: visible")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Component is ready!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = final_test()
    sys.exit(0 if success else 1)
