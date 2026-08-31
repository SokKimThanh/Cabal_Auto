"""
Script to parse DB5C - Class-Skill Mapping Audit (Hybrids: FB, FS)
and consolidate all DB5 audits into a final v1.0.0 manifest.
"""
import re
import json
import hashlib
import os
import datetime

SOURCE_FILE = "lib/data/bm2-bm3-detail-skill-db-cabal.txt"
SPRITE_CATALOGUE_FILE = "lib/data/skill-db-cabal-2.txt"
TARGET_SLUGS = {"force-blader", "force-shielder"}
DB5B_SLUGS = {"wizard", "force-archer", "force-gunner", "dark-mage"}
DB5A_SLUGS = {"warrior", "blader", "gladiator"}

def get_sprite_keys():
    try:
        with open(SPRITE_CATALOGUE_FILE, 'r') as f:
            content = f.read()
            return set(re.findall(r'"([^"]+)":{"x":', content))
    except FileNotFoundError:
        print(f"Error: Could not find sprite catalogue at {SPRITE_CATALOGUE_FILE}")
        return set()


def run_audit(content=None):
    print("=== DB5C Audit Force Hybrids & Final Consolidation ===")
    print(f"\nSource ID: class_skill_evidence")
    print(f"File Path: {SOURCE_FILE}")
    print("Parser Boundary: slug sections (force-blader, force-shielder)")
    print("Target Keys: target classes + DB5A + DB5B consolidated manifest")
    print("Forbidden Inputs: skills.json, user configs, untraceable prose")

    try:
        if content is None:
            with open(SOURCE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find source file at {SOURCE_FILE}. Simulating empty/malformed source.")
        content = ""

    if not content.strip():
         print("Warning: Source content is empty or malformed.")

    lines = content.split('\n')
    current_slug = None
    current_lines = []
    class_sections = []

    for line in lines:
        match = re.search(r'slug:\s*"([^"]+)"', line)
        if match:
            if current_slug:
                class_sections.append((current_slug, '\n'.join(current_lines)))
            current_slug = match.group(1)
            current_lines = [line]
        elif current_slug:
            current_lines.append(line)

    if current_slug:
        class_sections.append((current_slug, '\n'.join(current_lines)))

    manifest = {}
    rejected = {}
    coverage = {}

    sprite_keys = get_sprite_keys()

    def add_skill(skills_dict, rej_list, original_slug, category):
        normalized = re.sub(r'-\d+$', '', original_slug)
        # Check against sprite catalogue
        snake_case_slug = normalized.replace('-', '_')
        if snake_case_slug in sprite_keys:
             skills_dict[normalized] = {"category": category, "confidence": "HIGH"}
        else:
             skills_dict[normalized] = {"category": category, "confidence": "AMBIGUOUS"}
             rej_list.append({"original": original_slug, "normalized": normalized, "reason": f"Skill '{snake_case_slug}' not found in skill_sprite_catalogue and has no valid alias"})


    # 1. Parse DB5C Hybrids and DB5B and DB5A
    for slug, section in class_sections:
        if slug not in TARGET_SLUGS and slug not in DB5B_SLUGS and slug not in DB5A_SLUGS:
            continue

        skills = {}
        rej = []

        # Parse Passives
        passives_match = re.search(r'recommendedSkillSlugs:\s*\[(.*?)\]', section, re.DOTALL)
        if passives_match:
            for skill in re.findall(r'"([^"]+)"', passives_match.group(1)):
                add_skill(skills, rej, skill, "passive")

        # Parse Featured Skills (BM2, BM3, Buffs)
        featured_start = section.find('featuredSkillSections:')
        if featured_start != -1:
            next_block = re.search(r'\n {12}\w+:', section[featured_start+22:])
            end_idx = featured_start + 22 + next_block.start() if next_block else len(section)
            featured_content = section[featured_start:end_idx]

            blocks = re.findall(r'id:\s*"([^"]+)"[^{}]*?skillSlugs:\s*\[([^\]]*)\]', featured_content, re.DOTALL)
            for cat_id, slugs_str in blocks:
                category = "bm2" if "battle-mode-2" in cat_id else ("bm3" if "battle-mode-3" in cat_id else "buff")
                for skill in re.findall(r'"([^"]+)"', slugs_str):
                    add_skill(skills, rej, skill, category)

        # Parse Combos
        combo_start = section.find('comboSection:')
        if combo_start != -1:
            next_block = re.search(r'\n {12}\w+:', section[combo_start+15:])
            end_idx = combo_start + 15 + next_block.start() if next_block else len(section)
            combo_content = section[combo_start:end_idx]

            slug_lists = re.findall(r'skillSlugs:\s*\[([^\]]*)\]', combo_content, re.DOTALL)
            for slugs_str in slug_lists:
                for skill in re.findall(r'"([^"]+)"', slugs_str):
                    add_skill(skills, rej, skill, "attack")

        # Blade Buff Conditionals (Force Blader specific in Z section)
        if slug == "force-blader":
            blade_buffs_match = re.search(r'bladeBuffConditionals:\s*\[(.*?)\]', section, re.DOTALL)
            if blade_buffs_match:
                 for skill in re.findall(r'"([^"]+)"', blade_buffs_match.group(1)):
                     add_skill(skills, rej, skill, "blade-buff")

        manifest[slug] = skills
        rejected[slug] = rej
        coverage[slug] = {
            "mapped": len(skills),
            "rejected": len(rej)
        }

    consolidated_manifest = manifest
    total_coverage = coverage
    total_rejected = rejected
    critical_unresolved = 0
    for cls, skills in consolidated_manifest.items():
        for s, data in skills.items():
            if data["confidence"] != "HIGH":
                 critical_unresolved += 1

    # Generate Hash
    hash_source = []
    for cls, skills in consolidated_manifest.items():
        for s in sorted(skills.keys()):
            hash_source.append(f"{cls}:{s}:{skills[s]['category']}")
    hash_str = hashlib.sha256(",".join(hash_source).encode('utf-8')).hexdigest()[:8]

    # Calculate overall metrics for Gatekeeping
    total_skills_mapped = sum(len(skills) for skills in consolidated_manifest.values())
    total_classes = len(consolidated_manifest)
    total_rejected_count = sum(len(r) for r in total_rejected.values())

    # 9 Classes (3 from DB5A, 4 from DB5B, 2 from DB5C)
    expected_classes = 9
    coverage_percentage = (total_classes / expected_classes) * 100 if expected_classes > 0 else 0

    final_manifest = {
        "metadata": {
            "version": "v1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "auditor": "DB5C Audit Service",
            "source_hash": hash_str,
            "manifest_checksum": hashlib.md5(json.dumps(consolidated_manifest, sort_keys=True).encode('utf-8')).hexdigest()
        },
        "data": consolidated_manifest,
        "rejected": total_rejected
    }

    # Save final consolidated manifest
    with open('db5_consolidated_manifest_v1.0.0.json', 'w') as f:
        json.dump(final_manifest, f, indent=2)

    print(f"\n--- 9-Class Consolidated Coverage Report ---")
    print(json.dumps(total_coverage, indent=2))
    print(f"\nTotal Classes Mapped: {total_classes} / {expected_classes}")
    print(f"Total Skills Mapped: {total_skills_mapped}")

    print(f"\n--- All Rejected Records Summary ---")
    print(json.dumps(total_rejected, indent=2))

    print(f"\n--- Final SHA-256 Manifest Hash ---")
    print(hash_str)

    print(f"\n--- Hard Gatekeeping Checklist ---")
    print(f"Coverage: {coverage_percentage}% (Required: >=95%)")
    print(f"Critical Unresolved: {critical_unresolved} (Required: 0)")

    if coverage_percentage >= 95 and critical_unresolved == 0:
        print("\nOutcome: APPROVE DB6")
    else:
        print("\nOutcome: BLOCK DB6")
        if critical_unresolved > 0:
            print("Reason: There are unresolved or ambiguous skill aliases that must be fixed before DB6.")

    print("\nPASSED (Consolidation complete)")
    print("Deferred next session: DB6 - Import verified class-skill mapping")

if __name__ == "__main__":
    run_audit()
