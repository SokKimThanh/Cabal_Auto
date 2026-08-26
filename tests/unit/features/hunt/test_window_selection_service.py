import pytest
from lib.features.hunt.window_selection_service import WindowSelectionService

def test_resolve_bounds_with_current():
    cfg = {"hunt_area": {"window_bounds": [10, 10, 100, 100]}, "window_bounds": [20, 20, 200, 200]}
    # current bounds take precedence
    assert WindowSelectionService.resolve_bounds(cfg, [5, 5, 50, 50]) == [5, 5, 50, 50]

def test_resolve_bounds_with_hunt_area():
    cfg = {"hunt_area": {"window_bounds": [10, 10, 100, 100]}, "window_bounds": [20, 20, 200, 200]}
    # hunt_area takes precedence if no current
    assert WindowSelectionService.resolve_bounds(cfg) == [10, 10, 100, 100]

def test_resolve_bounds_with_legacy_root():
    cfg = {"window_bounds": [20, 20, 200, 200]}
    # legacy root is fallback
    assert WindowSelectionService.resolve_bounds(cfg) == [20, 20, 200, 200]

def test_resolve_bounds_none_returns_none():
    assert WindowSelectionService.resolve_bounds({}) is None
    assert WindowSelectionService.resolve_bounds(None) is None

def test_update_bounds_creates_hunt_area():
    cfg = {}
    normalized = WindowSelectionService.update_bounds(cfg, [1, 2, 3, 4])
    assert normalized == [1, 2, 3, 4]
    assert cfg["window_bounds"] == [1, 2, 3, 4]
    assert cfg["hunt_area"]["window_bounds"] == [1, 2, 3, 4]

def test_update_bounds_updates_existing():
    cfg = {"hunt_area": {"window_bounds": [10, 10, 10, 10]}, "window_bounds": [20, 20, 20, 20]}
    normalized = WindowSelectionService.update_bounds(cfg, [5, 5, 50, 50])
    assert normalized == [5, 5, 50, 50]
    assert cfg["window_bounds"] == [5, 5, 50, 50]
    assert cfg["hunt_area"]["window_bounds"] == [5, 5, 50, 50]

def test_update_bounds_handles_invalid():
    cfg = {}
    normalized = WindowSelectionService.update_bounds(cfg, "invalid")
    assert normalized is None
    assert cfg["window_bounds"] is None
    assert cfg["hunt_area"]["window_bounds"] is None

def test_resolve_bounds_missing_or_invalid_minimized_rect():
    cfg = {"hunt_area": {"window_bounds": [-32000, -32000, 100, 100]}} # Minimized
    assert WindowSelectionService.resolve_bounds(cfg) is None

    cfg = {"hunt_area": {"window_bounds": None}} # Missing
    assert WindowSelectionService.resolve_bounds(cfg) is None

    cfg = {"hunt_area": {"window_bounds": [0, 0, 0, 100]}} # Invalid height
    assert WindowSelectionService.resolve_bounds(cfg) is None
