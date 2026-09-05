import tkinter as tk
from tkinter import ttk
from lib.ui_style import UIStyle

def configure_ttk_styles(root=None):
    """
    Idempotent function to configure ttk styles.
    Uses 'clam' or other available theme as base and overrides specific elements.
    """
    if root is None:
        root = tk._default_root
        if root is None:
            return

    style = ttk.Style(root)

    # Idempotency check: don't reconfigure if already configured
    # We can check a custom theme name or layout presence
    if 'cabal_dark' in style.theme_names() and style.theme_use() == 'cabal_dark':
        return

    # Create a custom theme based on 'clam' or another solid base
    base_theme = 'clam' if 'clam' in style.theme_names() else 'default'

    try:
        style.theme_create('cabal_dark', parent=base_theme, settings={
            ".": {
                "configure": {
                    "background": UIStyle.THEME_BG_APP,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "troughcolor": UIStyle.THEME_BG_PANEL,
                    "selectbackground": UIStyle.THEME_STATE_SELECTED,
                    "selectforeground": UIStyle.THEME_TEXT_PRIMARY,
                    "fieldbackground": UIStyle.THEME_BG_INPUT,
                    "font": (UIStyle.resolve_font_family('body'), UIStyle.SIZE_TEXT),
                    "bordercolor": UIStyle.THEME_BORDER_DEFAULT,
                    "lightcolor": UIStyle.THEME_BG_APP,
                    "darkcolor": UIStyle.THEME_BG_APP,
                }
            },
            "TFrame": {
                "configure": {
                    "background": UIStyle.THEME_BG_APP,
                }
            },
            "TLabel": {
                "configure": {
                    "background": UIStyle.THEME_BG_APP,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                }
            },
            "TCombobox": {
                "configure": {
                    "background": UIStyle.THEME_BG_INPUT,
                    "fieldbackground": UIStyle.THEME_BG_INPUT,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "selectbackground": UIStyle.THEME_STATE_SELECTED,
                    "selectforeground": UIStyle.THEME_TEXT_PRIMARY,
                    "arrowcolor": UIStyle.THEME_TEXT_PRIMARY,
                }
            },
            "Treeview": {
                "configure": {
                    "background": UIStyle.THEME_BG_PANEL,
                    "fieldbackground": UIStyle.THEME_BG_PANEL,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('selected', UIStyle.THEME_STATE_SELECTED)],
                    "foreground": [('selected', UIStyle.THEME_TEXT_PRIMARY)],
                }
            },
            "Treeview.Heading": {
                "configure": {
                    "background": UIStyle.THEME_BG_SIDEBAR,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "font": (UIStyle.resolve_font_family('body'), UIStyle.SIZE_TEXT, "bold"),
                    "relief": "flat",
                },
                "map": {
                    "background": [('active', UIStyle.THEME_BG_TOOLBAR)],
                }
            },
            "TScrollbar": {
                "configure": {
                    "background": UIStyle.THEME_BG_PANEL,
                    "troughcolor": UIStyle.THEME_BG_APP,
                    "arrowcolor": UIStyle.THEME_TEXT_PRIMARY,
                    "bordercolor": UIStyle.THEME_BORDER_DEFAULT,
                },
                "map": {
                    "background": [('active', UIStyle.THEME_BG_SIDEBAR)],
                }
            },
            "TCheckbutton": {
                "configure": {
                    "background": UIStyle.THEME_BG_APP,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "indicatorcolor": UIStyle.THEME_BG_INPUT,
                },
                "map": {
                    "background": [('active', UIStyle.THEME_BG_APP), ('disabled', UIStyle.THEME_BG_APP)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                    "indicatorcolor": [('selected', UIStyle.THEME_STATE_HUNTING), ('disabled', UIStyle.THEME_BG_APP)],
                }
            },
            # Button semantic roles
            "Primary.TButton": {
                "configure": {
                    "background": UIStyle.THEME_STATE_HUNTING,
                    "foreground": UIStyle.THEME_BG_APP,
                    "focuscolor": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('active', UIStyle.THEME_STATE_HUNTING_BORDER), ('disabled', UIStyle.THEME_BG_PANEL)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                }
            },
            "Danger.TButton": {
                "configure": {
                    "background": UIStyle.THEME_STATE_DANGER,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "focuscolor": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('active', '#b91c1c'), ('disabled', UIStyle.THEME_BG_PANEL)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                }
            },
            "Info.TButton": {
                "configure": {
                    "background": UIStyle.THEME_STATE_INFO,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "focuscolor": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('active', '#2563eb'), ('disabled', UIStyle.THEME_BG_PANEL)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                }
            },
            "Warning.TButton": {
                "configure": {
                    "background": UIStyle.THEME_STATE_READY,
                    "foreground": UIStyle.THEME_BG_APP,
                    "focuscolor": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('active', '#ca8a04'), ('disabled', UIStyle.THEME_BG_PANEL)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                }
            },
            "Neutral.TButton": {
                "configure": {
                    "background": UIStyle.THEME_BG_PANEL,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "focuscolor": UIStyle.THEME_TEXT_PRIMARY,
                },
                "map": {
                    "background": [('active', UIStyle.THEME_BG_SIDEBAR), ('disabled', UIStyle.THEME_BG_APP)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                    "bordercolor": [('focus', UIStyle.THEME_STATE_INFO)]
                }
            },
            "Icon.TButton": {
                "configure": {
                    "background": UIStyle.THEME_BG_APP,
                    "foreground": UIStyle.THEME_TEXT_PRIMARY,
                    "relief": "flat",
                    "padding": 2,
                },
                "map": {
                    "background": [('active', UIStyle.THEME_BG_PANEL), ('disabled', UIStyle.THEME_BG_APP)],
                    "foreground": [('disabled', UIStyle.THEME_TEXT_MUTED)],
                }
            }
        })
    except tk.TclError as e:
        # Ignore only the "already exists" case; log anything else to avoid silent theme failures.
        if "already exists" not in str(e):
            import logging
            logging.getLogger(__name__).exception("Failed to create ttk theme 'cabal_dark'")
            return

    try:
        style.theme_use('cabal_dark')
    except tk.TclError:
        import logging
        logging.getLogger(__name__).exception("Failed to activate ttk theme 'cabal_dark'")
