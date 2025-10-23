import json
import os
import pytest
from pathlib import Path


def test_migrate_attack_keys(tmp_path):
    # Import inside test to avoid import-time side effects
    import app_gui as ag
    # Prepare a temporary hunt_config.json with legacy attack_keys
    data = {
        "window_title": "Cabal",
        "attack_keys": ["1", "2", "3", "4"]
    }
    lib_data = tmp_path / 'lib' / 'data'
    lib_data.mkdir(parents=True, exist_ok=True)
    hunt_config = lib_data / 'hunt_config.json'
    with open(hunt_config, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    orig = ag.HUNT_CONFIG_PATH
    try:
        ag.HUNT_CONFIG_PATH = hunt_config
        cfg = ag.load_hunt_config()
        # After load, attack_keys should be removed and skill_slots present
        assert 'attack_keys' not in cfg
        assert isinstance(cfg.get('skill_slots'), list)
        assert len(cfg['skill_slots']) == 4
        assert cfg['skill_slots'][0]['key'] == '1'
    finally:
        ag.HUNT_CONFIG_PATH = orig


def test_attack_keys_derived_from_skill_slots(tmp_path):
    import app_gui as ag
    lib_data = tmp_path / 'lib' / 'data'
    lib_data.mkdir(parents=True, exist_ok=True)
    hunt_config = lib_data / 'hunt_config.json'
    data = {
        "window_title": "Cabal",
        "skill_slots": [
            {"name": "", "key": "1"},
            {"name": "", "key": "4"}
        ]
    }
    with open(hunt_config, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    orig = ag.HUNT_CONFIG_PATH
    try:
        ag.HUNT_CONFIG_PATH = hunt_config
        cfg = ag.load_hunt_config()
        assert isinstance(cfg.get('skill_slots'), list)
        keys = [s.get('key') for s in cfg.get('skill_slots', [])]
        assert keys == ['1', '4']
    finally:
        ag.HUNT_CONFIG_PATH = orig
