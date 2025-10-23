"""
Diagnostic test - Kiểm tra chi tiết từng phím
"""
import sys
import time
import pytest

sys.path.insert(0, 'E:/Cabal_Auto')

from lib.system.win_input import tap, key_down, key_up

# Mark as Windows-only due to win_input dependency
pytestmark = pytest.mark.windows

print("=" * 60)
print("KEY DIAGNOSTIC TEST - Kiểm tra chi tiết từng phím")
print("=" * 60)
print()
print("Test này sẽ:")
print("1. Test từng phím riêng lẻ với thời gian press khác nhau")
print("2. Test cả key_down/key_up riêng biệt")
print("3. Kiểm tra xem có conflict giữa các phím không")
print()
print("⚠️ Click vào game window ngay bây giờ!")
print()
input("Press ENTER to start...")

print("\n" + "=" * 60)
print("PHASE 1: Test phím ngắn (50ms) - Giống attack thường")
print("=" * 60)

for key in ['1', '2', '3', '4']:
    print(f"\n[Test] Phím '{key}' - Press 50ms (attack)")
    try:
        tap(key, 50)
        print(f"  ✓ Sent successfully")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    time.sleep(1)
    input("  Xem trong game có gì xảy ra? Press ENTER to continue...")

print("\n" + "=" * 60)
print("PHASE 2: Test phím dài (1500ms) - Giống skill cast")
print("=" * 60)

for key in ['1', '2', '3', '4']:
    print(f"\n[Test] Phím '{key}' - Press 1500ms (skill)")
    try:
        tap(key, 1500)
        print(f"  ✓ Sent successfully")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    time.sleep(1)
    input("  Xem trong game có gì xảy ra? Press ENTER to continue...")

print("\n" + "=" * 60)
print("PHASE 3: Test key_down + key_up riêng biệt")
print("=" * 60)

for key in ['1', '2', '3', '4']:
    print(f"\n[Test] Phím '{key}' - key_down, wait 1.5s, key_up")
    try:
        print(f"  → key_down('{key}')")
        key_down(key)
        print(f"  → waiting 1.5s...")
        time.sleep(1.5)
        print(f"  → key_up('{key}')")
        key_up(key)
        print(f"  ✓ Complete")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    time.sleep(1)
    input("  Xem trong game có gì xảy ra? Press ENTER to continue...")

print("\n" + "=" * 60)
print("PHASE 4: Test phím khác (không conflict)")
print("=" * 60)

test_keys = ['5', '6', 'q', 'e']
for key in test_keys:
    print(f"\n[Test] Phím '{key}' - Press 1500ms")
    try:
        tap(key, 1500)
        print(f"  ✓ Sent successfully")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    time.sleep(1)
    input("  Xem trong game có gì xảy ra? Press ENTER to continue...")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
print("\n📋 PHÂN TÍCH:")
print("• Nếu phím 4 (buff) hoạt động nhưng 1-3 không:")
print("  → Có thể game hoặc server ưu tiên phím gán cho skill (skill slot keys) hơn các phím khác")
print("  → Hoặc có anti-cheat chỉ block attack skills")
print("• Nếu phím 5, 6, q, e hoạt động:")
print("  → Phím 1-4 bị conflict trong game config")
print("• Nếu key_down/key_up hoạt động khác tap():")
print("  → Có vấn đề về timing trong tap() function")
