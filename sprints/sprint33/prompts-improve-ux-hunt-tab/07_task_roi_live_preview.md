# Task 7: Phát triển Cơ chế `VisionSnapshotDebugger` (On-Demand Preview)

## Bối cảnh (Context)
Dù quá trình cấu hình ROI khá chi tiết ở Setup Tab, nhưng trong quá trình săn thực tế, nếu nhận diện ảnh thất bại, người dùng không thể biết thuật toán Vision đang "nhìn" thấy gì. Cần một tính năng cho phép chụp một bức ảnh On-Demand (theo yêu cầu) kèm theo bounding box và độ tự tin (Confidence score) quét được.

## Yêu cầu (Requirements)
1. Thêm một nút (Button) mang tên "Debug Vision" ở góc của tab Hunt.
2. Khi bấm nút, mở ra một cửa sổ popup (`tk.Toplevel`) chứa một `tk.Canvas`.
3. Tại cửa sổ này, thực hiện một lời gọi hàm (Method Call) trực tiếp xuống `VisionEngine` để xin một Raw Frame (Ảnh thô mới nhất) và danh sách Bounding Boxes. Tuyệt đối KHÔNG đăng ký nhận Raw Frame qua EventBus! LƯU Ý: Phải yêu cầu `VisionEngine` cung cấp một phương thức Thread-Safe (sử dụng Mutex/Lock) để clone frame, tránh Race Condition với luồng quét ngầm.
4. Sử dụng OpenCV / Pillow để vẽ (draw) ảnh màn hình game đã được Resize nhỏ lại, kèm theo các hình chữ nhật (Bounding Box) đè lên, ghi chú text "Mục tiêu [0.85]".
5. Nút bấm trong Popup có thể có tính năng "Refresh Snapshot" để chụp lại ảnh tĩnh mới. Cửa sổ đóng sẽ tự hủy Image Reference.

## Rủi ro (Risks & Pitfalls)
- **EventBus Overload / Memory Thrashing:** Khái niệm "Live Stream" (phát video qua event bus ở 10fps) sẽ phá hủy luồng UI Thread của Tkinter và gây Memory Leak. Việc sử dụng "On-Demand Snapshot" bằng hàm hỏi/đáp (Polling khi click) giải quyết triệt để vấn đề này. TRÁNH DEADLOCK: Luồng UI gọi method trực tiếp vào VisionEngine phải đảm bảo Lock nội bộ không block quá lâu (Set cứng Timeout = 500ms). Nếu Timeout, UI phải dùng lại ảnh Snapshot cũ.
- **Garbage Collection:** Hủy biến ảnh cũ (set None) trước khi gán ảnh mới từ OpenCV!

## Unit Tests Cần Thêm (Unit Tests to Add)
- Đảm bảo việc bấm "Refresh" liên tục 50 lần không làm tăng RAM (Memory Leak test). Đảm bảo CPU overhead khi mở chức năng này < 5%.
## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Ngừng Lạm dụng EventBus cho Dữ liệu lớn:** Nếu mã nguồn cũ của Backend đang cố gắng gửi mảng Numpy (Raw frame) qua `SceneMonstersDetectedEvent`, hãy xóa/refactor luồng đó ngay lập tức! Bạn phải trả khoản nợ rò rỉ bộ nhớ (Memory Thrashing) này bằng cách chuyển qua kiến trúc "Method Call xin cấp ảnh (On-Demand)" kèm Mutex Lock thay vì phát tán ảnh lung tung qua Bus.
- **Toán học Bounding Box:** Khi bạn thu nhỏ Raw Frame (resize image), bạn PHẢI nhân chia tọa độ Box (x, y, w, h) mà VisionEngine trả về theo đúng tỷ lệ Scale, nếu không khung viền sẽ bị vẽ sai lệch hoàn toàn so với ảnh.
- **i18n Hardcode:** Các nút mới như "Debug Vision", "Refresh Snapshot" phải được đăng ký key vào hệ thống ngôn ngữ và gọi qua `self.app._t()`.
