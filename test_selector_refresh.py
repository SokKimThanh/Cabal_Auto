#!/usr/bin/env python3
"""Direct test of CompactWindowSelector._on_refresh"""

import tkinter as tk
import sys

# Setup app context
from lib.features.hunt.hunt_config import load_hunt_config

# Try to load i18n
try:
    from lib.i18n import i18n_set_lang
    hunt_cfg = load_hunt_config()
    lang = str(hunt_cfg.get("language", "vi"))
    i18n_set_lang(lang)
except Exception as e:
    print(f"[Test] Warning: i18n setup failed: {e}")
    pass

# Minimal root window
root = tk.Tk()
root.title("Test App")
root.geometry("800x400")
root.win_items = []
root.win_items_map = {}

# Create window controller
from ui.controllers.app_window_controller import AppWindowController
window_controller = AppWindowController(root)

# Create compact selector
from ui.components.compact_window_selector import CompactWindowSelector

# Create action bar frame
action_bar = tk.Frame(root, bg="#1a1a1a", height=80)
action_bar.pack(fill="x")

print("[Test] Creating CompactWindowSelector...")
selector = CompactWindowSelector(
    parent=action_bar,
    on_window_selected=lambda w: print(f"[Test] Window selected: {w}"),
    window_controller=window_controller,
    root=root,
)

print("[Test] Calling _on_refresh()...")
selector._on_refresh()
print("[Test] _on_refresh() complete")

# Show info label
frame = selector.get_frame()
frame.pack(fill="x", padx=10, pady=5)

# Update display
root.update()

# Print results
print(f"\n[Test] Results:")
print(f"  Found {len(selector.win_items)} windows in selector.win_items")
print(f"  Found {len(root.win_items)} windows in root.win_items")
info_text = selector.info_label.cget('text')
# Remove unicode checkmark for compatibility
info_text = info_text.replace('\u2713', '[OK]')
print(f"  Info label: {info_text}")

# List windows
for i, w in enumerate(selector.win_items):
    print(f"    [{i}] {w['title']} [PID:{w['pid']}]")

print("\n[Test] Done! Keep window open for 3 seconds...")
root.after(3000, root.quit)
root.mainloop()
