import json
import sqlite3
import pytest
from database import MonsterDatabase
from lib.db.migrations import m001_add_skill_ids_to_builds
from lib.db.services.build_service import BuildService

@pytest.fixture
def test_db():
    db = MonsterDatabase()
    # Ensure it starts fresh
    cursor = db.conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS builds")
    cursor.execute("""
        CREATE TABLE builds (
            build_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            author TEXT,
            description TEXT,
            upvote_count INTEGER DEFAULT 0
        )
    """)
    db.conn.commit()
    return db

def test_migration_up_down(test_db):
    # Migration Up
    m001_add_skill_ids_to_builds.up(test_db.conn)
    cursor = test_db.conn.cursor()
    cursor.execute("PRAGMA table_info(builds)")
    cols = [c[1] for c in cursor.fetchall()]
    assert "attack_skill_ids" in cols
    assert "buff_skill_ids" in cols

    # Insert a record
    cursor.execute("INSERT INTO builds (class_id, author, description, attack_skill_ids, buff_skill_ids) VALUES (1, 'Test', 'Test', '[]', '[]')")
    test_db.conn.commit()

    # Migration Down
    m001_add_skill_ids_to_builds.down(test_db.conn)
    cursor.execute("PRAGMA table_info(builds)")
    cols = [c[1] for c in cursor.fetchall()]
    assert "attack_skill_ids" not in cols
    assert "buff_skill_ids" not in cols

def test_legacy_build_parsing(test_db, monkeypatch):
    cursor = test_db.conn.cursor()
    cursor.execute("INSERT INTO builds (class_id, author, description, upvote_count) VALUES (1, 'Legacy', 'Test Legacy', 0)")
    test_db.conn.commit()
    build_id = cursor.lastrowid

    # After inserting legacy build, migrate up
    m001_add_skill_ids_to_builds.up(test_db.conn)

    svc = BuildService()
    # Mock get_connection to return our test_db connection
    import lib.db.services.build_service
    monkeypatch.setattr(lib.db.services.build_service, 'get_connection', lambda: (test_db.conn, False))

    build = svc.get_build_by_id(build_id)
    assert build is not None
    assert build["author"] == "Legacy"
    assert build["attack_skill_ids"] == []
    assert build["buff_skill_ids"] == []

def test_create_and_update_build(test_db, monkeypatch):
    m001_add_skill_ids_to_builds.up(test_db.conn)

    # Create classes table needed for foreign key constraint in build service
    cursor = test_db.conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS classes (class_id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT OR IGNORE INTO classes (class_id, name) VALUES (1, 'TestClass')")
    test_db.conn.commit()

    svc = BuildService()
    import lib.db.services.build_service
    monkeypatch.setattr(lib.db.services.build_service, 'get_connection', lambda: (test_db.conn, False))

    build_id = svc.create_build({
        "class_id": 1,
        "author": "NewAuthor",
        "description": "NewDesc",
        "attack_skill_ids": [1, 2, 3],
        "buff_skill_ids": [4]
    })

    assert build_id is not None

    build = svc.get_build_by_id(build_id)
    assert build["attack_skill_ids"] == [1, 2, 3]
    assert build["buff_skill_ids"] == [4]

    updated = svc.update_build(build_id, {
        "attack_skill_ids": [1, 2]
    })

    assert updated is True

    build2 = svc.get_build_by_id(build_id)
    assert build2["attack_skill_ids"] == [1, 2]
    assert build2["buff_skill_ids"] == [4]
