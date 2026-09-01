# Session Prompt UX4.1: Dual-Lane Skill Strip UI Layout & Compact Cards

Timebox: 20–25 minutes.
Priority: High – Establishes the visual dual-lane skill layout and eliminates legacy UI clutter.

---

## ⚠ Cần xác nhận trước khi code: quan hệ với CB3B
Session này trùng lặp đáng kể về phạm vi với **CB3B (Redesign Skill Configuration & Dual-Lane Combo UI)** — cả hai đều dựng layout 2 làn (Combo Chain / Buff Lane), Compact Card (dropdown skill + key entry + badge cast/cooldown), checkbox Auto Combo + dropdown phím mở combo, và cùng sửa `ui/tabs/hunt_tab.py`. Trước khi bắt đầu, xác nhận một trong hai trường hợp:
- **(a)** UX4.1 + UX4.2 là bản viết lại/thay thế phần UI đã làm ở CB3B (tách rõ View và Logic hơn) — khi đó CB3B's dual-lane UI code nên được gỡ bỏ/hợp nhất, tránh tồn tại song song 2 implementation cùng quản lý dữ liệu skill.
- **(b)** Đây là hai vùng UI khác nhau thực sự (VD: CB3B là panel cấu hình skill đầy đủ ở đâu đó, UX4.1 là dải "Quick Skill Strip" gọn ở đáy Vùng B theo layout đã dựng ở UX2) — khi đó cần đảm bảo cả hai UI cùng đọc/ghi chung một nguồn dữ liệu (`hunt_cfg["skill_slots"]`/`buff_slots` theo CB3B) để không desync.
Nếu không chốt được điều này trước khi code, rủi ro là hai bộ UI cùng sửa cùng một dữ liệu theo hai đường khác nhau.

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
  * **Làn A (Combo Chain):** hiển thị mặc định 4–6 thẻ Compact Card xếp ngang, quản lý bằng `grid(row=0, column=i, sticky="ew")` với `weight=1`. Đây là số lượng hiển thị gợi ý ban đầu, **không phải giới hạn cứng** — nếu dữ liệu skill (khi UX4.2 wiring vào) có nhiều hơn 6 mục, làn này cần hỗ trợ scroll ngang thay vì cắt bớt.
  * **Làn B (Buff Lane):** 2–3 ô Compact Card quản lý bằng `grid(row=1, column=i, sticky="ew")`, cùng nguyên tắc không giới hạn cứng như trên.
- Thiết kế thẻ Compact Card Component:
  * Dropdown chọn Skill Name + Ô Entry gán phím (chiều cao chuẩn 32 px). Trong phạm vi session này (UI-only), dropdown lấy danh sách skill từ một nguồn tĩnh/passthrough đơn giản (VD: toàn bộ skill catalog hiện có, không lọc, không "thông minh") chỉ để có dữ liệu render và test — logic chọn lọc/gợi ý thông minh thuộc UX4.2, không cài ở đây.
  * Huy hiệu chỉ số rút gọn chống tràn chữ: `⚡ <cast>s` (Cast Time) và `⏳ <cd>s` (Cooldown). Font chữ và padding tự co giãn theo `scale_factor` khi DPI từ 100% đến 200%.
  * **Fallback hiển thị:** Card luôn hiển thị placeholder mặc định `⚡ --s | ⏳ --s`, kể cả khi người dùng đã chọn một skill trong dropdown — vì việc tra cứu cast/cooldown thật từ dữ liệu skill thuộc phạm vi UX4.2 (Smart Routing), session này không thực hiện lookup, tránh lấn phạm vi và tránh hiển thị số liệu tra cứu nửa vời/sai.

### 2. Bộ Điều Khiển Auto Combo & State Binding
- Checkbox: `[☑] Bật Auto Combo` (liên kết với `BooleanVar`).
- Dropdown: `Phím Mở Combo` (Mặc định `Alt+3`).
- **Hành vi UI:** Khi checkbox Auto Combo bỏ tích, tự động vô hiệu hóa (`state="disabled"`) ô chọn phím mở combo; khi tích chọn, mở lại trạng thái (`state="normal"`).
  * **Giữ nguyên giá trị đã chọn khi disable**: việc chuyển `state="disabled"` chỉ được đổi thuộc tính trạng thái của widget, tuyệt đối không xóa/reset giá trị đang hiển thị trong Combobox. Khi người dùng tích lại checkbox, phím mở combo đã chọn trước đó phải còn nguyên.

### 3. Đa Ngôn Ngữ (i18n) & Chuẩn Bị Tooltip
- Đăng ký đầy đủ các key dịch song ngữ `vi`/`en` cho tiêu đề làn (Combo Lane / Buff Lane), nhãn Auto Combo và tooltip chỉ số trong namespace `skill_strip`.
- Mỗi thẻ Card được gắn sẵn đối tượng Tooltip để sẵn sàng hiển thị thông báo nghiệp vụ ở session sau.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_skill_strip_ui.py`)
- **Test Auto Combo State Toggle:** Thay đổi giá trị `BooleanVar` của checkbox Auto Combo → Assert combobox phím mở chuyển đổi chính xác giữa `normal` và `disabled`, và giá trị đang chọn không bị xóa khi chuyển qua lại 2 trạng thái.
- **Test Placeholder Fallback:** Khởi tạo thẻ card trống, và cả trường hợp đã chọn một skill trong dropdown → Assert cả hai trường hợp đều hiển thị `⚡ --s | ⏳ --s` (chưa lookup dữ liệu thật) mà không gây lỗi format string.
- **Test Dynamic i18n:** Đổi ngôn ngữ `vi` <-> `en` → Assert toàn bộ nhãn tiêu đề làn và checkbox cập nhật ngay lập tức.
- (Added) **Test Legacy Cleanup:** Duyệt cây widget của khu vực skill strip sau khi render → Assert không còn bất kỳ nút nào mang text/tag tương ứng 6 nút "Xóa" cũ.
- (Added) **Test Lane Overflow:** Nạp một danh sách skill giả lập nhiều hơn 6 mục vào Làn A → Assert layout chuyển sang scroll ngang thay vì cắt bớt hoặc tràn khung.

### 2. Visual & High-DPI Check
- Khởi động GUI: Xác nhận dải kỹ năng render ngay ngắn, không bị đè chữ hay tràn viền ở các mức DPI 100%, 125%, 150%, 175%, 200%.

---

## Session Boundary Gate
- **PASSED nếu:** Bố cục 2 làn hiển thị hoàn chỉnh, loại bỏ sạch 6 nút Xóa cũ (verify bằng test), giao diện responsive mượt mà, card không lookup dữ liệu thật (đúng phạm vi UI-only), và vượt qua toàn bộ UI unit tests.
- **REVERTED nếu:** Vỡ layout ở DPI cao, phát sinh xung đột geometry manager, hoặc session vô tình cài logic thuộc phạm vi UX4.2 (lookup cast/cooldown thật, validate trùng phím).
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.