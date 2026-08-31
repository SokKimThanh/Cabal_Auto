# Session Prompt UX4.1: Dual-Lane Skill Strip UI Layout & Compact Cards

Timebox: 20–25 minutes.  
Priority: High – Establishes the visual dual-lane skill layout and eliminates legacy UI clutter.

---

## Objective
Xây dựng khung giao diện dải kỹ năng tại đáy Vùng B (kích thước chuẩn 1576 x 120 px) chia làm 2 làn độc lập: Làn Combo Chain (Hàng ngang phía trên) và Làn Buff Lane (Phía dưới). Loại bỏ sạch 6 nút "Xóa" text cũ, tích hợp các thẻ Compact Card có huy hiệu co giãn DPI, fallback hiển thị an toàn và bộ điều khiển Auto Combo.

*(Lưu ý: Session này tập trung 100% vào tầng Giao diện / View. Toàn bộ logic Smart Routing, Validate trùng phím và Migration JSON sẽ được thực hiện ở Session UX4.2).*

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (hoặc frame Quick Skill Strip trong `app_gui.py`)
- Modify: `lib/system/i18n.py`
- Reference: `lib/ui_style.py`

---

## Implementation Details

### 1. Bố Cục Dual-Lane & DPI Scaling Guard (1576 x 120 px)
- Khởi tạo container dải kỹ năng với viền phẳng `UIStyle.BORDER_COLOR` (1px).
- Phân chia 2 dải ngang độc lập:
  * **Làn A (Combo Chain):** 4–6 thẻ Compact Card xếp ngang, quản lý bằng `grid(row=0, column=i, sticky="ew")` với `weight=1`.
  * **Làn B (Buff Lane):** 2–3 ô Compact Card quản lý bằng `grid(row=1, column=i, sticky="ew")`.
- Thiết kế thẻ Compact Card Component:
  * Dropdown chọn Skill Name + Ô Entry gán phím (chiều cao chuẩn 32 px).
  * Huy hiệu chỉ số rút gọn chống tràn chữ: `⚡ <cast>s` (Cast Time) và `⏳ <cd>s` (Cooldown). Font chữ và padding tự co giãn theo `scale_factor` khi DPI từ 100% đến 200%.
  * **Fallback hiển thị:** Khi chưa chọn skill hoặc thiếu dữ liệu, hiển thị placeholder mặc định `⚡ --s | ⏳ --s` an toàn.

### 2. Bộ Điều Khiển Auto Combo & State Binding
- Checkbox: `[☑] Bật Auto Combo` (liên kết với `BooleanVar`).
- Dropdown: `Phím Mở Combo` (Mặc định `Alt+3`).
- **Hành vi UI:** Khi checkbox Auto Combo bỏ tích, tự động vô hiệu hóa (`state="disabled"`) ô chọn phím mở combo; khi tích chọn, mở lại trạng thái (`state="normal"`).

### 3. Đa Ngôn Ngữ (i18n) & Chuẩn Bị Tooltip
- Đăng ký đầy đủ các key dịch song ngữ `vi`/`en` cho tiêu đề làn (Combo Lane / Buff Lane), nhãn Auto Combo và tooltip chỉ số trong namespace `skill_strip`.
- Mỗi thẻ Card được gắn sẵn đối tượng Tooltip để sẵn sàng hiển thị thông báo nghiệp vụ ở session sau.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_skill_strip_ui.py`)
- **Test Auto Combo State Toggle:** Thay đổi giá trị `BooleanVar` của checkbox Auto Combo -> Assert combobox phím mở chuyển đổi chính xác giữa `normal` và `disabled`.
- **Test Placeholder Fallback:** Khởi tạo thẻ card trống -> Assert hiển thị `⚡ --s | ⏳ --s` mà không gây lỗi format string.
- **Test Dynamic i18n:** Đổi ngôn ngữ `vi` <-> `en` -> Assert toàn bộ nhãn tiêu đề làn và checkbox cập nhật ngay lập tức.

### 2. Visual & High-DPI Check
- Khởi động GUI: Xác nhận dải kỹ năng render ngay ngắn, không bị đè chữ hay tràn viền ở các mức DPI 100%, 125%, 150%, 175%, 200%.

---

## Session Boundary Gate
- **PASSED nếu:** Bố cục 2 làn hiển thị hoàn chỉnh, loại bỏ sạch 6 nút Xóa cũ, giao diện responsive mượt mà và vượt qua toàn bộ UI unit tests.
- **REVERTED nếu:** Vỡ layout ở DPI cao hoặc phát sinh xung đột geometry manager.
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.