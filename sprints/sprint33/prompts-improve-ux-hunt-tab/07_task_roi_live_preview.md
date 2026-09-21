# Task 7: Phát triển Cơ chế `VisionLivePreview`

## Bối cảnh (Context)
Dù quá trình cấu hình ROI khá chi tiết ở Setup Tab, nhưng trong quá trình săn thực tế, nếu nhận diện ảnh thất bại (do đổi độ phân giải, lag, hoặc lệch khung), người dùng không thể biết thuật toán Vision đang "nhìn" thấy gì. Cần một tính năng cho phép xem ảnh live kèm theo bounding box (viền đỏ/xanh) và độ tự tin (Confidence score) quét được.

## Yêu cầu (Requirements)
1. Thêm một nút (Button) mang tên "Debug Vision" hoặc "Live Preview" ở góc của tab Hunt (hoặc nằm cạnh HuntStatusTicker của Task 6).
2. Khi bấm nút, mở ra một cửa sổ popup (`tk.Toplevel`) chứa một `tk.Canvas`.
3. Tại cửa sổ này, hãy đăng ký (subscribe) sự kiện `SceneMonstersDetectedEvent` và các event có chứa `frame` ảnh gốc (nếu có).
4. Sử dụng OpenCV / Pillow để vẽ (draw) ảnh màn hình game thu nhỏ, kèm theo các hình chữ nhật (Bounding Box) đè lên, ghi chú text "Mục tiêu [0.85]" (0.85 là confidence score) tương tự cách debug YOLO.
5. Khi người dùng đóng popup, phải Unbind event ngay lập tức để tiết kiệm tài nguyên.

## Rủi ro (Risks & Pitfalls)
- **Truyền Frame qua EventBus:** Hiện tại `SceneMonstersDetectedEvent` chỉ trả về danh sách Snapshot (tọa độ bbox, tên) chứ chưa kèm theo ảnh thô (raw frame). Bạn có thể cần phải sửa `HuntOrchestrator` để nó nhét thêm raw frame (cv2 image) vào sự kiện, HOẶC component LivePreview phải tự hook vào `VisionEngine` để xin frame mới nhất.
- **CPU/RAM Usage:** Việc render ảnh liên tục trên Tkinter rất tốn RAM (Garbage collection của PhotoImage). Bắt buộc phải resize ảnh xuống độ phân giải thấp (vd 640x480) và hủy biến ảnh cũ trước khi gán ảnh mới!

## Unit Tests Cần Thêm (Unit Tests to Add)
- Tạo ảnh Dummy Numpy, phát event và kiểm tra hàm vẽ Bounding Box lên Canvas có lỗi không (đảm bảo ko tràn bộ nhớ / memory leak).