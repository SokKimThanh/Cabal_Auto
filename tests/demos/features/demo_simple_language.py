"""
Demo: Test Ngôn Ngữ Đơn Giản Cho Timing Calculator
Chạy file này để xem so sánh Trước vs Sau
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from lib.features.timing.calculator import calculate_timing

# Test data
skills = [
    {'name': 'Dark Explosion', 'cooldown': 1.9, 'cast_time': 1.7, 'type': 'attack'},
    {'name': 'Bone Javelin', 'cooldown': 2.4, 'cast_time': 1.5, 'type': 'attack'}
]

result = calculate_timing(10000, 500, skill_rotation=skills)

print("=" * 80)
print("PHẦN 1: XEM TRƯỚC CÀI ĐẶT (PREVIEW AFTER CALCULATE)")
print("=" * 80)
print()

# ❌ PHIÊN BẢN CŨ (Phức tạp)
print("❌ TRƯỚC ĐÂY (Dùng thuật ngữ kỹ thuật - KHÓ HIỂU):")
print("-" * 80)
print(f"""
📊 DỮ LIỆU ĐẦU VÀO:
  • Monster HP: {result.monster_hp:,.0f}
  • Damage/hit: {result.damage_per_hit:,.0f}
  • Attack Speed: {result.attacks_per_second:.2f} hits/s
  • Time/hit: {1.0/result.attacks_per_second:.2f}s

⏱️  TIMING CƠ BẢN:
  • attack_press_ms: {result.attack_press_ms} ms
    📐 Công thức: max(50, min(150, avg_cast_time * 0.1))
    💡 APS càng cao → nhấn phím càng nhanh
    
  • target_cycle_delay: {result.target_cycle_delay:.2f}s
    📐 Công thức: max(0.15, time_per_hit × 1.2)
    💡 Đợi lâu hơn 1 hit để tránh đổi target giữa chừng
""")

print("\n" + "=" * 80)
print()

# ✅ PHIÊN BẢN MỚI (Đơn giản)
print("✅ BÂY GIỜ (Ngôn ngữ trẻ em lớp 5 - DỄ HIỂU):")
print("-" * 80)
print(f"""
📋 CÁC CON SỐ SẼ ĐƯỢC LƯU VÀO MÁY:

📊 THÔNG TIN QUÁI VẬT:
  • Máu quái: {result.monster_hp:,.0f} HP
  • Sát thương 1 đòn: {result.damage_per_hit:,.0f}
  • Tốc độ đánh: {result.attacks_per_second:.2f} đòn/giây
  • Cần đánh: {result.hits_to_kill} đòn
  • Tổng thời gian: {result.estimated_kill_time_sec:.2f} giây

⏱️  CÁC SỐ QUAN TRỌNG:

1️⃣ Nhấn phím giữ bao lâu?
   → {result.attack_press_ms} mili-giây
   💡 Giống như bấm nút giữ rồi thả ra

2️⃣ Đổi quái sau bao lâu?
   → {result.target_cycle_delay:.2f} giây
   💡 Đợi lâu hơn 1 đòn đánh, tránh đổi lung tung

3️⃣ Tìm quái sau bao lâu?
   → {result.search_interval:.2f} giây
   💡 Tìm nhanh để phát hiện quái kịp thời

4️⃣ Đánh sau bao lâu?
   → {result.attack_interval:.2f} giây
   💡 Đánh nhanh hơn bình thường một chút
""")

print("\n" + "=" * 80)
print()
print("🤖 AUTO SẼ LÀM GÌ KHI CHẠY?")
print("-" * 80)
print(f"""
1️⃣ TÌM QUÁI (cứ {result.search_interval:.2f} giây tìm 1 lần):
   • Nhìn màn hình tìm hình quái vật
   • Thấy quái → chuyển sang bước 2

2️⃣ CHỌN QUÁI:
   • Bấm phím Z để chọn quái
   • Đợi {result.target_cycle_delay:.2f} giây
   • Không chọn quái khác khi đang đánh

3️⃣ BẮT ĐẦU ĐÁNH (đánh {result.hits_to_kill} đòn):
   • Bấm phím tấn công giữ {result.attack_press_ms} mili-giây
   • Thả phím ra
   • Đợi {result.attack_interval:.2f} giây
   • Lặp lại: Đánh → Chờ → Đánh → Chờ...
   • Dự kiến hết ~{result.estimated_kill_time_sec:.1f} giây

4️⃣ KIỂM TRA QUÁI:
   • Nếu không thấy quái quá {result.lost_timeout_sec:.2f} giây:
     ❌ Dừng đánh (quái chết hoặc mất rồi)
   • Nếu còn thấy quái:
     ✅ Đánh tiếp tối thiểu {result.attack_min_duration_sec:.2f} giây

5️⃣ QUÁI CHẾT RỒI:
   • Quay lại bước 1 (tìm quái mới)
   • Cứ thế lặp lại mãi mãi
""")

print("\n" + "=" * 80)
print()
print("=" * 80)
print("PHẦN 2: SAU KHI APPLY (CONFIRMATION BOX)")
print("=" * 80)
print()

# ❌ PHIÊN BẢN CŨ (Phức tạp)
print("❌ TRƯỚC ĐÂY (Nhiều code và thuật ngữ - KHÓ HIỂU):")
print("-" * 80)
print(f"""
⚡ QUÁ TRÌNH THỰC THI KHI CHẠY AUTO:

1. auto_hunt.py ĐỌC FILE hunt_config.json
   → Load các thông số timing vừa lưu

2. TÌM KIẾM QUÁI (mỗi {result.search_interval:.2f}s):
   → while True:
       template_matcher.locate_template()
       time.sleep({result.search_interval:.2f})

3. NHẤN PHÍM Z ĐỂ TARGET:
   → tap('z', {result.attack_press_ms})
   → time.sleep({result.target_cycle_delay:.2f})

4. TẤN CÔNG (mỗi {result.attack_interval:.2f}s):
   → tap(attack_key, {result.attack_press_ms})  # GIỮ PHÍM {result.attack_press_ms}ms
   → time.sleep({result.attack_interval:.2f})     # ĐỢI {result.attack_interval:.2f}s

────────────────────────────────────────
🔑 API GỌI THỰC TẾ:

  lib/system/win_input.py:
    def tap(key, press_ms):
        key_down(key)                    # ⬇️ NHẤN
        time.sleep(press_ms/1000.0)      # ⏱️ GIỮ
        key_up(key)                      # ⬆️ THẢ PHÍM

  Windows API:
    user32.SendInput(...)                # 🪟 WINDOWS
    → CABAL Game nhận input              # 🎮 GAME
""")

print("\n" + "=" * 80)
print()

# ✅ PHIÊN BẢN MỚI (Đơn giản)
print("✅ BÂY GIỜ (Giống kể chuyện - DỄ HIỂU):")
print("-" * 80)
print(f"""
============================================================
✅ ĐÃ LƯU VÀO MÁY TÍNH RỒI!
============================================================

📂 LƯU Ở ĐÂU: lib/data/hunt_config.json

🔧 CÁC SỐ ĐÃ LƯU:
  • Giữ phím: {result.attack_press_ms} mili-giây
  • Đợi đổi quái: {result.target_cycle_delay:.2f} giây
  • Tìm quái: mỗi {result.search_interval:.2f} giây
  • Đánh: mỗi {result.attack_interval:.2f} giây
  • Quái mất quá: {result.lost_timeout_sec:.2f} giây thì dừng
  • Đánh tối thiểu: {result.attack_min_duration_sec:.2f} giây

────────────────────────────────────────────────────────────
🤖 KHI BẤM NÚT CHẠY AUTO, NÓ SẼ LÀM GÌ?
────────────────────────────────────────────────────────────

BƯỚC 1: Đọc file hunt_config.json
  → Lấy các con số vừa lưu ra dùng

BƯỚC 2: Tìm quái (cứ {result.search_interval:.2f} giây tìm 1 lần)
  → Nhìn màn hình, tìm hình quái vật
  → Nếu thấy → chuyển sang BƯỚC 3

BƯỚC 3: Bấm phím Z chọn quái
  → Giữ phím Z trong {result.attack_press_ms} mili-giây
  → Đợi {result.target_cycle_delay:.2f} giây

BƯỚC 4: Bắt đầu đánh (đánh {result.hits_to_kill} đòn)
  → Bấm phím tấn công, giữ {result.attack_press_ms} mili-giây
  → Thả phím ra
  → Đợi {result.attack_interval:.2f} giây
  → Lặp lại khoảng {result.hits_to_kill} lần (tầm {result.estimated_kill_time_sec:.1f} giây)

BƯỚC 5: Kiểm tra quái còn không
  → Nếu không thấy quái quá {result.lost_timeout_sec:.2f} giây:
     ❌ Quái chết rồi! Dừng đánh
  → Nếu vẫn thấy quái:
     ✅ Đánh tiếp tối thiểu {result.attack_min_duration_sec:.2f} giây nữa

BƯỚC 6: Quái chết rồi, tìm quái mới
  → Quay lại BƯỚC 2
  → Cứ thế lặp đi lặp lại mãi mãi

────────────────────────────────────────────────────────────
🔑 MÁY TÍNH SẼ BẤM PHÍM NHƯ THẾ NÀO?
────────────────────────────────────────────────────────────

  1. Chương trình gọi hàm tap()
  2. Hàm tap() gọi key_down() → Nhấn phím xuống
  3. Đợi {result.attack_press_ms} mili-giây
  4. Gọi key_up() → Thả phím lên
  5. Windows gửi tín hiệu cho Game Cabal
  6. Game Cabal nhận được → Nhân vật đánh quái!

============================================================
✅ KẾT LUẬN: AUTO SẼ BẤM PHÍM THẬT!
   (Giống như bạn ngồi bấm, nhưng máy làm giúp)
============================================================
""")

print("\n" + "=" * 80)
print()
print("🎯 KẾT QUẢ:")
print("  ✅ Đã loại bỏ thuật ngữ kỹ thuật (attack_press_ms, APS, API)")
print("  ✅ Đã thay thế bằng câu hỏi đơn giản (Giữ phím bao lâu?)")
print("  ✅ Đã bỏ công thức toán (max, min, multiply)")
print("  ✅ Đã bỏ pseudocode (while True, time.sleep)")
print("  ✅ Dùng ngôn ngữ trẻ em lớp 5 (Bấm nút giữ rồi thả ra)")
print("=" * 80)
