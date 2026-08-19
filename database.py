# -*- coding: utf-8 -*-
"""
Module quản lý CSDL SQLite cho ứng dụng Auto Bot.
"""

import json
import logging
import math
import re
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


LOGGER = logging.getLogger(__name__)
ALL_FILTER_LABEL = "Tất cả"
UNKNOWN_LOCATION_LABEL = "Chưa xác định"
UNKNOWN_MONSTER_TYPE_LABEL = "Chưa xác định"
LEGACY_ALL_FILTERS = {ALL_FILTER_LABEL, "All", "All Monsters", "All Locations", ""}


class MonsterDatabase:
    """Quản lý thao tác với database monsters.db."""

    DB_PATH = Path(__file__).parent / "monsters.db"
    DATA_DIR = Path(__file__).parent / "lib" / "data"
    LOCATION_SEED_FILE = "location-db-cabal.txt"
    MONSTER_TYPE_SEED_FILE = "type-monster-db-cabal.txt"

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
        "priority",
        "damage_per_hit",
        "description",
        "template",
        "training_mode",
        "window_bounds",
        "templates",
    ]

    NUMERIC_COLUMNS = {
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
        "priority",
        "damage_per_hit",
    }

    def __init__(self, db_path: Optional[Path] = None, data_dir: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else self.DB_PATH
        self.data_dir = Path(data_dir) if data_dir else self.DATA_DIR

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn

    def init_db(self) -> None:
        """Khởi tạo schema và seed dữ liệu lookup."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS location (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monster_type (
                    id INTEGER PRIMARY KEY,
                    label TEXT NOT NULL,
                    sort_order INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monsters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL DEFAULT '',
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
                    serverBossType INTEGER,
                    dungeonId TEXT,
                    priority INTEGER NOT NULL DEFAULT 1,
                    damage_per_hit REAL NOT NULL DEFAULT 0,
                    description TEXT NOT NULL DEFAULT '',
                    template TEXT NOT NULL DEFAULT '',
                    training_mode INTEGER NOT NULL DEFAULT 0,
                    window_bounds TEXT,
                    templates TEXT NOT NULL DEFAULT '[]',
                    FOREIGN KEY (dungeonId) REFERENCES location(id) ON DELETE SET NULL,
                    FOREIGN KEY (serverBossType) REFERENCES monster_type(id) ON DELETE SET NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dungeons (
                    dungeonId TEXT PRIMARY KEY,
                    name TEXT
                )
                """
            )
            self._ensure_monsters_columns(conn)

        self._seed_location_table()
        self._seed_monster_type_table()

    def init_database_data(self) -> None:
        """Backward-compatible alias."""
        self.init_db()

    def setup_schema(self) -> None:
        """Backward-compatible alias."""
        self.init_db()

    def _ensure_monsters_columns(self, conn: sqlite3.Connection) -> None:
        existing_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(monsters)").fetchall()
        }
        required_columns = {
            "priority": "INTEGER NOT NULL DEFAULT 1",
            "damage_per_hit": "REAL NOT NULL DEFAULT 0",
            "description": "TEXT NOT NULL DEFAULT ''",
            "template": "TEXT NOT NULL DEFAULT ''",
            "training_mode": "INTEGER NOT NULL DEFAULT 0",
            "window_bounds": "TEXT",
            "templates": "TEXT NOT NULL DEFAULT '[]'",
        }

        for column_name, definition in required_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE monsters ADD COLUMN {column_name} {definition}"
                )

    def _seed_location_table(self) -> None:
        seed_path = self.data_dir / self.LOCATION_SEED_FILE
        if not seed_path.exists():
            LOGGER.warning("Missing location seed file: %s", seed_path)
            return

        content = seed_path.read_text(encoding="utf-8")
        records = [
            (match.group(1), match.group(2).replace('\\"', '"'))
            for match in re.finditer(r"(\d+):\s*\"([^\"]+)\"", content)
        ]

        with self._connect() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO location (id, name) VALUES (?, ?)",
                records,
            )
            conn.executemany(
                "INSERT OR IGNORE INTO dungeons (dungeonId, name) VALUES (?, ?)",
                records,
            )

    def _seed_monster_type_table(self) -> None:
        seed_path = self.data_dir / self.MONSTER_TYPE_SEED_FILE
        if not seed_path.exists():
            LOGGER.warning("Missing monster type seed file: %s", seed_path)
            return

        content = seed_path.read_text(encoding="utf-8")
        records: List[tuple[int, str, int]] = []
        for sort_order, match in enumerate(
            re.finditer(
                r'value:\s*"(?P<value>[^"]+)"\s*,\s*label:\s*"(?P<label>[^"]+)"',
                content,
            ),
            start=1,
        ):
            raw_value = match.group("value").strip()
            if not raw_value.isdigit():
                continue
            records.append((int(raw_value), match.group("label").strip(), sort_order))

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO monster_type (id, label, sort_order)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    label = excluded.label,
                    sort_order = excluded.sort_order
                """,
                records,
            )

    def _base_select(self) -> str:
        return f"""
            SELECT
                monsters.{", monsters.".join(self.MONSTER_COLUMNS)},
                COALESCE(location.name, '{UNKNOWN_LOCATION_LABEL}') AS location_name,
                COALESCE(monster_type.label, '{UNKNOWN_MONSTER_TYPE_LABEL}') AS monster_type_name
            FROM monsters
            LEFT JOIN location ON location.id = monsters.dungeonId
            LEFT JOIN monster_type ON monster_type.id = monsters.serverBossType
        """

    def _deserialize_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        templates_raw = data.get("templates")
        window_bounds_raw = data.get("window_bounds")

        if isinstance(templates_raw, str):
            try:
                data["templates"] = json.loads(templates_raw)
            except json.JSONDecodeError:
                data["templates"] = []
        elif templates_raw is None:
            data["templates"] = []

        if isinstance(window_bounds_raw, str) and window_bounds_raw.strip():
            try:
                data["window_bounds"] = json.loads(window_bounds_raw)
            except json.JSONDecodeError:
                data["window_bounds"] = None
        else:
            data["window_bounds"] = None

        data["training_mode"] = bool(data.get("training_mode", 0))
        return data

    def get_monster_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM monsters").fetchone()
        return int(row["total"] or 0) if row else 0

    def get_monster_types(self) -> List[Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT label FROM monster_type ORDER BY sort_order, label"
            ).fetchall()
        return [row["label"] for row in rows]

    def get_locations(self) -> List[Any]:
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT DISTINCT COALESCE(location.name, '{UNKNOWN_LOCATION_LABEL}') AS location_name
                FROM monsters
                LEFT JOIN location ON location.id = monsters.dungeonId
                ORDER BY LOWER(location_name) ASC
                """
            ).fetchall()
        return [row["location_name"] for row in rows]

    def _sort_expression(self, sort_column: str) -> str:
        text_map = {
            "name": "LOWER(COALESCE(monsters.name, ''))",
            "dungeonId": "LOWER(COALESCE(location.name, ''))",
            "serverBossType": "LOWER(COALESCE(monster_type.label, ''))",
            "location_name": "LOWER(COALESCE(location.name, ''))",
            "monster_type_name": "LOWER(COALESCE(monster_type.label, ''))",
            "description": "LOWER(COALESCE(monsters.description, ''))",
            "template": "LOWER(COALESCE(monsters.template, ''))",
        }
        if sort_column in text_map:
            return text_map[sort_column]
        if sort_column in self.MONSTER_COLUMNS:
            return (
                "CASE "
                f"WHEN monsters.{sort_column} IS NULL OR TRIM(CAST(monsters.{sort_column} AS TEXT)) = '' "
                "THEN 0 "
                f"ELSE CAST(monsters.{sort_column} AS REAL) END"
            )
        return "LOWER(COALESCE(monsters.name, ''))"

    def get_filtered_monsters(
        self,
        keyword: str = "",
        monster_type: Optional[str] = None,
        location: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_column: str = "name",
        sort_order: str = "ASC",
    ) -> Dict[str, Any]:
        safe_page = max(1, int(page or 1))
        safe_page_size = max(1, int(page_size or 25))
        safe_sort_order = str(sort_order or "ASC").upper()
        if safe_sort_order not in {"ASC", "DESC"}:
            safe_sort_order = "ASC"

        filters: List[str] = []
        params: List[Any] = []

        if keyword and str(keyword).strip():
            filters.append("monsters.name LIKE ?")
            params.append(f"%{str(keyword).strip()}%")

        normalized_type = str(monster_type or "").strip()
        if normalized_type not in LEGACY_ALL_FILTERS:
            filters.append(
                f"COALESCE(monster_type.label, '{UNKNOWN_MONSTER_TYPE_LABEL}') = ?"
            )
            params.append(normalized_type)

        normalized_location = str(location or "").strip()
        if normalized_location not in LEGACY_ALL_FILTERS:
            filters.append(f"COALESCE(location.name, '{UNKNOWN_LOCATION_LABEL}') = ?")
            params.append(normalized_location)

        where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
        base_select = self._base_select()
        sort_expression = self._sort_expression(sort_column)

        with self._connect() as conn:
            count_row = conn.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM monsters
                LEFT JOIN location ON location.id = monsters.dungeonId
                LEFT JOIN monster_type ON monster_type.id = monsters.serverBossType
                {where_clause}
                """,
                params,
            ).fetchone()
            total_records = int(count_row["total"] or 0) if count_row else 0
            total_pages = (
                max(1, math.ceil(total_records / safe_page_size)) if total_records else 1
            )
            offset = (safe_page - 1) * safe_page_size
            rows = conn.execute(
                f"""
                {base_select}
                {where_clause}
                ORDER BY {sort_expression} {safe_sort_order}, LOWER(COALESCE(monsters.name, '')) ASC
                LIMIT ? OFFSET ?
                """,
                params + [safe_page_size, offset],
            ).fetchall()

        return {
            "items": [self._deserialize_row(row) for row in rows],
            "total_records": total_records,
            "total_pages": total_pages,
        }

    def get_all_monsters(self, limit: int = 100) -> List[Dict[str, Any]]:
        safe_limit = max(1, int(limit or 100))
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                {self._base_select()}
                ORDER BY LOWER(COALESCE(monsters.name, '')) ASC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [self._deserialize_row(row) for row in rows]

    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                f"{self._base_select()} WHERE monsters.id = ?",
                (monster_id,),
            ).fetchone()
        return self._deserialize_row(row) if row else None

    def search_monsters(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        payload = self.get_filtered_monsters(
            keyword=keyword,
            page=1,
            page_size=max(1, int(limit or 50)),
        )
        return payload["items"]

    def _normalize_monster(self, monster: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for column in self.MONSTER_COLUMNS:
            if column == "id":
                normalized[column] = str(monster.get("id") or uuid.uuid4())
                continue

            value = monster.get(column)
            if column == "name":
                normalized[column] = str(value or "").strip()
            elif column == "dungeonId":
                normalized[column] = str(value).strip() if value not in (None, "") else None
            elif column == "serverBossType":
                if value in (None, ""):
                    normalized[column] = None
                else:
                    normalized[column] = int(value)
            elif column == "training_mode":
                normalized[column] = 1 if bool(value) else 0
            elif column == "window_bounds":
                normalized[column] = (
                    json.dumps(value, ensure_ascii=False) if value not in (None, "") else None
                )
            elif column == "templates":
                normalized[column] = json.dumps(value or [], ensure_ascii=False)
            elif column in self.NUMERIC_COLUMNS:
                if value in (None, ""):
                    normalized[column] = 0
                elif column == "damage_per_hit":
                    normalized[column] = float(value)
                else:
                    normalized[column] = int(float(value))
            elif column in {"description", "template"}:
                normalized[column] = str(value or "")
            else:
                normalized[column] = value

        return normalized

    def replace_monsters(self, monsters: List[Dict[str, Any]]) -> None:
        normalized_rows = [self._normalize_monster(monster) for monster in monsters]
        placeholders = ", ".join("?" for _ in self.MONSTER_COLUMNS)
        columns_sql = ", ".join(self.MONSTER_COLUMNS)

        with self._connect() as conn:
            conn.execute("DELETE FROM monsters")
            if normalized_rows:
                conn.executemany(
                    f"INSERT INTO monsters ({columns_sql}) VALUES ({placeholders})",
                    [tuple(row[column] for column in self.MONSTER_COLUMNS) for row in normalized_rows],
                )

    def delete_monster(self, monster_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))

    def close(self) -> None:
        """Backward-compatible no-op."""
        return None


_db_instance: Optional[MonsterDatabase] = None


def get_db() -> MonsterDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = MonsterDatabase()
        _db_instance.init_db()
    return _db_instance


def close_db() -> None:
    global _db_instance
    _db_instance = None


def init_database() -> None:
    get_db()


def get_all_monsters(limit: int = 100) -> List[Dict[str, Any]]:
    return get_db().get_all_monsters(limit)


def get_monster_by_id(monster_id: str) -> Optional[Dict[str, Any]]:
    return get_db().get_monster_by_id(monster_id)


def search_monsters(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    return get_db().search_monsters(keyword, limit)


def get_monster_types() -> List[Any]:
    return get_db().get_monster_types()


def get_locations() -> List[Any]:
    return get_db().get_locations()


def get_filtered_monsters(
    keyword: str = "",
    monster_type: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    sort_column: str = "name",
    sort_order: str = "ASC",
) -> Dict[str, Any]:
    return get_db().get_filtered_monsters(
        keyword=keyword,
        monster_type=monster_type,
        location=location,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_order=sort_order,
    )
