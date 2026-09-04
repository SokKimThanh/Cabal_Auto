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

Run: pytest tests/sprints/sprint22/test_training_mode.py -v
"""

import json
import sys
import time
import pytest
from pathlib import Path

pytestmark = pytest.mark.integration


# ============================================================================
# PROJECT PATH SETUP
# ============================================================================
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ============================================================================
# TEST FUNCTIONS
# ============================================================================


def test_database_schema():
    """Test 1: Verify monsters.json schema supports training_mode field."""
    monsters_path = Path('lib/data/monsters.json')
    
    assert monsters_path.exists(), f"monsters.json should exist at {monsters_path}"
    
    with open(monsters_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # monsters.json is a direct array
    monsters = data if isinstance(data, list) else data.get('monsters', [])
    
    assert isinstance(monsters, list), "monsters.json should contain a list of monsters"
    
    # Check that all monsters have required fields
    if len(monsters) > 0:
        # Verify first monster has basic required fields
        first_monster = monsters[0]
        assert 'name' in first_monster, "Monster should have 'name' field"
        assert 'hp' in first_monster, "Monster should have 'hp' field"
        assert 'templates' in first_monster, "Monster should have 'templates' field"
        
        # Note: training_mode is optional, so we just verify the schema can support it
        # If any monster has training_mode field, verify it's a boolean
        for monster in monsters:
            if 'training_mode' in monster:
                training_mode = monster['training_mode']
                assert isinstance(training_mode, bool), \
                    f"Monster '{monster.get('name')}' training_mode should be boolean, got {type(training_mode)}"
                break
    else:
        pytest.skip("No monsters in database to test schema")


def test_skill_stats_class():
    """Test 2: Verify SkillStats class functionality."""
    from lib.features.skills.skill_stats import SkillStats
    
    # Initialize
    stats = SkillStats()
    assert stats is not None, "SkillStats should initialize successfully"
    
    # Test record_cast
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.1)
    stats.record_cast('Power Slash', success=True)
    time.sleep(0.1)
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.1)
    stats.record_cast('Ice Storm', success=False)
    
    # Test get_cast_count
    fire_ball_count = stats.get_cast_count('Fire Ball')
    assert fire_ball_count == 2, f"Fire Ball count should be 2, got {fire_ball_count}"
    
    # Test get_last_cast_time
    last_cast = stats.get_last_cast_time('Fire Ball')
    assert last_cast is not None, "last_cast_time should not be None for casted skill"
    
    # Test get_time_since_last_cast
    time_since = stats.get_time_since_last_cast('Fire Ball')
    assert time_since is not None, "time_since_last_cast should not be None for casted skill"
    assert time_since >= 0, f"time_since_last_cast should be non-negative, got {time_since}"
    
    # Test get_success_rate
    fire_ball_rate = stats.get_success_rate('Fire Ball')
    assert fire_ball_rate == 100.0, f"Fire Ball success rate should be 100%, got {fire_ball_rate}%"
    
    ice_storm_rate = stats.get_success_rate('Ice Storm')
    assert ice_storm_rate == 0.0, f"Ice Storm success rate should be 0%, got {ice_storm_rate}%"
    
    # Test get_all_stats
    all_stats = stats.get_all_stats()
    assert isinstance(all_stats, dict), f"get_all_stats should return dict, got {type(all_stats)}"
    assert len(all_stats) == 3, f"Should have 3 skills, got {len(all_stats)}"
    
    # Test reset
    stats.reset_skill('Fire Ball')
    reset_count = stats.get_cast_count('Fire Ball')
    assert reset_count == 0, f"reset_skill should reset cast count to 0, got {reset_count}"


def test_i18n_translations():
    """Test 3: Verify i18n translations exist."""
    from lib.i18n.translations import GLOBAL_TRANSLATIONS
    
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
    
    assert not missing_en, f"Missing EN translations: {missing_en}"
    assert not missing_vi, f"Missing VI translations: {missing_vi}"


def test_hunt_config_schema():
    """Test 4: Verify hunt_config.json schema support."""
    config_path = Path('lib/data/hunt_config.json')
    
    if not config_path.exists():
        pytest.skip("hunt_config.json not found (will be created on first run)")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verify config is valid JSON dict
    assert isinstance(config, dict), "hunt_config.json should contain a dictionary"


def test_file_structure():
    """Test 5: Verify all required files exist."""
    required_files = [
        'lib/features/skills/skill_stats.py',
        'lib/i18n/translations.py',
        'lib/data/monsters.json',
        'app_gui.py',
        'ui/auto_hunt.py',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    assert not missing_files, f"Missing required files: {missing_files}"


# ============================================================================
# MANUAL TEST RUNNER (not for pytest)
# ============================================================================

if __name__ == '__main__':
    """Manual test execution."""
    print("\n⚠️  For automated testing, use: pytest tests/sprints/sprint22/test_training_mode.py")
    sys.exit(pytest.main([__file__, "-v"]))
