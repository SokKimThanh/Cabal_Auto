"""
Action-Notification Integration Example

Demonstrates how to integrate ButtonStateMixin with NotificationWidget
using the ActionNotificationMixin to provide consistent user feedback.

This example shows:
1. Button state management (enabled/disabled based on conditions)
2. Action validation with notifications (warning before action)
3. Success/error feedback (notification after action)
4. Confirmation prompts (for destructive actions)
5. Clear separation between button state and notification state

Run this example:
    python examples/action_notification_integration.py
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Add project root to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from ui.mixins.button_state_mixin import ButtonStateMixin
from ui.mixins.action_notification_mixin import ActionNotificationMixin
from ui.components.notification_widget import NotificationWidget


class SimpleTaskManager(ButtonStateMixin, ActionNotificationMixin, tk.Tk):
    """
    Simple task manager demonstrating button-notification integration.
    
    Features:
    - Add/Edit/Delete tasks
    - Edit mode toggle
    - Check All support
    - Automatic validation notifications
    - Success/error feedback
    - Confirmation for destructive actions
    """
    
    def __init__(self):
        # Initialize Tk first
        tk.Tk.__init__(self)
        # Initialize mixins
        ButtonStateMixin.__init__(self, debug_mode=True)
        ActionNotificationMixin.__init__(self, debug_mode=True)
        
        self.title("Task Manager - Action-Notification Integration")
        self.geometry("600x500")
        
        # Data
        self.tasks = []
        
        # Create UI
        self._create_ui()
        
        # Register button state rules
        self._register_button_rules()
        
        # Register action notification rules
        self._register_action_rules()
        
        # Show welcome message
        self.after(100, lambda: self.notification_widget.show_info(
            "Welcome! Switch to Edit Mode to add/edit/delete tasks."
        ))
    
    def _create_ui(self):
        """Create the UI layout."""
        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(
            main_frame,
            text="📋 Task Manager",
            font=('Arial', 16, 'bold')
        )
        title.pack(pady=(0, 10))
        
        # Notification area
        self.notification_widget = NotificationWidget(
            main_frame,
            auto_hide_seconds=3
        )
        self.notification_widget.pack(fill='x', pady=(0, 10))
        self.notification_widget.hide()  # Hide initially
        
        # Set notification widget for mixin
        self.set_notification_widget(self.notification_widget)
        
        # Mode controls
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill='x', pady=(0, 10))
        
        self.view_mode_btn = ttk.Button(
            mode_frame,
            text="📖 View Mode",
            command=self._set_view_mode
        )
        self.view_mode_btn.pack(side='left', padx=(0, 5))
        
        self.edit_mode_btn = ttk.Button(
            mode_frame,
            text="✏️ Edit Mode",
            command=self._set_edit_mode
        )
        self.edit_mode_btn.pack(side='left', padx=(0, 5))
        
        # Check All
        self.check_all_var = tk.BooleanVar(value=False)
        self.check_all_cb = ttk.Checkbutton(
            mode_frame,
            text="Check All",
            variable=self.check_all_var,
            command=self._on_check_all_changed
        )
        self.check_all_cb.pack(side='left', padx=(20, 0))
        
        # Status
        self.status_label = ttk.Label(
            mode_frame,
            text="Mode: View | Selection: None",
            foreground='blue'
        )
        self.status_label.pack(side='right')
        
        # Task list
        list_frame = ttk.LabelFrame(main_frame, text="Tasks", padding=5)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.task_list = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.task_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.task_list.yview)
        
        # Bind selection event
        self.task_list.bind('<<ListboxSelect>>', self._on_task_selected)
        
        # Button panel
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        self.add_btn = ttk.Button(
            button_frame,
            text="➕ Add Task",
            command=lambda: self.execute_action('add_task', self._do_add_task)
        )
        self.add_btn.pack(side='left', padx=(0, 5))
        
        self.edit_btn = ttk.Button(
            button_frame,
            text="✏️ Edit Task",
            command=lambda: self.execute_action('edit_task', self._do_edit_task)
        )
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ttk.Button(
            button_frame,
            text="🗑️ Delete Task",
            command=lambda: self.execute_action('delete_task', self._do_delete_task)
        )
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        self.complete_btn = ttk.Button(
            button_frame,
            text="✓ Mark Complete",
            command=lambda: self.execute_action('complete_task', self._do_complete_task)
        )
        self.complete_btn.pack(side='left', padx=(0, 5))
        
        # Register widgets with ButtonStateMixin
        self.register_selection_widget('tasks', self.task_list)
        self.register_button('view_mode', self.view_mode_btn)
        self.register_button('edit_mode', self.edit_mode_btn)
        self.register_button('add', self.add_btn)
        self.register_button('edit', self.edit_btn)
        self.register_button('delete', self.delete_btn)
        self.register_button('complete', self.complete_btn)
    
    def _register_button_rules(self):
        """Register button state rules (technical conditions)."""
        self.register_button_rules({
            'view_mode': {'always': True},
            'edit_mode': {'always': True},
            'add': {'requires_edit_mode': True},
            'edit': {
                'requires_edit_mode': True,
                'requires_selection': 'tasks'
            },
            'delete': {
                'requires_edit_mode': True,
                'enabled_with_check_all_or_selection': 'tasks'
            },
            'complete': {
                'requires_selection': 'tasks'
            }
        })
    
    def _register_action_rules(self):
        """Register action notification rules (user feedback)."""
        self.register_action_rules({
            'add_task': {
                'validation': {
                    'check': lambda: self.is_edit_mode(),
                    'message': "⚠️ Please enable Edit Mode first to add tasks",
                    'type': 'warning'
                },
                'success': {
                    'message': "✅ Task added successfully!",
                    'type': 'success'
                },
                'error': {
                    'message': "❌ Failed to add task: {error}",
                    'type': 'error'
                }
            },
            'edit_task': {
                'validation': {
                    'check': lambda: self.is_edit_mode() and self.has_selection('tasks'),
                    'message': "⚠️ Please enable Edit Mode and select a task to edit",
                    'type': 'warning'
                },
                'success': {
                    'message': "✅ Task updated successfully!",
                    'type': 'success'
                },
                'error': {
                    'message': "❌ Failed to update task: {error}",
                    'type': 'error'
                }
            },
            'delete_task': {
                'validation': {
                    'check': lambda: self.is_edit_mode() and (self.has_selection('tasks') or self.is_check_all()),
                    'message': "⚠️ Please enable Edit Mode and select a task or enable Check All",
                    'type': 'warning'
                },
                'confirmation': {
                    'check': lambda: self.is_check_all() and len(self.tasks) > 1,
                    'message': f"This will delete ALL {len(self.tasks) if hasattr(self, 'tasks') else 0} tasks. Are you sure?",
                    'type': 'warning'
                },
                'success': {
                    'message': "✅ Task(s) deleted successfully!",
                    'type': 'success'
                },
                'error': {
                    'message': "❌ Failed to delete task: {error}",
                    'type': 'error'
                }
            },
            'complete_task': {
                'validation': {
                    'check': lambda: self.has_selection('tasks'),
                    'message': "⚠️ Please select a task to mark as complete",
                    'type': 'warning'
                },
                'success': {
                    'message': "✅ Task marked as complete!",
                    'type': 'success'
                },
                'error': {
                    'message': "❌ Failed to mark task complete: {error}",
                    'type': 'error'
                }
            }
        })
    
    # Action implementations
    
    def _do_add_task(self):
        """Add a new task."""
        task_name = f"Task {len(self.tasks) + 1}"
        self.tasks.append({'name': task_name, 'completed': False})
        self.task_list.insert('end', f"[ ] {task_name}")
        return task_name
    
    def _do_edit_task(self):
        """Edit selected task."""
        selection = self.task_list.curselection()
        if not selection:
            raise ValueError("No task selected")
        
        idx = selection[0]
        task = self.tasks[idx]
        
        # Simple edit: add " (edited)" suffix
        task['name'] += " (edited)"
        prefix = "[✓] " if task['completed'] else "[ ] "
        self.task_list.delete(idx)
        self.task_list.insert(idx, f"{prefix}{task['name']}")
        self.task_list.selection_set(idx)
        
        return task['name']
    
    def _do_delete_task(self):
        """Delete selected task(s) or all if Check All."""
        if self.is_check_all():
            # Delete all
            count = len(self.tasks)
            self.tasks.clear()
            self.task_list.delete(0, 'end')
            return f"{count} tasks"
        else:
            # Delete selected
            selection = self.task_list.curselection()
            if not selection:
                raise ValueError("No task selected")
            
            idx = selection[0]
            task = self.tasks.pop(idx)
            self.task_list.delete(idx)
            return task['name']
    
    def _do_complete_task(self):
        """Mark selected task as complete."""
        selection = self.task_list.curselection()
        if not selection:
            raise ValueError("No task selected")
        
        idx = selection[0]
        task = self.tasks[idx]
        task['completed'] = True
        
        # Update display
        self.task_list.delete(idx)
        self.task_list.insert(idx, f"[✓] {task['name']}")
        self.task_list.selection_set(idx)
        
        return task['name']
    
    # Event handlers
    
    def _set_view_mode(self):
        """Switch to view mode."""
        self.set_edit_mode(False)
        self._update_status()
        self.notification_widget.show_info("📖 Switched to View Mode")
    
    def _set_edit_mode(self):
        """Switch to edit mode."""
        self.set_edit_mode(True)
        self._update_status()
        self.notification_widget.show_info("✏️ Switched to Edit Mode")
    
    def _on_check_all_changed(self):
        """Handle Check All checkbox change."""
        self.set_check_all(self.check_all_var.get())
        self._update_status()
    
    def _on_task_selected(self, event):
        """Handle task selection change."""
        self.update_button_states()
        self._update_status()
    
    def _update_status(self):
        """Update status label."""
        mode = "Edit" if self.is_edit_mode() else "View"
        
        if self.is_check_all():
            selection = f"Check All ({len(self.tasks)} tasks)"
        else:
            sel = self.task_list.curselection()
            if sel:
                task = self.tasks[sel[0]]
                selection = f"Selected: {task['name']}"
            else:
                selection = "None"
        
        self.status_label.config(text=f"Mode: {mode} | Selection: {selection}")


def main():
    """Run the example."""
    print("="*70)
    print("🎮 Task Manager - Action-Notification Integration Example")
    print("="*70)
    print()
    print("📖 Features Demonstrated:")
    print("  1. Button State Management (ButtonStateMixin)")
    print("     • Buttons enabled/disabled based on conditions")
    print("     • Edit mode vs View mode")
    print("     • Check All support")
    print()
    print("  2. Notification Integration (ActionNotificationMixin)")
    print("     • Validation warnings before action")
    print("     • Success feedback after action")
    print("     • Error handling with user-friendly messages")
    print("     • Confirmation prompts for destructive actions")
    print()
    print("🎯 Try This:")
    print("  • Try to Add/Edit/Delete in View Mode → See validation warning")
    print("  • Switch to Edit Mode → Buttons enable")
    print("  • Add a task → See success notification")
    print("  • Select a task and Edit → See update notification")
    print("  • Enable Check All and Delete → See confirmation prompt")
    print("  • Mark task complete (works in any mode)")
    print()
    print("✨ Key Concept:")
    print("  • Button State = Technical condition (BEFORE action)")
    print("  • Notification = User feedback (AFTER action)")
    print("  • Two separate systems working together!")
    print()
    print("="*70)
    print()
    
    app = SimpleTaskManager()
    app.mainloop()


if __name__ == '__main__':
    main()
