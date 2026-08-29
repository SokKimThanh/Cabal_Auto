import os
import sqlite3
import pytest
from pathlib import Path

def test_import_database():
    import database
    from database import MonsterDatabase
    assert database is not None
    assert MonsterDatabase is not None

def test_database_init():
    import database
    from database import init_database

    # Optional: ensure db path
    db_path = database.MonsterDatabase.DB_PATH
    if db_path.exists():
        os.remove(db_path)

    init_database()

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    assert "monsters" in tables
    assert "dungeons" in tables
    assert "monster_type" in tables

    # Check seed data
    cursor.execute("SELECT COUNT(*) FROM dungeons")
    dungeon_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM monster_type")
    type_count = cursor.fetchone()[0]

    assert type_count > 0
    assert dungeon_count > 0

    conn.close()
