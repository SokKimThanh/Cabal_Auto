"""
UI Mixins Package

Collection of reusable mixin classes for UI components.
These mixins provide common functionality that can be mixed into any Tkinter window.

Available Mixins:
- ButtonStateMixin: Automatic button state management based on selection
- (Future) NotificationMixin: Inline notification support
- (Future) DirtyStateMixin: Unsaved changes tracking
- (Future) ValidationMixin: Form validation helpers

Author: SokKimThanh
Date: 2025-10-25
"""

from ui.mixins.button_state_mixin import ButtonStateMixin

__all__ = [
    'ButtonStateMixin',
]
