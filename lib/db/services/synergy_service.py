import sqlite3
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class SynergyService:
    def __init__(self):
        pass

    def create_synergy(self, data: Dict[str, Any]) -> Optional[int]:
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
                INSERT INTO synergies (class_id, name, activation_sequence, recommendation)
                VALUES (:class_id, :name, :activation_sequence, :recommendation)
                """,
                {
                    "class_id": class_id,
                    "name": data.get("name"),
                    "activation_sequence": data.get("activation_sequence"),
                    "recommendation": data.get("recommendation"),
                }
            )
            synergy_id = cursor.lastrowid
            conn.commit()
            return synergy_id
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Create synergy error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_synergy_by_id(self, synergy_id: int) -> Optional[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM synergies WHERE synergy_id = ?", (synergy_id,))
            row = cursor.fetchone()
            if row:
                synergy = dict(row)
                cursor.execute("SELECT * FROM synergy_effects WHERE synergy_id = ?", (synergy_id,))
                synergy['effects'] = [dict(e) for e in cursor.fetchall()]
                return synergy
            return None
        except Exception as e:
            print(f"[SynergyService] Read error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def get_synergies_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM synergies WHERE class_id = ?", (class_id,))
            synergies = [dict(row) for row in cursor.fetchall()]

            for syn in synergies:
                cursor.execute("SELECT * FROM synergy_effects WHERE synergy_id = ?", (syn['synergy_id'],))
                syn['effects'] = [dict(e) for e in cursor.fetchall()]

            return synergies
        except Exception as e:
            print(f"[SynergyService] Read all error: {e}")
            return []
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def update_synergy(self, synergy_id: int, data: Dict[str, Any]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            class_id = data.get("class_id")
            if class_id is not None:
                cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
                if not cursor.fetchone():
                    raise ValueError(f"class_id {class_id} does not exist.")

            cursor.execute(
                """
                UPDATE synergies
                SET class_id = COALESCE(:class_id, class_id),
                    name = COALESCE(:name, name),
                    activation_sequence = COALESCE(:activation_sequence, activation_sequence),
                    recommendation = COALESCE(:recommendation, recommendation)
                WHERE synergy_id = :synergy_id
                """,
                {
                    "synergy_id": synergy_id,
                    "class_id": class_id,
                    "name": data.get("name"),
                    "activation_sequence": data.get("activation_sequence"),
                    "recommendation": data.get("recommendation"),
                }
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Update error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def delete_synergy(self, synergy_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM synergies WHERE synergy_id = ?", (synergy_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except sqlite3.IntegrityError as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Integrity error on delete: {e}")
            return False
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Delete error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    # --- Effects ---
    def create_synergy_effect(self, synergy_id: int, data: Dict[str, Any]) -> Optional[int]:
        conn, is_local = get_connection()
        if not conn:
            return None
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM synergies WHERE synergy_id = ?", (synergy_id,))
            if not cursor.fetchone():
                raise ValueError(f"synergy_id {synergy_id} does not exist.")

            cursor.execute(
                """
                INSERT INTO synergy_effects (synergy_id, stat, value, duration, target)
                VALUES (:synergy_id, :stat, :value, :duration, :target)
                """,
                {
                    "synergy_id": synergy_id,
                    "stat": data.get("stat"),
                    "value": data.get("value"),
                    "duration": data.get("duration"),
                    "target": data.get("target"),
                }
            )
            effect_id = cursor.lastrowid
            conn.commit()
            return effect_id
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Create effect error: {e}")
            return None
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def update_synergy_effect(self, effect_id: int, data: Dict[str, Any]) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE synergy_effects
                SET stat = COALESCE(:stat, stat),
                    value = COALESCE(:value, value),
                    duration = COALESCE(:duration, duration),
                    target = COALESCE(:target, target)
                WHERE effect_id = :effect_id
                """,
                {
                    "effect_id": effect_id,
                    "stat": data.get("stat"),
                    "value": data.get("value"),
                    "duration": data.get("duration"),
                    "target": data.get("target"),
                }
            )
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Update effect error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def delete_synergy_effect(self, effect_id: int) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM synergy_effects WHERE effect_id = ?", (effect_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[SynergyService] Delete effect error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
