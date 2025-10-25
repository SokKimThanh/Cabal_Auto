"""
Inline Confirmation Widget

A reusable confirmation widget that displays Yes/No buttons inline 
without using popup dialogs. Provides a non-intrusive way to confirm 
user actions.

Features:
- Icon-only buttons (accept/cancel)
- Auto-hide after timeout
- Customizable callback
- Lightweight and reusable
- No popup interruption

Usage:
    from ui.components.confirmation_widget import ConfirmationWidget
    
    # Create widget
    confirmation = ConfirmationWidget(
        parent=some_frame,
        on_confirm=lambda: print("Confirmed!"),
        on_cancel=lambda: print("Cancelled"),
        auto_hide_seconds=5,
        bg='#F2F2F2'
    )
    
    # Show confirmation
    confirmation.show()
    
    # Or hide manually
    confirmation.hide()
"""

import tkinter as tk
from typing import Callable, Optional, Literal

try:
    from ui.components.create_icon_button import create_icon_button
except ImportError:
    from create_icon_button import create_icon_button

try:
    from lib.i18n import i18n_t
except ImportError:
    # Fallback if i18n not available
    def i18n_t(key: str, ns: str = '', default: str = '') -> str:
        return default or key


class ConfirmationWidget(tk.Frame):
    """
    Inline confirmation widget with Yes/No buttons.
    
    Displays two icon-only buttons (accept/cancel) that allow users to
    confirm or cancel an action without using popup dialogs.
    
    Attributes:
        on_confirm: Callback function to execute when Yes is clicked
        on_cancel: Optional callback function when No is clicked
        auto_hide_seconds: Seconds before auto-hiding (0 = no auto-hide)
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_confirm: Callable[[], None],
        on_cancel: Optional[Callable[[], None]] = None,
        auto_hide_seconds: int = 5,
        bg: str = '#F2F2F2',
        **kwargs
    ):
        """
        Initialize confirmation widget.
        
        Args:
            parent: Parent widget
            on_confirm: Function to call when Yes button is clicked
            on_cancel: Optional function to call when No button is clicked
            auto_hide_seconds: Auto-hide timeout in seconds (0 = disabled)
            bg: Background color (default: light gray)
            **kwargs: Additional Frame arguments
        """
        super().__init__(parent, bg=bg, relief='flat', bd=1, **kwargs)
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.auto_hide_seconds = auto_hide_seconds
        self._auto_hide_id: Optional[str] = None
        
        self._create_widgets()
        
        # Initially hidden
        self.pack_forget()
    
    def _create_widgets(self) -> None:
        """Create Yes/No buttons."""
        # Yes button (accept icon - green)
        self.yes_button = create_icon_button(
            self,
            icon_name='accept',
            icon_fallback='✓',
            icon_size=16,
            command=self._on_yes_clicked,
            button_type='green_light',
            variant='icon_only',
            width=20,
            height=20,
            tooltip_key='tooltip_confirm_yes',
            tooltip_ns='monster_editor'
        )
        self.yes_button.pack(side='left', padx=2, pady=2)
        
        # No button (cancel icon - gray)
        self.no_button = create_icon_button(
            self,
            icon_name='cancel',
            icon_fallback='✗',
            icon_size=16,
            command=self._on_no_clicked,
            button_type='secondary',
            variant='icon_only',
            width=20,
            height=20,
            tooltip_key='tooltip_confirm_no',
            tooltip_ns='monster_editor'
        )
        self.no_button.pack(side='left', padx=2, pady=2)
    
    def _on_yes_clicked(self) -> None:
        """Handle Yes button click."""
        try:
            # Execute confirm callback
            if self.on_confirm:
                self.on_confirm()
        except Exception as e:
            print(f"[ConfirmationWidget] Error in confirm callback: {e}")
        finally:
            # Always hide after action
            self.hide()
    
    def _on_no_clicked(self) -> None:
        """Handle No button click."""
        try:
            # Execute cancel callback if provided
            if self.on_cancel:
                self.on_cancel()
        except Exception as e:
            print(f"[ConfirmationWidget] Error in cancel callback: {e}")
        finally:
            # Always hide after action
            self.hide()
    
    def show(self, side: Literal['left', 'right', 'top', 'bottom'] = 'left', padx: tuple = (0, 5), pady: int = 0) -> None:
        """
        Show the confirmation widget.
        
        Args:
            side: Pack side ('left', 'right', 'top', 'bottom')
            padx: Horizontal padding
            pady: Vertical padding
        """
        # Cancel previous auto-hide timer if exists
        self._cancel_auto_hide()
        
        # Show widget
        if not self.winfo_ismapped():
            self.pack(side=side, padx=padx, pady=pady)  # type: ignore
        
        # Start auto-hide timer if enabled
        if self.auto_hide_seconds > 0:
            self._auto_hide_id = self.after(
                self.auto_hide_seconds * 1000,
                self.hide
            )
    
    def hide(self) -> None:
        """Hide the confirmation widget."""
        # Cancel auto-hide timer
        self._cancel_auto_hide()
        
        # Hide widget
        if self.winfo_ismapped():
            self.pack_forget()
    
    def _cancel_auto_hide(self) -> None:
        """Cancel auto-hide timer if active."""
        if self._auto_hide_id:
            self.after_cancel(self._auto_hide_id)
            self._auto_hide_id = None
    
    def is_visible(self) -> bool:
        """Check if widget is currently visible."""
        return self.winfo_ismapped()
    
    def set_confirm_callback(self, callback: Callable[[], None]) -> None:
        """Update the confirm callback function."""
        self.on_confirm = callback
    
    def set_cancel_callback(self, callback: Optional[Callable[[], None]]) -> None:
        """Update the cancel callback function."""
        self.on_cancel = callback
    
    def destroy(self) -> None:
        """Clean up resources before destroying."""
        self._cancel_auto_hide()
        super().destroy()


# Example usage and testing
if __name__ == "__main__":
    def test_confirmation_widget():
        """Test the confirmation widget."""
        root = tk.Tk()
        root.title("Confirmation Widget Test")
        root.geometry("400x300")
        
        # Create container
        container = tk.Frame(root, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Status label
        status_label = tk.Label(
            container,
            text="Click 'Show Confirmation' to test",
            font=('Arial', 12),
            bg='white'
        )
        status_label.pack(pady=10)
        
        # Create confirmation widget
        def on_confirm():
            status_label.config(text="✓ Confirmed!", fg='green')
        
        def on_cancel():
            status_label.config(text="✗ Cancelled", fg='red')
        
        confirmation = ConfirmationWidget(
            container,
            on_confirm=on_confirm,
            on_cancel=on_cancel,
            auto_hide_seconds=5,
            bg='#F2F2F2'
        )
        confirmation.pack(pady=10)
        
        # Test button
        def show_test():
            status_label.config(text="Waiting for confirmation...", fg='orange')
            confirmation.show()
        
        test_button = tk.Button(
            container,
            text="Show Confirmation",
            command=show_test,
            bg='#007ACC',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10
        )
        test_button.pack(pady=10)
        
        # Info text
        info_text = tk.Label(
            container,
            text="Auto-hides after 5 seconds if no action taken",
            font=('Arial', 9),
            fg='gray',
            bg='white'
        )
        info_text.pack(pady=5)
        
        root.mainloop()
    
    test_confirmation_widget()
