import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class SkillService:
    def __init__(self):
        pass

    def create_skill(self, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Check class_id exists
            class_id = data.get("class_id")
            if class_id is not None:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {class_id} does not exist.")

            cursor.execute(
                """
                INSERT INTO skills (name, alias, icon_x, icon_y, icon_w, icon_h, class_id, type)
                VALUES (:name, :alias, :icon_x, :icon_y, :icon_w, :icon_h, :class_id, :type)
                """,
                {
                    "name": data.get("name"),
                    "alias": data.get("alias"),
                    "icon_x": data.get("icon_x", 0),
                    "icon_y": data.get("icon_y", 0),
                    "icon_w": data.get("icon_w", 0),
                    "icon_h": data.get("icon_h", 0),
                    "class_id": class_id,
                    "type": data.get("type"),
                }
            )
            skill_id = cursor.lastrowid
            conn.commit()
            return skill_id
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SkillService] Create error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_skill_by_id(self, skill_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[SkillService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_skills_by_filter(self, class_id: Optional[int] = None, skill_type: Optional[str] = None) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM skills WHERE 1=1"
            params = []

            if class_id is not None:
                query += " AND class_id = ?"
                params.append(class_id)
            if skill_type is not None:
                query += " AND type = ?"
                params.append(skill_type)

            query += " ORDER BY name ASC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[SkillService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def update_skill(self, skill_id: int, data: Dict[str, Any]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Check class_id exists if provided
            class_id = data.get("class_id")
            if class_id is not None:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {class_id} does not exist.")

            cursor.execute(
                """
                UPDATE skills
                SET name = COALESCE(:name, name),
                    alias = COALESCE(:alias, alias),
                    icon_x = COALESCE(:icon_x, icon_x),
                    icon_y = COALESCE(:icon_y, icon_y),
                    icon_w = COALESCE(:icon_w, icon_w),
                    icon_h = COALESCE(:icon_h, icon_h),
                    class_id = COALESCE(:class_id, class_id),
                    type = COALESCE(:type, type)
                WHERE skill_id = :skill_id
                """,
                {
                    "skill_id": skill_id,
                    "name": data.get("name"),
                    "alias": data.get("alias"),
                    "icon_x": data.get("icon_x"),
                    "icon_y": data.get("icon_y"),
                    "icon_w": data.get("icon_w"),
                    "icon_h": data.get("icon_h"),
                    "class_id": class_id,
                    "type": data.get("type"),
                }
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SkillService] Update error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def delete_skill(self, skill_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM skills WHERE skill_id = ?", (skill_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except sqlite3.IntegrityError as e:
            try: conn.rollback()
            except: pass
            print(f"[SkillService] Integrity error on delete (FK violation?): {e}")
            return False
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SkillService] Delete error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
