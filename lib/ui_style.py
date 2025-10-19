# -*- coding: utf-8 -*-
"""
UI Style Guide - Centralized fonts, colors, and sizes for consistent UI.

Usage:
    from lib.ui_style import UIStyle as UI
    tk.Label(parent, font=UI.FONT_LABEL, fg=UI.COLOR_TEXT)
"""
from __future__ import annotations

class UIStyle:
    # Font family and sizes
    FONT_FAMILY = 'Segoe UI'
    SIZE_TITLE = 12
    SIZE_SECTION = 11
    SIZE_LABEL = 10
    SIZE_TEXT = 10
    SIZE_BUTTON = 10
    SIZE_SMALL = 8

    # Font tuples
    FONT_TITLE = (FONT_FAMILY, SIZE_TITLE, 'bold')
    FONT_SECTION = (FONT_FAMILY, SIZE_SECTION, 'bold')
    FONT_LABEL = (FONT_FAMILY, SIZE_LABEL)
    FONT_TEXT = (FONT_FAMILY, SIZE_TEXT)
    FONT_BUTTON = (FONT_FAMILY, SIZE_BUTTON)
    FONT_SMALL = (FONT_FAMILY, SIZE_SMALL)

    # Colors
    COLOR_PRIMARY = '#2196F3'
    COLOR_PRIMARY_TEXT = '#0D47A1'
    COLOR_ACCENT = '#4CAF50'
    COLOR_DANGER = '#F44336'
    COLOR_WARNING = '#FF7043'
    COLOR_INFO = '#1976D2'
    COLOR_MUTED = '#757575'
    COLOR_TEXT = '#212121'
    COLOR_SUBTEXT = '#666666'
    COLOR_HINT = '#757575'

    # Backgrounds
    BG_DEFAULT = '#FFFFFF'
    BG_PANEL = '#F5F5F5'
    BG_SECTION = '#E3F2FD'
    BG_TITLE = '#2196F3'

    # Button backgrounds
    BTN_PRIMARY_BG = '#2E7D32'
    BTN_PRIMARY_FG = '#FFFFFF'
    BTN_NEUTRAL_BG = '#757575'
    BTN_NEUTRAL_FG = '#FFFFFF'
    BTN_DANGER_BG = '#F44336'
    BTN_DANGER_FG = '#FFFFFF'
    BTN_INFO_BG = '#1976D2'
    BTN_INFO_FG = '#FFFFFF'
    BTN_ACCENT_BG = '#00897B'
    BTN_ACCENT_FG = '#FFFFFF'

    # Icon sizes
    ICON_SMALL = 16
    ICON_MEDIUM = 20
    ICON_LARGE = 24
