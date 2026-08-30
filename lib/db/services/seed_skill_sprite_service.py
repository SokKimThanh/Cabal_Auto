import json
import hashlib
import logging
from typing import Dict, Any, Tuple
from lib.db.connection import get_connection

# Set up logging for the service
logger = logging.getLogger("SeedSkillSpriteService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SeedSkillSpriteService:
    def __init__(self, source_file: str = "lib/data/skill-db-cabal-2.txt"):
        self.source_file = source_file
        self.source_id = "skill_sprite_catalogue"
        self.authorized_file = "lib/data/skill-db-cabal-2.txt"
        self.forbidden_inputs = [
            "image-count-skill-db-cabal.txt",
            "skills.json",
            "bm2-bm3-detail-skill-db-cabal.txt",
            "color-skill-character-db-cabal.txt",
            "monsters.json",
            "hunt_config.json"
        ]

    def _validate_source(self):
        """Validates that the source file is authorized and not forbidden."""
        if self.source_file != self.authorized_file:
            raise ValueError(f"Unauthorized source file: {self.source_file}. Must be {self.authorized_file}")

        for forbidden in self.forbidden_inputs:
            if forbidden in self.source_file:
                raise ValueError(f"Forbidden source file used: {self.source_file}")

    def _extract_sprites(self) -> Tuple[Dict[str, Any], str]:
        self._validate_source()

        with open(self.source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        start_str = "JSON.parse('"
        start_idx = content.find(start_str)
        if start_idx == -1:
            raise ValueError("Could not find JSON.parse boundary in source file.")

        start_idx += len(start_str)

        # Count curly braces to find the end of the JSON object accurately
        brace_count = 0
        in_string = False
        escape_char = False

        end_idx = -1

        for i in range(start_idx, len(content)):
            char = content[i]

            if in_string:
                if char == '\\' and not escape_char:
                    escape_char = True
                else:
                    if char == '"' and not escape_char:
                        in_string = False
                    escape_char = False
            else:
                if char == '"':
                    in_string = True
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

        if end_idx == -1:
            raise ValueError("Could not find end of JSON object in source file.")

        json_str = content[start_idx:end_idx]

        try:
            data = json.loads(json_str)
            sprites = data.get('sprites', {})
            return sprites, file_hash
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from source: {e}")

    def seed_skill_sprites(self) -> Dict[str, Any]:
        try:
            sprites, file_hash = self._extract_sprites()
        except Exception as e:
            logger.error(f"Failed to extract sprites: {e}")
            return {"status": "ABORTED/REVERTED", "message": str(e)}

        expected_count = len(sprites)

        conn, is_local = get_connection()
        if not conn:
            logger.error("Could not connect to database")
            return {"status": "error", "message": "Could not connect to database"}

        inserted = 0
        skipped = 0
        errors = 0

        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # Add required columns if they don't exist
            cursor.execute("PRAGMA table_info(skills)")
            columns = [col[1] for col in cursor.fetchall()]

            if "skill_code" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN skill_code TEXT")
            if "icon_x" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN icon_x INTEGER DEFAULT 0")
            if "icon_y" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN icon_y INTEGER DEFAULT 0")
            if "icon_w" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN icon_w INTEGER DEFAULT 0")
            if "icon_h" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN icon_h INTEGER DEFAULT 0")

            # Fetch existing skill_codes for idempotency check
            cursor.execute("SELECT skill_code FROM skills WHERE skill_code IS NOT NULL")
            existing_codes = {row[0] for row in cursor.fetchall()}

            records_to_insert = []
            for skill_code, coords in sprites.items():
                if skill_code in existing_codes:
                    skipped += 1
                    continue

                records_to_insert.append((
                    skill_code,  # name
                    skill_code,  # skill_code
                    coords.get("x", 0),
                    coords.get("y", 0),
                    coords.get("width", 0),
                    coords.get("height", 0)
                ))

            if records_to_insert:
                try:
                    cursor.executemany(
                        """
                        INSERT INTO skills (name, skill_code, icon_x, icon_y, icon_w, icon_h)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        records_to_insert
                    )
                    inserted += len(records_to_insert)
                except Exception as batch_err:
                    logger.warning(f"Batch insert error: {batch_err}. Falling back to individual inserts.", exc_info=True)
                    # Fallback to individual inserts to find out exactly which record failed
                    for record in records_to_insert:
                        try:
                            cursor.execute(
                                """
                                INSERT INTO skills (name, skill_code, icon_x, icon_y, icon_w, icon_h)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                record
                            )
                            inserted += 1
                        except Exception as single_err:
                            skill_code = record[0]
                            logger.error(f"Failed to insert record {skill_code}: {single_err}", exc_info=True)
                            errors += 1

            try:
                conn.commit()
            except Exception as e:
                logger.error(f"Failed to commit transaction: {e}", exc_info=True)
                conn.rollback()
                return {"status": "ABORTED/REVERTED", "message": f"Commit failed: {e}"}

            status = "PASSED" if errors == 0 else "PARTIAL_SUCCESS"

            # Integrity check
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT skill_code) FROM skills")
            total_rows, distinct_names = cursor.fetchone()

            if expected_count != (inserted + skipped + errors):
                logger.warning(f"Integrity warning: Expected {expected_count} records but processed {inserted + skipped + errors}")

            return {
                "status": status,
                "source_id": self.source_id,
                "source_file": self.source_file,
                "file_hash": file_hash,
                "expected_count": expected_count,
                "inserted": inserted,
                "skipped": skipped,
                "errors": errors,
                "total_rows": total_rows,
                "distinct_names": distinct_names
            }

        except Exception as e:
            logger.error(f"Unexpected error during seed: {e}", exc_info=True)
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
    service = SeedSkillSpriteService()
    result = service.seed_skill_sprites()
    print(json.dumps(result, indent=2))
