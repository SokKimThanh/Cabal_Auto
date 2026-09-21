# Kế hoạch Thực thi Kỹ thuật: Cải tiến UX/UI Hệ thống Skill & Combo (Hunt Tab)

## 1. Mục tiêu Tổng quan
Triển khai các đề xuất cải tiến từ tài liệu `docs/proposals/UX_IMPROVEMENT_HUNT_SKILL_COMBO.md`. Trọng tâm là cải thiện UI, loại bỏ rác mã nguồn (Emoji hardcode), và tái cấu trúc Layout. Các giải pháp phải tuân thủ nghiêm ngặt nguyên tắc hiệu năng Tkinter và Sự chia tách trách nhiệm (Separation of Concerns).

## 2. Kiến trúc và Các File bị ảnh hưởng (Files to Modify)
- **Data & Controller:**
  - `ui/controllers/skill_panel_controller.py`: Bổ sung logic quản lý danh sách kỹ năng tuần tự thay vì gắn cứng vào lưới index.
  - `lib/ui/animation_manager.py`: (TẠO MỚI) Centralized Animation Controller xử lý nội suy cho toàn hệ thống UI.
- **UI Components & Panels:**
  - `ui/panels/skill_panel.py`: Cấu trúc lại toàn bộ layout, gỡ bỏ Checkbox cũ, tích hợp Button toggle. Thay toàn bộ Emoji.
  - `ui/panels/target_status_panel.py`: Áp dụng `font_mono`, gọi API từ AnimationManager để giảm giật thanh máu.
  - `ui/panels/skill_stats_panel.py`: Chuyển hiển thị Success Rate sang text bar, bắt buộc bind vào `SkillStatsUpdatedEvent`.
  - `ui/tabs/hunt_tab.py`: Đổi `ResponsiveGridBase` sang `ttk.PanedWindow`.

## 3. Các Class/Component Cần tạo mới (Classes to Create)
- `lib/ui/animation_manager.py` (`UIAnimationManager`): Quản lý vòng lặp nội suy duy nhất thay vì gọi `.after()` phân tán.
- `ui/components/skill_timeline_strip.py` (`SkillTimelineStrip`): Component thanh nằm ngang hỗ trợ Icon Kỹ năng.
- `ui/components/combo_rhythm_bar.py` (`ComboRhythmBar`): Component phản hồi thị giác Sweet Spot.
- `ui/components/hunt_status_ticker.py` (`HuntStatusTicker`): Component hứng Log lỗi từ Background.
- `ui/components/vision_snapshot_debugger.py` (`VisionSnapshotDebugger`): Component xem ảnh On-Demand của Camera thay vì bắt Live stream (gây memory thrashing).

## 4. Rủi ro Triển khai và Giải pháp (Rollout Risks)
- **Sai lệch Dữ liệu HP:** Việc dùng Tween/Animation cho thanh máu có thể tạo độ trễ đồ họa, khiến người dùng nhìn thấy số lượng máu sai lệch với thực tế. Mặc định con số HP (Text) phải nhảy tức thời (instant update), chỉ được làm mượt thanh Canvas.
- **Automation Test Breakdown:** Thay Checkbox bằng Toggle Button có thể làm vỡ toàn bộ các kịch bản Automation Test đang binding vào `BooleanVar` cũ. Phải giữ nguyên Data Structure.
- **Rhythm Bar CPU Overhead:** Thanh Combo Rhythm chạy liên tục gây rối mắt và làm nặng CPU (khi bot đang tự đánh). Cần thiết kế để có thể ẩn/tắt.
- **Phân mảnh Animation Loop:** Nếu mỗi component tự gọi `.after(16)`, Tkinter Main Loop sẽ bị tranh chấp dẫn đến giật lag. BẮT BUỘC dùng Centralized Animation Manager.
- **EventBus Overload:** Không truyền raw image/numpy array qua `EventBus` để tránh rò rỉ bộ nhớ. Component Snapshot lấy ảnh bằng Method Call Thread-Safe (Mutex Locked) trực tiếp từ Vision Engine để chống Race Condition.
- **Separation of Concerns (ROI Manager):** `Hunt Tab` chỉ cấu hình mục tiêu (Target). Mọi cấu hình liên quan đến hệ thống (System ROI: Minimap, Self Stats, Combo Bar) phải được tách sang `Setup Tab` hoặc Vision Manager.
- **Data Migration Crash:** Khi load config cũ, có thể xảy ra KeyError. Bắt buộc tạo Schema Validation Layer và sinh file backup (.bak) trước khi tiến hành migration để bảo vệ dữ liệu người dùng.

## 5. Tiêu chí Chấp nhận Hiệu năng (Performance Acceptance Criteria)
1. FPS của luồng Orchestrator không sụt quá 2ms khi các tính năng UI mới được bật.
2. Overhead CPU của toàn hệ thống khi chạy tính năng Snapshot Debugger không vượt quá 5%.
3. Không văng lỗi TclError khi tắt ứng dụng hoặc đóng popup.
4. Giao diện mượt mà, phân cấp Typography chuẩn bằng `UIStyleV2`.