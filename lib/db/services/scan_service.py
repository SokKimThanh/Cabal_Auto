import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from lib.db.connection import get_connection


class ScanService:
    def __init__(self):
        pass

    def create_scan(self, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Constraints checking
            if "monster_id" in data and data["monster_id"]:
                cursor.execute(
                    "SELECT 1 FROM monsters WHERE id = ?", (str(data["monster_id"]),)
                )
                if not cursor.fetchone():
                    raise ValueError(f"monster_id {data['monster_id']} does not exist.")
            if "skill_id" in data and data["skill_id"]:
                cursor.execute(
                    "SELECT 1 FROM skills WHERE skill_id = ?", (data["skill_id"],)
                )
                if not cursor.fetchone():
                    raise ValueError(f"skill_id {data['skill_id']} does not exist.")
            if "class_id" in data and data["class_id"]:
                cursor.execute(
                    "SELECT 1 FROM classes WHERE class_id = ?", (data["class_id"],)
                )
                if not cursor.fetchone():
                    raise ValueError(f"class_id {data['class_id']} does not exist.")

            cursor.execute(
                """
                INSERT INTO scans (monster_id, skill_id, class_id, status)
                VALUES (:monster_id, :skill_id, :class_id, :status)
                """,
                {
                    "monster_id": (
                        str(data.get("monster_id")) if data.get("monster_id") else None
                    ),
                    "skill_id": data.get("skill_id"),
                    "class_id": data.get("class_id"),
                    "status": data.get("status", "pending"),
                },
            )
            scan_id = cursor.lastrowid
            conn.commit()
            return scan_id
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[ScanService] Create scan error: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def get_scan_by_id(self, scan_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[ScanService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass


    def get_distinct_scanned_monsters(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT s.monster_id, m.name
                FROM scans s
                JOIN monsters m ON s.monster_id = m.id
                WHERE s.monster_id IS NOT NULL
                ORDER BY m.name ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ScanService] get_distinct_scanned_monsters error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def get_scans_with_details(
        self, class_id: Optional[int] = None, monster_id: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        conn, is_local = get_connection()
        if not conn:
            return [], 0

        try:
            cursor = conn.cursor()

            # Base queries
            count_query = "SELECT COUNT(*) FROM scans s"
            data_query = '''
                SELECT
                    s.scan_id,
                    s.timestamp,
                    c.name as class_name,
                    sk.name as skill_name,
                    m.name as monster_name,
                    s.status
                FROM scans s
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN skills sk ON s.skill_id = sk.skill_id
                LEFT JOIN monsters m ON s.monster_id = m.id
            '''

            # Filters
            conditions = []
            params = []

            if class_id is not None and class_id != 0:
                conditions.append("s.class_id = ?")
                params.append(class_id)

            if monster_id is not None and monster_id != "":
                conditions.append("s.monster_id = ?")
                params.append(str(monster_id))

            where_clause = ""
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)

            # Get total count
            cursor.execute(count_query + where_clause, params)
            total_count = cursor.fetchone()[0]

            # Get paginated data
            offset = (page - 1) * page_size
            data_query += where_clause + " ORDER BY s.timestamp DESC LIMIT ? OFFSET ?"
            params.extend([page_size, offset])

            cursor.execute(data_query, params)
            records = [dict(row) for row in cursor.fetchall()]

            return records, total_count

        except Exception as e:
            print(f"[ScanService] get_scans_with_details error: {e}")
            return [], 0
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def get_scans(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ScanService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def update_scan_status(self, scan_id: int, status: str) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE scans SET status = ? WHERE scan_id = ?", (status, scan_id)
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[ScanService] Update status error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def delete_scan(self, scan_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[ScanService] Delete scan error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass
