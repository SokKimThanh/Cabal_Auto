"""
Test skill rotation independently - Kiểm tra skill rotation độc lập
"""
import sys
import time
import pytest

sys.path.insert(0, 'E:/Cabal_Auto')

from lib.system.win_input import tap

# Mark as Windows-only due to win_input dependency
pytestmark = pytest.mark.windows

print("=" * 60)
print("SKILL ROTATION TEST - Test bấm phím kỹ năng")
print("=" * 60)
print()
print("Chuẩn bị test bấm 4 phím: 1, 2, 3, 4")
print("Mỗi phím sẽ được bấm với thời gian khác nhau")
print()
print("⚠️ Lưu ý: Click vào game window trước khi chạy!")
print()
input("Press ENTER to start test in 5 seconds...")

print("\nStarting test in 5 seconds...")
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print("\n" + "=" * 60)
print("TESTING SKILLS")
print("=" * 60)

skills = [
    {"name": "Dark Explosion", "key": "1", "press_ms": 1700, "cooldown": 1.9},
    {"name": "Bone Javelin", "key": "2", "press_ms": 1500, "cooldown": 2.4},
    {"name": "Skull Shooter", "key": "3", "press_ms": 1500, "cooldown": 2.2},
    {"name": "Regeneration", "key": "4", "press_ms": 1000, "cooldown": 2.2},
]

try:
    for i in range(3):  # Test 3 lần
        print(f"\n--- Round {i+1} ---")
        for skill in skills:
            print(f"[{time.strftime('%H:%M:%S')}] Casting {skill['name']} (key={skill['key']}, press={skill['press_ms']}ms)")
            try:
                tap(skill['key'], skill['press_ms'])
                print(f"  ✓ Sent key '{skill['key']}' successfully")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
            
            # Wait for cooldown
            print(f"  Waiting {skill['cooldown']}s cooldown...")
            time.sleep(skill['cooldown'])
        
        print(f"\nCompleted round {i+1}/3")
        if i < 2:
            time.sleep(1)

except KeyboardInterrupt:
    print("\n\n⚠️ Test interrupted by user")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
print("\nNếu bạn KHÔNG thấy game bấm phím:")
print("1. ✅ Đảm bảo game window đang active (click vào game)")
print("2. ✅ Chạy script với quyền Administrator")
print("3. ✅ Kiểm tra game có anti-cheat block input không")
print("4. ✅ Thử bấm phím tay xem game có response không")
print("\nNếu bạn THẤY game bấm phím:")
print("✓ Skill rotation đang hoạt động đúng!")
print("✓ Bây giờ có thể dùng trong app chính")
