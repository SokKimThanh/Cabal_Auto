# 00 Context: Audit Summary & Fix Plan (Sprint 34)

Tài liệu này cung cấp bối cảnh từ đợt kiểm toán Sprint 33 (Improve UX Hunt Tab), với mục đích định hướng cho 8 task fix trong Sprint 34.
**Lưu ý:** Độ dài file này luôn duy trì dưới 10KB. Toàn bộ nội dung dựa trên `audit-ux-hunt-tab.md`.

## 1. Tóm tắt điều hành (Bảng 11 task compact Sprint 33)

| Task | Tên | Trạng thái | Ghi chú chính |
|------|-----|------------|---------------|
| 0 | UIAnimationManager | ✅ DONE (100%) | Design xuất sắc, unit tests pass. |
| 1 | Refactor Controller | ✅ DONE (100%) | Methods đúng, nhưng chưa được gọi (lỗi cascade sang Task 4). |
| 2 | ComboRhythmBar | ✅ DONE (100%) | Hoàn chỉnh, test pass 5/5. |
| 3 | SkillTimelineStrip | 🟡 PARTIAL (87.5%)| Tốt, nhưng có TclError crash rủi ro khi fallback icon string. |
| 4 | Rebuild SkillPanel | 🟡 PARTIAL (83.3%)| **Bug Cascade:** Không gọi data từ Controller, UI render rỗng. |
| 5 | TargetStatus + SkillStats | 🟡 PARTIAL (83.3%)| Tốt nhưng hardcode i18n, không có unit test. |
| 6 | HuntStatusTicker | 🟡 PARTIAL (85%) | Tốt nhưng chứa hardcode emoji, cần verify integration. |
| 7 | VisionSnapshotDebugger | 🟡 PARTIAL (95%) | Đạt chuẩn, ngoại trừ 1 spec bug khi timeout xóa canvas. |
| 8 | Multi-ROI Manager | 🟡 PARTIAL (85%) | Data flow chuẩn (atomic, pydantic), vẫn còn hardcode text. |
| 9 | Standardize Icon | ❌ FAILED (15%) | **Lazy coding**, 20+ chỗ hardcode emoji trên toàn hệ thống. |
| 10 | Layout & Typography | 🟡 PARTIAL (85%) | Thiếu `minsize` cho PanedWindow gây rủi ro layout. |

## 2. 6 Findings Chính (Các vấn đề P0/P1)

1. **Cascade Task 1 ↔ Task 4:** Các phương thức lấy dữ liệu buff/combo không được gọi, dẫn đến Skill Timeline rỗng. Đây là nguyên nhân thất bại mục tiêu chính của Sprint 33.
2. **Task 9 Failed:** Vẫn tồn tại hơn 20 vị trí hardcode emoji trên UI và Backend dù hạ tầng `IconHelper` đã sẵn sàng.
3. **Verify Task 6 Integration:** Ticker Component hoàn chỉnh nhưng cần xác thực mối quan hệ render thực tế giữa `HuntWorkspaceFrame` và `HuntTab`.
4. **Task 3 TclError Crash:** Sử dụng string emoji với phương thức `create_image` khi fallback gây crash nếu máy thiếu icon png.
5. **MagicMock trên Production:** Code backend có phát hiện framework test (`isinstance(..., MagicMock)`), là một code smell nghiêm trọng.
6. **Task 7 Spec Bug:** Xử lý sai yêu cầu khi `VisionSnapshotDebugger` bị timeout (xóa thay vì giữ lại ảnh cũ).

## 3. Debt Checklist D1-D6

| Nợ Kỹ Thuật | Trạng thái | Đánh giá & Bằng chứng |
|-------------|------------|-----------------------|
| **D1** (Coupling UI-Config)| ❌ CHƯA TRẢ | `hunt_cfg.get(...)` bị rải rác ở UI thay vì qua Controller. |
| **D2** (Schema Validation) | ✅ ĐÃ TRẢ | Áp dụng Pydantic trong `hunt_config.py`. |
| **D3** (EventBus Bloat) | ✅ ĐÃ TRẢ | Payload sạch. |
| **D4** (Tkinter Event Loop)| ❌ CHƯA TRẢ | Phân mảnh các hàm `_pulse_step`, `after` thay vì dùng AnimationManager. |
| **D5** (Bounding Box Scale)| ✅ ĐÃ TRẢ | Áp dụng trên Snapshot Debugger. |
| **D6** (i18n Hardcode) | ❌ CHƯA TRẢ | Xảy ra diện rộng trên cả UI và Backend (Vượt ra khỏi scope Sprint 33). |

## 4. Sprint 34 — 8 Fix Table

| Task | Priority | Ước lượng | Mô tả |
|------|----------|-----------|-------|
| 01 | P0 | 2h | Fix cascade Task 1 ↔ 4 (Truyền đúng dữ liệu vào Timeline). |
| 02 | P0 | 1h | Fix TclError fallback (Sử dụng widget hợp lệ khi thiếu PNG). |
| 03 | P1 | 8h | Sweep emoji & chuẩn hóa icon với `IconHelper`. |
| 04 | P1 | 1h | Verify và fix integration của `HuntStatusTicker`. |
| 05 | P2 | 0.5h | Fix spec fallback của `VisionSnapshotDebugger`. |
| 06 | P1 | 6h | Trả nợ D1: Tách rời cấu hình UI (Decouple config read/write). |
| 07 | P1 | 4h | Trả nợ D4, D6: Gộp event loop vào UIAnimationManager & i18n hóa. |
| 08 | P2 | 2h | Xóa code detect Test trong production và sửa hardcode backend. |

## 5. Conventions Bắt Buộc (Rules of Engagement)

- **Strict i18n:** Mọi chuỗi hiển thị (bao gồm cả UI và tin nhắn qua EventBus từ Backend) phải dùng hệ thống đa ngôn ngữ `_t()`.
- **No Emoji Strings:** Tuyệt đối không hardcode emoji như `🔴`, `🟢`, `⚠️`, `🛡️`. Bắt buộc dùng hệ thống quản lý icon `IconHelper` / `create_icon_button`.
- **No Test Code in Production:** Không cho phép sử dụng các trick nhận diện môi trường test (như `MagicMock`) trong code chạy thực.
- **Strict TDD & Regression:** Code phải pass toàn bộ test case cũ, không được dùng `except Exception: pass` để che giấu lỗi.
- **Traceability:** Mọi thay đổi đều phải truy xuất nguồn gốc (Trace) về mã lỗi (Finding #X) hoặc nợ kỹ thuật (Debt DX) được mô tả trong báo cáo kiểm toán này.

## 6. File Ownership Matrix (Tổng quát)

| File / Component Path | Primary Owner | Shared File (Chỉ sửa phần thuộc task) |
|-----------------------|---------------|---------------------------------------|
| `ui/panels/skill_panel.py` | Task 01, Task 06 | Task 03 |
| `ui/components/skill_timeline_strip.py` | Task 02 | Task 01, Task 03 |
| `ui/components/hunt_status_ticker.py` | Task 04 | Task 03 |
| `ui/components/vision_snapshot_debugger.py`| Task 05 | Task 03 |
| `lib/features/hunt/hunt_config.py` | Task 06 | - |
| `ui/components/status_badge.py` | Task 07 | Task 03 |
| `lib/features/hunt/monster_manager_win.py` | Task 08 | Task 03 |
| `lib/features/hunt/hunt_orchestrator.py` | Task 08 | Task 03 |


## 7. Trạng thái Thực tế (Cập nhật sau Audit Codebase)

Dựa trên báo cáo `audit_report.md` và kiểm tra source code thực tế, các Task đang có tình trạng như sau:

- **🟢 Đã hoàn thành sẵn (Cần cập nhật plan):**
  - **Task 01:** `get_combo_sequence` và `get_buff_sequence` đã được gọi đúng.
  - **Task 02:** `SkillTimelineStrip` đã có logic xử lý `isinstance(img, str)` fallback dùng `create_text`.
  - **Task 04:** `HuntStatusTicker` đã được tích hợp vào `HuntWorkspaceFrame`.
- **🟡 Hoàn thành một phần:**
  - **Task 07:** `_pulse_step` đã bị loại bỏ khỏi `status_badge.py`, nhưng hardcode string (D6) vẫn còn.
  - **Task 08:** Đã loại bỏ `MagicMock` khỏi production, nhưng cần sửa các message hardcode qua EventBus.
- **🔴 Chưa hoàn thành (Cần ưu tiên):**
  - **Task 03:** Đã dọn dẹp sạch toàn bộ emoji cứng, chuẩn hóa sang IconHelper và đa ngôn ngữ.
  - **Task 05:** Lỗi `delete("all")` trong `VisionSnapshotDebugger` vẫn còn tồn tại.
  - **Task 06:** Tight coupling `hunt_cfg.get(...)` ở UI vẫn xuất hiện ở nhiều file.
