# Prompt 08: Build Apply Build Implementation

## Điều kiện
Chỉ thực hiện sau Prompt 07.

## Mục tiêu
Hoàn thiện chức năng Apply Build.

## Phạm vi
- `BuildManagerFrame`
- Hunt Config
- Rotation Manager

## Root Cause liên quan
(Trích từ báo cáo gốc): Tính năng Apply Build (áp dụng build vào setup hiện tại) dường như chưa được hoàn thiện 100% trong `BuildManagerFrame`. Việc map các Build IDs vào Hunt Config và nạp lên tab Auto Scanner/Hunter hiện đang bị thiếu.

## Công việc cần thực hiện
- Map Build vào Hunt Config.
- Đồng bộ Rotation.
- Refresh UI liên quan.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Nút Apply Build hoạt động thực tế.
- Setup tự động được cập nhật dựa trên cấu hình Build đã chọn.

## Commit Message
`feat(build): implement apply build workflow`
