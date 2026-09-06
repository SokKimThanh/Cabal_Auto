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
    # TYPOGRAPHY
    # =========================================================

    FONT_FAMILY_UI = "Inter"
    FONT_FAMILY_UI_FALLBACK = "Segoe UI"
    FONT_FAMILY_MONO = "JetBrains Mono"
    FONT_FAMILY_MONO_FALLBACK = "Courier New"

    # Sizes
    SIZE_TITLE = 16    # Title/Section
    SIZE_HEADER = 14   # Header
    SIZE_BODY = 13     # Body
    SIZE_LABEL = 12    # Label
    SIZE_SMALL = 11    # Small/caption
    SIZE_TINY = 10     # Tiny/badge/tag

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
