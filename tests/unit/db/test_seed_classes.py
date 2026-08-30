import pytest
import sqlite3
import os
import sys
import tempfile
from pathlib import Path

# Thêm đường dẫn gốc để import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from lib.db.services.seed_classes_service import SeedClassesService
import database

@pytest.fixture
def test_db_setup():
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_monsters.db"

    # Save original DB_PATH
    orig_db_path = database.MonsterDatabase.DB_PATH
    database.MonsterDatabase.DB_PATH = db_path

    # Initialize schema
    db = database.get_db()
    db.setup_schema()

    yield db_path

    database.close_db()
    # Restore original
    database.MonsterDatabase.DB_PATH = orig_db_path
    if db_path.exists():
        os.remove(db_path)
    os.rmdir(temp_dir)

def test_seed_classes_idempotent(test_db_setup):
    service = SeedClassesService() # Uses real txt file fallback
    src, acc, rej = service.seed_classes()

    assert src == 9
    assert acc == 9
    assert rej == 0

    db = database.get_db()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM classes")
    count = cursor.fetchone()[0]
    assert count == 9

    # Run second time
    src2, acc2, rej2 = service.seed_classes()
    assert acc2 == 9

    cursor.execute("SELECT COUNT(*) FROM classes")
    count2 = cursor.fetchone()[0]
    assert count2 == 9

def test_seed_classes_parse_robustness():
    # Write a temporary text file with malformed data
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "fake_data.txt"
    with open(temp_file, "w") as f:
        f.write("""
        blader: { id: "blader_x", name: "Blader X", description: "foo", icon: "bar.png" }
        m = {
            blader: { str: 10, int: 5, dex: 15 }
        };
        # Malformed class: missing stats
        warrior: { id: "warrior", name: "Warrior", description: "foo", icon: "w.png" }
        """)

    service = SeedClassesService(filepath=str(temp_file))
    valid, rejected, h = service.parse_classes()

    # Blader X should be accepted, Warrior rejected
    assert len(valid) == 1
    assert rejected == 1
    assert valid[0]['class_code'] == 'blader-x' # Normalization check
    assert h != ""

    os.remove(temp_file)
    os.rmdir(temp_dir)

def test_seed_classes_empty_db(test_db_setup):
    # Verify empty db state first
    db = database.get_db()
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM classes")
    assert cursor.fetchone()[0] == 0

    service = SeedClassesService()
    src, acc, rej = service.seed_classes()
    assert acc == 9

def test_seed_classes_backfill_duplicate_names(test_db_setup):
    # Setup dummy data with non-unique names that might clash in standard backfill
    db = database.get_db()
    cursor = db.conn.cursor()
    cursor.execute("INSERT INTO classes (name) VALUES ('Test Class')")
    cursor.execute("INSERT INTO classes (name) VALUES ('Test Class')")
    db.conn.commit()

    service = SeedClassesService()
    # The backfill logic tries to lower(replace(name)). Doing this with duplicates
    # should NOT crash the migration but rather just skip assigning the index to those
    # that failed the unique check OR fail schema migration gracefully.
    # The current patch handles OperationalError.

    # However since we need unique backfill:
    # Actually if they fail unique index creation, sqlite catches it.

    # Run schema migration manually to test
    service.apply_schema_migrations()

    cursor.execute("SELECT name, class_code FROM classes")
    rows = cursor.fetchall()

    # Because of the duplicate name, the first one gets 'test-class',
    # But when we try to create the unique index, if they BOTH have 'test-class', it fails.
    # Our migration doesn't crash but logs error on index creation if it does.
    # The actual seed overrides anyway.
