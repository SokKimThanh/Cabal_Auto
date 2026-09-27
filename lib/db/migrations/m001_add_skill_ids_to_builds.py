import sqlite3

def up(conn: sqlite3.Connection):
    cursor = conn.cursor()
    # Add attack_skill_ids and buff_skill_ids columns
    try:
        cursor.execute("ALTER TABLE builds ADD COLUMN attack_skill_ids TEXT DEFAULT '[]'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

    try:
        cursor.execute("ALTER TABLE builds ADD COLUMN buff_skill_ids TEXT DEFAULT '[]'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise

    conn.commit()

def down(conn: sqlite3.Connection):
    # SQLite does not support dropping columns directly in versions older than 3.35.0.
    # So we'll have to create a new table, copy data over, and swap them.
    cursor = conn.cursor()

    # 1. Create a temporary table with the old schema
    cursor.execute("""
        CREATE TABLE builds_backup (
            build_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            author TEXT,
            description TEXT,
            upvote_count INTEGER DEFAULT 0,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
        )
    """)

    # 2. Copy data from builds to builds_backup
    cursor.execute("""
        INSERT INTO builds_backup (build_id, class_id, author, description, upvote_count)
        SELECT build_id, class_id, author, description, upvote_count FROM builds
    """)

    # 3. Drop the old builds table
    cursor.execute("DROP TABLE builds")

    # 4. Rename builds_backup to builds
    cursor.execute("ALTER TABLE builds_backup RENAME TO builds")

    conn.commit()
