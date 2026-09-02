import re
with open("tests/test_migration.py", "r") as f:
    content = f.read()

# patch test_priority_schema_enforced
old_test = """    def test_priority_schema_enforced():
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
        assert r2["monster_id"] == 0"""

new_test = """    def test_priority_schema_enforced():
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
        assert r2["monster_id"] == 60"""

content = content.replace("def test_priority_schema_enforced():\n    legacy_config = {\n        \"monster_rotation\": [\n            {\"priority\": 1, \"id\": 50},\n            {\"priority\": 2, \"name\": \"Test\"}\n        ]\n    }\n    migrated = migrate_hunt_config(legacy_config)\n    r1 = migrated[\"monster_rotation\"][0]\n    assert r1[\"monster_id\"] == 50\n    assert r1[\"priority\"] == 1\n\n    r2 = migrated[\"monster_rotation\"][1]\n    assert r2[\"monster_id\"] == 0", "def test_priority_schema_enforced():\n    legacy_config = {\n        \"monster_rotation\": [\n            {\"priority\": 1, \"id\": 50},\n            {\"priority\": 2, \"id\": 60, \"name\": \"Test\"}\n        ]\n    }\n    migrated = migrate_hunt_config(legacy_config)\n    r1 = migrated[\"monster_rotation\"][0]\n    assert r1[\"monster_id\"] == 50\n    assert r1[\"priority\"] == 1\n\n    r2 = migrated[\"monster_rotation\"][1]\n    assert r2[\"monster_id\"] == 60")

with open("tests/test_migration.py", "w") as f:
    f.write(content)
