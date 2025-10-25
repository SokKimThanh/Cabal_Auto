"""
Simple visual test for empty window bug.

BUG HISTORY & FIXES:
====================
1. ✅ Removed Ctrl+Shift+M hotkey code from app_gui.py (~50+ lines, 7 locations)
2. ✅ Removed duplicate `import tkinter as tk` from __init__ - bug persisted
3. ✅ Systematically tested imports (DataSyncManager, NotificationWidget, etc.) - none were cause
4. ✅ BREAKTHROUGH: Found real culprit - `tk.StringVar()` without `master` parameter
5. ✅ Fixed 5 tk variable declarations to include `master=self`:
   - Line 343: game_window_mode_var
   - Line 1565-1567: col_image_visible, col_threshold_visible, col_path_visible  
   - Line 1607: show_window_controls_var
6. ✅ Removed window position controls (checkbox + components) - ~150 lines
7. ✅ Fixed MRO conflict: Created proper fallback ActionNotificationMixin class
8. ✅ Fixed StringVar initialization: Moved after _load_ui_settings(), removed master=self
9. ✅ Fixed fallback mixin: Accept debug_mode parameter properly for MRO chain

ROOT CAUSE:
-----------
Creating tk.StringVar() without master parameter causes Tkinter to auto-create 
a hidden root window. This manifested as 2 windows appearing in taskbar instead of 1.

FINAL SOLUTION:
---------------
- Remove master=self from StringVar (line 361) since it's called before super().__init__()
- Fallback ActionNotificationMixin must properly handle MRO chain
- All tk variables in UI creation use master=self (after super().__init__() completes)

TEST RESULT:
------------
✅ Bug FIXED - Only 1 window appears (Monster Editor, no empty "tk" window)
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from ui.windows.quick_monster_editor import show_quick_monster_editor

print("\n" + "="*70)
print("VISUAL TEST: Check Taskbar for Extra Windows")
print("="*70)
print("\nInstructions:")
print("1. Note current number of windows in taskbar")
print("2. Click 'Open Editor' button")
print("3. Check taskbar again")
print("4. Expected: +1 window (Monster Editor)")
print("5. Bug present: +2 windows (Editor + empty 'tk' window)")
print("="*70 + "\n")

# Create main window
app = tk.Tk()
app.title("Main App - Visual Test")
app.geometry("500x300")

label = tk.Label(
    app,
    text="Visual Test for Empty Window Bug",
    font=("Arial", 16, "bold"),
    pady=30
)
label.pack()

info = tk.Label(
    app,
    text="Look at your taskbar BEFORE clicking the button.\n"
         "Count the windows.\n\n"
         "Then click the button and count again.\n\n"
         "Expected: +1 window (Monster Editor only)\n"
         "Bug: +2 windows (Editor + empty window)",
    font=("Arial", 11),
    justify="left",
    fg="#333"
)
info.pack(pady=20)

def open_editor():
    print("\n[TEST] Opening Monster Editor...")
    print("[TEST] Check your taskbar now!")
    try:
        editor = show_quick_monster_editor(
            parent=app,
            monster_id=None,
            on_save=lambda mid, mdata: print(f"Saved: {mid}")
        )
        print("[TEST] Editor opened successfully")
    except Exception as e:
        print(f"[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()

btn = tk.Button(
    app,
    text="🧪 Open Monster Editor",
    command=open_editor,
    font=("Arial", 14, "bold"),
    bg="#2196F3",
    fg="white",
    padx=30,
    pady=15
)
btn.pack(pady=20)

app.mainloop()
