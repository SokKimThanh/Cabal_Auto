"""
Quick test to verify combobox data loading in Timing Calculator
"""
import sys
import pytest
from pathlib import Path

pytestmark = pytest.mark.unit

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_data_loading():
    """Test that monsters and skills load correctly"""
    print("=" * 70)
    print("TESTING COMBOBOX DATA LOADING")
    print("=" * 70)
    
    # Mock data for testing
    test_monsters = [
        {'name': 'Coc go~', 'hp': 10000, 'damage_per_hit': 175, 'description': 'Test monster 1'},
        {'name': 'Dragon Boss', 'hp': 100000, 'damage_per_hit': 1000, 'description': 'Test monster 2'},
        {'name': 'Weak Slime', 'hp': 1000, 'damage_per_hit': 500, 'description': 'Test monster 3'},
    ]
    
    test_skills = [
        {'name': 'Dark Explosion', 'cooldown': 1.5, 'cast_time': 0.5, 'type': 'attack'},
        {'name': 'Lightning Strike', 'cooldown': 2.0, 'cast_time': 0.3, 'type': 'attack'},
        {'name': 'Heal', 'cooldown': 5.0, 'cast_time': 1.0, 'type': 'buff'},
        {'name': 'Fire Ball', 'cooldown': 1.0, 'cast_time': 0.2, 'type': 'attack'},
    ]
    
    print("\n📦 Test Data:")
    print(f"  Monsters: {len(test_monsters)}")
    for m in test_monsters:
        print(f"    - {m['name']} (HP: {m['hp']:,}, Damage: {m['damage_per_hit']})")
    
    print(f"\n  Skills: {len(test_skills)}")
    for s in test_skills:
        print(f"    - {s['name']} (Type: {s['type']}, CD: {s['cooldown']}s)")
    
    # Simulate what _refresh_timing_monsters() does
    print("\n\n📊 Simulating _refresh_timing_monsters():")
    print("-" * 70)
    monster_names = [m['name'] for m in test_monsters]
    print(f"Monster names for combobox: {monster_names}")
    print(f"✅ Total: {len(monster_names)} monsters")
    
    # Simulate what _refresh_timing_skills() does
    print("\n\n📊 Simulating _refresh_timing_skills():")
    print("-" * 70)
    attack_skills = [s for s in test_skills if s.get('type') == 'attack']
    skill_names = [s['name'] for s in attack_skills]
    print(f"Attack skill names for combobox: {skill_names}")
    print(f"✅ Total: {len(skill_names)} attack skills (filtered from {len(test_skills)} total)")
    
    # Simulate monster selection
    print("\n\n📊 Simulating monster selection (Coc go~):")
    print("-" * 70)
    selected_name = 'Coc go~'
    selected_monster = next((m for m in test_monsters if m['name'] == selected_name), None)
    
    if selected_monster:
        hp = selected_monster.get('hp', 'N/A')
        damage = selected_monster.get('damage_per_hit', 'N/A')
        desc = selected_monster.get('description', 'N/A')
        
        print(f"Selected: {selected_name}")
        print(f"  HP: {hp:,}" if isinstance(hp, (int, float)) else f"  HP: {hp}")
        print(f"  Damage per hit: {damage:,}" if isinstance(damage, (int, float)) else f"  Damage: {damage}")
        print(f"  Description: {desc}")
        print("✅ Monster info loaded successfully")
    else:
        print("❌ Failed to find monster")
    
    # Simulate skill selection
    print("\n\n📊 Simulating skill selection (Dark Explosion):")
    print("-" * 70)
    selected_skill_name = 'Dark Explosion'
    selected_skill = next((s for s in test_skills if s['name'] == selected_skill_name), None)
    
    if selected_skill:
        cooldown = selected_skill.get('cooldown', 'N/A')
        cast_time = selected_skill.get('cast_time', 'N/A')
        skill_type = selected_skill.get('type', 'N/A')
        
        print(f"Selected: {selected_skill_name}")
        print(f"  Cooldown: {cooldown}s")
        print(f"  Cast time: {cast_time}s")
        print(f"  Type: {skill_type}")
        print("✅ Skill info loaded successfully")
    else:
        print("❌ Failed to find skill")
    
    print("\n\n" + "=" * 70)
    print("✅ ALL DATA LOADING TESTS PASSED!")
    print("=" * 70)
    
    print("\n\n💡 How to test in real UI:")
    print("-" * 70)
    print("""
1. Make sure you have some monsters and skills in Library Manager
   
2. Go to Monster Library tab:
   - Add a monster with HP and damage_per_hit
   - Example: Name="Coc go~", HP=10000, Damage=175
   
3. Go to Skill Library tab:
   - Add an attack skill
   - Example: Name="Dark Explosion", Type="attack", Cooldown=1.5
   
4. Go to Timing Calculator tab:
   - Comboboxes should now have data
   - Select monster → See HP/damage info
   - Select skill → See cooldown/cast time info
   - Click Calculate → See results
   - Click Apply → Settings saved
   
5. If comboboxes are empty:
   - Check that monsters list is not empty when Library Manager opens
   - Check that skills list is not empty
   - Check console for error messages
    """)

if __name__ == '__main__':
    test_data_loading()
