# Prompt 06: Build Details Panel

## Mục tiêu
Cải thiện hiển thị Build Details.

## Phạm vi
- `BuildManagerFrame`
- Build Details Panel

## Root Cause liên quan
(Trích từ báo cáo gốc): Hiện trạng hiển thị của cột Attack/Buff preview chỉ in ra mảng JSON như `[1, 2, 3]` ở phần Details, khó hiểu đối với end-user. Cần phải parse các ID này và hiển thị thành tên kỹ năng thực tế.

## Công việc cần thực hiện
- Parse ID (ID skills từ dữ liệu JSON).
- Hiển thị tên skill tương ứng thay vì ID.
- Kiểm tra cache.
- Kiểm tra performance.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Mảng ID `[1, 2, 3]` được thay thế bằng danh sách tên kỹ năng (ví dụ: `Sword Spin, Fireball`).
- Hiệu suất không bị ảnh hưởng đáng kể.

## Commit Message
`improve(build): show skill names in details panel`
