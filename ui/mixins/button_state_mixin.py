"""
Button State Management Mixin

Provides automatic button state management based on selection state.
This mixin can be used by any Tkinter window that has buttons dependent on selection state.

Usage:
    class MyWindow(tk.Toplevel, ButtonStateMixin):
        def __init__(self):
            tk.Toplevel.__init__(self)
            ButtonStateMixin.__init__(self)

            # Define button state rules
            self.register_button_rules({
                'my_add_btn': {'always': True},
                'my_edit_btn': {'requires_selection': 'item_list'},
                'my_delete_btn': {'requires_selection': 'item_list'},
                'child_add_btn': {'requires_parent': 'item_list'},
                'child_edit_btn': {'requires_selection': 'child_list'},
            })

            # Call update after any state change
            self.update_button_states()

Author: SokKimThanh
Date: 2025-10-25
"""

from typing import Dict, List, Optional, Union, Callable, Any
import tkinter as tk
from tkinter import ttk
import logging


class ButtonState:
    """Enumeration of button states."""

    ENABLED = "normal"
    DISABLED = "disabled"
    HIDDEN = "hidden"
    VISIBLE = "visible"


class ButtonStateMixin:
    """
    Mixin class for comprehensive button state management.

    Features:
    - Centralized button state logic (enabled/disabled/visible/hidden)
    - Edit mode vs View mode support
    - Check All handling
    - Support for hierarchical dependencies (parent-child)
    - Context-based state management
    - Custom validation functions
    - Automatic state updates based on selection
    - Easy integration with any Tkinter window
    - Comprehensive error handling
    - Optional logging for debugging

    Button Types Supported:
    - Data operation buttons (Add/Edit/Delete)
    - Hierarchical buttons (Parent-Child relationship)
    - Global/aggregate buttons (Check All, Confirm, etc.)
    - Mode toggle buttons (Edit/View mode)

    Attributes:
        _button_rules: Dictionary mapping button names to their enable conditions
        _visibility_rules: Dictionary mapping button names to visibility conditions
        _selection_widgets: Dictionary mapping widget names to widget instances
        _button_refs: Dictionary mapping button names to button instances
        _context: State context (edit_mode, check_all, selections, etc.)
        _logger: Optional logger for debugging
        _debug_mode: Enable/disable debug logging
    """

    def __init__(
        self, debug_mode: bool = False, logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the button state mixin.

        Args:
            debug_mode: Enable debug logging (default: False)
            logger: Custom logger instance (default: creates new logger)
        """
        self._button_rules: Dict[str, Dict[str, Any]] = {}
        self._visibility_rules: Dict[str, Dict[str, Any]] = {}
        self._selection_widgets: Dict[str, Union[tk.Listbox, ttk.Treeview]] = {}
        self._button_refs: Dict[str, Union[tk.Button, ttk.Button]] = {}

        # Context state tracking
        self._context: Dict[str, Any] = {
            "edit_mode": False,
            "check_all": False,
            "selections": {},
            "data_count": {},
        }

        self._debug_mode = debug_mode
        self._logger = logger or logging.getLogger(__name__)

        if debug_mode:
            self._logger.setLevel(logging.DEBUG)
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(
                    logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
                )
                self._logger.addHandler(handler)

    def register_button_rules(self, rules: Dict[str, Dict[str, Any]]) -> None:
        """
        Register button state rules with validation.

        Args:
            rules: Dictionary mapping button names to their conditions.
                   Each condition can have:
                   - 'always': bool - Always enabled if True
                   - 'requires_selection': str - Requires selection in named widget
                   - 'requires_parent': str - Requires parent selection before enabling
                   - 'requires_multiple': List[str] - Requires selection in multiple widgets
                   - 'custom': Callable - Custom validation function returning bool

        Raises:
            TypeError: If rules is not a dictionary
            ValueError: If rule format is invalid

        Example:
            {
                'add_monster_btn': {'always': True},
                'edit_monster_btn': {'requires_selection': 'monster_list'},
                'add_template_btn': {'requires_parent': 'monster_list'},
                'test_template_btn': {
                    'requires_multiple': ['monster_list', 'template_list']
                },
                'custom_btn': {
                    'custom': lambda: self.some_condition()
                }
            }
        """
        if not isinstance(rules, dict):
            raise TypeError(f"rules must be a dictionary, got {type(rules).__name__}")

        # Validate each rule
        valid_keys = {
            "always",
            "requires_selection",
            "requires_parent",
            "requires_multiple",
            "custom",
            "requires_edit_mode",
            "requires_check_all",
            "disabled_in_edit_mode",
            "enabled_with_check_all_or_selection",
            "requires_context",
        }
        for button_name, rule in rules.items():
            if not isinstance(rule, dict):
                raise ValueError(
                    f"Rule for '{button_name}' must be a dictionary, got {type(rule).__name__}"
                )

            # Check for unknown keys
            unknown_keys = set(rule.keys()) - valid_keys
            if unknown_keys:
                self._logger.warning(
                    f"Unknown rule keys for '{button_name}': {unknown_keys}"
                )

            # Validate 'always' type
            if "always" in rule and not isinstance(rule["always"], bool):
                raise ValueError(
                    f"'always' rule for '{button_name}' must be bool, got {type(rule['always']).__name__}"
                )

            # Validate 'requires_selection' type
            if "requires_selection" in rule and not isinstance(
                rule["requires_selection"], str
            ):
                raise ValueError(
                    f"'requires_selection' for '{button_name}' must be str, got {type(rule['requires_selection']).__name__}"
                )

            # Validate 'requires_parent' type
            if "requires_parent" in rule and not isinstance(
                rule["requires_parent"], str
            ):
                raise ValueError(
                    f"'requires_parent' for '{button_name}' must be str, got {type(rule['requires_parent']).__name__}"
                )

            # Validate 'requires_multiple' type
            if "requires_multiple" in rule:
                if not isinstance(rule["requires_multiple"], (list, tuple)):
                    raise ValueError(
                        f"'requires_multiple' for '{button_name}' must be list/tuple, got {type(rule['requires_multiple']).__name__}"
                    )

            # Validate 'custom' type
            if "custom" in rule and not callable(rule["custom"]):
                raise ValueError(
                    f"'custom' rule for '{button_name}' must be callable, got {type(rule['custom']).__name__}"
                )

        self._button_rules.update(rules)

        if self._debug_mode:
            self._logger.debug(f"Registered {len(rules)} button rules")

    def register_selection_widget(
        self, name: str, widget: Union[tk.Listbox, ttk.Treeview]
    ) -> None:
        """
        Register a selection widget (Listbox or Treeview) with validation.

        Args:
            name: Name to reference this widget in button rules
            widget: The widget instance

        Raises:
            TypeError: If widget is not Listbox or Treeview
            ValueError: If name is empty or widget is None
        """
        if not name:
            raise ValueError("Widget name cannot be empty")

        if widget is None:
            raise ValueError(f"Widget for '{name}' cannot be None")

        if not isinstance(widget, (tk.Listbox, ttk.Treeview)):
            raise TypeError(
                f"Widget '{name}' must be Listbox or Treeview, got {type(widget).__name__}"
            )

        self._selection_widgets[name] = widget

        if self._debug_mode:
            self._logger.debug(
                f"Registered selection widget '{name}' ({type(widget).__name__})"
            )

    def register_button(self, name: str, button: Union[tk.Button, ttk.Button]) -> None:
        """
        Register a button widget for state management with validation.

        Args:
            name: Name used in button rules
            button: The button widget instance

        Raises:
            TypeError: If button is not Button or ttk.Button
            ValueError: If name is empty or button is None
        """
        if not name:
            raise ValueError("Button name cannot be empty")

        if button is None:
            raise ValueError(f"Button for '{name}' cannot be None")

        if not isinstance(button, (tk.Button, ttk.Button)):
            raise TypeError(
                f"Button '{name}' must be tk.Button or ttk.Button, got {type(button).__name__}"
            )

        self._button_refs[name] = button

        if self._debug_mode:
            self._logger.debug(f"Registered button '{name}' ({type(button).__name__})")

    def has_selection(self, widget_name: str) -> bool:
        """
        Check if a widget has selection with error handling.

        Args:
            widget_name: Name of the registered widget

        Returns:
            True if widget has selection, False otherwise
        """
        widget = self._selection_widgets.get(widget_name)
        if not widget:
            if self._debug_mode:
                self._logger.warning(f"Widget '{widget_name}' not registered")
            return False

        try:
            # Check if widget still exists
            if not widget.winfo_exists():
                if self._debug_mode:
                    self._logger.warning(f"Widget '{widget_name}' no longer exists")
                return False

            if isinstance(widget, ttk.Treeview):
                return bool(widget.selection())
            elif isinstance(widget, tk.Listbox):
                return bool(widget.curselection())
            else:
                return False
        except tk.TclError as e:
            if self._debug_mode:
                self._logger.error(f"Error checking selection for '{widget_name}': {e}")
            return False

    def get_selection_value(self, widget_name: str) -> Optional[Any]:
        """
        Get the current selection value from a widget with error handling.

        Args:
            widget_name: Name of the registered widget

        Returns:
            Selected item ID/index or None if no selection
        """
        widget = self._selection_widgets.get(widget_name)
        if not widget:
            if self._debug_mode:
                self._logger.warning(f"Widget '{widget_name}' not registered")
            return None

        try:
            if not widget.winfo_exists():
                return None

            if isinstance(widget, ttk.Treeview):
                selection = widget.selection()
                return selection[0] if selection else None
            elif isinstance(widget, tk.Listbox):
                selection = widget.curselection()
                return selection[0] if selection else None
            else:
                return None
        except tk.TclError as e:
            if self._debug_mode:
                self._logger.error(f"Error getting selection from '{widget_name}': {e}")
            return None

    # === Batch Registration Methods ===

    def register_buttons_batch(
        self, buttons: Dict[str, Union[tk.Button, ttk.Button]]
    ) -> None:
        """
        Register multiple buttons at once.

        Args:
            buttons: Dictionary mapping button names to button instances

        Example:
            self.register_buttons_batch({
                'add_btn': self.add_button,
                'edit_btn': self.edit_button,
                'delete_btn': self.delete_button
            })
        """
        for name, button in buttons.items():
            try:
                self.register_button(name, button)
            except (TypeError, ValueError) as e:
                self._logger.error(f"Failed to register button '{name}': {e}")

    def register_widgets_batch(
        self, widgets: Dict[str, Union[tk.Listbox, ttk.Treeview]]
    ) -> None:
        """
        Register multiple selection widgets at once.

        Args:
            widgets: Dictionary mapping widget names to widget instances

        Example:
            self.register_widgets_batch({
                'monsters': self.monster_tree,
                'templates': self.template_tree
            })
        """
        for name, widget in widgets.items():
            try:
                self.register_selection_widget(name, widget)
            except (TypeError, ValueError) as e:
                self._logger.error(f"Failed to register widget '{name}': {e}")

    # === Context Management Methods ===

    def set_edit_mode(self, edit_mode: bool) -> None:
        """
        Set edit mode state and update button states.

        Args:
            edit_mode: True for edit mode, False for view mode
        """
        self._context["edit_mode"] = edit_mode

        if self._debug_mode:
            self._logger.debug(f"Edit mode: {edit_mode}")

        self.update_button_states()

    def set_check_all(self, check_all: bool) -> None:
        """
        Set check all state and update button states.

        Args:
            check_all: True if all items are checked
        """
        self._context["check_all"] = check_all

        if self._debug_mode:
            self._logger.debug(f"Check all: {check_all}")

        self.update_button_states()

    def update_context(self, **kwargs) -> None:
        """
        Update multiple context values at once.

        Args:
            **kwargs: Context key-value pairs to update

        Example:
            self.update_context(
                edit_mode=True,
                check_all=False,
                monster_count=5
            )
        """
        self._context.update(kwargs)

        if self._debug_mode:
            self._logger.debug(f"Context updated: {kwargs}")

        self.update_button_states()

    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get context value(s).

        Args:
            key: Specific key to get, or None for entire context

        Returns:
            Context value or entire context dict
        """
        if key is None:
            return self._context.copy()
        return self._context.get(key)

    def is_edit_mode(self) -> bool:
        """Check if currently in edit mode."""
        return bool(self._context.get("edit_mode", False))

    def is_check_all(self) -> bool:
        """Check if check all is enabled."""
        return bool(self._context.get("check_all", False))

    # === State Inspection Methods ===

    def get_enabled_buttons(self) -> List[str]:
        """
        Get list of currently enabled button names.

        Returns:
            List of button names that are currently enabled
        """
        enabled = []
        all_buttons = list(
            dict.fromkeys(
                list(self._button_refs.keys()) + list(self._button_rules.keys())
            )
        )
        for button_name in all_buttons:
            if self.should_enable_button(button_name):
                enabled.append(button_name)
        return enabled

    def get_disabled_buttons(self) -> List[str]:
        """
        Get list of currently disabled button names.

        Returns:
            List of button names that are currently disabled
        """
        disabled = []
        all_buttons = list(
            dict.fromkeys(
                list(self._button_refs.keys()) + list(self._button_rules.keys())
            )
        )
        for button_name in all_buttons:
            if not self.should_enable_button(button_name):
                disabled.append(button_name)
        return disabled

    def debug_state(self) -> Dict[str, Any]:
        """
        Get current state information for debugging.

        Returns:
            Dictionary containing current state information
        """
        return {
            "registered_widgets": list(self._selection_widgets.keys()),
            "registered_buttons": list(self._button_refs.keys()),
            "button_rules": self._button_rules.copy(),
            "selections": {
                name: self.has_selection(name)
                for name in self._selection_widgets.keys()
            },
            "enabled_buttons": self.get_enabled_buttons(),
            "disabled_buttons": self.get_disabled_buttons(),
        }

    def should_enable_button(self, button_name: str) -> bool:
        """
        Check if a button should be enabled based on its rules.

        Args:
            button_name: Name of the button to check

        Returns:
            True if button should be enabled, False otherwise
        """
        rule = self._button_rules.get(button_name)
        if not rule:
            # No rule defined, default to enabled
            return True

        # Check 'always' condition - can be True or False
        if "always" in rule:
            return bool(rule["always"])

        # Check 'requires_edit_mode' condition
        if "requires_edit_mode" in rule:
            required_mode = rule["requires_edit_mode"]
            if self.is_edit_mode() != required_mode:
                return False

        # Check 'requires_check_all' condition
        if "requires_check_all" in rule:
            if not self.is_check_all():
                return False

        # Check 'disabled_in_edit_mode' condition
        if rule.get("disabled_in_edit_mode") and self.is_edit_mode():
            return False

        # Check 'enabled_with_check_all_or_selection' condition
        if rule.get("enabled_with_check_all_or_selection"):
            widget_name = rule["enabled_with_check_all_or_selection"]
            if not (self.is_check_all() or self.has_selection(widget_name)):
                return False

        # Check 'requires_selection' condition
        if "requires_selection" in rule:
            widget_name = rule["requires_selection"]
            if not self.has_selection(widget_name):
                return False

        # Check 'requires_parent' condition (for hierarchical widgets)
        if "requires_parent" in rule:
            parent_widget = rule["requires_parent"]
            if not self.has_selection(parent_widget):
                return False

        # Check 'requires_multiple' condition
        if "requires_multiple" in rule:
            widget_names = rule["requires_multiple"]
            for widget_name in widget_names:
                if not self.has_selection(widget_name):
                    return False

        # Check 'requires_context' condition
        if "requires_context" in rule:
            context_checks = rule["requires_context"]
            for key, expected_value in context_checks.items():
                actual_value = self._context.get(key)
                if actual_value != expected_value:
                    return False

        # Check 'custom' condition
        if "custom" in rule:
            custom_func = rule["custom"]
            if callable(custom_func):
                try:
                    # Pass context to custom function if it accepts it
                    import inspect

                    sig = inspect.signature(custom_func)
                    if len(sig.parameters) > 0:
                        return bool(custom_func(self._context))
                    else:
                        return bool(custom_func())
                except Exception as e:
                    if self._debug_mode:
                        self._logger.error(
                            f"Error in custom validation for {button_name}: {e}"
                        )
                    return False

        return True

    def update_button_states(self) -> None:
        """
        Update all registered buttons based on their rules.

        This method should be called after any state change that might
        affect button enablement (selection change, data load, etc.)
        """
        for button_name, button in self._button_refs.items():
            if not button or not button.winfo_exists():
                continue

            should_enable = self.should_enable_button(button_name)

            # Update button state
            try:
                if should_enable:
                    button.configure(state="normal")
                else:
                    button.configure(state="disabled")
            except tk.TclError:
                # Button might have been destroyed
                pass

    def bind_auto_update(
        self, widget_name: str, event: str = "<<TreeviewSelect>>"
    ) -> None:
        """
        Automatically update button states when widget selection changes.

        Args:
            widget_name: Name of the widget to bind to
            event: Event to bind (default: '<<TreeviewSelect>>' for Treeview)
        """
        widget = self._selection_widgets.get(widget_name)
        if not widget:
            return

        def on_selection_change(event=None):
            self.update_button_states()

        widget.bind(event, on_selection_change, add="+")

    def setup_hierarchical_buttons(
        self,
        parent_widget: str,
        child_widget: str,
        parent_buttons: Dict[str, Union[tk.Button, ttk.Button]],
        child_buttons: Dict[str, Union[tk.Button, ttk.Button]],
    ) -> None:
        """
        Convenience method for setting up hierarchical button management.

        This is useful for parent-child relationships like Monster-Template,
        Category-Item, etc.

        Args:
            parent_widget: Name of parent selection widget
            child_widget: Name of child selection widget
            parent_buttons: Dict of parent buttons {'add': btn, 'edit': btn, 'delete': btn}
            child_buttons: Dict of child buttons {'add': btn, 'edit': btn, 'delete': btn}

        Example:
            self.setup_hierarchical_buttons(
                parent_widget='monster_list',
                child_widget='template_list',
                parent_buttons={
                    'add': self.add_monster_btn,
                    'edit': self.edit_monster_btn,
                    'delete': self.delete_monster_btn
                },
                child_buttons={
                    'add': self.add_template_btn,
                    'edit': self.edit_template_btn,
                    'delete': self.delete_template_btn
                }
            )
        """
        # Register buttons
        for action, button in parent_buttons.items():
            btn_name = f"parent_{action}"
            self.register_button(btn_name, button)

        for action, button in child_buttons.items():
            btn_name = f"child_{action}"
            self.register_button(btn_name, button)

        # Setup rules
        rules = {
            "parent_add": {"always": True},
            "parent_edit": {"requires_selection": parent_widget},
            "parent_delete": {"requires_selection": parent_widget},
            "child_add": {"requires_parent": parent_widget},
            "child_edit": {"requires_selection": child_widget},
            "child_delete": {"requires_selection": child_widget},
        }

        self.register_button_rules(rules)

        # Bind auto updates
        self.bind_auto_update(parent_widget, "<<TreeviewSelect>>")
        self.bind_auto_update(child_widget, "<<TreeviewSelect>>")


if __name__ == "__main__":
    """Demo of ButtonStateMixin usage."""

    root = tk.Tk()
    root.title("ButtonStateMixin Demo")
    root.geometry("600x400")

    # Create a demo window
    class DemoWindow(tk.Frame, ButtonStateMixin):
        def __init__(self, parent):
            tk.Frame.__init__(self, parent)
            ButtonStateMixin.__init__(self)

            self.pack(fill="both", expand=True, padx=10, pady=10)

            # Create parent list
            parent_frame = tk.LabelFrame(self, text="Parent Items (Monster)")
            parent_frame.pack(fill="both", expand=True, pady=5)

            self.parent_tree = ttk.Treeview(parent_frame, show="tree")
            self.parent_tree.pack(side="left", fill="both", expand=True)

            parent_btn_frame = tk.Frame(parent_frame)
            parent_btn_frame.pack(side="right", fill="y", padx=5)

            self.add_parent_btn = tk.Button(
                parent_btn_frame, text="Add Parent", command=self.add_parent
            )
            self.add_parent_btn.pack(pady=2)

            self.edit_parent_btn = tk.Button(parent_btn_frame, text="Edit Parent")
            self.edit_parent_btn.pack(pady=2)

            self.del_parent_btn = tk.Button(parent_btn_frame, text="Delete Parent")
            self.del_parent_btn.pack(pady=2)

            # Create child list
            child_frame = tk.LabelFrame(self, text="Child Items (Template)")
            child_frame.pack(fill="both", expand=True, pady=5)

            self.child_tree = ttk.Treeview(child_frame, show="tree")
            self.child_tree.pack(side="left", fill="both", expand=True)

            child_btn_frame = tk.Frame(child_frame)
            child_btn_frame.pack(side="right", fill="y", padx=5)

            self.add_child_btn = tk.Button(child_btn_frame, text="Add Child")
            self.add_child_btn.pack(pady=2)

            self.edit_child_btn = tk.Button(child_btn_frame, text="Edit Child")
            self.edit_child_btn.pack(pady=2)

            self.del_child_btn = tk.Button(child_btn_frame, text="Delete Child")
            self.del_child_btn.pack(pady=2)

            # Setup button state management
            self.setup_button_management()

            # Initial state update
            self.update_button_states()

            # Add some demo data
            for i in range(1, 4):
                self.parent_tree.insert("", "end", f"parent_{i}", text=f"Parent {i}")

        def setup_button_management(self):
            """Setup button state management using the mixin."""
            # Register widgets
            self.register_selection_widget("parent_list", self.parent_tree)
            self.register_selection_widget("child_list", self.child_tree)

            # Use the convenience method for hierarchical setup
            self.setup_hierarchical_buttons(
                parent_widget="parent_list",
                child_widget="child_list",
                parent_buttons={
                    "add": self.add_parent_btn,
                    "edit": self.edit_parent_btn,
                    "delete": self.del_parent_btn,
                },
                child_buttons={
                    "add": self.add_child_btn,
                    "edit": self.edit_child_btn,
                    "delete": self.del_child_btn,
                },
            )

        def add_parent(self):
            """Demo add parent function."""
            import uuid

            # Use UUID to avoid duplicate IDs when clicking fast
            item_id = f"parent_{uuid.uuid4().hex[:8]}"
            self.parent_tree.insert("", "end", item_id, text=f"New Parent")
            self.parent_tree.selection_set(item_id)
            self.update_button_states()

    demo = DemoWindow(root)
    root.mainloop()
