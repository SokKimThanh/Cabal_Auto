import pytest
import json
from lib.db.services.db5b_audit_magic_ranged import run_audit

pytestmark = pytest.mark.unit


def test_audit_empty_source(tmp_path, capsys):
    test_file = tmp_path / "empty.txt"
    test_file.write_text("")

    # We need to temporarily patch SOURCE_FILE in the module
    import lib.db.services.db5b_audit_magic_ranged as audit_module
    old_file = audit_module.SOURCE_FILE
    audit_module.SOURCE_FILE = str(test_file)

    try:
        run_audit()
        captured = capsys.readouterr()

        # Manifest output should be generated but for all keys it should be 0 or empty
        assert "Total:" not in captured.out or "\"total\": 0" in captured.out

        with open("lib/data/db5b_magic_ranged_manifest.json", "r") as f:
            manifest = json.load(f)
            assert manifest == {}
    finally:
        audit_module.SOURCE_FILE = old_file

def test_audit_malformed_input(tmp_path, capsys):
    test_file = tmp_path / "malformed.txt"
    test_file.write_text("just some random text without any proper structure")

    import lib.db.services.db5b_audit_magic_ranged as audit_module
    old_file = audit_module.SOURCE_FILE
    audit_module.SOURCE_FILE = str(test_file)

    try:
        run_audit()

        with open("lib/data/db5b_magic_ranged_manifest.json", "r") as f:
            manifest = json.load(f)
            assert manifest == {}
    finally:
        audit_module.SOURCE_FILE = old_file

def test_audit_idempotency_and_logic(tmp_path):
    test_file = tmp_path / "test_data.txt"
    content = """
            slug: "wizard"
            className: "Wizard"
            recommendedSkillSlugs: ["force-control", "ruling-force"]
            featuredSkillSections: [{
                id: "battle-mode-2",
                title: "Battle Mode 2",
                skillSlugs: ["twin-gunner", "twin-gunner-attack-1", "fatal-shot"],
            }, {
                id: "buffs",
                title: "Buffs",
                skillSlugs: ["sharpness", "vital-force-439"],
            }],
            comboSection: {
                id: "combos",
                scenarios: [{
                    skillSlugs: ["force-kick"]
                }]
            }
"""
    test_file.write_text(content)

    import lib.db.services.db5b_audit_magic_ranged as audit_module
    old_file = audit_module.SOURCE_FILE
    audit_module.SOURCE_FILE = str(test_file)

    try:
        run_audit()

        with open("lib/data/db5b_magic_ranged_manifest.json", "r") as f:
            manifest = json.load(f)

        assert "wizard" in manifest
        w_skills = manifest["wizard"]

        # Check passives
        assert w_skills["force-control"]["category"] == "passive"
        assert w_skills["force-control"]["confidence"] == "HIGH"

        # Check BM2
        assert w_skills["twin-gunner"]["category"] == "bm2"
        assert w_skills["twin-gunner-attack"]["category"] == "bm2"
        assert w_skills["twin-gunner-attack"]["confidence"] == "AMBIGUOUS" # Due to suffix strip

        # Check Buffs and Suffix Strip
        assert w_skills["vital-force"]["category"] == "buff"
        assert w_skills["vital-force"]["confidence"] == "AMBIGUOUS"

        # Check Combos
        assert w_skills["force-kick"]["category"] == "attack"
        assert w_skills["force-kick"]["confidence"] == "HIGH"

        # Idempotency check: Running it twice should yield the exact same file
        with open("lib/data/db5b_magic_ranged_manifest.json", "r") as f:
            first_run_content = f.read()

        run_audit()

        with open("lib/data/db5b_magic_ranged_manifest.json", "r") as f:
            second_run_content = f.read()

        assert first_run_content == second_run_content

    finally:
        audit_module.SOURCE_FILE = old_file
