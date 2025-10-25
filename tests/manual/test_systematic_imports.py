"""Systematic test to find which import causes extra window.

Strategy: Comment out imports one by one and test after each.
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

print("\n" + "="*70)
print("SYSTEMATIC IMPORT TEST")
print("="*70)

# Test 1: Import with ALL components
print("\n[TEST 1] Import QuickMonsterEditor with ALL components")
print("Watch taskbar carefully...")

try:
    # Clear any previous imports
    if 'ui.windows.quick_monster_editor' in sys.modules:
        del sys.modules['ui.windows.quick_monster_editor']
    
    from ui.windows.quick_monster_editor import show_quick_monster_editor
    print("✅ Import successful")
    
    # Create test window
    app = tk.Tk()
    app.title("Test App")
    app.geometry("400x300")
    
    label = tk.Label(
        app,
        text="TEST 1: Full Import\n\nClick button and check taskbar",
        font=("Arial", 12),
        pady=30
    )
    label.pack()
    
    def open_editor():
        print("\n[Opening Editor...]")
        print("COUNT WINDOWS IN TASKBAR NOW!")
        try:
            editor = show_quick_monster_editor(
                parent=app,
                monster_id=None,
                on_save=lambda mid, mdata: None
            )
            print("✅ Editor opened")
            
            # Ask user
            app.after(2000, lambda: ask_result())
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def ask_result():
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Test Result",
            "Did you see 2 windows created?\n\n"
            "YES = Bug present (2 windows)\n"
            "NO = Bug fixed (1 window only)"
        )
        if result:
            print("❌ BUG PRESENT - Extra window detected")
            print("\nNext: Test with components commented out")
        else:
            print("✅ BUG FIXED - Only 1 window created")
        
        app.quit()
    
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
    
    info = tk.Label(
        app,
        text="Instructions:\n"
             "1. Note current window count\n"
             "2. Click button\n"
             "3. Count windows again\n"
             "4. Answer dialog",
        font=("Arial", 9),
        fg="#666"
    )
    info.pack()
    
    app.mainloop()
    
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
