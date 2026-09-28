# Prompt 03: Build Dialog Layout Audit

## Mục tiêu
Review UX và layout `BuildEditDialog`.

## Phạm vi
- `BuildEditDialog`
- UI Layout Components

## Root Cause liên quan
(Trích từ báo cáo gốc): Class kế thừa trực tiếp từ `tk.Toplevel`, gọi `geometry("600x550")` và dùng grid layout cơ bản mà không dùng framework chuẩn của project như `ResponsiveGridBase` hay `ExpandedPanel`. Khung cứng nhắc, khi resize sẽ bị lỗi vùng chết. Các ô nhập liệu dùng chiều rộng cứng.

## Công việc cần thực hiện
- Kiểm tra geometry cứng.
- Kiểm tra responsive.
- Kiểm tra scroll.
- Kiểm tra ResponsiveGridBase.
- Kiểm tra dead space.
- Đề xuất:
  - Layout mới.
  - Responsive strategy.
  - Không code lớn.
  - Chỉ audit + đề xuất.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Báo cáo audit layout chi tiết và đề xuất giải pháp.

## Commit Message
`docs(build): audit build dialog layout issues`
