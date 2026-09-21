# Task 4: Cấu trúc lại `SkillPanel` & Cải tiến Nút Bật/Tắt Combo

## Bối cảnh (Context)
Lắp ráp các thành phần đã tạo ở Task 1, 2, 3 vào file UI chính của bảng Kỹ năng. Đồng thời cải thiện luồng Bật/Tắt chế độ Auto Combo.

## Yêu cầu (Requirements)
1. Sửa file `ui/panels/skill_panel.py`.
2. Xóa các hàm `_build_combo_section` và `_build_buff_section` cũ.
3. Chèn `ComboRhythmBar` lên trên cùng.
4. Chèn 2 `SkillTimelineStrip` (1 cho Combo, 1 cho Buff).
5. Xóa Checkbox "Bật Auto Combo" ở Header. Xóa nút "Start/Stop Combo" cũ. Hợp nhất lại thành một Nút Toggle Button duy nhất (Nổi bật, lớn) đặt dưới cùng của Panel.
   - Trạng thái hoạt động: Xanh lá (`UI.ACCENT_GREEN_BG`).
   - Trạng thái chờ: Nền xám/mặc định (`UI.BG_SURFACE`).

## Rủi ro (Risks & Pitfalls)
- Phải đảm bảo tín hiệu (Event) từ nút Toggle này gọi đúng xuống các `EventBus` hoặc `Controller` hiện hữu để core logic HuntOrchestrator nhận được trạng thái. Đừng để vỡ state!
- Chiều cao (Height) của ResponsiveGrid có thể bị vỡ. Sử dụng nguyên tắc: "Pack top elements first, pin bottom action bars, and pack middle content last with fill=both, expand=True".

## Unit Tests Cần Thêm (Unit Tests to Add)
- Test UI headless: Mô phỏng click vào Toggle Button và kiểm tra biến trạng thái (state variable) có thực sự chuyển từ `False` sang `True` không.