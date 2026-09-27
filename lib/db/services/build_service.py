import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection


class BuildService:
    def __init__(self):
        pass

    def create_build(self, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Constraints checking
            class_id = data.get("class_id")
            if class_id is not None:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {class_id} does not exist.")

            cursor.execute(
                """
                INSERT INTO builds (class_id, author, description, upvote_count, attack_skill_ids, buff_skill_ids)
                VALUES (:class_id, :author, :description, :upvote_count, :attack_skill_ids, :buff_skill_ids)
                """,
                {
                    "class_id": class_id,
                    "author": data.get("author"),
                    "description": data.get("description"),
                    "upvote_count": data.get("upvote_count", 0),
                    "attack_skill_ids": data.get("attack_skill_ids", "[]"),
                    "buff_skill_ids": data.get("buff_skill_ids", "[]"),
                },
            )
            build_id = cursor.lastrowid
            conn.commit()
            return build_id
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[BuildService] Create build error: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def _parse_build(self, row: sqlite3.Row) -> Dict[str, Any]:
        if not row:
            return {}
        build_dict = dict(row)
        if "attack_skill_ids" not in build_dict:
            build_dict["attack_skill_ids"] = "[]"
        if "buff_skill_ids" not in build_dict:
            build_dict["buff_skill_ids"] = "[]"
        return build_dict

    def get_build_by_id(self, build_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM builds WHERE build_id = ?", (build_id,))
            row = cursor.fetchone()
            return self._parse_build(row) if row else None
        except Exception as e:
            print(f"[BuildService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def get_builds(self) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM builds ORDER BY upvote_count DESC")
            return [self._parse_build(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[BuildService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def update_build(self, build_id: int, data: Dict[str, Any]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Constraints checking
            class_id = data.get("class_id")
            if class_id is not None:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {class_id} does not exist.")

            cursor.execute(
                """
                UPDATE builds
                SET class_id = COALESCE(:class_id, class_id),
                    author = COALESCE(:author, author),
                    description = COALESCE(:description, description),
                    upvote_count = COALESCE(:upvote_count, upvote_count),
                    attack_skill_ids = COALESCE(:attack_skill_ids, attack_skill_ids),
                    buff_skill_ids = COALESCE(:buff_skill_ids, buff_skill_ids)
                WHERE build_id = :build_id
                """,
                {
                    "build_id": build_id,
                    "class_id": class_id,
                    "author": data.get("author"),
                    "description": data.get("description"),
                    "upvote_count": data.get("upvote_count"),
                    "attack_skill_ids": data.get("attack_skill_ids"),
                    "buff_skill_ids": data.get("buff_skill_ids"),
                },
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[BuildService] Update build error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass

    def delete_build(self, build_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM builds WHERE build_id = ?", (build_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"[BuildService] Delete build error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except:
                    pass
