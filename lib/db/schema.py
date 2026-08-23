# -*- coding: utf-8 -*-
"""
Database Schema Setup Module.
Defines tables: dungeons, monster_type, monsters (30 columns).
"""

import sqlite3

REQUIRED_TABLES = ["monsters", "dungeons", "monster_type"]

MONSTER_COLUMNS = [
    "id",
    "name",
    "level",
    "exp",
    "hp",
    "defense",
    "attackRate",
    "defenseRate",
    "hpRecharge",
    "accuracy",
    "penetration",
    "damageReduction",
    "evasion",
    "resistCritRate",
    "primaryAttackMin",
    "primaryAttackMax",
    "secondaryAttackMin",
    "secondaryAttackMax",
    "ignoreAccuracy",
    "ignoreDamageReduction",
    "ignorePenetration",
    "absoluteDamage",
    "resistSkillAmp",
    "resistCritDamage",
    "resistSuppress",
    "resistSilence",
    "resistDiffDamage",
    "hpProportionDamage",
    "serverBossType",
    "dungeonId",
]


def setup_schema(conn: sqlite3.Connection) -> None:
    """Tạo schema bảng với dungeons, monster_type và monsters (30 cột)."""
    cursor = conn.cursor()

    # Bảng dungeons
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dungeons (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Bảng monster_type
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_type (
            value TEXT PRIMARY KEY,
            label TEXT NOT NULL
        )
    """)

    # Bảng monsters với 30 cột và khóa ngoại
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monsters (
            id TEXT PRIMARY KEY,
            name TEXT,
            level INTEGER,
            exp INTEGER,
            hp INTEGER,
            defense INTEGER,
            attackRate INTEGER,
            defenseRate INTEGER,
            hpRecharge INTEGER,
            accuracy INTEGER,
            penetration INTEGER,
            damageReduction INTEGER,
            evasion INTEGER,
            resistCritRate INTEGER,
            primaryAttackMin INTEGER,
            primaryAttackMax INTEGER,
            secondaryAttackMin INTEGER,
            secondaryAttackMax INTEGER,
            ignoreAccuracy INTEGER,
            ignoreDamageReduction INTEGER,
            ignorePenetration INTEGER,
            absoluteDamage INTEGER,
            resistSkillAmp INTEGER,
            resistCritDamage INTEGER,
            resistSuppress INTEGER,
            resistSilence INTEGER,
            resistDiffDamage INTEGER,
            hpProportionDamage INTEGER,
            serverBossType TEXT,
            dungeonId TEXT,
            FOREIGN KEY (dungeonId) REFERENCES dungeons(id) ON DELETE SET NULL,
            FOREIGN KEY (serverBossType) REFERENCES monster_type(value) ON DELETE SET NULL
        )
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_monsters_dungeonId ON monsters(dungeonId);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_monsters_serverBossType ON monsters(serverBossType);"
    )

    conn.commit()
