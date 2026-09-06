# PROMPT: Refactor Window Detection - Extract Wizard Logic & Remove Setup Wizard (Sprint 26)

## 📋 Context & Objective

**Goal**: Consolidate window detection logic from Setup Wizard into a reusable service, apply it to main UI (refresh button + combobox), then remove the Setup Wizard feature entirely.

**Current State**:
- Setup Wizard (`ui/windows/setup_wizard.py`) has comprehensive window finding logic
- Main UI refresh button + combobox in `app_gui.py` use simpler `WindowManager` approach
- Redundant implementations → maintenance burden
- Setup Wizard is optional feature that can be deprecated

**Target State**:
- Extract window detection into shared service/utility
- Apply to main UI (refresh + combobox)
- Remove Setup Wizard completely
- Remove "Quick Setup" sidebar button
- Cleaner, more maintainable code

## 🎯 Detailed Requirements

### Phase 1: Extract Window Detection Logic

#### 1.1 Create `lib/features/hunt/window_detection_service.py`

New utility service to centralize all window detection logic.

**What to extract**:

From `ui/windows/setup_wizard.py` (lines 1656-1710):
- `_enum_windows()` method - uses WinAPI to enumerate all visible windows
- Window filtering logic - filters by title, process name
- PID/process lookup using psutil

From `ui/controllers/app_window_controller.py` (lines 14-56):
- `_list_windows()` method - builds results with bounds, minimized state
- Process name filtering - only allows "cabal.exe"
- Result sorting - prioritizes Cabal-named windows

**New service structure**:

```python
# lib/features/hunt/window_detection_service.py

class WindowDetectionService:
    """Centralized window detection for Cabal game."""
    
    def __init__(self):
        """Initialize with WindowManager."""
        self.wm = WindowManager()
    
    def find_all_cabal_windows(self, filter_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find all Cabal windows with optional text filtering.
        
        Returns:
            List of dicts with keys: hwnd, pid, title, proc, bounds, is_minimized
        """
        # Implementation: combine logic from both locations
        # 1. Use WinAPI enumeration (from wizard)
        # 2. Filter by cabal.exe process
        # 3. Return sorted results with bounds info
    
    def find_best_cabal_window(self, prefer_current_hwnd: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Auto-detect best Cabal window.
        
        Priority:
        1. Currently selected window (if still valid)
        2. First window with "Cabal" in title
        3. First cabal.exe process window
        
        Returns:
            Window dict or None
        """
        # Implementation
    
    def enumerate_windows_raw(self) -> List[Dict[str, Any]]:
        """Low-level window enumeration using WinAPI."""
        # Direct copy of _enum_windows() from wizard
    
    def filter_windows(self, windows: List[Dict[str, Any]], filter_text: str) -> List[Dict[str, Any]]:
        """Filter windows by title/process name."""
        # Implementation: search logic
    
    def get_window_bounds(self, hwnd: int) -> Optional[Dict[str, int]]:
        """Get window rectangle and state."""
        # Wrap WindowManager.get_window_info()
    
    def restore_window_if_minimized(self, hwnd: int) -> bool:
        """Try to restore minimized window."""
        # From app_window_controller._retry_resolve_bounds()
```

### Phase 2: Update `app_window_controller.py`

**Refactor to use new service**:

1. Import `WindowDetectionService`
2. Replace `_list_windows()` with call to service
3. Simplify `on_hunt_find_windows()` and `on_hunt_refresh_windows()`
4. Remove duplicate logic

**Before**:
```python
def _list_windows(self, title_contains=None):
    wm = WindowManager()
    windows = wm.list_windows(title_contains=title_contains, visible_only=True)
    # ... lots of filtering code
```

**After**:
```python
def on_hunt_find_windows(self):
    service = WindowDetectionService()
    items = service.find_all_cabal_windows()
    self.root.win_items = items
    # ... update combobox
```

### Phase 3: Remove Setup Wizard

#### 3.1 Remove Setup Wizard UI Components

**In `app_gui.py`**:

1. **Remove sidebar button** (around line 705-710):
   ```python
   # REMOVE:
   (
       "sidebar_quick_setup",
       lambda: self.on_setup_wizard(hide_parent=False),
       UI.FONT_SECTION,
       None,
       "🔧"
   ),
   ```

2. **Remove methods** (lines 1358-1362):
   ```python
   # REMOVE:
   def on_setup_wizard(self, hide_parent=True):
       self.window_controller.on_setup_wizard(hide_parent)

   def try_close_setup_wizard(self) -> bool:
       return self.window_controller.try_close_setup_wizard()
   ```

3. **Remove Setup Wizard hotkey management** (lines 1389-1412):
   ```python
   # REMOVE entire _update_setup_wizard_hotkey_state() method
   ```

4. **Remove import** (line 1):
   ```python
   # REMOVE:
   from ui.windows.setup_wizard import show_setup_wizard
   ```

#### 3.2 Remove from `app_window_controller.py`

1. **Remove methods**:
   - `on_setup_wizard()` (if exists)
   - `try_close_setup_wizard()` (if exists)
   - `_auto_detect_and_save_cabal_window()` (deprecated - use service instead)

#### 3.3 Remove Setup Wizard Hotkey Configuration

**In `app_gui.py` hotkey section** (around lines 2536-2576):

```python
# REMOVE:
wizard_key = _hotkey_value("global_hotkey_wizard_var", "setup_wizard_key", "ctrl+alt+n")
wizard_hotkey = HotkeyBinding(
    # ... wizard hotkey config
)

# In hotkey list - REMOVE wizard from hotkey_details and registrations
```

#### 3.4 Remove UI Mode / User Level References

Setup Wizard used "beginner" vs "advanced" modes. If this is only for wizard:
- Remove `user_level` / `ui_mode` concept
- Or keep if used elsewhere

**Search for**:
- `wizard_hotkey_combo` references
- `wizard_hotkey_label` references
- `user_level` / `ui_mode` in startup

#### 3.5 Delete Setup Wizard Files

```bash
# Delete:
rm ui/windows/setup_wizard.py
rm ui/windows/setup_wizard_vision.py (KEEP - used for vision system)

# Check if empty after removing setup_wizard:
ls ui/windows/
```

#### 3.6 Update `app_lifecycle_controller.py`

Currently has `check_first_time_setup()` that launches wizard.

**Behavior after wizard removal**:
- Don't show messagebox asking about wizard
- Just silently run `auto_detect` if first-time
- Or skip entirely - let user manually select window

**Options**:
```python
# Option A: Silent auto-detect
def check_first_time_setup(self) -> None:
    if is_first_time:
        service = WindowDetectionService()
        best_window = service.find_best_cabal_window()
        if best_window:
            save_to_config(best_window)

# Option B: Skip first-time check entirely
# (remove the method)
```

### Phase 4: Simplify Window Selection in Main UI

**No changes needed** - logic already works via `on_hunt_find_windows()`:

1. Click refresh button → calls `on_hunt_find_windows()`
2. Click combobox dropdown → calls `on_hunt_find_windows()` if list empty
3. Select from dropdown → calls `on_window_combo_selected()`

Just update to use new service behind the scenes.

## 📁 Files to Modify

### New Files:
- ✅ `lib/features/hunt/window_detection_service.py` - NEW

### Files to Edit:
- `app_gui.py` - Remove sidebar button, methods, hotkey logic, import
- `ui/controllers/app_window_controller.py` - Use new service, remove duplicate logic
- `ui/controllers/app_lifecycle_controller.py` - Update first-time check
- Possibly `lib/features/hunt/hotkey_controller.py` - Remove wizard hotkey registration

### Files to Delete:
- `ui/windows/setup_wizard.py` - REMOVE
- ❌ `ui/windows/setup_wizard_vision.py` - KEEP (used for vision system)

### Files to Check/Update:
- i18n translations - search for `setup_wizard` namespace and consider cleanup
- Tests if they reference setup_wizard

## 🔍 Code Locations Reference

### Setup Wizard Window Detection (to extract):
- **File**: `ui/windows/setup_wizard.py`
- **Method**: `_enum_windows()` - lines 1656-1710
- **Method**: `_search_windows()` - lines 1460-1487
- **Method**: `_on_window_select()` - lines 1494-1510

### App Window Controller (existing logic):
- **File**: `ui/controllers/app_window_controller.py`
- **Method**: `_list_windows()` - lines 14-56
- **Method**: `on_hunt_find_windows()` - lines 102-127
- **Method**: `on_hunt_refresh_windows()` - lines 89-101
- **Method**: `_retry_resolve_bounds()` - lines 68-87

### Setup Wizard References (to remove):
- **File**: `app_gui.py`
- **Sidebar button**: line 705-710 - "sidebar_quick_setup"
- **Methods**: lines 1358-1362
- **Hotkey code**: lines 1389-1412, 2536-2576
- **Import**: line 1 - `from ui.windows.setup_wizard import show_setup_wizard`

### First-Time Check (to update):
- **File**: `ui/controllers/app_lifecycle_controller.py`
- **Method**: `check_first_time_setup()` - lines 88-110+

## 🛠️ Implementation Steps

### Step 1: Create New Service
1. Create `lib/features/hunt/window_detection_service.py`
2. Extract and merge logic from wizard + controller
3. Implement `find_all_cabal_windows(filter_text=None)`
4. Implement `find_best_cabal_window()`
5. Add comprehensive docstrings
6. Add error handling and logging

### Step 2: Update App Window Controller
1. Import new service
2. Update `on_hunt_find_windows()` to use service
3. Update `on_hunt_refresh_windows()` to use service
4. Remove duplicate `_list_windows()` method
5. Simplify `_retry_resolve_bounds()` to use service

### Step 3: Remove Wizard - Part 1 (UI)
1. Remove sidebar "sidebar_quick_setup" button
2. Remove `on_setup_wizard()` method
3. Remove `try_close_setup_wizard()` method
4. Remove import of setup_wizard

### Step 4: Remove Wizard - Part 2 (Hotkeys)
1. Remove `_update_setup_wizard_hotkey_state()` method
2. Remove setup wizard from hotkey registration
3. Remove wizard hotkey config (setup_wizard_key, etc.)
4. Clean up hotkey_details display

### Step 5: Update App Lifecycle
1. Decide on first-time behavior (silent auto-detect vs skip)
2. Update `check_first_time_setup()` accordingly
3. Update or remove wizard-related logic
4. Test first-time run experience

### Step 6: Delete Files
1. Delete `ui/windows/setup_wizard.py`
2. Verify no import errors
3. Search for remaining references to `setup_wizard`

### Step 7: Testing
1. Run app normally → window combobox works
2. Click refresh button → finds windows
3. Click combobox dropdown → finds windows
4. Select window → applies selection
5. First-time run → auto-detects or skips wizard gracefully
6. No import errors
7. All tests pass (if exist)

## ✅ Success Criteria

- ✅ New `WindowDetectionService` created and working
- ✅ Refresh button uses new service
- ✅ Combobox uses new service
- ✅ Setup Wizard completely removed
- ✅ No references to setup_wizard in codebase
- ✅ No "Quick Setup" button in sidebar
- ✅ App starts without errors
- ✅ Window detection works smoothly
- ✅ Code is cleaner and less duplicated
- ✅ All unit tests pass
- ✅ Formatted with black
- ✅ No linting errors with flake8

## 📊 Code Quality

### Before (Metrics):
- Setup Wizard: ~1700 lines (mostly UI + window logic mix)
- App Window Controller: ~330 lines
- Duplicate window detection logic in 2+ places
- Hotkey logic mixed with UI code

### After (Metrics):
- WindowDetectionService: ~200-250 lines (focused, reusable)
- App Window Controller: ~200 lines (simplified, cleaner)
- App GUI: -50 lines (removed wizard-related code)
- Single source of truth for window detection

## 🔗 Related Files

- `lib/system/window_manager.py` - Low-level window ops
- `lib/features/hunt/config_validator.py` - Window validation
- `lib/features/hunt/hunt_config.py` - Config persistence
- `ui/controllers/app_lifecycle_controller.py` - App startup
- `lib/i18n/translations.py` - i18n strings (setup_wizard namespace)

## 📝 Notes

1. **Backward Compatibility**: Setup Wizard is not used by existing users (optional), so safe to remove
2. **First-Time Users**: Will need to manually select window OR implement silent auto-detect
3. **Hotkeys**: Ctrl+Shift+N (was wizard) can be reassigned or removed
4. **Vision Wizard**: Keep! (`setup_wizard_vision.py` is for vision system, not setup)
5. **Window Selection**: Always available in main UI combobox, so no functionality lost

## 🚀 Deployment Plan

1. Create + test new service
2. Update controller to use service
3. Remove wizard references one by one
4. Manual smoke test (refresh, select, apply)
5. Run full test suite
6. Format code (black + flake8)
7. Create PR with clear commit messages:
   - `refactor: extract window detection service`
   - `refactor: update window controller to use new service`
   - `feat: remove setup wizard (deprecated)`
   - `chore: remove setup wizard hotkey config`

## ❓ Questions to Clarify

1. **First-time users**: Should auto-detect window silently or show manual selection dialog?
2. **Ctrl+Shift+N hotkey**: Remove entirely or reassign to something else?
3. **User level concept**: Only for wizard (remove) or used elsewhere (keep)?
4. **i18n cleanup**: Remove all `setup_wizard.*` translation keys?
