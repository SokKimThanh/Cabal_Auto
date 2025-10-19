"""
Quick Test: Skill Rotation Builder UI
Run this to verify UI components work
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

print("="*70)
print("🧪 SKILL ROTATION BUILDER - QUICK TEST")
print("="*70)
print()

# Test 1: Import module
print("Test 1: Import module...")
try:
    from lib.features.skill_rotation import (
        SkillRotation,
        calculate_rotation_timing,
        generate_rotation_preview,
        SkillRotationUI
    )
    print("✅ Module imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Calculate sample rotation
print("Test 2: Calculate sample rotation...")
sample_skills = [
    {
        'name': 'Dark Explosion',
        'key': '1',
        'type': 'attack',
        'cooldown': 1.9,
        'cast_time': 1.7
    },
    {
        'name': 'Regeneration',
        'key': '4',
        'type': 'buff',
        'cooldown': 2.2,
        'cast_time': 1.0
    },
    {
        'name': 'Bone Javelin',
        'key': '2',
        'type': 'attack',
        'cooldown': 2.4,
        'cast_time': 1.5
    }
]

try:
    rotation = calculate_rotation_timing(sample_skills)
    print(f"✅ Rotation calculated")
    print(f"   • Total cycle: {rotation.total_cycle_time:.2f}s")
    print(f"   • Skills: {rotation.skills_per_cycle}")
    print(f"   • Attack interval: {rotation.attack_interval:.2f}s")
    print(f"   • Press duration: {rotation.attack_press_ms}ms")
except Exception as e:
    print(f"❌ Calculation failed: {e}")
    sys.exit(1)

print()

# Test 3: Generate preview
print("Test 3: Generate preview...")
try:
    preview = generate_rotation_preview(rotation)
    print("✅ Preview generated")
    print()
    print("─" * 70)
    print(preview)
    print("─" * 70)
except Exception as e:
    print(f"❌ Preview failed: {e}")
    sys.exit(1)

print()

# Test 4: Check UI class
print("Test 4: Check UI class...")
try:
    # Just verify class is available
    assert hasattr(SkillRotationUI, '_build_ui')
    assert hasattr(SkillRotationUI, '_calculate_rotation')
    assert hasattr(SkillRotationUI, '_apply_rotation')
    print("✅ UI class has required methods")
except AssertionError:
    print("❌ UI class missing methods")
    sys.exit(1)

print()

# Test 5: Check hunt_config.json
print("Test 5: Check hunt_config.json...")
try:
    import json
    config_path = root_dir / 'lib' / 'data' / 'hunt_config.json'
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        skills = config.get('skill_slots', [])
        print(f"✅ hunt_config.json found")
        print(f"   • Skills available: {len(skills)}")
        
        if skills:
            print(f"   • Sample skill: {skills[0]['name']}")
    else:
        print("⚠️  hunt_config.json not found")
except Exception as e:
    print(f"⚠️  Config check failed: {e}")

print()
print("="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print()
print("🚀 Next step: Run `python app_gui.py` and go to 'Skill Rotation' tab")
print()
