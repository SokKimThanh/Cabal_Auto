# Task 4: Cấu trúc lại `SkillPanel` & Cải tiến Nút Bật/Tắt Combo

## Bối cảnh (Context)
Lắp ráp các thành phần đã tạo ở Task 1, 2, 3 vào file UI chính của bảng Kỹ năng. Đồng thời cải thiện luồng Bật/Tắt chế độ Auto Combo.

## Yêu cầu (Requirements)
6. ĐẢM BẢO giữ nguyên biến `self.widgets["auto_combo_var"] = tk.BooleanVar()` cũ vì nó có thể đang được Automation Test hoặc tab khác gọi tới. Toggle button mới chỉ map UI state vào biến này.
1. Sửa file `ui/panels/skill_panel.py`.
2. Xóa các hàm `_build_combo_section` và `_build_buff_section` cũ.
3. Chèn `ComboRhythmBar` lên trên cùng.
4. Chèn 2 `SkillTimelineStrip` (1 cho Combo, 1 cho Buff).
5. Đổi UI Checkbox thành Nút Toggle Button duy nhất đặt dưới cùng. LƯU Ý: Phải sử dụng lại cấu trúc biến `BooleanVar` của Checkbox cũ, Nút Toggle chỉ đóng vai trò là Wrapper UI, tuyệt đối KHÔNG ĐỔI TÊN API hoặc cấu trúc dữ liệu để tránh làm gãy kịch bản Automation Test.
   - Trạng thái hoạt động: Xanh lá (`UI.ACCENT_GREEN_BG`).
   - Trạng thái chờ: Nền xám/mặc định (`UI.BG_SURFACE`).

## Rủi ro (Risks & Pitfalls)
- Phải đảm bảo tín hiệu (Event) từ nút Toggle này gọi đúng xuống các `EventBus` hoặc `Controller` hiện hữu để core logic HuntOrchestrator nhận được trạng thái. Đừng để vỡ state!
- Chiều cao (Height) của ResponsiveGrid có thể bị vỡ. Sử dụng nguyên tắc: "Pack top elements first, pin bottom action bars, and pack middle content last with fill=both, expand=True".

## Unit Tests Cần Thêm (Unit Tests to Add)
- Test UI headless: Mô phỏng click vào Toggle Button và kiểm tra biến trạng thái (state variable) có thực sự chuyển từ `False` sang `True` không.
## Phụ lục (Important Note from Review):
- Chú ý: Hiện tại `btn_start_combo` và `btn_stop_combo` chỉ đang đổi Text UI mà KHÔNG đồng bộ với config ngầm. Checkbox cũ `auto_combo_var` cũng không được lưu!
- BẠN PHẢI đảm bảo nút Toggle mới khi được click sẽ ghi trạng thái vào `hunt_cfg` (ví dụ `cfg["combo"]["enabled"] = True/False`) hoặc gọi API cập nhật cấu hình của StateController, để `HuntOrchestrator` có thể đọc được!

## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Sửa Lỗi Binding Vô Danh:** Lỗi kỹ thuật tồn tại từ lâu là nút "Start/Stop" chỉ đổi UI mà không update trạng thái thực sự xuống backend. Bạn phải trả khoản nợ này bằng cách: Đảm bảo Toggle Button mới cập nhật đúng vào config chính xác là `hunt_cfg["combo"]["enabled"]` thông qua Controller, để Orchestrator có thể nhận biết được thao tác của người dùng.
- **i18n Hardcode:** Các trạng thái "Bật Auto Combo", "Đang chạy Combo" không được code cứng. Hãy dùng `self._t("...")` để đảm bảo hệ thống chuyển đổi ngôn ngữ hoạt động.
