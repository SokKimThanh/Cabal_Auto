import sqlite3
import pytest
from lib.db.schema import setup_icons_schema

@pytest.fixture
def db_conn():
    # Setup an in-memory database
    conn = sqlite3.connect(":memory:")
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Initialize the schema
    setup_icons_schema(conn)

    yield conn

    # Teardown
    conn.close()

def test_insert_icon_and_usage(db_conn):
    """Test case 1: Test insert thành công vào bảng icons và icon_usages"""
    cursor = db_conn.cursor()

    # Insert an icon
    cursor.execute("""
        INSERT INTO icons (icon_key, name, fallback_emoji, category, description)
        VALUES ('test_icon', 'Test Icon', '😎', 'Test Category', 'A test icon')
    """)
    db_conn.commit()

    # Verify icon insertion
    cursor.execute("SELECT * FROM icons WHERE icon_key = 'test_icon'")
    icon_row = cursor.fetchone()
    assert icon_row is not None
    assert icon_row[0] == 'test_icon'
    assert icon_row[5] == 'Test Category' # Category

    # Insert an icon usage
    cursor.execute("""
        INSERT INTO icon_usages (icon_key, module_name, ui_component_type, ui_element_id)
        VALUES ('test_icon', 'test_module', 'button', 'btn_test')
    """)
    db_conn.commit()

    # Verify icon usage insertion
    cursor.execute("SELECT * FROM icon_usages WHERE icon_key = 'test_icon'")
    usage_row = cursor.fetchone()
    assert usage_row is not None
    assert usage_row[1] == 'test_icon'
    assert usage_row[2] == 'test_module'

def test_unique_icon_key_constraint(db_conn):
    """Test case 2: Test vi phạm ràng buộc UNIQUE của icon_key trong bảng icons"""
    cursor = db_conn.cursor()

    # Insert first icon
    cursor.execute("""
        INSERT INTO icons (icon_key, name, fallback_emoji, category)
        VALUES ('duplicate_icon', 'First Icon', '😎', 'General')
    """)
    db_conn.commit()

    # Attempt to insert second icon with the same key
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        cursor.execute("""
            INSERT INTO icons (icon_key, name, fallback_emoji, category)
            VALUES ('duplicate_icon', 'Second Icon', '🤓', 'General')
        """)
        db_conn.commit()

    assert "UNIQUE constraint failed" in str(exc_info.value).lower() or "unique constraint failed" in str(exc_info.value).lower()
