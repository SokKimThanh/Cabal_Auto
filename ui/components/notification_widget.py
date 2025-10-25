"""
Inline Notification Widget

A reusable notification widget for displaying info, success, warning, and error
messages inline without popup dialogs. Auto-dismisses after a timeout.

Features:
- Multiple notification types (info, success, warning, error)
- Icon + message display
- Auto-dismiss with timeout
- Optional close button
- Color-coded by type
- Non-intrusive inline display

Usage:
    from ui.components.notification_widget import NotificationWidget
    
    # Create widget
    notification = NotificationWidget(
        parent=some_frame,
        bg='#FFFFFF'
    )
    
    # Show success
    notification.show_success("Operation completed successfully!")
    
    # Show error
    notification.show_error("Failed to save file.")
    
    # Show info
    notification.show_info("Processing your request...")
    
    # Show warning
    notification.show_warning("File already exists.")
"""

import tkinter as tk
from typing import Literal, Optional

# Notification types and their colors
NOTIFICATION_STYLES = {
    'info': {
        'bg': '#E3F2FD',      # Light blue
        'fg': '#1976D2',      # Dark blue
        'icon': 'ℹ️',
        'border': '#2196F3'   # Blue
    },
    'success': {
        'bg': '#E8F5E9',      # Light green
        'fg': '#388E3C',      # Dark green
        'icon': '✓',
        'border': '#4CAF50'   # Green
    },
    'warning': {
        'bg': '#FFF3CD',      # Light yellow
        'fg': '#856404',      # Dark yellow
        'icon': '⚠',
        'border': '#FFC107'   # Yellow
    },
    'error': {
        'bg': '#FFEBEE',      # Light red
        'fg': '#C62828',      # Dark red
        'icon': '✗',
        'border': '#F44336'   # Red
    }
}


class NotificationWidget(tk.Frame):
    """
    Inline notification widget for info/success/warning/error messages.
    
    Displays a message with icon and color-coding based on notification type.
    Auto-dismisses after timeout.
    
    Attributes:
        auto_hide_seconds: Seconds before auto-hiding (0 = no auto-hide)
        show_close_button: Whether to show close button
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        auto_hide_seconds: int = 3,
        show_close_button: bool = True,
        bg: str = '#FFFFFF',
        **kwargs
    ):
        """
        Initialize notification widget.
        
        Args:
            parent: Parent widget
            auto_hide_seconds: Auto-hide timeout in seconds (0 = disabled)
            show_close_button: Show close button (X)
            bg: Background color for container
            **kwargs: Additional Frame arguments
        """
        super().__init__(parent, bg=bg, relief='flat', **kwargs)
        
        self.auto_hide_seconds = auto_hide_seconds
        self.show_close_button = show_close_button
        self._auto_hide_id: Optional[str] = None
        self._is_visible = False
        
        # Notification content frame (will be recreated for each show)
        self.notification_frame: Optional[tk.Frame] = None
    
    def show(
        self,
        message: str,
        notification_type: Literal['info', 'success', 'warning', 'error'] = 'info',
        side: Literal['left', 'right', 'top', 'bottom'] = 'top',
        fill: Literal['none', 'x', 'y', 'both'] = 'x',
        padx: int = 0,
        pady: int = 0
    ) -> None:
        """
        Show notification with message and type.
        
        Args:
            message: Message to display
            notification_type: Type of notification (info, success, warning, error)
            side: Pack side
            fill: Pack fill
            padx: Horizontal padding
            pady: Vertical padding
        """
        # Cancel previous auto-hide timer
        self._cancel_auto_hide()
        
        # Clear previous notification frame if exists
        if self.notification_frame:
            try:
                self.notification_frame.destroy()
            except tk.TclError:
                pass
        
        # Get style for notification type
        style = NOTIFICATION_STYLES.get(notification_type, NOTIFICATION_STYLES['info'])
        
        # Create notification frame with border
        self.notification_frame = tk.Frame(
            self,
            bg=style['border'],
            relief='solid',
            bd=1
        )
        self.notification_frame.pack(fill='x', padx=2, pady=2)
        
        # Inner frame for content
        content_frame = tk.Frame(
            self.notification_frame,
            bg=style['bg'],
            padx=8,
            pady=6
        )
        content_frame.pack(fill='x', expand=True)
        
        # Icon label
        icon_label = tk.Label(
            content_frame,
            text=style['icon'],
            font=('Arial', 14, 'bold'),
            fg=style['fg'],
            bg=style['bg']
        )
        icon_label.pack(side='left', padx=(0, 8))
        
        # Message label
        message_label = tk.Label(
            content_frame,
            text=message,
            font=('Arial', 10),
            fg=style['fg'],
            bg=style['bg'],
            justify='left',
            wraplength=400  # Wrap long messages
        )
        message_label.pack(side='left', fill='x', expand=True)
        
        # Close button (optional)
        if self.show_close_button:
            close_button = tk.Button(
                content_frame,
                text='✕',
                font=('Arial', 10, 'bold'),
                fg=style['fg'],
                bg=style['bg'],
                activebackground=style['bg'],
                relief='flat',
                cursor='hand2',
                command=self.hide,
                width=2,
                height=1
            )
            close_button.pack(side='right', padx=(8, 0))
        
        # Show widget if not already visible
        if not self._is_visible:
            try:
                self.pack(side=side, fill=fill, padx=padx, pady=pady)  # type: ignore
                self._is_visible = True
                self.update_idletasks()
            except Exception as e:
                print(f"[NotificationWidget] Error packing widget: {e}")
                self._is_visible = False
        
        # Start auto-hide timer if enabled
        if self.auto_hide_seconds > 0:
            self._auto_hide_id = self.after(
                self.auto_hide_seconds * 1000,
                self.hide
            )
    
    def show_info(self, message: str) -> None:
        """Show info notification."""
        self.show(message, 'info')
    
    def show_success(self, message: str) -> None:
        """Show success notification."""
        self.show(message, 'success')
    
    def show_warning(self, message: str) -> None:
        """Show warning notification."""
        self.show(message, 'warning')
    
    def show_error(self, message: str) -> None:
        """Show error notification."""
        self.show(message, 'error')
    
    def hide(self) -> None:
        """Hide the notification widget."""
        # Cancel auto-hide timer
        self._cancel_auto_hide()
        
        # Destroy notification frame
        if self.notification_frame:
            try:
                self.notification_frame.destroy()
                self.notification_frame = None
            except tk.TclError:
                pass
        
        # Hide widget
        if self._is_visible:
            try:
                self.pack_forget()
                self._is_visible = False
            except tk.TclError:
                self._is_visible = False
    
    def _cancel_auto_hide(self) -> None:
        """Cancel auto-hide timer if active."""
        if self._auto_hide_id:
            try:
                self.after_cancel(self._auto_hide_id)
            except tk.TclError:
                pass
            finally:
                self._auto_hide_id = None
    
    def is_visible(self) -> bool:
        """Check if widget is currently visible."""
        return self._is_visible
    
    def destroy(self) -> None:
        """Clean up resources before destroying."""
        # Cancel any pending timers
        self._cancel_auto_hide()
        
        # Destroy notification frame
        if self.notification_frame:
            try:
                self.notification_frame.destroy()
            except tk.TclError:
                pass
        
        # Destroy widget
        try:
            super().destroy()
        except tk.TclError:
            pass


# Example usage and testing
if __name__ == "__main__":
    def test_notification_widget():
        """Test the notification widget."""
        root = tk.Tk()
        root.title("Notification Widget Test")
        root.geometry("500x400")
        
        # Create container
        container = tk.Frame(root, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Title
        title = tk.Label(
            container,
            text="Notification Widget Test",
            font=('Arial', 14, 'bold'),
            bg='white'
        )
        title.pack(pady=10)
        
        # Create notification widget (single instance for all types)
        notification = NotificationWidget(
            container,
            auto_hide_seconds=5,
            show_close_button=True,
            bg='white'
        )
        notification.pack(pady=10, fill='x')
        notification.hide()  # Hide initially
        
        # Test buttons
        button_frame = tk.Frame(container, bg='white')
        button_frame.pack(pady=20)
        
        # Info button
        info_btn = tk.Button(
            button_frame,
            text="Show Info",
            command=lambda: notification.show_info("This is an information message."),
            bg='#2196F3',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=8
        )
        info_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Success button
        success_btn = tk.Button(
            button_frame,
            text="Show Success",
            command=lambda: notification.show_success("Operation completed successfully!"),
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=8
        )
        success_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Warning button
        warning_btn = tk.Button(
            button_frame,
            text="Show Warning",
            command=lambda: notification.show_warning("This action may have consequences."),
            bg='#FFC107',
            fg='black',
            font=('Arial', 10),
            padx=15,
            pady=8
        )
        warning_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # Error button
        error_btn = tk.Button(
            button_frame,
            text="Show Error",
            command=lambda: notification.show_error("An error occurred while processing."),
            bg='#F44336',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=8
        )
        error_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Info text
        info_text = tk.Label(
            container,
            text="Notifications auto-hide after 5 seconds\nClick X to dismiss manually",
            font=('Arial', 9),
            fg='gray',
            bg='white',
            justify='center'
        )
        info_text.pack(pady=10)
        
        root.mainloop()
    
    test_notification_widget()
