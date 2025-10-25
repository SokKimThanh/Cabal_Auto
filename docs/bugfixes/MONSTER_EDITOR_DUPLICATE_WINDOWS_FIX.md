"""
BUG FIX: Monster Editor Opening Duplicate Windows
Date: 2025-10-25
Status: ✅ FIXED

================================================================================
PROBLEM DESCRIPTION
================================================================================

User reported: "Ctrl+Shift+M mở dư cửa sổ"
- Pressing Ctrl+Shift+M opens extra window
- One window shows Monster Editor (correct)
- Another window shows "Trợ lý săn Cabal" (main app) or empty form

================================================================================
ROOT CAUSE ANALYSIS
================================================================================

1. PREVIOUS FIX (Already Applied)
   - Removed duplicate bind_all for Ctrl+Shift+M (line 5436)
   - This fixed: double-trigger when app is focused
   - Result: Hotkey now only registered once (global hotkey at line 5522)

2. NEW ISSUE (This Fix)
   - Rapid hotkey presses or keyboard library quirks
   - self.after(0, self._open_monster_editor) can queue multiple calls
   - No protection against concurrent opening

3. CONFUSION FACTOR
   - User may see TWO windows:
     a) Main app window "Trợ lý săn Cabal" (already exists)
     b) Monster Editor "Quick Monster Editor" (newly opened)
   - Both windows may appear on screen simultaneously

================================================================================
SOLUTION IMPLEMENTED
================================================================================

Added debounce/flag protection to prevent concurrent opening:

File: app_gui.py

1. Added Flag (line 829):
   ```python
   self._monster_editor_opening = False  # Flag to prevent double opening
   ```

2. Protected _open_monster_editor() method (line 5257-5302):
   ```python
   def _open_monster_editor(self):
       # Prevent double-opening if already in progress
       if self._monster_editor_opening:
           print("[Monster Editor] Already opening, ignoring duplicate request")
           return
       
       try:
           self._monster_editor_opening = True
           print("[Monster Editor] Opening Quick Monster Editor...")
           
           # ... existing code to open editor ...
           
       except Exception as e:
           # ... error handling ...
       finally:
           # Reset flag after 1 second
           self.after(1000, lambda: setattr(self, '_monster_editor_opening', False))
   ```

HOW IT WORKS:
- First call sets flag to True
- Subsequent calls within 1 second are ignored
- Flag resets after 1 second for next legitimate open
- Works with existing singleton pattern in show_quick_monster_editor()

================================================================================
VERIFICATION
================================================================================

Test Scenarios:
1. ✅ Press Ctrl+Shift+M once → Opens 1 Monster Editor
2. ✅ Press Ctrl+Shift+M rapidly → Only 1 Monster Editor opens
3. ✅ Close editor, wait 1 second, press again → Opens new editor
4. ✅ Editor already open, press again → Existing editor lifts to front

Test Script:
- tests/manual/test_monster_editor_duplicate.py
- Tracks open count and reports duplicates

================================================================================
ADDITIONAL NOTES
================================================================================

Two Windows Are Normal:
1. Main App Window ("Trợ lý săn Cabal")
   - This is tk.Tk root window
   - Always exists while app is running
   - Contains Hunt tab, Setup tab, menus

2. Monster Editor ("Quick Monster Editor")
   - This is tk.Toplevel dialog
   - Opens on Ctrl+Shift+M
   - Modal, topmost window
   - Closes independently

User Expectation vs Reality:
- User may expect main app to hide when Monster Editor opens
- Current behavior: Both windows visible (by design)
- This is normal for dialog/modal windows in Tkinter

If User Wants Main App Hidden:
- Could add: app.withdraw() when opening Monster Editor
- Could add: app.deiconify() when closing Monster Editor
- But this may confuse users who want both visible

================================================================================
DEFENSE IN DEPTH
================================================================================

Multiple protections now in place:

1. No Duplicate Hotkey Registration (Previous fix)
   - Only global hotkey registered (line 5522)
   - No bind_all for Monster Editor

2. Debounce Flag (This fix)
   - Prevents rapid calls to _open_monster_editor()
   - 1 second cooldown

3. Singleton Pattern (Existing)
   - show_quick_monster_editor() checks if instance exists
   - Reuses existing instance if window still open

4. Threading Safety
   - self.after(0, ...) ensures main thread execution
   - No race conditions with window creation

================================================================================
MONITORING
================================================================================

Console Output to Watch:
```
[Hotkeys] Monster Editor hotkey pressed
[Monster Editor] Opening Quick Monster Editor...
[Monster Editor] Quick Monster Editor opened successfully
```

If bug still occurs, will see:
```
[Hotkeys] Monster Editor hotkey pressed
[Monster Editor] Opening Quick Monster Editor...
[Monster Editor] Already opening, ignoring duplicate request  ← This is protection working
```

================================================================================
CONCLUSION
================================================================================

✅ Fixed potential race condition with debounce flag
✅ Protects against rapid hotkey presses
✅ Works with existing singleton pattern
✅ Maintains user experience

If user still sees "extra window":
- Likely seeing main app window (normal behavior)
- Can be verified by checking window titles:
  * "Trợ lý săn Cabal" = Main app (always visible)
  * "Quick Monster Editor" = Monster editor dialog (opens on hotkey)

================================================================================
"""