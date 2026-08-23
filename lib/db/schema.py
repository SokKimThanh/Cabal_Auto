import sqlite3

def setup_skills_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Bảng classes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon_path TEXT,
            str_base INTEGER DEFAULT 0,
            int_base INTEGER DEFAULT 0,
            dex_base INTEGER DEFAULT 0
        )
    """)

    # Bảng skills
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            alias TEXT,
            icon_x INTEGER DEFAULT 0,
            icon_y INTEGER DEFAULT 0,
            icon_w INTEGER DEFAULT 0,
            icon_h INTEGER DEFAULT 0,
            class_id INTEGER,
            type TEXT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
        )
    """)

    # Bảng synergies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synergies (
            synergy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            name TEXT NOT NULL,
            activation_sequence TEXT,
            recommendation TEXT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
        )
    """)

    # Bảng synergy_effects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synergy_effects (
            effect_id INTEGER PRIMARY KEY AUTOINCREMENT,
            synergy_id INTEGER,
            stat TEXT NOT NULL,
            value REAL,
            duration REAL,
            target TEXT,
            FOREIGN KEY (synergy_id) REFERENCES synergies(synergy_id) ON DELETE CASCADE
        )
    """)

    # Bảng scans
    # monster_id tham chiếu tới bảng monsters(id) hiện có (kiểu TEXT)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_id TEXT,
            skill_id INTEGER,
            class_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            FOREIGN KEY (monster_id) REFERENCES monsters(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE RESTRICT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
        )
    """)

    # Bảng builds
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS builds (
            build_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            author TEXT,
            description TEXT,
            upvote_count INTEGER DEFAULT 0,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
        )
    """)
