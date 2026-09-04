import pytest
from lib.features.hunt.config_validator import validate_hunt_area, get_valid_hunt_area, normalize_window_bounds_value

pytestmark = pytest.mark.unit


def test_validate_hunt_area_empty():
    assert validate_hunt_area({}) == {"window_title": None, "window_bounds": None}
    assert validate_hunt_area(None) == {"window_title": None, "window_bounds": None}

def test_validate_hunt_area_valid():
    hunt_area = {
        "window_title": "Cabal",
        "window_bounds": {"left": 0, "top": 0, "width": 800, "height": 600}
    }
    assert validate_hunt_area(hunt_area) == {
        "window_title": "Cabal",
        "window_bounds": [0, 0, 800, 600]
    }

def test_validate_hunt_area_list_bounds():
    hunt_area = {
        "window_title": "Cabal",
        "window_bounds": [10, 20, 800, 600]
    }
    assert validate_hunt_area(hunt_area) == {
        "window_title": "Cabal",
        "window_bounds": [10, 20, 800, 600]
    }

def test_validate_hunt_area_malformed_title():
    hunt_area = {
        "window_title": 123,
        "window_bounds": [10, 20, 800, 600]
    }
    assert validate_hunt_area(hunt_area) == {
        "window_title": "123",
        "window_bounds": [10, 20, 800, 600]
    }

def test_validate_hunt_area_malformed_bounds():
    hunt_area = {
        "window_title": "Game",
        "window_bounds": "invalid"
    }
    assert validate_hunt_area(hunt_area) == {
        "window_title": "Game",
        "window_bounds": None
    }

def test_get_valid_hunt_area_empty_config():
    assert get_valid_hunt_area({}) == {"window_title": None, "window_bounds": None}
    assert get_valid_hunt_area(None) == {"window_title": None, "window_bounds": None}

def test_get_valid_hunt_area_missing_hunt_area():
    cfg = {"ui_mode": "beginner"}
    assert get_valid_hunt_area(cfg) == {"window_title": None, "window_bounds": None}

def test_get_valid_hunt_area_with_valid_data():
    cfg = {
        "hunt_area": {
            "window_title": "MyWindow",
            "window_bounds": {"left": 5, "top": 10, "width": 640, "height": 480}
        }
    }
    assert get_valid_hunt_area(cfg) == {
        "window_title": "MyWindow",
        "window_bounds": [5, 10, 640, 480]
    }


def test_normalize_window_bounds_value_minimized():
    assert normalize_window_bounds_value([ -32000, -32000, 100, 100 ]) is None
    assert normalize_window_bounds_value({ "left": -32000, "top": -32000, "width": 100, "height": 100 }) is None

def test_normalize_window_bounds_value_invalid_size():
    assert normalize_window_bounds_value([ 0, 0, 0, 100 ]) is None
    assert normalize_window_bounds_value([ 0, 0, 100, -10 ]) is None

def test_get_valid_hunt_area_preserves_keys():
    cfg = {
        "hunt_area": {
            "window_title": "MyWindow",
            "window_bounds": [5, 10, 640, 480],
            "extra_key": "should_be_removed_by_schema"
        }
    }
    result = get_valid_hunt_area(cfg)
    assert result == {
        "window_title": "MyWindow",
        "window_bounds": [5, 10, 640, 480]
    }
    assert "extra_key" not in result
