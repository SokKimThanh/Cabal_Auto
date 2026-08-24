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
