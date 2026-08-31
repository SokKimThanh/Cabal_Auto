import pytest
import sqlite3
from unittest.mock import patch, MagicMock

from lib.db.adapters.catalogue_adapters import MonsterCatalogueLookup, SkillCatalogueLookup, SkillRuntimeView

@pytest.fixture
def mock_db_connection():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE monsters (
            id TEXT PRIMARY KEY,
            name TEXT,
            hp INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE classes (
            class_id INTEGER PRIMARY KEY,
            name TEXT,
            class_code TEXT,
            icon_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE skills (
            skill_id INTEGER PRIMARY KEY,
            name TEXT,
            alias TEXT,
            icon_x INTEGER,
            icon_y INTEGER,
            icon_w INTEGER,
            icon_h INTEGER,
            class_id INTEGER,
            type TEXT
        )
    """)

    # Seed data
    cursor.execute("INSERT INTO monsters (id, name, hp) VALUES ('m1', 'Wolf', 100)")
    cursor.execute("INSERT INTO classes (class_id, name, class_code, icon_path) VALUES (1, 'Warrior', 'warrior', 'icon.png')")
    cursor.execute("INSERT INTO skills (skill_id, name, alias, icon_x, icon_y, icon_w, icon_h, class_id, type) VALUES (1, 'Slash', 'slash_alias', 10, 20, 30, 40, 1, 'attack')")
    cursor.execute("INSERT INTO skills (skill_id, name, alias, icon_x, icon_y, icon_w, icon_h, class_id, type) VALUES (2, 'Unmapped Skill', 'unmapped', 0, 0, 0, 0, NULL, 'utility')")

    conn.commit()

    with patch("lib.db.adapters.catalogue_adapters.get_connection", return_value=(conn, False)) as mock_get_conn:
        yield conn

def test_monster_catalogue_lookup_success(mock_db_connection):
    ref = MonsterCatalogueLookup.get_reference_by_id('m1')
    assert ref is not None
    assert ref['name'] == 'Wolf'
    assert ref['hp'] == 100

    ref2 = MonsterCatalogueLookup.get_reference_by_name('Wolf')
    assert ref2 is not None
    assert ref2['id'] == 'm1'

def test_monster_catalogue_lookup_missing(mock_db_connection):
    ref = MonsterCatalogueLookup.get_reference_by_id('non_existent')
    assert ref is None

def test_skill_catalogue_lookup_success(mock_db_connection):
    ref = SkillCatalogueLookup.get_reference_by_name('Slash')
    assert ref is not None
    assert ref['name'] == 'Slash'
    assert ref['alias'] == 'slash_alias'
    assert 'class_data' in ref
    assert ref['class_data']['name'] == 'Warrior'

def test_skill_catalogue_lookup_unmapped(mock_db_connection):
    ref = SkillCatalogueLookup.get_reference_by_name('Unmapped Skill')
    assert ref is not None
    assert ref['name'] == 'Unmapped Skill'
    assert 'class_data' not in ref

def test_skill_catalogue_lookup_missing(mock_db_connection):
    ref = SkillCatalogueLookup.get_reference_by_name('Not exist')
    assert ref is None

def test_skill_runtime_view_preserves_user_config():
    user_skill = {
        "name": "My Custom Slash",
        "key": "5",
        "type": "attack",
        "cooldown": 1.2,
        "cast_time": 0.8,
        "image": "custom.png",
        "rotation": 1
    }

    catalogue_record = {
        "name": "Slash",
        "alias": "slash",
        "icon_x": 10,
        "icon_y": 10,
        "icon_w": 32,
        "icon_h": 32,
        "class_data": {
            "name": "Warrior",
            "class_code": "warrior",
            "icon_path": "warrior.png"
        }
    }

    view = SkillRuntimeView.build_view(user_skill, catalogue_record)

    # Must preserve exactly what user set
    assert view["name"] == "My Custom Slash"
    assert view["key"] == "5"
    assert view["cooldown"] == 1.2
    assert view["cast_time"] == 0.8
    assert view["image"] == "custom.png"
    assert view["rotation"] == 1

    # Should be enriched with catalogue data under separate keys
    assert view["catalogue_alias"] == "slash"
    assert view["catalogue_icon"]["x"] == 10
    assert view["class_name"] == "Warrior"

def test_skill_runtime_view_without_catalogue():
    user_skill = {
        "name": "My Custom Slash",
        "key": "5",
        "cooldown": 1.2
    }

    view = SkillRuntimeView.build_view(user_skill)

    assert view["name"] == "My Custom Slash"
    assert view["key"] == "5"
    assert "catalogue_alias" not in view
