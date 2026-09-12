import sqlite3
import pytest
from lib.db.services.icon_service import IconService
from lib.db.schema import setup_icons_schema

@pytest.fixture
def icon_service():
    conn = sqlite3.connect(':memory:')
    setup_icons_schema(conn)
    service = IconService(conn)
    yield service
    conn.close()

def test_delete_icon_in_use(icon_service):
    icon_service.upsert_icon({
        'icon_key': 'del_test_in_use',
        'name': 'Delete Test In Use'
    })

    # Register usage
    icon_service.register_usage('del_test_in_use', 'module1', 'button', 'btn1')

    # Try to delete - should raise ValueError
    with pytest.raises(ValueError, match="icon_in_use_error"):
        icon_service.delete_icon('del_test_in_use')
