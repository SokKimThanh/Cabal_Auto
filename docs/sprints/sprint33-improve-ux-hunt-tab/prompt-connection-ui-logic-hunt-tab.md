# Tài liệu Đặc tả và Phân tích Hệ thống Auto Hunt - MVC Architecture

## 1. Tổng quan Kiến trúc MVC Hiện tại và Vấn đề
Dựa trên khảo sát mã nguồn, ứng dụng hiện tại tuân theo mô hình MVC (Model-View-Controller) nhưng đang gặp vấn đề **tight coupling (phụ thuộc chặt chẽ)** giữa UI (View) và Logic Nghiệp vụ (Controllers/Services).

Ví dụ điển hình:
- `ComboRhythmBar` (UI component) được giả định là nhận phản hồi từ `CabalComboDetector` (Logic component) nhưng sự liên kết thực tế chưa rõ ràng, hoặc UI loop đang ảnh hưởng đến độ mượt của Logic ngầm.
- `SkillPanel` giữ lại các biến widget cũ (`combo_dropdowns`, `combo_hotkeys`) cho mục đích tương thích ngược (backward compatibility) và kiểm thử tự động, dẫn đến codebase phình to và rủi ro crash cao khi thay đổi.

## 2. Luồng Dữ liệu Tổng thể (The Auto Hunt Pipeline)
Hệ thống Auto Hunt của Cabal vận hành liên tục qua nhiều Pipeline:
1. **Scan (Chụp màn hình) → ROI (Region of Interest):** Trích xuất khung hình từ game.
2. **Nhận diện (Vision Engine):** `TargetBarDetector`, `TargetNameReader`, `TargetHpReader` phân tích khung hình để xác định mục tiêu, máu, mana.
3. **Target (Trạng thái Mục tiêu):** Cập nhật `TargetInfo` (Tên, Level, HP, MP) và báo về `HuntOrchestrator` và UI (`TargetStatusPanel`).
4. **Combat & Combo (Tấn công & Chuỗi kỹ năng):**
   - `HuntOrchestrator` quản lý luồng chiến đấu.
   - `SkillCasterService` quyết định kỹ năng tiếp theo.
   - `CabalComboDetector` chờ điểm sáng (vạch sáng) quét qua Sweet Spot (Hit-zone 0.78) để gửi tín hiệu (`do_press`) nhấn phím Z và skill.
5. **Thống kê (Analytics):** Thống kê số lần tung chiêu thành công, tính toán tỷ lệ, cooldown và phát EventBus.

## 3. Các Điểm Nghẽn (Bottlenecks) và Nợ Kỹ thuật
- **UI block Logic Thread:** Nếu UI render với tần số quá nhanh hoặc không an toàn (thread-unsafe), nó có thể khiến `HuntOrchestrator` bị trễ, làm lỡ nhịp Sweet Spot của `CabalComboDetector` (vốn đòi hỏi độ trễ nhỏ hơn 4ms).
- **Hardcode UI references:** Một số chỗ có thể dùng trực tiếp `MagicMock` hoặc `ttk` elements dẫn đến crash khi thay đổi thư viện hoặc cấu trúc thẻ (như `ttk.Treeview`).
- **Thiết kế Skill Panel bất cập:** Không thể kéo thả kỹ năng (Drag & Drop) vì luồng chọn Class và List Skill bị đứt gãy. Khi người dùng chọn Class, cần nạp toàn bộ Skill vào một danh sách khả dụng (Available Skills), từ đó mới kéo thả vào `SkillTimelineStrip` thay vì combobox rời rạc.
- **Auto-target Z:** Hệ thống phải tự tìm và khóa mục tiêu tiếp theo (nhấn phím Z) ngay khi mục tiêu hiện tại `HP <= 0`, nếu không nhân vật sẽ đứng im.

## 4. Đề xuất Refactor (Tách biệt UI và Logic)
- **Sử dụng EventBus hoàn toàn:** Mọi giao tiếp từ Logic → UI phải thông qua EventBus và được xử lý trong hàm `widget.after(0, ...)` để đảm bảo thread-safe.
- **Tối ưu FPS Render UI:** Giới hạn FPS của `ComboRhythmBar` (ví dụ 30-60 fps) độc lập với tần số 4ms của `CabalComboDetector`. Phát tín hiệu Hit thay vì truyền liên tục array.
- **Xây dựng lại luồng Drap & Drop Skill:**
  1. `SkillPresetService` cung cấp danh sách Available Skills theo Class.
  2. UI hiển thị dưới dạng icon/grid.
  3. Người dùng Drag icon từ Grid vào `SkillTimelineStrip`.
  4. Controller lắng nghe event Update và lưu xuống config.
- **Thanh tiến trình Mini trong Treeview:** Không dùng widget, sử dụng ký tự Block Unicode (`████░░░░`) kết hợp font Monospaced để vẽ biểu đồ mini.

## 5. Danh sách Test Cases cần thiết
- [ ] Test luồng chọn Class: Đổi class ID = 1 sang ID = 2 phải load lại toàn bộ danh sách Skill Available.
- [ ] Test kéo thả (Drag & Drop) từ Available Grid sang Timeline.
- [ ] Test re-order (Đảo vị trí) trên Timeline.
- [ ] Test Auto Target: Khi giả lập Event Target HP = 0, `HuntOrchestrator` phải phát sinh phím tắt 'Z' hoặc phím target được cấu hình.
- [ ] Test Combo Detector: Gửi mock frame có điểm sáng di chuyển, verify rằng phím skill được bấm chính xác tại sweet spot mà không crash giao diện.
