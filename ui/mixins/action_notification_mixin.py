"""
Action-Notification Integration Mixin

Provides a rule-based system to automatically trigger notifications based on
button actions and their results. This mixin bridges ButtonStateMixin and
NotificationWidget to provide consistent user feedback.

Key Concepts:
1. Button State = Technical condition (enabled/disabled) - BEFORE action
2. Notification = User feedback (info/success/warning/error) - AFTER action
3. This mixin = Integration layer that connects them

When does a button trigger a notification?
1. Validation Error: User clicks but conditions not met
   Example: Click "Edit" without selection → Warning "Please select an item"

2. Action Result: Operation succeeds or fails
   Example: Save success → Success "Saved successfully"
            Save fails → Error "Failed to save: [reason]"

3. Confirmation Needed: Action affects related data
   Example: Delete monster with templates → Confirm "This will delete all templates too"

Usage:
    from ui.mixins.button_state_mixin import ButtonStateMixin
    from ui.mixins.action_notification_mixin import ActionNotificationMixin
    from ui.components.notification_widget import NotificationWidget
    
    class MyEditor(ButtonStateMixin, ActionNotificationMixin, tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            
            # Setup notification widget
            self.notification_widget = NotificationWidget(self)
            
            # Register action rules
            self.register_action_rules({
                'add_monster': {
                    'validation': {
                        'check': lambda: self.is_edit_mode(),
                        'message': "Please enable Edit Mode first",
                        'type': 'warning'
                    },
                    'success': {
                        'message': "Monster added successfully",
                        'type': 'success'
                    },
                    'error': {
                        'message': "Failed to add monster: {error}",
                        'type': 'error'
                    }
                },
                'delete_monster': {
                    'confirmation': {
                        'check': lambda: self.has_templates(),
                        'message': "This will delete all templates. Continue?",
                        'type': 'warning'
                    },
                    'validation': {
                        'check': lambda: self.get_selected('monsters') or self.is_check_all(),
                        'message': "Please select a monster or enable Check All",
                        'type': 'warning'
                    },
                    'success': {
                        'message': "Monster deleted successfully",
                        'type': 'success'
                    }
                }
            })
            
            # Execute action with automatic notification
            self.execute_action('add_monster', self._do_add_monster)

Features:
- Automatic validation before action
- Success/error feedback after action
- Confirmation prompts for destructive actions
- Integrates seamlessly with ButtonStateMixin
- Uses NotificationWidget for consistent UI
- Clear rule-based configuration
"""

import logging
from typing import Callable, Dict, Optional, Any, Literal
import inspect

# Type aliases
NotificationType = Literal['info', 'success', 'warning', 'error']
ActionResult = tuple[bool, Optional[str]]  # (success, error_message)


class ActionNotificationMixin:
    """
    Mixin for integrating button actions with notification feedback.
    
    This mixin provides a rule-based system to automatically trigger notifications
    based on button actions and their results.
    
    Features:
    - Pre-action validation with notifications
    - Post-action success/error feedback
    - Confirmation prompts for destructive actions
    - Flexible rule configuration
    - Integration with NotificationWidget
    
    Attributes:
        _action_rules: Dictionary mapping action names to their notification rules
        _notification_widget: NotificationWidget instance for displaying messages
        _logger: Logger instance for debugging
    """
    
    def __init__(self, *args, debug_mode=False, **kwargs):
        """Initialize action-notification tracking."""
        # Only call super().__init__ if it won't cause issues
        # (Mixins should be cooperative but defensive)
        if hasattr(super(), '__init__'):
            try:
                super().__init__(*args, **kwargs)
            except TypeError:
                # If kwargs not accepted, try without them
                pass
        
        # Action notification rules: {action_name: {validation: {...}, success: {...}, error: {...}}}
        self._action_rules: Dict[str, Dict[str, Any]] = {}
        
        # Reference to notification widget (should be set by subclass)
        self._notification_widget = None
        
        # Logger setup
        self._logger = logging.getLogger(self.__class__.__module__)
        self._debug_mode = debug_mode
    
    def set_notification_widget(self, widget) -> None:
        """
        Set the notification widget for displaying messages.
        
        Args:
            widget: NotificationWidget instance
            
        Example:
            from ui.components.notification_widget import NotificationWidget
            notification = NotificationWidget(self)
            self.set_notification_widget(notification)
        """
        self._notification_widget = widget
        if self._debug_mode:
            self._logger.debug(f"Notification widget set: {type(widget).__name__}")
    
    def register_action_rules(self, rules: Dict[str, Dict[str, Any]]) -> None:
        """
        Register notification rules for button actions.
        
        Args:
            rules: Dictionary mapping action names to their notification rules.
                   Each action can have:
                   - 'validation': Pre-action check with notification
                     * 'check': Callable returning bool
                     * 'message': Notification message if check fails
                     * 'type': Notification type (default: 'warning')
                   - 'confirmation': Ask user before proceeding
                     * 'check': Callable returning bool (when to ask)
                     * 'message': Confirmation prompt
                     * 'type': Notification type (default: 'warning')
                   - 'success': Post-action success notification
                     * 'message': Success message (can use {result} placeholder)
                     * 'type': Notification type (default: 'success')
                   - 'error': Post-action error notification
                     * 'message': Error message (can use {error} placeholder)
                     * 'type': Notification type (default: 'error')
                   
        Raises:
            TypeError: If rules is not a dictionary
            ValueError: If rule format is invalid
            
        Example:
            self.register_action_rules({
                'add_monster': {
                    'validation': {
                        'check': lambda: self.is_edit_mode(),
                        'message': "Please enable Edit Mode first",
                        'type': 'warning'
                    },
                    'success': {
                        'message': "Monster added successfully",
                        'type': 'success'
                    },
                    'error': {
                        'message': "Failed to add monster: {error}",
                        'type': 'error'
                    }
                },
                'delete_monster': {
                    'confirmation': {
                        'check': lambda: self.has_templates(),
                        'message': "This will delete all templates. Continue?",
                        'type': 'warning'
                    },
                    'validation': {
                        'check': lambda: self.has_selection('monsters'),
                        'message': "Please select a monster first",
                        'type': 'warning'
                    },
                    'success': {
                        'message': "Monster deleted successfully"
                    }
                }
            })
        """
        if not isinstance(rules, dict):
            raise TypeError(f"rules must be a dictionary, got {type(rules).__name__}")
        
        # Validate each rule
        valid_rule_types = {'validation', 'confirmation', 'success', 'error'}
        valid_notification_types = {'info', 'success', 'warning', 'error'}
        
        for action_name, action_rules in rules.items():
            if not isinstance(action_rules, dict):
                raise ValueError(f"Rules for '{action_name}' must be a dictionary, got {type(action_rules).__name__}")
            
            # Check for unknown rule types
            unknown_types = set(action_rules.keys()) - valid_rule_types
            if unknown_types:
                self._logger.warning(f"Unknown rule types for '{action_name}': {unknown_types}")
            
            # Validate validation rule
            if 'validation' in action_rules:
                val_rule = action_rules['validation']
                if not isinstance(val_rule, dict):
                    raise ValueError(f"'validation' rule for '{action_name}' must be a dictionary")
                if 'check' not in val_rule or not callable(val_rule['check']):
                    raise ValueError(f"'validation' rule for '{action_name}' must have a callable 'check'")
                if 'message' not in val_rule or not isinstance(val_rule['message'], str):
                    raise ValueError(f"'validation' rule for '{action_name}' must have a string 'message'")
                if 'type' in val_rule and val_rule['type'] not in valid_notification_types:
                    raise ValueError(f"Invalid notification type for '{action_name}': {val_rule['type']}")
            
            # Validate confirmation rule
            if 'confirmation' in action_rules:
                conf_rule = action_rules['confirmation']
                if not isinstance(conf_rule, dict):
                    raise ValueError(f"'confirmation' rule for '{action_name}' must be a dictionary")
                if 'check' not in conf_rule or not callable(conf_rule['check']):
                    raise ValueError(f"'confirmation' rule for '{action_name}' must have a callable 'check'")
                if 'message' not in conf_rule or not isinstance(conf_rule['message'], str):
                    raise ValueError(f"'confirmation' rule for '{action_name}' must have a string 'message'")
            
            # Validate success/error rules
            for rule_type in ['success', 'error']:
                if rule_type in action_rules:
                    rule = action_rules[rule_type]
                    if not isinstance(rule, dict):
                        raise ValueError(f"'{rule_type}' rule for '{action_name}' must be a dictionary")
                    if 'message' not in rule or not isinstance(rule['message'], str):
                        raise ValueError(f"'{rule_type}' rule for '{action_name}' must have a string 'message'")
                    if 'type' in rule and rule['type'] not in valid_notification_types:
                        raise ValueError(f"Invalid notification type for '{action_name}': {rule['type']}")
        
        self._action_rules.update(rules)
        
        if self._debug_mode:
            self._logger.debug(f"Registered {len(rules)} action rules")
    
    def execute_action(
        self,
        action_name: str,
        action_callback: Callable,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute an action with automatic notification feedback.
        
        This method handles the complete action lifecycle:
        1. Validation: Check pre-conditions and show warning if failed
        2. Confirmation: Ask user if needed (for destructive actions)
        3. Execution: Run the actual action callback
        4. Feedback: Show success or error notification based on result
        
        Args:
            action_name: Name of the action (must be registered in action_rules)
            action_callback: The actual action function to execute
            *args: Positional arguments to pass to action_callback
            **kwargs: Keyword arguments to pass to action_callback
            
        Returns:
            Result from action_callback if successful, None if failed/cancelled
            
        Raises:
            ValueError: If action_name is not registered or notification widget not set
            
        Example:
            def _do_add_monster(self):
                # Actual implementation
                monster = Monster(name="New Monster")
                self.monsters.append(monster)
                return monster
            
            # Execute with automatic notifications
            result = self.execute_action('add_monster', self._do_add_monster)
        """
        if action_name not in self._action_rules:
            raise ValueError(f"Action '{action_name}' is not registered. Call register_action_rules() first.")
        
        if self._notification_widget is None:
            raise ValueError("Notification widget not set. Call set_notification_widget() first.")
        
        rules = self._action_rules[action_name]
        
        # 1. Validation check
        if 'validation' in rules:
            val_rule = rules['validation']
            try:
                if not val_rule['check']():
                    # Validation failed - show notification and return
                    msg_type = val_rule.get('type', 'warning')
                    self._show_notification(val_rule['message'], msg_type)
                    if self._debug_mode:
                        self._logger.debug(f"Action '{action_name}' validation failed")
                    return None
            except Exception as e:
                self._logger.error(f"Validation check error for '{action_name}': {e}")
                self._show_notification(f"Validation error: {e}", 'error')
                return None
        
        # 2. Confirmation check (for destructive actions)
        if 'confirmation' in rules:
            conf_rule = rules['confirmation']
            try:
                if conf_rule['check']():
                    # Need confirmation - show messagebox
                    from tkinter import messagebox
                    confirmed = messagebox.askyesno(
                        "Confirmation",
                        conf_rule['message'],
                        parent=self if hasattr(self, 'winfo_toplevel') else None
                    )
                    if not confirmed:
                        if self._debug_mode:
                            self._logger.debug(f"Action '{action_name}' cancelled by user")
                        return None
            except Exception as e:
                self._logger.error(f"Confirmation check error for '{action_name}': {e}")
                # Continue anyway if confirmation check fails
        
        # 3. Execute action
        try:
            result = action_callback(*args, **kwargs)
            
            # 4. Success notification
            if 'success' in rules:
                success_rule = rules['success']
                message = success_rule['message'].format(result=result)
                msg_type = success_rule.get('type', 'success')
                self._show_notification(message, msg_type)
            
            if self._debug_mode:
                self._logger.debug(f"Action '{action_name}' completed successfully")
            
            return result
            
        except Exception as e:
            # 4. Error notification
            if 'error' in rules:
                error_rule = rules['error']
                message = error_rule['message'].format(error=str(e))
                msg_type = error_rule.get('type', 'error')
                self._show_notification(message, msg_type)
            else:
                # Default error notification if no rule defined
                self._show_notification(f"Action failed: {e}", 'error')
            
            self._logger.error(f"Action '{action_name}' failed: {e}")
            return None
    
    def _show_notification(self, message: str, msg_type: NotificationType = 'info') -> None:
        """
        Show notification using the notification widget.
        
        Args:
            message: Notification message
            msg_type: Type of notification (info/success/warning/error)
        """
        if self._notification_widget is None:
            self._logger.warning(f"Cannot show notification: widget not set. Message: {message}")
            return
        
        # Call appropriate method on notification widget
        method_name = f'show_{msg_type}'
        if hasattr(self._notification_widget, method_name):
            method = getattr(self._notification_widget, method_name)
            method(message)
        else:
            self._logger.warning(f"Notification widget doesn't have method: {method_name}")
    
    def get_action_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered action rules.
        
        Returns:
            Dictionary of action rules
        """
        return self._action_rules.copy()
    
    def has_action_rule(self, action_name: str) -> bool:
        """
        Check if an action has registered rules.
        
        Args:
            action_name: Name of the action
            
        Returns:
            True if action has rules, False otherwise
        """
        return action_name in self._action_rules
