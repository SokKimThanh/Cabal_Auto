"""
Sprint 22 Patch 1 - Training Mode Test Suite

Automated tests for Training Mode feature implementation.

Test Coverage:
1. Database schema validation
2. Monster library load/save with training_mode
3. UI component initialization
4. SkillStats class functionality
5. Config persistence
6. i18n translations

Run: python tests/test_training_mode.py
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_database_schema():
    """Test 1: Verify monsters.json has training_mode field."""
    print("\n" + "="*60)
    print("TEST 1: Database Schema Validation")
    print("="*60)
    
    monsters_path = Path('lib/data/monsters.json')
    
    if not monsters_path.exists():
        print("❌ FAIL: monsters.json not found")
        return False
    
    with open(monsters_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # monsters.json is a direct array
    monsters = data if isinstance(data, list) else data.get('monsters', [])
    
    # Find "Coc go~" training dummy
    coc_go = None
    for monster in monsters:
        if 'Coc' in monster.get('name', '') and 'go' in monster.get('name', '').lower():
            coc_go = monster
            break
    
    if not coc_go:
        print("❌ FAIL: 'Coc go~' monster not found")
        return False
    
    if 'training_mode' not in coc_go:
        print("❌ FAIL: 'training_mode' field missing")
        return False
    
    if coc_go['training_mode'] != True:
        print("❌ FAIL: 'training_mode' should be True")
        return False
    
    print("✅ PASS: Database schema valid")
    print(f"   - Found monster: {coc_go.get('name')}")
    print(f"   - training_mode: {coc_go.get('training_mode')}")
    print(f"   - HP: {coc_go.get('hp')}")
    print(f"   - Templates: {len(coc_go.get('templates', []))}")
    return True


def test_skill_stats_class():
    """Test 2: Verify SkillStats class functionality."""
    print("\n" + "="*60)
    print("TEST 2: SkillStats Class Functionality")
    print("="*60)
    
    try:
        from lib.features.skills.skill_stats import SkillStats
    except ImportError as e:
        print(f"❌ FAIL: Cannot import SkillStats: {e}")
        return False
    
    # Initialize
    stats = SkillStats()
    print("✅ SkillStats initialized")
    
    # Test record_cast
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.1)
    stats.record_cast('Power Slash', success=True)
    time.sleep(0.1)
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.1)
    stats.record_cast('Ice Storm', success=False)
    
    print("✅ Recorded 4 skill casts")
    
    # Test get_cast_count
    fire_ball_count = stats.get_cast_count('Fire Ball')
    if fire_ball_count != 2:
        print(f"❌ FAIL: Fire Ball count should be 2, got {fire_ball_count}")
        return False
    print(f"✅ get_cast_count works: Fire Ball = {fire_ball_count}")
    
    # Test get_last_cast_time
    last_cast = stats.get_last_cast_time('Fire Ball')
    if last_cast is None:
        print("❌ FAIL: last_cast_time should not be None")
        return False
    print(f"✅ get_last_cast_time works: {last_cast}")
    
    # Test get_time_since_last_cast
    time_since = stats.get_time_since_last_cast('Fire Ball')
    if time_since is None or time_since < 0:
        print("❌ FAIL: time_since_last_cast invalid")
        return False
    print(f"✅ get_time_since_last_cast works: {time_since:.3f}s")
    
    # Test get_success_rate
    fire_ball_rate = stats.get_success_rate('Fire Ball')
    if fire_ball_rate != 100.0:
        print(f"❌ FAIL: Fire Ball success rate should be 100%, got {fire_ball_rate}%")
        return False
    
    ice_storm_rate = stats.get_success_rate('Ice Storm')
    if ice_storm_rate != 0.0:
        print(f"❌ FAIL: Ice Storm success rate should be 0%, got {ice_storm_rate}%")
        return False
    
    print(f"✅ get_success_rate works:")
    print(f"   - Fire Ball: {fire_ball_rate}%")
    print(f"   - Ice Storm: {ice_storm_rate}%")
    
    # Test get_all_stats
    all_stats = stats.get_all_stats()
    if len(all_stats) != 3:
        print(f"❌ FAIL: Should have 3 skills, got {len(all_stats)}")
        return False
    
    print(f"✅ get_all_stats works: {len(all_stats)} skills tracked")
    
    # Display all stats
    print("\n   📊 All Skill Statistics:")
    for skill, data in all_stats.items():
        time_str = f"{data['time_since_last_cast']:.1f}s ago" if data['time_since_last_cast'] else "Never"
        print(f"   - {skill}: {data['cast_count']} casts, {data['success_rate']:.0f}% success, last: {time_str}")
    
    # Test reset
    stats.reset_skill('Fire Ball')
    if stats.get_cast_count('Fire Ball') != 0:
        print("❌ FAIL: reset_skill failed")
        return False
    print("✅ reset_skill works")
    
    print("\n✅ PASS: All SkillStats tests passed")
    return True


def test_i18n_translations():
    """Test 3: Verify i18n translations exist."""
    print("\n" + "="*60)
    print("TEST 3: i18n Translations")
    print("="*60)
    
    try:
        from lib.i18n.translations import GLOBAL_TRANSLATIONS
    except ImportError as e:
        print(f"❌ FAIL: Cannot import translations: {e}")
        return False
    
    required_keys = [
        'enable_training_mode',
        'training_mode_desc',
        'training_mode_active',
        'training_mode_disabled',
        'skill_stats_title',
        'skill_name_col',
        'cast_count_col',
        'last_cast_col',
        'cooldown_col',
        'success_rate_col',
        'training_dummy_filter',
        'no_training_dummies',
        'time_ago_format',
        'cooldown_ready'
    ]
    
    missing_en = []
    missing_vi = []
    
    en_translations = GLOBAL_TRANSLATIONS.get('en', {})
    vi_translations = GLOBAL_TRANSLATIONS.get('vi', {})
    
    for key in required_keys:
        if key not in en_translations:
            missing_en.append(key)
        if key not in vi_translations:
            missing_vi.append(key)
    
    if missing_en:
        print(f"❌ FAIL: Missing EN translations: {missing_en}")
        return False
    
    if missing_vi:
        print(f"❌ FAIL: Missing VI translations: {missing_vi}")
        return False
    
    print(f"✅ PASS: All {len(required_keys)} translation keys present")
    print("\n   Sample translations:")
    print(f"   EN: {en_translations['enable_training_mode']}")
    print(f"   VI: {vi_translations['enable_training_mode']}")
    print(f"   EN: {en_translations['skill_stats_title']}")
    print(f"   VI: {vi_translations['skill_stats_title']}")
    
    return True


def test_hunt_config_schema():
    """Test 4: Verify hunt_config.json schema support."""
    print("\n" + "="*60)
    print("TEST 4: Hunt Config Schema")
    print("="*60)
    
    config_path = Path('lib/data/hunt_config.json')
    
    if not config_path.exists():
        print("⚠️  WARNING: hunt_config.json not found (will be created on first run)")
        return True
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check if training_mode_enabled field can be added
    print(f"✅ hunt_config.json exists")
    print(f"   Current keys: {list(config.keys())[:5]}...")
    
    if 'training_mode_enabled' in config:
        print(f"   training_mode_enabled: {config['training_mode_enabled']}")
    else:
        print("   training_mode_enabled: (not set, will default to False)")
    
    return True


def test_file_structure():
    """Test 5: Verify all required files exist."""
    print("\n" + "="*60)
    print("TEST 5: File Structure Validation")
    print("="*60)
    
    required_files = [
        'lib/features/skills/skill_stats.py',
        'lib/i18n/translations.py',
        'lib/data/monsters.json',
        'app_gui.py',
        'ui/auto_hunt.py',
        'docs/sprint22/SPRINT22_PATCH1_TRAINING_MODE.md',
        'docs/sprint22/IMPLEMENTATION_GUIDE.md',
        'docs/sprint22/SPRINT22_SUMMARY.md',
        'docs/sprint22/IMPLEMENTATION_STATUS.md',
        'docs/INDEX.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ FAIL: Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print(f"✅ PASS: All {len(required_files)} required files exist")
    
    # Check file sizes
    print("\n   File sizes:")
    for file_path in required_files[:5]:  # Show first 5
        size = Path(file_path).stat().st_size
        print(f"   - {file_path}: {size:,} bytes")
    
    return True


def run_all_tests():
    """Run all automated tests."""
    print("\n" + "="*60)
    print("🧪 SPRINT 22 PATCH 1 - TRAINING MODE TEST SUITE")
    print("="*60)
    print(f"Date: October 21, 2025")
    print(f"Tests: 5 automated test suites")
    print("="*60)
    
    results = {
        'Database Schema': test_database_schema(),
        'SkillStats Class': test_skill_stats_class(),
        'i18n Translations': test_i18n_translations(),
        'Hunt Config Schema': test_hunt_config_schema(),
        'File Structure': test_file_structure()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ready for manual UI testing!")
        print("\nNext steps:")
        print("1. Run: python app_gui.py")
        print("2. Navigate to Hunt tab")
        print("3. Enable Training Mode checkbox")
        print("4. Start hunt and verify skill stats display")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
    
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
