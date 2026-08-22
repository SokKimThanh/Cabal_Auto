"""Test consolidated image paths after migration."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("IMAGE PATH CONSOLIDATION TEST")
print("=" * 60)

# Test 1: Icon Helper
print("\n[1] Testing Icon Helper (icons)...")
try:
    from ui.helpers.icon_helper import IconHelper
    helper = IconHelper()
    icons_dir = helper.icons_dir
    print(f"✓ Icons directory: {icons_dir}")
    print(f"  Exists: {icons_dir.exists()}")
    if icons_dir.exists():
        icon_count = len(list(icons_dir.glob('*.png'))) + len(list(icons_dir.glob('*.ico')))
        print(f"  Icon files: {icon_count}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Capture Helper  
print("\n[2] Testing Capture Helper (monsters)...")
try:
    from ui.helpers import capture_helper
    assets_dir = capture_helper.ASSETS_DIR
    print(f"✓ Monsters directory: {assets_dir}")
    print(f"  Exists: {assets_dir.exists()}")
    if assets_dir.exists():
        monster_count = len(list(assets_dir.glob('*.png')))
        print(f"  Monster files: {monster_count}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Skill Migrator
print("\n[3] Testing Skill Migrator (skills)...")
try:
    from lib.features.skills.migrator import SkillMigrator
    migrator = SkillMigrator()
    skills_dir = migrator.project_images_dir
    print(f"✓ Skills directory: {skills_dir}")
    abs_skills_dir = skills_dir if skills_dir.is_absolute() else Path.cwd() / skills_dir
    print(f"  Resolved to: {abs_skills_dir}")
    print(f"  Exists: {abs_skills_dir.exists()}")
    if abs_skills_dir.exists():
        skill_count = len(list(abs_skills_dir.glob('*.png')))
        print(f"  Skill files: {skill_count}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Physical verification
print("\n[4] Physical Directory Verification...")
root = Path(__file__).parent
assets_images = root / 'assets' / 'images'
print(f"Root assets/images: {assets_images}")
for subdir in ['icons', 'monsters', 'skills']:
    path = assets_images / subdir
    if path.exists():
        count = len(list(path.glob('*.png'))) + len(list(path.glob('*.ico')))
        print(f"  {subdir}/: {count} files")
    else:
        print(f"  {subdir}/: NOT FOUND")

# Test 5: Old directory check
print("\n[5] Old Directory Check (should be empty or removed)...")
old_lib_assets = root / 'lib' / 'assets' / 'images'
if old_lib_assets.exists():
    old_count = sum(1 for _ in old_lib_assets.rglob('*.png'))
    print(f"⚠ Old lib/assets/images still exists with {old_count} files")
    print(f"  Path: {old_lib_assets}")
    print("  → Can be safely removed after verification")
else:
    print("✓ Old lib/assets/images not found (already removed)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
