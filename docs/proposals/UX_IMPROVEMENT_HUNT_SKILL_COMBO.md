# Đề xuất cải tiến UX/UI cho Hệ thống Skill & Combo trong Tab Hunt

## 1. Tổng quan vấn đề hiện tại

Dựa trên việc phân tích mã nguồn (`ui/tabs/hunt_tab.py`, `ui/panels/skill_panel.py`, `ui/panels/target_status_panel.py`, `ui/panels/skill_stats_panel.py`) và giả lập luồng thao tác người dùng, có một số hạn chế về mặt UX/UI trong Tab Hunt hiện hành:

### 1.1. Luồng thiết lập và quản lý Skill (`SkillPanel`)
- **Bố cục dàn trải, lãng phí không gian:** Hiện tại, phần thiết lập combo/buff được chia thành lưới tĩnh (4 cards cho combo, 2 cards cho buff). Mỗi card chứa `Combobox` chọn skill, `Entry` cho phím tắt, và nhãn hiển thị thời gian hồi chiêu. Điều này khiến giao diện bị cố định, chiếm nhiều diện tích dọc và không linh hoạt cho các lớp nhân vật cần nhiều hoặc ít ô skill hơn.
- **Thao tác chọn Skill chưa tối ưu:** Việc người dùng phải chọn chiêu thức qua `ttk.Combobox` trên từng ô (card) không mang lại cảm giác tổng quan, đặc biệt là khi số lượng skill lớn. Việc quản lý thứ tự (rotation) không trực quan.
- **Nút điều khiển (Auto Combo):** Việc tách biệt Checkbox "Bật Auto Combo" trên header và Nút "Start Combo"/"Stop Combo" ở dưới cùng gây bối rối về luồng trạng thái (state).

### 1.2. Trực quan hóa tiến trình Combo và Thời gian (Timing)
- **Thiết hụt feedback thời gian thực:** Thuật toán `CabalComboDetector` bắt vạch sáng (hit-zone sweet spot) rất tốt, nhưng trên giao diện `SkillPanel` chỉ có một đèn báo đơn giản (`combo_indicator_dot` 🔴/🟢) và Text. Người dùng không thấy được tiến độ của chuỗi combo, nhịp độ đánh (rhythm), hay khi nào chiêu tiếp theo sẽ được tung ra.

### 1.3. Theo dõi trạng thái mục tiêu (`TargetStatusPanel`)
- Mặc dù sử dụng `EmptyState` và huy hiệu (Badge) khá tốt, việc trình bày thông tin HP/MP bằng Canvas vẽ tay tĩnh (không có animation chuyển trạng thái mượt) và không làm nổi bật được trạng thái "Đang bị tấn công" (trái ngược với "Chờ") làm mất đi cảm giác "action" của Tab Hunt.

### 1.4. Hiển thị Thống kê (`SkillStatsPanel`)
- **Quá nhiều thông tin dạng bảng:** Bảng `ttk.Treeview` hiển thị tĩnh các chỉ số (casts, last_cast, cooldown, success). Tuy nhiên, thông tin này nên được thiết kế dưới dạng biểu đồ hoặc thanh tiến trình mini (Mini progress bars) để người dùng có thể lướt nhanh hiệu suất thành công của combo.
- Tag màu (excellent, good, poor) hiện tại phụ thuộc trực tiếp vào màu text trên nền tối, đôi khi thiếu tương phản (contrast).

---

## 2. Mục tiêu cải tiến

1. **Trực quan hóa Chuỗi Skill (Visual Skill Rotation):** Biến lưới Combobox tĩnh thành một thanh (strip) hoặc trục thời gian (timeline) các kỹ năng có thể kéo thả (Drag & Drop) hoặc sắp xếp lại dễ dàng.
2. **Cải thiện Feedback khi Auto Combo:** Thêm thanh tiến trình trực quan (Visual Combo Bar) mô phỏng lại vạch combo trong game, giúp người dùng (đặc biệt là power user) biết được bot đang "hit" ở tỷ lệ nào của sweet spot.
3. **Đơn giản hóa Bố cục:** Gộp các nút điều khiển, đồng nhất trạng thái Auto Combo, tận dụng tối đa `ResponsiveGridBase` để UI tự động co giãn đẹp mắt.
4. **Chuẩn hóa Màu sắc và Typography:** Tuân thủ chặt chẽ `UIStyleV2`, sử dụng `FONT_MONO` cho các con số đếm (HP, Cooldown, Time) để tránh hiện tượng text bị giật (jitter) khi số nhảy liên tục.

---

## 3. Đề xuất thiết kế chi tiết (Luồng và Thành phần)

### 3.1. Thiết kế lại `SkillPanel` (Active Skills)
- **Chuyển từ Lưới Card sang dạng "Timeline Strip":**
  - Thay vì 4 combo box to, hãy sử dụng một thanh ngang (horizontal scrollable frame hoặc danh sách nhỏ gọn) hiển thị các Icon kỹ năng theo thứ tự xuất chiêu.
  - Dưới mỗi Icon là phím tắt (Hotkey).
  - **Tương tác:** Nhấp vào một ô (slot) trống sẽ mở ra một popup hoặc menu dạng lưới (grid menu) tất cả các kỹ năng của Class để chọn nhanh (như dạng bảng ngọc), thay vì một Combobox kéo dài.
- **Tách biệt Combo và Buff:**
  - Giữ hai lane riêng biệt nhưng làm cho chúng nhỏ gọn lại. Sử dụng Icon thay cho chữ (Text) càng nhiều càng tốt.
- **Tích hợp "Combo Rhythm Bar":**
  - Ngay phía trên dải Skill, thêm một Canvas ngang mỏng. Khi "Auto Combo" hoạt động, một vạch sáng (indicator) sẽ chạy từ trái sang phải, điểm "Sweet Spot" (hit-zone) được tô màu `UI.ACCENT_AMBER`. Khi bot trigger combo, sẽ lóe sáng để cung cấp phản hồi (feedback) trực quan rằng hệ thống `CabalComboDetector` đang hoạt động tốt.

### 3.2. Cải thiện Điều khiển Auto Combo (Control Flow)
- **Hợp nhất Nút Bật/Tắt:** Loại bỏ Checkbox "Bật Auto Combo" ở header. Đưa toàn bộ việc kiểm soát thành một Nút lớn (Action Button) ở góc hoặc phía dưới cùng của `SkillPanel` với thiết kế dạng công tắc (Toggle Button).
  - *Trạng thái Off:* Nền `UI.BG_SURFACE`, Chữ "Bật Auto Combo".
  - *Trạng thái On:* Nền `UI.ACCENT_GREEN_BG`, viền sáng, Chữ "Đang chạy Combo", kèm Icon động hoặc màu thay đổi.

### 3.3. Tối ưu hóa `TargetStatusPanel`
- **Animation cho Thanh Máu (HP/MP Bar):**
  - Hiện tại Canvas đang cập nhật tọa độ `hp_fill_rect` ngay lập tức. Nên thêm một logic làm mượt (tween/easing) trong hàm `_on_target_hp_updated` để thanh máu tụt dần thay vì giật cục.
- **Cải thiện Typography số liệu:**
  - Đảm bảo các nhãn HP/MP, Level, Defense sử dụng tuân thủ biến `self.font_mono` của `UIStyleV2` để giữ số có độ rộng cố định (monospaced).
- **Trạng thái (Alert/State):**
  - Tận dụng màu `UI.COLOR_DANGER` chớp nháy viền khi mục tiêu còn dưới 20% máu, tạo cảm giác kịch tính.

### 3.4. Cải tiến `SkillStatsPanel` (Performance)
- **Thêm Cột Visual Success Rate:**
  - Bỏ cột số Text "%", thay bằng một thanh tiến trình mini (Mini Bar) ngay trong cột của `Treeview` (GIỮ NGUYÊN cấu trúc `Treeview` để đảm bảo hiệu năng, sử dụng font mono và ký tự unicode block để vẽ).
- **Làm nổi bật Skill lỗi:**
  - Những skill có cooldown bị lỡ hoặc hụt combo nhiều sẽ được làm nổi bật với màu `UI.TEXT_DANGER` hoặc cảnh báo "⚠️" để người dùng biết cần phải tinh chỉnh lại phím tắt hoặc timing cho chiêu đó.

---

## 4. Kế hoạch triển khai (Roadmap)

1. **Giai đoạn 1: Nâng cấp Data Layer & Controller (Không phá vỡ UI)**
   - Cập nhật `SkillPanelController` để hỗ trợ việc truyền dữ liệu dạng mảng (list) cho Timeline Strip thay vì các Slot index cố định.
2. **Giai đoạn 2: Thay thế UI Component**
   - Viết component mới: `SkillTimelineStrip` (thay cho Grid Combo Box) và `ComboRhythmBar`.
   - Chèn các component này vào `ui/panels/skill_panel.py`. Đảm bảo các sự kiện (<<ComboboxSelected>>) được chuyển đổi tương đương sang click event.
3. **Giai đoạn 3: Tối ưu Hóa Visuals (Fonts, Colors)**
   - Áp dụng `font_mono` cho mọi UI hiển thị con số thời gian thực (`SkillStatsPanel`, `TargetStatusPanel`).
   - Thêm Easing animation cho Canvas HP/MP.
4. **Giai đoạn 4: QA & Feedback**
   - Giả lập luồng `manual_skill_rotation_ui.py` để kiểm tra độ trễ (lag) của UI khi ComboRhythmBar hoạt động với tần số cao (mỗi 4ms từ Detector). Tối ưu hóa bằng cách giới hạn FPS render của UI (ví dụ 30fps) tách biệt với luồng logic chạy ngầm (background logic).

---

*Tài liệu này là tiền đề định hướng cho việc refactor lại mã UI của module tab săn (hunt tab), tập trung giải quyết bài toán rối rắm về thị giác và thiếu thông tin thời gian thực.*