# UI Helpers

UI helper utilities for the Cabal Auto Manager application.

## Modules

### button_styles.py
Global button styling configuration with predefined color schemes.

**Usage:**
```python
from ui.helpers import get_button_config

config = get_button_config('green_light')
button = tk.Button(parent, text='Save', **config)
```

### icon_helper.py
Icon loading with automatic fallback to emoji when icon files are not available.

**Usage:**
```python
from ui.helpers import IconHelper

icon_helper = IconHelper()
icon = icon_helper.get_icon('save', fallback='💾', size=16)
```

### tooltip.py
i18n-enabled tooltip widgets.

**Usage:**
```python
from ui.helpers import attach_i18n_tooltip

attach_i18n_tooltip(button, key='btn_save', ns='app', lang_provider=get_lang)
```

### capture_helper.py
Screen capture utilities for template matching.

**Usage:**
```python
from ui.helpers.capture_helper import capture_region_and_save

capture_region_and_save(x, y, width, height, output_path)
```

## Migration from lib.ui

All helper modules have been moved from `lib/ui/` to `ui/helpers/` for better organization.

**Old imports:**
```python
from lib.ui.icon_helper import IconHelper
from lib.ui.button_styles import get_button_config
from lib.ui.tooltip import attach_i18n_tooltip
```

**New imports:**
```python
from ui.helpers import IconHelper, get_button_config, attach_i18n_tooltip
```
