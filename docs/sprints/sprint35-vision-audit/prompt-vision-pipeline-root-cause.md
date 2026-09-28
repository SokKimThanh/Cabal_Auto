# Vision Pipeline & UI Components Root Cause Analysis

## Phần 1 - Hiện trạng
Hệ thống Vision Pipeline bao gồm chức năng ScreenCapture để thu thập ảnh liên tục từ game window thông qua `dxcam` hoặc `BitBlt`.

### Capture Flow:
- Dữ liệu thu thập từ `lib/system/screen_capture.py` -> `ScreenCapture.get_frame()` -> `lib/vision/monster_detector.py`.
- Các vùng xử lý (ROI): Dữ liệu được cắt thành các ROI (Region of Interest) cho Target Name, Target HP, Skill Cooldown.
- Output: Truyền về EventBus qua `HuntOrchestrator` (`lib/features/hunt/hunt_orchestrator.py`).
- Hiển thị (UI Panels): Các module đăng ký (bind) với EventBus để nhận `TargetHpUpdatedEvent`, `TargetStatusUpdatedEvent`, `TargetInfoUpdatedEvent`, `SceneMonstersDetectedEvent`.

## Phần 2 - Root Cause

### 1. Vision Scan và ROI Data Flow
**Triệu chứng:** Dữ liệu mục tiêu quét được nhưng `TargetStatusPanel` không phản ánh.
**Call Chain & Data Flow:**
1. `ScreenCapture.get_frame()` -> Frame `np.ndarray`.
2. `MonsterDetector._capture_frame()` lấy frame hiện tại (Dòng 436).
3. Truyền cho `VisionEngine.process_frame()` (Dòng 386).
4. `TargetNameReader.read_target_name` -> Xử lý qua OCR.
5. `TargetHPReader.read_hp` -> OCR cho HP.
6. `MonsterDetector` gộp vào `DetectionStats`.
7. `HuntOrchestrator` lắng nghe queue -> Dòng 396 kích hoạt `EventBus.trigger(TargetInfoUpdatedEvent(fmt, target_id=m_id, name=m_name, hp=str(m_hp)))`.
8. `TargetStatusPanel` bắt sự kiện qua `_on_target_info_updated` (Dòng 56).
**Nguyên nhân (Root Cause):** Dữ liệu truyền bị nghẽn ở lớp EventBus do cấu trúc data payload trong OCR/Vision result thay đổi liên tục, khiến các handler trong `TargetStatusPanel` không parse được và ngắt luồng. Mismatch này dẫn đến hiện tượng UI cập nhật rỗng.
**ROI Status:**
- Target Name ROI: Hoạt động. Trả data tốt.
- Target HP ROI: Hoạt động nhưng trả % bị sai do đọc font bị lỗi ở một số độ phân giải.
- Cooldown ROI: Trả dữ liệu nhưng không được sử dụng ở `TargetStatusPanel` (Bị bypass).

### 2. Lỗi hiển thị Debug Vision
**Triệu chứng:** Preview trong Debug Vision bị đơ, frame không update hoặc báo "No active frame".
**Nguyên nhân:** Khóa `snapshot_lock` ở `VisionEngine` có thể bị chiếm giữ lâu bởi process frame chạy nền khiến luồng UI bị block. Đồng thời Debug Vision chỉ lấy ảnh tĩnh `latest_frame` chứ không có pipeline trực tiếp. OCR result không được update kịp thời vào Snapshot.

### 3. Target Status Panel
**Triệu chứng:** Một số trường UI bị "dead bind".
**Nguyên nhân:** `TargetStatusPanel` bind nhiều event nhưng thiếu xử lý data clearing khi `ClearTargetUIEvent` xảy ra không hoàn toàn (còn field cũ bị kẹt trên màn hình).

### 4. Rotation Panel
**Call Chain:** `Scan Result → Rotation Logic → Rotation State → Rotation Panel`.
**Nguyên nhân:** Dữ liệu scan thời gian thực (cooldown từ `SkillCooldownDetector`) chưa thực sự ảnh hưởng trực tiếp tới logic tính toán rotation (chủ yếu tính toán tĩnh từ configuration). Các hàm như `_render_rotation_sequence` render từ configuration list thay vì vision state.

### 5. Class Panel và Skill Panel
**Nguyên nhân:** `SkillStatsPanel` (nghe `SkillStatsUpdatedEvent`) lấy dữ liệu từ `HuntOrchestrator` (Dòng 430). Một số field như cast time / cooldown lấy cấu hình tĩnh, không bind kết nối với OCR pipeline scan thực. Do đó panel này hiển thị thông tin lỗi thời (từ DB tĩnh thay vì vision).

## Phần 3 - Technical Debt
**1. tk.Button & ttk.Button còn sót lại:**
- `ui/dialogs/skill_edit_dialog.py`: tk.Button tại các dòng 162, 165
- `ui/mixins/button_state_mixin.py`: tk.Button tại các dòng 734, 737, 750, 753, 756
(Cần refactor sang `create_icon_button`)

**2. Hardcoded Text & i18n bypass:**
- Rất nhiều text cứng trong `ui/dialogs/build_edit_dialog.py` (vd: "Description:", "Upvotes:").
- Cứng trong `ui/dialogs/skill_edit_dialog.py` (vd: "Name (*):", "Icon X:").
- `ui/tabs/hunt_tab.py`: Hardcoded `Debug Vision` bypass (Dòng 139).
- `ui/views/icon_manager_frame.py` (vd: "Gắn (Map)", "Mục lục").
- `ui/views/scan_history_frame.py` (vd: "Class:").

**3. Dead Code ở Hunt Tab:**
- `ui/tabs/hunt_tab.py`: `def _build_ui(self)` (Dòng 52), `def _show_monster_context_menu` (Dòng 32), `def _select_all_monsters` (Dòng 45) hiện đều là dead code, logic thừa từ các version cũ chưa được dọn dẹp.

**4. Code Duplication:**
- `TargetNameReader` và `TargetHPReader` đang có chung nhiều logic tiền xử lý ảnh và OCR (cv2 crop, pytesseract config), cần abstract ra một lớp cơ sở.

## Phần 4 - Đề xuất sửa chữa
1. **Vision Pipeline:** Map chính xác cấu trúc `TargetInfoUpdatedEvent` từ `HuntOrchestrator` sang `TargetStatusPanel`. Abstract OpenCV logic chung.
2. **Debug Vision:** Sử dụng callback trực tiếp lấy frame từ `ScreenCapture` thay vì qua `snapshot_lock`.
3. **Rotation/Class/Skill Panels:** Cleanup dead logic, link dữ liệu realtime cooldown vào pipeline.
4. **Tab Hunt Cleanup:** Xoá các hàm context menu, "select_all_monsters".
5. **i18n & create_icon_button:** Refactor thay thế toàn bộ `tk.Button` được liệt kê sang `create_icon_button` và chuyển hardcoded texts vào key translations.

## Phần 5 - Kế hoạch thực thi
- **Batch 1 - Vision Pipeline Audit & Fix:** Dọn dẹp lỗi mismatch Event Data Structure trong `HuntOrchestrator` và các Vision Detectors. Abstract OCR logic.
- **Batch 2 - Debug Vision:** Viết lại luồng lấy ảnh trong `VisionSnapshotDebugger`.
- **Batch 3 - Target Status:** Đồng bộ Event Bus `TargetStatusPanel` và dọn các field UI chết.
- **Batch 4 - Rotation Panel:** Dọn các rendering logic chết ở `SkillRotationUI`.
- **Batch 5 - Class Panel:** Dọn code dư ở `ClassPanel` (nếu có).
- **Batch 6 - Skill Panel:** Refactor `SkillStatsPanel` nhận đúng data realtime.
- **Batch 7 - Tab Hunt Cleanup:** Xóa các callbacks context menu và "Select All".
- **Batch 8 - i18n Cleanup:** Khắc phục hardcoded string inline tại các Dialog và Tab.
- **Batch 9 - create_icon_button Cleanup:** Thay thế các trường hợp `tk.Button` đã phát hiện ở phần Technical Debt.

Tất cả các Batch sẽ được triển khai, build độc lập và commit riêng rẽ để đảm bảo khả năng Rollback an toàn.
