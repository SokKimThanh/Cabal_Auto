"""
Script to parse DB5B - Class-Skill Mapping Audit (Magic & Ranged: WI, FA, FG, DM)
"""
import re
import json
import hashlib

SOURCE_FILE = "lib/data/bm2-bm3-detail-skill-db-cabal.txt"
TARGET_SLUGS = {"wizard", "force-archer", "force-gunner", "dark-mage"}

def run_audit(content=None):
    if content is None:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()

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
    hash_source = []

    for slug, section in class_sections:
        if slug not in TARGET_SLUGS:
            continue

        skills = {}
        rej = []

        # Robust parsing using multi-line JSON-like extraction rather than brittle counting
        # 1. Parse Passive Skills
        passives_match = re.search(r'recommendedSkillSlugs:\s*\[(.*?)\]', section, re.DOTALL)
        if passives_match:
            for skill in re.findall(r'"([^"]+)"', passives_match.group(1)):
                skills[skill] = {"category": "passive", "confidence": "HIGH"}

        # 2. Parse Featured Skills (BM2, BM3, Buffs)
        featured_start = section.find('featuredSkillSections:')
        if featured_start != -1:
            # We look for the start of the next top-level block to bound our search
            # Top-level properties in this JS object are indented with 12 spaces.
            next_block = re.search(r'\n {12}\w+:', section[featured_start+22:])
            end_idx = featured_start + 22 + next_block.start() if next_block else len(section)
            featured_content = section[featured_start:end_idx]

            blocks = re.findall(r'id:\s*"([^"]+)"[^{}]*?skillSlugs:\s*\[([^\]]*)\]', featured_content, re.DOTALL)
            for cat_id, slugs_str in blocks:
                category = "bm2" if "battle-mode-2" in cat_id else ("bm3" if "battle-mode-3" in cat_id else "buff")
                for skill in re.findall(r'"([^"]+)"', slugs_str):
                    normalized = re.sub(r'-\d+$', '', skill)
                    if normalized != skill:
                        skills[normalized] = {"category": category, "confidence": "AMBIGUOUS"}
                        rej.append({"original": skill, "normalized": normalized, "reason": "suffix_stripped"})
                    else:
                        skills[normalized] = {"category": category, "confidence": "HIGH"}

        # 3. Parse Combos (Attacks)
        combo_start = section.find('comboSection:')
        if combo_start != -1:
            next_block = re.search(r'\n {12}\w+:', section[combo_start+15:])
            end_idx = combo_start + 15 + next_block.start() if next_block else len(section)
            combo_content = section[combo_start:end_idx]

            slug_lists = re.findall(r'skillSlugs:\s*\[([^\]]*)\]', combo_content, re.DOTALL)
            for slugs_str in slug_lists:
                for skill in re.findall(r'"([^"]+)"', slugs_str):
                    normalized = re.sub(r'-\d+$', '', skill)
                    if normalized != skill:
                        skills[normalized] = {"category": "attack", "confidence": "AMBIGUOUS"}
                        rej.append({"original": skill, "normalized": normalized, "reason": "suffix_stripped"})
                    else:
                        skills[normalized] = {"category": "attack", "confidence": "HIGH"}

        manifest[slug] = skills
        rejected[slug] = rej
        coverage[slug] = {
            "total": len(skills),
            "passives": len([s for s, data in skills.items() if data["category"] == "passive"]),
            "attacks": len([s for s, data in skills.items() if data["category"] == "attack"]),
            "bm2": len([s for s, data in skills.items() if data["category"] == "bm2"]),
            "bm3": len([s for s, data in skills.items() if data["category"] == "bm3"]),
            "buffs": len([s for s, data in skills.items() if data["category"] == "buff"]),
            "rejected": len(rej)
        }

        for s in sorted(skills.keys()):
            hash_source.append(f"{slug}:{s}:{skills[s]['category']}")

    hash_str = hashlib.sha256(",".join(hash_source).encode('utf-8')).hexdigest()[:8]

    print("=== DB5B Audit Magic & Ranged Classes ===")
    print("\nSource ID: class_skill_evidence")
    print(f"File Path: {SOURCE_FILE}")
    print("Parser Boundary: slug sections (wizard, force-archer, force-gunner, dark-mage)")

    print("\n--- Coverage Report ---")
    print(json.dumps(coverage, indent=2))

    print("\n--- Rejected Records ---")
    print(json.dumps(rejected, indent=2))

    print(f"\n--- Partial SHA-256 Partition Hash ---")
    print(hash_str)

    # Save the manifest to a JSON file for the next step
    manifest_path = "lib/data/db5b_magic_ranged_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest partition saved to {manifest_path}")

if __name__ == "__main__":
    run_audit()
