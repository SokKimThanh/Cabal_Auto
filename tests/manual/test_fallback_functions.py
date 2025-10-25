"""
Test script to verify fallback functions handle invalid parameters correctly.

This script tests that the fallback create_icon_button and create_icon_label
functions properly filter out invalid tkinter Button/Label parameters.
"""

import tkinter as tk
from typing import Optional


def get_button_config(button_type: str) -> dict:
    """Mock button config."""
    return {'font': ('Arial', 10, 'bold')}


def create_icon_button(parent, icon_name: str, command, text: str = '', button_type: str = 'green_light', **kwargs):
    """Fallback create_icon_button - filter invalid tk.Button parameters."""
    # Get base config
    config = get_button_config(button_type)
    
    # Remove parameters that tk.Button doesn't support
    invalid_params = [
        'icon_fallback', 'icon_size', 'variant', 
        'tooltip_key', 'tooltip_ns', 'auto_hover_disabled'
    ]
    
    # Filter kwargs
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
    config.update(filtered_kwargs)
    
    # Use icon_fallback as text if provided
    icon_fallback = kwargs.get('icon_fallback', icon_name)
    display_text = text or icon_fallback
    
    return tk.Button(parent, text=display_text, command=command, **config)


def create_icon_label(parent, icon_name: str, text: str = '', icon_fallback: str = '❓', **kwargs):
    """Fallback create_icon_label."""
    # Filter out invalid Label parameters
    invalid_params = ['icon_size']
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
    return tk.Label(parent, text=f"{icon_fallback} {text}", **filtered_kwargs)


def test_fallback_functions():
    """Test that fallback functions handle parameters correctly."""
    print("Testing fallback functions...")
    
    root = tk.Tk()
    root.title("Fallback Function Test")
    root.geometry("400x300")
    
    frame = tk.Frame(root, bg='white', padx=20, pady=20)
    frame.pack(fill='both', expand=True)
    
    # Test 1: create_icon_button with all custom parameters
    print("\n1. Testing create_icon_button with custom parameters...")
    try:
        btn1 = create_icon_button(
            frame,
            icon_name='save',
            icon_fallback='💾',
            icon_size=16,
            command=lambda: print("Button 1 clicked!"),
            button_type='primary',
            variant='icon_only',
            width=20,
            height=20,
            tooltip_key='tooltip_save',
            tooltip_ns='test',
            auto_hover_disabled=True
        )
        btn1.pack(pady=5)
        print("   ✓ Success: Button created without TclError")
    except tk.TclError as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2: create_icon_button with text
    print("\n2. Testing create_icon_button with text...")
    try:
        btn2 = create_icon_button(
            frame,
            icon_name='delete',
            icon_fallback='🗑️',
            icon_size=16,
            command=lambda: print("Button 2 clicked!"),
            text='Delete',
            button_type='red',
            width=100
        )
        btn2.pack(pady=5)
        print("   ✓ Success: Button with text created")
    except tk.TclError as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 3: create_icon_label with custom parameters
    print("\n3. Testing create_icon_label with icon_fallback...")
    try:
        label1 = create_icon_label(
            frame,
            icon_name='monster',
            text='Monster Name',
            icon_fallback='👹',
            icon_size=16,
            fg='blue'
        )
        label1.pack(pady=5)
        print("   ✓ Success: Label created without TclError")
    except tk.TclError as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 4: Multiple buttons with different parameters
    print("\n4. Testing multiple buttons...")
    try:
        for i, (icon, fallback) in enumerate([
            ('edit', '✏️'),
            ('add', '➕'),
            ('test', '🧪')
        ]):
            btn = create_icon_button(
                frame,
                icon_name=icon,
                icon_fallback=fallback,
                icon_size=16,
                command=lambda x=i: print(f"Button {x} clicked!"),
                variant='icon_only',
                width=20,
                height=20
            )
            btn.pack(side='left', padx=2)
        print("   ✓ Success: All buttons created")
    except tk.TclError as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
    print("\nWindow will stay open for visual verification.")
    print("Close the window to exit.")
    
    root.mainloop()


if __name__ == "__main__":
    test_fallback_functions()
