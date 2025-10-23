"""
Test Timing Calculator UI - Sprint 19 Task #4

This script tests the timing calculator functionality integrated into Library Manager.

Test Scenarios:
1. Basic calculation with normal monster
2. High HP boss monster
3. Low HP weak monster
4. Different attack speed presets
5. Apply to hunt config
6. Edge cases (missing data, invalid input)

Run: pytest tests/unit/test_timing_calculator_ui.py
"""

import sys
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_calculator_logic():
    """Test the calculator logic directly"""
    from lib.features.timing.calculator import calculate_timing, calculate_timing_from_monster
    
    print("=" * 70)
    print("TIMING CALCULATOR LOGIC TESTS")
    print("=" * 70)
    
    # Test 1: Normal monster
    print("\n📊 Test 1: Normal Monster (Coc go~)")
    print("-" * 70)
    result1 = calculate_timing(
        monster_hp=10000,
        damage_per_hit=175,
        attacks_per_second=2.0
    )
    print(result1)
    
    # Assertions
    assert result1.hits_to_kill == 58, f"Expected 58 hits, got {result1.hits_to_kill}"
    assert result1.estimated_kill_time_sec == 29.0, f"Expected 29s kill time, got {result1.estimated_kill_time_sec}"
    print("✅ Test 1 passed!")
    
    # Test 2: Boss monster
    print("\n\n📊 Test 2: Boss Monster (High HP)")
    print("-" * 70)
    result2 = calculate_timing(
        monster_hp=100000,
        damage_per_hit=1000,
        attacks_per_second=2.0
    )
    print(result2)
    assert result2.hits_to_kill == 100, f"Expected 100 hits, got {result2.hits_to_kill}"
    print("✅ Test 2 passed!")
    
    # Test 3: Weak monster
    print("\n\n📊 Test 3: Weak Monster (Low HP)")
    print("-" * 70)
    result3 = calculate_timing(
        monster_hp=1000,
        damage_per_hit=500,
        attacks_per_second=2.0
    )
    print(result3)
    assert result3.hits_to_kill == 2, f"Expected 2 hits, got {result3.hits_to_kill}"
    print("✅ Test 3 passed!")
    
    # Test 4: Fast attack speed
    print("\n\n📊 Test 4: Fast Attack Speed (4 APS)")
    print("-" * 70)
    result4 = calculate_timing(
        monster_hp=10000,
        damage_per_hit=300,
        attacks_per_second=4.0
    )
    print(result4)
    assert result4.hits_to_kill == 34, f"Expected 34 hits, got {result4.hits_to_kill}"
    print("✅ Test 4 passed!")
    
    # Test 5: Calculate from monster dict
    print("\n\n📊 Test 5: Calculate from Monster Dict")
    print("-" * 70)
    monster = {
        'name': 'Test Dragon',
        'hp': 50000,
        'damage_per_hit': 750
    }
    result5 = calculate_timing_from_monster(monster, attacks_per_second=2.5)
    print(result5)
    assert result5 is not None, "Result should not be None"
    assert result5.hits_to_kill == 67, f"Expected 67 hits, got {result5.hits_to_kill}"
    print("✅ Test 5 passed!")
    
    # Test 6: Missing data
    print("\n\n📊 Test 6: Missing Data Handling")
    print("-" * 70)
    invalid_monster = {
        'name': 'Invalid',
        'hp': 0,  # Invalid HP
        'damage_per_hit': 100
    }
    result6 = calculate_timing_from_monster(invalid_monster)
    print(f"Result for invalid monster: {result6}")
    assert result6 is None, "Should return None for invalid data"
    print("✅ Test 6 passed!")
    
    print("\n" + "=" * 70)
    print("✅ ALL LOGIC TESTS PASSED!")
    print("=" * 70)


def test_presets():
    """Test attack speed presets"""
    from lib.features.timing.calculator import get_timing_presets
    
    print("\n\n" + "=" * 70)
    print("ATTACK SPEED PRESETS TEST")
    print("=" * 70)
    
    presets = get_timing_presets()
    
    assert 'slow' in presets, "Slow preset missing"
    assert 'normal' in presets, "Normal preset missing"
    assert 'fast' in presets, "Fast preset missing"
    assert 'very_fast' in presets, "Very fast preset missing"
    
    print("\n📋 Available Presets:")
    for name, (aps, desc) in presets.items():
        print(f"  {name:12s}: {aps:.1f} APS - {desc}")
    
    # Verify APS values
    assert presets['slow'][0] == 1.0, "Slow should be 1.0 APS"
    assert presets['normal'][0] == 2.0, "Normal should be 2.0 APS"
    assert presets['fast'][0] == 3.0, "Fast should be 3.0 APS"
    assert presets['very_fast'][0] == 4.0, "Very fast should be 4.0 APS"
    
    print("\n✅ ALL PRESET TESTS PASSED!")


def test_ui_integration():
    """Test UI integration (requires GUI)"""
    print("\n\n" + "=" * 70)
    print("UI INTEGRATION TEST")
    print("=" * 70)
    print("\n⚠️ Manual UI Testing Required:")
    print("=" * 70)
    print("""
To test the UI, follow these steps:

1. Run: python app_gui.py
2. Click "Library Manager" button
3. Go to "Timing Calculator" tab
4. Select a monster (e.g., "Coc go~")
5. Select a skill (e.g., "Dark Explosion")
6. Choose attack speed preset or enter custom value
7. Click "🔢 Calculate Optimal Timing"
8. Verify results display correctly
9. Click "✅ Apply to Hunt Config"
10. Verify settings saved to hunt_config.json

Expected UI Elements:
✓ Step 1: Monster dropdown with info display
✓ Step 2: Skill dropdown with info display
✓ Step 3: Attack speed presets + custom input
✓ Calculate button (blue, prominent)
✓ Results text area (formatted nicely)
✓ Apply button (green, initially disabled)

Expected Behavior:
✓ Monster info updates when selected
✓ Skill info updates when selected
✓ Preset changes update APS input
✓ Calculate shows formatted results
✓ Apply button enables after calculation
✓ Apply updates hunt config and shows success
    """)


def test_calculation_accuracy():
    """Test calculation accuracy with real-world scenarios"""
    from lib.features.timing.calculator import calculate_timing
    
    print("\n\n" + "=" * 70)
    print("CALCULATION ACCURACY TESTS (Real-World Scenarios)")
    print("=" * 70)
    
    scenarios = [
        {
            'name': 'Low-level grinding',
            'hp': 5000,
            'damage': 250,
            'aps': 2.0,
            'expected_hits': 20,
            'expected_time': 10.0
        },
        {
            'name': 'Mid-level farming',
            'hp': 25000,
            'damage': 500,
            'aps': 2.5,
            'expected_hits': 50,
            'expected_time': 20.0
        },
        {
            'name': 'Boss hunting',
            'hp': 150000,
            'damage': 2000,
            'aps': 1.5,
            'expected_hits': 75,
            'expected_time': 50.0
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 70)
        
        result = calculate_timing(
            monster_hp=scenario['hp'],
            damage_per_hit=scenario['damage'],
            attacks_per_second=scenario['aps']
        )
        
        print(f"Monster HP: {scenario['hp']:,}")
        print(f"Damage/hit: {scenario['damage']:,}")
        print(f"Attack speed: {scenario['aps']:.1f} APS")
        print(f"\nCalculated:")
        print(f"  Hits to kill: {result.hits_to_kill}")
        print(f"  Kill time: {result.estimated_kill_time_sec:.2f}s")
        print(f"  Lost timeout: {result.lost_timeout_sec:.2f}s")
        print(f"  Attack duration: {result.attack_min_duration_sec:.2f}s")
        
        # Verify
        assert result.hits_to_kill == scenario['expected_hits'], \
            f"Expected {scenario['expected_hits']} hits, got {result.hits_to_kill}"
        assert result.estimated_kill_time_sec == scenario['expected_time'], \
            f"Expected {scenario['expected_time']}s, got {result.estimated_kill_time_sec}s"
        
        print("✅ Accuracy verified!")
    
    print("\n" + "=" * 70)
    print("✅ ALL ACCURACY TESTS PASSED!")
    print("=" * 70)


def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("TIMING CALCULATOR TEST SUITE - Sprint 19 Task #4")
    print("🧪" * 35 + "\n")
    
    try:
        test_calculator_logic()
        test_presets()
        test_calculation_accuracy()
        test_ui_integration()
        
        print("\n\n" + "🎉" * 35)
        print("ALL AUTOMATED TESTS PASSED!")
        print("Please complete manual UI testing as described above.")
        print("🎉" * 35 + "\n")
        
    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
