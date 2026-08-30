import pytest
import sqlite3
from unittest.mock import patch, mock_open
from lib.db.services.seed_skill_sprite_service import SeedSkillSpriteService


@pytest.fixture
def memory_db():
    conn = sqlite3.connect(':memory:')
    # Create the schema WITHOUT the icon_* columns to verify the dynamic addition
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            alias TEXT,
            class_id INTEGER,
            type TEXT
        )
    """)
    conn.commit()
    yield conn
    conn.close()


def test_seed_with_empty_db(memory_db):
    # Mock get_connection to return our memory DB
    with patch('lib.db.services.seed_skill_sprite_service.get_connection', return_value=(memory_db, False)):
        service = SeedSkillSpriteService()

        # We'll mock _extract_sprites directly for the DB test to isolate from file reading
        mock_sprites = {
            "test_skill_1": {"x": 10, "y": 20, "width": 30, "height": 40},
            "test_skill_2": {"x": 50, "y": 60, "width": 30, "height": 40}
        }

        with patch.object(service, '_extract_sprites', return_value=(mock_sprites, "dummy_hash")):
            result = service.seed_skill_sprites()

            assert result["status"] == "PASSED"
            assert result["inserted"] == 2
            assert result["skipped"] == 0

            # Verify columns were created properly
            cursor = memory_db.cursor()
            cursor.execute("PRAGMA table_info(skills)")
            columns = [col[1] for col in cursor.fetchall()]
            assert "skill_code" in columns
            assert "icon_x" in columns
            assert "icon_y" in columns
            assert "icon_w" in columns
            assert "icon_h" in columns

            # Verify data
            cursor.execute("SELECT skill_code, icon_x, icon_y FROM skills ORDER BY skill_code")
            rows = cursor.fetchall()
            assert len(rows) == 2
            assert rows[0] == ("test_skill_1", 10, 20)
            assert rows[1] == ("test_skill_2", 50, 60)


def test_seed_idempotency(memory_db):
    with patch('lib.db.services.seed_skill_sprite_service.get_connection', return_value=(memory_db, False)):
        service = SeedSkillSpriteService()
        mock_sprites = {
            "test_skill_1": {"x": 10, "y": 20, "width": 30, "height": 40}
        }

        with patch.object(service, '_extract_sprites', return_value=(mock_sprites, "dummy_hash")):
            # First insert
            result1 = service.seed_skill_sprites()
            assert result1["status"] == "PASSED"
            assert result1["inserted"] == 1
            assert result1["skipped"] == 0

            # Second insert (should be skipped)
            result2 = service.seed_skill_sprites()
            assert result2["status"] == "PASSED"
            assert result2["inserted"] == 0
            assert result2["skipped"] == 1

            # Still only 1 record
            cursor = memory_db.cursor()
            cursor.execute("SELECT COUNT(*) FROM skills")
            assert cursor.fetchone()[0] == 1


def test_malformed_source_no_boundary():
    service = SeedSkillSpriteService()
    # Source file content without JSON.parse('
    malformed_content = "This is some text but not the right boundary."

    with patch('builtins.open', mock_open(read_data=malformed_content)):
        with pytest.raises(ValueError, match="Could not find JSON.parse boundary"):
            service._extract_sprites()


def test_malformed_source_invalid_json():
    service = SeedSkillSpriteService()
    # Source file content with bad JSON inside the boundary
    malformed_content = "some text JSON.parse('{ \"sprites\": { bad json } }') more text"

    with patch('builtins.open', mock_open(read_data=malformed_content)):
        with pytest.raises(ValueError, match="Failed to decode JSON"):
            service._extract_sprites()


def test_forbidden_file():
    service = SeedSkillSpriteService("lib/data/skills.json")
    with pytest.raises(ValueError, match="Unauthorized source file"):
        service._extract_sprites()
