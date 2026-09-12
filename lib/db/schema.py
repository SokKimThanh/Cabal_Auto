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
            value_text TEXT,
            duration_text TEXT,
            FOREIGN KEY (synergy_id) REFERENCES synergies(synergy_id) ON DELETE CASCADE
        )
    """)

    # Class Skill Assignments Table
    # Stores the verified relationships between classes and their valid skills.
    # Requires a populated manifest (DB5 step) to act as canonical source of truth.
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
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_csa_class_id ON class_skill_assignments(class_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_csa_skill_id ON class_skill_assignments(skill_id)"
    )

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

    # Bảng skill_presets - Lưu các preset skill presets (mặc định hoặc tùy chỉnh)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_presets (
            preset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_default BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(class_id, name, is_default),
            FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE
        )
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_presets_class ON skill_presets(class_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_presets_default ON skill_presets(is_default)"
    )

    # Bảng preset_skills - Lưu skill order trong một preset
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preset_skills (
            preset_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            lane_type TEXT NOT NULL,
            position INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(preset_id) REFERENCES skill_presets(preset_id) ON DELETE CASCADE,
            FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE(preset_id, lane_type, position)
        )
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_preset_skills_preset ON preset_skills(preset_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_preset_skills_skill ON preset_skills(skill_id)"
    )

    # Bảng user_preset_state - Theo dõi preset active hiện tại cho mỗi class
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preset_state (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL UNIQUE,
            active_preset_id INTEGER,
            preset_mode TEXT DEFAULT 'default',
            last_applied TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY(active_preset_id) REFERENCES skill_presets(preset_id) ON DELETE SET NULL
        )
    """)

    conn.commit()

def setup_icons_schema(conn: sqlite3.Connection):
    """Thiết lập schema cho hệ thống quản lý Icon"""
    cursor = conn.cursor()

    # Bảng icons - Lưu định nghĩa và thông tin của Icon
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS icons (
            icon_key TEXT PRIMARY KEY UNIQUE NOT NULL,
            name TEXT,
            filepath TEXT,
            fallback_emoji TEXT,
            tooltip_translation_key TEXT,
            category TEXT NOT NULL DEFAULT 'General',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bảng icon_usages - Lưu lịch sử/vị trí sử dụng của Icon
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS icon_usages (
            usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon_key TEXT NOT NULL,
            module_name TEXT,
            ui_component_type TEXT,
            ui_element_id TEXT,
            description TEXT,
            FOREIGN KEY(icon_key) REFERENCES icons(icon_key) ON DELETE CASCADE
        )
    """)

    # Seed data for icon_manager specifically to handle Self-Management Paradox
    cursor.execute("""
        INSERT OR IGNORE INTO icons (icon_key, name, fallback_emoji, category, description)
        VALUES ('icon_manager', 'Icon Manager', '📁', 'ui', 'Icon for the Icon Manager sidebar button')
    """)

    # We shouldn't use INSERT OR IGNORE for usages if there's no unique constraint,
    # so we first check if it exists.
    cursor.execute("""
        SELECT COUNT(*) FROM icon_usages
        WHERE icon_key = 'icon_manager' AND ui_element_id = 'btn_icon_manager'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id, description)
            VALUES ('icon_manager', 'App', 'sidebar_button', 'btn_icon_manager', 'Sidebar tracking for self-management paradox')
        """)

    conn.commit()
