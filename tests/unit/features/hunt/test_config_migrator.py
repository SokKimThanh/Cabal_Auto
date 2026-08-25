import pytest
from lib.features.hunt.config_migrator import normalize_window_bounds_value, migrate_hunt_config

def test_normalize_window_bounds_value_dict():
    bounds = {"left": 10, "top": 20, "width": 100, "height": 200}
    assert normalize_window_bounds_value(bounds) == [10, 20, 100, 200]

def test_normalize_window_bounds_value_dict_malformed():
    bounds = {"left": 10, "top": 20, "width": 100}  # Missing height
    assert normalize_window_bounds_value(bounds) is None

def test_normalize_window_bounds_value_dict_invalid_types():
    bounds = {"left": 10, "top": 20, "width": "abc", "height": 200}
    assert normalize_window_bounds_value(bounds) is None

def test_normalize_window_bounds_value_list():
    bounds = [10, 20, 100, 200]
    assert normalize_window_bounds_value(bounds) == [10, 20, 100, 200]

def test_normalize_window_bounds_value_list_malformed():
    bounds = [10, 20, 100]  # Missing height
    assert normalize_window_bounds_value(bounds) is None

def test_normalize_window_bounds_value_list_invalid_types():
    bounds = [10, 20, "abc", 200]
    assert normalize_window_bounds_value(bounds) is None

def test_normalize_window_bounds_value_none():
    assert normalize_window_bounds_value(None) is None

def test_migrate_hunt_config_adds_ui_mode():
    cfg = {}
    migrate_hunt_config(cfg)
    assert cfg["ui_mode"] == "beginner"

def test_migrate_hunt_config_legacy_monsters_list_of_dicts():
    cfg = {
        "monsters": [
            {"id": "m1", "name": "Monster 1"},
            {"id": "m2", "name": "Monster 2"},
        ]
    }
    migrate_hunt_config(cfg)
    assert cfg["monster_rotation"] == ["m1", "m2"]
    assert cfg["monsters"] == []

def test_migrate_hunt_config_legacy_monsters_list_of_strings():
    cfg = {
        "monsters": ["m1", "m2"]
    }
    migrate_hunt_config(cfg)
    assert cfg["monster_rotation"] == ["m1", "m2"]
    assert cfg["monsters"] == []

def test_migrate_hunt_config_adds_defaults():
    cfg = {}
    migrate_hunt_config(cfg)
    assert cfg["monster_rotation"] == []
    assert cfg["skills"] == {}
    assert cfg["global_hotkeys"]["enabled"] is True
    assert cfg["hunt_area"] == {"window_bounds": None}

def test_migrate_hunt_config_normalizes_window_bounds():
    cfg = {
        "hunt_area": {
            "window_bounds": {"left": 10, "top": 20, "width": 100, "height": 200}
        }
    }
    migrate_hunt_config(cfg)
    assert cfg["hunt_area"]["window_bounds"] == [10, 20, 100, 200]

def test_migrate_hunt_config_malformed_hunt_area():
    cfg = {"hunt_area": None}
    migrate_hunt_config(cfg)
    assert cfg["hunt_area"] == {"window_bounds": None}

    cfg2 = {"hunt_area": []}
    migrate_hunt_config(cfg2)
    assert cfg2["hunt_area"] == {"window_bounds": None}

def test_migrate_hunt_config_malformed_global_hotkeys():
    cfg = {"global_hotkeys": None}
    migrate_hunt_config(cfg)
    assert cfg["global_hotkeys"]["enabled"] is True

    cfg2 = {"global_hotkeys": []}
    migrate_hunt_config(cfg2)
    assert cfg2["global_hotkeys"]["enabled"] is True

def test_migrate_hunt_config_malformed_top_level():
    cfg = migrate_hunt_config(None)
    assert isinstance(cfg, dict)
    assert cfg["hunt_area"] == {"window_bounds": None}

    cfg2 = migrate_hunt_config([])
    assert isinstance(cfg2, dict)
    assert cfg2["hunt_area"] == {"window_bounds": None}

def test_migrate_hunt_config_keeps_existing_fields():
    cfg = {
        "ui_mode": "advanced",
        "monster_rotation": ["m3"],
        "skills": {"slot1": "skill1"},
        "global_hotkeys": {"enabled": False, "start_key": "x"},
    }
    migrate_hunt_config(cfg)
    assert cfg["ui_mode"] == "advanced"
    assert cfg["monster_rotation"] == ["m3"]
    assert cfg["skills"] == {"slot1": "skill1"}
    assert cfg["global_hotkeys"]["enabled"] is False
    assert cfg["global_hotkeys"]["start_key"] == "x"
