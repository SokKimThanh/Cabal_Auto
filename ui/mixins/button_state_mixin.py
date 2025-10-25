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


class ButtonStateMixin:
    """
    Mixin class for automatic button state management.
    
    Features:
    - Centralized button state logic
    - Support for hierarchical dependencies (parent-child)
    - Custom validation functions
    - Automatic enable/disable based on selection
    - Easy integration with any Tkinter window
    
    Attributes:
        _button_rules: Dictionary mapping button names to their enable conditions
        _selection_widgets: Dictionary mapping widget names to widget instances
    """
    
    def __init__(self):
        """Initialize the button state mixin."""
        self._button_rules: Dict[str, Dict[str, Any]] = {}
        self._selection_widgets: Dict[str, Union[tk.Listbox, ttk.Treeview]] = {}
        self._button_refs: Dict[str, Union[tk.Button, ttk.Button]] = {}
        
    def register_button_rules(self, rules: Dict[str, Dict[str, Any]]) -> None:
        """
        Register button state rules.
        
        Args:
            rules: Dictionary mapping button names to their conditions.
                   Each condition can have:
                   - 'always': bool - Always enabled if True
                   - 'requires_selection': str - Requires selection in named widget
                   - 'requires_parent': str - Requires parent selection before enabling
                   - 'requires_multiple': List[str] - Requires selection in multiple widgets
                   - 'custom': Callable - Custom validation function returning bool
                   
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
        self._button_rules.update(rules)
        
    def register_selection_widget(self, name: str, widget: Union[tk.Listbox, ttk.Treeview]) -> None:
        """
        Register a selection widget (Listbox or Treeview).
        
        Args:
            name: Name to reference this widget in button rules
            widget: The widget instance
        """
        self._selection_widgets[name] = widget
        
    def register_button(self, name: str, button: Union[tk.Button, ttk.Button]) -> None:
        """
        Register a button widget for state management.
        
        Args:
            name: Name used in button rules
            button: The button widget instance
        """
        self._button_refs[name] = button
        
    def has_selection(self, widget_name: str) -> bool:
        """
        Check if a widget has selection.
        
        Args:
            widget_name: Name of the registered widget
            
        Returns:
            True if widget has selection, False otherwise
        """
        widget = self._selection_widgets.get(widget_name)
        if not widget:
            return False
            
        if isinstance(widget, ttk.Treeview):
            return bool(widget.selection())
        elif isinstance(widget, tk.Listbox):
            return bool(widget.curselection())
        else:
            return False
            
    def get_selection_value(self, widget_name: str) -> Optional[Any]:
        """
        Get the current selection value from a widget.
        
        Args:
            widget_name: Name of the registered widget
            
        Returns:
            Selected item ID/index or None if no selection
        """
        widget = self._selection_widgets.get(widget_name)
        if not widget:
            return None
            
        if isinstance(widget, ttk.Treeview):
            selection = widget.selection()
            return selection[0] if selection else None
        elif isinstance(widget, tk.Listbox):
            selection = widget.curselection()
            return selection[0] if selection else None
        else:
            return None
            
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
            
        # Check 'always' condition
        if rule.get('always'):
            return True
            
        # Check 'requires_selection' condition
        if 'requires_selection' in rule:
            widget_name = rule['requires_selection']
            if not self.has_selection(widget_name):
                return False
                
        # Check 'requires_parent' condition (for hierarchical widgets)
        if 'requires_parent' in rule:
            parent_widget = rule['requires_parent']
            if not self.has_selection(parent_widget):
                return False
                
        # Check 'requires_multiple' condition
        if 'requires_multiple' in rule:
            widget_names = rule['requires_multiple']
            for widget_name in widget_names:
                if not self.has_selection(widget_name):
                    return False
                    
        # Check 'custom' condition
        if 'custom' in rule:
            custom_func = rule['custom']
            if callable(custom_func):
                try:
                    return bool(custom_func())
                except Exception as e:
                    print(f"[ButtonStateMixin] Error in custom validation for {button_name}: {e}")
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
                    button.configure(state='normal')
                else:
                    button.configure(state='disabled')
            except tk.TclError:
                # Button might have been destroyed
                pass
                
    def bind_auto_update(self, widget_name: str, event: str = '<<TreeviewSelect>>') -> None:
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
            
        widget.bind(event, on_selection_change, add='+')
        
    def setup_hierarchical_buttons(
        self,
        parent_widget: str,
        child_widget: str,
        parent_buttons: Dict[str, Union[tk.Button, ttk.Button]],
        child_buttons: Dict[str, Union[tk.Button, ttk.Button]]
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
            btn_name = f'parent_{action}'
            self.register_button(btn_name, button)
            
        for action, button in child_buttons.items():
            btn_name = f'child_{action}'
            self.register_button(btn_name, button)
            
        # Setup rules
        rules = {
            'parent_add': {'always': True},
            'parent_edit': {'requires_selection': parent_widget},
            'parent_delete': {'requires_selection': parent_widget},
            'child_add': {'requires_parent': parent_widget},
            'child_edit': {'requires_selection': child_widget},
            'child_delete': {'requires_selection': child_widget},
        }
        
        self.register_button_rules(rules)
        
        # Bind auto updates
        self.bind_auto_update(parent_widget, '<<TreeviewSelect>>')
        self.bind_auto_update(child_widget, '<<TreeviewSelect>>')


if __name__ == '__main__':
    """Demo of ButtonStateMixin usage."""
    
    root = tk.Tk()
    root.title("ButtonStateMixin Demo")
    root.geometry("600x400")
    
    # Create a demo window
    class DemoWindow(tk.Frame, ButtonStateMixin):
        def __init__(self, parent):
            tk.Frame.__init__(self, parent)
            ButtonStateMixin.__init__(self)
            
            self.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Create parent list
            parent_frame = tk.LabelFrame(self, text="Parent Items (Monster)")
            parent_frame.pack(fill='both', expand=True, pady=5)
            
            self.parent_tree = ttk.Treeview(parent_frame, show='tree')
            self.parent_tree.pack(side='left', fill='both', expand=True)
            
            parent_btn_frame = tk.Frame(parent_frame)
            parent_btn_frame.pack(side='right', fill='y', padx=5)
            
            self.add_parent_btn = tk.Button(parent_btn_frame, text="Add Parent", command=self.add_parent)
            self.add_parent_btn.pack(pady=2)
            
            self.edit_parent_btn = tk.Button(parent_btn_frame, text="Edit Parent")
            self.edit_parent_btn.pack(pady=2)
            
            self.del_parent_btn = tk.Button(parent_btn_frame, text="Delete Parent")
            self.del_parent_btn.pack(pady=2)
            
            # Create child list
            child_frame = tk.LabelFrame(self, text="Child Items (Template)")
            child_frame.pack(fill='both', expand=True, pady=5)
            
            self.child_tree = ttk.Treeview(child_frame, show='tree')
            self.child_tree.pack(side='left', fill='both', expand=True)
            
            child_btn_frame = tk.Frame(child_frame)
            child_btn_frame.pack(side='right', fill='y', padx=5)
            
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
                self.parent_tree.insert('', 'end', f'parent_{i}', text=f'Parent {i}')
                
        def setup_button_management(self):
            """Setup button state management using the mixin."""
            # Register widgets
            self.register_selection_widget('parent_list', self.parent_tree)
            self.register_selection_widget('child_list', self.child_tree)
            
            # Use the convenience method for hierarchical setup
            self.setup_hierarchical_buttons(
                parent_widget='parent_list',
                child_widget='child_list',
                parent_buttons={
                    'add': self.add_parent_btn,
                    'edit': self.edit_parent_btn,
                    'delete': self.del_parent_btn
                },
                child_buttons={
                    'add': self.add_child_btn,
                    'edit': self.edit_child_btn,
                    'delete': self.del_child_btn
                }
            )
            
        def add_parent(self):
            """Demo add parent function."""
            import uuid
            # Use UUID to avoid duplicate IDs when clicking fast
            item_id = f'parent_{uuid.uuid4().hex[:8]}'
            self.parent_tree.insert('', 'end', item_id, text=f'New Parent')
            self.parent_tree.selection_set(item_id)
            self.update_button_states()
    
    demo = DemoWindow(root)
    root.mainloop()
