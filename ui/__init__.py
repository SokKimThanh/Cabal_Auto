"""
UI Package

Main UI package for Cabal Auto Manager.

Structure:
- components/: Reusable UI components (buttons, labels, etc.)
- helpers/: UI helper utilities (icon_helper, button_styles, tooltip)
- windows/: Main window and dialog classes
- utils/: UI utility functions

Migration Notes:
- All modules from lib/ui/ have been moved to ui/helpers/ or ui/utils/
- All main windows are now in ui/windows/
- Use new import paths for better organization
"""

__version__ = "2.0.0"

# Component exports
from .components import create_icon_button, create_icon_label

# Helper exports
from .helpers import (
    get_button_config,
    IconHelper,
    get_icon_helper,
    attach_i18n_tooltip,
)

__all__ = [
    # Components
    "create_icon_button",
    "create_icon_label",
    # Helpers
    "get_button_config",
    "IconHelper",
    "get_icon_helper",
    "attach_i18n_tooltip",
]
