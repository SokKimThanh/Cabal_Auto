import sqlite3
from pathlib import Path

import pytest

from database import MonsterDatabase
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
    db.conn.execute(
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
    db.conn.commit()

    stub = _AppStub()
    App._check_db_connection(stub)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0]

    assert count == 1
    assert "Loaded 1 quái vật" in stub.hunt_status.get()
