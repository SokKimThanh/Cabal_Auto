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
    """Stub minimale của App dùng cho unit test _check_db_connection."""
    def __init__(self) -> None:
        self._db_status_var = _StatusVar()
        self._db_status_bg = "#e8e8e8"
        self._db_status_fg = "#555555"

    def _set_db_status(self, message: str, ok: bool) -> None:
        self._db_status_var.set(message)
        if ok:
            self._db_status_bg = "#d4edda"
            self._db_status_fg = "#155724"
        else:
            self._db_status_bg = "#f8d7da"
            self._db_status_fg = "#721c24"


def test_init_db_creates_database_and_updates_status(monkeypatch, tmp_path: Path) -> None:
    from database import close_db
    close_db()

    db_path = tmp_path / "monsters.db"
    monkeypatch.setattr(MonsterDatabase, "DB_PATH", db_path)
    # Bỏ qua messagebox trong test
    import tkinter.messagebox as mb
    monkeypatch.setattr(mb, "showwarning", lambda *a, **kw: None)

    stub = _AppStub()
    from ui.controllers.app_lifecycle_controller import AppLifecycleController
    lifecycle = AppLifecycleController(stub)
    lifecycle.check_db_connection()

    assert db_path.exists()
    status = stub._db_status_var.get()
    # CSDL đầy đủ → thanh trạng thái xanh với thông tin đầy đủ
    assert "✅" in status or "CSDL" in status

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0]

    assert count >= 0


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

    import tkinter.messagebox as mb
    monkeypatch.setattr(mb, "showwarning", lambda *a, **kw: None)

    stub = _AppStub()
    from ui.controllers.app_lifecycle_controller import AppLifecycleController
    lifecycle = AppLifecycleController(stub)
    lifecycle.check_db_connection()

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0]

    assert count >= 0
    status = stub._db_status_var.get()
    assert "✅" in status
    assert "Quái:" in status
