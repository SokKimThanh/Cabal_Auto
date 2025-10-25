"""
Quick test script to verify ConfirmationWidget shows up correctly.
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import tkinter as tk
from ui.components.confirmation_widget import ConfirmationWidget


def test_confirmation_widget():
    """Test basic confirmation widget functionality."""
    root = tk.Tk()
    root.title("Confirmation Widget Test")
    root.geometry("600x400")
    root.configure(bg='white')
    
    # Create main container
    main_frame = tk.Frame(root, bg='white', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Title
    title = tk.Label(
        main_frame,
        text="Confirmation Widget Test",
        font=('Arial', 16, 'bold'),
        bg='white'
    )
    title.pack(pady=10)
    
    # Status label
    status = tk.Label(
        main_frame,
        text="Click 'Show Confirmation' button below",
        font=('Arial', 12),
        bg='white',
        fg='gray'
    )
    status.pack(pady=10)
    
    # Container for confirmation widget (similar to Monster Editor)
    header_frame = tk.Frame(main_frame, bg='#F0F0F0', relief='solid', bd=1)
    header_frame.pack(fill='x', pady=10)
    
    # Left side frame (where confirmation widget will appear)
    left_frame = tk.Frame(header_frame, bg='#F0F0F0')
    left_frame.pack(side='left', padx=10, pady=10)
    
    # Label next to confirmation
    label = tk.Label(
        left_frame,
        text="Confirmation will appear here →",
        bg='#F0F0F0',
        fg='blue'
    )
    label.pack(side='left', padx=5)
    
    # Create confirmation widget
    def on_confirm():
        status.config(text="✓ Confirmed!", fg='green')
        print("[Test] User clicked Yes")
    
    def on_cancel():
        status.config(text="✗ Cancelled", fg='red')
        print("[Test] User clicked No")
    
    confirmation = ConfirmationWidget(
        parent=left_frame,
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        auto_hide_seconds=5,
        bg='#F2F2F2'
    )
    
    # Right side frame (buttons)
    right_frame = tk.Frame(header_frame, bg='#F0F0F0')
    right_frame.pack(side='right', padx=10, pady=10)
    
    # Test buttons
    def show_test():
        status.config(text="Waiting for confirmation...", fg='orange')
        print("[Test] Showing confirmation widget...")
        confirmation.show(side='left', padx=(10, 0))
        print(f"[Test] Widget visible: {confirmation.is_visible()}")
    
    def hide_test():
        status.config(text="Confirmation hidden", fg='gray')
        print("[Test] Hiding confirmation widget...")
        confirmation.hide()
    
    def cancel_test():
        status.config(text="Confirmation cancelled", fg='gray')
        print("[Test] Cancelling confirmation widget...")
        confirmation.cancel()
    
    show_btn = tk.Button(
        right_frame,
        text="Show Confirmation",
        command=show_test,
        bg='#4CAF50',
        fg='white',
        font=('Arial', 10, 'bold'),
        padx=10,
        pady=5
    )
    show_btn.pack(side='left', padx=2)
    
    hide_btn = tk.Button(
        right_frame,
        text="Hide",
        command=hide_test,
        bg='#FF9800',
        fg='white',
        font=('Arial', 10, 'bold'),
        padx=10,
        pady=5
    )
    hide_btn.pack(side='left', padx=2)
    
    cancel_btn = tk.Button(
        right_frame,
        text="Cancel",
        command=cancel_test,
        bg='#F44336',
        fg='white',
        font=('Arial', 10, 'bold'),
        padx=10,
        pady=5
    )
    cancel_btn.pack(side='left', padx=2)
    
    # Info text
    info = tk.Label(
        main_frame,
        text="• Click 'Show Confirmation' to display Yes/No buttons\n"
             "• Click Yes (✓) to confirm\n"
             "• Click No (✗) to cancel\n"
             "• Widget auto-hides after 5 seconds if no action taken\n"
             "• Use 'Hide' to manually hide without executing callback\n"
             "• Use 'Cancel' to hide and clear callbacks",
        font=('Arial', 9),
        bg='white',
        fg='gray',
        justify='left'
    )
    info.pack(pady=20, anchor='w', padx=20)
    
    print("="*60)
    print("Confirmation Widget Test Started")
    print("="*60)
    print("Watch console for debug messages...")
    print("")
    
    root.mainloop()


if __name__ == "__main__":
    test_confirmation_widget()
