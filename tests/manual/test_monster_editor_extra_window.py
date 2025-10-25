"""
Test script to check if QuickMonsterEditor creates extra empty window.

This test verifies the fix for Tkinter's "extra empty window" issue
where Toplevel without proper parent creates a hidden root window.

Expected behavior:
- Only 2 windows: Main app + Monster Editor
- No extra "tk" or empty titled windows

Sprint 24 - Validation Test
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

print(f"Project root: {project_root}")
print(f"Working directory: {os.getcwd()}")

from ui.windows.quick_monster_editor import show_quick_monster_editor


def count_windows():
    """Count all Tk/Toplevel windows."""
    import win32gui
    
    windows = []
    
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            # Filter Tk/Tcl windows
            if class_name and ('tk' in class_name.lower() or 'toplevel' in class_name.lower()):
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'class': class_name
                })
    
    try:
        win32gui.EnumWindows(enum_callback, None)
    except:
        pass
    
    return windows


def test_monster_editor_window_count():
    """Test that opening Monster Editor doesn't create extra windows."""
    print("="*70)
    print("TEST: QuickMonsterEditor Extra Window Issue")
    print("="*70)
    
    # Create main app window
    print("\n1. Creating main app window...")
    app = tk.Tk()
    app.title("Test App - Main Window")
    app.geometry("400x300")
    
    # Add test button
    def open_editor():
        print("\n2. Opening Monster Editor...")
        try:
            # Count windows before
            windows_before = count_windows()
            print(f"\n   Windows BEFORE opening editor: {len(windows_before)}")
            for w in windows_before:
                print(f"     - {w['title'] or '<no title>'} ({w['class']})")
            
            # Open Monster Editor
            editor = show_quick_monster_editor(
                parent=app,
                monster_id=None,
                on_save=lambda mid, mdata: print(f"Monster saved: {mid}")
            )
            
            # Count windows after (wait a bit for window to appear)
            app.after(500, lambda: check_window_count(windows_before))
            
        except Exception as e:
            print(f"\n   ❌ ERROR opening editor: {e}")
            import traceback
            traceback.print_exc()
    
    def check_window_count(windows_before):
        """Check window count after opening editor."""
        windows_after = count_windows()
        print(f"\n3. Windows AFTER opening editor: {len(windows_after)}")
        for w in windows_after:
            print(f"     - {w['title'] or '<no title>'} ({w['class']})")
        
        # Analysis
        new_windows = len(windows_after) - len(windows_before)
        print(f"\n4. Analysis:")
        print(f"   - Expected new windows: 1 (Monster Editor only)")
        print(f"   - Actual new windows: {new_windows}")
        
        if new_windows == 1:
            print(f"   ✅ PASS: Only Monster Editor created")
        elif new_windows == 2:
            print(f"   ❌ FAIL: Extra empty window detected!")
            print(f"   🐛 This indicates Toplevel parent issue")
        elif new_windows == 0:
            print(f"   ⚠️  WARNING: No new window detected")
        else:
            print(f"   ❓ UNEXPECTED: {new_windows} new windows")
        
        # Show result dialog
        result_msg = f"Expected: 1 new window\nActual: {new_windows} new windows\n\n"
        if new_windows == 1:
            result_msg += "✅ TEST PASSED"
            messagebox.showinfo("Test Result", result_msg)
        else:
            result_msg += "❌ TEST FAILED"
            messagebox.showerror("Test Result", result_msg)
    
    # UI
    label = tk.Label(
        app,
        text="Test QuickMonsterEditor\nExtra Window Issue",
        font=("Arial", 14, "bold"),
        pady=20
    )
    label.pack()
    
    info_label = tk.Label(
        app,
        text="Click button to open Monster Editor\n"
             "Check if extra empty window appears",
        font=("Arial", 10),
        fg="#666"
    )
    info_label.pack(pady=10)
    
    test_btn = tk.Button(
        app,
        text="🧪 Open Monster Editor",
        command=open_editor,
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=10
    )
    test_btn.pack(pady=20)
    
    instructions = tk.Label(
        app,
        text="Expected: Only 1 new window (Monster Editor)\n"
             "If you see 2 new windows, bug is still present",
        font=("Arial", 9),
        fg="#FF6F00",
        justify="left"
    )
    instructions.pack(pady=10)
    
    print("\n📋 Test Instructions:")
    print("   1. Click 'Open Monster Editor' button")
    print("   2. Check console output for window count")
    print("   3. Verify result in dialog")
    print("   4. Check taskbar for extra windows")
    print("\n   Expected: Only 1 new window (Monster Editor)")
    print("   Bug present: 2 new windows (Monster Editor + empty window)")
    
    app.mainloop()


if __name__ == "__main__":
    # Check if win32gui available for window counting
    try:
        import win32gui
        print("✅ win32gui available - detailed window counting enabled")
    except ImportError:
        print("⚠️  win32gui not available - install pywin32 for detailed testing")
        print("   pip install pywin32")
        
        def count_windows():
            """Fallback - just count Tk toplevels."""
            return []
    
    test_monster_editor_window_count()
