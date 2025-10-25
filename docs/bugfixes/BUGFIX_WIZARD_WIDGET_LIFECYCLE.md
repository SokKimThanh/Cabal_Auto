# Setup Wizard Widget Lifecycle Fix

## Issue

**Error**: `TclError: invalid command name ".!toplevel.!frame.!frame2.!canvas.!frame.!label11"`

**When**: 
- User navigates between wizard steps
- User changes language on Step 2+
- User rapidly switches between steps

**Root Cause**: 
- Methods try to config widgets that have been destroyed
- `hasattr()` checks attribute existence, NOT widget validity
- Destroyed widgets still have attributes but are invalid

## Technical Analysis

### The Problem

```python
# BEFORE (UNSAFE)
def _on_language_change(self):
    if hasattr(self, "level_new_radio"):
        self.level_new_radio.config(text=...)  # TclError if destroyed!
```

**Flow**:
1. User on Step 1 → `level_new_radio` widget created
2. User clicks Next → Step 2 UI built → Step 1 widgets destroyed
3. User changes language → `_on_language_change()` called
4. `hasattr(self, "level_new_radio")` → **True** (attribute still exists)
5. `self.level_new_radio.config(...)` → **TclError** (widget destroyed)

### Why hasattr() Isn't Enough

```python
class SetupWizard:
    def _build_step1_welcome(self):
        self.level_new_radio = tk.Radiobutton(...)  # Attribute assigned
    
    def _show_step(self, step_number):
        for widget in self.content_frame.winfo_children():
            widget.destroy()  # Widgets destroyed
        
        # But self.level_new_radio attribute still exists!
        # It points to a destroyed widget
```

**Key Insight**: 
- `hasattr()` checks Python object attribute
- Does NOT check Tk widget validity
- Destroyed widgets are "zombie references"

## The Fix

### 1. Check Widget Existence Before Config

```python
# AFTER (SAFE)
def _on_language_change(self):
    try:
        if hasattr(self, "level_new_radio") and self.level_new_radio.winfo_exists():
            self.level_new_radio.config(text=...)
    except tk.TclError:
        pass  # Widget destroyed - skip gracefully
```

**Protection Layers**:
1. ✅ `hasattr()` - Check Python attribute exists
2. ✅ `winfo_exists()` - Check Tk widget is valid
3. ✅ `try-except` - Catch any race conditions

### 2. All Affected Methods Fixed

#### _on_language_change()
```python
# Update Step 1 widgets (5 widgets checked)
try:
    if hasattr(self, "level_new_radio") and self.level_new_radio.winfo_exists():
        self.level_new_radio.config(text=self._t("user_level_new"))
except tk.TclError:
    pass
```

#### _update_rotation_builder_button_state()
```python
# Check button and hint label
if not hasattr(self, "rotation_builder_button"):
    return

try:
    if not self.rotation_builder_button.winfo_exists():
        return
except tk.TclError:
    return

# Then config safely
try:
    self.rotation_builder_button.config(state=tk.NORMAL)
except tk.TclError:
    pass
```

#### _show_step()
```python
# Defensive for persistent widgets too
try:
    self.progress_label.config(text=f"Step {step_number}...")
except (tk.TclError, AttributeError):
    pass

try:
    for i, dot in enumerate(self.progress_dots):
        dot.config(fg="...")
except (tk.TclError, AttributeError):
    pass
```

## Code Changes

### Files Modified

**ui/windows/setup_wizard.py** (3 methods):

1. **_on_language_change()** (Lines ~1355-1402)
   - Added `winfo_exists()` checks (5 widgets)
   - Wrapped each config in try-except
   - Prevents config of destroyed Step 1 widgets

2. **_update_rotation_builder_button_state()** (Lines ~1495-1532)
   - Added early widget validity check
   - Protected button and hint label configs
   - Prevents config of destroyed Step 4 widgets

3. **_show_step()** (Lines ~507-575)
   - Wrapped persistent widget configs (defensive)
   - Protected progress_label, dots, buttons
   - Extra safety for critical UI elements

## Testing

### Test Cases

#### 1. Language Change on Step 1 ✅
```
Step 1 → Change language EN→VI
Expected: Widgets update correctly
Result: ✅ PASS
```

#### 2. Language Change on Step 2+ ✅
```
Step 1 → Next → Step 2 → Back → Step 1 → Change language
Expected: No TclError, graceful skip
Result: ✅ PASS
```

#### 3. Rapid Step Navigation ✅
```
Step 1 → Next → Back → Next → Back (rapid)
Expected: No crashes, smooth transitions
Result: ✅ PASS
```

#### 4. User Level Change on Step 4 ✅
```
Step 4 → Change user level (triggers button state update)
Expected: Button/hint update correctly
Result: ✅ PASS
```

### Manual Test

```bash
python app_gui.py
# 1. Wizard opens
# 2. Change language (EN ↔ VI) → Works ✓
# 3. Navigate to Step 2
# 4. Back to Step 1
# 5. Change language again → No crash ✓
# 6. Go through all steps → No errors ✓
```

## Widget Lifecycle Explained

### Safe Lifecycle Pattern

```python
# CREATION (in _build_stepX methods)
def _build_step1_welcome(self):
    self.level_new_radio = tk.Radiobutton(...)  # Widget created
    # At this point:
    # - hasattr(self, "level_new_radio") → True
    # - self.level_new_radio.winfo_exists() → True

# DESTRUCTION (in _show_step)
def _show_step(self, step_number):
    for widget in self.content_frame.winfo_children():
        widget.destroy()  # Widgets destroyed
    # After this:
    # - hasattr(self, "level_new_radio") → Still True! (attribute remains)
    # - self.level_new_radio.winfo_exists() → False (widget destroyed)
    
# SAFE ACCESS (with checks)
def _on_language_change(self):
    if hasattr(self, "level_new_radio"):  # Attribute exists?
        if self.level_new_radio.winfo_exists():  # Widget valid?
            self.level_new_radio.config(...)  # Safe to config
```

### Widget Types

**Persistent Widgets** (survive step changes):
- `self.progress_label`
- `self.progress_dots`
- `self.back_button`
- `self.next_button`
- `self.cancel_button`

**Step-Specific Widgets** (destroyed on step change):
- `self.level_new_radio` (Step 1)
- `self.level_new_desc` (Step 1)
- `self.rotation_builder_button` (Step 4)
- `self.rotation_builder_hint` (Step 4)
- All listboxes, labels in content_frame

## Best Practices

### Always Check Widget Validity

```python
# ❌ WRONG - Crashes if widget destroyed
if hasattr(self, "widget"):
    self.widget.config(...)

# ✅ CORRECT - Safe with double check
try:
    if hasattr(self, "widget") and self.widget.winfo_exists():
        self.widget.config(...)
except tk.TclError:
    pass
```

### Why Three Layers?

1. **hasattr()**: Quick check - avoid AttributeError
2. **winfo_exists()**: Tk validity check - avoid TclError
3. **try-except**: Safety net - catch race conditions

### When to Use

Use this pattern when:
- ✅ Configuring step-specific widgets from other methods
- ✅ Updating UI based on state changes
- ✅ Handling user input that affects multiple widgets
- ✅ Widget may be destroyed before callback completes

Don't need when:
- ❌ Widget just created in same method
- ❌ Operating on persistent widgets only
- ❌ Inside the step's own build method

## Related Issues

### Similar Patterns in Codebase

Check these patterns for similar issues:
```python
# Potentially unsafe
if hasattr(self, "widget"):
    self.widget.config(...)

# Should be
try:
    if hasattr(self, "widget") and self.widget.winfo_exists():
        self.widget.config(...)
except tk.TclError:
    pass
```

### Prevention

To prevent future issues:
1. Always use `winfo_exists()` for step-specific widgets
2. Wrap widget operations in try-except
3. Document which widgets are persistent vs temporary
4. Test navigation + state changes together

## Status

✅ **COMPLETE**  
All widget lifecycle issues in Setup Wizard resolved.

---

**Date**: 2025-01-XX  
**Component**: Setup Wizard  
**Type**: Bug Fix  
**Severity**: High (causes crashes)  
**Impact**: Affects all wizard navigation + language changes  
**Files Changed**: 1 (ui/windows/setup_wizard.py)  
**Lines Modified**: ~100 lines (3 methods)
