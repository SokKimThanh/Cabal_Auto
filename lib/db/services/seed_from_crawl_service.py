"""Seed class_skill_assignments from crawl data.

FIX BUG #7: db5_mapping_manifest.json chỉ có 38/411 dòng confidence="high"
→ mỗi class chỉ có 2-6 skill. File crawl có 248 mapping đầy đủ hơn.
"""
import json
import logging
import sqlite3
from pathlib import Path
from lib.db.connection import get_connection

logger = logging.getLogger(__name__)

CRAWL_FILE = Path(__file__).parent.parent.parent.parent / "lib" / "data" / "crawding" / "skills.json"


class SeedFromCrawlService:
    def __init__(self, crawl_file: Path = CRAWL_FILE):
        self.crawl_file = crawl_file

    def _load_crawl_data(self) -> list:
        if not self.crawl_file.exists():
            logger.error(f"Crawl file not found: {self.crawl_file}")
            return []
        try:
            with open(self.crawl_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load crawl file: {e}")
            return []

    def seed(self) -> dict:
        """Import crawl data into class_skill_assignments."""
        data = self._load_crawl_data()
        if not data:
            return {"status": "aborted", "message": "no crawl data"}

        conn, is_local = get_connection()
        if not conn:
            return {"status": "error", "message": "no DB connection"}

        try:
            cursor = conn.cursor()

            # Get map of class_id and skill_id that exist in DB
            cursor.execute("SELECT class_id FROM classes")
            valid_classes = {r[0] for r in cursor.fetchall()}
            cursor.execute("SELECT skill_id FROM skills")
            valid_skills = {r[0] for r in cursor.fetchall()}

            records = []
            rejected = []
            for row in data:
                # Adjust key names based on actual schema of crawding/skills.json
                class_id = row.get("class_id") or row.get("classId")
                skill_id = row.get("skill_id") or row.get("skillId")
                skill_type_id = row.get("skill_type_id", 1)
                source_ref = "crawl_import"
                is_recommended = 0

                if class_id is None or skill_id is None:
                    rejected.append((row, "missing class_id or skill_id"))
                    continue

                try:
                    class_id = int(class_id)
                    skill_id = int(skill_id)
                except (ValueError, TypeError):
                    rejected.append((row, f"invalid id types"))
                    continue

                if class_id not in valid_classes:
                    rejected.append((row, f"class_id {class_id} not in DB"))
                    continue
                if skill_id not in valid_skills:
                    rejected.append((row, f"skill_id {skill_id} not in DB"))
                    continue

                records.append(
                    (class_id, skill_id, skill_type_id, source_ref, is_recommended)
                )

            if records:
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO class_skill_assignments
                    (class_id, skill_id, skill_type_id, source_ref, is_recommended)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    records,
                )
                conn.commit()

            # Report per-class counts
            cursor.execute("""
                SELECT class_id, COUNT(*) FROM class_skill_assignments
                GROUP BY class_id ORDER BY class_id
            """)
            per_class = dict(cursor.fetchall())

            logger.info(f"[SeedCrawl] Imported: {len(records)}")
            logger.info(f"[SeedCrawl] Rejected: {len(rejected)}")
            logger.info(f"[SeedCrawl] Per class: {per_class}")

            return {
                "status": "passed",
                "imported": len(records),
                "rejected": len(rejected),
                "per_class": per_class,
            }

        except Exception as e:
            logger.error(f"Seed failed: {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception:
                pass
            return {"status": "error", "message": str(e)}
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(SeedFromCrawlService().seed())
