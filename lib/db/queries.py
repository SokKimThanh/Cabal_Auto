# -*- coding: utf-8 -*-
"""
Database Queries Module.
Handles query operations, filtering, pagination, health checks, and CRUD operations.
"""

import math
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from lib.db.schema import MONSTER_COLUMNS, REQUIRED_TABLES


def get_monster_types(conn: sqlite3.Connection) -> List[Any]:
    """Lấy danh sách các serverBossType distinct."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT serverBossType
        FROM monsters
        WHERE serverBossType IS NOT NULL AND serverBossType != ''
        ORDER BY serverBossType
    """)
    return [row[0] for row in cursor.fetchall()]


def get_monster_type_list(conn: sqlite3.Connection) -> List[Dict[str, str]]:
    """Trả về danh sách loại quái dạng [{'value': '1', 'label': 'Boss'}, ...]"""
    cursor = conn.cursor()
    cursor.execute("SELECT value, label FROM monster_type ORDER BY value")
    return [{"value": row[0], "label": row[1]} for row in cursor.fetchall()]


def get_dungeons(conn: sqlite3.Connection) -> List[Any]:
    """Lấy danh sách dungeonId từ bảng dungeons."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM dungeons ORDER BY id")
    return [row[0] for row in cursor.fetchall()]


def get_dungeon_list(conn: sqlite3.Connection) -> List[Dict[str, str]]:
    """Trả về danh sách dungeon dạng [{'id': '1', 'name': 'Bloody Ice'}, ...]"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM dungeons ORDER BY id")
    return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]


def get_filtered_monsters(
    conn: sqlite3.Connection,
    keyword: str = "",
    monster_type: Optional[str] = None,
    dungeon_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    sort_column: str = "name",
    sort_order: str = "ASC",
) -> Dict[str, Any]:
    """Lấy danh sách quái vật theo filter có phân trang."""
    safe_page = max(1, int(page or 1))
    safe_page_size = max(1, int(page_size or 25))
    allowed_columns = set(MONSTER_COLUMNS)
    safe_sort_column = sort_column if sort_column in allowed_columns else "name"
    safe_sort_order = str(sort_order or "ASC").upper()
    if safe_sort_order not in {"ASC", "DESC"}:
        safe_sort_order = "ASC"

    filters: List[str] = []
    params: List[Any] = []

    if keyword and str(keyword).strip():
        filters.append("name LIKE ?")
        params.append(f"%{str(keyword).strip()}%")

    if monster_type and str(monster_type).strip() not in ("All Monsters", "All", ""):
        filters.append("serverBossType = ?")
        params.append(str(monster_type).strip())

    if dungeon_id and str(dungeon_id).strip() not in ("All Dungeons", "All Locations", "All", ""):
        filters.append("dungeonId = ?")
        params.append(str(dungeon_id).strip())

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ""

    cursor = conn.cursor()

    count_query = f"SELECT COUNT(*) AS total FROM monsters{where_clause}"
    cursor.execute(count_query, params)
    total_records = int(cursor.fetchone()["total"] or 0)
    total_pages = max(1, math.ceil(total_records / safe_page_size)) if total_records else 1

    offset = (safe_page - 1) * safe_page_size
    sql = (
        f"SELECT * FROM monsters{where_clause} "
        f"ORDER BY {safe_sort_column} {safe_sort_order} "
        f"LIMIT ? OFFSET ?"
    )
    cursor.execute(sql, params + [safe_page_size, offset])

    return {
        "items": [dict(row) for row in cursor.fetchall()],
        "total_records": total_records,
        "total_pages": total_pages,
    }


def get_all_monsters(conn: sqlite3.Connection, limit: int = 100) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, level, hp FROM monsters LIMIT ?", (limit,))
    return [dict(row) for row in cursor.fetchall()]


def get_monster_by_id(conn: sqlite3.Connection, monster_id: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monsters WHERE id = ?", (str(monster_id),))
    row = cursor.fetchone()
    return dict(row) if row else None


def search_monsters(conn: sqlite3.Connection, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, level, hp FROM monsters WHERE name LIKE ? LIMIT ?",
        (f"%{keyword}%", limit),
    )
    return [dict(row) for row in cursor.fetchall()]


def insert_or_update_monster(conn: sqlite3.Connection, monster: Dict[str, Any]) -> bool:
    """Chèn hoặc cập nhật một quái vật (INSERT OR REPLACE) hỗ trợ 30 cột."""
    columns = MONSTER_COLUMNS
    data = {k: v for k, v in monster.items() if k in columns}

    for col in ('dungeonId', 'serverBossType'):
        if col in data:
            if data[col] is None or str(data[col]).strip() == '' or str(data[col]).lower() == 'none':
                data[col] = None
            else:
                data[col] = str(data[col]).strip()

    if not data.get("id"):
        print("[DB] Lỗi insert/update monster: missing 'id'")
        return False

    for col in columns:
        if col not in data:
            if col in ('dungeonId', 'serverBossType'):
                data[col] = None
            elif col == 'name':
                data[col] = ''
            elif col == 'id':
                data[col] = str(monster.get('id', ''))
            else:
                try:
                    data[col] = int(monster.get(col, 0))
                except (ValueError, TypeError):
                    data[col] = 0

    placeholders = ','.join(['?' for _ in data])
    columns_str = ','.join(data.keys())
    values = list(data.values())
    sql = f"INSERT OR REPLACE INTO monsters ({columns_str}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB] Lỗi insert/update monster: {e}")
        return False


def delete_monster(conn: sqlite3.Connection, monster_id: str) -> bool:
    """Xóa quái vật theo ID. Chỉ trả về True nếu có hàng thực sự bị xóa."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM monsters WHERE id = ?", (str(monster_id),))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DB] Lỗi xóa monster: {e}")
        return False


def check_db_health(db_path: Path) -> Dict[str, Any]:
    """Kiểm tra tình trạng CSDL SQLite."""
    required = REQUIRED_TABLES

    if not db_path.exists():
        return {
            "ok": False,
            "missing_tables": required,
            "counts": {},
            "error": f"Không tìm thấy file CSDL: {db_path}",
        }

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing = {row[0] for row in cursor.fetchall()}

        missing = [t for t in required if t not in existing]
        if missing:
            return {"ok": False, "missing_tables": missing, "counts": {}, "error": None}

        counts: Dict[str, int] = {}
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            for table in required:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]

        return {"ok": True, "missing_tables": [], "counts": counts, "error": None}
    except Exception as exc:
        return {
            "ok": False,
            "missing_tables": required,
            "counts": {},
            "error": str(exc),
        }
