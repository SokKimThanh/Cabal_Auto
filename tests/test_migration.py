import json
import pytest
import os
import tempfile
from unittest.mock import patch
from lib.features.hunt.config_migrator import migrate_hunt_config
from lib.features.hunt.hunt_config import load_hunt_config, HUNT_CONFIG_PATH

def test_idempotency():
    legacy_config = {
        "ui_mode": "beginner",
        "monsters": [
            {"id": "100", "name": "Goblin"},
            {"id": "101", "name": "Orc"}
        ],
        "skills": {
            "1": {"key": "1", "cast_time": 1.5, "cooldown": 2.0}
        }
    }

    migrated_1 = migrate_hunt_config(dict(legacy_config))
    migrated_2 = migrate_hunt_config(dict(migrated_1))

    assert migrated_1 == migrated_2
    assert migrated_2["schema_version"] == 2

def test_backup(tmp_path):
    legacy_config = {
        "ui_mode": "beginner",
        "monsters": [{"id": "100", "name": "Goblin"}]
    }

    config_file = tmp_path / "hunt_config.json"
    with open(config_file, "w") as f:
        json.dump(legacy_config, f)

    with patch("lib.features.hunt.hunt_config.HUNT_CONFIG_PATH", config_file):
        load_hunt_config()

    backup_file = config_file.with_suffix(".json.bak")
    assert backup_file.exists()

    with open(backup_file, "r") as f:
        backup_content = json.load(f)
    assert backup_content == legacy_config

def test_conflict_precedence():
    legacy_config = {
        "skills": {
            "1": {"key": "1", "cast_time": 2.0, "cooldown": 3.0}
        },
        "attack_keys": [
            {"key": "1", "cast_time": 1.0, "cooldown": 1.0},
            {"key": "2", "cast_time": 0.5, "cooldown": 0.5}
        ]
    }

    migrated = migrate_hunt_config(legacy_config)
    skills = {s["key"]: s for s in migrated["skill_slots"]}

    assert skills["1"]["cast_time"] == 2.0  # skills precedence
    assert skills["1"]["cooldown"] == 3.0

    assert skills["2"]["cast_time"] == 0.5  # attack_keys fallback
    assert skills["2"]["cooldown"] == 0.5

def test_malformed_entry_skipped():
    legacy_config = {
        "skills": {
            "1": {"key": "1", "cast_time": 1.5},
            "2": {"key": "2"}  # missing cast_time
        }
    }

    migrated = migrate_hunt_config(legacy_config)
    skills = [s["key"] for s in migrated["skill_slots"]]

    assert "1" in skills
    assert "2" not in skills

def test_monster_rotation_migration():
    legacy_config = {
        "monsters": [
            {"id": "100", "name": "Goblin"},
            "200",
            {"monster_id": "300", "name": "Dragon"}
        ]
    }

    migrated = migrate_hunt_config(legacy_config)
    rotation = migrated["monster_rotation"]

    assert len(rotation) == 3
    assert rotation[0]["monster_id"] == 100
    assert rotation[0]["priority"] == 1
    assert rotation[0]["name"] == "Goblin"

    assert rotation[1]["monster_id"] == 0
    assert rotation[1]["priority"] == 2
    assert rotation[1]["name"] == "200"

    assert rotation[2]["monster_id"] == 300
    assert rotation[2]["priority"] == 3
    assert rotation[2]["name"] == "Dragon"

def test_priority_schema_enforced():
    legacy_config = {
        "monster_rotation": [
            {"priority": 1, "id": 50},
            {"priority": 2, "name": "Test"}
        ]
    }
    migrated = migrate_hunt_config(legacy_config)
    r1 = migrated["monster_rotation"][0]
    assert r1["monster_id"] == 50
    assert r1["priority"] == 1

    r2 = migrated["monster_rotation"][1]
    assert r2["monster_id"] == 0
    assert r2["priority"] == 2
