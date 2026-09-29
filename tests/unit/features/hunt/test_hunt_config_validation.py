import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from lib.features.hunt.hunt_config import load_hunt_config

@pytest.fixture
def mock_hunt_config_path(monkeypatch, tmp_path):
    mock_path = tmp_path / "mock_hunt_config.json"
    monkeypatch.setattr("lib.features.hunt.hunt_config.HUNT_CONFIG_PATH", mock_path)
    return mock_path

def test_load_hunt_config_validates_rois(mock_hunt_config_path):
    # Simulate a corrupted schema where 'rois' is accidentally a list instead of a dict
    corrupted_data = {
        "schema_version": 3,
        "rois": [{"x": 10, "y": 20}] # Invalid schema (must be dict)
    }

    with open(mock_hunt_config_path, "w", encoding="utf-8") as f:
        json.dump(corrupted_data, f)

    # Loading config should trigger Pydantic validation error and fall back to default
    config = load_hunt_config()

    # Valid default config should restore 'rois' to empty dict
    assert "rois" in config
    assert isinstance(config["rois"], dict)

def test_load_hunt_config_restores_from_bak_on_validation_error(mock_hunt_config_path):
    # Corrupt main file
    corrupted_data = {"schema_version": 3, "rois": ["invalid"]}
    with open(mock_hunt_config_path, "w", encoding="utf-8") as f:
        json.dump(corrupted_data, f)

    # Valid bak file
    valid_bak_data = {"schema_version": 3, "rois": {"minimap": [0, 0, 100, 100]}}
    bak_path = mock_hunt_config_path.with_suffix(".json.bak")
    with open(bak_path, "w", encoding="utf-8") as f:
        json.dump(valid_bak_data, f)

    config = load_hunt_config()

    # Assert it recovered the data from the .bak file
    assert config["rois"]["minimap"] == [0, 0, 100, 100]
