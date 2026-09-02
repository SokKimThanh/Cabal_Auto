import re
import os
import hashlib
import sqlite3
import logging
from typing import Tuple, List, Dict
from lib.db.connection import get_connection

class SeedBM3SynergiesService:
    def __init__(self, filepath: str = None):
        if filepath is None:
            self.filepath = os.getenv('CABAL_BM3_SYNERGY_DB_FILE', 'lib/data/bm2-bm3-skill-db-cabal.txt')
        else:
            self.filepath = filepath
        self.source_id = "bm3_synergy_catalogue"

    def parse_synergies(self) -> Tuple[List[Dict], int, int, str]:
        """
        Parses the synergy data from the authorized source file.
        Returns: (parsed_data, source_synergy_count, source_effect_count, file_hash)
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        except FileNotFoundError:
            logging.error(f"[SeedBM3SynergiesService] Could not find data file at: {self.filepath}")
            return [], 0, 0, ""

        parsed_classes = []
        synergy_count = 0
        effect_count = 0

        # Split content by class blocks
        class_blocks = re.split(r'\b"?([a-zA-Z_-]+)"?:\s*\{\s*id:\s*"bm3-synergies"', content)

        for i in range(1, len(class_blocks), 2):
            class_slug = class_blocks[i]
            block_content = class_blocks[i+1]

            # Find the rows array
            idx = block_content.find("rows: [")
            if idx == -1:
                continue

            start_idx = idx + 6
            bracket_count = 0
            end_idx = -1
            for j in range(start_idx, len(block_content)):
                if block_content[j] == '[':
                    bracket_count += 1
                elif block_content[j] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = j
                        break

            if end_idx == -1:
                continue

            rows_content = block_content[start_idx:end_idx+1]

            # Extract synergies
            synergies = re.finditer(r'synergyName:\s*"([^"]+)",\s*activationSequence:\s*"([^"]+)",\s*recommendation:\s*"([^"]+)",\s*effects:\s*\[(.*?)\]', rows_content, re.DOTALL)

            class_synergies = []
            for syn in synergies:
                syn_name, act_seq, rec, effects_str = syn.groups()

                effects_list = []
                effects = re.finditer(r'stat:\s*"([^"]+)",\s*value:\s*"([^"]+)",\s*duration:\s*"([^"]+)",\s*target:\s*"([^"]+)"', effects_str)
                for eff in effects:
                    stat, val, dur, tgt = eff.groups()

                    # Try to parse numeric value and duration
                    num_val = None
                    num_dur = None
                    try:
                        v_match = re.search(r'[-+]?\d*\.\d+|[-+]?\d+', val)
                        if v_match:
                            num_val = float(v_match.group())
                    except: pass

                    try:
                        d_match = re.search(r'[-+]?\d*\.\d+|[-+]?\d+', dur)
                        if d_match:
                            num_dur = float(d_match.group())
                    except: pass

                    effects_list.append({
                        "stat": stat,
                        "value_text": val,
                        "value": num_val,
                        "duration_text": dur,
                        "duration": num_dur,
                        "target": tgt
                    })
                    effect_count += 1

                class_synergies.append({
                    "name": syn_name,
                    "activation_sequence": act_seq,
                    "recommendation": rec,
                    "effects": effects_list
                })
                synergy_count += 1

            if class_synergies:
                parsed_classes.append({
                    "class_slug": class_slug,
                    "synergies": class_synergies
                })

        return parsed_classes, synergy_count, effect_count, file_hash

    def seed(self) -> Tuple[bool, int, int]:
        """
        Seeds the BM3 synergies into the database.
        Returns: (success, seeded_synergies, seeded_effects)
        """
        parsed_classes, source_synergy_count, source_effect_count, file_hash = self.parse_synergies()

        if not parsed_classes:
            logging.warning("[SeedBM3SynergiesService] No synergies parsed.")
            return False, 0, 0

        print(f"[SeedBM3SynergiesService] Parsed {source_synergy_count} synergies, {source_effect_count} effects for {len(parsed_classes)} classes.")
        print(f"Source ID: {self.source_id}")
        print(f"Parser Boundary: Exact regex matching on 'rows: [...]' within 'id: \"bm3-synergies\"' blocks.")
        print(f"Forbidden Inputs: User config files are ignored, only the exact parsed file is used.")

        conn, is_local = get_connection()
        if not conn:
            logging.error("[SeedBM3SynergiesService] Could not get database connection.")
            return False, 0, 0

        seeded_synergies = 0
        seeded_effects = 0
        unmatched_classes = []

        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")

            # Pre-fetch all class mappings to avoid N+1 queries
            cursor.execute("SELECT class_code, class_id FROM classes")
            class_mappings = {row[0]: row[1] for row in cursor.fetchall()}

            for cls_data in parsed_classes:
                class_slug = cls_data["class_slug"]
                class_code = class_slug.replace('_', '-')

                # Resolve class_id using in-memory dictionary
                class_id = class_mappings.get(class_code)
                if class_id is None:
                    unmatched_classes.append(class_slug)
                    logging.warning(f"[SeedBM3SynergiesService] Unmatched class slug: {class_slug}")
                    continue

                for syn in cls_data["synergies"]:
                    # Check idempotency: synergy identity is (class_id, name, activation_sequence)
                    cursor.execute(
                        "SELECT synergy_id FROM synergies WHERE class_id = ? AND name = ? AND activation_sequence = ?",
                        (class_id, syn["name"], syn["activation_sequence"])
                    )
                    existing_syn = cursor.fetchone()

                    if existing_syn:
                        synergy_id = existing_syn[0]
                        # For idempotency, we delete existing effects and re-insert them.
                        cursor.execute("DELETE FROM synergy_effects WHERE synergy_id = ?", (synergy_id,))
                    else:
                        cursor.execute(
                            """
                            INSERT INTO synergies (class_id, name, activation_sequence, recommendation)
                            VALUES (?, ?, ?, ?)
                            """,
                            (class_id, syn["name"], syn["activation_sequence"], syn["recommendation"])
                        )
                        synergy_id = cursor.lastrowid
                        seeded_synergies += 1

                    # Insert effects
                    for eff in syn["effects"]:
                        cursor.execute(
                            """
                            INSERT INTO synergy_effects (synergy_id, stat, value, value_text, duration, duration_text, target)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (synergy_id, eff["stat"], eff["value"], eff["value_text"], eff["duration"], eff["duration_text"], eff["target"])
                        )
                        seeded_effects += 1

            conn.commit()

            if unmatched_classes:
                print(f"[SeedBM3SynergiesService] Unmatched class slugs: {unmatched_classes}")

            # Post-seed validation
            cursor.execute("PRAGMA foreign_key_check;")
            fk_issues = cursor.fetchall()
            if fk_issues:
                logging.error(f"[SeedBM3SynergiesService] Foreign key violations: {fk_issues}")
                # Report how many were processed before failing the check
                logging.error(f"Rolling back after processing {seeded_synergies} synergies and {seeded_effects} effects.")
                conn.rollback()
                return False, 0, 0

            cursor.execute("""
                SELECT se.effect_id
                FROM synergy_effects AS se
                LEFT JOIN synergies AS syn ON syn.synergy_id = se.synergy_id
                WHERE syn.synergy_id IS NULL;
            """)
            orphans = cursor.fetchall()
            if orphans:
                logging.error(f"[SeedBM3SynergiesService] Orphaned synergy effects found: {len(orphans)}")
                logging.error(f"Rolling back after processing {seeded_synergies} synergies and {seeded_effects} effects.")
                conn.rollback()
                return False, 0, 0

            return True, seeded_synergies, seeded_effects

        except Exception as e:
            try: conn.rollback()
            except: pass
            logging.error(f"[SeedBM3SynergiesService] Seeding error: {e}")
            return False, 0, 0
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
