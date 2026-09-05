import os

import pytest

pytest.importorskip("tkinter", reason="Skipping ttk theme tests because tkinter is not available")

pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests",
)

import tkinter as tk
from tkinter import ttk
from ui.theme.ttk_theme import configure_ttk_styles
from ui.helpers.button_styles import get_button_config, apply_button_role
@pytest.fixture
def tk_root():
    root = tk.Tk()
    configure_ttk_styles(root)
    yield root
    root.destroy()

def test_get_button_config_legacy_roles(tk_root):
    # Test semantic roles compatibility with tk.Button
    config = get_button_config('primary')
    assert 'bg' in config
    assert 'fg' in config
    assert 'font' in config

    config = get_button_config('danger')
    assert 'bg' in config

def test_get_button_config_legacy_aliases(tk_root):
    # Test legacy aliases for backward compatibility
    config_green = get_button_config('green')
    assert 'bg' in config_green
    config_red = get_button_config('red')
    assert 'bg' in config_red

def test_apply_button_role(tk_root):
    # Create a button and apply role
    btn = ttk.Button(tk_root, text="Test")

    apply_button_role(btn, 'danger')
    assert btn.cget('style') == 'Danger.TButton'

    apply_button_role(btn, 'primary')
    assert btn.cget('style') == 'Primary.TButton'

def test_legacy_constants_use_tokens():
    # Verify legacy constants read from DS1 tokens
    from ui.helpers.button_styles import BTN_GREEN_BG, BTN_RED_BG, BTN_BLUE_BG
    from lib.ui_style import UIStyle

    assert BTN_GREEN_BG == UIStyle.THEME_STATE_HUNTING
    assert BTN_RED_BG == UIStyle.THEME_STATE_DANGER
    assert BTN_BLUE_BG == UIStyle.THEME_STATE_INFO
