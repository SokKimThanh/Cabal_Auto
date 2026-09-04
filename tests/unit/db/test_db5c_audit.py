import pytest
import os
import json
import hashlib
from unittest.mock import patch
from lib.db.services.db5c_audit_hybrid_and_consolidate import run_audit

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_files(tmp_path):
    source_file = tmp_path / "bm2-bm3-detail-skill-db-cabal.txt"
    sprite_file = tmp_path / "skill-db-cabal-2.txt"

    source_content = """
    slug: "force-blader"
    passiveSkillConfig: {
        recommendedSkillSlugs: ["sharp-eyes", "eyes-of-mind"]
    }
    comboSection: {
        skillSlugs: ["split-attack-1", "split-attack-2"]
    }
    """
    sprite_content = '{"sharp_eyes":{"x":480,"y":720,"width":38,"height":38},"eyes_of_mind":{"x":0,"y":0,"width":0,"height":0},"split_attack":{"x":1,"y":1,"width":1,"height":1}}'

    source_file.write_text(source_content)
    sprite_file.write_text(sprite_content)

    return str(source_file), str(sprite_file)

@patch('lib.db.services.db5c_audit_hybrid_and_consolidate.SOURCE_FILE', new_callable=str)
@patch('lib.db.services.db5c_audit_hybrid_and_consolidate.SPRITE_CATALOGUE_FILE', new_callable=str)
def test_idempotency_and_malformed(mock_sprite, mock_source, mock_files, tmp_path, monkeypatch):
    source_path, sprite_path = mock_files

    # We patch the globals in the module. Since we can't easily patch constants directly if they are used as default args
    # we patch them at the module level.
    import lib.db.services.db5c_audit_hybrid_and_consolidate as db5c

    # Save original
    orig_source = db5c.SOURCE_FILE
    orig_sprite = db5c.SPRITE_CATALOGUE_FILE

    db5c.SOURCE_FILE = source_path
    db5c.SPRITE_CATALOGUE_FILE = sprite_path

    monkeypatch.chdir(tmp_path)

    # Run 1
    db5c.run_audit()
    assert os.path.exists('db5_consolidated_manifest_v1.0.0.json')

    with open('db5_consolidated_manifest_v1.0.0.json', 'r') as f:
        run1_data = json.load(f)

    # Run 2
    db5c.run_audit()
    with open('db5_consolidated_manifest_v1.0.0.json', 'r') as f:
        run2_data = json.load(f)

    # Check idempotency: metadata timestamp will differ, but checksums and data should be identical
    assert run1_data['metadata']['manifest_checksum'] == run2_data['metadata']['manifest_checksum']
    assert run1_data['data'] == run2_data['data']
    assert run1_data['rejected'] == run2_data['rejected']

    # Test missing/malformed file (does not crash)
    db5c.SOURCE_FILE = "non_existent_file.txt"
    # Should not throw exception
    db5c.run_audit()

    with open('db5_consolidated_manifest_v1.0.0.json', 'r') as f:
        malformed_data = json.load(f)
        assert malformed_data['data'] == {} # Empty data

    # Restore
    db5c.SOURCE_FILE = orig_source
    db5c.SPRITE_CATALOGUE_FILE = orig_sprite
