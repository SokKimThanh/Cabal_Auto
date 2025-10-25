# Critical Fix: Python Import Snapshot Issue

## 🐛 The Hidden Bug

### What User Saw
```
[show_quick_monster_editor] Called (PID: 8076)
  Singleton exists: False    ← Always False!
[show_quick_monster_editor] ✓ Creating NEW instance
```

Every time `Ctrl+Shift+M` pressed → New window created (duplicate)

---

## 🔍 Root Cause: Import Creates Snapshot

### The Problem
```python
# app_gui.py (WRONG):
from ui.windows.quick_monster_editor import _quick_editor_instance

# At import time:
# _quick_editor_instance = None (snapshot taken)

def _open_monster_editor(self):
    # Later, when hotkey pressed:
    if _quick_editor_instance is not None:  # ❌ Always None!
        # This branch NEVER executes
```

### What Happened
1. `app_gui.py` imports `_quick_editor_instance` at module load time
2. Value at that moment: `None`
3. Python creates **local copy** of that value
4. Later, `show_quick_monster_editor()` updates global:
   ```python
   # In quick_monster_editor.py:
   _quick_editor_instance = QuickMonsterEditor()  # Updates global
   ```
5. But `app_gui.py` still sees **frozen snapshot** (`None`)
6. Next hotkey press → thinks no instance exists → creates duplicate

---

## ✅ The Fix

### Before (Creates Snapshot)
```python
# ❌ Variable import = snapshot at import time
from ui.windows.quick_monster_editor import _quick_editor_instance

# _quick_editor_instance is now LOCAL variable (frozen at None)
```

### After (References Global)
```python
# ✅ Module import = live reference
import ui.windows.quick_monster_editor as monster_editor_module

# monster_editor_module._quick_editor_instance accesses ACTUAL global
```

### Code Changes
```python
# app_gui.py - _open_monster_editor()

# OLD:
from ui.windows.quick_monster_editor import show_quick_monster_editor, _quick_editor_instance
if _quick_editor_instance is not None:  # ❌ Always False

# NEW:
import ui.windows.quick_monster_editor as monster_editor_module
if monster_editor_module._quick_editor_instance is not None:  # ✅ Sees real value
```

---

## 🧪 Test Results

### Before Fix
```
Press Ctrl+Shift+M → Window #1 created
Press Ctrl+Shift+M → Window #2 created (duplicate!)
Press Ctrl+Shift+M → Window #3 created (duplicate!)
```

### After Fix
```
Press Ctrl+Shift+M → Window #1 created
Press Ctrl+Shift+M → Window #1 brought to front (reused) ✅
Press Ctrl+Shift+M → Window #1 brought to front (reused) ✅
Close window
Press Ctrl+Shift+M → Window #2 created (fresh instance) ✅
```

---

## 📚 Python Import Behavior

### Variable Import (Creates Copy)
```python
# module_a.py
x = 1

# module_b.py
from module_a import x
print(x)  # 1

# module_a.py (updated)
x = 2

# module_b.py
print(x)  # Still 1! (frozen at import time)
```

### Module Import (Live Reference)
```python
# module_a.py
x = 1

# module_b.py
import module_a
print(module_a.x)  # 1

# module_a.py (updated)
module_a.x = 2

# module_b.py
print(module_a.x)  # 2! (sees live value)
```

---

## 💡 Key Takeaways

1. **Never import mutable global variables directly**
   - Use module imports instead
   - Access via `module.variable`

2. **Singleton pattern requires live references**
   - Can't use snapshots
   - Must see real-time state

3. **This applies to ALL singleton windows**
   - Vision Wizard
   - Template Manager
   - Library Manager
   - Any window using global instance variable

---

## 🔄 Related Fixes

All 3 fixes work together:

1. **Clear on close** - Prevents stale references
2. **Robust validation** - Handles edge cases
3. **Module import** (NEW) - Sees actual global state

Without Fix #3, Fixes #1-2 were ineffective because `app_gui.py` couldn't see the updates!

---

## 📝 Verification Steps

1. Launch app
2. Press `Ctrl+Shift+M` → Editor opens
3. Check log: `Singleton exists: False` ✅
4. Press `Ctrl+Shift+M` again
5. Check log: `Singleton exists: True`, `Singleton valid: True` ✅
6. Check log: `Reusing existing instance` ✅
7. Check UI: Only 1 window visible ✅

---

## ✅ Status

**Fixed in Sprint 24**  
**Commit:** Module-level import for singleton access  
**Files Changed:**
- `app_gui.py` - `_open_monster_editor()`
- `docs/bugfixes/BUGFIX_MONSTER_EDITOR_SINGLETON.md` - Updated root cause

**Testing:** Manual verification passed ✅
