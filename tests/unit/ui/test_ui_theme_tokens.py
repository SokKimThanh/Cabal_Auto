import pytest
from lib.ui_style import UIStyle

def test_hex_tokens():
    # Validate colors are hex format
    hex_colors = [
        UIStyle.THEME_BG_APP, UIStyle.THEME_BG_SIDEBAR, UIStyle.THEME_BG_PANEL,
        UIStyle.THEME_BG_INPUT, UIStyle.THEME_BG_TOOLBAR, UIStyle.THEME_BG_STATUSBAR,
        UIStyle.THEME_BORDER_DEFAULT, UIStyle.THEME_BORDER_PANEL,
        UIStyle.THEME_TEXT_PRIMARY, UIStyle.THEME_TEXT_SECONDARY, UIStyle.THEME_TEXT_MUTED,
        UIStyle.THEME_STATE_HUNTING, UIStyle.THEME_STATE_HUNTING_BORDER,
        UIStyle.THEME_STATE_SELECTED, UIStyle.THEME_STATE_INFO,
        UIStyle.THEME_STATE_READY, UIStyle.THEME_STATE_DANGER
    ]
    for color in hex_colors:
        assert color.startswith("#")
        assert len(color) == 7
        # Ensure it's a valid hex
        int(color[1:], 16)

def test_font_resolver():
    # Without tk root, fallback to last item
    display_font = UIStyle.resolve_font_family('display')
    assert display_font in ['Rajdhani', 'Segoe UI Semibold', 'Segoe UI']

    body_font = UIStyle.resolve_font_family('body')
    assert body_font in ['Inter', 'Segoe UI']

    mono_font = UIStyle.resolve_font_family('mono')
    assert mono_font in ['JetBrains Mono', 'Cascadia Mono', 'Consolas']

    other_font = UIStyle.resolve_font_family('other')
    assert other_font == 'Segoe UI'

def test_legacy_aliases():
    assert UIStyle.BG_DEFAULT == '#FFFFFF'
    assert hasattr(UIStyle, 'COLOR_TEXT')

def test_preblend_helper():
    # alpha=0 -> background color
    assert UIStyle.blend_alpha_to_hex(0.0, "#ffffff", "#000000") == "#000000"
    # alpha=1 -> foreground color
    assert UIStyle.blend_alpha_to_hex(1.0, "#ffffff", "#000000") == "#ffffff"
    # alpha=0.5 -> mid color
    assert UIStyle.blend_alpha_to_hex(0.5, "#ffffff", "#000000") == "#7f7f7f"

def test_win32_overlay_tokens():
    assert isinstance(UIStyle.OVERLAY_BG_COLOR, tuple)
    assert len(UIStyle.OVERLAY_BG_COLOR) == 3
    assert isinstance(UIStyle.COLOR_BLACK_RGB, tuple)

def get_relative_luminance(hex_color: str) -> float:
    # Remove hash
    hex_color = hex_color.lstrip('#')
    # Parse RGB
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Normalize
    rgb = [v / 255.0 for v in (r, g, b)]

    # Apply WCAG 2.0 formula
    for i in range(3):
        if rgb[i] <= 0.03928:
            rgb[i] = rgb[i] / 12.92
        else:
            rgb[i] = ((rgb[i] + 0.055) / 1.055) ** 2.4

    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

def get_contrast_ratio(hex1: str, hex2: str) -> float:
    lum1 = get_relative_luminance(hex1)
    lum2 = get_relative_luminance(hex2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def test_contrast_ratio():
    # WCAG AA requires a contrast ratio of at least 4.5:1 for normal text

    # Primary text on App Background
    contrast_app = get_contrast_ratio(UIStyle.THEME_TEXT_PRIMARY, UIStyle.THEME_BG_APP)
    assert contrast_app >= 4.5, f"Contrast between TEXT_PRIMARY and BG_APP too low: {contrast_app}"

    # Primary text on Panel Background
    contrast_panel = get_contrast_ratio(UIStyle.THEME_TEXT_PRIMARY, UIStyle.THEME_BG_PANEL)
    assert contrast_panel >= 4.5, f"Contrast between TEXT_PRIMARY and BG_PANEL too low: {contrast_panel}"
