import sqlite3

def normalize_name(name):
    return name.lower().replace(" ", "_")

def merge_skills():
    conn = sqlite3.connect("monsters.db")
    cursor = conn.cursor()

    # Enable foreign keys so CASCADE works properly if needed, although we are updating manually
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Find all duplicates based on normalized names
    cursor.execute("""
        SELECT LOWER(REPLACE(name, ' ', '_')) as norm_name
        FROM skills
        GROUP BY norm_name
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()

    merged_count = 0
    deleted_count = 0

    for (norm_name,) in duplicates:
        # Get all skills with this normalized name, ordered by skill_id ASC (oldest first)
        # Oldest usually has the old data (snake_case name, NULL class_id, but has icon coords)
        # Newest usually has the good data (Proper Case, class_id, etc)
        cursor.execute("""
            SELECT skill_id, name, alias, icon_x, icon_y, icon_w, icon_h, class_id, type, skill_code
            FROM skills
            WHERE LOWER(REPLACE(name, ' ', '_')) = ?
            ORDER BY skill_id ASC
        """, (norm_name,))
        rows = cursor.fetchall()

        if len(rows) < 2:
            continue

        old_row = rows[0]
        new_row = rows[-1]

        old_id = old_row[0]
        new_id = new_row[0]

        # We want to keep new_row, and update its missing icon/code from old_row
        icon_x = new_row[3] if new_row[3] != 0 else old_row[3]
        icon_y = new_row[4] if new_row[4] != 0 else old_row[4]
        icon_w = new_row[5] if new_row[5] != 0 else old_row[5]
        icon_h = new_row[6] if new_row[6] != 0 else old_row[6]
        skill_code = new_row[9] if new_row[9] else old_row[9]

        # 1. Update the new skill with old skill's values
        cursor.execute("""
            UPDATE skills
            SET icon_x = ?, icon_y = ?, icon_w = ?, icon_h = ?, skill_code = ?
            WHERE skill_id = ?
        """, (icon_x, icon_y, icon_w, icon_h, skill_code, new_id))

        # 2. Re-point foreign keys from old_id to new_id
        # For class_skill_assignments, be careful of UNIQUE constraint (class_id, skill_id)
        # We will try to update, if it fails because the new_id is already assigned, we just delete the old assignment.
        cursor.execute("SELECT class_id, category, source_ref, is_recommended FROM class_skill_assignments WHERE skill_id = ?", (old_id,))
        csa_rows = cursor.fetchall()
        for csa in csa_rows:
            class_id, cat, source, rec = csa
            try:
                cursor.execute("""
                    UPDATE class_skill_assignments
                    SET skill_id = ?
                    WHERE skill_id = ? AND class_id = ?
                """, (new_id, old_id, class_id))
            except sqlite3.IntegrityError:
                # Already exists for new_id, so we just delete the old one
                cursor.execute("DELETE FROM class_skill_assignments WHERE skill_id = ? AND class_id = ?", (old_id, class_id))

        # For preset_skills (preset_id, lane_type, position) UNIQUE constraint isn't affected directly by skill_id
        cursor.execute("""
            UPDATE preset_skills
            SET skill_id = ?
            WHERE skill_id = ?
        """, (new_id, old_id))

        # For scans
        cursor.execute("""
            UPDATE scans
            SET skill_id = ?
            WHERE skill_id = ?
        """, (new_id, old_id))

        # 3. Delete old skills
        # Delete all but the newest one
        for row in rows[:-1]:
            del_id = row[0]
            cursor.execute("DELETE FROM skills WHERE skill_id = ?", (del_id,))
            deleted_count += 1

        merged_count += 1

    conn.commit()
    conn.close()

    print(f"Successfully merged {merged_count} duplicate groups.")
    print(f"Deleted {deleted_count} duplicate records.")

if __name__ == "__main__":
    merge_skills()
