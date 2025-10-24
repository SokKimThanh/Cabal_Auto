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
    command: Callable,
    text: Optional[str] = None,
    button_type: str = 'green_light',
    icon_size: int = 16,
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
        icon_size: Icon size in pixels (default: 16)
        icon_fallback: Fallback emoji if icon not found
        tooltip_key: i18n key for tooltip
        tooltip_ns: i18n namespace for tooltip
        tooltip_text: Direct tooltip text (overrides tooltip_key)
        state: Button state ('normal', 'disabled', 'highlight', 'danger')
        variant: Button variant ('compact', 'small', 'medium', 'large', 'text')
        width: Custom button width (overrides variant width)
        padding: Custom padding dict {'padx': int, 'pady': int}
        on_hover: Callback when mouse enters button (event)
        on_leave: Callback when mouse leaves button (event)
        on_focus: Callback when button receives focus (event)
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
    
    # Apply custom width
    if width is not None:
        base_config['width'] = width
    
    # Apply custom padding
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
    
    # Bind hover callbacks
    if on_hover:
        button.bind('<Enter>', on_hover)
    if on_leave:
        button.bind('<Leave>', on_leave)
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
        nonlocal tooltip_window, after_id
        
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
