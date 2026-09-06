# -*- coding: utf-8 -*-
"""
Design System for Cabal Auto Hunt - Phase 2 Modern Dark Theme
Centralized fonts, colors, and sizes for a consistent, modern UI.
"""

class UIStyleV2:
    # =========================================================
    # COLOR PALETTE (Semantic Tokens)
    # =========================================================

    # Backgrounds
    BG_BASE = "#0f0f0f"      # Main app background
    BG_SURFACE = "#1a1a1a"   # Panels, cards, elevated content
    BG_ELEVATED = "#111111"  # Sidebar, header, inputs, surfaces
    BG_SUBTLE = "#0a0a0a"    # Status bar, dividers

    # Borders & Dividers
    BORDER_PRIMARY = "#2a2a2a" # Standard panel borders
    BORDER_SUBTLE = "#1f1f1f"  # Subtle dividers, secondary borders

    # Text
    TEXT_PRIMARY = "#d1d5db"   # Main content text
    TEXT_SECONDARY = "#9ca3af" # Secondary text
    TEXT_MUTED = "#6b7280"     # Tertiary text
    TEXT_SUBTLE = "#374151"    # Placeholders

    # Accent Colors
    ACCENT_GREEN = "#4ade80"     # Active, success, primary actions
    ACCENT_GREEN_BG = "#1f2d1f"  # Green background tint
    ACCENT_AMBER = "#f59e0b"     # Warning, waiting state
    ACCENT_BLUE = "#38bdf8"      # Info, running/active state
    DANGER = "#dc2626"           # Errors, critical, health low

    # =========================================================
    # BACKWARD COMPATIBILITY: TTK Theme Constants (From UIStyle)
    # Mapping old naming to new semantic tokens
    # =========================================================

    # RGB Colors (for OpenCV/overlay)
    COLOR_BLACK_RGB = (0, 0, 0)
    COLOR_WHITE_RGB = (255, 255, 255)
    COLOR_RED_RGB = (255, 0, 0)
    COLOR_GREEN_RGB = (0, 255, 0)
    COLOR_BLUE_RGB = (0, 0, 255)

    # Legacy colors mapping for older components
    COLOR_PRIMARY = '#2196F3'
    COLOR_PRIMARY_TEXT = '#0D47A1'
    COLOR_ACCENT = '#4CAF50'
    COLOR_DANGER = '#F44336'
    COLOR_WARNING = '#FF7043'
    COLOR_INFO = '#1976D2'
    COLOR_MUTED = TEXT_MUTED
    COLOR_TEXT = TEXT_PRIMARY
    COLOR_SUBTEXT = TEXT_SECONDARY
    COLOR_HINT = TEXT_SUBTLE

    OVERLAY_BG_ALPHA = 0.3            # 30% opacity for black background
    OVERLAY_BG_COLOR = (0, 0, 0)      # Black RGB tuple for Win32

    # Background aliases
    BG_DEFAULT = BG_BASE
    THEME_BG_APP = BG_BASE
    THEME_BG_SIDEBAR = BG_ELEVATED
    THEME_BG_PANEL = BG_SURFACE
    THEME_BG_INPUT = BG_ELEVATED
    THEME_BG_TOOLBAR = BG_ELEVATED
    THEME_BG_STATUSBAR = BG_SUBTLE

    # Border aliases
    THEME_BORDER_DEFAULT = BORDER_PRIMARY
    THEME_BORDER_PANEL = BORDER_PRIMARY

    # Text aliases
    THEME_TEXT_PRIMARY = TEXT_PRIMARY
    THEME_TEXT_SECONDARY = TEXT_SECONDARY
    THEME_TEXT_MUTED = TEXT_MUTED

    # State color aliases
    THEME_STATE_HUNTING = ACCENT_GREEN
    THEME_STATE_HUNTING_BORDER = "#16a34a"  # Darker green for borders
    THEME_STATE_SELECTED = "#1d4ed8"        # Blue for selection
    THEME_STATE_INFO = ACCENT_BLUE
    THEME_STATE_READY = ACCENT_AMBER
    THEME_STATE_DANGER = DANGER

    # =========================================================
    # BACKWARD COMPATIBILITY: Old Spacing Aliases
    # =========================================================

    SPACING_2 = 2
    SPACING_4 = 4  # Should match SPACE_XS if needed but using explicit int per instructions
    SPACING_6 = 6
    SPACING_8 = 8  # SPACE_SM
    SPACING_10 = 10
    SPACING_12 = 12 # SPACE_MD
    SPACING_16 = 16 # SPACE_LG
    SPACING_20 = 20
    SPACING_24 = 24 # SPACE_XL
    SPACING_32 = 32

    # =========================================================
    # TYPOGRAPHY
    # =========================================================

    FONT_FAMILY_UI = "Inter"
    FONT_FAMILY_UI_FALLBACK = "Segoe UI"
    FONT_FAMILY_MONO = "JetBrains Mono"
    FONT_FAMILY_MONO_FALLBACK = "Courier New"
    
    # Backward compatibility aliases
    FONT_FAMILY = FONT_FAMILY_UI_FALLBACK  # For old code expecting FONT_FAMILY

    # Sizes
    SIZE_TITLE = 16    # Title/Section
    SIZE_HEADER = 14   # Header
    SIZE_BODY = 13     # Body
    SIZE_LABEL = 12    # Label
    SIZE_SMALL = 11    # Small/caption
    SIZE_TINY = 10     # Tiny/badge/tag
    
    # Backward compatibility aliases for old UIStyle constants
    SIZE_TEXT = SIZE_BODY
    SIZE_BUTTON = SIZE_LABEL
    SIZE_SECTION = SIZE_HEADER

    # Font tuples for backward compatibility with older code
    FONT_TITLE = (FONT_FAMILY_UI_FALLBACK, SIZE_TITLE, "bold")
    FONT_SECTION = (FONT_FAMILY_UI_FALLBACK, SIZE_HEADER, "bold")
    FONT_HEADER = (FONT_FAMILY_UI_FALLBACK, SIZE_HEADER, "bold")
    FONT_BODY = (FONT_FAMILY_UI_FALLBACK, SIZE_BODY)
    FONT_LABEL = (FONT_FAMILY_UI_FALLBACK, SIZE_LABEL)
    FONT_TEXT = (FONT_FAMILY_UI_FALLBACK, SIZE_BODY)
    FONT_BUTTON = (FONT_FAMILY_UI_FALLBACK, SIZE_LABEL)
    FONT_SMALL = (FONT_FAMILY_UI_FALLBACK, SIZE_SMALL)
    FONT_TINY = (FONT_FAMILY_UI_FALLBACK, SIZE_TINY)

    # Base Font definitions (can be resolved dynamically)
    @classmethod
    def get_font(cls, role="body", size=None, weight="normal"):
        """Helper to get a font tuple for Tkinter"""
        family = cls.resolve_font_family("ui")
        if role == "mono":
            family = cls.resolve_font_family("mono")

        if size is None:
            if role == "title": size = cls.SIZE_TITLE
            elif role == "header": size = cls.SIZE_HEADER
            elif role == "body": size = cls.SIZE_BODY
            elif role == "label": size = cls.SIZE_LABEL
            elif role == "small": size = cls.SIZE_SMALL
            elif role == "tiny": size = cls.SIZE_TINY
            else: size = cls.SIZE_BODY

        return (family, size, weight)

    @classmethod
    def resolve_font_family(cls, type="ui") -> str:
        """Resolve font family based on availability in Tkinter."""
        try:
            import tkinter.font as tkfont
        except Exception:
            tkfont = None

        available_fonts = []
        if tkfont is not None:
            try:
                available_fonts = tkfont.families()
            except Exception:
                pass

        if type == "mono":
            fallbacks = [cls.FONT_FAMILY_MONO, cls.FONT_FAMILY_MONO_FALLBACK, "Consolas", "monospace"]
        else:
            fallbacks = [cls.FONT_FAMILY_UI, cls.FONT_FAMILY_UI_FALLBACK, "sans-serif"]

        for f in fallbacks:
            if f in available_fonts:
                return f
        return fallbacks[-1]

    # =========================================================
    # OVERLAY STYLING
    # =========================================================

    DETECTION_STATE_SEARCHING = (255, 59, 48)     # Red for searching
    DETECTION_STATE_DETECTED = (52, 199, 89)    # Green for detected
    DETECTION_STATE_TRACKING = (0, 122, 255)     # Blue for tracking

    DETECTION_BORDER_WIDTH = 2        # Border thickness in pixels
    DETECTION_TEXT_FONT_HEIGHT = 16   # Text font height (Segoe UI style)
    DETECTION_TEXT_PADDING = 4        # Padding around text labels
    DETECTION_TEXT_CHAR_WIDTH = 8     # Approximate character width

    DETECTION_TEXT_COLOR = (0, 0, 0)        # Black text
    DETECTION_TEXT_BG_COLOR = (255, 255, 255)     # White opaque background

    # FPS Counter
    FPS_COUNTER_WIDTH = 100
    FPS_COUNTER_HEIGHT = 20
    FPS_COUNTER_PADDING = 4
    FPS_COUNTER_TEXT_COLOR = (0, 0, 0)      # Black text
    FPS_COUNTER_BG_COLOR = (255, 255, 255)        # White background
    FPS_COUNTER_POSITION = 'top-right'            # Position anchor

    # =========================================================
    # SIDEBAR ICONS
    # =========================================================

    SIDEBAR_ICONS = {
        "tab_hunt": "🎯",
        "tab_setup": "⚙️",
        "btn_skill_manager": "⚔️",
        "btn_monster_manager": "👾",
        "btn_map_overlay": "🗺️",
        "btn_macro_recorder": "📼",
        "tab_help": "❓",
        "tab_logs": "📝",
        "tab_settings": "🔧"
    }

    @classmethod
    def get_sidebar_icon(cls, key: str) -> str:
        return cls.SIDEBAR_ICONS.get(key, "•")

    # =========================================================
    # SPACING & RADIUS
    # =========================================================

    # Spacing
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 12
    SPACE_LG = 16
    SPACE_XL = 24

    # Border Radius (Logical representation, Tkinter support varies)
    RADIUS_SM = 4   # inputs, small elements
    RADIUS_MD = 6   # buttons, cards
    RADIUS_LG = 8   # panels
    RADIUS_XL = 12  # large sections

    # =========================================================
    # COMPONENT STYLES
    # =========================================================

    @classmethod
    def get_panel_style(cls):
        return {
            "bg": cls.BG_SURFACE,
            "highlightbackground": cls.BORDER_PRIMARY,
            "highlightcolor": cls.BORDER_PRIMARY,
            "highlightthickness": 1
        }

    @classmethod
    def blend_alpha_to_hex(cls, alpha: float, hex_bg: str, hex_fg: str) -> str:
        """Helper to pre-blend two hex colors given an alpha for Tkinter support"""
        try:
            # Simple fallback if this is just used for legacy tests
            if alpha <= 0.0: return hex_bg
            if alpha >= 1.0: return hex_fg

            # Simple parsing (assuming #RRGGBB)
            bg = (int(hex_bg[1:3], 16), int(hex_bg[3:5], 16), int(hex_bg[5:7], 16))
            fg = (int(hex_fg[1:3], 16), int(hex_fg[3:5], 16), int(hex_fg[5:7], 16))

            r = int(fg[0] * alpha + bg[0] * (1 - alpha))
            g = int(fg[1] * alpha + bg[1] * (1 - alpha))
            b = int(fg[2] * alpha + bg[2] * (1 - alpha))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_fg

    @classmethod
    def get_button_style(cls, variant="primary"):
        """Returns kwargs for tk.Button styling"""
        if variant == "primary":
            return {
                "bg": cls.ACCENT_GREEN,
                "fg": "#000000",
                "activebackground": "#86efac", # Lighter green for hover/active
                "activeforeground": "#000000",
                "relief": "flat",
                "borderwidth": 0
            }
        elif variant == "secondary":
            return {
                "bg": cls.BG_ELEVATED,
                "fg": cls.TEXT_PRIMARY,
                "activebackground": cls.BG_SURFACE,
                "activeforeground": cls.TEXT_PRIMARY,
                "relief": "flat",
                "borderwidth": 1,
                "highlightbackground": cls.BORDER_PRIMARY,
            }
        elif variant == "icon":
            return {
                "bg": cls.BG_ELEVATED,
                "fg": cls.TEXT_MUTED,
                "activebackground": cls.BG_SURFACE,
                "activeforeground": cls.TEXT_PRIMARY,
                "relief": "flat",
                "borderwidth": 1,
                "highlightbackground": cls.BORDER_SUBTLE,
            }
        return {}
