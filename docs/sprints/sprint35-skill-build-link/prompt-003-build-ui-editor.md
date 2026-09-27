# Prompt 003 - Build Editor UI Integration

## 1. Mục tiêu (Objective)
Cập nhật giao diện của Build Editor Dialog và Build Manager Frame để người dùng có thể chọn, chỉnh sửa và xem được các kỹ năng (`attack_skill_ids`, `buff_skill_ids`) thuộc về Build đó.

## 2. Phạm vi thay đổi (Scope)
- **UI - Build Editor:** Bổ sung các widget cho phép xem và chọn danh sách kỹ năng cho Build.
- **UI - Build Manager:** Hiển thị preview/thông tin các kỹ năng đang lưu trong Build khi xem chi tiết.
- Thêm Nút "Apply Build" vào UI, nhưng **chưa implement logic phát event**.
- **Ngoài phạm vi:** Database, Services, Event xử lý apply build vào Lane.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- UI hiển thị đúng danh sách kỹ năng đã chọn.
- Dữ liệu chỉnh sửa từ UI được truyền đúng xuống Build Service/Repository (từ batch 2) để lưu trữ.
- Load Build vào Editor hiển thị đúng các kỹ năng đã lưu trước đó.

## 4. Các rủi ro tiềm ẩn (Risks)
- Layout UI bị vỡ khi hiển thị quá nhiều kỹ năng.
- Không load được danh sách icon kỹ năng hợp lệ.

## 5. Kế hoạch Rollback (Rollback Plan)
- Revert các commit chỉnh sửa `build_manager_frame.py` và `build_edit_dialog.py`.

## 6. Impact Analysis
**Affected modules:**
- Build editor dialog
- Build manager frame

**Must not affect:**
- Skill Panel UI
- Lane rendering
- Backend logic/Database

**Regression checklist:**
- Thêm/Sửa/Xóa Build thông qua UI hoạt động bình thường.
- Dữ liệu cũ vẫn hiển thị tốt.

## 7. Acceptance Test
**Scenario 1: Hiển thị form chọn kỹ năng**
- **Given** User mở cửa sổ tạo mới/sửa Build
- **When** Dialog hiện lên
- **Then** Có phần cho phép người dùng chọn Attack skills và Buff skills.

**Scenario 2: Lưu lại lựa chọn từ UI**
- **Given** User đã chọn một vài kỹ năng trong Edit Dialog
- **When** Nhấn Save
- **Then** Build mới được lưu thành công kèm danh sách kỹ năng vừa chọn.

## 8. Technical Debt Handling
**Trong batch này phải:**
- Tách các UI component con nếu Build Editor đang bị quá tải logic.
- Đảm bảo widget hiển thị tooltip/icon chuẩn của dự án.

**Không được:**
- Thêm TODO, FIXME.
- Sử dụng hardcode text (phải dùng i18n/localization nếu có).

## 9. Commit Strategy
- **Commit 1:** `feat(ui): add skill selection widgets to build editor`
- **Commit 2:** `feat(ui): display skill info and apply button in build manager`
