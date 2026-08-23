# -*- coding: utf-8 -*-
"""
Database Reference Data Seeding Module.
Seeds reference data for dungeons and monster_type.
"""

import re
import sqlite3
from pathlib import Path


def seed_dungeons(conn: sqlite3.Connection, location_file: Path) -> None:
    """Đọc file location-db-cabal.txt và chèn dữ liệu vào bảng dungeons."""
    if not location_file.exists():
        print(f"[DB] Bỏ qua seed dungeons: không tìm thấy {location_file}")
        return

    with open(location_file, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.findall(r'(\w+):\s*"([^"]+)"', content)
    if not entries:
        print("[DB] Không tìm thấy dữ liệu dungeons trong file.")
        return

    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO dungeons (id, name) VALUES (?, ?)",
        [(str(loc_id), name) for loc_id, name in entries],
    )
    conn.commit()
    print(f"[DB] Seed dungeons: đã xử lý {len(entries)} bản ghi.")


def seed_monster_type(conn: sqlite3.Connection, type_file: Path) -> None:
    """Đọc file type-monster-db-cabal.txt và chèn dữ liệu vào bảng monster_type."""
    if not type_file.exists():
        print(f"[DB] Bỏ qua seed monster_type: không tìm thấy {type_file}")
        return

    with open(type_file, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.findall(r'value:\s*"([^"]+)"[^}]*label:\s*"([^"]+)"', content)
    if not entries:
        print("[DB] Không tìm thấy dữ liệu monster_type trong file.")
        return

    filtered = [(v, label) for v, label in entries if v != "all"]

    cursor = conn.cursor()
    default_types = [("0", "Normal"), ("1", "Boss")]
    cursor.executemany(
        "INSERT OR IGNORE INTO monster_type (value, label) VALUES (?, ?)",
        default_types + filtered,
    )
    conn.commit()
    print(f"[DB] Seed monster_type: đã xử lý {len(filtered)} bản ghi.")


def seed_reference_data(conn: sqlite3.Connection, location_file: Path, type_file: Path) -> None:
    """Seed dữ liệu tham chiếu nếu bảng còn trống."""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM dungeons")
    if cursor.fetchone()[0] == 0:
        seed_dungeons(conn, location_file)

    cursor.execute("SELECT COUNT(*) FROM monster_type")
    if cursor.fetchone()[0] == 0:
        seed_monster_type(conn, type_file)
