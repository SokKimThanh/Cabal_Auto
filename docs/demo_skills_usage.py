"""
Demo: Hiển thị cách Auto sử dụng Attack Skills vs Buff Skills
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

print("=" * 80)
print("DEMO: AUTO SỬ DỤNG KỸ NĂNG NHƯ THẾ NÀO?")
print("=" * 80)
print()

# Giả lập config
skill_slots = [
    {
        "name": "Dark Explosion",
        "key": "1",
        "type": "attack",
        "cooldown": 1.9,
        "cast_time": 1.7
    },
    {
        "name": "Bone Javelin",
        "key": "2",
        "type": "attack",
        "cooldown": 2.4,
        "cast_time": 1.5
    },
    {
        "name": "Skull Shooter",
        "key": "3",
        "type": "attack",
        "cooldown": 2.2,
        "cast_time": 1.5
    },
    {
        "name": "Regeneration",
        "key": "4",
        "type": "buff",
        "cooldown": 2.2,
        "cast_time": 1.0
    }
]

# Phân loại skills
attack_skills = [s for s in skill_slots if s['type'] == 'attack']
buff_skills = [s for s in skill_slots if s['type'] == 'buff']

print("📋 CẤU HÌNH KỸ NĂNG:")
print("-" * 80)
for skill in skill_slots:
    icon = "⚔️" if skill['type'] == 'attack' else "🛡️"
    skill_type = "TẤN CÔNG (CHÍNH)" if skill['type'] == 'attack' else "PHỤ TRỢ (BUFF)"
    print(f"{icon} [{skill['key']}] {skill['name']:20s} - {skill_type}")
    print(f"    Cooldown: {skill['cooldown']}s | Cast Time: {skill['cast_time']}s")
print()

print("=" * 80)
print("⚔️  PHẦN 1: KỸ NĂNG TẤN CÔNG (ATTACK) - DÙNG ĐỂ ĐÁNH QUÁI")
print("=" * 80)
print()

print(f"Số lượng: {len(attack_skills)} skills")
print("-" * 80)
for i, skill in enumerate(attack_skills, 1):
    print(f"{i}. [{skill['key']}] {skill['name']}")
    print(f"   • Cooldown: {skill['cooldown']}s (đợi bấm lại)")
    print(f"   • Cast Time: {skill['cast_time']}s (thời gian ra chiêu)")
print()

# Tính toán rotation
total_cast_time = sum(s['cast_time'] for s in attack_skills)
rotation_cycle = total_cast_time
attacks_per_second = len(attack_skills) / rotation_cycle

print("🔄 CHU KỲ LUÂN PHIÊN:")
print("-" * 80)
print(f"Tổng Cast Time: {' + '.join(str(s['cast_time']) for s in attack_skills)} = {total_cast_time}s")
print(f"Rotation Cycle: {rotation_cycle:.2f} giây")
print(f"Attack Speed: {len(attack_skills)} skills / {rotation_cycle:.2f}s = {attacks_per_second:.2f} đòn/giây")
print()

print("⏱️  TIMELINE ĐÁNH QUÁI (10 giây đầu):")
print("-" * 80)
current_time = 0.0
skill_index = 0

events = []
for i in range(6):  # Simulate 6 attacks
    skill = attack_skills[skill_index % len(attack_skills)]
    events.append({
        'time': current_time,
        'action': f"Bấm [{skill['key']}] {skill['name']}",
        'duration': skill['cast_time'],
        'type': 'attack'
    })
    current_time += max(skill['cooldown'], skill['cast_time'])
    skill_index += 1

for event in events:
    if event['time'] > 10:
        break
    print(f"⏰ {event['time']:5.2f}s: ⚔️  {event['action']}")
    print(f"         → Giữ phím {event['duration']:.1f} giây, thả ra")

print()
print("💡 Kết luận:")
print("   • Auto sẽ LUÂN PHIÊN bấm skill 1 → 2 → 3 → 1 → 2 → 3...")
print("   • ĐỢI COOLDOWN trước khi bấm lại skill cũ")
print("   • Timing Calculator TÍNH DỰA TRÊN các skill này!")
print()

print("=" * 80)
print("🛡️  PHẦN 2: KỸ NĂNG PHỤ TRỢ (BUFF) - DÙNG ĐỂ HỖ TRỢ NHÂN VẬT")
print("=" * 80)
print()

print(f"Số lượng: {len(buff_skills)} skills")
print("-" * 80)
for i, skill in enumerate(buff_skills, 1):
    print(f"{i}. [{skill['key']}] {skill['name']}")
    print(f"   • Cooldown: {skill['cooldown']}s (bấm lại sau cooldown)")
    print(f"   • Cast Time: {skill['cast_time']}s (thời gian ra chiêu)")
print()

print("⏱️  TIMELINE BUFF (10 giây đầu):")
print("-" * 80)
if buff_skills:
    buff = buff_skills[0]
    buff_time = 0.0
    buff_count = 0
    while buff_time <= 10:
        print(f"⏰ {buff_time:5.2f}s: 🛡️  Bấm [{buff['key']}] {buff['name']}")
        print(f"         → Hồi máu/buff cho nhân vật")
        buff_time += buff['cooldown']
        buff_count += 1
else:
    print("(Không có buff skill)")
print()
print("💡 Kết luận:")
print("   • Auto sẽ bấm ĐỊNH KỲ (mỗi X giây 1 lần)")
print("   • KHÔNG LUÂN PHIÊN (chỉ bấm 1 phím)")
print("   • Timing Calculator KHÔNG TÍNH skill này!")
print()

print("=" * 80)
print("🎮 PHẦN 3: CÁCH 2 LOẠI SKILL HOẠT ĐỘNG CÙNG LÚC")
print("=" * 80)
print()

print("⏱️  TIMELINE TỔNG HỢP (10 giây đầu):")
print("-" * 80)

# Merge attack và buff events
all_events = []

# Add attack events
current_time = 0.0
skill_index = 0
for i in range(6):
    skill = attack_skills[skill_index % len(attack_skills)]
    all_events.append({
        'time': current_time,
        'action': f"⚔️  [{skill['key']}] {skill['name']} (đánh quái)",
        'type': 'attack'
    })
    current_time += max(skill['cooldown'], skill['cast_time'])
    skill_index += 1

# Add buff events
if buff_skills:
    buff = buff_skills[0]
    buff_time = 0.0
    while buff_time <= 10:
        all_events.append({
            'time': buff_time,
            'action': f"🛡️  [{buff['key']}] {buff['name']} (hồi máu)",
            'type': 'buff'
        })
        buff_time += buff['cooldown']

# Sort by time
all_events.sort(key=lambda x: x['time'])

# Print timeline
for event in all_events:
    if event['time'] > 10:
        break
    print(f"⏰ {event['time']:5.2f}s: {event['action']}")

print()
print("💡 KẾT LUẬN:")
print("-" * 80)
print("✅ Nhân vật sẽ:")
print("   • Tay phải: Đánh quái (skill 1, 2, 3 luân phiên)")
print("   • Tay trái: Tự hồi máu (skill 4 định kỳ)")
print()
print("✅ Timing Calculator:")
print("   • CHỈ TÍNH skill tấn công (1, 2, 3)")
print("   • KHÔNG TÍNH skill buff (4)")
print()
print("✅ Kết quả:")
print("   • attack_interval: Dựa vào cooldown của skill 1, 2, 3")
print("   • attack_press_ms: Dựa vào cast_time của skill 1, 2, 3")
print("   • Skill 4 chạy riêng, không ảnh hưởng timing đánh quái!")
print()

print("=" * 80)
print()
print("🎯 TÓM TẮT:")
print("-" * 80)
print(f"⚔️  Attack Skills ({len(attack_skills)}): [{', '.join(s['key'] for s in attack_skills)}]")
print(f"   → Luân phiên đánh quái")
print(f"   → Timing Calculator: ✅ CÓ TÍNH")
print()
print(f"🛡️  Buff Skills ({len(buff_skills)}): [{', '.join(s['key'] for s in buff_skills)}]")
print(f"   → Bấm định kỳ hỗ trợ")
print(f"   → Timing Calculator: ❌ KHÔNG TÍNH")
print()
print("🤖 Auto điều khiển 2 việc SONG SONG → Hiệu quả tối đa!")
print("=" * 80)
