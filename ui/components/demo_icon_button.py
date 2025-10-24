"""
Demo script for icon_button component

Run this to test all features:
- Basic icon buttons
- Different button types (green_light, red, blue, orange, refresh)
- Different variants (compact, small, medium, large, text)
- Different states (normal, disabled, highlight, danger)
- Tooltips (i18n and plain text)
- Callbacks (hover, focus)
- Convenience functions
"""

import sys
from pathlib import Path

# Add project root to sys.path for imports
project_root = Path(__file__).resolve().parents[2]  # ui/components/* -> project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk
from icon_button import (
    create_icon_button,
    create_add_button,
    create_delete_button,
    create_save_button,
    create_cancel_button,
    create_refresh_button
)


def demo_icon_button():
    """Demo window for icon button component."""
    root = tk.Tk()
    root.title("Icon Button Component Demo")
    root.geometry("800x900")
    root.configure(bg='#f0f0f0')
    
    # Counter for command testing
    click_count = {'value': 0}
    
    def on_click():
        click_count['value'] += 1
        status_label.config(text=f"Button clicked: {click_count['value']} times")
    
    def on_hover(event):
        hover_label.config(text="Mouse hover detected!")
    
    def on_leave(event):
        hover_label.config(text="Mouse left button")
    
    def on_focus(event):
        focus_label.config(text="Button focused!")
    
    # Title
    title = tk.Label(
        root,
        text="🎨 Icon Button Component Demo",
        font=('Arial', 16, 'bold'),
        bg='#f0f0f0',
        pady=10
    )
    title.pack()
    
    # Status labels
    status_label = tk.Label(
        root,
        text="Click any button...",
        font=('Arial', 10),
        bg='#f0f0f0'
    )
    status_label.pack()
    
    hover_label = tk.Label(
        root,
        text="Hover over buttons...",
        font=('Arial', 10),
        bg='#f0f0f0'
    )
    hover_label.pack()
    
    focus_label = tk.Label(
        root,
        text="Focus on buttons...",
        font=('Arial', 10),
        bg='#f0f0f0'
    )
    focus_label.pack(pady=(0, 10))
    
    # Container
    container = tk.Frame(root, bg='#f0f0f0')
    container.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Section 1: Button Types
    section1 = tk.LabelFrame(
        container,
        text="1. Button Types (button_type parameter)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section1.pack(fill='x', pady=(0, 10))
    
    types_frame = tk.Frame(section1, bg='#f0f0f0')
    types_frame.pack()
    
    create_icon_button(
        types_frame,
        icon_name='save',
        text='Green Light',
        command=on_click,
        button_type='green_light',
        tooltip_text='Green light button'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        types_frame,
        icon_name='delete',
        text='Red',
        command=on_click,
        button_type='red',
        tooltip_text='Red danger button'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        types_frame,
        icon_name='info',
        text='Blue',
        command=on_click,
        button_type='blue',
        tooltip_text='Blue info button'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        types_frame,
        icon_name='warning',
        text='Orange',
        command=on_click,
        button_type='orange',
        tooltip_text='Orange warning button'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        types_frame,
        icon_name='refresh',
        text='Refresh',
        command=on_click,
        button_type='refresh',
        tooltip_text='Refresh button'
    ).pack(side='left', padx=5, pady=5)
    
    # Section 2: Variants (sizes)
    section2 = tk.LabelFrame(
        container,
        text="2. Variants / Sizes (variant parameter)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section2.pack(fill='x', pady=(0, 10))
    
    variants_frame = tk.Frame(section2, bg='#f0f0f0')
    variants_frame.pack()
    
    create_icon_button(
        variants_frame,
        icon_name='add',
        text='Compact',
        command=on_click,
        button_type='green_light',
        variant='compact',
        tooltip_text='Compact size'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        variants_frame,
        icon_name='add',
        text='Small',
        command=on_click,
        button_type='green_light',
        variant='small',
        tooltip_text='Small size'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        variants_frame,
        icon_name='add',
        text='Medium',
        command=on_click,
        button_type='green_light',
        variant='medium',
        tooltip_text='Medium size (default)'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        variants_frame,
        icon_name='add',
        text='Large',
        command=on_click,
        button_type='green_light',
        variant='large',
        tooltip_text='Large size'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        variants_frame,
        icon_name='add',
        text='Text Button',
        command=on_click,
        button_type='blue',
        variant='text',
        tooltip_text='Text-only variant (no border/padding)'
    ).pack(side='left', padx=5, pady=5)
    
    # Section 3: States
    section3 = tk.LabelFrame(
        container,
        text="3. Button States (state parameter)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section3.pack(fill='x', pady=(0, 10))
    
    states_frame = tk.Frame(section3, bg='#f0f0f0')
    states_frame.pack()
    
    create_icon_button(
        states_frame,
        icon_name='check',
        text='Normal',
        command=on_click,
        button_type='green_light',
        state='normal',
        tooltip_text='Normal state'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        states_frame,
        icon_name='check',
        text='Highlight',
        command=on_click,
        button_type='green_light',
        state='highlight',
        tooltip_text='Highlighted state (brighter)'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        states_frame,
        icon_name='warning',
        text='Danger',
        command=on_click,
        button_type='blue',  # Will be overridden to red
        state='danger',
        tooltip_text='Danger state (forced red)'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        states_frame,
        icon_name='cancel',
        text='Disabled',
        command=on_click,
        button_type='refresh',
        state='disabled',
        tooltip_text='Disabled state (not clickable)'
    ).pack(side='left', padx=5, pady=5)
    
    # Section 4: Icon only buttons
    section4 = tk.LabelFrame(
        container,
        text="4. Icon-Only Buttons (no text parameter)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section4.pack(fill='x', pady=(0, 10))
    
    icons_frame = tk.Frame(section4, bg='#f0f0f0')
    icons_frame.pack()
    
    create_icon_button(
        icons_frame,
        icon_name='add',
        command=on_click,
        button_type='green_light',
        variant='compact',
        tooltip_text='Add item'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        icons_frame,
        icon_name='delete',
        command=on_click,
        button_type='red',
        variant='compact',
        tooltip_text='Delete item'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        icons_frame,
        icon_name='edit',
        command=on_click,
        button_type='blue',
        variant='compact',
        tooltip_text='Edit item'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        icons_frame,
        icon_name='refresh',
        command=on_click,
        button_type='refresh',
        variant='compact',
        tooltip_text='Refresh list'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        icons_frame,
        icon_name='settings',
        command=on_click,
        button_type='orange',
        variant='compact',
        tooltip_text='Settings'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        icons_frame,
        icon_name='search',
        command=on_click,
        button_type='blue',
        variant='compact',
        tooltip_text='Search'
    ).pack(side='left', padx=2, pady=5)
    
    # Section 5: Callbacks
    section5 = tk.LabelFrame(
        container,
        text="5. Event Callbacks (on_hover, on_leave, on_focus)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section5.pack(fill='x', pady=(0, 10))
    
    callbacks_frame = tk.Frame(section5, bg='#f0f0f0')
    callbacks_frame.pack()
    
    create_icon_button(
        callbacks_frame,
        icon_name='info',
        text='Hover Me',
        command=on_click,
        button_type='blue',
        on_hover=on_hover,
        on_leave=on_leave,
        tooltip_text='Hover to trigger event'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        callbacks_frame,
        icon_name='edit',
        text='Focus Me',
        command=on_click,
        button_type='orange',
        on_focus=on_focus,
        tooltip_text='Tab to focus and trigger event'
    ).pack(side='left', padx=5, pady=5)
    
    # Section 6: Convenience functions
    section6 = tk.LabelFrame(
        container,
        text="6. Convenience Functions (Pre-configured buttons)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section6.pack(fill='x', pady=(0, 10))
    
    convenience_frame = tk.Frame(section6, bg='#f0f0f0')
    convenience_frame.pack()
    
    create_add_button(
        convenience_frame,
        command=on_click,
        text='Add',
        tooltip_text='Pre-configured add button'
    ).pack(side='left', padx=5, pady=5)
    
    create_delete_button(
        convenience_frame,
        command=on_click,
        text='Delete',
        tooltip_text='Pre-configured delete button'
    ).pack(side='left', padx=5, pady=5)
    
    create_save_button(
        convenience_frame,
        command=on_click,
        text='Save',
        tooltip_text='Pre-configured save button'
    ).pack(side='left', padx=5, pady=5)
    
    create_cancel_button(
        convenience_frame,
        command=on_click,
        text='Cancel',
        tooltip_text='Pre-configured cancel button'
    ).pack(side='left', padx=5, pady=5)
    
    create_refresh_button(
        convenience_frame,
        command=on_click,
        text='Refresh',
        tooltip_text='Pre-configured refresh button'
    ).pack(side='left', padx=5, pady=5)
    
    # Section 7: Custom styling
    section7 = tk.LabelFrame(
        container,
        text="7. Custom Styling (width, padding, **kwargs)",
        font=('Arial', 11, 'bold'),
        bg='#f0f0f0',
        padx=10,
        pady=10
    )
    section7.pack(fill='x', pady=(0, 10))
    
    custom_frame = tk.Frame(section7, bg='#f0f0f0')
    custom_frame.pack()
    
    create_icon_button(
        custom_frame,
        icon_name='save',
        text='Custom Width',
        command=on_click,
        button_type='green_light',
        width=20,  # Custom width
        tooltip_text='Custom width=20'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        custom_frame,
        icon_name='save',
        text='Custom Padding',
        command=on_click,
        button_type='blue',
        padding={'padx': 20, 'pady': 15},  # Custom padding
        tooltip_text='Custom padding (20, 15)'
    ).pack(side='left', padx=5, pady=5)
    
    create_icon_button(
        custom_frame,
        icon_name='save',
        text='Custom Font',
        command=on_click,
        button_type='orange',
        font=('Comic Sans MS', 12, 'italic'),  # Custom font via kwargs
        tooltip_text='Custom font via **kwargs'
    ).pack(side='left', padx=5, pady=5)
    
    root.mainloop()


if __name__ == '__main__':
    demo_icon_button()
