# Kế hoạch Thực thi Kỹ thuật: Cải tiến UX/UI Hệ thống Skill & Combo (Hunt Tab)

## 1. Mục tiêu Tổng quan
Triển khai các đề xuất cải tiến từ tài liệu `docs/proposals/UX_IMPROVEMENT_HUNT_SKILL_COMBO.md`. Trọng tâm là chuyển đổi lưới Combobox tĩnh thành thanh tiến trình thời gian thực (Timeline Strip), thêm phản hồi thị giác (Combo Rhythm Bar), và làm mượt các hiển thị trạng thái mục tiêu (Target Status).

## 2. Kiến trúc và Các File bị ảnh hưởng (Files to Modify)
- **Data & Controller:**
  - `ui/controllers/skill_panel_controller.py`: Bổ sung logic quản lý danh sách kỹ năng tuần tự thay vì gắn cứng vào lưới index.
- **UI Components & Panels:**
  - `ui/panels/skill_panel.py`: Cấu trúc lại toàn bộ layout phần combo/buff; gỡ bỏ Checkbox cũ, thay thế bằng Action Button lớn.
  - `ui/panels/target_status_panel.py`: Cập nhật logic vẽ (draw) trên Canvas để thêm easing animation cho thanh HP/MP; áp dụng `font_mono`.
  - `ui/panels/skill_stats_panel.py`: Chuyển đổi hiển thị Text thành thanh tiến trình thu nhỏ (Mini Progress Bar) cho tỷ lệ thành công (Success Rate).
- **Styles:**
  - `lib/ui_style_v2.py`: Đảm bảo các định nghĩa màu cảnh báo (Warning/Danger) và font monospace đã sẵn sàng và được gọi đúng chuẩn.

## 3. Các Class/Component Cần tạo mới (Classes to Create)
- `ui/components/skill_timeline_strip.py` (`SkillTimelineStrip`): Component thanh nằm ngang quản lý giao diện các kỹ năng, hỗ trợ thao tác click để chọn/đổi kỹ năng thay vì Combobox.
- `ui/components/combo_rhythm_bar.py` (`ComboRhythmBar`): Component hiển thị thanh mô phỏng điểm "Sweet Spot" (hit-zone) của hệ thống combo, nhấp nháy khi có sự kiện trigger.

## 4. Rủi ro Triển khai (Rollout Risks)
- **Desync Trạng thái (State Desynchronization):** Khi thay đổi từ Checkbox sang Nút (Button) Bật/Tắt Combo, nếu không đồng bộ trạng thái kỹ lưỡng với `SkillRuntimeService` và `HuntOrchestrator`, có thể dẫn đến việc giao diện hiển thị Combo đang chạy nhưng bot thực tế đã dừng.
- **Hiệu năng UI (UI Thread Performance):** Việc thêm animation cho thanh máu (mỗi khung hình - frame) và thanh Combo Rhythm Bar (phản hồi với detector chạy mỗi 4ms) có thể gây quá tải vòng lặp sự kiện của Tkinter (event loop) nếu không được giới hạn tần số quét (throttle/debounce) ở mức ~30-60 FPS.
- **Mất khả năng tương thích ngược:** Việc thay đổi Controller có thể làm hỏng các bài test hiện hành (unit tests) mong đợi cấu trúc dữ liệu cũ (ví dụ 4 slots cho combo, 2 slots cho buff).

## 5. Tiêu chí Chấp nhận (Acceptance Criteria)
1. Giao diện `SkillPanel` hiển thị chuỗi kỹ năng dưới dạng thanh ngang gọn gàng, không còn sử dụng 4 Grid Card.
2. Có thanh `ComboRhythmBar` cung cấp phản hồi trực quan (sáng lên) khi chế độ Auto Combo hoạt động.
3. Thanh HP/MP của quái vật trên `TargetStatusPanel` chuyển động mượt mà (tweening) khi máu giảm, không giật cục.
4. Các con số (HP, MP, Cooldown) hoàn toàn sử dụng `font_mono` của `UIStyleV2`, không bị rung rinh (jitter) chữ khi thay đổi giá trị.
5. Toàn bộ các unit test hiện hữu liên quan đến Controller và UI phải passing (hoặc được cập nhật tương ứng).
### 6. Bổ sung quan trọng (System/Hunt Status Bar)
- **Vấn đề:** Hiện tại `HuntOrchestrator` liên tục bắn các event cực kỳ quan trọng như `HuntStatusUpdatedEvent` (báo lỗi quét, timeout, mất cửa sổ, v.v) nhưng giao diện UI không hề có component nào lắng nghe (bind) và hiển thị. Điều này làm người dùng bị mù thông tin khi ấn "Bắt đầu săn" mà bot không hoạt động.
- **Giải pháp:** Cần phát triển thêm một component `HuntStatusTicker` (hoặc `MiniLogPanel`) đặt ở dưới cùng của `HuntWorkspaceFrame`. Component này sẽ subscribe `HuntStatusUpdatedEvent` và hiển thị text chạy hoặc text log nhỏ để người dùng biết bot đang làm gì (VD: "Đang tìm cửa sổ...", "Không tìm thấy mục tiêu...", "Đang tấn công...").
- **Task bổ sung:** Task 6: Phát triển `HuntStatusTicker`.

### 7. Bổ sung quan trọng (Live Preview / Vision Debugger)
- **Vấn đề:** Hiện tại người dùng chọn Target Policy và vẽ Region nhưng khi Bot chạy, quá trình quét hoàn toàn chạy ngầm ("Blackbox"). Người dùng không biết Bot có bắt đúng điểm ảnh không, hoặc `Confidence Score` là bao nhiêu nếu quét trật.
- **Giải pháp:** Cần phát triển một tính năng "Live Preview" (Ảnh thu nhỏ màn hình game hiển thị bounding box của quái vật) để người dùng thấy rõ độ chính xác (Success rate của Scanner). Nó có thể là một nút nhấn "Debug Vision" bật lên một popup, hoặc tích hợp luôn vào góc của `HuntWorkspaceFrame`.
- **Task bổ sung:** Task 7: Phát triển cơ chế `VisionLivePreview` (Window/Overlay).

### 8. Bổ sung quan trọng (Multi-ROI Manager)
- **Vấn đề:** Ban đầu, chúng ta nghĩ chỉ cần 1 nút "Vẽ vùng quét" cho toàn bộ Tab Hunt. Tuy nhiên, kiến trúc Bot phức tạp đòi hỏi thu thập dữ liệu từ nhiều khu vực khác nhau (ROI Quái vật, ROI Thanh Combo, ROI Máu/Mana nhân vật, ROI Bản đồ). Các thông số này còn có thể được Bot "học" và lưu lại. Việc thiết kế 1 nút bấm chung chung là hoàn toàn không đáp ứng được yêu cầu phân luồng kết xuất (telemetry).
- **Giải pháp:** Xây dựng một "Multi-ROI Manager" (Trình quản lý Vùng quét đa năng). Đây sẽ là một danh sách hoặc các nút phân loại rõ ràng (Ví dụ: [Vẽ ROI Bãi Quái], [Vẽ ROI Combo], [Vẽ ROI Tọa Độ Bản Đồ]). Mỗi vùng được lưu trữ độc lập trong cấu hình để Bot sử dụng cho các luồng thuật toán tương ứng.
- **Task bổ sung:** Task 8: Phát triển bảng `Multi-ROI Manager`.

### 9. Bổ sung quan trọng (Standardize Icon System)
- **Vấn đề:** Các Panel bên trong Tab Hunt (đặc biệt là `MonsterTargetPanel`, `SkillPanel`, `TargetStatusPanel`) đang sử dụng rất nhiều Emoji tĩnh (hardcoded emojis như 🔴, 🟢, 🎯, ℹ️, ➕) và các Nút bấm (Button) thuần chữ (text-only) không đồng bộ với ngôn ngữ thiết kế chung của hệ thống.
- **Giải pháp:** Cần tái cấu trúc toàn bộ nút bấm ở Tab Hunt để sử dụng hàm `create_icon_button` từ `ui.components`. Các nhãn (Label) chứa Emoji cũng cần được thay bằng `create_icon_label` hoặc thông qua `IconHelper`. Đảm bảo tất cả component mới phải đăng ký mã Element ID vào Registry.
- **Task bổ sung:** Task 9: Chuẩn hóa hệ thống Icon cho Tab Hunt.
