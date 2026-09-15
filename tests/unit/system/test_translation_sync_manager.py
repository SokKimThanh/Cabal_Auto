import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from lib.db.services.translation_sync_manager import TranslationSyncManager

pytestmark = pytest.mark.unit

@patch("lib.db.services.translation_sync_manager.TranslationService")
@patch("lib.db.services.translation_sync_manager.GLOBAL_TRANSLATIONS")
def test_seed_initial_data(mock_global_translations, mock_service_class):
    # Setup mock data
    mock_global_translations.items.return_value = [("en", {"key1": "val1"})]
    mock_service_instance = MagicMock()
    mock_service_class.return_value = mock_service_instance

    # Run seed
    success = TranslationSyncManager.seed_initial_data()

    # Assertions
    assert success is True
    mock_service_instance.bulk_upsert.assert_called_with("global", {"en": {"key1": "val1"}})

@patch("lib.db.services.translation_sync_manager.TranslationService")
def test_export_to_json(mock_service_class, tmp_path):
    # Setup mock data
    mock_service_instance = MagicMock()
    mock_service_instance.get_all.return_value = [
        {"namespace": "global", "key": "key1", "lang": "en", "text": "Hello", "updated_at": "2024"},
        {"namespace": "global", "key": "key1", "lang": "vi", "text": "Xin chao", "updated_at": "2024"},
        {"namespace": "custom", "key": "key2", "lang": "en", "text": "Test", "updated_at": "2024"}
    ]
    mock_service_class.return_value = mock_service_instance

    with patch("lib.db.services.translation_sync_manager.Path") as MockPath:
        # We need Path("assets/i18n") to return tmp_path instead so it writes to temp dir
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__.side_effect = lambda x: tmp_path / x
        MockPath.return_value = mock_path_instance

        success = TranslationSyncManager.export_to_json()

        assert success is True

        # Verify JSON files are created properly
        en_file = tmp_path / "en.json"
        vi_file = tmp_path / "vi.json"

        assert en_file.exists()
        assert vi_file.exists()

        with open(en_file, "r") as f:
            en_data = json.load(f)
            assert en_data["key1"] == "Hello"
            assert en_data["custom.key2"] == "Test"

        with open(vi_file, "r") as f:
            vi_data = json.load(f)
            assert vi_data["key1"] == "Xin chao"
            assert "custom.key2" not in vi_data
