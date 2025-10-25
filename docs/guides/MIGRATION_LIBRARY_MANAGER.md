# Migration Plan: Refactor Library Manager to Use ButtonStateMixin

## Overview

`library_manager.py` có 3 tabs với nhiều buttons:
1. **Monster Tab**: Monster list + Template list (hierarchical)
2. **Skill Tab**: Skill list với Add/Edit/Delete
3. **Template Tab**: Template list với operations

## Current State Analysis

Cần phân tích button state logic hiện tại trong LibraryManager.

### Monster Tab Structure
- `monster_tree`: Treeview for monsters
- `template_tree`: Treeview for templates (child of monster)
- Buttons: Add/Edit/Delete Monster, Add/Edit/Delete Template, etc.

### Skill Tab Structure
- `skill_tree`: Treeview for skills
- Buttons: Add/Edit/Delete Skill

### Template Tab Structure
- `template_tree`: Treeview for templates
- Buttons: Template operations

## Migration Steps

### Phase 1: Import and Initialize

```python
# Add to imports at top of file
from ui.mixins import ButtonStateMixin

# Modify class declaration
class LibraryManagerWindow(tk.Toplevel, ButtonStateMixin):
    def __init__(self, parent, ...):
        tk.Toplevel.__init__(self, parent)
        ButtonStateMixin.__init__(self)  # Add this line
        # ... rest of init
```

### Phase 2: Monster Tab Setup

```python
def _setup_monster_button_management(self):
    """Setup button state management for Monster tab."""
    # Register widgets
    self.register_selection_widget('monsters', self.monster_tree)
    self.register_selection_widget('templates', self.template_tree)
    
    # Use hierarchical helper
    self.setup_hierarchical_buttons(
        parent_widget='monsters',
        child_widget='templates',
        parent_buttons={
            'add': self.monster_add_btn,      # Find actual button names
            'edit': self.monster_edit_btn,
            'delete': self.monster_delete_btn,
        },
        child_buttons={
            'add': self.template_add_btn,
            'edit': self.template_edit_btn,
            'delete': self.template_delete_btn,
        }
    )
    
    # Register additional template operation buttons
    additional_buttons = {
        'capture_template': (self.template_capture_btn, {'requires_parent': 'monsters'}),
        'browse_template': (self.template_browse_btn, {'requires_parent': 'monsters'}),
        'test_template': (self.template_test_btn, {'requires_multiple': ['monsters', 'templates']}),
        # ... other template buttons
    }
    
    for name, (btn, rule) in additional_buttons.items():
        if btn and hasattr(self, btn):
            self.register_button(name, btn)
            self.register_button_rules({name: rule})
```

### Phase 3: Skill Tab Setup

```python
def _setup_skill_button_management(self):
    """Setup button state management for Skill tab."""
    # Register widgets
    self.register_selection_widget('skills', self.skill_tree)
    
    # Register buttons
    buttons = {
        'add_skill': (self.skill_add_btn, {'always': True}),
        'edit_skill': (self.skill_edit_btn, {'requires_selection': 'skills'}),
        'delete_skill': (self.skill_delete_btn, {'requires_selection': 'skills'}),
        'import_skill': (self.skill_import_btn, {'always': True}),
        'export_skill': (self.skill_export_btn, {'requires_selection': 'skills'}),
    }
    
    for name, (btn, rule) in buttons.items():
        if btn and hasattr(self, btn):
            self.register_button(name, btn)
            self.register_button_rules({name: rule})
    
    # Auto-update
    self.bind_auto_update('skills', '<<TreeviewSelect>>')
```

### Phase 4: Template Tab Setup

```python
def _setup_template_button_management(self):
    """Setup button state management for Template tab."""
    # Register widgets
    self.register_selection_widget('template_standalone', self.template_standalone_tree)
    
    # Register buttons
    buttons = {
        'add_template': (self.template_standalone_add_btn, {'always': True}),
        'edit_template': (self.template_standalone_edit_btn, {'requires_selection': 'template_standalone'}),
        'delete_template': (self.template_standalone_delete_btn, {'requires_selection': 'template_standalone'}),
        'test_template': (self.template_standalone_test_btn, {'requires_selection': 'template_standalone'}),
    }
    
    for name, (btn, rule) in buttons.items():
        if btn and hasattr(self, btn):
            self.register_button(name, btn)
            self.register_button_rules({name: rule})
    
    # Auto-update
    self.bind_auto_update('template_standalone', '<<TreeviewSelect>>')
```

### Phase 5: Call Setup Methods

```python
def __init__(self, parent, ...):
    # ... existing init code
    
    # Setup button state management for all tabs
    self._setup_monster_button_management()
    self._setup_skill_button_management()
    self._setup_template_button_management()
    
    # Initial button state update
    self.update_button_states()
```

### Phase 6: Add update_button_states() Calls

Add `self.update_button_states()` after:
- Monster add/edit/delete
- Template add/edit/delete  
- Skill add/edit/delete
- Any selection change (auto via bind_auto_update)
- Tab change (if different buttons per tab)

## Action Required: Find Button References

Need to grep for actual button variable names:

```bash
# Find monster buttons
grep -n "add.*monster" ui/windows/library_manager.py
grep -n "edit.*monster" ui/windows/library_manager.py
grep -n "delete.*monster" ui/windows/library_manager.py

# Find template buttons
grep -n "add.*template" ui/windows/library_manager.py
grep -n "edit.*template" ui/windows/library_manager.py

# Find skill buttons
grep -n "add.*skill" ui/windows/library_manager.py
grep -n "edit.*skill" ui/windows/library_manager.py
```

## Testing Checklist

### Monster Tab
- [ ] Add Monster always enabled
- [ ] Edit/Delete Monster enabled when monster selected
- [ ] Add Template enabled when monster selected
- [ ] Edit/Delete Template enabled when template selected
- [ ] Template operations enabled with correct dependencies

### Skill Tab
- [ ] Add Skill always enabled
- [ ] Edit/Delete Skill enabled when skill selected
- [ ] Import always enabled
- [ ] Export enabled when skill selected

### Template Tab
- [ ] Add Template always enabled
- [ ] Edit/Delete Template enabled when template selected
- [ ] Test enabled when template selected

### Cross-Tab
- [ ] Button states update when switching tabs
- [ ] No interference between tabs

## Benefits

- **Consistent** behavior across all tabs
- **Less code** (remove manual state checks)
- **Easy to maintain** (centralized rules)
- **Same as QuickMonsterEditor** (unified system)

## Estimated Time

- Find button references: 10 minutes
- Implement Phase 1-5: 20 minutes
- Add update calls: 15 minutes
- Testing: 20 minutes
- **Total: ~65 minutes**

## Next Steps

1. ✅ Create ButtonStateMixin
2. ✅ Document usage
3. ⏳ Find LibraryManager button references
4. ⏳ Implement migration
5. ⏳ Test thoroughly
6. 🔜 Migrate QuickMonsterEditor (optional refactor)
