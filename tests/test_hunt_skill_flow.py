"""
Test complete hunt skill flow - Kiểm tra toàn bộ flow skill trong hunt
"""
import sys
import time
sys.path.insert(0, 'E:/Cabal_Auto')

from lib.system.win_input import tap

print("=" * 70)
print("HUNT SKILL FLOW TEST - Mô phỏng hunt flow đầy đủ")
print("=" * 70)
print()
print("Test này sẽ mô phỏng đúng logic của app:")
print("1. SEARCH MODE: Chỉ cast buff skills (phím 4)")
print("2. ATTACK MODE: Cast attack skills (phím 1, 2, 3)")
print()
print("⚠️ Chuẩn bị:")
print("  1. Click vào game window")
print("  2. Đảm bảo character đang đứng yên")
print("  3. Quan sát xem skills có được cast không")
print()
input("Press ENTER to start test in 5 seconds...")

print("\nCountdown...")
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

# Skill configuration from hunt_config.json
skills = [
    {"name": "Dark Explosion", "key": "1", "type": "attack", "cooldown": 1.9, "press_ms": 1700},
    {"name": "Bone Javelin", "key": "2", "type": "attack", "cooldown": 2.4, "press_ms": 1500},
    {"name": "Skull Shooter", "key": "3", "type": "attack", "cooldown": 2.2, "press_ms": 1500},
    {"name": "Regeneration", "key": "4", "type": "buff", "cooldown": 2.2, "press_ms": 1000},
]

# Track cooldowns
skill_runtime = []
for skill in skills:
    skill_runtime.append({
        'name': skill['name'],
        'key': skill['key'],
        'type': skill['type'],
        'cooldown': skill['cooldown'],
        'press_ms': skill['press_ms'],
        'next_ready': 0.0  # Ready immediately
    })

def try_cast_skills(runtime, now, target_available, attack_phase):
    """Exact logic from app_gui.py"""
    if not runtime:
        return
    
    # Check ready skills
    ready_skills = [s for s in runtime if now >= s['next_ready']]
    if ready_skills:
        print(f"\n[Skills] Ready skills: {[s['name'] for s in ready_skills]}")
        print(f"         target_available={target_available}, attack_phase={attack_phase}")
    
    for skill in runtime:
        if now < skill['next_ready']:
            continue
        
        skill_type = skill.get('type', 'attack')
        
        # ⭐ THIS IS THE KEY LOGIC ⭐
        if skill_type == 'attack' and not (attack_phase and target_available):
            print(f"  ⊗ Skip {skill['name']} (attack skill needs attack_phase=True AND target=True)")
            continue
        
        if skill_type == 'buff' and attack_phase:
            pass  # Buffs can cast anytime
        
        # Cast skill
        try:
            print(f"  → Casting {skill['name']} (key={skill['key']}, press={skill['press_ms']}ms)")
            tap(skill['key'], skill['press_ms'])
            print(f"  ✓ Cast successful!")
            
            # Update cooldown
            skill['next_ready'] = time.time() + skill['cooldown']
            
            # Wait for cast time
            cast_time = skill['press_ms'] / 1000.0
            sleep_time = min(cast_time, 0.5)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"  ✗ Cast failed: {e}")

print("\n" + "=" * 70)
print("TEST SCENARIO 1: SEARCH MODE (chỉ buff)")
print("=" * 70)
print("Mô phỏng: Đang tìm monster, chưa có target")
print()

for i in range(3):
    print(f"\n--- Search Cycle {i+1}/3 ---")
    now = time.time()
    
    # Search mode: attack_phase=False, no target
    try_cast_skills(skill_runtime, now, target_available=False, attack_phase=False)
    
    time.sleep(2)  # Wait between cycles

print("\n" + "=" * 70)
print("TEST SCENARIO 2: ATTACK MODE (attack + buff)")
print("=" * 70)
print("Mô phỏng: Đã tìm thấy monster, đang đánh")
print()

# Reset cooldowns for attack test
for skill in skill_runtime:
    skill['next_ready'] = 0.0

for i in range(3):
    print(f"\n--- Attack Cycle {i+1}/3 ---")
    now = time.time()
    
    # Attack mode: attack_phase=True, target available
    try_cast_skills(skill_runtime, now, target_available=True, attack_phase=True)
    
    time.sleep(2)  # Wait between cycles

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
print("\n📊 EXPECTED RESULTS:")
print()
print("SEARCH MODE (Scenario 1):")
print("  ✓ Should cast: Regeneration (buff)")
print("  ⊗ Should skip: Dark Explosion, Bone Javelin, Skull Shooter (attack needs target)")
print()
print("ATTACK MODE (Scenario 2):")
print("  ✓ Should cast: Dark Explosion, Bone Javelin, Skull Shooter (attack with target)")
print("  ✓ Should cast: Regeneration (buff anytime)")
print()
print("\n❓ WHAT DID YOU SEE IN GAME?")
print()
print("Case A: Chỉ thấy skill 4 (Regeneration) cast trong cả 2 scenario")
print("  → Attack skills (1, 2, 3) không được cast dù đã đúng logic")
print("  → Vấn đề: Game window không focus hoặc anti-cheat")
print()
print("Case B: Scenario 1 chỉ cast skill 4, Scenario 2 cast tất cả")
print("  → ✅ ĐÚNG! Logic hoạt động hoàn hảo")
print("  → Vấn đề trong app chính: Template matching không detect monster")
print()
print("Case C: Không thấy skill nào cast cả")
print("  → Game window không focus")
print("  → Cần click vào game trước khi chạy test")
print()
print("\n💡 NEXT STEPS:")
print("Dựa vào kết quả test, cho tôi biết bạn thấy case nào?")
