# UI Utils

UI utility functions for the Cabal Auto Manager application.

## Modules

### detection_converter.py
Detection format converter for converting between different detection formats.

### overlay_controller.py
Overlay window controller for managing overlay window lifecycle.

### overlay_settings.py
Overlay settings management for saving and loading overlay preferences.

### window_tracker.py
Window tracking utilities for tracking game window position and state.

### win_input.py
Windows input simulation utilities for sending keyboard/mouse events to the game.

## Migration from ui/ and lib/ui

All utility modules have been consolidated into `ui/utils/` for better organization.

**Old imports:**
```python
from ui.utils.overlay_controller import OverlayController
from ui.win_input import send_key
```

**New imports:**
```python
from ui.utils.overlay_controller import OverlayController
from ui.utils.win_input import send_key
```
