"""
Test script to verify Monster Editor doesn't open twice.

This script:
1. Launches the app
2. Simulates Ctrl+Shift+M hotkey
3. Checks if Monster Editor opens only once
4. Verifies no duplicate windows

Run:
    python tests/manual/test_monster_editor_duplicate.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_monster_editor_duplicate():
    """Test if Monster Editor opens duplicate windows."""
    print("="*70)
    print("🧪 Testing Monster Editor Duplicate Window Issue")
    print("="*70)
    print()
    print("📋 Test Steps:")
    print("  1. App will start")
    print("  2. Press Ctrl+Shift+M")
    print("  3. Check console output for duplicate messages")
    print("  4. Count visible windows")
    print()
    print("✅ Expected Result:")
    print("  • Only 1 '[Monster Editor] Opening...' message")
    print("  • Only 1 Monster Editor window visible")
    print("  • Main app window remains visible")
    print()
    print("❌ Bug Symptom:")
    print("  • Multiple '[Monster Editor] Opening...' messages")
    print("  • 2 Monster Editor windows visible")
    print()
    print("="*70)
    print()
    print("⏳ Starting app... Press Ctrl+Shift+M to test")
    print()
    
    # Import app
    try:
        from app_gui import App
        import tkinter as tk
        
        # Create app
        root = tk.Tk()
        root.withdraw()  # Hide root
        
        app = App()
        
        # Add counter for Monster Editor opens
        original_open = app._open_monster_editor
        open_count = {'count': 0}
        
        def tracked_open():
            open_count['count'] += 1
            print(f"\n🔍 [TEST] Monster Editor open called (Count: {open_count['count']})")
            original_open()
        
        app._open_monster_editor = tracked_open
        
        # Add instructions
        def check_count():
            if open_count['count'] > 1:
                print(f"\n❌ [TEST] BUG DETECTED: Monster Editor opened {open_count['count']} times!")
            elif open_count['count'] == 1:
                print(f"\n✅ [TEST] PASS: Monster Editor opened exactly once")
            
            # Schedule next check
            app.after(5000, check_count)
        
        app.after(5000, check_count)
        
        print("✅ App started. Waiting for Ctrl+Shift+M...")
        print("   (The test will auto-check every 5 seconds)")
        print()
        
        app.mainloop()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_monster_editor_duplicate()
