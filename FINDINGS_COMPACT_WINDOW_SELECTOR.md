# Findings: CompactWindowSelector Refresh Button Debug Report

**Date:** 2026-09-07  
**Component:** `ui/components/compact_window_selector.py`  
**Status:** RESOLVED ✅

---

## Executive Summary

The refresh button in `CompactWindowSelector` was not displaying windows because of **three cascading bugs** in the window detection pipeline. All issues have been fixed and verified.

**Root Causes:**
1. ❌ ctypes pointer not being dereferenced correctly
2. ❌ Missing dependency (`psutil`) causing process name detection to fail
3. ❌ Verbose logging masking the actual failures

---

## Issue #1: ctypes Pointer Dereference Error

### Problem
In `lib/system/window_manager.py`, the `EnumWindows` callback received window handles as `ctypes.LP_c_long` pointers, but the code tried to convert them using `int(hwnd)`, resulting in:

```
invalid literal for int() with base 10: b'\xc0\x03\x02\x00\x00\x00\x00\x00'
```

### Root Cause
When `win32gui.GetWindowPlacement(hwnd)` was called with the raw pointer object, pywin32 raised:
```
The object is not a PyHANDLE object
```

### Solution
Convert ctypes pointers to integer using proper dereferencing:

```python
# ❌ WRONG
hwnd_int = int(hwnd)  # Fails on raw bytes

# ✅ CORRECT
hwnd_int = ctypes.cast(hwnd, ctypes.c_void_p).value  # Properly dereferences pointer
```

**File Modified:** `lib/system/window_manager.py` Line 200  
**Method:** `list_windows()` → `callback(hwnd, _)` function

---

## Issue #2: Missing psutil Dependency

### Problem
Process names were being returned as `'PID:5628'` instead of `'cabal.exe'`, causing all windows to be filtered out by the process filter.

**Example Output:**
```
[WindowController] 🔍 Checking window: title='Fix async window enumeration...' | process='PID:20064'
[WindowController]   ❌ Skipped (process 'PID:20064' not in ['cabal.exe', 'cabalmain.exe'])
```

### Root Cause
In `lib/system/window_manager.py` Line 311-318:

```python
try:
    if psutil:
        process = psutil.Process(pid)
        process_name = process.name()  # ← psutil was None (not imported)
    else:
        process_name = f"PID:{pid}"    # ← Fallback being used
except Exception:
    process_name = "Unknown"
```

**Why psutil was None:**
- `requirements.txt` did not list `psutil` as a dependency
- The module imports with graceful fallback, but process name detection silently failed
- No error was raised, just silent degradation

### Solution
1. Added `psutil>=5.9.0; sys_platform == "win32"` to `requirements.txt`
2. Installed the package: `pip install psutil`
3. Process names now correctly detected as `'msedge.exe'`, `'python.exe'`, etc.

**File Modified:** `requirements.txt` Line 13

---

## Issue #3: Verbose Logging Masking Real Issues

### Problem
The codebase had been instrumented with both `print()` and `logger.info()` statements for debugging, resulting in **247+ log lines per refresh** that obscured actual failures:

```
[WindowManager] 🔎 Processing window #1: hwnd=12345
[WindowManager]   is_visible=True, is_minimized=False
[WindowManager]   title='Some Window'
[WindowManager]   ✅ Process=msedge.exe
[WindowManager]   ✅ ADDED TO RESULTS
... repeated 247 times ...
[WindowManager] 📊 SUMMARY: Enumerated=247, Skipped=226, Results=21
```

This made it nearly impossible to see that:
- Windows **were** being found (21 total)
- But **all were being filtered out** (0 results)
- And why each one failed the filter

### Solution
Cleaned up all logging:
- Removed verbose `print()` statements
- Changed detail logs to `logger.debug()` (only shown in DEBUG mode)
- Kept only essential `logger.info()` for key events
- Removed prefix tags like `[Refresh]`, `[UI Update]`, `[Selection]`

**Files Modified:**
- `lib/system/window_manager.py` - Removed 15+ print statements
- `ui/controllers/app_window_controller.py` - Removed 8+ print statements  
- `ui/components/compact_window_selector.py` - Removed 30+ print statements

**Before (verbose):**
```
[UI Update] 📥 Received 5 windows from thread
[UI Update] self.is_open = False, self.listbox = True
[UI Update] 🔓 Auto-opening listbox with 5 windows
[UI Update] pack_propagate(True) done
[UI Update] listbox height set to 6
[UI Update] listbox_frame height set to 150
[UI Update] is_open = True
[UI Update] dropdown_btn text changed to ▲
[Listbox] Updating with search text: ''
[Listbox] Filtered 5 windows from 5 total
[Listbox] Cleared listbox
[Listbox] Inserted 5 items into listbox
```

**After (clean):**
```
Received 5 windows
Auto-opened listbox
```

---

## Issue #4: Listbox Not Auto-Opening

### Problem
Even when windows were successfully fetched, the listbox remained closed (height=0) and was not visible to the user.

### Root Cause
Missing auto-open logic in `_update_ui_with_windows()`. The method saved data but didn't open the UI to display it.

### Solution
Added auto-open when:
1. Windows are found (count > 0)
2. Listbox is not already open (is_open == False)

```python
if count > 0 and not self.is_open:
    self.listbox_frame.pack_propagate(True)
    self.listbox.config(height=6)
    self.listbox_frame.config(height=150)
    self.is_open = True
    self.dropdown_btn.config(text="▲")
```

**File Modified:** `ui/components/compact_window_selector.py` Line 246

---

## Verification & Testing

### Pre-Fix State
- ❌ Refresh button clicked → 0 windows found
- ❌ No windows displayed in listbox
- ❌ Console flooded with verbose logs

### Post-Fix State
- ✅ Refresh button clicked → Finds available windows (e.g., 5 windows)
- ✅ Listbox automatically opens showing available windows
- ✅ Console shows only essential logs
- ✅ User can click window to select it
- ✅ Search filter works correctly

### Test Cases Validated
1. **Refresh with windows available** → Windows appear in listbox ✅
2. **Refresh with no windows** → Shows "✗ 0 windows" ✅
3. **Window selection** → Closes listbox, stores selection ✅
4. **Search filtering** → Filters windows by title ✅
5. **Toggle listbox** → Open/close with dropdown button ✅

---

## Files Changed Summary

| File | Changes | Lines |
|------|---------|-------|
| `lib/system/window_manager.py` | Added hwnd pointer dereferencing | 200 |
| `requirements.txt` | Added psutil dependency | 13 |
| `ui/controllers/app_window_controller.py` | Cleaned logs | 23-50 |
| `ui/components/compact_window_selector.py` | Removed verbose logs, kept logic | 180-400 |

**Total:** 4 files modified, ~80 lines of logging code removed

---

## Lessons Learned

1. **ctypes Callback Pointer Handling**
   - Raw pointers from EnumWindows need `ctypes.cast()` to convert to int
   - Simple `int(pointer)` will fail with byte literal error
   - Always cast to `ctypes.c_void_p` before using `.value`

2. **Graceful Fallback Can Hide Bugs**
   - When a dependency is optional (like psutil), it's easy to not notice it's missing
   - Consider logging a warning when falling back to degraded mode
   - Or make critical dependencies explicit with `raise ImportError` if missing

3. **Logging During Debug Must Be Cleaned Up**
   - Verbose output during debugging helps find issues
   - But leaving it in production masks real problems
   - Always convert debug prints to `logger.debug()` for production
   - Use proper log levels: INFO for events, DEBUG for details, ERROR for failures

4. **UI State Management**
   - Boolean flags like `is_open` are essential for tracking component state
   - Auto-open features improve UX when data is available
   - Always reset UI state properly (buttons, listbox visibility, etc.)

---

## Recommendations for Future Development

1. **Add Pre-flight Checks**
   ```python
   # In __init__ or startup:
   try:
       import psutil
   except ImportError:
       logger.warning("psutil not installed - process detection disabled")
   ```

2. **Use Structured Logging**
   - Replace tags like `[Refresh]` with logger context/names
   - Use `logging.getLogger(__name__)` consistently

3. **Add Unit Tests**
   - Test window enumeration with mocked win32gui
   - Test pointer conversion edge cases
   - Test filter logic with known window lists

4. **Monitor Log Output**
   - Add CI check for "log pollution" (excessive logging)
   - Enforce use of `logger.debug()` for detail logs

---

## Conclusion

The refresh button now works correctly. Users can:
1. Click the Refresh button 🔄
2. Windows are fetched asynchronously
3. Listbox automatically opens showing available windows
4. User can select a window from the list
5. Search filter provides real-time filtering

All fixes maintain backward compatibility and follow the existing architectural patterns (threading, UI updates via `root.after()`).
