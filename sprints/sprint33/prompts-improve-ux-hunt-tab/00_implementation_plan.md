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
  - `ui/tabs/setup_tab.py`: Chứa giao diện quản lý các System ROI.

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
- **Data Migration Crash:** Khi load config cũ, có thể xảy ra KeyError. Bắt buộc dùng `pydantic` để tạo Schema Validation. Nếu quá trình Migration từ `region` sang `rois` bị lỗi, hệ thống phải tự động Restore lại file `.bak` vừa backup và log ra màn hình lỗi.

## 5. Tiêu chí Chấp nhận Hiệu năng (Performance Acceptance Criteria)
1. FPS của luồng Orchestrator không sụt quá 2ms khi các tính năng UI mới được bật.
2. Overhead CPU của toàn hệ thống khi chạy tính năng Snapshot Debugger không vượt quá 5%.
3. Không văng lỗi TclError khi tắt ứng dụng hoặc đóng popup.
4. Giao diện mượt mà, phân cấp Typography chuẩn bằng `UIStyleV2`.
## 6. Nợ kỹ thuật phải trả (Technical Debt)
Trong quá trình triển khai Sprint 33, lập trình viên cần chú ý giải quyết (hoặc không làm trầm trọng thêm) các khoản nợ kỹ thuật sau:
1. **Tight Coupling UI & Config (Khớp nối cứng):** Các Panel hiện tại đang chọc thẳng vào `app.state_controller.hunt_cfg.get(...)`. Cần refactor đưa các luồng đọc/ghi này vào bên trong Controller (ví dụ: `HuntConfigController`) để UI chỉ nhận dữ liệu sạch.
2. **Missing Schema Validation:** File `hunt_config.json` đang được đọc/ghi dưới dạng Dictionary thô (Raw Dict). Điều này gây rủi ro crash (KeyError) rất cao khi cấu trúc thay đổi (ví dụ chuyển `region` sang `rois`). Nợ kỹ thuật này cần được trả bằng cách áp dụng `Pydantic` hoặc `dataclasses` để map JSON thành Object an toàn ở các Sprint sau.
3. **EventBus Payload Bloat:** EventBus chỉ nên dùng để truyền tín hiệu (Signal), KHÔNG dùng để truyền tải dữ liệu lớn/thay đổi liên tục (như raw image frames). Bất kỳ luồng Event nào đang làm điều này cần được refactor thành Method Call trực tiếp.
4. **Phân mảnh Tkinter Event Loop:** Tất cả các lệnh `self.after()` phục vụ cho hoạt họa đồ họa rải rác ở các file cũ cần được thu gom lại và quản lý tập trung bởi `UIAnimationManager`.

## 7. Trình tự Triển khai (Execution Phases)
Để tránh tình trạng block chéo giữa các lập trình viên và quản trị rủi ro tích hợp, toàn bộ 11 Task của Sprint 33 PHẢI được thực hiện theo nhóm và thứ tự từ dưới lên trên (Bottom-Up) như sau:

### Phase 1: Core Foundation & Data Layer (Nền móng & Dữ liệu)
*Hoàn thành Phase này trước tiên vì các UI Component sẽ phụ thuộc vào các module này.*
- **Task 0:** Xây dựng `UIAnimationManager` (`00_task_ui_animation_manager.md`).
- **Task 1:** Refactor `SkillPanelController` để hỗ trợ mảng dữ liệu động (`01_task_refactor_controller.md`).

### Phase 2: Independent UI Components (Các Component Độc lập)
*Các lập trình viên có thể làm song song các Task này mà không đụng chạm file của nhau.*
- **Task 2:** Phát triển Component `ComboRhythmBar` (`02_task_combo_rhythm_bar.md`).
- **Task 3:** Phát triển Component `SkillTimelineStrip` (`03_task_skill_timeline_strip.md`).
- **Task 6:** Phát triển Component `HuntStatusTicker` (`06_task_system_status_bar.md`).
- **Task 7:** Phát triển Component `VisionSnapshotDebugger` (`07_task_roi_live_preview.md`).

### Phase 3: Tab Layout & Integration (Tích hợp & Ráp nối UI)
*Gắn các Component từ Phase 2 vào các Panel chính của Hunt Tab.*
- **Task 4:** Cấu trúc lại `SkillPanel` & Nút Toggle Combo (`04_task_rebuild_skill_panel.md`).
- **Task 5:** Áp dụng Animation & Event Bindings cho `TargetStatusPanel` và `SkillStatsPanel` (`05_task_target_status_animation.md`).

### Phase 4: Advanced Configuration & Polish (Cấu hình Nâng cao & Đánh bóng)
*Thực hiện các thay đổi vĩ mô về Layout và Migration Dữ liệu ở bước cuối cùng để tránh gây Crash trong quá trình dev.*
- **Task 8:** Tích hợp `Hunt Area Manager` và Cấu trúc lại System ROIs (`08_task_roi_managers.md`).
- **Task 9:** Chuẩn hóa Hệ thống Icon (Standardize Icon System) (`09_task_standardize_icons.md`).
- **Task 10:** Tái cấu trúc Layout (PanedWindow) và Phân cấp Typography (`10_task_layout_and_typography_hierarchy.md`).
