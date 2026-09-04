import pytest
from lib.db.services.class_skill_evidence_service import ClassSkillEvidenceService
import json

pytestmark = pytest.mark.unit


def test_map_category():
    service = ClassSkillEvidenceService()
    assert service.map_category("Battle Mode 2") == "bm2"
    assert service.map_category("Combo") == "attack"
    assert service.map_category("Blader Buffs") == "buff"
    assert service.map_category("Wizard Debuffs") == "debuff"

def test_extract_categories():
    service = ClassSkillEvidenceService()
    content = """
    slug: "blader"
    id: "battle-mode-2", title: "Battle Mode 2"
    skillSlugs: ["grappler", "grappler-attack-1"]
    """
    results = service.extract_categories(content)
    assert len(results) == 1
    assert results[0]['class_code'] == 'blader'
    assert results[0]['categories'][0]['category'] == 'Battle Mode 2'
    assert 'grappler' in results[0]['categories'][0]['slugs']

def test_build_manifest(monkeypatch):
    service = ClassSkillEvidenceService()

    # Mock dependencies
    def mock_read_file(filepath):
        if filepath == service.source_file:
            return 'slug: "blader" id: "battle-mode-2", title: "Battle Mode 2" skillSlugs: ["exact-match", "missing-skill"]'
        return ''

    monkeypatch.setattr(service, "read_file_content", mock_read_file)
    monkeypatch.setattr(service, "get_source_hash", lambda: "mock_hash")
    monkeypatch.setattr(service, "get_sprite_keys", lambda: {"exact-match"})

    manifest = service.build_manifest()

    assert len(manifest) == 2

    exact_match_row = next(r for r in manifest if r['source_skill_code'] == 'exact-match')
    assert exact_match_row['confidence'] == 'high'
    assert exact_match_row['unresolved_aliases'] == []

    missing_skill_row = next(r for r in manifest if r['source_skill_code'] == 'missing-skill')
    assert missing_skill_row['confidence'] == 'ambiguous'
    assert missing_skill_row['unresolved_aliases'] == ['missing-skill']
