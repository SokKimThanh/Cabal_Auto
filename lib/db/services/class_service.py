import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class ClassService:
    def __init__(self):
        pass

    def create_class(self, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO classes (name, description, icon_path, str_base, int_base, dex_base)
                VALUES (:name, :description, :icon_path, :str_base, :int_base, :dex_base)
                """,
                {
                    "name": data.get("name"),
                    "description": data.get("description", ""),
                    "icon_path": data.get("icon_path", ""),
                    "str_base": data.get("str_base", 0),
                    "int_base": data.get("int_base", 0),
                    "dex_base": data.get("dex_base", 0),
                }
            )
            class_id = cursor.lastrowid
            conn.commit()
            return class_id
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ClassService] Create error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_class_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_id = ?", (class_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[ClassService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_all_classes(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ClassService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def update_class(self, class_id: int, data: Dict[str, Any]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE classes
                SET name = COALESCE(:name, name),
                    description = COALESCE(:description, description),
                    icon_path = COALESCE(:icon_path, icon_path),
                    str_base = COALESCE(:str_base, str_base),
                    int_base = COALESCE(:int_base, int_base),
                    dex_base = COALESCE(:dex_base, dex_base)
                WHERE class_id = :class_id
                """,
                {
                    "class_id": class_id,
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "icon_path": data.get("icon_path"),
                    "str_base": data.get("str_base"),
                    "int_base": data.get("int_base"),
                    "dex_base": data.get("dex_base"),
                }
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ClassService] Update error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def delete_class(self, class_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classes WHERE class_id = ?", (class_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except sqlite3.IntegrityError as e:
            try: conn.rollback()
            except: pass
            print(f"[ClassService] Integrity error on delete (FK violation?): {e}")
            return False
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[ClassService] Delete error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
