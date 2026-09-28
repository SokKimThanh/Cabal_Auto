# Prompt 04: Build Skill Selector UX

## Mục tiêu
Cải thiện trải nghiệm chọn skill.

## Phạm vi
- `BuildEditDialog`
- Skill Selection Components

## Root Cause liên quan
(Trích từ báo cáo gốc): Khung `tk.Listbox` hiện tại khó nhìn (màu select là primary trên nền đen surface), không trực quan. Người dùng không có công cụ "Search" hoặc "Filter" bên trong list skill, phải cuộn tìm rất khó khăn khi class có hàng chục kỹ năng.

## Công việc cần thực hiện
- Audit Listbox hiện tại.
- Đánh giá khả năng search.
- Đánh giá khả năng filter.
- Đánh giá khả năng preview.
- Thiết kế component chọn skill chuẩn.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Bản đề xuất UX design (UX design proposal) cho component chọn skill chuẩn, trực quan và dễ sử dụng.

## Commit Message
`docs(build): propose skill selector improvements`
