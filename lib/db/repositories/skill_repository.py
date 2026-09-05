import sqlite3
from typing import Optional, List, Dict, Any
from lib.db.connection import get_connection

class SkillRepository:
    def get_skill(self, skill_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass
    def list_skills(self, class_id: Optional[int] = None, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        conn, _ = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM skills"
            params = []
            conditions = []

            if class_id is not None:
                conditions.append("class_id = ?")
                params.append(class_id)
            if type_filter is not None:
                conditions.append("type = ?")
                params.append(type_filter)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
