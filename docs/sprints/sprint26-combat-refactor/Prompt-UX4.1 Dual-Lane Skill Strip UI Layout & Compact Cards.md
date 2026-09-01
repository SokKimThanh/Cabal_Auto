# Session Prompt UX4.1: Dual-Lane Skill Strip UI Layout & Compact Cards

Timebox: 20–25 minutes.
Priority: High – Establishes the visual dual-lane skill layout and eliminates legacy UI clutter.

---

## ⚠ Xác nhận trước khi bắt đầu: Quan hệ với Session CB3B

Session **CB3B** ("Redesign Skill Configuration & Dual-Lane Combo UI") đã xây một panel dual-lane rất giống panel này: cùng cấu trúc 4-6 card Combo Lane / 2-3 ô Buff Lane, cùng checkbox "Enable Auto Combo", cùng dropdown "Combo Start Key" mặc định `Alt+3`. Trước khi triển khai session này, cần xác nhận một trong hai trường hợp:

- **(a) Đây là bản thiết kế lại/thay thế** cho panel đã làm ở CB3B (VD: gộp lại thành một dải gọn duy nhất, xoá bỏ panel cũ) — nếu vậy, ghi rõ panel cũ từ CB3B sẽ bị loại bỏ khỏi UI, tránh tồn tại 2 bản UI cho cùng một chức năng.
- **(b) Đây là một panel hiển thị song song, riêng biệt** với panel CB3B (VD: một cái nằm trong tab Setup để cấu hình chi tiết, một cái là dải "quick view" gọn ngay trong màn hình Hunt) — nếu vậy, **bắt buộc** cả hai panel phải đọc/ghi vào cùng một nguồn trạng thái duy nhất:
  - Checkbox Auto Combo ở cả hai nơi phải bind vào cùng một `BooleanVar`/config key (`hunt_cfg["combo"]["enabled"]`), không tạo biến độc lập cho mỗi panel.
  - Dropdown Combo Start Key ở cả hai nơi phải đọc/ghi cùng một giá trị (`hunt_cfg["combo"]["combo_start_key"]`).
  - Thay đổi ở panel này phải phản ánh ngay sang panel kia (nếu cả hai đang hiển thị đồng thời, hoặc ít nhất đồng bộ khi chuyển view — theo cơ chế `on_view_shown` đã có ở UX2), tránh tình trạng bật Auto Combo ở nơi này nhưng nơi khác vẫn hiển thị tắt.

Ghi rõ lựa chọn (a) hoặc (b) trong code comment ở đầu module trước khi implement.

*(Lưu ý: Session này tập trung 100% vào tầng Giao diện / View. Toàn bộ logic Smart Routing, Validate trùng phím và Migration JSON sẽ được thực hiện ở Session UX4.2).*

## Objective
Xây dựng khung giao diện dải kỹ năng tại đáy Vùng B (kích thước chuẩn 1576 x 120 px) chia làm 2 làn độc lập: Làn Combo Chain (Hàng ngang phía trên) và Làn Buff Lane (Phía dưới). Loại bỏ sạch 6 nút "Xóa" text cũ, tích hợp các thẻ Compact Card có huy hiệu co giãn DPI, fallback hiển thị an toàn và bộ điều khiển Auto Combo.

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
  * **Fallback hiển thị:** Khi chưa chọn skill hoặc thiếu dữ liệu, hiển thị placeholder mặc định `⚡ --s | ⏳ --s` an toàn. Áp dụng fallback theo từng chỉ số riêng lẻ — nếu chỉ thiếu `cooldown` nhưng có `cast_time`, hiển thị `⚡ 1.2s | ⏳ --s` (không fallback toàn bộ card chỉ vì thiếu một field).

### 2. Bộ Điều Khiển Auto Combo & State Binding
- Checkbox: `[☑] Bật Auto Combo` (liên kết với `BooleanVar`, theo đúng nguồn trạng thái đã xác nhận ở mục "Xác nhận trước khi bắt đầu").
- Dropdown: `Phím Mở Combo` (Mặc định `Alt+3`, cùng nguồn dữ liệu với CB3B nếu cả hai panel cùng tồn tại).
- **Hành vi UI:** Khi checkbox Auto Combo bỏ tích, tự động vô hiệu hóa (`state="disabled"`) ô chọn phím mở combo; khi tích chọn, mở lại trạng thái (`state="normal"`).

### 3. Đa Ngôn Ngữ (i18n) & Chuẩn Bị Tooltip
- Đăng ký đầy đủ các key dịch song ngữ `vi`/`en` cho tiêu đề làn (Combo Lane / Buff Lane), nhãn Auto Combo và tooltip chỉ số trong namespace `skill_strip`.
- Mỗi thẻ Card được gắn sẵn đối tượng Tooltip để sẵn sàng hiển thị thông báo nghiệp vụ ở session sau. Trong session này, nội dung tooltip là placeholder tạm thời có ý nghĩa (VD: "Chi tiết sẽ cập nhật ở bản tiếp theo"), không để trống hoàn toàn, để tránh hiển thị tooltip rỗng gây khó hiểu cho người dùng.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_skill_strip_ui.py`)
- **Test Auto Combo State Toggle:** Thay đổi giá trị `BooleanVar` của checkbox Auto Combo → Assert combobox phím mở chuyển đổi chính xác giữa `normal` và `disabled`.
- **Test Placeholder Fallback (đầy đủ):** Khởi tạo thẻ card trống → Assert hiển thị `⚡ --s | ⏳ --s` mà không gây lỗi format string.
- (Added) **Test Placeholder Fallback (một phần):** Khởi tạo thẻ card chỉ có `cast_time`, thiếu `cooldown` → Assert hiển thị đúng `⚡ <cast>s | ⏳ --s`, không fallback nhầm cả hai chỉ số.
- **Test Dynamic i18n:** Đổi ngôn ngữ `vi` <-> `en` → Assert toàn bộ nhãn tiêu đề làn và checkbox cập nhật ngay lập tức.
- (Added) **Test Legacy Buttons Removed:** Duyệt toàn bộ cây widget của khu vực dải kỹ năng → Assert không còn widget nào mang text/style của 6 nút "Xóa" cũ.
- (Added, chỉ áp dụng nếu chọn phương án (b) ở trên) **Test Shared State Sync:** Nếu panel CB3B và panel này cùng tồn tại, thay đổi Auto Combo ở panel này → Assert `BooleanVar`/config đọc được ở panel CB3B phản ánh đúng giá trị mới (cùng nguồn dữ liệu, không lệch).

### 2. Visual & High-DPI Check
- Khởi động GUI: Xác nhận dải kỹ năng render ngay ngắn, không bị đè chữ hay tràn viền ở các mức DPI 100%, 125%, 150%, 175%, 200%.

---

## Session Boundary Gate
- **PASSED nếu:** Bố cục 2 làn hiển thị hoàn chỉnh, loại bỏ sạch 6 nút Xóa cũ (xác nhận qua test tự động), giao diện responsive mượt mà, quan hệ với panel CB3B đã được xác nhận rõ ràng (thay thế hoặc đồng bộ trạng thái), và vượt qua toàn bộ UI unit tests.
- **REVERTED nếu:** Vỡ layout ở DPI cao, phát sinh xung đột geometry manager, hoặc tạo ra trạng thái Auto Combo độc lập/lệch với panel CB3B (nếu cả hai cùng tồn tại).
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.