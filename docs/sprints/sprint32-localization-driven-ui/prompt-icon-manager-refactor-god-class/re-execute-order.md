# Chiến lược Thực thi và Rollback (Execution & Rollback Strategy)

Do quá trình bóc tách (refactor) một God Class như `IconManagerFrame` tiềm ẩn nhiều nguy cơ làm đứt gãy luồng dữ liệu (Data Flow) giữa các thành phần liên đới chặt chẽ, việc thực hiện cần tuân thủ nghiêm ngặt trình tự sau để đảm bảo tính an toàn:

## 1. Trình tự thực thi bắt buộc
Tiến hành chia để trị bằng cách bóc tách các "chóp" (ngoại vi) ít phụ thuộc nhất vào trước, sau đó mới tiến sâu vào lõi:
1. **[Prompt 01] CategoryManagerComponent:** Rất độc lập. Chỉ liên quan đến tab "Quản lý danh mục". Dễ dàng bóc tách mà không ảnh hưởng tới các tab khác.
2. **[Prompt 03] IconPreviewComponent:** Component thụ động (Chỉ nhận dữ liệu để vẽ ảnh thu nhỏ). Không chứa logic sửa đổi dữ liệu gốc.
3. **[Prompt 02] ImageLibraryComponent:** Phức tạp hơn một chút vì liên quan đến việc File Import và chọn File, nhưng vẫn giới hạn trong phạm vi trả về một `filepath`.
4. **[Prompt 04] IconFormComponent:** Cần cẩn thận ở bước này vì liên quan trực tiếp đến state của Form (Add/Edit) và quá trình Save.
5. **[Prompt 05] IconTreeComponent:** Đây là trái tim của giao diện, chứa thuật toán render bất đồng bộ. Làm bước này cuối cùng khi mọi thứ xung quanh đã được module hoá và bọc lại bằng callback an toàn.

## 2. Chiến lược xử lý sự cố (Fallback / Re-execute)

Nếu tại bất kỳ bước nào trong 5 Prompt trên gặp lỗi không tương thích hoặc vỡ layout:
1. **Dừng ngay lập tức:** Không cố gắng sửa tạm bợ (hack) bằng cách tạo thêm cờ (flags) hay biến toàn cục (global state) trên `IconManagerFrame`. Điều đó chỉ làm tình trạng God Class tồi tệ hơn.
2. **Khôi phục bản vá (Revert):** Dùng lệnh `git restore ui/views/icon_manager_frame.py` để lùi file chính về trạng thái hoàn hảo trước đó. Xóa bỏ Component đang tách lỗi.
3. **Phân tích nguyên nhân:** Thông thường lỗi xảy ra do bóc tách thiếu biến trạng thái (state variable) hoặc bỏ quên một sự kiện (event binding) ngầm định.
4. **Tạo biến phụ trợ tạm thời:** Thay vì nhét lại đoạn mã vào hàm khổng lồ, hãy sửa đổi nội dung Prompt hiện tại để tạo ra một "Interface hờ" (Dummy Proxy) giúp component kết nối lỏng lẻo hơn (loose coupling) thông qua Callback thay vì tham chiếu chéo (cross-reference) biến cục bộ. Sau đó thực thi lại Prompt.
