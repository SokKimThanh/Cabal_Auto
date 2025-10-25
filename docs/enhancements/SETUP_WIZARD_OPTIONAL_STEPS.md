# Setup Wizard - Optional Steps Enhancement

## Overview

**Issue**: Setup Wizard required all steps (Window, Monster, Skills) which caused data duplication issues for first-time users when they configured data in multiple forms.

**Solution**: Make Monster and Skills steps **optional**, allowing users to:
1. Configure basic settings early (Window only)
2. Add Monster/Skills later via Library Manager
3. Prevent data sync conflicts across multiple forms

## Design Rationale

### Problem: Data Duplication
When first-time users configure the same data in multiple places:
- Setup Wizard creates initial config
- Library Manager creates/edits monsters
- Various forms read/write to same files
- Result: **Duplicate or conflicting data**

### Solution: Early Sync Strategy
By allowing skip of optional steps:
- ✅ Users sync Window settings immediately
- ✅ Monster/Skills added when ready (via Library Manager)
- ✅ Single source of truth for data
- ✅ No conflicting writes from multiple forms

## Step Requirements

### Step 1: Welcome (Always Valid)
- **Status**: Optional
- **Fields**: Language selection, User level
- **Can Skip**: Yes

### Step 2: Window Selection (REQUIRED) 🔴
- **Status**: **Mandatory**
- **Fields**: Game window title, PID, HWND
- **Can Skip**: NO - Must select window to proceed
- **Validation**: Shows warning if not selected

### Step 3: Monster Selection (OPTIONAL) ✅
- **Status**: Optional
- **Fields**: Monster name, HP, templates
- **Can Skip**: YES - Shows info message, allows proceed
- **Empty State**: Shows helpful message with skip instructions

### Step 4: Skills Configuration (OPTIONAL) ✅
- **Status**: Optional
- **Fields**: 9 skill slots
- **Can Skip**: YES - Shows info message, allows proceed
- **Empty State**: All slots can remain empty

### Step 5: Review (Always Valid)
- **Status**: Always valid
- **Fields**: Summary of all selections
- **Warnings**: Shows appropriate messages:
  - Red warning for missing Window (shouldn't happen)
  - Blue notes for missing Monster/Skills (expected)

## Code Changes

### 1. UI Labels Updated

```python
# Step 3 subtitle
subtitle.config(text=self._t("step3_subtitle") + " (Optional - you can add monsters later)")

# Step 4 subtitle
subtitle.config(text=self._t("step4_subtitle") + " (Optional - you can configure later)")
```

### 2. Empty Monster State (Enhanced)

**Before**:
```python
if not self.monsters_data:
    tk.Label(text="No monsters found", fg="orange").pack()
    return
```

**After**:
```python
if not self.monsters_data:
    # Show helpful message for empty monster list
    tk.Label(text="📋 No Monsters Yet", font=("Arial", 14, "bold")).pack()
    tk.Label(text="✓ You can skip this step and add monsters later").pack()
    tk.Label(text="💡 Tip: Click 'Next' to continue without selecting a monster").pack()
    return
```

### 3. Validation Logic Updated

#### Step 2 (Window) - REQUIRED
```python
if self.current_step == 2:
    if not self.wizard_data.get("window_title"):
        messagebox.showwarning(
            "Window Required",
            "⚠️ Game window selection is required to continue.\n\n"
            "Please select your game window from the list."
        )
        return False
    return True
```

#### Step 3 (Monster) - OPTIONAL
```python
if self.current_step == 3:
    if not self.wizard_data.get("monster_name"):
        messagebox.showinfo(
            "Monster Selection (Optional)",
            "No monster selected. You can add monsters later via Library Manager.\n\n"
            "💡 Tip: Configuring window and skills first helps prevent data sync issues."
        )
    return True  # Allow proceed regardless
```

#### Step 4 (Skills) - OPTIONAL
```python
if self.current_step == 4:
    # ... collect skills ...
    assigned = [s for s in skill_slots if s]
    if not assigned:
        messagebox.showinfo(
            "Skills (Optional)",
            "No skills assigned. You can configure skills later via Library Manager.\n\n"
            "💡 Completing basic setup first helps prevent data sync issues."
        )
    return True  # Allow proceed regardless
```

### 4. Review Step Warnings

**Before**:
```python
# All warnings shown as orange
if not monster_name:
    tk.Label(text="⚠️ Warning: No monster selected", fg="orange").pack()
```

**After**:
```python
# Only Window is critical (red)
if not window_info:
    tk.Label(text="⚠️ Warning: No game window selected (Required)", fg="red").pack()

# Monster/Skills are optional (blue info)
if not monster_name:
    tk.Label(text="ℹ️ Note: No monster selected (Can be added later)", fg="#2196F3").pack()

if not assigned_skills:
    tk.Label(text="ℹ️ Note: No skills configured (Can be added later)", fg="#2196F3").pack()
```

## User Experience

### Scenario 1: Complete Setup (All Steps)
1. User opens app → Wizard appears
2. Step 1: Select language → Next
3. Step 2: Select window → Next
4. Step 3: Select monster → Next
5. Step 4: Configure skills → Next
6. Step 5: Review → Finish
7. ✅ All data saved

### Scenario 2: Minimal Setup (Window Only)
1. User opens app → Wizard appears
2. Step 1: Select language → Next
3. Step 2: Select window → Next
4. Step 3: **No monsters yet** → Shows skip message → Next
5. Step 4: **No skills** → Shows skip message → Next
6. Step 5: Review shows notes for missing data → Finish
7. ✅ Window saved, Monster/Skills empty (can add later)

### Scenario 3: Adding Data Later
1. User completes minimal setup (Window only)
2. Opens Library Manager (Ctrl+Shift+L)
3. Adds monsters in Monster tab
4. Configures skills in Rotation tab
5. ✅ Data added through single source (Library Manager)
6. ✅ No duplication, no conflicts

## Benefits

### 1. Prevents Data Duplication ✅
- Single entry point for Monster/Skills (Library Manager)
- No conflicting writes from multiple forms
- Cleaner data management

### 2. Better User Experience ✅
- Not forced to configure everything upfront
- Can start using app with minimal setup
- Gradual configuration as needed

### 3. Reduces Errors ✅
- Less chance of sync issues
- Simpler first-run experience
- Clear guidance on what's required vs optional

### 4. Flexibility ✅
- Power users can complete full setup
- New users can start minimal
- Both workflows supported

## Testing

### Test 1: Window Required
```
Step 2 → Try Next without selection
Expected: ⚠️ Warning dialog, blocks proceed
Result: ✅ PASS
```

### Test 2: Monster Optional
```
Step 3 → No monsters.json data → Try Next
Expected: ℹ️ Info dialog, allows proceed
Result: ✅ PASS
```

### Test 3: Skills Optional
```
Step 4 → Leave all slots empty → Try Next
Expected: ℹ️ Info dialog, allows proceed
Result: ✅ PASS
```

### Test 4: Review Notes
```
Step 5 → Complete with Window only
Expected: Blue notes for missing Monster/Skills
Result: ✅ PASS
```

## Files Modified

1. **ui/windows/setup_wizard.py**
   - Updated docstrings (3 methods)
   - Enhanced empty state UI (Step 3)
   - Updated validation logic (Steps 2, 3, 4)
   - Updated review warnings (Step 5)
   - Added helpful messages throughout

2. **tests/manual/test_wizard_optional_steps.py**
   - New test script for validation
   - Tests logic and empty state handling
   - Provides manual test instructions

## Migration Guide

### For Users
No action needed. Existing configs remain valid.

### For Developers
If you call Setup Wizard programmatically:

**Before**:
```python
# Assumed all data would be filled
wizard_data = wizard.wizard_data
monster = wizard_data["monster_name"]  # Could be empty now!
```

**After**:
```python
# Check for optional data
wizard_data = wizard.wizard_data
monster = wizard_data.get("monster_name")
if monster:
    # Use monster data
else:
    # Handle empty case (expected for minimal setup)
```

## Related Issues

- **Fixed**: Data duplication across multiple forms
- **Improved**: First-run user experience
- **Enhanced**: Empty state messaging

## Documentation

- This file: `docs/enhancements/SETUP_WIZARD_OPTIONAL_STEPS.md`
- Test script: `tests/manual/test_wizard_optional_steps.py`
- Related: `docs/bugfixes/BUGFIX_SETUP_WIZARD_PATH.md`

## Status

✅ **COMPLETE**  
Setup Wizard now allows skipping Monster and Skills steps for better data management.

---

**Date**: 2025-01-XX  
**Component**: Setup Wizard  
**Type**: Enhancement  
**Impact**: Improves data consistency and UX for first-time users  
**Files Changed**: 2 (1 source, 1 test)
