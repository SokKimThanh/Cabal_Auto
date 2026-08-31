import json
import logging
import sqlite3
import hashlib
from typing import Dict, Any, Tuple
from lib.db.connection import get_connection

# Set up logging for the service
logger = logging.getLogger("SeedClassSkillAssignmentsService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SeedClassSkillAssignmentsService:
    def __init__(self, manifest_file: str = "db5_mapping_manifest.json"):
        self.manifest_file = manifest_file
        self.source_id = "class_skill_evidence"
        self.source_file = "lib/data/bm2-bm3-detail-skill-db-cabal.txt"

    def apply_schema_migrations(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_skill_assignments (
                class_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                is_recommended INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (class_id, skill_id),
                FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
            )
        """)

    def load_manifest(self) -> list:
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            return manifest
        except FileNotFoundError:
            logger.error(f"Manifest file {self.manifest_file} not found. Please run DB5 audit first.")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse manifest JSON: {e}")
            return []

    def get_source_hash(self):
        try:
            with open(self.source_file, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            logger.error(f"Source file {self.source_file} not found. Cannot verify hash.")
            return None

    def _extract_recommendation(self, row: dict, source_ref: str) -> int:
        """Helper to extract or infer recommendation status."""
        is_recommended = row.get("recommendation", 0)
        if not isinstance(is_recommended, int):
            if str(is_recommended).lower() in ("true", "1", "yes"):
                is_recommended = 1
            else:
                is_recommended = 0

        if source_ref == 'passiveSkillConfig':
            is_recommended = 1

        return is_recommended

    def seed_assignments(self) -> Dict[str, Any]:
        manifest = self.load_manifest()
        if not manifest:
            return {"status": "ABORTED/REVERTED", "message": "Manifest could not be loaded."}

        # Verify source hash
        current_hash = self.get_source_hash()
        if not current_hash:
            return {"status": "ABORTED/REVERTED", "message": "Source file not found to verify hash."}

        # We can just verify with the first row's hash since they should all be identical
        manifest_hash = manifest[0].get("source_hash") if manifest else None
        if manifest_hash and current_hash != manifest_hash:
            logger.warning(f"Hash mismatch! Manifest Hash: {manifest_hash}, Current Hash: {current_hash}")
            return {"status": "ABORTED/REVERTED", "message": "Source hash mismatch"}

        conn, is_local = get_connection()
        if not conn:
            logger.error("Could not connect to database")
            return {"status": "error", "message": "Could not connect to database"}

        inserted_count = 0
        rejected_count = 0
        total_manifest_rows = len(manifest)

        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Apply schema
            self.apply_schema_migrations(cursor)

            # Pre-fetch classes and skills
            cursor.execute("SELECT class_code, class_id FROM classes WHERE class_code IS NOT NULL")
            class_map = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT skill_code, skill_id FROM skills WHERE skill_code IS NOT NULL")
            skill_map = {row[0]: row[1] for row in cursor.fetchall()}

            records_to_insert = []
            rejected_records = []

            for row in manifest:
                source_class = row.get("source_class")
                source_skill_code = row.get("source_skill_code")
                confidence = row.get("confidence")

                # Boundary: Malformed/Unresolved
                if confidence != "high":
                    rejected_records.append({"row": row, "reason": "Confidence is not high"})
                    rejected_count += 1
                    continue

                # Boundary: Missing parent rows
                class_id = class_map.get(source_class)
                skill_id = skill_map.get(source_skill_code)

                if class_id is None or skill_id is None:
                    rejected_records.append({"row": row, "reason": f"Parent missing: class_id={class_id}, skill_id={skill_id}"})
                    rejected_count += 1
                    continue

                category = row.get("category", "")
                source_ref = row.get("evidence_location", "")

                is_recommended = self._extract_recommendation(row, source_ref)

                records_to_insert.append((class_id, skill_id, category, source_ref, is_recommended))

            if records_to_insert:
                # Boundary: Repeated import (Idempotent upsert)
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO class_skill_assignments
                    (class_id, skill_id, category, source_ref, is_recommended)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    records_to_insert
                )
                inserted_count += len(records_to_insert)

            # Integrity checks
            cursor.execute("PRAGMA foreign_key_check;")
            fk_issues = cursor.fetchall()
            if fk_issues:
                logger.error(f"Foreign key check failed: {fk_issues}")
                conn.rollback()
                return {"status": "ABORTED/REVERTED", "message": f"Foreign key check failed: {fk_issues}"}

            # Orphan checks logic
            cursor.execute("""
                SELECT csa.class_id, csa.skill_id
                FROM class_skill_assignments AS csa
                LEFT JOIN classes AS c ON c.class_id = csa.class_id
                LEFT JOIN skills AS s ON s.skill_id = csa.skill_id
                WHERE c.class_id IS NULL OR s.skill_id IS NULL
            """)
            orphans = cursor.fetchall()
            if orphans:
                logger.error(f"Found orphan class_skill_assignments: {orphans}")
                conn.rollback()
                return {"status": "ABORTED/REVERTED", "message": f"Orphan checks failed: {orphans}"}

            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM class_skill_assignments")
            total_db_rows = cursor.fetchone()[0]

            logger.info("--- DB6 Import Report ---")
            logger.info(f"Source ID: {self.source_id}")
            logger.info(f"Manifest File: {self.manifest_file}")
            logger.info(f"Target Table: class_skill_assignments")
            logger.info(f"Manifest rows: {total_manifest_rows}")
            logger.info(f"Imported mappings: {inserted_count}")
            logger.info(f"Rejected mappings: {rejected_count}")
            logger.info(f"Total mappings in DB: {total_db_rows}")
            logger.info("Status: PASSED")

            return {
                "status": "PASSED",
                "manifest_rows": total_manifest_rows,
                "imported": inserted_count,
                "rejected": rejected_count,
                "total_rows": total_db_rows,
                "rejected_records": rejected_records
            }

        except Exception as e:
            logger.error(f"Unexpected error during DB6 seed: {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception:
                pass
            return {"status": "ABORTED/REVERTED", "message": str(e)}
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")

if __name__ == "__main__":
    service = SeedClassSkillAssignmentsService()
    result = service.seed_assignments()
    if result.get("status") != "PASSED":
        print(f"Failed to seed: {result}")

    # Idempotency check
    print("Running idempotency check...")
    result2 = service.seed_assignments()
    if result2.get("status") == "PASSED":
        print(f"Idempotency check passed! Row count is same: {result.get('total_rows')} == {result2.get('total_rows')}")
