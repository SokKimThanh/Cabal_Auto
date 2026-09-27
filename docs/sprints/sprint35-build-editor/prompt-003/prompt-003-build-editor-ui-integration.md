# Prompt 003 - Build Editor UI Integration

## 1. Objective
Cập nhật Build Editor Dialog và Build Manager Frame để người dùng có thể xem, chọn và chỉnh sửa các kỹ năng (`attack_skill_ids`, `buff_skill_ids`) thuộc về Build.

## 2. Scope
### UI - Build Editor
- Bổ sung widget hiển thị và chọn Attack Skills.
- Bổ sung widget hiển thị và chọn Buff Skills.
- Đồng bộ dữ liệu giữa UI và Build Model.

### UI - Build Manager
- Hiển thị thông tin các skill đã được gán cho Build.
- Bổ sung nút **Apply Build** trên giao diện.

### Ngoài phạm vi
- Database.
- Repository.
- Service.
- Event xử lý Apply Build.
- Lane Integration.

## 3. Definition of Done (DoD)
- Người dùng có thể chọn Attack Skills cho Build.
- Người dùng có thể chọn Buff Skills cho Build.
- Build đã lưu được load lại chính xác trên UI.
- Dữ liệu từ UI được truyền đúng xuống tầng Service.
- Nút Apply Build hiển thị đúng trên giao diện nhưng chưa phát event.

## 4. Risks
- Layout bị vỡ khi Build chứa nhiều skill.
- Hiển thị icon/tooltip không đúng.
- Load Build cũ không có skill gây lỗi UI.

## 5. Rollback Plan
- Revert commit `feat(ui): integrate skill selection into build editor`.

## 6. Impact Analysis
### Affected Modules
- Build Editor Dialog
- Build Manager Frame

### Must Not Affect
- Skill Panel UI
- Lane rendering
- Repository
- Service
- Database

### Regression Checklist
- [x] Thêm Build.
- [x] Sửa Build.
- [x] Xóa Build.
- [x] Load Build cũ.
- [x] Load Build mới có skill.
- [x] Nút Apply Build hiển thị đúng.

## 7. Acceptance Test
- **Scenario 1:** Hiển thị form chọn skill - Khi mở cửa sổ tạo hoặc sửa Build, khu vực chọn Attack Skills và Buff Skills sẽ được hiển thị.
- **Scenario 2:** Lưu skill từ UI - Khi nhấn Save, Build được lưu thành công cùng danh sách skill.
- **Scenario 3:** Load Build đã có skill - Khi mở lại Build Editor, các skill được hiển thị chính xác theo dữ liệu đã lưu.

## 8. Technical Debt Handling
- Đã tách UI component (`BuildEditDialog` ra file riêng).
- Đã sửa nợ trực tiếp gọi config dict trong `ui/components/vision_snapshot_debugger.py`.
- Các file test tạm đã được xoá.
- Mọi text mới sử dụng i18n/localization (`self.app._t()`).
- Tái sử dụng `create_icon_button()` theo convention.

## 9. Commit Strategy
Batch này được hoàn thành bằng một commit duy nhất: `feat(ui): integrate skill selection into build editor`

## 10. Implementation Plan & Tech Notes
- Tách `BuildEditDialog` ra khỏi `build_manager_frame.py` vào `ui/dialogs/build_edit_dialog.py`.
- Cập nhật UI của `BuildEditDialog` với 2 widget `Listbox` để cho phép chọn Attack Skills và Buff Skills. Các skills được lọc tự động dựa theo `class_id` đã chọn (sử dụng service `app.db_skill_service.get_skills_by_filter`).
- Khởi tạo và thiết lập các biến mapping ID của skill. Khi lưu, lấy các ID skill theo item đang được chọn và gán vào `attack_skill_ids` và `buff_skill_ids`.
- Trong `BuildManagerFrame`, bổ sung 2 label preview bên dưới Treeview. Cập nhật các label này mỗi khi người dùng chọn một Build trong Treeview.
- Bổ sung nút Apply Build vào thanh Toolbar bên dưới bằng cách sử dụng `create_icon_button`. Bổ sung một hàm rỗng `_apply_build()` cho chức năng của nút này. Nút được toggle on/off tùy theo có chọn build hay không.
- Localization: Áp dụng `self.app._t()` cho các label mới.
