# Python Coding Guidelines for AI Assistant

**Version**: 2.0.0  
**Date**: October 25, 2025  
**Status**: ACTIVE & ENFORCED  
**Applies to**: All Python code written by AI Assistant

---

## 🎯 Core Principles

These guidelines are **mandatory** and must be followed for every line of Python code written. No exceptions.

**New in v2.0**: Added comprehensive UI Form Design Guidelines for Tkinter applications (Section 8)

---

## 📋 The Rules

### Python Core Rules (1-7)
1. Always Check Data Types Before Use
2. Never Call Attributes/Methods on None
3. Never Call Instance Methods via Class
4. Never Call Functions with Missing Required Arguments
5. Never Duplicate Expensive Operations
6. Use Only Stable Package Versions
7. Never Mix Namespace Imports

### UI Form Rules (8)
8. Follow Tkinter UI Form Design Standards
   - Three-layer architecture
   - Inline notifications (no popups)
   - Widget lifecycle safety
   - Consistent component patterns
   - i18n integration
   - Accessibility support

---

## 📋 The 7 Golden Rules (Python Core)

### Rule 1: Always Check Data Types Before Use

**Requirement**: Type hints + runtime validation

```python
# ✅ CORRECT
def process_data(data: Optional[List[str]] = None) -> List[str]:
    if data is None:
        data = []
    
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data)}")
    
    return [item.upper() for item in data if item]

# ❌ WRONG
def process_data(data):
    return [item.upper() for item in data]  # Crash if None!
```

**Checklist**:
- [ ] All function parameters have type hints
- [ ] All return types are specified
- [ ] Input validation before use
- [ ] Proper error messages with actual types

---

### Rule 2: Never Call Attributes/Methods on None

**Requirement**: Explicit None checks before access

```python
# ✅ CORRECT
window_info = manager.get_window_info(hwnd)
if window_info is not None:
    title = window_info.title
    width = window_info.rect['width']
else:
    logger.error("Window not found")
    return None

# ❌ WRONG
window_info = manager.get_window_info(hwnd)
title = window_info.title  # AttributeError if None!
```

**Checklist**:
- [ ] Check `is not None` before accessing attributes
- [ ] Check `is not None` before calling methods
- [ ] Early return on None with proper logging
- [ ] Use Optional[T] type hints for nullable types

---

### Rule 3: Pass Complete and Correct Arguments

**Requirement**: Read function signature, pass all required args with correct types

```python
# ✅ CORRECT
def match_templates(
    self,
    frame: np.ndarray,
    roi: Optional[Tuple[int, int, int, int]] = None,
    templates: Optional[List[str]] = None,
    max_results: int = 10
) -> List[Detection]:
    pass

# Call with proper arguments
results = self.match_templates(
    frame=current_frame,
    roi=(10, 10, 100, 100),  # x, y, w, h - all 4 values
    templates=["temp1", "temp2"],
    max_results=5
)

# ❌ WRONG
results = self.match_templates(
    frame=current_frame,
    roi=(10, 10),  # Missing w, h!
    templates="temp1"  # Wrong type, should be List!
)
```

**Checklist**:
- [ ] Read function signature before calling
- [ ] Pass all required arguments
- [ ] Use correct types for each argument
- [ ] Use keyword arguments for clarity

---

### Rule 4: Call Instance and Static Methods Correctly

**Requirement**: Instance via `self`/instance, static via `ClassName`

```python
class WindowManager:
    def find_window(self, title: str) -> Optional[int]:
        """Instance method"""
        pass
    
    @staticmethod
    def validate_hwnd(hwnd: int) -> bool:
        """Static method"""
        pass

# ✅ CORRECT - Instance method
manager = WindowManager()
hwnd = manager.find_window("Game")

# ✅ CORRECT - Static method
is_valid = WindowManager.validate_hwnd(hwnd)

# ❌ WRONG - Instance method via class
hwnd = WindowManager.find_window("Game")  # Missing self!

# ❌ WRONG - Static via instance (confusing)
is_valid = manager.validate_hwnd(hwnd)
```

**Checklist**:
- [ ] Instance methods: Always create instance first
- [ ] Instance methods: Call via `self` or `instance`
- [ ] Static methods: Call via `ClassName`
- [ ] No confusion between instance and static

---

### Rule 5: Avoid Unnecessary Duplicate Logic

**Requirement**: Cache results, don't call same function repeatedly

```python
# ✅ CORRECT - Call once, cache result
stats = self.get_capture_stats()
if stats:
    logger.info(f"FPS: {stats['fps']}")
    logger.info(f"Captured: {stats['frames_captured']}")
    logger.info(f"Dropped: {stats['frames_dropped']}")

# ❌ WRONG - Repeated calls
logger.info(f"FPS: {self.get_capture_stats()['fps']}")
logger.info(f"Captured: {self.get_capture_stats()['frames_captured']}")
logger.info(f"Dropped: {self.get_capture_stats()['frames_dropped']}")

# ❌ WRONG - Duplicate logic
if user.is_admin():
    allow_access()
if user.is_admin():  # Already checked above!
    show_admin_menu()
```

**Checklist**:
- [ ] No duplicate function calls in same scope
- [ ] Cache expensive operations
- [ ] No repeated condition checks
- [ ] DRY principle (Don't Repeat Yourself)

---

### Rule 6: Use Stable Library Versions

**Requirement**: Only stable releases, no dev/alpha/beta versions

```powershell
# ✅ CORRECT - Stable versions with binary wheels
python -m pip install opencv-python==4.12.0
python -m pip install numpy==2.3.4
python -m pip install pywin32==311

# ❌ WRONG - Unstable versions
python -m pip install opencv-python==5.0.0.dev
python -m pip install numpy>=2.5.0a1  # Alpha!

# ✅ CORRECT - Use python -m pip
python -m pip install package

# ❌ WRONG - Direct pip call
pip install package
.\venv\Scripts\pip.exe install package
```

**Checklist**:
- [ ] Only stable/release versions (no dev/alpha/beta)
- [ ] Specify exact versions in requirements
- [ ] Use `python -m pip` not direct `pip`
- [ ] Prefer packages with binary wheels

---

### Rule 7: Check Library Namespaces and Versions

**Requirement**: Verify namespace for different library versions

```python
# ✅ CORRECT - Try new API first, fallback to old
try:
    # OpenCV 4.5+ moved trackers to legacy
    tracker = cv2.legacy.TrackerCSRT_create()
except AttributeError:
    # OpenCV < 4.5 compatibility
    tracker = cv2.TrackerCSRT_create()

# ✅ CORRECT - Explicit version check
import cv2
cv_version = tuple(map(int, cv2.__version__.split('.')[:2]))
if cv_version >= (4, 5):
    tracker = cv2.legacy.TrackerCSRT_create()
else:
    tracker = cv2.TrackerCSRT_create()

# ❌ WRONG - Assume API without checking
tracker = cv2.TrackerCSRT_create()  # Fails on OpenCV 4.5+!
```

**Checklist**:
- [ ] Check library version if API changed
- [ ] Use try-except for namespace compatibility
- [ ] Provide fallback for older versions
- [ ] Document version requirements

---

## 🔍 Pre-Commit Checklist

Before suggesting any code, verify:

```markdown
□ Type Hints: All parameters and returns typed?
□ None Checks: Checked before accessing?
□ Arguments: Correct count and types?
□ Method Calls: Proper instance/static pattern?
□ No Duplication: Cached results, no repeated calls?
□ Dependencies: Stable versions only?
□ Compatibility: Fallbacks for version differences?
□ Tests: Will tests pass?
□ Linting: No Pylance errors?
□ Documentation: Docstrings complete?
```

---

## 📚 Code Template

Standard template following all rules:

```python
from typing import Optional, List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """
    Example class following all 7 rules.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with type checking.
        
        Args:
            config: Optional configuration dictionary
        """
        # Rule 1: Type check
        if config is None:
            config = {}
        
        if not isinstance(config, dict):
            raise TypeError(f"Expected dict, got {type(config)}")
        
        self.config = config
        self.manager: Optional[SomeManager] = None
        
        # Rule 2: Check None before use
        try:
            self.manager = SomeManager(config)
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
    
    def process_items(
        self,
        items: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[str]:
        """
        Process items with safety checks.
        
        Args:
            items: Items to process
            options: Processing options
            max_results: Maximum results
            
        Returns:
            Processed results
        """
        # Rule 1 & 3: Validate inputs
        if items is None:
            items = []
        
        if not isinstance(items, list):
            raise TypeError(f"Expected list, got {type(items)}")
        
        if options is None:
            options = {}
        
        # Rule 2: Check manager
        if self.manager is None:
            logger.error("Manager not initialized")
            return []
        
        # Rule 5: Cache result
        config = self._get_config()  # Call once
        
        results = []
        for item in items[:max_results]:
            if item is None:
                continue
            
            # Rule 4: Instance method via self
            result = self._process_single(item, config)
            if result is not None:
                results.append(result)
        
        return results
    
    def _process_single(self, item: str, config: Dict[str, Any]) -> Optional[str]:
        """Process single item."""
        if item is None or not item:
            return None
        return item.upper()
    
    @staticmethod
    def validate_input(value: Optional[str]) -> bool:
        """Validate input (static method)."""
        if value is None:
            return False
        return len(value) > 0
    
    def _get_config(self) -> Dict[str, Any]:
        """Get config copy."""
        return self.config.copy()


# Usage
def main():
    # Rule 3: Proper initialization
    config = {"key": "value"}
    example = ExampleClass(config=config)
    
    # Rule 3: Pass all arguments
    items = ["a", "b", None, "c"]
    results = example.process_items(
        items=items,
        options={"mode": "fast"},
        max_results=10
    )
    
    # Rule 2: Check None
    if results:
        for result in results:
            if result is not None:
                print(result)
    
    # Rule 4: Static via Class
    is_valid = ExampleClass.validate_input("test")
```

---

## 🚨 Common Violations to Avoid

### ❌ Type Safety Violations
```python
# WRONG: No type hints
def process(data):
    return data.upper()

# WRONG: No None check
def get_title(info):
    return info.title  # Crash if None!
```

### ❌ Method Call Violations
```python
# WRONG: Instance method via class
result = MyClass.instance_method()  # Missing self!

# WRONG: Multiple duplicate calls
print(f"Value: {expensive_function()}")
print(f"Double: {expensive_function() * 2}")  # Called again!
```

### ❌ Argument Violations
```python
# WRONG: Missing required arguments
result = function(arg1)  # Missing arg2, arg3!

# WRONG: Wrong types
result = function(items="string")  # Should be List!
```

---

## 🎨 UI Form Design Guidelines (Tkinter)

**Status**: MANDATORY for all UI form implementations  
**Applies to**: All Tkinter-based forms, editors, dialogs, and wizards

### 8.1 Three-Layer Architecture

**Requirement**: Separate UI from logic and data access

```python
# Layer 1: Data Access (lib/data/)
class MonsterRepository:
    """Handles monster data persistence"""
    def load_monsters(self) -> List[Dict]:
        pass
    
    def save_monster(self, data: Dict) -> bool:
        pass

# Layer 2: Business Logic (lib/features/)
class MonsterValidator:
    """Validates monster data"""
    def validate_name(self, name: str) -> Tuple[bool, str]:
        if not name or not name.strip():
            return False, "Name is required"
        return True, ""

# Layer 3: UI Presentation (ui/windows/)
class MonsterEditorWindow(tk.Toplevel):
    """UI form for editing monsters"""
    def __init__(self):
        self.repository = MonsterRepository()
        self.validator = MonsterValidator()
```

**Checklist**:
- [ ] Data access in `lib/data/`
- [ ] Business logic in `lib/features/`
- [ ] UI presentation in `ui/windows/` or `ui/components/`
- [ ] No direct file I/O in UI classes
- [ ] No validation logic in UI classes

### 8.2 Form Component Standards

**Requirement**: Use consistent component patterns

```python
# ✅ CORRECT: Labeled Entry
def _create_labeled_entry(
    self,
    parent: tk.Frame,
    label_text: str,
    variable: tk.StringVar,
    required: bool = False
) -> tk.Entry:
    """Create a labeled entry field with consistent styling"""
    
    # Label with required indicator
    label = tk.Label(
        parent,
        text=f"{label_text}{'*' if required else ''}:",
        font=("Segoe UI", 10)
    )
    label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    # Entry field
    entry = tk.Entry(
        parent,
        textvariable=variable,
        font=("Segoe UI", 10),
        width=30
    )
    entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    
    return entry

# ✅ CORRECT: Action Buttons
def _create_action_buttons(self, parent: tk.Frame) -> None:
    """Create form action buttons with consistent layout"""
    
    button_frame = tk.Frame(parent)
    button_frame.grid(row=0, column=0, sticky="ew", pady=10)
    
    # Primary action (left)
    self.save_btn = tk.Button(
        button_frame,
        text=self.i18n.get("save"),
        command=self._on_save,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=15
    )
    self.save_btn.pack(side="left", padx=5)
    
    # Secondary action (right)
    cancel_btn = tk.Button(
        button_frame,
        text=self.i18n.get("cancel"),
        command=self._on_cancel,
        bg="#f44336",
        fg="white",
        font=("Segoe UI", 10),
        width=15
    )
    cancel_btn.pack(side="right", padx=5)
```

**Checklist**:
- [ ] Required fields marked with asterisk (*)
- [ ] Consistent fonts: Segoe UI 10pt for fields, 10pt bold for buttons
- [ ] Primary buttons on left, secondary on right
- [ ] Consistent colors: green (#4CAF50) for save, red (#f44336) for cancel
- [ ] Grid layout with consistent padding (5px standard, 10px sections)

### 8.3 Validation & Feedback

**Requirement**: Use inline notifications instead of popups

```python
from ui.components.notification_widget import NotificationWidget

class MyForm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        # Create notification widget at top
        self.notification = NotificationWidget(
            self.main_frame,
            auto_hide=5,  # Auto-hide after 5 seconds
            show_close_button=True
        )
        self.notification.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.notification.hide()  # Hidden by default
    
    def _validate_and_save(self) -> None:
        """Validate form data and save"""
        
        # Step 1: Validate
        is_valid, errors = self._validate_form()
        
        if not is_valid:
            # Show validation errors inline
            self.notification.show(
                message="\n".join(errors),
                notification_type="warning"
            )
            return
        
        # Step 2: Save
        try:
            success = self.repository.save(self._get_form_data())
            
            if success:
                # Show success message
                self.notification.show(
                    message=self.i18n.get("save_success"),
                    notification_type="info"
                )
                self.after(2000, self.destroy)  # Close after 2s
            else:
                self.notification.show(
                    message=self.i18n.get("save_failed"),
                    notification_type="warning"
                )
        except Exception as e:
            self.notification.show(
                message=f"{self.i18n.get('error')}: {str(e)}",
                notification_type="warning"
            )
    
    def _validate_form(self) -> Tuple[bool, List[str]]:
        """Validate all form fields"""
        errors = []
        
        # Validate name
        name = self.name_var.get().strip()
        is_valid, error = self.validator.validate_name(name)
        if not is_valid:
            errors.append(f"• {error}")
        
        # Validate level
        try:
            level = int(self.level_var.get())
            if level < 1 or level > 200:
                errors.append("• Level must be between 1-200")
        except ValueError:
            errors.append("• Level must be a number")
        
        return (len(errors) == 0, errors)
```

**Checklist**:
- [ ] NotificationWidget at top of form
- [ ] auto_hide=5 seconds for info messages
- [ ] show_close_button=True for user control
- [ ] Validation before save (no popup messageboxes)
- [ ] Clear error messages with bullet points
- [ ] Success feedback before closing form

### 8.4 Widget Lifecycle Management

**Requirement**: Safe widget configuration and cleanup

```python
class MyForm(tk.Toplevel):
    def _update_ui_state(self) -> None:
        """Update UI state safely"""
        
        # ✅ Check widget exists before configuring
        if hasattr(self, "save_btn") and self.save_btn.winfo_exists():
            try:
                self.save_btn.config(state="normal" if self._is_valid() else "disabled")
            except tk.TclError:
                # Widget destroyed during configuration
                pass
    
    def _on_language_change(self) -> None:
        """Handle language change safely"""
        
        # ✅ Check all widgets before updating
        widgets_to_update = [
            (self.title_label, "text", self.i18n.get("title")),
            (self.save_btn, "text", self.i18n.get("save")),
            (self.cancel_btn, "text", self.i18n.get("cancel"))
        ]
        
        for widget, option, value in widgets_to_update:
            if hasattr(self, widget.__class__.__name__.lower() + "_btn"):
                if widget.winfo_exists():
                    try:
                        widget.config(**{option: value})
                    except tk.TclError:
                        pass
    
    def destroy(self) -> None:
        """Clean up resources before destroying"""
        
        # Unregister callbacks
        if hasattr(self, "i18n"):
            self.i18n.unregister_callback(self._on_language_change)
        
        # Call parent destroy
        super().destroy()
```

**Checklist**:
- [ ] Check `winfo_exists()` before configuring widgets
- [ ] Wrap widget configs in try-except for TclError
- [ ] Unregister callbacks in destroy()
- [ ] No configuration of destroyed widgets

### 8.5 Button State Management

**Requirement**: Context-aware button enabling/disabling

```python
from ui.mixins.button_state_mixin import ButtonStateMixin

class MyForm(tk.Toplevel, ButtonStateMixin):
    def __init__(self):
        super().__init__()
        
        # Create buttons
        self.save_btn = tk.Button(self, text="Save", command=self._on_save)
        
        # Initial state
        self._update_button_states()
    
    def _update_button_states(self) -> None:
        """Update all button states based on current context"""
        
        # Enable save button only if form is valid
        is_valid = self._is_form_valid()
        self._set_button_state(self.save_btn, is_valid)
    
    def _on_field_change(self, *args) -> None:
        """Called when any field changes"""
        self._update_button_states()
    
    def _is_form_valid(self) -> bool:
        """Check if form has valid data"""
        name = self.name_var.get().strip()
        return len(name) > 0
```

**Checklist**:
- [ ] Use ButtonStateMixin for consistent state management
- [ ] Update button states on field changes
- [ ] Disable save button for invalid data
- [ ] Visual feedback for disabled state

### 8.6 Form Data Flow Pattern

**Requirement**: Clear data flow from UI → Validation → Save → Feedback

```python
class MyForm(tk.Toplevel):
    """
    Data Flow:
    1. User Input → StringVar/IntVar
    2. Trigger → _on_save()
    3. Collect → _get_form_data()
    4. Validate → _validate_form()
    5. Save → repository.save()
    6. Feedback → notification.show()
    7. Close → destroy() or stay open
    """
    
    def _on_save(self) -> None:
        """Save button clicked - orchestrate the flow"""
        
        # Step 1: Collect form data
        form_data = self._get_form_data()
        
        # Step 2: Validate
        is_valid, errors = self._validate_form(form_data)
        if not is_valid:
            self._show_validation_errors(errors)
            return
        
        # Step 3: Save
        success, message = self._save_data(form_data)
        
        # Step 4: Feedback
        if success:
            self._show_success_feedback(message)
            self.after(2000, self.destroy)  # Auto-close
        else:
            self._show_error_feedback(message)
    
    def _get_form_data(self) -> Dict[str, Any]:
        """Collect all form field values"""
        return {
            "name": self.name_var.get().strip(),
            "level": int(self.level_var.get()),
            "hp": int(self.hp_var.get())
        }
    
    def _validate_form(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate form data using validator"""
        errors = []
        
        # Use validator from business logic layer
        is_valid, error = self.validator.validate_monster(data)
        if not is_valid:
            errors.append(error)
        
        return (len(errors) == 0, errors)
    
    def _save_data(self, data: Dict) -> Tuple[bool, str]:
        """Save data using repository"""
        try:
            success = self.repository.save_monster(data)
            if success:
                return True, self.i18n.get("save_success")
            else:
                return False, self.i18n.get("save_failed")
        except Exception as e:
            return False, str(e)
```

**Checklist**:
- [ ] Clear flow: Collect → Validate → Save → Feedback
- [ ] No direct save without validation
- [ ] Use repository for persistence
- [ ] Use validator for business rules
- [ ] Show feedback for all outcomes

### 8.7 Internationalization (i18n)

**Requirement**: All text must be translatable

```python
class MyForm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        # Get i18n instance
        from lib.i18n import I18n
        self.i18n = I18n.get_instance()
        
        # Register for language changes
        self.i18n.register_callback(self._on_language_change)
        
        # Use i18n for all text
        self.title(self.i18n.get("form_title"))
        
        # Labels
        label = tk.Label(self, text=self.i18n.get("name_label"))
        
        # Buttons
        save_btn = tk.Button(self, text=self.i18n.get("save"))
        cancel_btn = tk.Button(self, text=self.i18n.get("cancel"))
        
        # Messages
        self.notification.show(
            message=self.i18n.get("validation_failed"),
            notification_type="warning"
        )
    
    def _on_language_change(self) -> None:
        """Update all text when language changes"""
        if not self.winfo_exists():
            return
        
        try:
            self.title(self.i18n.get("form_title"))
            # Update all labels and buttons
            self._update_text_elements()
        except tk.TclError:
            pass
```

**Checklist**:
- [ ] All text through i18n.get()
- [ ] Register callback for language changes
- [ ] Update all text in _on_language_change()
- [ ] Unregister callback in destroy()
- [ ] No hardcoded strings in UI

### 8.8 Accessibility & UX

**Requirement**: Keyboard navigation and visual feedback

```python
class MyForm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._on_save())
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Tab order (automatic by grid/pack order)
        self.name_entry.focus_set()  # Initial focus
        
        # Visual feedback on hover
        self.save_btn.bind("<Enter>", lambda e: self._on_button_hover(e))
        self.save_btn.bind("<Leave>", lambda e: self._on_button_leave(e))
    
    def _on_button_hover(self, event) -> None:
        """Visual feedback when hovering over button"""
        event.widget.config(relief="raised")
    
    def _on_button_leave(self, event) -> None:
        """Reset visual state when leaving button"""
        event.widget.config(relief="flat")
```

**Checklist**:
- [ ] Enter key triggers save
- [ ] Escape key closes form
- [ ] Initial focus on first field
- [ ] Visual hover feedback
- [ ] Logical tab order

### 8.9 Complete Form Template

**Use this template for new forms**:

```python
"""
MyForm - Description of what this form does
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path

from ui.components.notification_widget import NotificationWidget
from ui.mixins.button_state_mixin import ButtonStateMixin
from lib.i18n import I18n


class MyForm(tk.Toplevel, ButtonStateMixin):
    """Form for editing/creating XYZ data"""
    
    def __init__(self, parent: tk.Tk, item_id: Optional[str] = None):
        """
        Initialize form
        
        Args:
            parent: Parent window
            item_id: ID of item to edit (None for create new)
        """
        super().__init__(parent)
        
        # Dependencies
        self.i18n = I18n.get_instance()
        self.repository = None  # Initialize your repository
        self.validator = None  # Initialize your validator
        
        # Form state
        self.item_id = item_id
        self.is_edit_mode = item_id is not None
        
        # Configure window
        self._configure_window()
        
        # Build UI
        self._build_ui()
        
        # Load data if editing
        if self.is_edit_mode:
            self._load_data()
        
        # Initial state
        self._update_button_states()
        
        # Register callbacks
        self.i18n.register_callback(self._on_language_change)
    
    def _configure_window(self) -> None:
        """Configure window properties"""
        self.title(self.i18n.get("form_title"))
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._on_save())
        self.bind("<Escape>", lambda e: self.destroy())
    
    def _build_ui(self) -> None:
        """Build user interface"""
        # Main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notification widget
        self.notification = NotificationWidget(
            self.main_frame,
            auto_hide=5,
            show_close_button=True
        )
        self.notification.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.notification.hide()
        
        # Form fields
        self._build_form_fields()
        
        # Action buttons
        self._build_action_buttons()
    
    def _build_form_fields(self) -> None:
        """Build form fields"""
        fields_frame = tk.Frame(self.main_frame)
        fields_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Example: Name field
        self.name_var = tk.StringVar()
        self.name_var.trace_add("write", self._on_field_change)
        self._create_labeled_entry(
            fields_frame,
            self.i18n.get("name_label"),
            self.name_var,
            required=True,
            row=0
        )
        
        # Add more fields here...
    
    def _create_labeled_entry(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        required: bool = False,
        row: int = 0
    ) -> tk.Entry:
        """Create labeled entry field"""
        # Label
        label = tk.Label(
            parent,
            text=f"{label_text}{'*' if required else ''}:",
            font=("Segoe UI", 10)
        )
        label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
        
        # Entry
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 10),
            width=30
        )
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        return entry
    
    def _build_action_buttons(self) -> None:
        """Build action buttons"""
        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        # Save button
        self.save_btn = tk.Button(
            button_frame,
            text=self.i18n.get("save"),
            command=self._on_save,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=15
        )
        self.save_btn.pack(side="left", padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text=self.i18n.get("cancel"),
            command=self.destroy,
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 10),
            width=15
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _on_field_change(self, *args) -> None:
        """Handle field value changes"""
        self._update_button_states()
    
    def _update_button_states(self) -> None:
        """Update button states based on form validity"""
        if hasattr(self, "save_btn") and self.save_btn.winfo_exists():
            is_valid = self._is_form_valid()
            self._set_button_state(self.save_btn, is_valid)
    
    def _is_form_valid(self) -> bool:
        """Check if form has valid data"""
        name = self.name_var.get().strip()
        return len(name) > 0
    
    def _load_data(self) -> None:
        """Load existing data for editing"""
        if not self.item_id:
            return
        
        try:
            data = self.repository.load_item(self.item_id)
            if data:
                self.name_var.set(data.get("name", ""))
                # Load other fields...
        except Exception as e:
            self.notification.show(
                message=f"{self.i18n.get('load_error')}: {str(e)}",
                notification_type="warning"
            )
    
    def _on_save(self) -> None:
        """Handle save button click"""
        # Collect data
        form_data = self._get_form_data()
        
        # Validate
        is_valid, errors = self._validate_form(form_data)
        if not is_valid:
            self.notification.show(
                message="\n".join(errors),
                notification_type="warning"
            )
            return
        
        # Save
        try:
            success = self.repository.save_item(form_data)
            
            if success:
                self.notification.show(
                    message=self.i18n.get("save_success"),
                    notification_type="info"
                )
                self.after(2000, self.destroy)
            else:
                self.notification.show(
                    message=self.i18n.get("save_failed"),
                    notification_type="warning"
                )
        except Exception as e:
            self.notification.show(
                message=f"{self.i18n.get('error')}: {str(e)}",
                notification_type="warning"
            )
    
    def _get_form_data(self) -> Dict[str, Any]:
        """Collect form data"""
        return {
            "name": self.name_var.get().strip(),
            # Add other fields...
        }
    
    def _validate_form(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate form data"""
        errors = []
        
        # Validate name
        is_valid, error = self.validator.validate_name(data["name"])
        if not is_valid:
            errors.append(f"• {error}")
        
        # Add other validations...
        
        return (len(errors) == 0, errors)
    
    def _on_language_change(self) -> None:
        """Handle language change"""
        if not self.winfo_exists():
            return
        
        try:
            self.title(self.i18n.get("form_title"))
            # Update all text elements
            if hasattr(self, "save_btn") and self.save_btn.winfo_exists():
                self.save_btn.config(text=self.i18n.get("save"))
        except tk.TclError:
            pass
    
    def destroy(self) -> None:
        """Clean up before destroying"""
        # Unregister callbacks
        if hasattr(self, "i18n"):
            self.i18n.unregister_callback(self._on_language_change)
        
        super().destroy()
```

### 8.10 Anti-Patterns to Avoid

**❌ NEVER do these**:

```python
# ❌ Direct file I/O in UI class
class MyForm(tk.Toplevel):
    def save(self):
        with open("data.json", "w") as f:  # WRONG!
            json.dump(self.data, f)

# ❌ Validation logic in UI class
class MyForm(tk.Toplevel):
    def validate(self):
        if len(self.name) < 3:  # WRONG!
            return False

# ❌ Popup messageboxes for validation
def save(self):
    if not self.name:
        messagebox.showerror("Error", "Name required")  # WRONG!

# ❌ No widget existence check
def update_ui(self):
    self.label.config(text="New text")  # WRONG! Widget may be destroyed

# ❌ Hardcoded text
label = tk.Label(self, text="Save")  # WRONG! Not translatable
```

**✅ Correct patterns**:

```python
# ✅ Use repository for data access
self.repository.save_item(data)

# ✅ Use validator for business rules
is_valid, error = self.validator.validate_name(name)

# ✅ Use inline notifications
self.notification.show(message, "warning")

# ✅ Check widget existence
if self.label.winfo_exists():
    self.label.config(text="New text")

# ✅ Use i18n for all text
label = tk.Label(self, text=self.i18n.get("save"))
```

### 8.11 UI Form Checklist

**Before submitting any form code, verify**:

- [ ] **Architecture**
  - [ ] Data access in repository class
  - [ ] Validation in validator class
  - [ ] UI only handles presentation
  
- [ ] **Components**
  - [ ] Consistent label/entry layout
  - [ ] Required fields marked with *
  - [ ] Standard fonts and colors
  - [ ] Primary/secondary button positions
  
- [ ] **Validation**
  - [ ] NotificationWidget for feedback
  - [ ] No popup messageboxes
  - [ ] Clear error messages
  - [ ] Validation before save
  
- [ ] **Lifecycle**
  - [ ] winfo_exists() checks
  - [ ] Try-except for TclError
  - [ ] Unregister callbacks in destroy()
  
- [ ] **State Management**
  - [ ] ButtonStateMixin for buttons
  - [ ] Update states on field changes
  - [ ] Disable save for invalid data
  
- [ ] **i18n**
  - [ ] All text through i18n.get()
  - [ ] Language change callback
  - [ ] No hardcoded strings
  
- [ ] **Accessibility**
  - [ ] Enter key saves
  - [ ] Escape key cancels
  - [ ] Initial focus set
  - [ ] Logical tab order

---

## 📖 References

- Python Type Hints: [PEP 484](https://peps.python.org/pep-0484/)
- Optional Types: [PEP 484 - Optional](https://peps.python.org/pep-0484/#the-optional-type)
- Type Checking: [mypy documentation](http://mypy-lang.org/)
- Best Practices: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Tkinter Documentation: [Official Tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- UI Design Patterns: [Material Design Guidelines](https://material.io/design)

---

## 🔐 Enforcement

**Status**: ACTIVE  
**Authority**: Mandatory for all AI-generated code  
**Violations**: Must be fixed before code submission  
**Review**: Every code suggestion must pass all rules (Python + UI)  

**Signed**: GitHub Copilot AI Assistant  
**Date**: October 25, 2025  
**Version**: 2.0.0

---

## 📝 Change Log

### Version 2.0.0 (2025-10-25)
- **MAJOR UPDATE**: Added comprehensive UI Form Design Guidelines (Section 8)
- Added Rule 8: Tkinter UI Form Standards
  - Three-layer architecture (Data/Logic/UI separation)
  - Form component standards (labels, entries, buttons)
  - Inline notifications (no popup messageboxes)
  - Widget lifecycle management (winfo_exists + try-except)
  - Button state management with mixins
  - Data flow patterns (Collect → Validate → Save → Feedback)
  - i18n integration for all text
  - Accessibility & keyboard shortcuts
  - Complete form template with 400+ lines of example code
  - Anti-patterns and correct patterns
  - Comprehensive checklist (11 sections)
- Updated enforcement to include UI guidelines
- Added Tkinter and Material Design references
- **Purpose**: Ensure consistent UI implementation for both developers and AI assistants

### Version 1.0.0 (2025-10-23)
- Initial version
- Established 7 core rules
- Created enforcement checklist
- Added code templates
- Documented common violations

---

**END OF GUIDELINES**
