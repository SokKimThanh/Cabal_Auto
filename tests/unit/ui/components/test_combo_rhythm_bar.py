import pytest
import tkinter as tk
import time
from unittest.mock import patch, MagicMock

from ui.components.combo_rhythm_bar import ComboRhythmBar
from lib.ui.animation_manager import UIAnimationManager
from lib.ui_style_v2 import UIStyleV2 as UI

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def rhythm_bar(root):
    # Ensure animation manager is fresh
    UIAnimationManager.reset_instance()
    bar = ComboRhythmBar(root)
    bar.pack()
    root.update()
    yield bar
    UIAnimationManager.reset_instance()

def test_combo_rhythm_bar_initialization(rhythm_bar):
    """Test component initializes without errors and sets default values."""
    assert rhythm_bar.is_visible.get() is True
    assert rhythm_bar.last_trigger_time == 0
    assert rhythm_bar.current_color == UI.BG_ELEVATED

def test_trigger_hit_changes_color(rhythm_bar):
    """Test that trigger_hit calls the animation manager to change colors."""
    with patch.object(rhythm_bar.animation_manager, 'register_tween') as mock_register:
        rhythm_bar.trigger_hit()

        # Color should immediately update
        assert rhythm_bar.current_color == UI.ACCENT_AMBER

        # Animation manager should be called
        mock_register.assert_called_once()
        args, kwargs = mock_register.call_args
        assert kwargs['target_id'] == rhythm_bar.animation_target_id
        assert kwargs['duration_ms'] == rhythm_bar.DEBOUNCE_MS

def test_trigger_hit_debounce(rhythm_bar):
    """Test that consecutive trigger_hit calls within DEBOUNCE_MS are ignored."""
    with patch.object(rhythm_bar.animation_manager, 'register_tween') as mock_register:
        # First hit
        rhythm_bar.trigger_hit()
        assert mock_register.call_count == 1

        # Immediate second hit (within debounce)
        rhythm_bar.trigger_hit()
        assert mock_register.call_count == 1  # Still 1

        # Simulate time passing beyond DEBOUNCE_MS
        rhythm_bar.last_trigger_time = time.time() - (rhythm_bar.DEBOUNCE_MS / 1000.0) - 0.1

        # Third hit (after debounce)
        rhythm_bar.trigger_hit()
        assert mock_register.call_count == 2  # Increased to 2

def test_toggle_visibility(rhythm_bar):
    """Test the visibility toggle logic hides and shows the bar container."""
    # Initially packed
    assert rhythm_bar.bar_container.winfo_ismapped() == True

    # Toggle off
    rhythm_bar.last_toggle_time = 0 # reset toggle debounce
    rhythm_bar.is_visible.set(False)
    rhythm_bar._on_toggle_visibility()
    rhythm_bar.update()

    # Assert hidden
    assert rhythm_bar.bar_container.winfo_ismapped() == False

    # Toggle on
    rhythm_bar.last_toggle_time = 0 # reset toggle debounce
    rhythm_bar.is_visible.set(True)
    rhythm_bar._on_toggle_visibility()
    rhythm_bar.update()

    # Assert visible
    assert rhythm_bar.bar_container.winfo_ismapped() == True

def test_update_color_callback(rhythm_bar):
    """Test the color update callback works and handles missing widget safely."""
    rhythm_bar.update()
    # It shouldn't crash
    rhythm_bar._update_color(0.5)

    # Simulate destroyed widget
    rhythm_bar.destroy()
    # Shouldn't crash even if destroyed
    rhythm_bar._update_color(0.5)
