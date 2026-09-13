# Sprint 30 - Bước 3: Gỡ rối luồng xử lý và tích hợp EventBus vào `app_gui.py`

**Mục tiêu:** Áp dụng EventBus để loại bỏ hoàn toàn mô hình callback lồng nhau giữa `App` và `HuntOrchestrator`, đồng thời đảm bảo Tkinter an toàn với thread thông qua việc unbind event.

**Các bước thực hiện:**
1. **Sửa đổi `HuntOrchestrator` (`lib/features/hunt/hunt_orchestrator.py`):**
   - Xóa bỏ callback `on_scene_monsters_detected` (và các callback UI khác nếu có) khỏi Constructor.
   - Thay vì gọi callback, hãy sử dụng `EventBus.trigger(SceneMonstersDetectedEvent(snapshot))` khi phát hiện quái vật.
   - Kiểm tra và đảm bảo các cập nhật trạng thái khác đều sử dụng `EventBus.trigger()` thay vì callback nối tiếp.
2. **Refactor `App` (trong `app_gui.py`):**
   - Loại bỏ các hàm tính toán logic nghiệp vụ như `promote_detected_monster`, logic validate start/stop (đã chuyển sang các Controller ở Bước 2).
   - View bây giờ khi user bấm nút sẽ chỉ gọi `self.hunt_controller.start_hunt()` hoặc `self.monster_rotation_controller.promote(idx)`.
   - Lắng nghe sự kiện: Thay vì truyền callback vào background services, gọi `EventBus.bind(...)` để lắng nghe các sự kiện như `HuntStateChangedEvent`, `HuntStatusUpdatedEvent`, `SceneMonstersDetectedEvent`, `MonsterRotationUpdatedEvent`.
   - **Quan trọng:** Tất cả các tác động cập nhật giao diện trong listener của EventBus **phải** được bọc bằng `self.after(0, ...)` để đảm bảo thread-safe cho Tkinter (tránh lỗi đóng băng UI).
3. **Quản lý vòng đời (Memory Leak Prevention):**
   - Tại hàm `on_close` hoặc các hàm destroy tương ứng của Tkinter trong `app_gui.py` (hoặc `AppLifecycleController`), hãy gọi `EventBus.unbind(...)` cho tất cả các event đã đăng ký ở trên để ngăn memory leak.
4. **Nghiệm thu:**
   - Chạy test thử các tính năng: Bắt đầu săn, dừng săn, thêm quái vật, log trạng thái trên thanh status bar.
   - Đảm bảo ứng dụng mượt mà, không gặp lỗi tăng RAM khi chuyển qua lại giữa các tính năng.
