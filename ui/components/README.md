# Icon Button Component Documentation

## Overview

The `icon_button` component provides a standardized, reusable way to create buttons with icons throughout the application. It integrates with global styling systems and provides advanced features like state management, tooltips, and callbacks.

## Location

```
ui/components/
├── __init__.py          # Package exports
├── icon_button.py       # Component implementation
└── demo_icon_button.py  # Demo & usage examples
```

## Features

### ✅ Global Integration
- **Icon System**: Uses `lib.ui.icon_helper.IconHelper` for consistent icons
- **Button Styles**: Uses `lib.ui.button_styles.get_button_config()` for theme colors
- **Tooltips**: Uses `lib.ui.tooltip.attach_i18n_tooltip()` for i18n tooltips
- **i18n**: Supports internationalized text and tooltips

### ✅ State Management
- `normal`: Default button state
- `disabled`: Non-clickable, grayed out
- `highlight`: Brighter colors for emphasis
- `danger`: Forces red danger styling (overrides button_type)

### ✅ Button Types
- `green_light`: Success/positive actions (save, add, confirm)
- `red`: Danger/destructive actions (delete, remove)
- `blue`: Info/neutral actions (edit, view, details)
- `orange`: Warning actions (settings, config)
- `refresh`: Neutral gray (cancel, refresh)

### ✅ Size Variants
- `compact`: Minimal padding (width=0, padx=2, pady=2)
- `small`: Small button (width=8, padx=4, pady=4)
- `medium`: Default size (width=12, padx=8, pady=6)
- `large`: Large button (width=16, padx=12, pady=8)
- `text`: Text-only, no border (width=0, padx=0, pady=0, flat relief)

### ✅ Event Callbacks
- `on_hover`: Called when mouse enters button
- `on_leave`: Called when mouse leaves button
- `on_focus`: Called when button receives focus

### ✅ Tooltip Support
- i18n tooltips with translation keys
- Direct text tooltips
- Automatic attachment and cleanup

### ✅ Icon Reference Management
- Automatic prevention of garbage collection
- Global reference storage
- Per-button reference storage

## API Reference

### Main Function

```python
create_icon_button(
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
) -> tk.Button
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | `tk.Widget` | Required | Parent widget for button |
| `icon_name` | `str` | Required | Icon name from icon_helper (e.g., 'add', 'delete') |
| `command` | `Callable` | Required | Button click callback |
| `text` | `str` | `None` | Optional button text (icon prepended if provided) |
| `button_type` | `str` | `'green_light'` | Button style type |
| `icon_size` | `int` | `16` | Icon size in pixels |
| `icon_fallback` | `str` | `''` | Fallback emoji if icon not found |
| `tooltip_key` | `str` | `None` | i18n key for tooltip |
| `tooltip_ns` | `str` | `None` | i18n namespace for tooltip |
| `tooltip_text` | `str` | `None` | Direct tooltip text (overrides tooltip_key) |
| `state` | `str` | `'normal'` | Button state |
| `variant` | `str` | `None` | Size variant |
| `width` | `int` | `None` | Custom button width |
| `padding` | `dict` | `None` | Custom padding {'padx': int, 'pady': int} |
| `on_hover` | `Callable` | `None` | Hover callback (receives event) |
| `on_leave` | `Callable` | `None` | Leave callback (receives event) |
| `on_focus` | `Callable` | `None` | Focus callback (receives event) |
| `**kwargs` | `Any` | - | Additional button config (overrides defaults) |

#### Returns

`tk.Button`: Configured button with icon and styles

### Convenience Functions

Pre-configured button creators for common actions:

```python
create_add_button(parent, command, **kwargs) -> tk.Button
create_delete_button(parent, command, **kwargs) -> tk.Button
create_save_button(parent, command, **kwargs) -> tk.Button
create_cancel_button(parent, command, **kwargs) -> tk.Button
create_refresh_button(parent, command, **kwargs) -> tk.Button
```

All accept the same parameters as `create_icon_button()` but with pre-configured `icon_name`, `icon_fallback`, and `button_type`.

## Usage Examples

### Basic Examples

#### 1. Simple Icon Button
```python
from ui.components import create_icon_button

btn = create_icon_button(
    parent=frame,
    icon_name='add',
    command=on_add,
    button_type='green_light',
    tooltip_text='Add new item'
)
```

#### 2. Icon Button with Text
```python
btn = create_icon_button(
    parent=frame,
    icon_name='save',
    text='Save All',
    command=on_save,
    button_type='green_light',
    variant='medium',
    tooltip_text='Save all changes'
)
```

#### 3. Icon-Only Compact Button
```python
btn = create_icon_button(
    parent=toolbar,
    icon_name='delete',
    command=on_delete,
    button_type='red',
    variant='compact',
    tooltip_text='Delete item'
)
```

### Advanced Examples

#### 4. Danger State Button
```python
btn = create_icon_button(
    parent=frame,
    icon_name='delete',
    text='Delete All',
    command=on_delete_all,
    state='danger',  # Forces red styling
    tooltip_text='Delete all items (cannot be undone)'
)
```

#### 5. Button with Hover Callback
```python
def on_hover(event):
    status_label.config(text='Hovering over save button')

def on_leave(event):
    status_label.config(text='Ready')

btn = create_icon_button(
    parent=frame,
    icon_name='save',
    text='Save',
    command=on_save,
    button_type='green_light',
    on_hover=on_hover,
    on_leave=on_leave,
    tooltip_text='Save changes'
)
```

#### 6. i18n Tooltip Button
```python
btn = create_icon_button(
    parent=frame,
    icon_name='add',
    command=on_add,
    button_type='green_light',
    tooltip_key='btn_add',  # Translation key
    tooltip_ns='monster_editor'  # Namespace
)
```

#### 7. Custom Styling
```python
btn = create_icon_button(
    parent=frame,
    icon_name='save',
    text='Custom',
    command=on_save,
    button_type='blue',
    width=20,  # Custom width
    padding={'padx': 15, 'pady': 10},  # Custom padding
    font=('Arial', 12, 'bold'),  # Custom font via kwargs
    tooltip_text='Customized button'
)
```

#### 8. Convenience Functions
```python
from ui.components import (
    create_add_button,
    create_delete_button,
    create_save_button,
    create_cancel_button
)

# Pre-configured buttons
add_btn = create_add_button(frame, command=on_add, text='Add Item')
delete_btn = create_delete_button(frame, command=on_delete, text='Delete')
save_btn = create_save_button(frame, command=on_save, text='Save')
cancel_btn = create_cancel_button(frame, command=on_cancel, text='Cancel')
```

### Real-World Example: Toolbar

```python
import tkinter as tk
from ui.components import create_icon_button

def create_toolbar(parent):
    toolbar = tk.Frame(parent, bg='#e0e0e0', height=40)
    toolbar.pack(fill='x', side='top')
    
    # Icon-only compact buttons for toolbar
    create_icon_button(
        toolbar,
        icon_name='add',
        command=on_add,
        button_type='green_light',
        variant='compact',
        tooltip_text='Add new item'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        toolbar,
        icon_name='delete',
        command=on_delete,
        button_type='red',
        variant='compact',
        tooltip_text='Delete selected'
    ).pack(side='left', padx=2, pady=5)
    
    create_icon_button(
        toolbar,
        icon_name='refresh',
        command=on_refresh,
        button_type='refresh',
        variant='compact',
        tooltip_text='Refresh list'
    ).pack(side='left', padx=2, pady=5)
    
    # Separator
    tk.Frame(toolbar, width=2, bg='#c0c0c0').pack(side='left', fill='y', padx=5, pady=5)
    
    create_icon_button(
        toolbar,
        icon_name='settings',
        command=on_settings,
        button_type='orange',
        variant='compact',
        tooltip_text='Settings'
    ).pack(side='left', padx=2, pady=5)
```

### Real-World Example: Form Buttons

```python
import tkinter as tk
from ui.components import create_save_button, create_cancel_button

def create_form_actions(parent):
    actions_frame = tk.Frame(parent)
    actions_frame.pack(fill='x', side='bottom', pady=10)
    
    # Save button - right side
    create_save_button(
        actions_frame,
        command=on_save,
        text='Save Changes',
        variant='medium',
        tooltip_text='Save all form changes'
    ).pack(side='right', padx=5)
    
    # Cancel button - right side
    create_cancel_button(
        actions_frame,
        command=on_cancel,
        text='Cancel',
        variant='medium',
        tooltip_text='Discard changes'
    ).pack(side='right', padx=5)
```

## Migration Guide

### From Manual Button Creation

**Before:**
```python
# Old manual way
from lib.ui.icon_helper import IconHelper
from lib.ui.button_styles import get_button_config
from lib.ui.tooltip import attach_i18n_tooltip

icon_helper = IconHelper()
save_icon = icon_helper.get_icon('save', fallback='💾')
save_config = get_button_config('green_light')

save_button = tk.Button(
    parent,
    text=f"{save_icon} Save",
    command=on_save,
    **save_config
)
save_button.icon = save_icon  # Prevent garbage collection
attach_i18n_tooltip(save_button, 'btn_save', ns='app', lang_provider=get_lang)
```

**After:**
```python
# New component way
from ui.components import create_icon_button

save_button = create_icon_button(
    parent,
    icon_name='save',
    text='Save',
    command=on_save,
    button_type='green_light',
    tooltip_key='btn_save',
    tooltip_ns='app'
)
```

### From app_gui._create_icon_button()

**Before:**
```python
# Old class method
btn = self._create_icon_button(
    parent=frame,
    icon_emoji='💾',
    command=on_save,
    style='medium',
    bg_color=UI.BTN_PRIMARY_BG
)
```

**After:**
```python
# New component function
from ui.components import create_icon_button

btn = create_icon_button(
    parent=frame,
    icon_name='save',
    icon_fallback='💾',
    command=on_save,
    button_type='green_light',
    variant='medium'
)
```

## Best Practices

### 1. Choose Appropriate Button Type
```python
# Success actions
create_icon_button(..., button_type='green_light')  # save, add, confirm

# Danger actions
create_icon_button(..., button_type='red')  # delete, remove

# Info actions
create_icon_button(..., button_type='blue')  # edit, view, details

# Warning actions
create_icon_button(..., button_type='orange')  # settings, config

# Neutral actions
create_icon_button(..., button_type='refresh')  # cancel, refresh
```

### 2. Use Variants Consistently
```python
# Toolbar: compact buttons
create_icon_button(..., variant='compact')

# Forms: medium buttons
create_icon_button(..., variant='medium')

# Primary actions: large buttons
create_icon_button(..., variant='large')
```

### 3. Always Provide Tooltips
```python
# Good: User knows what button does
create_icon_button(
    ...,
    tooltip_text='Save all changes'
)

# Bad: No tooltip, icon-only button unclear
create_icon_button(...)
```

### 4. Use State for Context
```python
# Danger action confirmation
create_icon_button(
    ...,
    text='Delete All',
    state='danger',  # Red warning
    tooltip_text='Cannot be undone'
)

# Disabled during operation
button = create_icon_button(...)
# ... later
button.config(state='disabled')
```

### 5. Use Convenience Functions
```python
# Good: Clear intent
from ui.components import create_save_button, create_cancel_button

save_btn = create_save_button(frame, command=on_save)
cancel_btn = create_cancel_button(frame, command=on_cancel)

# Also good: Explicit configuration
create_icon_button(frame, icon_name='save', command=on_save, button_type='green_light')
```

## Testing

### Run Demo
```bash
cd ui/components
python demo_icon_button.py
```

The demo shows:
1. All button types (green_light, red, blue, orange, refresh)
2. All size variants (compact, small, medium, large, text)
3. All states (normal, highlight, danger, disabled)
4. Icon-only buttons
5. Event callbacks (hover, leave, focus)
6. Convenience functions
7. Custom styling (width, padding, font)

### Manual Testing Checklist
- [ ] Icons load correctly (no pyImage errors)
- [ ] Button colors match button_type
- [ ] Hover effects work
- [ ] Tooltips appear on hover
- [ ] Callbacks trigger on events
- [ ] Disabled state prevents clicks
- [ ] All variants have correct sizes
- [ ] Text and icon-only buttons both work
- [ ] Custom styling overrides work
- [ ] i18n tooltips translate correctly

## Architecture

### Component Structure
```
icon_button.py
├── create_icon_button()        # Main function
├── _brighten_color()           # Color utility
├── _attach_simple_tooltip()    # Simple tooltip helper
├── Convenience Functions:
│   ├── create_add_button()
│   ├── create_delete_button()
│   ├── create_save_button()
│   ├── create_cancel_button()
│   └── create_refresh_button()
└── Global State:
    └── _ICON_REFS               # Icon reference storage
```

### Integration Points

**Icon System** (`lib.ui.icon_helper`):
- `IconHelper.get_icon()` - Load icons by name
- Fallback to emojis if icon not found

**Button Styles** (`lib.ui.button_styles`):
- `get_button_config()` - Get themed button config
- 5 button types: green_light, red, blue, orange, refresh

**Tooltips** (`lib.ui.tooltip`):
- `attach_i18n_tooltip()` - Attach i18n tooltips
- Simple tooltip fallback for plain text

**i18n** (`lib.i18n`):
- `t()` - Translate keys
- `get_lang()` - Get current language

### Reference Management

Icons are stored in two places to prevent garbage collection:

1. **Global Storage**: `_ICON_REFS` list stores all icons
2. **Button Attribute**: `button._icon_ref` stores icon on button

This ensures icons survive Python's garbage collector and don't show as "pyImage4".

## Troubleshooting

### Icons Show as "pyImage4"
**Cause**: Icon garbage collected
**Solution**: Already handled by component - icons stored in `_ICON_REFS` and `button._icon_ref`

### Tooltip Not Showing
**Cause**: Missing tooltip parameter
**Solution**: Add `tooltip_text` or `tooltip_key` parameter

### Wrong Button Colors
**Cause**: Wrong `button_type` parameter
**Solution**: Use correct type: 'green_light', 'red', 'blue', 'orange', 'refresh'

### Button Too Small/Large
**Cause**: Wrong `variant` parameter
**Solution**: Use correct variant: 'compact', 'small', 'medium', 'large'

### State Not Applying
**Cause**: Wrong `state` parameter or tkinter state conflict
**Solution**: 
- Use component `state` parameter for initial state
- Use `button.config(state='disabled')` for runtime changes

## Future Enhancements

### Planned Features
- [ ] Loading state with spinner
- [ ] Badge/notification dot
- [ ] Icon + text layout options (icon left/right/top/bottom)
- [ ] Animation effects (pulse, shake, bounce)
- [ ] Long-press support
- [ ] Button groups (toggle, radio)
- [ ] Async command support
- [ ] Progress indicator

### Integration Opportunities
- [ ] Command palette integration
- [ ] Keyboard shortcut display
- [ ] Undo/redo support
- [ ] Accessibility improvements
- [ ] Theme switching support

## References

- **icon_helper.py**: Icon loading and management
- **button_styles.py**: Global button theming
- **tooltip.py**: Tooltip system
- **i18n.py**: Internationalization
- **ui_style.py**: UI constants and guidelines

## Changelog

### v1.0.0 (Current)
- ✅ Initial release
- ✅ Full icon_helper integration
- ✅ Full button_styles integration
- ✅ Tooltip support (i18n and plain text)
- ✅ State management (normal, disabled, highlight, danger)
- ✅ Size variants (compact, small, medium, large, text)
- ✅ Event callbacks (hover, leave, focus)
- ✅ Reference management (prevent GC)
- ✅ Convenience functions
- ✅ Custom styling support
- ✅ Demo application
- ✅ Comprehensive documentation
