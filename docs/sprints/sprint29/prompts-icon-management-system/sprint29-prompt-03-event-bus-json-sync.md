# Prompt 03: Event Bus & JSON Synchronization cho Icon Management

## Mục tiêu
Triển khai cơ chế Publish-Subscribe (Event Bus) để phát sự kiện khi Icon thay đổi, đồng thời tích hợp logic xuất/nhập dữ liệu giữa Database và file `icons.json` đảm bảo đồng bộ hệ thống như mô tả trong mục "5. Cơ Chế Đồng Bộ Hệ Thống".

## Ngữ cảnh & Yêu cầu từ Đặc tả
- **Lúc khởi động (Startup Auto-Sync):** Cần nạp dữ liệu từ `icons.json` vào DB (`ON CONFLICT DO NOTHING`).
- **Xuất dữ liệu lúc Lưu (CRUD Sync):** Khi DB có thay đổi (Thêm/Sửa/Xóa), cần gọi hàm export dữ liệu ra đè lên `icons.json`.
- **Event Bus:** Khi lưu một Icon (ví dụ update ảnh), hệ thống phát ra `IconUpdatedEvent(icon_key)` để UI bắt và tự refresh.

## Các bước triển khai chi tiết dành cho Người/AI

### Bước 1: Tạo Event Bus / Sự kiện
- **Vị trí:** Mở (hoặc tạo) module quản lý Event (VD: `lib/events/` hoặc tương tự).
- **Hành động:**
  - Khai báo class sự kiện `IconUpdatedEvent` chứa thuộc tính `icon_key: str`.
  - Khai báo class `IconManagerSyncEvent` (tùy chọn) để gọi các hàm sync nếu cần thiết.
  - (Nếu hệ thống đã có EventBus, chỉ cần khai báo Type, nếu chưa, cần implement một class tĩnh đơn giản chứa list các listener `bind/trigger`).

### Bước 2: Viết logic Startup Sync (JSON -> DB)
- **Vị trí:** Có thể viết trong `IconService` hoặc một file `IconSyncManager`.
- **Hành động:**
  - Viết hàm `import_from_json(json_path: str)`:
    - Đọc file JSON (dùng `json.load`).
    - Lặp qua từng cấu hình Icon và gọi `IconService.upsert_icon()` với mode chỉ chèn nếu chưa tồn tại (`ON CONFLICT DO NOTHING`). Lưu ý sửa câu lệnh SQL nội bộ hoặc truyền cờ flag nếu `upsert_icon` hiện tại là ghi đè.

### Bước 3: Viết logic Export Sync (DB -> JSON)
- **Hành động:**
  - Viết hàm `export_to_json(json_path: str)`:
    - Gọi `IconService.get_all_icons()`.
    - Chuyển danh sách thành định dạng JSON string (có thụt lề cho đẹp).
    - Mở file `icons.json` ở chế độ ghi (`'w'`) và lưu xuống.

### Bước 4: Tích hợp vào Trigger
- **Hành động:**
  - Mở lại `IconService.upsert_icon` và `delete_icon` đã viết ở Prompt 02.
  - Sau khi thao tác DB thành công, gọi `export_to_json(...)` (hoặc gọi qua event).
  - Đối với `upsert_icon`, sau khi hoàn tất thành công, kích hoạt EventBus: `event_bus.trigger(IconUpdatedEvent(icon_key=data['icon_key']))`.

### Bước 5: Viết Unit Test cho Sync & Event
- **Vị trí:** Tạo file test `tests/unit/test_icon_sync.py`.
- **Hành động:**
  - Mock thao tác đọc/ghi file.
  - Test hàm `import_from_json` parse đúng dữ liệu đưa vào DB ảo.
  - Test hàm `export_to_json` trích xuất đúng format.
  - Cài một listener giả vào EventBus, gọi `upsert_icon` và kiểm tra listener có nhận được `icon_key` tương ứng không.

## Tiêu chí hoàn thành (Definition of Done)
- [ ] Dữ liệu từ file JSON được đồng bộ 1 chiều an toàn khi khởi chạy (không đè dữ liệu cũ trong DB).
- [ ] Mọi thay đổi CRUD từ Service đều ghi đè chính xác xuống file JSON.
- [ ] Sự kiện `IconUpdatedEvent` được bắn ra thành công.
- [ ] Test coverage cho Sync & Event đạt.

## Thời gian dự kiến: ~30 phút
