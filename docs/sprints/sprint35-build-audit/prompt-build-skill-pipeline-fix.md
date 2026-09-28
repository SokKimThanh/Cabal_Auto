# Prompt 01: Build Skill Pipeline Fix

## Mục tiêu
Sửa lỗi Attack Skills và Buff Skills bị rỗng.

## Phạm vi
- `SkillService`
- `BuildEditDialog`
- Repository liên quan

## Root Cause liên quan
(Trích từ báo cáo gốc): Các kỹ năng crawl về từ web được insert vào bảng `skills` với cột `skill_type_id = NULL`. Phân loại kỹ năng thực tế được lưu trong bảng quan hệ `class_skill_assignments`. Vì câu query trong `get_skills_by_filter` dùng `SELECT skills.*`, nó lấy `skill_type_id` bị NULL, khiến cho danh sách skill ở `BuildEditDialog` bị filter thành mảng rỗng `[]`, dẫn đến UI trống rỗng.

## Công việc cần thực hiện
- Truy vết `get_skills_by_filter`.
- Xác nhận source của `skill_type_id`.
- Sửa query trả đúng loại skill.
- Kiểm tra Attack Skills.
- Kiểm tra Buff Skills.
- Kiểm tra Create Build.
- Kiểm tra Edit Build.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Blader hiển thị đúng Attack Skills.
- Blader hiển thị đúng Buff Skills.

## Commit Message
`fix(build): restore attack and buff skill loading`
