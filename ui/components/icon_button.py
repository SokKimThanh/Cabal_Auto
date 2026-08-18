"""
Icon Button & Label Component

Reusable icon button and label components with:
- Global icon integration (lib.ui.icon_helper)
- Global button styles (lib.ui.button_styles)
- Tooltip support (lib.ui.tooltip)
- State management (enabled/disabled/highlight/danger)
- Flexible sizing and variants
- Hover/focus callbacks
- Automatic reference management (prevent garbage collection)

Usage:
    from ui.components import create_icon_button, create_icon_label
    
    # Icon button
    btn = create_icon_button(
        parent=frame,
        icon_name='add',
        text='Add Item',
        command=on_add,
        button_type='green_light',
        tooltip_key='btn_add',
        state='normal'
    )
    
    # Icon label
    label = create_icon_label(
        parent=frame,
        icon_name='monster',
        text='Monster Name:',
        tooltip_text='Enter the monster name'
    )
"""

from typing import Any, Callable, Optional, Dict, List
import tkinter as tk

# Global imports
import sys
from pathlib import Path

# Add project root to path if not already there
project_root = Path(__file__).resolve().parents[2]  # ui/components/* -> project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.helpers.icon_helper import IconHelper
    icon_helper = IconHelper()
except ImportError as e:
    print(f"Warning: Could not import IconHelper: {e}")
    # Fallback mock
    class MockIconHelper:
        def get_icon(self, name: str, fallback: str = '', size: int = 16) -> str:
            return fallback
    icon_helper = MockIconHelper()

try:
    from ui.helpers.button_styles import get_button_config
except ImportError as e:
    print(f"Warning: Could not import get_button_config: {e}")
    def get_button_config(button_type: str) -> dict:
        # Fallback configs matching button_styles.py
        configs = {
            'green_light': {
                'bg': '#2E7D32',
                'fg': 'white',
                'activebackground': '#1B5E20',
                'activeforeground': 'white',
                'font': ('Arial', 10, 'bold'),
                'relief': 'raised',
                'bd': 2,
                'cursor': 'hand2'
            },
            'red': {
                'bg': '#C62828',
                'fg': 'white',
                'activebackground': '#B71C1C',
                'activeforeground': 'white',
                'font': ('Arial', 10, 'bold'),
                'relief': 'raised',
                'bd': 2,
                'cursor': 'hand2'
            },
            'blue': {
                'bg': '#1565C0',
                'fg': 'white',
                'activebackground': '#0D47A1',
                'activeforeground': 'white',
                'font': ('Arial', 10, 'bold'),
                'relief': 'raised',
                'bd': 2,
                'cursor': 'hand2'
            },
            'orange': {
                'bg': '#EF6C00',
                'fg': 'white',
                'activebackground': '#E65100',
                'activeforeground': 'white',
                'font': ('Arial', 10, 'bold'),
                'relief': 'raised',
                'bd': 2,
                'cursor': 'hand2'
            },
            'refresh': {
                'bg': '#757575',
                'fg': 'white',
                'activebackground': '#616161',
                'activeforeground': 'white',
                'font': ('Arial', 10, 'bold'),
                'relief': 'raised',
                'bd': 2,
                'cursor': 'hand2'
            }
        }
        return configs.get(button_type, configs['green_light'])

try:
    from ui.helpers.tooltip import attach_i18n_tooltip
except ImportError:
    def attach_i18n_tooltip(widget, key: str, ns: Optional[str], lang_provider: Callable, delay: int = 400) -> Any:
        pass

try:
    from lib.i18n import t as i18n_t, get_lang
except ImportError:
    def i18n_t(key: str, *, ns: Optional[str] = None, default: Optional[str] = None) -> str:
        return default if default else key
    def get_lang() -> str:
        return 'vi'


# Global icon references to prevent garbage collection
_ICON_REFS: List[Any] = []


def create_icon_button(
    parent: Any,
    icon_name: str,
    command: Optional[Callable] = None,
    text: Optional[str] = None,
    button_type: str = 'green_light',
    icon_size: int = 16,
    button_size: Optional[int] = None,
    icon_fallback: str = '',
    tooltip_key: Optional[str] = None,
    tooltip_ns: Optional[str] = None,
    tooltip_text: Optional[str] = None,
    state: str = 'normal',
    variant: Optional[str] = None,
    width: Optional[int] = None,
    padding: Optional[Dict[str, int]] = None,
    on_hover: Optional[Callable] = None,
    on_leave: Optional[Callable] = None,
    on_focus: Optional[Callable] = None,
    auto_hover_disabled: bool = True,
    **kwargs
) -> tk.Button:
    """
    Create a standardized icon button with global styles.
    
    Args:
        parent: Parent widget
        icon_name: Icon name from icon_helper (e.g., 'add', 'delete', 'save')
        command: Button command callback
        text: Optional button text (icon will be prepended)
        button_type: Button style type ('green_light', 'red', 'blue', 'orange', 'refresh')
        icon_size: Icon size in pixels (default: 16) - controls the icon image size
        button_size: Total button size in pixels (optional) - auto-calculates padding if provided
        icon_fallback: Fallback emoji if icon not found
        tooltip_key: i18n key for tooltip
        tooltip_ns: i18n namespace for tooltip
        tooltip_text: Direct tooltip text (overrides tooltip_key)
        state: Button state ('normal', 'disabled', 'highlight', 'danger')
        variant: Button variant ('compact', 'small', 'medium', 'large', 'text')
        width: Custom button width (overrides variant width)
        padding: Custom padding dict {'padx': int, 'pady': int} (overrides button_size)
        on_hover: Callback when mouse enters button (event)
        on_leave: Callback when mouse leaves button (event)
        on_focus: Callback when button receives focus (event)
        auto_hover_disabled: Auto change icon/cursor to forbidden when hovering over disabled button (default: True)
        **kwargs: Additional button configuration (overrides defaults)
    
    Returns:
        tk.Button: Configured button with icon and styles
    
    Example:
        # Simple icon button
        btn = create_icon_button(
            parent=frame,
            icon_name='add',
            command=on_add,
            button_type='green_light',
            tooltip_key='btn_add',
            tooltip_ns='monster_editor'
        )
        
        # Icon button with text
        btn = create_icon_button(
            parent=frame,
            icon_name='save',
            text='Save All',
            command=on_save,
            button_type='green_light',
            variant='medium',
            tooltip_text='Save all changes'
        )
        
        # Danger state button
        btn = create_icon_button(
            parent=frame,
            icon_name='delete',
            command=on_delete,
            state='danger',
            tooltip_key='btn_delete'
        )
    """
    # Auto-detect state from button state and adjust icon accordingly
    # Priority: explicit state > tkinter state > normal
    actual_state = state
    
    # If state is 'disabled' or button will be disabled, show forbidden icon
    if state == 'disabled' or kwargs.get('state') == 'disabled':
        actual_state = 'disabled'
        # Replace icon with forbidden symbol
        original_icon_name = icon_name
        icon_name = 'forbidden'
        icon_fallback = '🚫'
        # Set default tooltip if none provided
        if not tooltip_text and not tooltip_key:
            lang = get_lang()
            if lang == 'vi':
                tooltip_text = f'Không thể {original_icon_name} lúc này'
            else:
                tooltip_text = f'Cannot {original_icon_name} at this time'
    
    # Get icon
    icon = icon_helper.get_icon(icon_name, fallback=icon_fallback, size=icon_size)
    
    # Determine if icon is PhotoImage or emoji string
    is_photoimage = not isinstance(icon, str)
    
    # Keep icon reference to prevent garbage collection
    if is_photoimage:
        _ICON_REFS.append(icon)
    
    # Get base button config from global styles
    base_config = get_button_config(button_type)
    
    # Apply variant sizing
    if variant:
        variant_configs = {
            'compact': {'width': 0, 'padx': 2, 'pady': 2},
            'small': {'width': 8, 'padx': 4, 'pady': 4},
            'medium': {'width': 12, 'padx': 8, 'pady': 6},
            'large': {'width': 16, 'padx': 12, 'pady': 8},
            'text': {'width': 0, 'padx': 0, 'pady': 0, 'relief': 'flat', 'bd': 0}
        }
        if variant in variant_configs:
            base_config.update(variant_configs[variant])
    
    # Auto-calculate padding from button_size if provided (only for icon-only buttons)
    if button_size is not None and not text:
        # button_size = icon_size + 2*padding + 2*border
        # Assuming border=2 (from relief='raised', bd=2)
        border_width = base_config.get('bd', 2)
        calculated_padding = (button_size - icon_size - 2 * border_width) // 2
        # Ensure minimum padding of 2
        calculated_padding = max(2, calculated_padding)
        base_config['padx'] = calculated_padding
        base_config['pady'] = calculated_padding
    
    # Apply custom width
    if width is not None:
        base_config['width'] = width
    
    # Apply custom padding (overrides button_size calculation)
    if padding:
        if 'padx' in padding:
            base_config['padx'] = padding['padx']
        if 'pady' in padding:
            base_config['pady'] = padding['pady']
    
    # Apply state styling
    state_overrides = {}
    if state == 'disabled':
        state_overrides['state'] = 'disabled'
    elif state == 'highlight':
        # Highlight: brighter colors
        if 'bg' in base_config:
            state_overrides['bg'] = _brighten_color(base_config['bg'], 0.1)
        if 'activebackground' in base_config:
            state_overrides['activebackground'] = _brighten_color(base_config['activebackground'], 0.1)
    elif state == 'danger':
        # Danger: force red colors
        danger_config = get_button_config('red')
        state_overrides['bg'] = danger_config.get('bg', '#C62828')
        state_overrides['activebackground'] = danger_config.get('activebackground', '#B71C1C')
        state_overrides['fg'] = danger_config.get('fg', 'white')
        state_overrides['activeforeground'] = danger_config.get('activeforeground', 'white')
    
    # Merge all configs: base -> state -> user kwargs
    final_config = {
        **base_config,
        **state_overrides,
        **kwargs
    }
    
    # Create button with proper image/text handling
    if is_photoimage:
        # PhotoImage: use image= parameter
        if text:
            # Icon + text: use compound='left' to show both
            button = tk.Button(
                parent,
                image=icon,
                text=text,
                compound='left',
                command=command,
                **final_config
            )
        else:
            # Icon only: just image
            button = tk.Button(
                parent,
                image=icon,
                command=command,
                **final_config
            )
    else:
        # Emoji string: use text= parameter
        if text:
            button_text = f"{icon} {text}"
        else:
            button_text = icon
        button = tk.Button(
            parent,
            text=button_text,
            command=command,
            **final_config
        )
    
    # Store icon reference on button to prevent garbage collection
    if is_photoimage:
        button._icon_ref = icon  # type: ignore[attr-defined]
    
    # Store original icon name and size for hover restoration
    button._original_icon_name = icon_name  # type: ignore[attr-defined]
    button._original_icon_size = icon_size  # type: ignore[attr-defined]
    button._original_icon_fallback = icon_fallback  # type: ignore[attr-defined]
    
    # Auto hover effect for disabled buttons
    if auto_hover_disabled and (state == 'disabled' or kwargs.get('state') == 'disabled'):
        # Get forbidden icon for hover
        forbidden_icon = icon_helper.get_icon('forbidden', fallback='🚫', size=icon_size)
        is_forbidden_photoimage = not isinstance(forbidden_icon, str)
        
        # Store forbidden icon reference
        if is_forbidden_photoimage:
            button._forbidden_icon_ref = forbidden_icon  # type: ignore[attr-defined]
            _ICON_REFS.append(forbidden_icon)
        
        def _auto_hover_enter(event):
            """Show forbidden icon and cursor when hovering over disabled button."""
            if str(button['state']) == 'disabled':
                # Change icon and cursor to forbidden
                if is_forbidden_photoimage:
                    button.config(image=forbidden_icon, cursor='X_cursor')
                else:
                    button.config(text='🚫', cursor='X_cursor')
        
        def _auto_hover_leave(event):
            """Restore original icon and cursor when leaving disabled button."""
            if str(button['state']) == 'disabled':
                # Restore original icon and cursor
                if is_photoimage:
                    button.config(image=icon, cursor='arrow')
                else:
                    button.config(text=icon, cursor='arrow')
        
        # Bind auto hover events
        button.bind('<Enter>', _auto_hover_enter, add='+')
        button.bind('<Leave>', _auto_hover_leave, add='+')
    
    # Attach tooltip
    if tooltip_text:
        # Direct tooltip text
        _attach_simple_tooltip(button, tooltip_text)
    elif tooltip_key:
        # i18n tooltip
        attach_i18n_tooltip(
            button,
            tooltip_key,
            ns=tooltip_ns,
            lang_provider=get_lang
        )
    
    # Bind custom hover callbacks (will be added after auto hover)
    if on_hover:
        button.bind('<Enter>', on_hover, add='+')
    if on_leave:
        button.bind('<Leave>', on_leave, add='+')
    if on_focus:
        button.bind('<FocusIn>', on_focus)
    
    return button


def _brighten_color(hex_color: str, factor: float = 0.1) -> str:
    """
    Brighten a hex color by a factor.
    
    Args:
        hex_color: Hex color string (e.g., '#2E7D32')
        factor: Brightness factor (0.0-1.0, default: 0.1)
    
    Returns:
        str: Brightened hex color
    """
    try:
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Parse RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Brighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        # Return hex
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception:
        return hex_color  # Return original on error


def _attach_simple_tooltip(widget: Any, text: str, delay: int = 400):
    """
    Attach a simple tooltip to a widget.
    
    Args:
        widget: Widget to attach tooltip to
        text: Tooltip text
        delay: Delay before showing tooltip (ms)
    """
    tooltip_window = None
    after_id = None
    
    def show_tooltip(event):
        nonlocal after_id
        
        def _show():
            nonlocal tooltip_window
            x = event.x_root + 10
            y = event.y_root + 10
            
            tooltip_window = tk.Toplevel()
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                tooltip_window,
                text=text,
                background='#ffffe0',
                foreground='#000000',
                relief='solid',
                borderwidth=1,
                font=('Arial', 9),
                padx=6,
                pady=4
            )
            label.pack()
        
        # Delay showing tooltip
        after_id = widget.after(delay, _show)
    
    def hide_tooltip(event):
        nonlocal tooltip_window, after_id
        
        # Cancel delayed show
        if after_id:
            widget.after_cancel(after_id)
            after_id = None
        
        # Destroy tooltip window
        if tooltip_window:
            tooltip_window.destroy()
            tooltip_window = None
    
    widget.bind('<Enter>', show_tooltip)
    widget.bind('<Leave>', hide_tooltip)
    widget.bind('<Button>', hide_tooltip)  # Hide on click


# Convenience functions for common button types
def create_add_button(parent: Any, command: Callable, **kwargs) -> tk.Button:
    """Create an 'Add' button with icon."""
    return create_icon_button(
        parent=parent,
        icon_name='add',
        icon_fallback='➕',
        command=command,
        button_type='green_light',
        **kwargs
    )


def create_delete_button(parent: Any, command: Callable, **kwargs) -> tk.Button:
    """Create a 'Delete' button with icon."""
    return create_icon_button(
        parent=parent,
        icon_name='delete',
        icon_fallback='🗑️',
        command=command,
        button_type='red',
        **kwargs
    )


def create_save_button(parent: Any, command: Callable, **kwargs) -> tk.Button:
    """Create a 'Save' button with icon."""
    return create_icon_button(
        parent=parent,
        icon_name='save',
        icon_fallback='💾',
        command=command,
        button_type='green_light',
        **kwargs
    )


def create_cancel_button(parent: Any, command: Callable, **kwargs) -> tk.Button:
    """Create a 'Cancel' button with icon."""
    # Default to neutral gray style
    if 'button_type' not in kwargs:
        kwargs['button_type'] = 'refresh'  # Use refresh for neutral gray
    return create_icon_button(
        parent=parent,
        icon_name='cancel',
        icon_fallback='✖',
        command=command,
        **kwargs
    )


def create_refresh_button(parent: Any, command: Callable, **kwargs) -> tk.Button:
    """Create a 'Refresh' button with icon."""
    return create_icon_button(
        parent=parent,
        icon_name='refresh',
        icon_fallback='🔄',
        command=command,
        button_type='refresh',
        **kwargs
    )


def create_icon_label(
    parent: Any,
    icon_name: str,
    text: str = '',
    icon_fallback: str = '❓',
    icon_size: int = 16,
    tooltip_text: Optional[str] = None,
    tooltip_key: Optional[str] = None,
    tooltip_ns: Optional[str] = None,
    font: Optional[tuple] = None,
    fg: Optional[str] = None,
    bg: Optional[str] = None,
    **kwargs
) -> tk.Label:
    """
    Create a label with icon and text.
    
    Args:
        parent: Parent widget
        icon_name: Icon name (e.g., 'monster', 'list', 'info')
        text: Label text (optional)
        icon_fallback: Fallback emoji if icon not found
        icon_size: Icon size in pixels (default: 16)
        tooltip_text: Direct tooltip text (optional)
        tooltip_key: i18n tooltip key (optional)
        tooltip_ns: i18n namespace for tooltip (optional)
        font: Font tuple (family, size, weight), uses UI.FONT_LABEL if None
        fg: Foreground color, uses UI.COLOR_TEXT if None
        bg: Background color, uses UI.BG_DEFAULT if None
        **kwargs: Additional Label configuration
    
    Returns:
        tk.Label: Configured label with icon and text
    
    Example:
        # Simple icon label
        label = create_icon_label(
            parent=frame,
            icon_name='monster',
            text='Monster Name:',
            tooltip_text='Enter the monster name'
        )
        
        # Title with icon
        title = create_icon_label(
            parent=frame,
            icon_name='list',
            text='Monster List',
            font=('Segoe UI', 11, 'bold'),
            fg='#0D47A1'
        )
    """
    # Get default styles
    try:
        from lib.ui_style import UIStyle as UI
    except ImportError:
        # Fallback UIStyle
        class UIStyle:
            FONT_LABEL = ('Segoe UI', 10)
            COLOR_TEXT = '#333'
            BG_DEFAULT = '#FFFFFF'
        UI = UIStyle
    
    # Get icon
    icon = icon_helper.get_icon(icon_name, fallback=icon_fallback, size=icon_size)
    
    # Determine if icon is PhotoImage or emoji string
    is_photoimage = not isinstance(icon, str)
    
    # Keep icon reference to prevent garbage collection
    if is_photoimage:
        _ICON_REFS.append(icon)
    
    # Apply default styles
    label_config = {
        'font': font or UI.FONT_LABEL,
        'fg': fg or UI.COLOR_TEXT,
        'bg': bg or UI.BG_DEFAULT
    }
    
    # Merge with user kwargs
    label_config.update(kwargs)
    
    # Create label with proper image/text handling
    if is_photoimage:
        # PhotoImage: use image= and compound='left'
        if text:
            label = tk.Label(
                parent,
                image=icon,
                text=text,
                compound='left',
                **label_config
            )
        else:
            # Icon only
            label = tk.Label(
                parent,
                image=icon,
                **label_config
            )
        # Store icon reference on label
        label._icon_ref = icon  # type: ignore[attr-defined]
    else:
        # Emoji string: use text= parameter
        if text:
            label_text = f"{icon} {text}"
        else:
            label_text = icon
        label = tk.Label(
            parent,
            text=label_text,
            **label_config
        )
    
    # Attach tooltip
    if tooltip_text:
        # Direct tooltip text
        _attach_simple_tooltip(label, tooltip_text)
    elif tooltip_key:
        # i18n tooltip
        attach_i18n_tooltip(
            label,
            tooltip_key,
            ns=tooltip_ns,
            lang_provider=get_lang
        )
    
    return label


# Utility functions for button state management
def update_button_state(
    button: tk.Button,
    enabled: bool,
    icon_name: Optional[str] = None,
    icon_fallback: str = '',
    icon_size: int = 16,
    tooltip_text: Optional[str] = None
) -> None:
    """
    Update button state and icon dynamically.
    
    When disabled, automatically changes icon to forbidden symbol.
    
    Args:
        button: Button widget to update
        enabled: Whether button should be enabled
        icon_name: New icon name (optional, keeps current if None)
        icon_fallback: Fallback emoji for new icon
        icon_size: Icon size in pixels
        tooltip_text: New tooltip text (optional)
    
    Example:
        # Disable button and change icon to forbidden
        update_button_state(save_btn, enabled=False, tooltip_text='No changes to save')
        
        # Enable button and restore icon
        update_button_state(save_btn, enabled=True, icon_name='save', tooltip_text='Save changes')
        
        # Just disable without changing icon
        update_button_state(stop_btn, enabled=False)
    """
    # Determine icon to use
    if enabled:
        # Enabled: use specified icon or keep current
        if icon_name:
            icon = icon_helper.get_icon(icon_name, fallback=icon_fallback, size=icon_size)
        else:
            # Keep current icon if available
            icon = getattr(button, '_icon_ref', None)
            if not icon:
                return  # Can't update icon, just update state
    else:
        # Disabled: use forbidden icon
        icon = icon_helper.get_icon('forbidden', fallback='🚫', size=icon_size)
        if not tooltip_text:
            lang = get_lang()
            if lang == 'vi':
                tooltip_text = 'Không khả dụng'
            else:
                tooltip_text = 'Not available'
    
    # Update button state
    button.config(state='normal' if enabled else 'disabled')
    
    # Update icon
    is_photoimage = not isinstance(icon, str)
    if is_photoimage:
        button.config(image=icon)
        button._icon_ref = icon  # type: ignore[attr-defined]
        _ICON_REFS.append(icon)  # Prevent garbage collection
    else:
        button.config(text=icon)
    
    # Update tooltip if provided
    if tooltip_text:
        # Remove old tooltip bindings
        button.unbind('<Enter>')
        button.unbind('<Leave>')
        button.unbind('<Button>')
        # Attach new tooltip
        _attach_simple_tooltip(button, tooltip_text)


def set_button_enabled(button: tk.Button, enabled: bool, tooltip: Optional[str] = None) -> None:
    """
    Simple helper to enable/disable button with automatic icon change.
    
    Args:
        button: Button to update
        enabled: True to enable, False to disable (shows forbidden icon)
        tooltip: Optional tooltip text
    
    Example:
        # Disable save button
        set_button_enabled(save_btn, False, 'No changes to save')
        
        # Enable save button
        set_button_enabled(save_btn, True, 'Save changes')
    """
    update_button_state(button, enabled=enabled, tooltip_text=tooltip)


def set_button_icon(button: tk.Button, icon_name: str, fallback: str = '', size: int = 16) -> None:
    """
    Change button icon without affecting state.
    
    Args:
        button: Button to update
        icon_name: New icon name
        fallback: Fallback emoji
        size: Icon size
    
    Example:
        # Change to save icon
        set_button_icon(btn, 'save', '💾')
        
        # Change to loading icon
        set_button_icon(btn, 'loading', '⏳')
    """
    icon = icon_helper.get_icon(icon_name, fallback=fallback, size=size)
    is_photoimage = not isinstance(icon, str)
    
    if is_photoimage:
        button.config(image=icon)
        button._icon_ref = icon  # type: ignore[attr-defined]
        _ICON_REFS.append(icon)
    else:
        button.config(text=icon)

