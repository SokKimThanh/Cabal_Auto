import pytest
import sqlite3
import datetime
from unittest.mock import patch, MagicMock

from lib.db.services.translation_service import TranslationService

pytestmark = pytest.mark.unit


@pytest.fixture
def memory_db():
    # Setup an in-memory database and connection for testing
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT NOT NULL,
            key TEXT NOT NULL,
            lang TEXT NOT NULL,
            text TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(namespace, key, lang)
        )
    """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_get_connection(memory_db):
    with patch('lib.db.services.translation_service.get_connection', return_value=(memory_db, False)):
        yield memory_db


def test_get_all_empty(mock_get_connection):
    service = TranslationService()
    results = service.get_all()
    assert results == []

def test_upsert_new_and_existing(mock_get_connection):
    service = TranslationService()

    # Insert new
    success = service.upsert("ns1", "key1", "en", "Hello")
    assert success is True

    results = service.get_all()
    assert len(results) == 1
    assert results[0]["namespace"] == "ns1"
    assert results[0]["key"] == "key1"
    assert results[0]["lang"] == "en"
    assert results[0]["text"] == "Hello"

    # Update existing
    success = service.upsert("ns1", "key1", "en", "Hello World")
    assert success is True

    results = service.get_all()
    assert len(results) == 1
    assert results[0]["text"] == "Hello World"


def test_bulk_upsert_transaction(mock_get_connection):
    service = TranslationService()

    translations = {
        "en": {
            "key1": "Hello",
            "key2": "World"
        },
        "vi": {
            "key1": "Xin chao",
            "key2": "The gioi"
        }
    }

    success = service.bulk_upsert("ns2", translations)
    assert success is True

    results = service.get_all("ns2")
    assert len(results) == 4

    # Check that update works properly
    translations_update = {
        "en": {
            "key1": "Hello!"
        }
    }
    success = service.bulk_upsert("ns2", translations_update)
    assert success is True

    results = service.get_all("ns2")
    # Length should still be 4, as we updated an existing row
    assert len(results) == 4

    # Find the updated row
    updated_row = next(r for r in results if r["key"] == "key1" and r["lang"] == "en")
    assert updated_row["text"] == "Hello!"
