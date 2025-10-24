"""
Demo: Icon Button Auto State Management

Demonstrates automatic icon changes based on button state:
- Enabled: Shows original icon (save, stop, etc.)
- Disabled: Automatically changes to forbidden icon (🚫)

Features:
1. set_button_enabled() - Enable/disable with auto icon change
2. update_button_state() - Full state control
3. set_button_icon() - Change icon independently

Author: SokKimThanh
Created: 2025-10-25
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk

# Import icon button components
try:
    from ui.components.icon_button import (
        create_icon_button,
        set_button_enabled,
        update_button_state,
        set_button_icon
    )
except ImportError as e:
    print(f"Error importing icon button: {e}")
    sys.exit(1)


def create_demo_window():
    """Create demo window with state management controls."""
    root = tk.Tk()
    root.title("Icon Button State Demo")
    root.geometry("700x600")
    
    # Main container
    main_frame = tk.Frame(root, bg='#f5f5f5', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Title
    title = tk.Label(
        main_frame,
        text="🎨 Icon Button Auto State Management",
        font=('Segoe UI', 14, 'bold'),
        bg='#f5f5f5',
        fg='#333'
    )
    title.pack(pady=(0, 10))
    
    # Description
    desc = tk.Label(
        main_frame,
        text="When disabled, icons automatically change to forbidden symbol (🚫)",
        font=('Segoe UI', 9),
        bg='#f5f5f5',
        fg='#666'
    )
    desc.pack(pady=(0, 20))
    
    # Buttons section
    buttons_frame = tk.LabelFrame(
        main_frame,
        text="Demo Buttons",
        font=('Segoe UI', 10, 'bold'),
        bg='#ffffff',
        padx=15,
        pady=15
    )
    buttons_frame.pack(fill='x', pady=(0, 15))
    
    # Row 1: Save button
    row1 = tk.Frame(buttons_frame, bg='#ffffff')
    row1.pack(fill='x', pady=5)
    
    tk.Label(
        row1,
        text="Save Button:",
        font=('Segoe UI', 9, 'bold'),
        bg='#ffffff',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    save_btn = create_icon_button(
        row1,
        icon_name='save',
        icon_fallback='💾',
        command=lambda: print("Save clicked"),
        button_type='green_light',
        variant='medium',
        tooltip_text='Save changes'
    )
    save_btn.pack(side='left', padx=5)
    
    tk.Label(
        row1,
        text="← Try disabling →",
        font=('Segoe UI', 8, 'italic'),
        bg='#ffffff',
        fg='#999'
    ).pack(side='left', padx=10)
    
    # Row 2: Stop button
    row2 = tk.Frame(buttons_frame, bg='#ffffff')
    row2.pack(fill='x', pady=5)
    
    tk.Label(
        row2,
        text="Stop Button:",
        font=('Segoe UI', 9, 'bold'),
        bg='#ffffff',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    stop_btn = create_icon_button(
        row2,
        icon_name='stop',
        icon_fallback='⏹️',
        command=lambda: print("Stop clicked"),
        button_type='red',
        variant='medium',
        state='disabled',  # Start disabled
        tooltip_text='Stop process'
    )
    stop_btn.pack(side='left', padx=5)
    
    tk.Label(
        row2,
        text="← Starts disabled (🚫)",
        font=('Segoe UI', 8, 'italic'),
        bg='#ffffff',
        fg='#999'
    ).pack(side='left', padx=10)
    
    # Row 3: Delete button
    row3 = tk.Frame(buttons_frame, bg='#ffffff')
    row3.pack(fill='x', pady=5)
    
    tk.Label(
        row3,
        text="Delete Button:",
        font=('Segoe UI', 9, 'bold'),
        bg='#ffffff',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    delete_btn = create_icon_button(
        row3,
        icon_name='delete',
        icon_fallback='🗑️',
        command=lambda: print("Delete clicked"),
        button_type='red',
        variant='medium',
        tooltip_text='Delete item'
    )
    delete_btn.pack(side='left', padx=5)
    
    tk.Label(
        row3,
        text="← Toggle enabled/disabled",
        font=('Segoe UI', 8, 'italic'),
        bg='#ffffff',
        fg='#999'
    ).pack(side='left', padx=10)
    
    # Controls section
    controls_frame = tk.LabelFrame(
        main_frame,
        text="State Controls",
        font=('Segoe UI', 10, 'bold'),
        bg='#ffffff',
        padx=15,
        pady=15
    )
    controls_frame.pack(fill='x', pady=(0, 15))
    
    # Control buttons
    control_row1 = tk.Frame(controls_frame, bg='#ffffff')
    control_row1.pack(fill='x', pady=5)
    
    tk.Button(
        control_row1,
        text="💾 Enable Save",
        font=('Segoe UI', 9),
        bg='#2E7D32',
        fg='white',
        command=lambda: set_button_enabled(save_btn, True, 'Save changes'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    tk.Button(
        control_row1,
        text="🚫 Disable Save",
        font=('Segoe UI', 9),
        bg='#757575',
        fg='white',
        command=lambda: set_button_enabled(save_btn, False, 'No changes to save'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    control_row2 = tk.Frame(controls_frame, bg='#ffffff')
    control_row2.pack(fill='x', pady=5)
    
    tk.Button(
        control_row2,
        text="⏹️ Enable Stop",
        font=('Segoe UI', 9),
        bg='#C62828',
        fg='white',
        command=lambda: set_button_enabled(stop_btn, True, 'Stop process'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    tk.Button(
        control_row2,
        text="🚫 Disable Stop",
        font=('Segoe UI', 9),
        bg='#757575',
        fg='white',
        command=lambda: set_button_enabled(stop_btn, False, 'Not running'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    control_row3 = tk.Frame(controls_frame, bg='#ffffff')
    control_row3.pack(fill='x', pady=5)
    
    tk.Button(
        control_row3,
        text="🗑️ Enable Delete",
        font=('Segoe UI', 9),
        bg='#C62828',
        fg='white',
        command=lambda: set_button_enabled(delete_btn, True, 'Delete item'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    tk.Button(
        control_row3,
        text="🚫 Disable Delete",
        font=('Segoe UI', 9),
        bg='#757575',
        fg='white',
        command=lambda: set_button_enabled(delete_btn, False, 'Nothing to delete'),
        padx=10,
        pady=5
    ).pack(side='left', padx=5)
    
    # Code example
    code_frame = tk.LabelFrame(
        main_frame,
        text="💡 Code Example",
        font=('Segoe UI', 10, 'bold'),
        bg='#f5f5f5',
        padx=10,
        pady=10
    )
    code_frame.pack(fill='both', expand=True)
    
    code_text = tk.Text(
        code_frame,
        font=('Consolas', 9),
        bg='#2b2b2b',
        fg='#d4d4d4',
        height=12,
        wrap='word',
        relief='flat',
        padx=10,
        pady=10
    )
    code_text.pack(fill='both', expand=True)
    
    code_example = """# Import
from ui.components.icon_button import (
    create_icon_button, 
    set_button_enabled
)

# Create button
save_btn = create_icon_button(
    parent=frame,
    icon_name='save',
    command=on_save,
    button_type='green_light'
)

# Disable when no changes (icon auto-changes to 🚫)
set_button_enabled(save_btn, enabled=False, 
                   tooltip='No changes to save')

# Enable when changes exist (icon restores to 💾)
set_button_enabled(save_btn, enabled=True,
                   tooltip='Save changes')"""
    
    code_text.insert('1.0', code_example)
    code_text.config(state='disabled')
    
    # Status
    status_frame = tk.Frame(main_frame, bg='#e3f2fd', relief='solid', bd=1, padx=10, pady=10)
    status_frame.pack(fill='x', pady=(10, 0))
    
    tk.Label(
        status_frame,
        text="ℹ️ Feature: Icons automatically change to 🚫 when disabled, "
             "and restore to original when enabled",
        font=('Segoe UI', 8),
        bg='#e3f2fd',
        fg='#0d47a1',
        wraplength=650,
        justify='left'
    ).pack()
    
    root.mainloop()


if __name__ == "__main__":
    print("=" * 70)
    print("Icon Button Auto State Management Demo")
    print("=" * 70)
    print("\nFeatures:")
    print("  • Automatic icon change: enabled → original, disabled → 🚫")
    print("  • set_button_enabled(btn, enabled, tooltip)")
    print("  • update_button_state(btn, enabled, icon_name, tooltip)")
    print("  • set_button_icon(btn, icon_name)")
    print("\nUse Cases:")
    print("  • Save button: disabled when no changes")
    print("  • Stop button: disabled when not running")
    print("  • Delete button: disabled when nothing selected")
    print("\nStarting demo...")
    print("=" * 70)
    
    create_demo_window()
