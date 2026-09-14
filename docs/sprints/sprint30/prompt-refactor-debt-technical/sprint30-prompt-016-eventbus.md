# Sprint 30 - Bước 1: Nâng cấp EventBus

**Mục tiêu:** Bổ sung cơ chế quản lý vòng đời (unbind) cho `EventBus` và định nghĩa các sự kiện mới để thay thế callback.

**Các bước thực hiện:**
1. **Mở tệp `lib/events/event_bus.py`:**
2. **Thêm phương thức `unbind`:**
   - Trong lớp `EventBus`, thêm phương thức `@classmethod def unbind(cls, event_type: Type[Event], listener: Callable[[Event], None]) -> None:`
   - Logic: Kiểm tra nếu `event_type` tồn tại trong `cls._listeners`, hãy gọi `.remove(listener)` bên trong khối `try/except ValueError` (để tránh crash nếu listener không tồn tại).
3. **Thêm các Event mới:**
   - Tạo lớp `SceneMonstersDetectedEvent(Event)` có thuộc tính `snapshot`.
   - Tạo lớp `MonsterRotationUpdatedEvent(Event)`.
4. **Viết/Cập nhật Unit Test (Nếu có thể):**
   - Đảm bảo việc bind, trigger, và unbind hoạt động chuẩn xác, không làm tăng bộ nhớ (memory leak).
