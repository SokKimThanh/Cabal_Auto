# QA Checklist: Improve UX Hunt Tab (Sprint 33)

## Task 1: Refactor Controller
- [ ] Hàm `get_combo_sequence` và `get_buff_sequence` trả về list chuẩn xác?
- [ ] Migration logic (nếu có) không làm crash app khi đọc file config cũ?
- [ ] Unit test cho SkillPanelController đã passing?

## Task 2: ComboRhythmBar Component
- [ ] Component không throw lỗi `_tkinter.TclError` khi destroy lúc đang chạy animation?
- [ ] Có kiểm tra `winfo_exists()` bên trong vòng lặp `.after()` không?
- [ ] Tỷ lệ tọa độ Sweet Spot chính xác là 0.78?

## Task 3: SkillTimelineStrip Component
- [ ] Icon ảnh có bị mất (Garbage collected) do không giữ reference không? (Check: Phải giữ `self._images`).
- [ ] Sử dụng `tk.Canvas` cho từng ô để vẽ overlay cooldown đúng chưa?
- [ ] Thay đổi biến tỷ lệ cooldown có chặn vượt ranh giới (clamp between 0.0 and 1.0) không?

## Task 4: Rebuild SkillPanel
- [ ] Layout không bị vỡ chiều cao? (Check: Áp dụng rule pack top, pin bottom, fill middle).
- [ ] Sự kiện Bật/Tắt Combo từ nút Toggle mới có truyền xuống đúng `EventBus` hoặc logic gốc thay vì bị kẹt lại ở UI không?
- [ ] Trạng thái khi mở lại tab có đồng bộ với State đang chạy ngầm của Bot không?

## Task 5: TargetStatus Animation & Fonts
- [ ] Chữ số HP/MP có sử dụng Monospace Font (font_mono) chưa?
- [ ] Khi mục tiêu mất máu cực nhanh, animation Tween có bị queue lùi (chạy chậm hơn thực tế) không? (Check: Cập nhật biến target_width tức thời).
- [ ] Có crash `TclError` khi tắt panel lúc thanh máu đang animate không? (Check: `winfo_exists()`).
## Phụ lục QA Cập nhật
- [ ] Task 5: File `SkillStatsPanel` đã thực hiện gọi `EventBus.bind(SkillStatsUpdatedEvent)` và cập nhật được data động lên bảng chưa?
- [ ] Task 5: Hàm Tweening Animation của HP bar có chạy ở 60 FPS (~`after(16)`) để bù lại khoảng thời gian trống 200ms của Scanner không?

## Task 6: HuntStatusTicker Component
- [ ] Component đã đăng ký `HuntStatusUpdatedEvent` và `HuntStateChangedEvent` chưa?
- [ ] Hàm update UI bên trong callback của EventBus có sử dụng `self.after(0, ...)` để đảm bảo Thread Safety chưa? (Cực kỳ quan trọng vì Orchestrator chạy ngầm).
- [ ] Có bị crash hoặc vỡ layout ở tab Hunt khi chèn thanh Ticker vào đáy không?

## Task 7: VisionLivePreview Component
- [ ] Component popup đã thực hiện Unbind (`EventBus.unbind`) ngay khi đóng cửa sổ (Sự kiện `WM_DELETE_WINDOW`) chưa? (Tránh rò rỉ bộ nhớ).
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
