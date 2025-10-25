# Migration Plan: Refactor Quick Monster Editor to Use ButtonStateMixin

## Current State

`quick_monster_editor.py` có custom `_update_button_states()` method với ~60 lines code.

## Target State

Sử dụng `ButtonStateMixin` để giảm code và tăng tính tái sử dụng.

## Migration Steps

### Step 1: Import Mixin

```python
# Add to imports
from ui.mixins import ButtonStateMixin

# Change class declaration
class QuickMonsterEditor(tk.Toplevel, ButtonStateMixin):
```

### Step 2: Initialize Mixin

```python
def __init__(self, ...):
    tk.Toplevel.__init__(self, parent)
    ButtonStateMixin.__init__(self)  # Add this
    # ... rest of init
```

### Step 3: Replace Current Button State Setup

**Remove current method:**
```python
# DELETE this method (~60 lines at line 520):
def _update_button_states(self) -> None:
    """Update button states based on current selection state."""
    has_monster = bool(self.current_monster_id)
    has_template = bool(self.template_listbox.selection() if self.template_listbox else False)
    # ... lots of if/else
```

**Add new setup method:**
```python
def _setup_button_state_management(self) -> None:
    """Setup automatic button state management using mixin."""
    # Register selection widgets
    self.register_selection_widget('monsters', self.monster_listbox)
    self.register_selection_widget('templates', self.template_listbox)
    
    # Register all buttons
    buttons_map = {
        # Monster buttons
        'add_monster': self.monster_add_btn,
        'edit_monster': self.monster_edit_btn,
        'delete_monster': self.monster_delete_btn,
        
        # Template buttons
        'add_template': self.template_add_btn,
        'edit_template': self.template_edit_btn,
        'delete_template': self.template_delete_btn,
        
        # Template operations
        'capture_template': self.template_capture_btn,
        'browse_template': self.template_browse_btn,
        'test_template': self.template_test_btn,
        'browse_template_folder': self.template_browse_folder_btn,
        
        # Info tab buttons
        'save_info': self.save_btn,
        'cancel_info': self.cancel_btn,
    }
    
    for name, btn in buttons_map.items():
        if btn:
            self.register_button(name, btn)
    
    # Define button rules
    self.register_button_rules({
        # Monster buttons
        'add_monster': {'always': True},
        'edit_monster': {'requires_selection': 'monsters'},
        'delete_monster': {'requires_selection': 'monsters'},
        
        # Template buttons (hierarchical)
        'add_template': {'requires_parent': 'monsters'},
        'edit_template': {'requires_selection': 'templates'},
        'delete_template': {'requires_selection': 'templates'},
        
        # Template operations
        'capture_template': {'requires_parent': 'monsters'},
        'browse_template': {'requires_parent': 'monsters'},
        'test_template': {
            'requires_multiple': ['monsters', 'templates']
        },
        'browse_template_folder': {'requires_parent': 'monsters'},
        
        # Info tab buttons (custom logic)
        'save_info': {
            'custom': lambda: bool(self.current_monster_id and self.is_editing)
        },
        'cancel_info': {
            'custom': lambda: bool(self.is_editing)
        },
    })
    
    # Auto-update on selection change
    self.bind_auto_update('monsters', '<<TreeviewSelect>>')
    self.bind_auto_update('templates', '<<TreeviewSelect>>')
```

### Step 4: Call Setup in __init__

```python
def __init__(self, ...):
    # ... existing init code
    
    # Setup button state management (add near end of __init__)
    self._setup_button_state_management()
    
    # Initial button state update
    self.update_button_states()
```

### Step 5: Keep Existing update_button_states() Calls

**DO NOT CHANGE** the ~9 calls to `self._update_button_states()`:
- Line ~355: After initial setup
- Line ~2143: After monster selection
- Line ~2463: After monster add
- Line ~2566: After monster delete
- Line ~2816: After template selection
- Line ~2838: After template add
- Line ~2975: After template capture
- Line ~3088: After template browse
- Line ~3175: After template delete

These will automatically use the mixin's `update_button_states()` method.

## Alternative: Use Hierarchical Setup Helper

For even simpler code:

```python
def _setup_button_state_management(self) -> None:
    """Setup automatic button state management using mixin."""
    # Register selection widgets
    self.register_selection_widget('monsters', self.monster_listbox)
    self.register_selection_widget('templates', self.template_listbox)
    
    # Use hierarchical helper for Monster-Template buttons
    self.setup_hierarchical_buttons(
        parent_widget='monsters',
        child_widget='templates',
        parent_buttons={
            'add': self.monster_add_btn,
            'edit': self.monster_edit_btn,
            'delete': self.monster_delete_btn,
        },
        child_buttons={
            'add': self.template_add_btn,
            'edit': self.template_edit_btn,
            'delete': self.template_delete_btn,
        }
    )
    
    # Register additional buttons manually
    additional_buttons = {
        'capture_template': (self.template_capture_btn, {'requires_parent': 'monsters'}),
        'browse_template': (self.template_browse_btn, {'requires_parent': 'monsters'}),
        'test_template': (self.template_test_btn, {'requires_multiple': ['monsters', 'templates']}),
        'browse_folder': (self.template_browse_folder_btn, {'requires_parent': 'monsters'}),
        'save_info': (self.save_btn, {'custom': lambda: bool(self.current_monster_id and self.is_editing)}),
        'cancel_info': (self.cancel_btn, {'custom': lambda: bool(self.is_editing)}),
    }
    
    for name, (btn, rule) in additional_buttons.items():
        if btn:
            self.register_button(name, btn)
            self.register_button_rules({name: rule})
```

## Testing Checklist

After migration, verify:

- [ ] Add Monster button always enabled
- [ ] Edit/Delete Monster buttons enabled only when monster selected
- [ ] Add Template button enabled only when monster selected
- [ ] Edit/Delete Template buttons enabled only when template selected
- [ ] Capture/Browse buttons enabled only when monster selected
- [ ] Test button enabled only when both monster and template selected
- [ ] Save/Cancel buttons enabled only in edit mode
- [ ] All buttons update correctly after add/delete operations
- [ ] Auto-update works when clicking on list items

## Benefits After Migration

- **-40 lines** of code (60 lines method → ~20 lines setup)
- **Consistent** with other windows
- **Easy to modify** rules
- **Testable** independently
- **No more manual state checks**

## Rollback Plan

If issues occur:
1. Git revert the changes
2. Keep using custom `_update_button_states()`
3. Report bugs in mixin

## Estimated Time

- Migration: 15 minutes
- Testing: 10 minutes
- Total: 25 minutes
