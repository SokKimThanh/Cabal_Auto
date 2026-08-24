import pytest
from lib.features.hunt.hunt_config import _normalize_window_bounds_value, _sanitize_templates

def test_normalize_window_bounds_value_rejects_zero_width_height():
    assert _normalize_window_bounds_value({"left": 0, "top": 0, "width": 0, "height": 100}) is None
    assert _normalize_window_bounds_value({"left": 0, "top": 0, "width": 100, "height": -1}) is None
    assert _normalize_window_bounds_value({"left": 10, "top": 20, "width": 100, "height": 100}) == [10, 20, 100, 100]

def test_sanitize_templates_preserves_grayscale():
    input_templates = [{"path": "dummy.png", "grayscale": True}]
    result = _sanitize_templates(input_templates)
    assert len(result) == 1
    assert result[0].get("grayscale") is True

def test_normalize_window_bounds_value_accepts_list_and_dict():
    # Test 1: Dict
    assert _normalize_window_bounds_value({"left": 1, "top": 2, "width": 3, "height": 4}) == [1, 2, 3, 4]
    # Test 2: List (flow simulation)
    from lib.features.hunt.hunt_config import _normalize_window_bounds
    data = {"hunt_area": {"window_bounds": {"left": 1, "top": 2, "width": 3, "height": 4}}}
    _normalize_window_bounds(data)
    # data["hunt_area"]["window_bounds"] should now be [1, 2, 3, 4]
    assert data["hunt_area"]["window_bounds"] == [1, 2, 3, 4]

    # Second pass from load_hunt_config
    res = _normalize_window_bounds_value(data["hunt_area"].get("window_bounds"))
    assert res == [1, 2, 3, 4]

    # Check rejecting <= 0 in list format
    assert _normalize_window_bounds_value([1, 2, 0, 4]) is None
    assert _normalize_window_bounds_value([1, 2, 3, -1]) is None
