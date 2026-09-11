import json
import sqlite3
import pytest
from lib.db.schema import setup_icons_schema
from lib.db.services.icon_service import IconService
from lib.db.services.icon_sync_manager import IconSyncManager
from lib.events.event_bus import EventBus, IconUpdatedEvent, IconManagerSyncEvent


@pytest.fixture
def icon_service():
    conn = sqlite3.connect(":memory:")
    setup_icons_schema(conn)
    service = IconService(conn)
    yield service
    conn.close()


@pytest.fixture
def temp_json_path(tmp_path):
    return tmp_path / "test_icons.json"


@pytest.fixture
def sync_manager(icon_service, temp_json_path):
    manager = IconSyncManager(icon_service, str(temp_json_path))
    yield manager


@pytest.fixture(autouse=True)
def cleanup_events():
    """Clear event bus listeners before and after each test."""
    EventBus.clear()
    yield
    EventBus.clear()


def test_import_from_json(sync_manager, temp_json_path, icon_service):
    # Prepare mock json
    mock_data = {"btn_add": ["add", "➕"], "btn_delete": ["delete", "🗑️"]}
    with open(temp_json_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    # Do import
    assert sync_manager.import_from_json() is True

    # Verify db
    icons = icon_service.get_all_icons()
    assert len(icons) == 2

    add_icon = icon_service.get_icon_by_key("btn_add")
    assert add_icon["filepath"] == "add"
    assert add_icon["fallback_emoji"] == "➕"
    assert add_icon["category"] == "General"


def test_export_to_json(sync_manager, temp_json_path, icon_service):
    # Prepare db
    icon_service.insert_ignore_icon(
        {
            "icon_key": "btn_edit",
            "name": "btn_edit",
            "filepath": "edit",
            "fallback_emoji": "✏️",
            "category": "ui",
        }
    )

    # Do export
    assert sync_manager.export_to_json() is True

    # Verify json
    assert temp_json_path.exists()
    with open(temp_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "btn_edit" in data
    assert data["btn_edit"] == ["edit", "✏️"]


def test_upsert_triggers_events(icon_service):
    updated_keys = []
    sync_called = False

    def handle_updated(event: IconUpdatedEvent):
        updated_keys.append(event.icon_key)

    def handle_sync(event: IconManagerSyncEvent):
        nonlocal sync_called
        sync_called = True

    EventBus.bind(IconUpdatedEvent, handle_updated)
    EventBus.bind(IconManagerSyncEvent, handle_sync)

    # Perform upsert
    icon_service.upsert_icon(
        {
            "icon_key": "test_trigger",
            "name": "Test Trigger",
            "filepath": "trigger.png",
            "fallback_emoji": "✨",
        }
    )

    assert "test_trigger" in updated_keys
    assert sync_called is True


def test_delete_triggers_sync_event(icon_service):
    # Insert first
    icon_service.insert_ignore_icon({"icon_key": "test_del_trigger"})

    sync_called = False

    def handle_sync(event: IconManagerSyncEvent):
        nonlocal sync_called
        sync_called = True

    EventBus.bind(IconManagerSyncEvent, handle_sync)

    # Perform delete
    icon_service.delete_icon("test_del_trigger")

    assert sync_called is True


def test_sync_manager_handles_sync_event(sync_manager, temp_json_path, icon_service):
    # sync_manager has already bound _handle_sync_event in its __init__

    icon_service.insert_ignore_icon(
        {"icon_key": "sync_evt_test", "filepath": "test", "fallback_emoji": "🧪"}
    )

    # Manually trigger to simulate upsert/delete side effect
    EventBus.trigger(IconManagerSyncEvent())

    # Assert export happened
    assert temp_json_path.exists()
    with open(temp_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "sync_evt_test" in data
    assert data["sync_evt_test"] == ["test", "🧪"]
