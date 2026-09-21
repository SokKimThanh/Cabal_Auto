import sqlite3
import pytest
from lib.db.schema import setup_icons_schema
from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor
from lib.db.services.ui_element_service import UIElementService
from lib.db.services.icon_sync_manager import IconSyncManager
from lib.db.services.icon_service import IconService

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    setup_icons_schema(conn)
    yield conn
    conn.close()

def test_sync_registry_to_db(db_conn):
    # Register some elements in Registry
    registry = UIElementRegistry.instance()
    registry.clear()

    registry.register(UIElementDescriptor(
        element_id="btn_test",
        module="TestModule",
        screen="TestScreen",
        element_type="button",
        is_exclusive=False
    ))
    registry.register(UIElementDescriptor(
        element_id="tab_sidebar",
        module="App",
        screen="Main",
        element_type="sidebar_button",
        is_exclusive=True
    ))

    # Run sync
    icon_service = IconService(db_conn)
    manager = IconSyncManager(icon_service, "dummy.json")
    success = manager.sync_registry_to_db(db_conn)
    assert success is True

    # Verify elements are in DB
    ui_service = UIElementService(db_conn)
    el1 = ui_service.get_element_by_id("TestModule", "TestScreen", "btn_test")
    assert el1 is not None
    assert el1["is_exclusive"] == 0

    el2 = ui_service.get_element_by_id("App", "Main", "tab_sidebar")
    assert el2 is not None
    assert el2["is_exclusive"] == 1

    # Check idempotent update
    registry.register(UIElementDescriptor(
        element_id="btn_test",
        module="TestModule",
        screen="TestScreen",
        element_type="button",
        is_exclusive=True # Changed
    ))
    manager.sync_registry_to_db(db_conn)
    el1_updated = ui_service.get_element_by_id("TestModule", "TestScreen", "btn_test")
    assert el1_updated["is_exclusive"] == 1
