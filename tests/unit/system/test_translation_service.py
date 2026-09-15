import pytest
import sqlite3
from unittest.mock import patch

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
    with patch(
        "lib.db.services.translation_service.get_connection",
        return_value=(memory_db, False),
    ):
        yield memory_db


def test_get_all_empty(mock_get_connection):
    service = TranslationService()
    results = service.get_all()
    assert results == []


def test_get_total_count(mock_get_connection):
    service = TranslationService()
    assert service.get_total_count() == 0

    service.upsert("ns1", "key1", "en", "Hello")
    assert service.get_total_count() == 1

    service.upsert("ns1", "key2", "en", "World")
    assert service.get_total_count() == 2

def test_get_namespaces(mock_get_connection):
    service = TranslationService()
    assert service.get_namespaces() == []

    service.upsert("ns1", "key1", "en", "Hello")
    service.upsert("ns2", "key1", "en", "World")
    service.upsert("ns1", "key2", "en", "Testing")

    assert set(service.get_namespaces()) == {"ns1", "ns2"}

def test_get_all_grouped(mock_get_connection):
    service = TranslationService()

    service.upsert("ns1", "key1", "en", "Hello")
    service.upsert("ns1", "key1", "vi", "Xin chao")
    service.upsert("ns1", "key2", "en", "World")
    service.upsert("ns2", "key3", "vi", "The gioi")

    results = service.get_all_grouped()

    # 3 unique keys
    assert len(results) == 3

    # Check ns1.key1
    key1_row = next(r for r in results if r["key"] == "key1")
    assert key1_row["namespace"] == "ns1"
    assert key1_row["en"] == "Hello"
    assert key1_row["vi"] == "Xin chao"

    # Check ns1.key2 (missing vi)
    key2_row = next(r for r in results if r["key"] == "key2")
    assert key2_row["en"] == "World"
    assert key2_row["vi"] is None

    # Check ns2.key3 (missing en)
    key3_row = next(r for r in results if r["key"] == "key3")
    assert key3_row["en"] is None
    assert key3_row["vi"] == "The gioi"

    # Test filtering by namespace
    ns1_results = service.get_all_grouped("ns1")
    assert len(ns1_results) == 2

def test_update_translation(mock_get_connection):
    service = TranslationService()

    # Insert new using update_translation
    success = service.update_translation("ns1", "key1", "en", "Initial")
    assert success is True

    # Update existing
    success = service.update_translation("ns1", "key1", "en", "Updated")
    assert success is True

    results = service.get_all()
    assert len(results) == 1
    assert results[0]["text"] == "Updated"

def test_delete_key(mock_get_connection):
    service = TranslationService()

    service.upsert("ns1", "key1", "en", "Hello")
    service.upsert("ns1", "key1", "vi", "Xin chao")
    service.upsert("ns1", "key2", "en", "World")

    success = service.delete_key("ns1", "key1")
    assert success is True

    results = service.get_all()
    # Should only have key2 left
    assert len(results) == 1
    assert results[0]["key"] == "key2"


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

    # Update existing (Should DO NOTHING due to change in prompt 01)
    success = service.upsert("ns1", "key1", "en", "Hello World")
    assert success is True

    results = service.get_all()
    assert len(results) == 1
    assert results[0]["text"] == "Hello"  # Verify it wasn't updated


def test_bulk_upsert_transaction(mock_get_connection):
    service = TranslationService()

    translations = {
        "en": {"key1": "Hello", "key2": "World"},
        "vi": {"key1": "Xin chao", "key2": "The gioi"},
    }

    success = service.bulk_upsert("ns2", translations)
    assert success is True

    results = service.get_all("ns2")
    assert len(results) == 4

    # Check that update works properly (Should DO NOTHING due to change in prompt 01)
    translations_update = {"en": {"key1": "Hello!"}}
    success = service.bulk_upsert("ns2", translations_update)
    assert success is True

    results = service.get_all("ns2")
    # Length should still be 4, as we did not insert a new row
    assert len(results) == 4

    # Find the row, should still have the old text
    updated_row = next(r for r in results if r["key"] == "key1" and r["lang"] == "en")
    assert updated_row["text"] == "Hello"  # Verify it wasn't updated
