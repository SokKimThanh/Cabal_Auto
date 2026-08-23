# -*- coding: utf-8 -*-
"""
Database Importer Module.
Handles parsing Webpack/JSON files and importing monsters data into SQLite.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from lib.db.schema import MONSTER_COLUMNS


def extract_json_from_webpack(content: str) -> str:
    """Trích xuất chuỗi JSON từ file Webpack/JS."""
    start = content.find("JSON.parse('")
    if start == -1:
        return ""
    start += len("JSON.parse('")
    end = content.find("')", start)
    if end == -1:
        return ""
    json_str = content[start:end]
    json_str = json_str.replace("\\'", "'").replace('\\"', '"')
    return json_str


def load_monsters_data(data_file: Path) -> List[Dict[str, Any]]:
    """Load dữ liệu quái vật từ file JSON/txt."""
    if not data_file.exists():
        raise FileNotFoundError(f"File dữ liệu không tồn tại: {data_file}")

    with open(data_file, "r", encoding="utf-8") as f:
        content = f.read()

    json_str = extract_json_from_webpack(content)
    if not json_str:
        raise ValueError("Không thể trích xuất JSON hợp lệ từ file dữ liệu.")

    try:
        monsters = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Lỗi parse JSON: {e}")

    if not isinstance(monsters, list):
        raise ValueError("Dữ liệu JSON gốc phải là danh sách (list/array).")

    return monsters


def import_dungeons_from_monsters(conn: sqlite3.Connection, monsters_data: List[Dict[str, Any]]) -> None:
    """Import tự động các dungeonId phát sinh từ danh sách monsters."""
    cursor = conn.cursor()
    dungeon_ids = set()

    for monster in monsters_data:
        d_id = monster.get("dungeonId") or monster.get("locationId")
        if d_id and str(d_id).strip():
            dungeon_ids.add(str(d_id).strip())

    for d_id in dungeon_ids:
        cursor.execute(
            """
            INSERT OR IGNORE INTO dungeons (id, name)
            VALUES (?, ?)
            """,
            (d_id, d_id),
        )

    conn.commit()


def import_monsters(conn: sqlite3.Connection, monsters_data: List[Dict[str, Any]]) -> None:
    """Import danh sách quái vật vào bảng monsters sử dụng dungeonId (30 cột)."""
    cursor = conn.cursor()
    insert_data = []

    for monster in monsters_data:
        row_data = {}
        for col in MONSTER_COLUMNS:
            val = monster.get(col)

            if not val and col == 'dungeonId':
                val = monster.get('locationId')

            if col in ('dungeonId', 'serverBossType'):
                if val is not None and str(val).strip() != '':
                    row_data[col] = str(val).strip()
                else:
                    row_data[col] = None
            else:
                if col in ('name', 'id') and not val:
                    row_data[col] = ''
                else:
                    row_data[col] = val if val is not None else 0

        row = tuple(row_data.get(col) for col in MONSTER_COLUMNS)
        insert_data.append(row)

    placeholders = ','.join(['?'] * len(MONSTER_COLUMNS))
    columns_str = ','.join(MONSTER_COLUMNS)
    query = f"INSERT OR REPLACE INTO monsters ({columns_str}) VALUES ({placeholders})"

    cursor.executemany(query, insert_data)
    conn.commit()
    print(f"[DB] Đã import thành công {len(insert_data)} quái vật vào bảng monsters.")
