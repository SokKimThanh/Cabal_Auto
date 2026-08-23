# -*- coding: utf-8 -*-
"""
Module quản lý CSDL SQLite cho ứng dụng Auto Bot (Facade Pattern).
Xử lý schema setup, data import, và các query hỗ trợ UI.
Sử dụng các sub-module trong lib/db/ để duy trì file gọn nhẹ (< 500 dòng).
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from lib.db.schema import setup_schema, REQUIRED_TABLES, MONSTER_COLUMNS
from lib.db.seed import seed_reference_data
from lib.db import importer as db_importer
from lib.db import queries as db_queries
from lib.db import api as db_api

if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class MonsterDatabase:
    """Facade class quản lý kết nối và điều phối các thao tác với monsters.db"""

    DB_PATH = Path(__file__).parent / "monsters.db"
    DATA_FILE = Path(__file__).parent / "lib" / "data" / "monster-db-cabal.txt"
    LOCATION_FILE = Path(__file__).parent / "lib" / "data" / "location-db-cabal.txt"
    MONSTER_TYPE_FILE = (
        Path(__file__).parent / "lib" / "data" / "type-monster-db-cabal.txt"
    )

    REQUIRED_TABLES = REQUIRED_TABLES
    MONSTER_COLUMNS = MONSTER_COLUMNS

    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self) -> None:
        self.conn = sqlite3.connect(str(self.DB_PATH))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

    def setup_schema(self) -> None:
        setup_schema(self.conn)

    def seed_reference_data(self) -> None:
        seed_reference_data(self.conn, self.LOCATION_FILE, self.MONSTER_TYPE_FILE)

    def init_db(self) -> None:
        self.setup_schema()
        self.seed_reference_data()

    def load_monsters_data(self) -> List[Dict[str, Any]]:
        return db_importer.load_monsters_data(self.DATA_FILE)

    def import_dungeons_from_monsters(self, monsters_data: List[Dict[str, Any]]) -> None:
        db_importer.import_dungeons_from_monsters(self.conn, monsters_data)

    def import_monsters(self, monsters_data: List[Dict[str, Any]]) -> None:
        db_importer.import_monsters(self.conn, monsters_data)

    def get_monster_types(self) -> List[Any]:
        return db_queries.get_monster_types(self.conn)

    def get_monster_type_list(self) -> List[Dict[str, str]]:
        return db_queries.get_monster_type_list(self.conn)

    def get_dungeons(self) -> List[Any]:
        return db_queries.get_dungeons(self.conn)

    def get_dungeon_list(self) -> List[Dict[str, str]]:
        return db_queries.get_dungeon_list(self.conn)

    def get_filtered_monsters(self, **kwargs) -> Dict[str, Any]:
        return db_queries.get_filtered_monsters(self.conn, **kwargs)

    def get_all_monsters(self, limit: int = 100) -> List[Dict[str, Any]]:
        return db_queries.get_all_monsters(self.conn, limit)

    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        return db_queries.get_monster_by_id(self.conn, monster_id)

    def search_monsters(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        return db_queries.search_monsters(self.conn, keyword, limit)

    def insert_or_update_monster(self, monster: Dict[str, Any]) -> bool:
        return db_queries.insert_or_update_monster(self.conn, monster)

    def delete_monster(self, monster_id: str) -> bool:
        return db_queries.delete_monster(self.conn, monster_id)

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None


_db_instance: Optional[MonsterDatabase] = None


def get_db() -> MonsterDatabase:
    global _db_instance
    if _db_instance is None or _db_instance.conn is None:
        _db_instance = MonsterDatabase()
        _db_instance.init_db()
        db_api.set_api_db_instance(_db_instance)
    return _db_instance


def close_db() -> None:
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
        db_api.set_api_db_instance(None)


def init_database() -> None:
    get_db()


def get_all_monsters_api(limit: int = 100) -> List[Dict[str, Any]]:
    return get_db().get_all_monsters(limit)


def get_monster_by_id_api(monster_id: str) -> Optional[Dict[str, Any]]:
    return get_db().get_monster_by_id(monster_id)


def search_monsters_api(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    return get_db().search_monsters(keyword, limit)


def get_monster_types_api() -> List[Any]:
    return get_db().get_monster_types()


def get_dungeons_api() -> List[Any]:
    return get_db().get_dungeons()


def get_filtered_monsters_api(**kwargs) -> Dict[str, Any]:
    return get_db().get_filtered_monsters(**kwargs)


def check_db_health() -> Dict[str, Any]:
    return db_queries.check_db_health(MonsterDatabase.DB_PATH)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print(" SCRIPT TẠO DATABASE (MONSTER DB FACADE)")
    print("=" * 50)

    db = MonsterDatabase()
    print("[1] Khởi tạo cấu trúc bảng (Schema với 30 cột)...")
    db.init_db()

    print("[2] Bắt đầu đọc dữ liệu từ Webpack/JSON...")
    try:
        monsters_data = db.load_monsters_data()
        print(f"    -> Đã phân tích thành công {len(monsters_data)} thực thể.")

        print("[3] Nhập dữ liệu Dungeons từ dungeonId...")
        db.import_dungeons_from_monsters(monsters_data)

        print("[4] Nhập dữ liệu Monsters chính...")
        db.import_monsters(monsters_data)

        print("\n" + "-" * 50)
        print(" TÓM TẮT TÌNH TRẠNG DATABASE ")
        print("-" * 50)

        health = check_db_health()
        if health["ok"]:
            for table, count in health["counts"].items():
                print(f" [OK] Bảng {table.ljust(15)}: {count} bản ghi")
            print("\n>> HOÀN TẤT: CSDL `monsters.db` sẵn sàng!")
        else:
            print(f">> CẢNH BÁO: {health['error']}")

    except Exception as e:
        print(f"\n[LỖI] {e}")
    finally:
        db.close()
        print("=" * 50 + "\n")
