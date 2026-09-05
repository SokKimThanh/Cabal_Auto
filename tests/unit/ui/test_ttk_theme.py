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
from lib.ui_style import UIStyle

@pytest.fixture
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_theme_idempotency(tk_root):
    # First call
    configure_ttk_styles(tk_root)
    style = ttk.Style(tk_root)
    assert style.theme_use() == 'cabal_dark'

    # Second call should not fail and should retain the theme
    configure_ttk_styles(tk_root)
    assert style.theme_use() == 'cabal_dark'

def test_base_component_styles(tk_root):
    configure_ttk_styles(tk_root)
    style = ttk.Style(tk_root)

    # Frame
    assert style.lookup('TFrame', 'background') == UIStyle.THEME_BG_APP

    # Label
    assert style.lookup('TLabel', 'background') == UIStyle.THEME_BG_APP
    assert style.lookup('TLabel', 'foreground') == UIStyle.THEME_TEXT_PRIMARY

    # Combobox
    assert style.lookup('TCombobox', 'background') == UIStyle.THEME_BG_INPUT
    assert style.lookup('TCombobox', 'fieldbackground') == UIStyle.THEME_BG_INPUT

    # Treeview
    assert style.lookup('Treeview', 'background') == UIStyle.THEME_BG_PANEL
    assert style.lookup('Treeview.Heading', 'background') == UIStyle.THEME_BG_SIDEBAR

    # Scrollbar
    assert style.lookup('TScrollbar', 'background') == UIStyle.THEME_BG_PANEL

    # Checkbutton
    assert style.lookup('TCheckbutton', 'background') == UIStyle.THEME_BG_APP

def test_semantic_button_roles(tk_root):
    configure_ttk_styles(tk_root)
    style = ttk.Style(tk_root)

    roles = [
        ('Primary.TButton', UIStyle.THEME_STATE_HUNTING),
        ('Danger.TButton', UIStyle.THEME_STATE_DANGER),
        ('Info.TButton', UIStyle.THEME_STATE_INFO),
        ('Warning.TButton', UIStyle.THEME_STATE_READY),
        ('Neutral.TButton', UIStyle.THEME_BG_PANEL),
    ]

    for role, expected_bg in roles:
        assert style.lookup(role, 'background') == expected_bg

    # Icon button
    assert style.lookup('Icon.TButton', 'relief') == 'flat'

def test_button_disabled_state(tk_root):
    configure_ttk_styles(tk_root)
    style = ttk.Style(tk_root)

    # Text shouldn't be lost, it should be muted
    # We can't directly check map states easily without instantiating and configuring state,
    # but we can verify the mapping dict contains it
    map_dict = style.map('Primary.TButton')

    # Extract foreground rules
    fg_rules = map_dict.get('foreground', [])
    disabled_rule = [rule for rule in fg_rules if 'disabled' in rule[0]]
    assert len(disabled_rule) > 0
    assert disabled_rule[0][1] == UIStyle.THEME_TEXT_MUTED
