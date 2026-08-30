import sqlite3
from lib.db.connection import get_connection

def migrate():
    conn, is_local = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(skills)")
        columns = [col[1] for col in cursor.fetchall()]
        if "skill_code" not in columns:
            cursor.execute("ALTER TABLE skills ADD COLUMN skill_code TEXT")
            conn.commit()
            print("Migration applied: added skill_code to skills table")
    finally:
        if is_local and conn:
            conn.close()

if __name__ == "__main__":
    migrate()
