#!/usr/bin/env python3
"""Test window enumeration to debug combobox list issue."""

import logging
from lib.system.window_manager import WindowManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_window_list():
    print("\n" + "="*60)
    print("TEST: Window Enumeration")
    print("="*60)
    
    wm = WindowManager()
    
    # 1. Get ALL visible windows
    print("\n[1] All visible windows:")
    all_windows = wm.list_windows(visible_only=True)
    print(f"  Total: {len(all_windows)}")
    for info in all_windows[:10]:
        print(f"    - HWND:{info.hwnd:8} PID:{info.pid:6} | "
              f"'{info.title}' "
              f"(proc: {info.process_name})")
    
    # 2. Filter to Cabal windows
    print("\n[2] Cabal windows only:")
    cabal_windows = wm.list_windows(title_contains=None, visible_only=True)
    allowed = ["cabal.exe", "cabalmain.exe"]
    cabal_filtered = [w for w in cabal_windows 
                      if w.process_name.lower() in allowed]
    print(f"  Total: {len(cabal_filtered)}")
    for info in cabal_filtered:
        print(f"    - HWND:{info.hwnd:8} PID:{info.pid:6} | "
              f"'{info.title}' "
              f"(proc: {info.process_name})")
    
    # 3. Simulate app_window_controller._list_windows()
    print("\n[3] Simulating AppWindowController._list_windows():")
    from ui.controllers.app_window_controller import AppWindowController
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Cabal Auto Hunt")
    
    controller = AppWindowController(root)
    result = controller._list_windows()
    
    print(f"  Returned: {len(result)} items")
    for item in result:
        print(f"    - HWND:{item['hwnd']:8} PID:{item['pid']:6} | "
              f"'{item['title']}'")
    
    # 4. Check what combobox would receive
    print("\n[4] Combobox values would be:")
    values = [item['title'] for item in result]
    print(f"  {values}")
    
    root.destroy()
    print("\n" + "="*60)

if __name__ == "__main__":
    test_window_list()
