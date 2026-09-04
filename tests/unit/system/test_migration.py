import json
import pytest
import os
import tempfile
from unittest.mock import patch
from lib.features.hunt.config_migrator import migrate_hunt_config
from lib.features.hunt.hunt_config import load_hunt_config, HUNT_CONFIG_PATH

pytestmark = pytest.mark.unit


def test_idempotency():
    legacy_config = {
        "schema_version": 1,
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
    assert migrated_2["schema_version"] == 3

def test_backup(tmp_path):
    legacy_config = {
        "schema_version": 1,
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

    assert rotation[1]["monster_id"] == 200
    assert rotation[1]["priority"] == 2
    assert rotation[1]["name"] == "200"

    assert rotation[2]["monster_id"] == 300
    assert rotation[2]["priority"] == 3
    assert rotation[2]["name"] == "Dragon"

def test_priority_schema_enforced():
    legacy_config = {
        "monster_rotation": [
            {"priority": 1, "id": 50},
            {"priority": 2, "id": 60, "name": "Test"}
        ]
    }
    migrated = migrate_hunt_config(legacy_config)
    r1 = migrated["monster_rotation"][0]
    assert r1["monster_id"] == 50
    assert r1["priority"] == 1

    r2 = migrated["monster_rotation"][1]
    assert r2["monster_id"] == 60
    assert r2["priority"] == 2

def test_v2_to_v3_schema_bump():
    legacy_config = {
        "schema_version": 2,
        "monster_rotation": [{"monster_id": 100, "priority": 1, "name": "Test"}]
    }
    migrated = migrate_hunt_config(dict(legacy_config))
    assert migrated["schema_version"] == 3
    assert migrated["target_policy"] == "configured_only"
    assert migrated["ack_strategy"] == "none"
    assert migrated["hotbar_roi"] is None
    assert migrated["ack_timeout_ms"] == 500

def test_v3_current_schema_sanitizer_idempotency():
    config = {
        "schema_version": 3,
        "target_policy": "invalid_policy",
        "ack_strategy": "invalid",
        "hotbar_roi": [10, 20, "NaN", 40],
        "ack_timeout_ms": "abc"
    }
    migrated_1 = migrate_hunt_config(dict(config))
    assert migrated_1["target_policy"] == "configured_only"
    assert migrated_1["ack_strategy"] == "none"
    assert migrated_1["hotbar_roi"] is None
    assert migrated_1["ack_timeout_ms"] == 500

    migrated_2 = migrate_hunt_config(dict(migrated_1))
    assert migrated_1 == migrated_2

def test_target_policy_validation():
    for policy in ["configured_only", "all_resolved", "any_target"]:
        config = {"schema_version": 3, "target_policy": policy}
        migrated = migrate_hunt_config(dict(config))
        assert migrated["target_policy"] == policy

def test_skill_ack_metadata_validation():
    config = {
        "schema_version": 3,
        "ack_strategy": "combo",
        "hotbar_roi": [100, 200, 50, 50],
        "ack_timeout_ms": 1000
    }
    migrated = migrate_hunt_config(dict(config))
    assert migrated["ack_strategy"] == "combo"
    assert migrated["hotbar_roi"] == [100, 200, 50, 50]
    assert migrated["ack_timeout_ms"] == 1000

def test_atomic_failure_cleanup(tmp_path):
    from lib.features.hunt.hunt_config import save_hunt_config, HUNT_CONFIG_PATH
    import os

    config_file = tmp_path / "hunt_config.json"
    with open(config_file, "w") as f:
        f.write('{"valid": true}')

    with patch("lib.features.hunt.hunt_config.HUNT_CONFIG_PATH", config_file):
        with patch("os.replace", side_effect=Exception("Mocked replace failure")):
            result = save_hunt_config({"new": "data"})
            assert result is False

        # Ensure temp file was cleaned up. Only hunt_config.json should be in the dir
        files = list(tmp_path.glob("*"))
        assert len(files) == 1
        assert files[0] == config_file

        with open(config_file, "r") as f:
            assert f.read() == '{"valid": true}'

def test_monster_rotation_conflict_precedence():
    from lib.features.hunt.config_migrator import migrate_hunt_config

    legacy_config = {
        "monster_rotation": [
            {"monster_id": 999, "name": "Canonical"}
        ],
        "monsters": [
            {"id": 100, "name": "Legacy"}
        ],
        "monster_list": [101]
    }

    migrated = migrate_hunt_config(legacy_config)
    assert len(migrated["monster_rotation"]) == 1
    assert migrated["monster_rotation"][0]["monster_id"] == 999


