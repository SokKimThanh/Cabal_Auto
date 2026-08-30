import json
import hashlib
from typing import Dict, Any, Tuple
from lib.db.connection import get_connection


class SeedSkillSpriteService:
    def __init__(self):
        self.source_file = "lib/data/skill-db-cabal-2.txt"
        self.source_id = "skill_sprite_catalogue"
        self.forbidden_inputs = [
            "image-count-skill-db-cabal.txt",
            "skills.json",
            "bm2-bm3-detail-skill-db-cabal.txt",
            "color-skill-character-db-cabal.txt",
            "monsters.json",
            "hunt_config.json"
        ]

    def _extract_sprites(self) -> Tuple[Dict[str, Any], str]:
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
        sprites, file_hash = self._extract_sprites()
        expected_count = len(sprites)

        conn, is_local = get_connection()
        if not conn:
            return {"status": "error", "message": "Could not connect to database"}

        inserted = 0
        skipped = 0
        errors = 0

        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            # The schema states that name is the skill code
            # We will use name as the column that stores the source sprite key (skill_code)
            # Add the skill_code column if it doesn't exist
            cursor.execute("PRAGMA table_info(skills)")
            columns = [col[1] for col in cursor.fetchall()]

            if "skill_code" not in columns:
                cursor.execute("ALTER TABLE skills ADD COLUMN skill_code TEXT")

            for skill_code, coords in sprites.items():
                # Idempotency check using skill_code
                cursor.execute("SELECT skill_id FROM skills WHERE skill_code = ?", (skill_code,))
                if cursor.fetchone():
                    skipped += 1
                    continue

                try:
                    cursor.execute(
                        """
                        INSERT INTO skills (name, skill_code, icon_x, icon_y, icon_w, icon_h)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            skill_code,  # Use skill_code as name because name is NOT NULL
                            skill_code,
                            coords.get("x", 0),
                            coords.get("y", 0),
                            coords.get("width", 0),
                            coords.get("height", 0)
                        )
                    )
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting {skill_code}: {e}")
                    errors += 1

            conn.commit()
            status = "PASSED" if errors == 0 else "PARTIAL_SUCCESS"

            # Integrity check
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT skill_code) FROM skills")
            total_rows, distinct_names = cursor.fetchone()

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
            try:
                conn.rollback()
            except Exception:
                pass
            return {"status": "ABORTED/REVERTED", "message": str(e)}
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass


if __name__ == "__main__":
    service = SeedSkillSpriteService()
    result = service.seed_skill_sprites()
    print(json.dumps(result, indent=2))
