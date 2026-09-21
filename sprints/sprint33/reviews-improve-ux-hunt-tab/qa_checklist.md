# QA Checklist: Improve UX Hunt Tab (Sprint 33)

## Task 1: Refactor Controller
- [ ] Hàm `get_combo_sequence` và `get_buff_sequence` trả về list chuẩn xác?
- [ ] Migration logic (nếu có) không làm crash app khi đọc file config cũ?
- [ ] Unit test cho SkillPanelController đã passing?

## Task 2: ComboRhythmBar Component
- [ ] Nút Toggle Visibility có ẩn được Rhythm bar để giảm tải CPU khi bot đang auto không?
- [ ] Component không throw lỗi `_tkinter.TclError` khi destroy lúc đang chạy animation?
- [ ] Có kiểm tra `winfo_exists()` khi nhận tick từ `UIAnimationManager` không?
- [ ] Tỷ lệ tọa độ Sweet Spot chính xác là 0.78?

## Task 3: SkillTimelineStrip Component
- [ ] Timeline hỗ trợ cuộn (scroll), giới hạn tối đa 8 slot, có tính năng kéo thả (Reorder) và Undo không?
- [ ] Icon ảnh có bị mất (Garbage collected) do không giữ reference không? (Check: Phải giữ `self._images`).
- [ ] Sử dụng `tk.Canvas` cho từng ô để vẽ overlay cooldown đúng chưa?
- [ ] Thay đổi biến tỷ lệ cooldown có chặn vượt ranh giới (clamp between 0.0 and 1.0) không?

## Task 4: Rebuild SkillPanel
- [ ] Automation Test (hay các file gọi API cũ) có bị lỗi do đổi Checkbox thành Toggle Button không? (Check: Phải giữ nguyên cấu trúc BooleanVar).
- [ ] Layout không bị vỡ chiều cao? (Check: Áp dụng rule pack top, pin bottom, fill middle).
- [ ] Sự kiện Bật/Tắt Combo từ nút Toggle mới có truyền xuống đúng `EventBus` hoặc logic gốc thay vì bị kẹt lại ở UI không?
- [ ] Trạng thái khi mở lại tab có đồng bộ với State đang chạy ngầm của Bot không?

## Task 5: TargetStatus Animation & Fonts
- [ ] Bảng Stats vẫn giữ nguyên Treeview, tần suất làm mới <= 1s và số record <= 50 không?
- [ ] HP Text có nhảy dữ liệu ngay lập tức mà không bị delay theo animation của thanh Canvas không?
- [ ] Chữ số HP/MP có sử dụng Monospace Font (font_mono) chưa?
- [ ] Khi mục tiêu mất máu cực nhanh, animation Tween có bị queue lùi (chạy chậm hơn thực tế) không? (Check: Cập nhật biến target_width tức thời).
- [ ] Có crash `TclError` khi tắt panel lúc thanh máu đang animate không? (Check: `winfo_exists()`).
## Phụ lục QA Cập nhật
- [ ] Task 5: File `SkillStatsPanel` đã thực hiện gọi `EventBus.bind(SkillStatsUpdatedEvent)` và cập nhật được data động lên bảng chưa?
- [ ] Task 5: Hàm Tweening Animation của HP bar có đăng ký qua `UIAnimationManager` để bù lại khoảng thời gian trống 200ms của Scanner không?

## Task 6: HuntStatusTicker Component
- [ ] Component đã đăng ký `HuntStatusUpdatedEvent` và `HuntStateChangedEvent` chưa?
- [ ] Hàm update UI bên trong callback của EventBus có sử dụng `self.after(0, ...)` để đảm bảo Thread Safety chưa? (Cực kỳ quan trọng vì Orchestrator chạy ngầm).
- [ ] Có bị crash hoặc vỡ layout ở tab Hunt khi chèn thanh Ticker vào đáy không?

## Task 7: VisionSnapshotDebugger Component
- [ ] Ảnh raw frame nhận được có được resize trước khi nhét vào `Tk.PhotoImage` chưa?
- [ ] Tham chiếu ảnh `self.current_image = ImageTk.PhotoImage(image)` có được giữ lại (keep reference) để chống lỗi nhấp nháy / đen màn hình do Garbage Collector không?
- [ ] Bounding box và Confidence score (điểm tự tin) được vẽ có khớp tỷ lệ với ảnh đã resize không?

## Task 8: Multi-ROI Manager
- [ ] Giao diện (Panel/Popup) có hiển thị rõ ràng danh sách các loại ROI cần quét (Hunt Area, Combo, Minimap...) không?
- [ ] Tính năng Migration có hoạt động không? (Check: Dùng config cũ chỉ có key `region`, khi save lại có tự động đổi sang cấu trúc `rois: { "hunt_area": [...] }` không?).
- [ ] Trải nghiệm UX: Khi nhấn "Vẽ lại" 1 vùng cụ thể, màn hình có tự động thu nhỏ/làm mờ để hiển thị cửa sổ game (bằng `RegionSelector`) không?
- [ ] Có ngăn chặn việc bấm vẽ ROI khi Bot đang ở trạng thái Running không?

## Task 9: Standardize Icon System
- [ ] Không còn bất kỳ Emoji hardcoded (🔴, 🟢, 🎯, ➕) nào xuất hiện dạng raw text trong mã nguồn của Tab Hunt chưa?
- [ ] Tất cả các Button có sử dụng đúng `create_icon_button` và truyền `element_id` để đăng ký Registry không?
- [ ] Hình ảnh (Icons) có bị nhấp nháy hoặc biến mất (thành nền trắng/đen) khi hover chuột hoặc sau vài giây không? (Check: Phải giữ reference `.image = img`).
- [ ] Các đoạn logic cũ sử dụng `.config(text="✓")` để cập nhật trạng thái đã được đổi thành việc thay đổi Icon key chưa?

## Task 10: Layout and Typography Hierarchy
- [ ] Màn hình HuntTab đã cho phép kéo thả ranh giới giữa bên Trái (Setup) và bên Phải (Monitor) chưa? (Bằng PanedWindow).
- [ ] Khi thu hẹp tối đa một bên, layout có bị tràn ra ngoài màn hình không? (Check: Phải set `minsize` cho các Pane).
- [ ] Các tiêu đề (Title) của Panel có to và rõ ràng hơn các Text nội dung (Hierarchy) nhờ sử dụng `UIStyleV2.get_font("title", weight="bold")` chưa?

## Kiến trúc và Hiệu năng (Performance Thresholds)
- [ ] Tính năng Snapshot Debugger (Task 7) không làm tăng quá 5% CPU usage (Baseline Test: Core i5 Gen 8th, 8GB RAM) khi mở và không rò rỉ RAM khi refresh liên tục?
- [ ] Có sử dụng `UIAnimationManager` duy nhất thay cho việc khởi tạo nhiều vòng lặp `.after` độc lập không?
- [ ] `UIAnimationManager` có logic ghi đè (override/cancel) tiến trình Tweening cũ nếu một Event mới đè lên để tránh thanh HP bị chạy thụt lùi không?
- [ ] Tốc độ loop của Orchestrator (Hunt Thread) có bị drop quá 2ms (Baseline Test: Core i5 Gen 8th) khi các tính năng UI mới đang chạy không?
- [ ] Dữ liệu config cũ có được Validate, TẠO FILE BACKUP (.bak) và Migrate an toàn, chống mất cấu hình do `KeyError` không?

## Quản trị Nợ Kỹ thuật (Technical Debt Check)
- [ ] Code mới KHÔNG gọi trực tiếp `hunt_cfg.get()` trên lớp UI (View) mà thông qua Controller chưa?
- [ ] Đã hoàn toàn loại bỏ việc truyền object quá lớn (như raw frame Numpy) qua EventBus chưa?
- [ ] Không có bất kỳ vòng lặp đồ họa `self.after()` nào bị bỏ sót bên ngoài `UIAnimationManager` chứ?
