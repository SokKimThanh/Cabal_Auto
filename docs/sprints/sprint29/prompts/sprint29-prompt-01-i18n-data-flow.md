# Sprint 29 - Prompt 01: Sửa luồng dữ liệu ngôn ngữ (i18n Data Flow)

## Mục tiêu
Khắc phục tình trạng dữ liệu ngôn ngữ (i18n) trong Database bị ghi đè bởi dữ liệu tĩnh (từ code) trong mỗi lần khởi động ứng dụng. Mục tiêu là biến Database thành "Single Source of Truth", file code chỉ dùng để nạp các từ khóa hoàn toàn mới.

## Phạm vi (Scope)
- Sửa đổi cơ chế upsert trong `lib/db/services/translation_service.py`.

## Chi tiết yêu cầu

1. **Cập nhật hàm `bulk_upsert`**
   - Mở file `lib/db/services/translation_service.py`.
   - Tìm đến hàm `bulk_upsert`.
   - Tìm câu lệnh SQL `INSERT INTO translations... ON CONFLICT(namespace, key, lang) DO UPDATE SET...`.
   - Đổi đoạn `DO UPDATE SET text = excluded.text, updated_at = excluded.updated_at` thành `DO NOTHING`.

2. **Cập nhật hàm `upsert`**
   - Tìm hàm `upsert` trong cùng file đó.
   - Áp dụng thay đổi tương tự: sửa từ `ON CONFLICT(...) DO UPDATE...` thành `ON CONFLICT(...) DO NOTHING`.

3. **Kiểm tra (Verification)**
   - Khởi động ứng dụng, đảm bảo không gặp lỗi SQL syntax.
   - *Tự đánh giá:* Dữ liệu mới chưa có trong DB vẫn sẽ được nạp vào, nhưng dữ liệu cũ sẽ không bị đè mất nếu người dùng đã sửa trên DB.

## Lưu ý (Memory Guidelines)
- Chú ý Memory Rule: *"At startup, the application synchronizes static translation dictionaries to the SQLite database... this operation must use `ON CONFLICT DO NOTHING` (inserting only new/missing keys) rather than updating or overwriting existing database entries."* Đảm bảo bạn làm đúng rule này.
