# Prompt 02: Build Validation Audit

## Mục tiêu
Kiểm tra và bổ sung validation Build.

## Phạm vi
- `BuildEditDialog`
- `BuildManagerFrame`
- Dữ liệu liên quan

## Root Cause liên quan
(Trích từ báo cáo gốc): Cho phép người dùng vô tình tạo Build với danh sách rỗng (thiếu Validation ở Dialog). Người dùng có thể lưu một build mà không có skill nào được chọn, hoặc class không hợp lệ, dẫn đến dữ liệu rác trong database.

## Công việc cần thực hiện
- Audit toàn bộ validation hiện tại.
- Xác định dữ liệu rác có thể tạo.
- Thêm validation:
  - Class bắt buộc.
  - Ít nhất 1 skill.
  - Author hợp lệ.
  - Build rỗng bị chặn.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Không thể lưu Build không hợp lệ.

## Commit Message
`feat(build): add build validation rules`
