import pytest
import tkinter as tk
import time
from unittest.mock import MagicMock, patch
from lib.events.event_bus import EventBus, SkillStatsUpdatedEvent
from ui.panels.skill_stats_panel import SkillStatsPanel
from lib.ui_style_v2 import UIStyleV2 as UI

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def app_mock():
    app = MagicMock()
    app._t.side_effect = lambda key, **kwargs: f"translated_{key}"
    return app

def test_skill_stats_panel_event_binding(root, app_mock, mocker):
    mocker.patch("ui.components.base.responsive_grid_base.ResponsiveGridBase.bind")
    panel = SkillStatsPanel(root, app_mock)
    panel.pack()

    # Mock after so it executes immediately in the test
    mocker.patch.object(panel, 'after', side_effect=lambda ms, func=None, *args: func(*args) if func else None)

    # Trigger event
    stats_data = {
        "Fireball": {"cast_count": 10, "last_cast": 1.2, "cooldown": 5.0, "success_rate": 85.5},
        "Heal": {"cast_count": 5, "last_cast": 0.5, "cooldown": 10.0, "success_rate": 100.0}
    }

    # Ensure it's not throttled by explicitly passing time
    panel._last_update_time = 0
    EventBus.trigger(SkillStatsUpdatedEvent(stats_data))
    root.update()

    # Verify items in Treeview
    children = panel.skill_stats_tree.get_children()
    assert len(children) == 2

    # Verify formatting (percentage)
    item_0_values = panel.skill_stats_tree.item(children[0], "values")
    assert item_0_values[0] == "Fireball"
    assert "85.5%" in item_0_values[4]

    item_1_values = panel.skill_stats_tree.item(children[1], "values")
    assert item_1_values[0] == "Heal"
    assert "100.0%" in item_1_values[4]

    panel.destroy()

def test_skill_stats_panel_destroyed_safe(root, app_mock, mocker):
    """Test that event callbacks do not crash if the widget is destroyed."""
    mocker.patch("ui.components.base.responsive_grid_base.ResponsiveGridBase.bind")
    panel = SkillStatsPanel(root, app_mock)

    # Destroy the widget intentionally
    panel.destroy()

    stats_data = {"Fireball": {"cast_count": 10, "success_rate": 85.5}}

    # Should not throw TclError
    EventBus.trigger(SkillStatsUpdatedEvent(stats_data))
    root.update()
