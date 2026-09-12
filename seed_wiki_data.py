import json
import sqlite3
import os

DB_PATH = "monsters.db"

def seed_classes():
    if not os.path.exists("lib/data/crawding/classes.json"):
        print("classes.json not found.")
        return

    with open("lib/data/crawding/classes.json", "r") as f:
        classes = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for c in classes:
        cursor.execute('''
            INSERT OR REPLACE INTO classes (class_id, name, description, icon_path, str_base, int_base, dex_base)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (c['class_id'], c['name'], c['description'], c['icon_path'], c['str_base'], c['int_base'], c['dex_base']))

    conn.commit()
    conn.close()
    print(f"Seeded {len(classes)} classes.")

def seed_skills():
    if not os.path.exists("lib/data/crawding/skills.json"):
        print("skills.json not found.")
        return

    with open("lib/data/crawding/skills.json", "r") as f:
        skills = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for s in skills:
        # Avoid duplicate skill names using normalized names
        normalized_name = s['name'].lower().replace(" ", "_")

        cursor.execute('''
            SELECT skill_id FROM skills
            WHERE LOWER(REPLACE(name, ' ', '_')) = ?
        ''', (normalized_name,))
        row = cursor.fetchone()

        if row:
            skill_id = row[0]
            # Since we just found a match, update the class_id and capitalization (name)
            # as well as the other fields, but avoid overwriting existing non-zero icon coords with 0.
            cursor.execute('''
                UPDATE skills
                SET name=?, alias=?,
                    icon_x=CASE WHEN ? = 0 THEN icon_x ELSE ? END,
                    icon_y=CASE WHEN ? = 0 THEN icon_y ELSE ? END,
                    icon_w=CASE WHEN ? = 0 THEN icon_w ELSE ? END,
                    icon_h=CASE WHEN ? = 0 THEN icon_h ELSE ? END,
                    type=?, class_id=?
                WHERE skill_id=?
            ''', (s['name'], s['alias'],
                  s['icon_x'], s['icon_x'],
                  s['icon_y'], s['icon_y'],
                  s['icon_w'], s['icon_w'],
                  s['icon_h'], s['icon_h'],
                  s['type'], s['class_id'], skill_id))
        else:
            cursor.execute('''
                INSERT INTO skills (name, alias, icon_x, icon_y, icon_w, icon_h, class_id, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (s['name'], s['alias'], s['icon_x'], s['icon_y'], s['icon_w'], s['icon_h'], s['class_id'], s['type']))
            skill_id = cursor.lastrowid

        # Optional: Setup class_skill_assignments if required by DB schema (using 'Unknown' category)
        cursor.execute('''
            INSERT OR IGNORE INTO class_skill_assignments (class_id, skill_id, category, source_ref, is_recommended)
            VALUES (?, ?, ?, ?, ?)
        ''', (s['class_id'], skill_id, s['type'], 'wiki', 0))

    conn.commit()
    conn.close()
    print(f"Seeded {len(skills)} skills.")

if __name__ == "__main__":
    seed_classes()
    seed_skills()
