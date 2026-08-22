# -*- coding: utf-8 -*-
"""
Integration tests for Monster CRUD operations (Requirement 9).
Verifies:
1. Add monster with basic info only -> saved successfully.
2. Add monster with basic + extended info -> saved completely (30 fields).
3. Edit monster -> ID remains unchanged, values updated.
4. Delete monster -> confirmation and deletion.
5. get_monster_by_id() returns accurate record data.
"""

import sqlite3
import pytest
from pathlib import Path
from database import MonsterDatabase, get_db
from dialogs.monster_validator import validate_monster_data, SCHEMA_COLUMNS


@pytest.fixture
def test_db(tmp_path: Path):
    db_file = tmp_path / "test_monsters.db"
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row

    db = MonsterDatabase()
    db.DB_PATH = db_file
    db.conn = conn
    db.init_db()
    yield db
    db.close()


class TestMonsterCRUD:

    def test_1_add_monster_basic_info_only(self, test_db: MonsterDatabase):
        """1. Thêm quái vật chỉ với thông tin cơ bản -> lưu thành công."""
        basic_data = {
            "id": "m_test_101",
            "name": "Wolf Leader",
            "level": 15,
            "hp": 500,
            "dungeonId": "101",
            "serverBossType": "0",
        }

        is_valid, errors, cleaned = validate_monster_data(basic_data, is_new=True)
        assert is_valid, f"Validation failed: {errors}"

        success = test_db.insert_or_update_monster(cleaned)
        assert success, "Failed to insert monster into database"

        retrieved = test_db.get_monster_by_id("m_test_101")
        assert retrieved is not None, "Monster not found via get_monster_by_id()"
        assert retrieved["id"] == "m_test_101"
        assert retrieved["name"] == "Wolf Leader"
        assert retrieved["level"] == 15
        assert retrieved["hp"] == 500
        assert retrieved["dungeonId"] == "101"
        assert retrieved["serverBossType"] == "0"
        # Extended fields default to 0
        assert retrieved["defense"] == 0
        assert retrieved["accuracy"] == 0

    def test_2_add_monster_extended_info_full_schema(self, test_db: MonsterDatabase):
        """2. Thêm quái vật với cả thông tin mở rộng -> lưu đầy đủ (30 cột)."""
        full_data = {
            "id": "m_test_202",
            "name": "Dragon Boss",
            "level": 100,
            "exp": 50000,
            "hp": 20000,
            "defense": 800,
            "attackRate": 1200,
            "defenseRate": 900,
            "hpRecharge": 50,
            "accuracy": 300,
            "penetration": 150,
            "damageReduction": 100,
            "evasion": 80,
            "resistCritRate": 25,
            "primaryAttackMin": 500,
            "primaryAttackMax": 800,
            "secondaryAttackMin": 300,
            "secondaryAttackMax": 600,
            "ignoreAccuracy": 10,
            "ignoreDamageReduction": 15,
            "ignorePenetration": 20,
            "absoluteDamage": 150,
            "resistSkillAmp": 30,
            "resistCritDamage": 40,
            "resistSuppress": 5,
            "resistSilence": 10,
            "resistDiffDamage": 12,
            "hpProportionDamage": 8,
            "serverBossType": "1",
            "dungeonId": "102",
        }

        is_valid, errors, cleaned = validate_monster_data(full_data, is_new=True)
        assert is_valid, f"Validation failed: {errors}"

        success = test_db.insert_or_update_monster(cleaned)
        assert success, "Failed to insert full monster record"

        retrieved = test_db.get_monster_by_id("m_test_202")
        assert retrieved is not None, "Monster not found via get_monster_by_id()"

        # Verify all 30 columns
        for col in SCHEMA_COLUMNS:
            assert col in retrieved, f"Column '{col}' missing from retrieved record"
            assert retrieved[col] == full_data[col], f"Mismatch for '{col}': {retrieved[col]} != {full_data[col]}"

    def test_3_edit_monster_id_unchanged(self, test_db: MonsterDatabase):
        """3. Edit quái vật, id không đổi."""
        initial_data = {
            "id": "m_test_303",
            "name": "Skeleton Warrior",
            "level": 20,
            "hp": 800,
            "dungeonId": "101",
            "serverBossType": "0",
        }
        test_db.insert_or_update_monster(initial_data)

        # Edit monster attributes while keeping ID constant
        update_data = {
            "id": "m_test_303",  # Read-only ID
            "name": "Skeleton Commander",
            "level": 35,
            "hp": 2500,
            "defense": 150,
            "dungeonId": "102",
            "serverBossType": "1",
        }

        is_valid, errors, cleaned = validate_monster_data(update_data, is_new=False)
        assert is_valid, f"Validation failed: {errors}"

        success = test_db.insert_or_update_monster(cleaned)
        assert success, "Failed to update monster"

        retrieved = test_db.get_monster_by_id("m_test_303")
        assert retrieved is not None
        assert retrieved["id"] == "m_test_303"  # ID remains unchanged
        assert retrieved["name"] == "Skeleton Commander"
        assert retrieved["level"] == 35
        assert retrieved["hp"] == 2500
        assert retrieved["defense"] == 150

    def test_4_delete_monster(self, test_db: MonsterDatabase):
        """4. Delete quái vật, xác nhận trước khi xóa."""
        monster_data = {
            "id": "m_test_404",
            "name": "Ghost Spectre",
            "level": 25,
            "hp": 600,
        }
        test_db.insert_or_update_monster(monster_data)

        # Verify exists before deletion
        assert test_db.get_monster_by_id("m_test_404") is not None

        # Execute delete
        deleted = test_db.delete_monster("m_test_404")
        assert deleted, "Failed to delete monster from database"

        # Verify no longer exists
        assert test_db.get_monster_by_id("m_test_404") is None

    def test_5_get_monster_by_id_correct_data(self, test_db: MonsterDatabase):
        """5. Gọi get_monster_by_id() để xác nhận dữ liệu hiển thị đúng."""
        monster = {
            "id": "m_test_505",
            "name": "Ice Golem",
            "level": 80,
            "hp": 15000,
            "defense": 600,
            "primaryAttackMin": 400,
            "primaryAttackMax": 650,
            "dungeonId": "101",
            "serverBossType": "0",
        }
        test_db.insert_or_update_monster(monster)

        fetched = test_db.get_monster_by_id("m_test_505")
        assert fetched is not None
        assert fetched["id"] == "m_test_505"
        assert fetched["name"] == "Ice Golem"
        assert fetched["level"] == 80
        assert fetched["hp"] == 15000
        assert fetched["defense"] == 600
        assert fetched["primaryAttackMin"] == 400
        assert fetched["primaryAttackMax"] == 650
