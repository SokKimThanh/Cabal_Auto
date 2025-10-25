"""
ACTION-NOTIFICATION MIXIN - QUICK REFERENCE

For developers: How to use ActionNotificationMixin in your windows

================================================================================
QUICK START
================================================================================

1. Import and inherit:
   ```python
   from ui.mixins.action_notification_mixin import ActionNotificationMixin
   
   class MyWindow(ActionNotificationMixin, tk.Toplevel):
       pass
   ```

2. Initialize:
   ```python
   def __init__(self, ...):
       tk.Toplevel.__init__(self, ...)
       ActionNotificationMixin.__init__(self, debug_mode=False)
   ```

3. Set notification widget:
   ```python
   self.notification_widget = NotificationWidget(...)
   self.set_notification_widget(self.notification_widget)
   ```

4. Register rules:
   ```python
   self.register_action_rules({
       'add_item': {
           'validation': {
               'check': lambda: self.is_editing,
               'message': "⚠️ Enable Edit Mode first",
               'type': 'warning'
           },
           'success': {
               'message': "✅ Item added!",
               'type': 'success'
           },
           'error': {
               'message': "❌ Failed: {error}",
               'type': 'error'
           }
       }
   })
   ```

5. Use in button command:
   ```python
   def _on_add_item(self):
       self.execute_action('add_item', self._do_add_item)
   
   def _do_add_item(self):
       if not self.is_editing:
           raise ValueError("Edit mode required")
       # ... actual implementation
       return result
   ```

================================================================================
RULE TYPES
================================================================================

validation:
  - When: Before action executes
  - Purpose: Check pre-conditions
  - If fails: Show notification, don't execute action
  - Example:
    ```python
    'validation': {
        'check': lambda: self.has_selection(),
        'message': "⚠️ Please select an item first",
        'type': 'warning'
    }
    ```

confirmation:
  - When: After validation, before execution
  - Purpose: Ask user for destructive actions
  - If user cancels: Don't execute action
  - Example:
    ```python
    'confirmation': {
        'check': lambda: self.has_children(),
        'message': "This will delete all children. Continue?",
        'type': 'warning'
    }
    ```

success:
  - When: After action executes successfully
  - Purpose: Show positive feedback
  - Example:
    ```python
    'success': {
        'message': "✅ Changes saved successfully!",
        'type': 'success'
    }
    ```

error:
  - When: Action raises exception
  - Purpose: Show error feedback
  - Can use {error} placeholder for exception message
  - Example:
    ```python
    'error': {
        'message': "❌ Failed to save: {error}",
        'type': 'error'
    }
    ```

================================================================================
NOTIFICATION TYPES
================================================================================

Type        | Color      | Icon | Usage
------------|------------|------|----------------------------------
'info'      | Blue       | ℹ️   | Informational messages
'success'   | Green      | ✅   | Action completed successfully
'warning'   | Yellow     | ⚠️   | Validation errors, confirmations
'error'     | Red        | ❌   | Errors, failures

================================================================================
COMMON PATTERNS
================================================================================

Pattern 1: Edit Mode Required
------------------------------
```python
'add_monster': {
    'validation': {
        'check': lambda: self.is_editing,
        'message': "⚠️ Enable Edit Mode first",
        'type': 'warning'
    },
    'success': {'message': "✅ Monster added!", 'type': 'success'},
    'error': {'message': "❌ Failed: {error}", 'type': 'error'}
}
```

Pattern 2: Selection Required
------------------------------
```python
'edit_item': {
    'validation': {
        'check': lambda: self.has_selection(),
        'message': "⚠️ Select an item to edit",
        'type': 'warning'
    },
    'success': {'message': "✅ Item updated!", 'type': 'success'},
    'error': {'message': "❌ Failed: {error}", 'type': 'error'}
}
```

Pattern 3: Destructive Action with Confirmation
------------------------------------------------
```python
'delete_monster': {
    'validation': {
        'check': lambda: self.has_selection(),
        'message': "⚠️ Select a monster to delete",
        'type': 'warning'
    },
    'confirmation': {
        'check': lambda: self.monster_has_templates(),
        'message': "Monster has templates. Delete all? This cannot be undone.",
        'type': 'warning'
    },
    'success': {'message': "✅ Monster deleted!", 'type': 'success'},
    'error': {'message': "❌ Failed: {error}", 'type': 'error'}
}
```

Pattern 4: No Changes to Save
------------------------------
```python
'save': {
    'validation': {
        'check': lambda: self.is_dirty,
        'message': "ℹ️ No changes to save",
        'type': 'info'
    },
    'success': {'message': "✅ Saved!", 'type': 'success'},
    'error': {'message': "❌ Save failed: {error}", 'type': 'error'}
}
```

Pattern 5: Multiple Conditions (AND logic)
------------------------------------------
```python
'add_template': {
    'validation': {
        'check': lambda: self.is_editing and self.has_monster_selection(),
        'message': "⚠️ Select a monster first and enable Edit Mode",
        'type': 'warning'
    },
    'success': {'message': "✅ Template added!", 'type': 'success'},
    'error': {'message': "❌ Failed: {error}", 'type': 'error'}
}
```

Pattern 6: Optional Success Notification
-----------------------------------------
```python
'refresh': {
    'validation': {
        'check': lambda: self.connection_available(),
        'message': "⚠️ No connection available",
        'type': 'warning'
    },
    # No success notification (silent success)
    'error': {'message': "❌ Refresh failed: {error}", 'type': 'error'}
}
```

================================================================================
IMPLEMENTATION PATTERN
================================================================================

Step 1: Separate button handler from implementation
----------------------------------------------------
```python
# Button command - thin wrapper
def _on_add_item(self):
    """Button click handler with notification support."""
    if hasattr(self, 'execute_action'):
        self.execute_action('add_item', self._do_add_item)
    else:
        # Fallback if mixin not available
        self._do_add_item()

# Actual implementation - pure logic
def _do_add_item(self) -> Any:
    """Actual add item implementation."""
    # Validation (raise ValueError for validation errors)
    if not self.is_editing:
        raise ValueError("Edit mode required")
    
    # Implementation
    item = {'id': uuid.uuid4(), 'name': 'New Item'}
    self.items.append(item)
    self.is_dirty = True
    
    # Update UI
    self._refresh_list()
    
    # Return result (used in success message if needed)
    return item
```

Step 2: Use exceptions for errors
----------------------------------
```python
def _do_save_file(self) -> str:
    """Save to file."""
    if not self.filepath:
        raise ValueError("No file path specified")
    
    try:
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f)
    except IOError as e:
        raise RuntimeError(f"File write error: {e}")
    
    return self.filepath
```

================================================================================
HELPER METHODS
================================================================================

Common helper methods to use in validation checks:

```python
def _has_selection(self) -> bool:
    """Check if item is selected."""
    if isinstance(self.listbox, ttk.Treeview):
        return len(self.listbox.selection()) > 0
    else:
        return len(self.listbox.curselection()) > 0

def _has_changes(self) -> bool:
    """Check if there are unsaved changes."""
    return self.is_dirty

def _is_valid_form(self) -> bool:
    """Check if form has valid data."""
    return self.name_entry.get().strip() != ""

def _has_children(self) -> bool:
    """Check if selected item has children."""
    selection = self.get_selected_item()
    return len(selection.get('children', [])) > 0
```

================================================================================
TESTING CHECKLIST
================================================================================

For each action with notification rules:

1. ✅ Test validation failure:
   - Trigger action when validation should fail
   - Verify warning notification appears
   - Verify action does NOT execute

2. ✅ Test validation success → action success:
   - Trigger action when all conditions met
   - Verify action executes
   - Verify success notification appears

3. ✅ Test validation success → action error:
   - Mock/force action to raise exception
   - Verify error notification appears
   - Verify error message includes exception details

4. ✅ Test confirmation (if applicable):
   - Trigger action that needs confirmation
   - Click "No" → verify action cancelled
   - Click "Yes" → verify action executes

5. ✅ Test without mixin (fallback):
   - Temporarily remove mixin
   - Verify action still works (fallback mode)

================================================================================
TROUBLESHOOTING
================================================================================

Problem: "Action not registered" error
Solution: Make sure to call register_action_rules() before using execute_action()

Problem: Validation check not working
Solution: Use lambda functions for checks that reference self: lambda: self.is_editing

Problem: Error message not showing {error} placeholder
Solution: Make sure to raise exceptions in _do_* methods, not return False

Problem: Notification not appearing
Solution: Verify set_notification_widget() was called with NotificationWidget instance

Problem: Confirmation dialog not showing
Solution: Check that confirmation 'check' lambda returns True when confirmation needed

Problem: Multiple notifications stacking
Solution: Use auto_hide_seconds in NotificationWidget to prevent stacking

================================================================================
BEST PRACTICES
================================================================================

1. ✅ Keep validation checks simple
   - Use lambda functions
   - Return bool (True = valid, False = invalid)

2. ✅ Use descriptive messages
   - Include emoji icons (⚠️ ✅ ❌ ℹ️)
   - Be specific about what's wrong
   - Suggest how to fix (e.g., "Enable Edit Mode first")

3. ✅ Separate concerns
   - Button handler (_on_*) = thin wrapper with execute_action()
   - Implementation (_do_*) = pure logic with exceptions

4. ✅ Use exceptions for errors
   - ValueError = validation errors
   - RuntimeError = execution errors
   - Specific exceptions for specific errors

5. ✅ Return meaningful results
   - Return created/modified object
   - Return affected count (e.g., "3 items deleted")
   - Return success indicator if needed

6. ✅ Support fallback mode
   - Always check hasattr(self, 'execute_action')
   - Provide direct call fallback
   - Don't assume mixin is always available

7. ✅ Use i18n for messages
   - Wrap messages in i18n_t() for multi-language support
   - Provide default English text
   - Use namespace for organization

================================================================================
EXAMPLES
================================================================================

See:
- ui/windows/quick_monster_editor.py (production example)
- examples/action_notification_integration.py (demo)
- tests/manual/test_quick_monster_editor_notifications.py (test)

================================================================================
"""