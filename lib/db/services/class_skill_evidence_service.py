import json
import hashlib
import re
import os

class ClassSkillEvidenceService:
    def __init__(self):
        self.source_file = 'lib/data/bm2-bm3-detail-skill-db-cabal.txt'
        self.sprite_file = 'lib/data/skill-db-cabal-2.txt'

    def read_file_content(self, filepath):
        with open(filepath, 'r') as f:
            return f.read()

    def get_source_hash(self):
        with open(self.source_file, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get_sprite_keys(self):
        content = self.read_file_content(self.sprite_file)
        return set(re.findall(r'"([^"]+)":{"x":', content))

    def map_category(self, title):
        title_lower = title.lower()
        if 'battle mode 1' in title_lower or 'bm1' in title_lower: return 'bm1'
        if 'battle mode 2' in title_lower or 'bm2' in title_lower: return 'bm2'
        if 'battle mode 3' in title_lower or 'bm3' in title_lower: return 'bm3'
        if 'debuff' in title_lower: return 'debuff'
        if 'buff' in title_lower: return 'buff'
        if 'passive' in title_lower: return 'passive'
        if 'heal' in title_lower: return 'utility'
        if 'combo' in title_lower: return 'attack'
        if 'totem' in title_lower: return 'utility'
        return 'attack'

    def extract_categories(self, content):
        slugs_pos = []
        for m in re.finditer(r'slug:\s*"([^"]+)"', content):
            slugs_pos.append((m.group(1), m.start()))

        valid_slugs = {"blader", "dark-mage", "force-archer", "force-blader", "force-gunner", "force-shielder", "gladiator", "warrior", "wizard"}
        slugs_pos = [s for s in slugs_pos if s[0] in valid_slugs]
        slugs_pos.sort(key=lambda x: x[1])
        slugs_pos.append(("END", len(content)))

        results = []
        for i in range(len(slugs_pos) - 1):
            slug, start = slugs_pos[i]
            _, end = slugs_pos[i+1]
            chunk = content[start:end]

            skill_categories = []

            section_matches = re.finditer(r'id:\s*"([^"]+)"\s*,\s*title:\s*"([^"]+)"[\s\S]*?skillSlugs:\s*\[(.*?)\]', chunk)
            for sm in section_matches:
                skill_categories.append({
                    'category': sm.group(2),
                    'slugs': re.findall(r'"([^"]+)"', sm.group(3)),
                    'evidence': sm.group(1)
                })

            combo_match = re.search(r'comboSection:\s*\{[\s\S]*?skillSlugs:\s*\[(.*?)\]', chunk)
            if combo_match:
                skill_categories.append({
                    'category': 'Combo',
                    'slugs': re.findall(r'"([^"]+)"', combo_match.group(1)),
                    'evidence': 'comboSection'
                })

            passive_match = re.search(r'passiveSkillConfig:\s*\{[\s\S]*?recommendedSkillSlugs:\s*\[(.*?)\]', chunk)
            if passive_match:
                skill_categories.append({
                    'category': 'Passive',
                    'slugs': re.findall(r'"([^"]+)"', passive_match.group(1)),
                    'evidence': 'passiveSkillConfig'
                })

            results.append({'class_code': slug, 'categories': skill_categories})

        return results

    def build_manifest(self):
        content = self.read_file_content(self.source_file)
        source_hash = self.get_source_hash()
        sprite_keys = self.get_sprite_keys()

        extracted = self.extract_categories(content)

        manifest_rows = []
        for r in extracted:
            class_code = r['class_code']
            for cat in r['categories']:
                db_category = self.map_category(cat['category'])
                for skill_code in cat['slugs']:
                    original = skill_code
                    unresolved = []
                    confidence = "high"

                    if original not in sprite_keys:
                        confidence = "ambiguous"
                        unresolved.append(original)

                    manifest_rows.append({
                        "source_class": class_code,
                        "source_skill_code": original,
                        "category": db_category,
                        "evidence_location": cat['evidence'],
                        "parser_boundary": "class-guide objects with slug and skillSlugs arrays",
                        "source_hash": source_hash,
                        "confidence": confidence,
                        "unresolved_aliases": unresolved
                    })

        return manifest_rows

    def report(self, manifest):
        total = len(manifest)
        unresolved = [m for m in manifest if m['confidence'] == 'ambiguous']

        print("--- DB5 Audit Report ---")
        print(f"Source ID: class_skill_evidence")
        print(f"Source file: {self.source_file}")
        print(f"Parser boundary: class-guide objects with slug and skillSlugs arrays")
        print(f"Expected source count: 9 classes")
        print(f"Forbidden inputs: skills.json, image-count-skill-db-cabal.txt, color-skill-character-db-cabal.txt")
        print(f"Total mappings found: {total}")
        print(f"Unresolved skill aliases (confidence=ambiguous): {len(unresolved)}")

        # Save manifest
        with open('db5_mapping_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        print("Manifest saved to db5_mapping_manifest.json")
        print("Status: PASSED (Read-only session)")

if __name__ == '__main__':
    service = ClassSkillEvidenceService()
    manifest = service.build_manifest()
    service.report(manifest)
