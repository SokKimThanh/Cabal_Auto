"""Test to count windows at each step."""

import tkinter as tk
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

print("\n=== Window Creation Trace ===\n")

# Function to count root windows
def count_roots():
    """Count number of Tk root windows."""
    count = 0
    try:
        # Check tk._default_root
        if hasattr(tk, '_default_root') and tk._default_root:
            count += 1
    except:
        pass
    return count

print(f"1. Before creating main app:")
print(f"   Root windows: {count_roots()}")

# Create main app
app = tk.Tk()
app.title("Main App")
app.geometry("400x300")

print(f"\n2. After creating main app:")
print(f"   Root windows: {count_roots()}")

def test_import():
    print(f"\n3. Before importing quick_monster_editor:")
    print(f"   Root windows: {count_roots()}")
    
    from ui.windows.quick_monster_editor import show_quick_monster_editor
    
    print(f"\n4. After importing quick_monster_editor:")
    print(f"   Root windows: {count_roots()}")
    
    print(f"\n5. Before calling show_quick_monster_editor:")
    print(f"   Root windows: {count_roots()}")
    
    editor = show_quick_monster_editor(
        parent=app,
        monster_id=None,
        on_save=lambda mid, mdata: None
    )
    
    print(f"\n6. After calling show_quick_monster_editor:")
    print(f"   Root windows: {count_roots()}")
    print(f"   Editor instance: {editor}")
    
    # Check for multiple Tk root instances
    print(f"\n7. Checking Tk internals:")
    if hasattr(tk, '_default_root'):
        print(f"   tk._default_root: {tk._default_root}")
    if hasattr(tk, '_support_default_root'):
        print(f"   tk._support_default_root: {tk._support_default_root}")
    
    print(f"\n8. Analysis:")
    print(f"   Expected root count: 1 (main app only)")
    print(f"   Actual root count: {count_roots()}")
    if count_roots() > 1:
        print(f"   ❌ BUG: Extra root window detected!")
    else:
        print(f"   ✅ OK: No extra root window")

btn = tk.Button(
    app,
    text="Run Test",
    command=test_import,
    font=("Arial", 14, "bold"),
    bg="#2196F3",
    fg="white",
    padx=30,
    pady=15
)
btn.pack(expand=True)

print(f"\n9. Ready for testing - click button")
print(f"   Watch console for root window count at each step")

app.mainloop()
