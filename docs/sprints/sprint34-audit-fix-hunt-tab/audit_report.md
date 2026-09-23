# Báo cáo Trạng thái Sprint 34: Audit Fix Hunt Tab

Dựa trên kết quả phân tích mã nguồn hiện tại so với kế hoạch đề ra trong Sprint 34, dưới đây là tình hình thực tế của ứng dụng về việc trả nợ kỹ thuật (Tech Debt) và sửa lỗi.

## 📊 Tổng quan Trạng thái Các Task

| Task ID | Tên Task | Trạng thái hiện tại | Ghi chú |
|---------|----------|---------------------|---------|
| 01 | Fix cascade Task 1 ↔ 4 | 🟡 Chưa hoàn thành | `get_combo_sequence` đã được sử dụng trong `ui/panels/skill_panel.py`, nhưng có vẻ vẫn cần kiểm tra lại toàn bộ luồng truyền dữ liệu từ controller vào `SkillTimelineStrip` (Finding #1). |
| 02 | Fix TclError fallback | 🟡 Chưa hoàn thành | `create_image` vẫn được gọi trong `ui/components/skill_timeline_strip.py` với tag "icon". Cần sửa để kiểm tra kiểu chuỗi (isinstance str) và dùng `create_text` làm fallback (Finding #4). |
| 03 | Sweep emoji standardize icon | 🔴 Rất nhiều lỗi | Vẫn còn tồn tại **rất nhiều** emoji cứng trong hệ thống: `ui/helpers/icons.json`, `ui/windows/library_manager.py`, `ui/panels/screen_state_panel.py`, `ui/icon_library.py`, v.v. (Finding #2 / Debt D6). |
| 04 | Verify integrate Task 6 | 🟢 Khả thi (Cần kiểm tra sâu) | `HuntStatusTicker` đã được import và khởi tạo trong `ui/views/hunt_workspace_frame.py`. Cần xác minh thêm về layout (pack) và độ ưu tiên event (Finding #3). |
| 05 | Fix vision fallback | 🔴 Lỗi hiển nhiên | Lệnh `self.canvas.delete("all")` và `self.canvas.delete("timeout_text")` vẫn còn tồn tại trong `ui/components/vision_snapshot_debugger.py`. Cần xóa lệnh "all" khi timeout (Finding #6). |
| 06 | Decouple D1 config | 🔴 Rất nhiều lỗi | `hunt_cfg` vẫn được truy cập và thiết lập trực tiếp rải rác khắp nơi ở các layer giao diện: `ui/controllers/overlay_controller.py`, `ui/windows/library_manager.py`, `ui/panels/skill_panel.py`, `ui/tabs/setup_tab.py` (Debt D1). |
| 07 | Cleanup D4 D6 | 🟢 Hoàn thành 1 phần | Không tìm thấy `_pulse_step` trong `ui/components/status_badge.py` (Tốt - Debt D4 có thể đã được giải quyết một phần). Tuy nhiên, hardcode tiếng Việt/Anh vẫn còn nhiều (Debt D6). |
| 08 | Fix MagicMock & backend i18n | 🟢 Hoàn thành 1 phần | Không tìm thấy `MagicMock` trong `lib/features/hunt/` (Tốt - Finding #5 có thể đã được sửa). Cần kiểm tra EventBus messages để xóa bỏ hoàn toàn hardcode text. |

## ⚠️ Nhận xét chung & Rủi ro

1. **Khối lượng nợ kỹ thuật vẫn còn lớn:** Các task tốn thời gian như Task 03 (Sweep emoji) và Task 06 (Decouple config) gần như chưa được bắt đầu hoặc mới xử lý được một phần rất nhỏ.
2. **Rủi ro Crash:** Task 02 (Fix TclError fallback) chưa hoàn thành, đồng nghĩa với việc ứng dụng vẫn có nguy cơ crash trên production nếu thiếu file ảnh.
3. **Lỗi UX/Spec:** Task 05 (Vision fallback) chưa xử lý, lệnh xóa canvas (`delete("all")`) vẫn còn, làm mất đi tính năng lưu ảnh lỗi theo yêu cầu gốc.

## 📝 Đề xuất Hành động Tiếp theo

- **Ưu tiên ngay lập tức:** Thực hiện Task 01, Task 02 và Task 05 để đảm bảo UI không hiển thị rỗng, không bị crash (TclError) và tuân thủ đúng spec thiết kế.
- **Dành thời gian tập trung:** Bắt đầu Task 03 và Task 06 (hai task nặng nhất) vì số lượng file bị ảnh hưởng là rất lớn, đặc biệt là `ui/windows/library_manager.py` và luồng truyền biến `hunt_cfg`.