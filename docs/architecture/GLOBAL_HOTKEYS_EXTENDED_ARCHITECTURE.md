# Global Hotkeys Extended - Architecture Document

**Date**: 2025-10-21  
**Sprint**: Extended Global Hotkeys  
**Objective**: Add Setup Wizard and Library Manager hotkeys to centralized Global Hotkeys system

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Existing Global Hotkeys System

**Implementation Location**: `app_gui.py` lines 3102-3180

**Current Hotkeys**:
- `Ctrl+Shift+R`: Start hunt (`_global_start_hotkey`)
- `Ctrl+Shift+E`: Stop hunt (`_global_stop_hotkey`)

**Registration Lifecycle**:
```python
__init__() → _register_global_hotkeys()
on_close() → _unregister_global_hotkeys()
```

**Config Structure** (`hunt_config.json`):
```json
"global_hotkeys": {
  "enabled": true,
  "start_key": "ctrl+shift+r",
  "stop_key": "ctrl+shift+e"
}
```

**UI Location**: Setup tab, lines ~900-1000
- Checkbox: Enable/Disable global hotkeys
- 2 Comboboxes: Customize start_key, stop_key
- Global Apply button: Save changes

### 1.2 Current UI Elements to Replace

**Setup Wizard Button** (line 1336):
- Location: Below hunt controls
- Command: `_open_setup_wizard()`
- Enable/disable logic: Based on `ui_mode == 'beginner'`
- Icon: `support.ico`

**Library Manager Button** (line 1365):
- Location: Setup tab
- Command: `_open_library_manager()`
- Always enabled
- Icon: 🗂️ emoji

---

## 2. PROPOSED ARCHITECTURE

### 2.1 Extended Config Schema

**New fields in `global_hotkeys` section**:
```json
"global_hotkeys": {
  "enabled": true,
  "start_key": "ctrl+shift+r",
  "stop_key": "ctrl+shift+e",
  "setup_wizard_key": "ctrl+shift+n",      // NEW
  "library_manager_key": "ctrl+shift+l"    // NEW
}
```

**Backward Compatibility**:
- If new keys missing → use defaults
- Old configs continue working
- No migration needed

### 2.2 Hotkey Registration Flow

**Extended `_register_global_hotkeys()`**:
```python
def _register_global_hotkeys(self):
    # Existing
    self._global_start_hotkey = keyboard.add_hotkey(start_key, self.on_hunt_start)
    self._global_stop_hotkey = keyboard.add_hotkey(stop_key, self.on_hunt_stop)
    
    # NEW - Setup Wizard (conditional)
    if self.ui_mode_var.get() == 'beginner':
        self._global_wizard_hotkey = keyboard.add_hotkey(
            wizard_key, 
            self._on_setup_wizard_hotkey
        )
    
    # NEW - Library Manager (always)
    self._global_library_hotkey = keyboard.add_hotkey(
        library_key,
        self._on_library_manager_hotkey
    )
```

**Extended `_unregister_global_hotkeys()`**:
```python
def _unregister_global_hotkeys(self):
    # Existing cleanup
    if self._global_start_hotkey:
        keyboard.remove_hotkey(self._global_start_hotkey)
    if self._global_stop_hotkey:
        keyboard.remove_hotkey(self._global_stop_hotkey)
    
    # NEW cleanup
    if self._global_wizard_hotkey:
        keyboard.remove_hotkey(self._global_wizard_hotkey)
    if self._global_library_hotkey:
        keyboard.remove_hotkey(self._global_library_hotkey)
```

### 2.3 Conditional Activation Logic

**Setup Wizard Hotkey Rules**:
- **ONLY active** when `ui_mode == 'beginner'`
- When switching UI mode → re-register hotkeys
- Combobox disabled (grayed out) in intermediate/advanced mode
- Tooltip explains mode requirement

**Implementation**:
```python
def _update_hotkeys_state(self):
    """Called when UI mode changes"""
    current_mode = self.ui_mode_var.get()
    
    # Re-register all hotkeys with new state
    self._unregister_global_hotkeys()
    self._register_global_hotkeys()
    
    # Update UI combobox state
    if current_mode == 'beginner':
        self.wizard_hotkey_combo.config(state='normal')
    else:
        self.wizard_hotkey_combo.config(state='disabled')
```

**Library Manager Hotkey**:
- **Always active** (no mode restriction)
- Combobox always enabled

---

## 3. UI DESIGN

### 3.1 Extended Global Hotkeys Table

**Location**: Setup tab, after existing hotkey rows

**New Rows**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Global Hotkeys Configuration                                    │
├─────────────────────────┬─────────────────────────┬─────────────┤
│ Function                │ Hotkey                   │ Icon        │
├─────────────────────────┼─────────────────────────┼─────────────┤
│ Start Hunt              │ [Ctrl+Shift+R      ▼]   │             │
│ Stop Hunt               │ [Ctrl+Shift+E      ▼]   │             │
├─────────────────────────┼─────────────────────────┼─────────────┤
│ Setup Wizard (NEW)      │ [Ctrl+Shift+N      ▼]   │ support.ico │
│   ℹ️ Beginner mode only                                          │
├─────────────────────────┼─────────────────────────┼─────────────┤
│ Library Manager (NEW)   │ [Ctrl+Shift+L      ▼]   │ 🗂️           │
│   ℹ️ Always available                                            │
└─────────────────────────┴─────────────────────────┴─────────────┘
```

**Row Components**:
1. **Label**: Function name (i18n key)
2. **Combobox**: Hotkey selector (ttk.Combobox)
3. **Icon**: Visual indicator (tk.Label with image)
4. **Tooltip**: Explain function + activation rules

### 3.2 Visual States

**Enabled State** (Setup Wizard in beginner mode):
- Combobox: Normal background, clickable
- Icon: Full color
- Cursor: Hand pointer
- Tooltip: "Press Ctrl+Shift+N to open Setup Wizard"

**Disabled State** (Setup Wizard in other modes):
- Combobox: Gray background, not clickable
- Icon: Grayed out (50% opacity)
- Cursor: Default arrow
- Tooltip: "Only available in Beginner mode. Switch UI mode to enable."

---

## 4. CALLBACK IMPLEMENTATION

### 4.1 Setup Wizard Hotkey

```python
def _on_setup_wizard_hotkey(self):
    """Callback for Ctrl+Shift+N hotkey.
    
    Only executes if ui_mode == 'beginner'.
    Prevents accidental wizard opening in advanced modes.
    """
    try:
        print("[Hotkeys] Setup Wizard hotkey pressed")
        
        # Check mode before opening
        if self.ui_mode_var.get() != 'beginner':
            print("[Hotkeys] Setup Wizard blocked - not in beginner mode")
            # Optional: Show notification toast
            return
        
        # Open wizard
        self._open_setup_wizard()
        
    except Exception as e:
        print(f"[Hotkeys] Error opening Setup Wizard: {e}")
```

### 4.2 Library Manager Hotkey

```python
def _on_library_manager_hotkey(self):
    """Callback for Ctrl+Shift+L hotkey.
    
    Always available regardless of UI mode.
    """
    try:
        print("[Hotkeys] Library Manager hotkey pressed")
        self._open_library_manager()
        
    except Exception as e:
        print(f"[Hotkeys] Error opening Library Manager: {e}")
```

---

## 5. VALIDATION & CONFLICT DETECTION

### 5.1 Extended Validation

**Function**: `_validate_global_hotkeys()`

**Checks**:
1. ✅ No duplicate keys across all 4 hotkeys
2. ✅ Valid key combination format
3. ✅ Not system reserved keys (e.g., Ctrl+Alt+Del)

**Implementation**:
```python
def _validate_global_hotkeys(self):
    """Validate all global hotkeys for conflicts."""
    keys = [
        self.start_hotkey_var.get(),
        self.stop_hotkey_var.get(),
        self.wizard_hotkey_var.get(),    # NEW
        self.library_hotkey_var.get()    # NEW
    ]
    
    # Check for duplicates
    if len(keys) != len(set(keys)):
        return False, "Hotkey conflict detected!"
    
    # Check valid format
    for key in keys:
        if not self._is_valid_hotkey(key):
            return False, f"Invalid hotkey format: {key}"
    
    return True, "All hotkeys valid"
```

### 5.2 Global Apply Button

**When clicked**:
1. Validate all 4 hotkeys
2. Save to `hunt_config.json`
3. Unregister old hotkeys
4. Register new hotkeys
5. Show success/error message

---

## 6. TRANSLATION KEYS

### 6.1 New i18n Keys

**File**: `lib/i18n/translations.json`

```json
{
  "en": {
    "setup_wizard_hotkey": "Setup Wizard",
    "library_manager_hotkey": "Library Manager",
    "wizard_hotkey_tooltip": "Press Ctrl+Shift+N to open Setup Wizard. Only works in Beginner mode.",
    "library_hotkey_tooltip": "Press Ctrl+Shift+L to open Library Manager. Works in all modes.",
    "wizard_blocked_mode": "Setup Wizard is only available in Beginner mode.",
    "hotkey_conflict_error": "Hotkey conflict detected. Please use different key combinations."
  },
  "vi": {
    "setup_wizard_hotkey": "Trợ lý Thiết lập",
    "library_manager_hotkey": "Quản lý Thư viện",
    "wizard_hotkey_tooltip": "Nhấn Ctrl+Shift+N để mở Trợ lý Thiết lập. Chỉ hoạt động ở chế độ Người mới.",
    "library_hotkey_tooltip": "Nhấn Ctrl+Shift+L để mở Quản lý Thư viện. Hoạt động ở mọi chế độ.",
    "wizard_blocked_mode": "Trợ lý Thiết lập chỉ khả dụng ở chế độ Người mới.",
    "hotkey_conflict_error": "Phát hiện xung đột phím tắt. Vui lòng dùng tổ hợp phím khác."
  }
}
```

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Config & Core Logic (Batch 2-5)
- Update config schema
- Implement registration/unregistration
- Add callback methods
- UI mode change detection

### Phase 2: UI Changes (Batch 3, 6)
- Add 2 new rows to Global Hotkeys table
- Remove standalone buttons
- Implement enable/disable visual states

### Phase 3: Polish & Testing (Batch 7-10)
- Add tooltips
- Validation logic
- Translations
- Comprehensive testing
- Documentation

---

## 8. TESTING SCENARIOS

### Scenario 1: Beginner Mode - All Hotkeys Active
**Setup**: UI mode = beginner  
**Expected**: All 4 hotkeys registered and working  
**Test**: Press each hotkey, verify action executes

### Scenario 2: Advanced Mode - Wizard Disabled
**Setup**: UI mode = intermediate/advanced  
**Expected**: Start, Stop, Library work. Wizard blocked.  
**Test**: Press Ctrl+Shift+N → No wizard opens

### Scenario 3: Mode Switch - Re-registration
**Setup**: Change from beginner → advanced  
**Expected**: Wizard hotkey unregistered, others remain  
**Test**: Check console logs for re-registration

### Scenario 4: Conflict Detection
**Setup**: Set wizard_key = start_key  
**Expected**: Validation fails, error message shown  
**Test**: Click Global Apply → Error dialog

### Scenario 5: Config Persistence
**Setup**: Change hotkeys, save, restart app  
**Expected**: New hotkeys loaded and registered  
**Test**: Check hotkeys work after app restart

---

## 9. ROLLBACK PLAN

**If issues arise**:
1. Revert config schema changes
2. Restore standalone buttons
3. Keep only Start/Stop hotkeys
4. Document issues for future fix

**Safe Points**:
- After each batch, commit working state
- Keep backup of hunt_config.json
- Test thoroughly before batch completion

---

## 10. SUCCESS CRITERIA

✅ All 4 hotkeys register successfully  
✅ Setup Wizard hotkey respects UI mode  
✅ Library Manager hotkey always works  
✅ No hotkey conflicts possible  
✅ UI reflects hotkey states accurately  
✅ Translations complete (EN/VI)  
✅ Config saves/loads correctly  
✅ Backward compatible with old configs  
✅ All test scenarios pass  
✅ Documentation updated

---

**Next Step**: Batch 2 - Update `hunt_config.json` schema
