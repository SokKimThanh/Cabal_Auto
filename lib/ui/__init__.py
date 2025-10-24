"""
lib.ui - DEPRECATED

This package has been reorganized and moved to ui/.

**Migration Guide:**

All modules have been moved:
- Helper utilities → ui/helpers/
- Windows & dialogs → ui/windows/
- Utility functions → ui/utils/
- Components → ui/components/

**New import paths:**
```python
# Old
from lib.ui.icon_helper import IconHelper
from lib.ui.button_styles import get_button_config
from lib.ui.tooltip import attach_i18n_tooltip
from lib.ui.library_manager import LibraryManagerWindow

# New
from ui.helpers import IconHelper, get_button_config, attach_i18n_tooltip
from ui.windows.library_manager import LibraryManagerWindow
```

Please update your imports to use the new structure.
See docs/UI_PACKAGE_REORGANIZATION.md for details.
"""

# NOTE:
# This package and several UI modules intentionally keep Python-side
# references to Tkinter PhotoImage objects (for example `self._image_refs`)
# to prevent Tcl/Tk garbage-collection of images. Some older code also
# used dynamic attributes on widget/root objects (e.g. `root._image_refs`).
# Those uses are intentional and annotated with `# type: ignore[attr-defined]`
# where necessary to keep static analyzers happy while preserving runtime
# behavior. Prefer storing images in the owning window's `_image_refs` list.

