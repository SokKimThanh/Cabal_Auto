"""
Quick Test: Setup Wizard Button
--------------------------------
Tests that the Setup Wizard button in app_gui.py can open the wizard successfully.

Bug Fixed: Import path was incorrect
- Before: from setup_wizard import show_setup_wizard (❌ Wrong path)
- After: from ui.setup_wizard import show_setup_wizard (✅ Correct path)
"""

import tkinter as tk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test the import
print("Testing Setup Wizard import...")
try:
    from ui.setup_wizard import show_setup_wizard
    print("✅ Import successful: show_setup_wizard found!")
    print(f"   Function: {show_setup_wizard}")
    print(f"   Module: {show_setup_wizard.__module__}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test calling the function
print("\nTesting Setup Wizard function call...")

root = tk.Tk()
root.title("Test: Setup Wizard Button")
root.geometry("600x400")

# Instructions
instructions = tk.Label(
    root,
    text=(
        "🧪 Setup Wizard Button Test\n\n"
        "This test verifies that the Setup Wizard can be opened\n"
        "from the main application using the correct import path.\n\n"
        "Bug Fixed:\n"
        "❌ Before: from setup_wizard import show_setup_wizard\n"
        "✅ After: from ui.setup_wizard import show_setup_wizard\n\n"
        "Click the button below to open Setup Wizard:"
    ),
    justify='center',
    bg='#e7f3ff',
    fg='#004085',
    padx=20,
    pady=20,
    font=('Arial', 10)
)
instructions.pack(expand=True, fill='both', padx=20, pady=20)

# Status label
status_label = tk.Label(
    root,
    text="Status: Ready to test",
    font=('Arial', 11, 'bold'),
    bg='#ffc107',
    fg='#000',
    pady=10
)
status_label.pack(fill='x')

def test_open_wizard():
    """Test opening the Setup Wizard."""
    try:
        status_label.config(
            text="Status: Opening Setup Wizard...",
            bg='#17a2b8',
            fg='white'
        )
        root.update()
        
        def on_complete(wizard_data):
            status_label.config(
                text=f"Status: Wizard completed! Language: {wizard_data.get('language', 'unknown')}",
                bg='#28a745',
                fg='white'
            )
            print(f"✅ Wizard completed: {wizard_data}")
        
        def on_cancel():
            status_label.config(
                text="Status: Wizard cancelled",
                bg='#6c757d',
                fg='white'
            )
            print("ℹ️ Wizard cancelled")
        
        # Call the function
        show_setup_wizard(
            root,
            config_manager=None,
            on_complete=on_complete,
            on_cancel=on_cancel
        )
        
        status_label.config(
            text="Status: Wizard opened successfully!",
            bg='#28a745',
            fg='white'
        )
        print("✅ Setup Wizard opened successfully!")
        
    except Exception as e:
        status_label.config(
            text=f"Status: Error - {str(e)[:50]}",
            bg='#dc3545',
            fg='white'
        )
        print(f"❌ Error opening wizard: {e}")
        import traceback
        traceback.print_exc()

# Test button
test_btn = tk.Button(
    root,
    text="🚀 Open Setup Wizard",
    command=test_open_wizard,
    font=('Arial', 12, 'bold'),
    bg='#007bff',
    fg='white',
    padx=30,
    pady=15,
    relief='raised',
    bd=3
)
test_btn.pack(pady=20)

# Result info
result_info = tk.Label(
    root,
    text=(
        "Expected Result:\n"
        "✅ Setup Wizard window should open\n"
        "✅ No import errors\n"
        "✅ Main window should be hidden while wizard is open"
    ),
    justify='left',
    bg='#f8f9fa',
    fg='#495057',
    padx=15,
    pady=10,
    font=('Arial', 9)
)
result_info.pack(fill='x', padx=20, pady=(0, 20))

print("\nTest window opened. Click 'Open Setup Wizard' button to test.")
root.mainloop()
