"""
Test Singleton Pattern - Verify "Coi app có tồn tại chưa"

Run this after launching app_gui.py to verify singleton logic.

ALSO CHECKS: Extra empty window issue (Tkinter Toplevel without parent)
"""

def test_singleton_check():
    """
    Manual test checklist for singleton pattern.
    
    Expected behavior:
    1. First press → Creates window
    2. Second press (while open) → Brings to front (NO duplicate)
    3. Close window
    4. Third press → Creates new window
    """
    
    print("=" * 70)
    print("TEST: Monster Editor Singleton Pattern")
    print("=" * 70)
    print()
    
    print("Test Steps:")
    print("1. Launch app: python app_gui.py")
    print("2. Press Ctrl+Shift+M")
    print("   Expected: Window opens")
    print("   Check log: 'exists=False, alive=False' → 'Creating NEW instance'")
    print("   ⚠️  ALSO CHECK: Only 1 window appears (NO extra empty window)")
    print()
    
    print("3. Press Ctrl+Shift+M again (window still open)")
    print("   Expected: Window brought to front (NO new window)")
    print("   Check log: 'exists=True, alive=True' → 'bringing to front'")
    print()
    
    print("4. Close the window (X button)")
    print("   Expected: Window closes")
    print("   Check log: 'Singleton instance cleared on close'")
    print()
    
    print("5. Press Ctrl+Shift+M again")
    print("   Expected: New window opens")
    print("   Check log: 'exists=False, alive=False' → 'Creating NEW instance'")
    print()
    
    print("=" * 70)
    print("PASS Criteria:")
    print("  ✅ Only 1 window visible at any time")
    print("  ✅ Step 3 does NOT create duplicate window")
    print("  ✅ Step 5 creates fresh instance after close")
    print("  ✅ NO extra empty windows appear at any step")
    print("=" * 70)
    print()
    
    print("Log Keywords to Look For:")
    print("  - 'Check: exists=False, alive=False' → Should create new")
    print("  - 'Check: exists=True, alive=True' → Should reuse")
    print("  - 'Instance already exists, bringing to front' → Reuse path")
    print("  - 'No valid instance found, creating new' → Create path")
    print("  - 'Singleton instance cleared on close' → Cleanup on close")
    print("  - 'Parent: App' → Correct parent type")
    print("  - 'Parent type: App' → Should match")
    print()


def test_empty_window_issue():
    """Test for extra empty window bug from Tkinter."""
    
    print("=" * 70)
    print("TEST: Extra Empty Window (Tkinter Toplevel Issue)")
    print("=" * 70)
    print()
    
    print("Background:")
    print("  When Toplevel() is created without parent, Tkinter creates")
    print("  a hidden root window automatically → Extra empty window appears")
    print()
    
    print("Diagnostic Steps:")
    print("1. Press Ctrl+Shift+M")
    print("2. Check log for:")
    print("   '[QuickMonsterEditor] __init__ called'")
    print("   '  Parent: App'         ← Should be 'App' (not None or Tk)")
    print("   '  Parent type: App'    ← Should match")
    print()
    
    print("3. Visual check:")
    print("   - Count windows in taskbar")
    print("   - Expected: 2 windows (Main app + Monster Editor)")
    print("   - If 3+: Extra empty window present (BUG)")
    print()
    
    print("4. Check window titles:")
    print("   - Main app: 'Trợ lý săn Cabal'")
    print("   - Monster Editor: 'Sửa Quái Nhanh'")
    print("   - If 'tk' or empty title: Extra window (BUG)")
    print()
    
    print("=" * 70)
    print("PASS Criteria:")
    print("  ✅ Parent type is 'App' (not None)")
    print("  ✅ Only 2 windows visible (Main + Editor)")
    print("  ✅ No 'tk' or empty titled windows")
    print("  ✅ No hidden windows in background")
    print("=" * 70)
    print()


def explain_check_logic():
    """Explain the singleton check logic in detail."""
    
    print("=" * 70)
    print("SINGLETON CHECK LOGIC EXPLANATION")
    print("=" * 70)
    print()
    
    print("Question: 'Lúc mở thêm cái mới thì phải coi app có tồn tại chưa?'")
    print("Answer:   Đúng! Code kiểm tra 3 điều kiện:")
    print()
    
    print("1. instance_exists = instance is not None")
    print("   → Kiểm tra biến global có giá trị không")
    print()
    
    print("2. instance_alive = instance.winfo_exists()")
    print("   → Kiểm tra window có còn sống trong Tkinter không")
    print("   → Returns: 1 (sống) hoặc 0 (đã destroy)")
    print()
    
    print("3. Decision:")
    print("   if exists=True AND alive=True:")
    print("       → Reuse (lift + focus)")
    print("   else:")
    print("       → Create new")
    print()
    
    print("=" * 70)
    print("CODE LOCATION:")
    print("=" * 70)
    print()
    print("File: app_gui.py")
    print("Method: _open_monster_editor()")
    print("Lines: ~5347-5370")
    print()
    print("Key Code:")
    print("```python")
    print("instance = monster_editor_module._quick_editor_instance")
    print("instance_exists = instance is not None")
    print()
    print("if instance_exists and instance:")
    print("    try:")
    print("        instance_alive = bool(instance.winfo_exists())")
    print("    except:")
    print("        instance_alive = False")
    print()
    print("if instance_exists and instance_alive and instance:")
    print("    # REUSE existing window")
    print("    instance.lift()")
    print("    instance.focus_force()")
    print("    return  # Don't create new!")
    print()
    print("# If we reach here: create new window")
    print("show_quick_monster_editor(...)")
    print("```")
    print()


if __name__ == "__main__":
    test_singleton_check()
    print()
    test_empty_window_issue()
    print()
    explain_check_logic()
    
    print("=" * 70)
    print("Ready to test? Run: python app_gui.py")
    print("Then press Ctrl+Shift+M and check:")
    print("  1. Log shows correct parent type")
    print("  2. Only 1 Monster Editor window appears")
    print("  3. No extra empty windows")
    print("=" * 70)
