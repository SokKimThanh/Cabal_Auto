"""Test skill image capture path in Library Manager."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("SKILL IMAGE CAPTURE - PATH TEST")
print("=" * 70)

print("\n[1] Testing capture_helper paths...")
try:
    from ui.helpers.capture_helper import ASSETS_DIR, ASSETS_SKILLS_DIR
    
    print(f"✓ Monster save dir: {ASSETS_DIR}")
    print(f"  Exists: {ASSETS_DIR.exists()}")
    
    print(f"✓ Skill save dir:   {ASSETS_SKILLS_DIR}")
    print(f"  Exists: {ASSETS_SKILLS_DIR.exists()}")
    
    # Check they're different
    if ASSETS_DIR != ASSETS_SKILLS_DIR:
        print("✓ Directories are different (correct!)")
    else:
        print("✗ ERROR: Both point to same directory!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[2] Testing capture function signature...")
try:
    import inspect
    from ui.helpers.capture_helper import capture_region_and_save
    
    sig = inspect.signature(capture_region_and_save)
    params = list(sig.parameters.keys())
    
    print(f"✓ Function parameters: {params}")
    
    if 'capture_type' in params:
        print("✓ 'capture_type' parameter exists")
        default = sig.parameters['capture_type'].default
        print(f"  Default value: '{default}'")
    else:
        print("✗ ERROR: 'capture_type' parameter missing!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[3] Testing Library Manager skill capture call...")
try:
    # Just check the code exists, don't actually run GUI
    from ui.windows.library_manager import LibraryManagerWindow
    import inspect
    
    # Get source of _capture_skill_image method
    source = inspect.getsource(LibraryManagerWindow._capture_skill_image)
    
    if "capture_type='skill'" in source:
        print("✓ Skill Tab uses capture_type='skill'")
    else:
        print("✗ WARNING: Skill Tab may not specify capture_type")
    
    if 'capture_region_and_save' in source:
        print("✓ Skill Tab calls capture_region_and_save")
    else:
        print("✗ ERROR: capture_region_and_save not found in skill capture")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[4] Physical directory verification...")
try:
    root = Path(__file__).parent
    skills_dir = root / 'assets' / 'images' / 'skills'
    monsters_dir = root / 'assets' / 'images' / 'monsters'
    
    print(f"Skills dir:   {skills_dir}")
    print(f"  Exists: {skills_dir.exists()}")
    if skills_dir.exists():
        skill_count = len(list(skills_dir.glob('*.png')))
        print(f"  PNG files: {skill_count}")
    
    print(f"Monsters dir: {monsters_dir}")
    print(f"  Exists: {monsters_dir.exists()}")
    if monsters_dir.exists():
        monster_count = len(list(monsters_dir.glob('*.png')))
        print(f"  PNG files: {monster_count}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nSUMMARY:")
print("- Monster images save to: assets/images/monsters/")
print("- Skill images save to:   assets/images/skills/")
print("- capture_type parameter controls which directory to use")
print("=" * 70)
