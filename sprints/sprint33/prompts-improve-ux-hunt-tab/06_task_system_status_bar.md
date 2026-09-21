# Task 6: Phát triển Component `HuntStatusTicker` (System Log)

## Bối cảnh (Context)
Khi người dùng bấm "Bắt đầu săn", rất nhiều thao tác chạy ngầm (Validate cửa sổ, quét ảnh, tìm quái) sinh ra các log cảnh báo thông qua sự kiện `HuntStatusUpdatedEvent` và `HuntStateChangedEvent`. Tuy nhiên, hiện tại giao diện không hiển thị các thông báo này khiến người dùng không biết bot đang lỗi hay đang chạy bình thường.

## Yêu cầu (Requirements)
5. Nhớ dùng hàm đa ngôn ngữ `self.app._t("...")` cho tất cả các text nội dung thay vì viết cứng tiếng Việt.
1. Tạo file `ui/components/hunt_status_ticker.py` định nghĩa class `HuntStatusTicker` (kế thừa `tk.Frame`).
2. Component này bao gồm một Icon trạng thái (Spinner hoặc Dấu chấm than tùy loại thông báo) và một `tk.Label` nằm ngang để hiển thị text thông báo mới nhất.
3. Trong phương thức `__init__`, phải đăng ký lắng nghe sự kiện:
   - `EventBus.bind(HuntStatusUpdatedEvent, self._on_status_msg)`
   - `EventBus.bind(HuntStateChangedEvent, self._on_state_changed)`
4. Tích hợp Component này vào đáy (bottom) của `ui/views/hunt_workspace_frame.py` (hoặc `hunt_tab.py`), nằm phía trên hoặc cùng hàng với thanh Action bar.

## Rủi ro (Risks & Pitfalls)
- **Thread Safety:** Các Event từ `HuntOrchestrator` được bắn từ Background Thread. Khi nhận event trong `_on_status_msg`, BẮT BUỘC phải dùng `self.after(0, update_ui_func)` để đẩy việc cập nhật Label text về Main UI Thread, nếu không sẽ văng lỗi `RuntimeError` hoặc crash Tkinter.
- Chú ý độ tương phản màu sắc cho các trạng thái (Lỗi -> Đỏ `UI.COLOR_DANGER`, Đang quét -> Vàng `UI.ACCENT_AMBER`, Bình thường -> Trắng/Xám).

## Unit Tests Cần Thêm (Unit Tests to Add)
- Giả lập bắn `HuntStatusUpdatedEvent` và kiểm tra xem Label text có thay đổi đúng nội dung hay không (nhớ test thông qua `root.update()` để luồng `after` được xử lý).
## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Tối ưu Hóa EventBus:** Rà soát lại tất cả các nơi đang bắn `HuntStatusUpdatedEvent`. Đảm bảo rằng payload truyền đi chỉ là String báo cáo (Signal/Text), không được phép kẹp theo các object nặng (như Dictionary sâu hoặc Raw frame) để tránh làm nghẽn cổ chai (bottleneck) của EventBus.
