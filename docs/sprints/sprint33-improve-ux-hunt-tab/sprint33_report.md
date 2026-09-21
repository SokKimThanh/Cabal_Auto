
## Nhiệm vụ hoàn thành: Cải tiến UX/UI Hunt Tab (Phase 1-4)

### Summary
Hoàn thành xuất sắc 4 Phase của Sprint 33 nhằm nâng cấp trải nghiệm người dùng trên Hunt Tab. Các thay đổi bao gồm việc tái cấu trúc layout, tích hợp Animation nội suy mượt mà, và xây dựng các Component chuyên biệt để tách biệt hiển thị với logic.

### Work Completed
- **Phase 1:** Xây dựng `UIAnimationManager` (Singleton) để quản lý một vòng lặp `.after(16)` duy nhất. Tái cấu trúc `SkillPanelController` để hỗ trợ mảng `skill_slots` động.
- **Phase 2:** Phát triển 4 UI Components độc lập: `ComboRhythmBar`, `SkillTimelineStrip`, `HuntStatusTicker`, và `VisionSnapshotDebugger`.
- **Phase 3:** Tích hợp các Component mới vào `SkillPanel`, `TargetStatusPanel`, và `SkillStatsPanel`. Chuyển đổi checkbox Auto Combo thành Button lớn. Áp dụng font monospace cho dữ liệu động.
- **Phase 4:** Tái cấu trúc `HuntTab` sử dụng `ttk.PanedWindow`. Tích hợp Quản lý vùng quét hệ thống (System ROI Manager) vào `SetupTab`. Loại bỏ emoji tĩnh và chuẩn hóa toàn bộ Icon bằng `create_icon_button`.

### Key Decisions
- Xóa bỏ luồng dữ liệu Raw Image thông qua EventBus trong hệ thống Vision Engine, thay vào đó sử dụng `get_snapshot` với `Mutex Lock` để chống tràn bộ nhớ (Memory Leak) khi sử dụng `VisionSnapshotDebugger`.
- Sử dụng phương pháp lưu trữ Atomic (ghi vào file `.tmp` rồi gọi `os.replace()`) khi cập nhật tọa độ System ROIs để chống hỏng file JSON cấu hình.

### Changes Made
- Tạo mới các file trong `lib/ui/animation_manager.py` và `ui/components/`.
- Cập nhật luồng logic UI trong các Panels: `SkillPanel`, `MonsterTargetPanel`, `TargetStatusPanel`, `SkillStatsPanel`.
- Cập nhật `VisionEngine` và `HuntOrchestrator` ở Background để không gửi payload ảnh lớn qua EventBus.
- Cập nhật `SetupTab` để có màn hình System ROI Manager.

### Issues / Risks
- Không ghi nhận rủi ro hồi quy với Animation do hệ thống đã tự động gỡ bỏ (Cancel/Override) các Frame không hợp lệ và kiểm tra an toàn vòng lặp Widget.

### Next Steps
- Cập nhật Migration với Pydantic (Sprint tiếp theo) cho cấu hình `hunt_cfg`.
