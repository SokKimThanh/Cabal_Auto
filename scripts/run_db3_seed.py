import sys
import os

# Ensure lib is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.db.services.seed_skill_sprite_service import SeedSkillSpriteService
import json

def run_seed():
    print("Starting DB3 - Seed Skill Sprite Catalogue...")

    # Empty DB state - Checked implicitly by service checking if rows exist
    # Validation constraints: Source ID, File, Parser boundary, idempotency, unique names
    service = SeedSkillSpriteService()

    print(f"Authorized source ID: {service.source_id}")
    print(f"Authorized file: {service.source_file}")

    result = service.seed_skill_sprites()

    print("\n--- Seed Results ---")
    print(json.dumps(result, indent=2))

    if result.get("status") == "PASSED":
        print(f"\nVALIDATION: PASSED")
        print(f"Total Rows: {result['total_rows']}, Distinct Names: {result['distinct_names']}, Inserted: {result['inserted']}, Skipped: {result['skipped']}")
    else:
        print(f"\nVALIDATION: ABORTED/REVERTED")
        print(f"Reason: {result.get('message', 'Unknown Error')}")
        sys.exit(1)

if __name__ == "__main__":
    run_seed()
