import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class SkillTypeService:
    def __init__(self):
        pass

    def get_all_skill_types(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT skill_type_id, name FROM skill_types ORDER BY skill_type_id ASC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[SkillTypeService] get_all_skill_types error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def create_skill_type(self, name: str) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO skill_types (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[SkillTypeService] create_skill_type error: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def update_skill_type(self, skill_type_id: int, name: str) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE skill_types SET name = ? WHERE skill_type_id = ?", (name, skill_type_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[SkillTypeService] update_skill_type error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def delete_skill_type(self, skill_type_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            # Let's check if it is used before deleting (or we can just try and fail if restricted)
            # Actually we just delete, if foreign key fails it raises error
            cursor.execute("DELETE FROM skill_types WHERE skill_type_id = ?", (skill_type_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[SkillTypeService] delete_skill_type error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass
