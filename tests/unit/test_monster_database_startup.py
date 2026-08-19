import sqlite3
from pathlib import Path
import re

import pytest

import app_gui
from database import MonsterDatabase, close_db
from app_gui import App


pytestmark = pytest.mark.db


class _StatusVar:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


class _AppStub:
    def __init__(self) -> None:
        self.hunt_status = _StatusVar()


def test_init_db_creates_database_and_updates_status(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "monsters.db"
    monkeypatch.setattr(MonsterDatabase, "DB_PATH", db_path)

    stub = _AppStub()
    App._check_db_connection(stub)

    assert db_path.exists()
    assert "Loaded 0 quái vật" in stub.hunt_status.get()

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0]

    assert count == 0


def test_init_db_reuses_existing_database_without_overwriting(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "monsters.db"
    monkeypatch.setattr(MonsterDatabase, "DB_PATH", db_path)

    db = MonsterDatabase()
    db.init_db()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO monsters (id, name, level, hp, defense, attackRate, defenseRate, hpRecharge,
                accuracy, penetration, damageReduction, evasion, resistCritRate,
                primaryAttackMin, primaryAttackMax, secondaryAttackMin, secondaryAttackMax,
                ignoreAccuracy, ignoreDamageReduction, ignorePenetration, absoluteDamage,
                resistSkillAmp, resistCritDamage, resistSuppress, resistSilence,
                resistDiffDamage, hpProportionDamage, serverBossType, dungeonId, exp)
            VALUES (?, ?, 1, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0)
            """,
            ("m-existing", "Existing Monster"),
        )

    stub = _AppStub()
    App._check_db_connection(stub)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0]

    assert count == 1
    assert "Loaded 1 quái vật" in stub.hunt_status.get()


def test_init_db_seeds_location_and_monster_type_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "monsters.db"
    source_data_dir = Path("F:/Cabal_Auto.worktrees/tdd-automation-testing-upgrade/lib/data")
    db = MonsterDatabase(db_path=db_path, data_dir=source_data_dir)

    db.init_db()

    location_seed = (source_data_dir / "location-db-cabal.txt").read_text(encoding="utf-8")
    monster_type_seed = (source_data_dir / "type-monster-db-cabal.txt").read_text(encoding="utf-8")
    expected_locations = len(re.findall(r"(\d+):\s*\"([^\"]+)\"", location_seed))
    expected_types = len(re.findall(r'value:\s*"(\d+)"\s*,\s*label:\s*"([^\"]+)"', monster_type_seed))

    with sqlite3.connect(db_path) as conn:
        location_count = conn.execute("SELECT COUNT(*) FROM location").fetchone()[0]
        monster_type_count = conn.execute("SELECT COUNT(*) FROM monster_type").fetchone()[0]

    assert location_count == expected_locations
    assert monster_type_count == expected_types


def test_init_db_logs_warning_when_seed_files_are_missing(caplog, tmp_path: Path) -> None:
    db_path = tmp_path / "monsters.db"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db = MonsterDatabase(db_path=db_path, data_dir=data_dir)

    with caplog.at_level("WARNING"):
        db.init_db()

    assert db_path.exists()
    assert "Missing location seed file" in caplog.text
    assert "Missing monster type seed file" in caplog.text


def test_monster_library_roundtrip_uses_database(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "monsters.db"
    json_path = tmp_path / "monsters.json"
    monkeypatch.setattr(MonsterDatabase, "DB_PATH", db_path)
    monkeypatch.setattr(app_gui, "MONSTER_DB_PATH", json_path)
    close_db()

    app_gui.save_monster_library(
        [
            {
                "id": "lib-1",
                "name": "Goblin",
                "hp": 150,
                "damage_per_hit": 20,
                "description": "DB only",
                "template": "",
                "templates": [],
                "training_mode": False,
            }
        ]
    )
    loaded = app_gui.load_monster_library()

    assert len(loaded) == 1
    assert loaded[0]["name"] == "Goblin"
    assert loaded[0]["damage_per_hit"] == 20
    assert not json_path.exists()
    close_db()
