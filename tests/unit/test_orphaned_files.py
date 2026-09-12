import sqlite3
import pytest
from lib.db.services.icon_service import IconService
from lib.db.schema import setup_icons_schema
from unittest.mock import patch

@pytest.fixture
def icon_service():
    conn = sqlite3.connect(':memory:')
    setup_icons_schema(conn)
    # Clear default icons if any to start fresh
    conn.execute("DELETE FROM icons")
    service = IconService(conn)
    yield service
    conn.close()

@patch('lib.db.services.icon_service.delete_icon_file')
def test_delete_orphaned_file(mock_delete_icon_file, icon_service):
    # Setup: insert 1 icon with file 'test.png'
    icon_service.upsert_icon({
        'icon_key': 'icon_1',
        'filepath': 'test.png'
    })

    # Delete the icon
    icon_service.delete_icon('icon_1')

    # Verify delete_icon_file was called with 'test.png'
    mock_delete_icon_file.assert_called_once_with('test.png')

@patch('lib.db.services.icon_service.delete_icon_file')
def test_not_delete_shared_file(mock_delete_icon_file, icon_service):
    # Setup: insert 2 icons with the same file 'test.png'
    icon_service.upsert_icon({
        'icon_key': 'icon_1',
        'filepath': 'test.png'
    })
    icon_service.upsert_icon({
        'icon_key': 'icon_2',
        'filepath': 'test.png'
    })

    # Delete one of the icons
    icon_service.delete_icon('icon_1')

    # Verify delete_icon_file was NOT called because icon_2 still uses it
    mock_delete_icon_file.assert_not_called()

@patch('lib.db.services.icon_service.delete_icon_file')
def test_upsert_orphaned_file(mock_delete_icon_file, icon_service):
    # Setup: insert 1 icon with file 'old.png'
    icon_service.upsert_icon({
        'icon_key': 'icon_1',
        'filepath': 'old.png'
    })

    # Upsert the same icon to use 'new.png'
    icon_service.upsert_icon({
        'icon_key': 'icon_1',
        'filepath': 'new.png'
    })

    # Verify delete_icon_file was called for 'old.png'
    mock_delete_icon_file.assert_called_once_with('old.png')
