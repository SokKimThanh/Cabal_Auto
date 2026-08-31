import pytest
from lib.db.services.class_skill_evidence_service import ClassSkillEvidenceService
import json

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
