# Game Window Mode Selector Component

Reusable Tkinter component for controlling game window display position relative to the application window.

## Features

- **3 Display Modes:**
  - `none` - No game window (screen off 🚫)
  - `below` - Game window appears below app (⬇️)
  - `above` - Game window appears above app/topmost (⬆️)

- **Auto-save Configuration:** Automatically saves selected mode to `hunt_config.json`
- **Visual Feedback:** Icon indicators for each mode
- **Callback Support:** Optional callback function triggered on mode change
- **Flexible Layout:** Can be used with pack(), grid(), or place()
- **Tooltip Support:** Built-in tooltip with customizable text
- **Fully Encapsulated:** Self-contained with no external dependencies (except Tkinter)

## Installation

Component is located at: `ui/components/game_window_mode_selector.py`

No additional installation required - pure Tkinter implementation.

## Basic Usage

```python
from ui.components.game_window_mode_selector import create_game_window_mode_selector

# Create selector
selector = create_game_window_mode_selector(
    parent=frame,
    config_path="lib/data/hunt_config.json"
)

# Layout
selector.pack(side='left', padx=10)
```

## Advanced Usage

### With Callback

```python
def on_mode_changed(mode: str):
    """Handle mode changes."""
    print(f"Mode changed to: {mode}")
    if mode == "above":
        launch_game_topmost()
    elif mode == "below":
        launch_game_below()
    elif mode == "none":
        close_game()

selector = create_game_window_mode_selector(
    parent=frame,
    config_path="lib/data/hunt_config.json",
    on_mode_change=on_mode_changed
)
```

### Custom Appearance

```python
selector = create_game_window_mode_selector(
    parent=frame,
    config_path="lib/data/hunt_config.json",
    initial_mode="below",           # Start with "below" selected
    icon_size=20,                   # Larger icons
    show_label=True,                # Show "Game:" label
    label_text="Display:",          # Custom label text
    tooltip_text="Choose window position"  # Custom tooltip
)
```

### Programmatic Control

```python
# Get current mode
current = selector.get_mode()  # Returns: 'none', 'below', or 'above'

# Set mode programmatically
selector.set_mode('above')
```

## API Reference

### `create_game_window_mode_selector()`

Factory function to create a selector instance.

**Parameters:**
- `parent` (Widget) - Parent Tkinter widget
- `config_path` (str) - Path to hunt_config.json (default: "lib/data/hunt_config.json")
- `on_mode_change` (Callable[[str], None] | None) - Callback function called when mode changes
- `initial_mode` (str) - Initial mode: 'none', 'below', or 'above' (default: 'none')
- `icon_size` (int) - Size of mode indicator icons (default: 16)
- `show_label` (bool) - Whether to show label (default: True)
- `label_text` (str) - Label text (default: "Game:")
- `tooltip_text` (str) - Tooltip text (default: Vietnamese text)

**Returns:** `GameWindowModeSelector` instance

### `GameWindowModeSelector` Class Methods

#### `get_mode() -> str`
Returns current mode: 'none', 'below', or 'above'

#### `set_mode(mode: str) -> None`
Sets mode programmatically. Valid values: 'none', 'below', 'above'

#### `pack(**kwargs) -> None`
Pack the selector using Tkinter pack geometry manager

#### `grid(**kwargs) -> None`
Grid the selector using Tkinter grid geometry manager

#### `place(**kwargs) -> None`
Place the selector using Tkinter place geometry manager

## Configuration File

The component reads/writes to `hunt_config.json`:

```json
{
  "game_window_mode": "none"
}
```

Valid values: `"none"`, `"below"`, `"above"`

## Examples

### Example 1: Quick Integration

```python
import tkinter as tk
from ui.components.game_window_mode_selector import create_game_window_mode_selector

root = tk.Tk()
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

selector = create_game_window_mode_selector(parent=frame)
selector.pack()

root.mainloop()
```

### Example 2: Multiple Selectors

```python
# Main game window selector
selector1 = create_game_window_mode_selector(
    parent=frame1,
    config_path="lib/data/main_config.json",
    label_text="Main Game:"
)

# Secondary window selector
selector2 = create_game_window_mode_selector(
    parent=frame2,
    config_path="lib/data/secondary_config.json",
    label_text="Secondary:"
)
```

### Example 3: Integration with Quick Monster Editor

```python
# In _create_top_panel()
self.game_mode_selector = create_game_window_mode_selector(
    parent=top_frame,
    config_path=str(self.hunt_config_path),
    on_mode_change=self._on_game_mode_change,
    initial_mode=self.game_window_mode_var.get(),
    show_label=True,
    label_text=i18n_t('label_game_mode', ns='monster_editor', default='Game:'),
    tooltip_text=i18n_t('tooltip_game_mode', ns='monster_editor', 
                       default='Chọn cách hiển thị cửa sổ game')
)
self.game_mode_selector.pack(side='left', padx=(15, 0), pady=15)
```

## Demo

Run the interactive demo to see all features:

```bash
python tests/demos/demo_game_window_mode_selector.py
```

Demo includes:
1. Basic usage
2. With callback function
3. Multiple selectors in one window
4. Programmatic control

## Architecture

```
GameWindowModeSelector
├── container (Frame)
│   ├── label (Label) - Optional "Game:" text
│   ├── mode_combo (Combobox) - Dropdown selector
│   └── icon_label (Label) - Visual mode indicator
└── Methods
    ├── _load_mode_from_config() - Load from JSON
    ├── _save_mode_to_config() - Save to JSON
    ├── _on_mode_selected() - Handle selection
    ├── get_mode() - Public API
    └── set_mode() - Public API
```

## Styling

Component inherits background color from parent widget. Default styling:
- Font: Segoe UI, 9pt
- Combobox width: 10 characters
- Icon size: Configurable (default 16)
- Tooltip: Light yellow background

## Translation Support

For i18n integration, pass translated strings:

```python
selector = create_game_window_mode_selector(
    parent=frame,
    label_text=i18n_t('label_game_mode', ns='monster_editor', default='Game:'),
    tooltip_text=i18n_t('tooltip_game_mode', ns='monster_editor', 
                       default='Choose game window display mode')
)
```

## Testing

Component is tested in:
- `tests/demos/demo_game_window_mode_selector.py` - Interactive demo
- `ui/windows/quick_monster_editor.py` - Real-world integration

## Troubleshooting

**Q: Mode not persisting after restart?**  
A: Check that `config_path` points to the correct `hunt_config.json` file.

**Q: Callback not firing?**  
A: Ensure callback function signature is `def callback(mode: str):` with one parameter.

**Q: Icons not showing?**  
A: Icons are emoji characters (🚫, ⬇️, ⬆️). Ensure your system supports emoji rendering.

**Q: Component not visible?**  
A: Make sure to call `.pack()`, `.grid()`, or `.place()` after creation.

## License

Part of Cabal_Auto project.

## Author

SokKimThanh  
Created: 2025-10-24
