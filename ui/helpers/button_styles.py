"""
Button Style Roles Helper (Migration to TTK Styles)

This module provides semantic role-based configuration for buttons.
It transitions away from hard-coded fonts and colors in favor of ttk style tokens.
"""

from lib.ui_style import UIStyle

# Map semantic roles to ttk styles
# These correspond to styles defined in ui.theme.ttk_theme
ROLE_STYLES = {
    "primary": "Primary.TButton",
    "success": "Primary.TButton",  # Alias for backward compatibility
    "green": "Primary.TButton",  # Alias
    "green_light": "Primary.TButton",  # Alias
    "danger": "Danger.TButton",
    "red": "Danger.TButton",  # Alias
    "info": "Info.TButton",
    "blue": "Info.TButton",  # Alias
    "refresh": "Info.TButton",  # Alias
    "warning": "Warning.TButton",
    "orange": "Warning.TButton",  # Alias
    "neutral": "Neutral.TButton",
    "icon": "Icon.TButton",
}


def get_button_config(button_type: str) -> dict:
    """
    Get legacy button configuration for a specific semantic role.

    Args:
        button_type: Semantic role (e.g., 'primary', 'danger', 'info', 'neutral', 'warning', 'icon', or legacy colors)

    Returns:
        dict: Button configuration dict compatible with tk.Button, maintaining API compatibility
              but mapping to DS1 UIStyle tokens.
    """
    # Legacy colors mapping to DS1 for tk.Button compatibility
    configs = {
        "green": {
            "bg": UIStyle.THEME_STATE_HUNTING,
            "fg": UIStyle.THEME_BG_APP,
            "activebackground": UIStyle.THEME_STATE_HUNTING_BORDER,
            "activeforeground": UIStyle.THEME_BG_APP,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "green_light": {
            "bg": UIStyle.THEME_STATE_HUNTING,
            "fg": UIStyle.THEME_BG_APP,
            "activebackground": UIStyle.THEME_STATE_HUNTING_BORDER,
            "activeforeground": UIStyle.THEME_BG_APP,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "red": {
            "bg": UIStyle.THEME_STATE_DANGER,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": "#b91c1c",
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "blue": {
            "bg": UIStyle.THEME_STATE_INFO,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": "#2563eb",
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "refresh": {
            "bg": UIStyle.THEME_STATE_INFO,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": "#2563eb",
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_SMALL),
            "relief": "raised",
            "bd": 1,
            "cursor": "hand2",
        },
        "orange": {
            "bg": UIStyle.THEME_STATE_READY,
            "fg": UIStyle.THEME_BG_APP,
            "activebackground": "#ca8a04",
            "activeforeground": UIStyle.THEME_BG_APP,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "primary": {
            "bg": UIStyle.THEME_STATE_HUNTING,
            "fg": UIStyle.THEME_BG_APP,
            "activebackground": UIStyle.THEME_STATE_HUNTING_BORDER,
            "activeforeground": UIStyle.THEME_BG_APP,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "danger": {
            "bg": UIStyle.THEME_STATE_DANGER,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": "#b91c1c",
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "info": {
            "bg": UIStyle.THEME_STATE_INFO,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": "#2563eb",
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "warning": {
            "bg": UIStyle.THEME_STATE_READY,
            "fg": UIStyle.THEME_BG_APP,
            "activebackground": "#ca8a04",
            "activeforeground": UIStyle.THEME_BG_APP,
            "disabledforeground": UIStyle.THEME_TEXT_SECONDARY,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "neutral": {
            "bg": UIStyle.THEME_BG_PANEL,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": UIStyle.THEME_BG_SIDEBAR,
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "font": (UIStyle.resolve_font_family("body"), UIStyle.SIZE_BUTTON, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
        },
        "icon": {
            "bg": UIStyle.THEME_BG_APP,
            "fg": UIStyle.THEME_TEXT_PRIMARY,
            "activebackground": UIStyle.THEME_BG_PANEL,
            "activeforeground": UIStyle.THEME_TEXT_PRIMARY,
            "disabledforeground": UIStyle.THEME_TEXT_MUTED,
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
        },
    }

    return configs.get(button_type, configs["green"])


def apply_button_role(button, role: str):
    """
    Apply a semantic role to a ttk.Button.

    Args:
        button: ttk.Button instance
        role: Semantic role (e.g., 'primary', 'danger', 'info', 'neutral', 'warning', 'icon')
    """
    style = ROLE_STYLES.get(role, "Primary.TButton")
    button.configure(style=style)


# Legacy label color mapping for compatibility
def get_label_color(color_type: str) -> dict:
    """
    Get label color configuration for consistent text styling.
    Maintained for API compatibility during migration.
    """
    colors = {
        "info": {"fg": UIStyle.THEME_STATE_INFO},
        "success": {"fg": UIStyle.THEME_STATE_HUNTING},
        "warning": {"fg": UIStyle.THEME_STATE_READY},
        "error": {"fg": UIStyle.THEME_STATE_DANGER},
        "gray": {"fg": UIStyle.THEME_TEXT_MUTED},
        "light_gray": {"fg": UIStyle.THEME_TEXT_SECONDARY},
        "dark": {"fg": UIStyle.THEME_TEXT_PRIMARY},
    }

    return colors.get(color_type, colors["dark"])


# =============================================================================
# Legacy Constants (Kept for backward compatibility, will be removed)
# =============================================================================

BTN_GREEN_BG = UIStyle.THEME_STATE_HUNTING
BTN_GREEN_FG = UIStyle.THEME_BG_APP
BTN_GREEN_ACTIVE_BG = UIStyle.THEME_STATE_HUNTING_BORDER
BTN_GREEN_ACTIVE_FG = UIStyle.THEME_BG_APP
BTN_GREEN_DISABLED_FG = UIStyle.THEME_TEXT_MUTED

BTN_GREEN_LIGHT_BG = UIStyle.THEME_STATE_HUNTING
BTN_GREEN_LIGHT_FG = UIStyle.THEME_BG_APP
BTN_GREEN_LIGHT_ACTIVE_BG = UIStyle.THEME_STATE_HUNTING_BORDER

BTN_RED_BG = UIStyle.THEME_STATE_DANGER
BTN_RED_FG = UIStyle.THEME_TEXT_PRIMARY
BTN_RED_ACTIVE_BG = "#b91c1c"
BTN_RED_ACTIVE_FG = UIStyle.THEME_TEXT_PRIMARY
BTN_RED_DISABLED_FG = UIStyle.THEME_TEXT_MUTED

BTN_BLUE_BG = UIStyle.THEME_STATE_INFO
BTN_BLUE_FG = UIStyle.THEME_TEXT_PRIMARY
BTN_BLUE_ACTIVE_BG = "#2563eb"
BTN_BLUE_ACTIVE_FG = UIStyle.THEME_TEXT_PRIMARY

BTN_REFRESH_BG = UIStyle.THEME_STATE_INFO
BTN_REFRESH_FG = UIStyle.THEME_TEXT_PRIMARY
BTN_REFRESH_ACTIVE_BG = "#2563eb"
BTN_REFRESH_ACTIVE_FG = UIStyle.THEME_TEXT_PRIMARY

BTN_ORANGE_BG = UIStyle.THEME_STATE_READY
BTN_ORANGE_FG = UIStyle.THEME_BG_APP
BTN_ORANGE_ACTIVE_BG = "#ca8a04"
BTN_ORANGE_ACTIVE_FG = UIStyle.THEME_BG_APP

BG_LIGHT_GRAY = UIStyle.THEME_BG_PANEL
BG_VERY_LIGHT_GRAY = UIStyle.THEME_BG_PANEL
TEXT_GRAY = UIStyle.THEME_TEXT_MUTED
TEXT_LIGHT_GRAY = UIStyle.THEME_TEXT_SECONDARY
TEXT_DARK = UIStyle.THEME_TEXT_PRIMARY
BORDER_LIGHT = UIStyle.THEME_BORDER_PANEL
BORDER_MEDIUM = UIStyle.THEME_BORDER_DEFAULT
