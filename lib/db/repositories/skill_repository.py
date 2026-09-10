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

    def list_skills(
        self, class_id: Optional[int] = None, type_filter: Optional[str] = None, include_all: bool = False
    ) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            params = []
            conditions = []

            if not include_all and class_id is not None:
                # Filter by class_id using the class_skill_assignments table
                query = "SELECT s.* FROM skills s JOIN class_skill_assignments csa ON s.skill_id = csa.skill_id"
                conditions.append("csa.class_id = ?")
                params.append(class_id)
            else:
                # Get all skills (ignoring class_id)
                query = "SELECT * FROM skills"

            if type_filter is not None:
                if "JOIN" in query:
                    conditions.append("s.type = ?")
                else:
                    conditions.append("type = ?")
                params.append(type_filter)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Deduplicate just in case the JOIN returns multiple rows for the same skill
            if "JOIN" in query:
                query += " GROUP BY s.skill_id"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass
