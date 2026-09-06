"""Verify UIStyleV2 has all required constants"""

from lib.ui_style_v2 import UIStyleV2 as UI

def test_all_colors_exist():
    """Check all color constants are defined"""
    required = [
        'BG_BASE', 'BG_SURFACE', 'BG_ELEVATED', 'BG_SUBTLE',
        'BORDER_PRIMARY', 'BORDER_SUBTLE',
        'TEXT_PRIMARY', 'TEXT_SECONDARY', 'TEXT_MUTED', 'TEXT_SUBTLE',
        'ACCENT_GREEN', 'ACCENT_AMBER', 'ACCENT_BLUE', 'DANGER'
    ]
    for attr in required:
        assert hasattr(UI, attr), f"Missing: {attr}"
        assert isinstance(getattr(UI, attr), str), f"Not a string: {attr}"

def test_backward_compat_aliases():
    """Check old UIStyle constants are aliased"""
    required_aliases = [
        'THEME_BG_APP', 'THEME_BG_SIDEBAR', 'THEME_BG_PANEL',
        'BG_DEFAULT', 'BG_PANEL', 'BG_MUTED', 'BG_SECTION',
        'THEME_TEXT_PRIMARY', 'THEME_TEXT_SECONDARY', 'THEME_TEXT_MUTED',
        'THEME_STATE_HUNTING',
        'BTN_PRIMARY_BG', 'BTN_PRIMARY_FG', 'BTN_NEUTRAL_BG', 'BTN_NEUTRAL_FG',
        'BTN_DANGER_BG', 'BTN_DANGER_FG', 'BTN_INFO_BG', 'BTN_INFO_FG',
        'SPACING_2', 'SPACING_4', 'SPACING_8', 'SPACING_12',
        'SIZE_SECTION'
    for attr in required_aliases:
        assert hasattr(UI, attr), f"Missing backward compat: {attr}"

def test_all_fonts_exist():
    """Check all font constants"""
    required = [
        'FONT_TITLE', 'FONT_SECTION', 'FONT_HEADER', 'FONT_BODY',
        'FONT_LABEL', 'FONT_TEXT', 'FONT_BUTTON', 'FONT_SMALL'
    ]
    for attr in required:
        assert hasattr(UI, attr), f"Missing: {attr}"
        assert isinstance(getattr(UI, attr), tuple), f"Not a tuple: {attr}"

def test_methods_exist():
    """Check all required methods"""
    methods = ['get_font', 'resolve_font_family', 'get_panel_style', 'get_button_style']
    for method in methods:
        assert hasattr(UI, method), f"Missing method: {method}"

if __name__ == "__main__":
    test_all_colors_exist()
    test_backward_compat_aliases()
    test_all_fonts_exist()
    test_methods_exist()
    print("All tests passed!")
