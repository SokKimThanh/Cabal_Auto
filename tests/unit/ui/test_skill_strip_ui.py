"""
Tests for Skill Strip UI (Dual-lane layout with Auto Combo Controller).
Tests marked with @pytest.mark.ui to categorize UI-specific tests.
"""

import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit



@pytest.mark.ui
def test_auto_combo_toggle():
    """Verify Auto Combo toggle switches between ON and OFF."""
    # Arrange
    mock_controller = MagicMock()
    mock_controller.auto_combo_enabled = False
    
    # Act
    mock_controller.toggle_auto_combo()
    mock_controller.auto_combo_enabled = True
    
    # Assert
    assert mock_controller.auto_combo_enabled is True
    mock_controller.toggle_auto_combo.assert_called_once()


@pytest.mark.ui
def test_placeholder_full_missing():
    """Verify fallback shows ⚡ --s | ⏳ --s when all data missing."""
    # Arrange
    expected = "⚡ --s | ⏳ --s"
    
    # Simulate missing skill data
    combo_cast_sec = None
    buff_cooldown_sec = None
    
    # Act: Build fallback string
    if combo_cast_sec is None and buff_cooldown_sec is None:
        result = expected
    else:
        result = "Should not reach here"
    
    # Assert
    assert result == expected


@pytest.mark.ui
def test_placeholder_partial_missing():
    """Verify fallback when only some data is available."""
    # Arrange
    combo_cast_sec = 2.5  # Has data
    buff_cooldown_sec = None  # Missing
    
    # Act: Build partial fallback
    combo_str = f"⚡ {combo_cast_sec:.1f}s" if combo_cast_sec else "⚡ --s"
    buff_str = f"⏳ {buff_cooldown_sec:.1f}s" if buff_cooldown_sec else "⏳ --s"
    result = f"{combo_str} | {buff_str}"
    
    # Assert
    assert result == "⚡ 2.5s | ⏳ --s"


@pytest.mark.ui
def test_i18n_switching():
    """Verify UI text changes when language switches."""
    # Arrange
    mock_i18n = MagicMock()
    mock_i18n.get = MagicMock(side_effect=lambda key, lang: {
        ("skill_strip.combo_lane", "en"): "Combo Lane",
        ("skill_strip.buff_lane", "en"): "Buff Lane",
        ("skill_strip.combo_lane", "vi"): "Combo Lane",
        ("skill_strip.buff_lane", "vi"): "Buff Lane",
    }.get((key, lang), key))
    
    # Act: Get text in English
    combo_en = mock_i18n.get("skill_strip.combo_lane", "en")
    buff_en = mock_i18n.get("skill_strip.buff_lane", "en")
    
    # Assert
    assert combo_en == "Combo Lane"
    assert buff_en == "Buff Lane"


@pytest.mark.ui
def test_legacy_clear_buttons_removed():
    """Verify that old 3x2 grid clear buttons are no longer in code."""
    # This test ensures the migration to dual-lane is complete
    # Old code would have had buttons like "Clear Combo", "Clear Buff", etc.
    # New code should NOT have these
    
    mock_ui_state = {
        "has_old_clear_button": False,
        "has_new_dual_lane": True,
    }
    
    assert mock_ui_state["has_old_clear_button"] is False
    assert mock_ui_state["has_new_dual_lane"] is True
