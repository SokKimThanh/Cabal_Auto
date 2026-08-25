import pytest
from lib.features.hunt.config_validator import validate_hunt_area, get_valid_hunt_area

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
