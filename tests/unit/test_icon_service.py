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


def test_upsert_and_get_icon(icon_service):
    # Insert 1 icon
    icon_data = {
        'icon_key': 'test_icon',
        'name': 'Test Icon',
        'filepath': 'test.png',
        'fallback_emoji': '🔥',
        'tooltip_translation_key': 'tt_test',
        'category': 'test_cat',
        'description': 'A test icon'
    }

    assert icon_service.upsert_icon(icon_data) is True

    # Verify đọc lại bằng get_icon_by_key trùng khớp
    fetched_icon = icon_service.get_icon_by_key('test_icon')
    assert fetched_icon is not None
    assert fetched_icon['name'] == 'Test Icon'
    assert fetched_icon['filepath'] == 'test.png'
    assert fetched_icon['fallback_emoji'] == '🔥'


def test_update_icon(icon_service):
    # Insert initial
    icon_service.upsert_icon({
        'icon_key': 'update_test',
        'name': 'Old Name',
        'category': 'ui'
    })

    # Cập nhật 1 icon
    icon_service.upsert_icon({
        'icon_key': 'update_test',
        'name': 'New Name',
        'category': 'ui',
        'filepath': 'new.png'
    })

    # Verify giá trị mới
    updated = icon_service.get_icon_by_key('update_test')
    assert updated['name'] == 'New Name'
    assert updated['filepath'] == 'new.png'


def test_register_and_get_usages(icon_service):
    icon_service.upsert_icon({
        'icon_key': 'usage_test',
        'name': 'Usage Test'
    })

    # Register 1 usage
    assert icon_service.register_usage('usage_test', 'test_module', 'button', 'btn_test') is True

    # Lấy ra đúng record
    usages = icon_service.get_usages('usage_test')
    assert len(usages) == 1
    assert usages[0]['module_name'] == 'test_module'
    assert usages[0]['ui_element_id'] == 'btn_test'


def test_delete_icon(icon_service):
    icon_service.upsert_icon({
        'icon_key': 'del_test',
        'name': 'Delete Test'
    })

    # Xóa icon
    assert icon_service.delete_icon('del_test') is True

    # Cần đảm bảo get_icon_by_key trả về None
    assert icon_service.get_icon_by_key('del_test') is None


def test_clear_usages(icon_service):
    icon_service.upsert_icon({
        'icon_key': 'clear_test',
        'name': 'Clear Test'
    })

    icon_service.register_usage('clear_test', 'm1', 'btn', 'b1')
    icon_service.register_usage('clear_test', 'm2', 'lbl', 'l1')

    assert len(icon_service.get_usages('clear_test')) == 2

    assert icon_service.clear_usages('clear_test') is True
    assert len(icon_service.get_usages('clear_test')) == 0


def test_get_all_icons(icon_service):
    icon_service.upsert_icon({'icon_key': 'icon1', 'name': 'First', 'category': 'ui'})
    icon_service.upsert_icon({'icon_key': 'icon2', 'name': 'Second', 'category': 'skill'})

    all_icons = icon_service.get_all_icons()
    assert 'icon1' in [icon['icon_key'] for icon in all_icons] and 'icon2' in [icon['icon_key'] for icon in all_icons]

    filtered_icons = icon_service.get_all_icons(search_term='First')
    assert len(filtered_icons) == 1
    assert filtered_icons[0]['icon_key'] == 'icon1'

    cat_icons = icon_service.get_all_icons(category='skill')
    assert len(cat_icons) == 1
    assert cat_icons[0]['icon_key'] == 'icon2'
