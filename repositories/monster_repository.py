"""
Monster Repository module for DB operations and transaction management.
"""

from __future__ import annotations
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

try:
    from database import get_db
except ImportError:
    get_db = None

class MonsterRepository:
    """Handles SQLite database interactions for monsters with transaction rollbacks."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_connection(self) -> tuple[Optional[sqlite3.Connection], bool]:
        """
        Returns (connection, is_local_connection).
        If is_local_connection is True, caller must close the connection in a finally block.
        """
        if get_db is not None:
            try:
                db_inst = get_db()
                if db_inst:
                    if hasattr(db_inst, "conn") and db_inst.conn is not None:
                        return db_inst.conn, False
                    if isinstance(db_inst, sqlite3.Connection):
                        return db_inst, False
            except Exception:
                pass
        if self.db_path:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                return conn, True
            except Exception:
                pass
        return None, False

    def load_all_monsters(self) -> List[Dict[str, Any]]:
        """Fetch all monster records safely from DB."""
        conn, is_local = self._get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monsters ORDER BY name ASC")
            rows = cursor.fetchall()
            monsters = []
            for r in rows:
                if isinstance(r, sqlite3.Row) or hasattr(r, "keys"):
                    m = dict(r)
                else:
                    m = {"id": r[0], "name": r[1]}
                monsters.append(m)
            return monsters
        except Exception as e:
            print(f"[MonsterRepository] Error loading monsters: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def save_monster(self, monster: Dict[str, Any]) -> bool:
        """Save/update a single monster record with transaction rollback safety."""
        conn, is_local = self._get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            s_boss = monster.get("serverBossType")
            if s_boss is not None:
                s_boss = str(s_boss)

            cursor.execute(
                """
                INSERT INTO monsters (
                    id, name, level, exp, hp, defense, attackRate, defenseRate,
                    hpRecharge, accuracy, penetration, damageReduction, evasion,
                    resistCritRate, primaryAttackMin, primaryAttackMax,
                    secondaryAttackMin, secondaryAttackMax, ignoreAccuracy,
                    ignoreDamageReduction, ignorePenetration, absoluteDamage,
                    resistSkillAmp, resistCritDamage, resistSuppress, resistSilence,
                    resistDiffDamage, hpProportionDamage, serverBossType, dungeonId
                ) VALUES (
                    :id, :name, :level, :exp, :hp, :defense, :attackRate, :defenseRate,
                    :hpRecharge, :accuracy, :penetration, :damageReduction, :evasion,
                    :resistCritRate, :primaryAttackMin, :primaryAttackMax,
                    :secondaryAttackMin, :secondaryAttackMax, :ignoreAccuracy,
                    :ignoreDamageReduction, :ignorePenetration, :absoluteDamage,
                    :resistSkillAmp, :resistCritDamage, :resistSuppress, :resistSilence,
                    :resistDiffDamage, :hpProportionDamage, :serverBossType, :dungeonId
                ) ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    level=excluded.level,
                    exp=excluded.exp,
                    hp=excluded.hp,
                    defense=excluded.defense,
                    attackRate=excluded.attackRate,
                    defenseRate=excluded.defenseRate,
                    hpRecharge=excluded.hpRecharge,
                    accuracy=excluded.accuracy,
                    penetration=excluded.penetration,
                    damageReduction=excluded.damageReduction,
                    evasion=excluded.evasion,
                    resistCritRate=excluded.resistCritRate,
                    primaryAttackMin=excluded.primaryAttackMin,
                    primaryAttackMax=excluded.primaryAttackMax,
                    secondaryAttackMin=excluded.secondaryAttackMin,
                    secondaryAttackMax=excluded.secondaryAttackMax,
                    ignoreAccuracy=excluded.ignoreAccuracy,
                    ignoreDamageReduction=excluded.ignoreDamageReduction,
                    ignorePenetration=excluded.ignorePenetration,
                    absoluteDamage=excluded.absoluteDamage,
                    resistSkillAmp=excluded.resistSkillAmp,
                    resistCritDamage=excluded.resistCritDamage,
                    resistSuppress=excluded.resistSuppress,
                    resistSilence=excluded.resistSilence,
                    resistDiffDamage=excluded.resistDiffDamage,
                    hpProportionDamage=excluded.hpProportionDamage,
                    serverBossType=excluded.serverBossType,
                    dungeonId=excluded.dungeonId
                """,
                {
                    "id": str(monster.get("id", "")),
                    "name": str(monster.get("name", "")),
                    "level": int(monster.get("level", 1)),
                    "exp": int(monster.get("exp", 0)),
                    "hp": int(monster.get("hp", 0)),
                    "defense": int(monster.get("defense", 0)),
                    "attackRate": int(monster.get("attackRate", 0)),
                    "defenseRate": int(monster.get("defenseRate", 0)),
                    "hpRecharge": int(monster.get("hpRecharge", 0)),
                    "accuracy": int(monster.get("accuracy", 0)),
                    "penetration": int(monster.get("penetration", 0)),
                    "damageReduction": int(monster.get("damageReduction", 0)),
                    "evasion": int(monster.get("evasion", 0)),
                    "resistCritRate": int(monster.get("resistCritRate", 0)),
                    "primaryAttackMin": int(monster.get("primaryAttackMin", 0)),
                    "primaryAttackMax": int(monster.get("primaryAttackMax", 0)),
                    "secondaryAttackMin": int(monster.get("secondaryAttackMin", 0)),
                    "secondaryAttackMax": int(monster.get("secondaryAttackMax", 0)),
                    "ignoreAccuracy": int(monster.get("ignoreAccuracy", 0)),
                    "ignoreDamageReduction": int(monster.get("ignoreDamageReduction", 0)),
                    "ignorePenetration": int(monster.get("ignorePenetration", 0)),
                    "absoluteDamage": int(monster.get("absoluteDamage", 0)),
                    "resistSkillAmp": int(monster.get("resistSkillAmp", 0)),
                    "resistCritDamage": int(monster.get("resistCritDamage", 0)),
                    "resistSuppress": int(monster.get("resistSuppress", 0)),
                    "resistSilence": int(monster.get("resistSilence", 0)),
                    "resistDiffDamage": int(monster.get("resistDiffDamage", 0)),
                    "hpProportionDamage": int(monster.get("hpProportionDamage", 0)),
                    "serverBossType": s_boss,
                    "dungeonId": str(monster.get("dungeonId", "101")),
                },
            )
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[MonsterRepository] Transaction failed, rolled back save: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def delete_monster(self, monster_id: str) -> bool:
        """Delete monster by ID with transaction rollback safety."""
        conn, is_local = self._get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monsters WHERE id = ?", (str(monster_id),))
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[MonsterRepository] Transaction failed, rolled back delete: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass
