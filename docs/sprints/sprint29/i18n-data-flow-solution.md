# Giải pháp thống nhất luồng dữ liệu ngôn ngữ (i18n)

## Mô tả vấn đề hiện tại
Hiện tại, hệ thống ngôn ngữ đang có sự chồng chéo luồng dữ liệu (data flow) dẫn đến việc không thể lấy Database làm nguồn dữ liệu chuẩn.

Cụ thể, ở mỗi lần khởi động ứng dụng, hàm `load_from_db()` trong `lib/i18n/__init__.py` sẽ gọi hàm `bulk_upsert` từ `lib/db/services/translation_service.py` để đồng bộ các từ khóa từ file code (ví dụ: `GLOBAL_TRANSLATIONS`) vào SQLite database.
Tuy nhiên, câu lệnh SQL hiện tại sử dụng cơ chế `ON CONFLICT DO UPDATE`:
```sql
INSERT INTO translations (namespace, key, lang, text, updated_at)
VALUES (:namespace, :key, :lang, :text, :updated_at)
ON CONFLICT(namespace, key, lang) DO UPDATE SET
    text = excluded.text,
    updated_at = excluded.updated_at
```
Điều này khiến cho bất kỳ chỉnh sửa nào của người dùng hoặc hệ thống trực tiếp trong Database đều sẽ bị "đè" (ghi đè) lại bằng dữ liệu tĩnh từ các file code vào lần khởi động tiếp theo. Hệ quả là Database không thể đóng vai trò là "Single Source of Truth".

## Phương hướng giải quyết (Cách 1)
Chuyển đổi luồng để **Database là nguồn dữ liệu chuẩn (gốc)**. File code chỉ mang tính chất dự phòng để cung cấp dữ liệu cho các từ khóa (keys) **hoàn toàn mới**.

Giải pháp cụ thể: Sửa câu lệnh SQL trong hàm `bulk_upsert` để khi gặp một từ khóa đã tồn tại (conflict), hệ thống sẽ **bỏ qua (DO NOTHING)** thay vì ghi đè lên nó.

## Các bước thực hiện chi tiết

### Bước 1: Sửa đổi câu lệnh SQL trong `TranslationService.bulk_upsert`
Mở file `lib/db/services/translation_service.py`, tìm đến phương thức `bulk_upsert`.
Thay đổi câu lệnh SQL từ `ON CONFLICT... DO UPDATE` thành `ON CONFLICT... DO NOTHING`.

**Code cũ:**
```python
cursor.execute(
    """
    INSERT INTO translations (namespace, key, lang, text, updated_at)
    VALUES (:namespace, :key, :lang, :text, :updated_at)
    ON CONFLICT(namespace, key, lang) DO UPDATE SET
        text = excluded.text,
        updated_at = excluded.updated_at
    """,
    # ...
```

**Code mới cần cập nhật:**
```python
cursor.execute(
    """
    INSERT INTO translations (namespace, key, lang, text, updated_at)
    VALUES (:namespace, :key, :lang, :text, :updated_at)
    ON CONFLICT(namespace, key, lang) DO NOTHING
    """,
    # ...
```
*(Lưu ý: Bạn cũng nên cập nhật logic tương tự cho hàm `upsert` đơn lẻ trong cùng file đó nếu cần thiết).*

### Bước 2: Xác nhận luồng Hydrate vẫn hoạt động tốt
Trong `lib/i18n/__init__.py`, hàm `load_from_db()` sau khi thực hiện `bulk_upsert` (bước trên sẽ chỉ chép keys mới) sẽ tiếp tục gọi `service.get_all()` để đọc toàn bộ từ Database lên.
Luồng này hiện tại đã đúng và không cần sửa gì thêm. Nó sẽ đảm bảo:
1. Những key cũ, người dùng đã sửa trong DB sẽ được load lên thành công.
2. Những key mới, vừa được insert ở Bước 1 sẽ được load lên thành công.

### Kết quả mong đợi
- Các dữ liệu có sẵn trong Database sẽ được bảo toàn nguyên vẹn, kể cả khi khởi động lại app.
- Khi Dev thêm mới bản dịch vào file `.py`, tự động ứng dụng sẽ nạp những bản dịch mới đó vào Database mà không chạm tới dữ liệu đã có.
