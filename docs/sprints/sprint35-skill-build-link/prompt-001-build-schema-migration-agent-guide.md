# Hướng dẫn chi tiết thực hiện Prompt 001 - Migrate Build Schema

Tài liệu này đóng vai trò hướng dẫn từng bước cho Bot hoặc Agent để thực hiện việc migrate Build Schema, thêm các cột `attack_skill_ids` và `buff_skill_ids`.

## Quy định tiên quyết
- **Tuyệt đối không thay đổi hay xóa file `monsters.db`** trong quá trình chạy test hay code. Nếu có thay đổi, phải `git restore` lại nó trước khi commit.
- **Tuân thủ đúng phạm vi:** Chỉ thay đổi Database Schema và Data Model (Data Access Layer - `BuildService`).

## Bước 1: Tạo Migration Script
1. Chạy lệnh: `mkdir -p lib/db/migrations`
2. Tạo file `lib/db/migrations/m001_add_skill_ids_to_builds.py`
3. Viết code cho hàm `up(conn)`: Sử dụng `ALTER TABLE builds ADD COLUMN attack_skill_ids TEXT DEFAULT '[]'` (bọc trong try/except để tránh lỗi trùng lặp khi chạy lại). Làm tương tự cho `buff_skill_ids`.
4. Viết code cho hàm `down(conn)`: Do SQLite có thể không hỗ trợ DROP COLUMN, dùng cách tạo bảng tạm (`builds_backup`), `INSERT INTO ... SELECT`, `DROP TABLE builds`, `ALTER TABLE ... RENAME TO`.

## Bước 2: Cập nhật file lib/db/schema.py
1. Tìm hàm tạo bảng `builds` trong `lib/db/schema.py`
2. Thêm hai cột mới vào thẳng câu lệnh `CREATE TABLE IF NOT EXISTS builds`:
   ```sql
   attack_skill_ids TEXT DEFAULT '[]',
   buff_skill_ids TEXT DEFAULT '[]',
   ```

## Bước 3: Đăng ký Migration chạy khi khởi tạo database
1. Mở file `database.py`.
2. Tìm hàm `setup_schema`.
3. Nhúng đoạn code chạy migration vào ngay sau lệnh `setup_icons_schema(self.conn)`:
   ```python
   from lib.db.migrations import m001_add_skill_ids_to_builds
   m001_add_skill_ids_to_builds.up(self.conn)
   ```

## Bước 4: Nâng cấp Data Access Layer (BuildService)
1. Mở `lib/db/services/build_service.py` và import `json`.
2. Chỉnh sửa hàm tạo (`create_build`):
   - Sửa SQL để thêm `attack_skill_ids`, `buff_skill_ids`.
   - Trong object value, truyền vào `json.dumps(data.get("attack_skill_ids", []))`.
3. Chỉnh sửa hàm cập nhật (`update_build`):
   - Thêm câu truy vấn `COALESCE` cho cả 2 cột giống với `upvote_count`.
   - Nhúng `json.dumps` nếu có dữ liệu truyền vào.
4. Tạo hàm parse dữ liệu an toàn để tương thích dữ liệu cũ:
   ```python
   def _parse_build(self, row: sqlite3.Row) -> Dict[str, Any]:
       if not row: return {}
       build_dict = dict(row)
       for key in ["attack_skill_ids", "buff_skill_ids"]:
           val = build_dict.get(key)
           try:
               build_dict[key] = json.loads(val) if val else []
           except (TypeError, ValueError):
               build_dict[key] = []
       return build_dict
   ```
5. Áp dụng hàm `_parse_build` này thay vì `dict(row)` cho các lệnh trả về ở hàm `get_build_by_id` và `get_builds`.

## Bước 5: Viết Unit Test trên Database Ảo In-Memory (QUAN TRỌNG)
1. Tuyệt đối không dùng `db = MonsterDatabase()` mặc định vì nó sẽ chọc vào `monsters.db` thật. Hãy ghi đè connection:
   ```python
   @pytest.fixture
   def test_db(monkeypatch):
       db = MonsterDatabase()
       conn = sqlite3.connect(':memory:')
       conn.row_factory = sqlite3.Row
       db.conn = conn
       monkeypatch.setattr(db, 'conn', conn)
       # ... Tạo bảng rỗng ...
       return db
   ```
2. Tạo các test để kiểm tra hàm `up` và `down` migration, kiểm tra hàm `create/update_build` lấy ra đúng `List` array trong `tests/unit/db/test_build_schema.py`.
3. Tạo file `tests/unit/db/test_build_schema_creation.py` để verify `lib/db/schema.py`.
4. Chạy test `python3 -m pytest tests/unit/db/test_build_schema*.py` để verify thành công.

## Bước 6: Các bước Pre-commit
- Gọi script pre commit check `bash pre_commit.sh` và đảm bảo kết quả pass.
- Đảm bảo `monsters.db` không nằm trong danh sách files bị thay đổi (`git restore monsters.db` nếu có).

## Bước 7: Thực hiện Commit Độc Lập
Chia thành 3 commit riêng biệt:
1. `git add lib/db/schema.py lib/db/services/build_service.py` -> `git commit -m "feat(build): add supported skill fields to model"`
2. `git add database.py lib/db/migrations/m001_add_skill_ids_to_builds.py` -> `git commit -m "feat(db): create migration script for build schema"`
3. `git add tests/unit/db/` -> `git commit -m "test(build): add tests for parsing old and new build models"`

Kết thúc quá trình.
