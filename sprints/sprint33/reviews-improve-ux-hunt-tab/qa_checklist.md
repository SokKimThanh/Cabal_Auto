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