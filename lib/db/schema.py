import sqlite3


def setup_skills_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Bảng skill_types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_types (
            skill_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

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
            skill_type_id INTEGER,
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
            skill_type_id INTEGER NOT NULL,
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS icon_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO icon_categories (id, name, description) VALUES (1, 'General', 'Mặc định chung')")
    cursor.execute("INSERT OR IGNORE INTO icon_categories (id, name, description) VALUES (2, 'UI', 'Giao diện hệ thống')")
    cursor.execute("INSERT OR IGNORE INTO icon_categories (id, name, description) VALUES (3, 'Skills', 'Kỹ năng nhân vật')")
    cursor.execute("INSERT OR IGNORE INTO icon_categories (id, name, description) VALUES (4, 'Monsters', 'Quái vật')")
    cursor.execute("INSERT OR IGNORE INTO icon_categories (id, name, description) VALUES (5, 'Items', 'Vật phẩm')")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS icons (
            icon_key TEXT PRIMARY KEY UNIQUE NOT NULL,
            name TEXT,
            filepath TEXT,
            fallback_emoji TEXT,
            tooltip_translation_key TEXT,
            category_id INTEGER NOT NULL DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES icon_categories(id)
        )
    """)

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

    cursor.execute("""
        INSERT OR IGNORE INTO icons (icon_key, name, fallback_emoji, tooltip_translation_key, category_id, description)
        VALUES ('icon_manager', 'Icon Manager', '📁', 'btn_icon_manager', 2, 'Icon for the Icon Manager sidebar button')
    """)
    cursor.execute("""
        UPDATE icons SET tooltip_translation_key = 'btn_icon_manager' WHERE icon_key = 'icon_manager'
    """)

    sidebar_icons = [
        ('hunt', 'Hunt', '🎯', 'tab_hunt', 2, 'Icon for the Hunt sidebar button'),
        ('setup', 'Setup', '⚙️', 'tab_setup', 2, 'Icon for the Setup sidebar button'),
        ('build_manager', 'Build Manager', '🛠️', 'btn_build_manager', 2, 'Icon for the Build Manager sidebar button'),
        ('skill_manager', 'Skill Manager', '⚔️', 'btn_skill_manager', 2, 'Icon for the Skill Manager sidebar button'),
        ('monster_manager', 'Monster Manager', '🐉', 'btn_monster_manager', 2, 'Icon for the Monster Manager sidebar button'),
        ('class_manager', 'Class Manager', '🛡️', 'btn_class_manager', 2, 'Icon for the Class Manager sidebar button'),
        ('scan_history', 'Scan History', '🕒', 'btn_scan_history', 2, 'Icon for the Scan History sidebar button'),
        ('logs', 'Activity Logs', '📋', 'sidebar_activity_logs', 2, 'Icon for the Activity Logs sidebar button'),
        ('stats', 'Stats', '📊', 'tab_stats', 2, 'Icon for the Stats sidebar button'),
        ('language_manager', 'Language Manager', '🌐', 'btn_language_manager', 2, 'Icon for the Language Manager sidebar button'),
        ('help', 'Support', '❓', 'sidebar_support', 2, 'Icon for the Help sidebar button')
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO icons (icon_key, name, fallback_emoji, tooltip_translation_key, category_id, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sidebar_icons)

    cursor.execute("""
        SELECT COUNT(*) FROM icon_usages
        WHERE icon_key = 'icon_manager' AND ui_element_id = 'btn_icon_manager'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id, description)
            VALUES ('icon_manager', 'App', 'sidebar_button', 'btn_icon_manager', 'Sidebar tracking for self-management paradox')
        """)

    sidebar_usages = [
        ('hunt', 'App', 'sidebar_button', 'tab_hunt', 'Sidebar tracking for Hunt'),
        ('setup', 'App', 'sidebar_button', 'tab_setup', 'Sidebar tracking for Setup'),
        ('build_manager', 'App', 'sidebar_button', 'btn_build_manager', 'Sidebar tracking for Build Manager'),
        ('skill_manager', 'App', 'sidebar_button', 'btn_skill_manager', 'Sidebar tracking for Skill Manager'),
        ('monster_manager', 'App', 'sidebar_button', 'btn_monster_manager', 'Sidebar tracking for Monster Manager'),
        ('class_manager', 'App', 'sidebar_button', 'btn_class_manager', 'Sidebar tracking for Class Manager'),
        ('scan_history', 'App', 'sidebar_button', 'btn_scan_history', 'Sidebar tracking for Scan History'),
        ('logs', 'App', 'sidebar_button', 'sidebar_activity_logs', 'Sidebar tracking for Activity Logs'),
        ('stats', 'App', 'sidebar_button', 'tab_stats', 'Sidebar tracking for Stats'),
        ('language_manager', 'App', 'sidebar_button', 'btn_language_manager', 'Sidebar tracking for Language Manager'),
        ('help', 'App', 'sidebar_button', 'sidebar_support', 'Sidebar tracking for Support')
    ]

    for usage in sidebar_usages:
        icon_key, mod_name, comp_type, el_id, desc = usage
        cursor.execute("""
            SELECT COUNT(*) FROM icon_usages
            WHERE icon_key = ? AND ui_element_id = ?
        """, (icon_key, el_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id, description)
                VALUES (?, ?, ?, ?, ?)
            """, usage)

    conn.commit()