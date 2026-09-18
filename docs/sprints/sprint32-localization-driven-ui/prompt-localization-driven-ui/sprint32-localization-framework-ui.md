# Tài liệu Kiến trúc & Lộ trình: Metadata-Driven Localization UI (Sprint 32 - 36)

## 1. Mục Tiêu Tối Thượng (Tầm Nhìn Kiến Trúc)

Mục tiêu cuối cùng của toàn bộ chuỗi nâng cấp này là chuyển đổi hệ thống giao diện (UI) hiện tại sang mô hình **Metadata-Driven Localization UI**.

Điều này có nghĩa là:
- **UI sẽ KHÔNG còn chứa dữ liệu hiển thị trực tiếp** (như chuỗi văn bản cứng "Lưu", "Thoát" hay mô tả tooltip dài dòng).
- **UI chỉ đóng vai trò là "Bộ khung" và chứa các Metadata (siêu dữ liệu)** như: `text_key`, `tooltip_key`, `icon_key`.
- Các hệ thống trung tâm (Localization System & Metadata System) sẽ tự động theo dõi, phân tích các metadata này và **quyết định nội dung hiển thị cuối cùng** dựa trên ngôn ngữ đang được chọn và các cấu hình tương ứng trong hệ thống.

Kết quả là chúng ta sẽ có một giao diện hoàn toàn tách biệt khỏi dữ liệu, dễ dàng bảo trì, mở rộng và thay đổi ngôn ngữ ngay lập tức mà không cần khởi động lại hay chạm vào code giao diện.

## 2. Hiện Trạng Hệ Thống (Sau Sprint 31)

### Những Gì Đã Hoàn Thành
Đến thời điểm hiện tại, dự án Cabal_Auto đã xây dựng được một nền tảng kiến trúc rất vững chắc:
- **Tách biệt Giao diện và Dữ liệu:** Giao diện đã được chia thành các Component độc lập, tuân thủ nguyên tắc Composite Pattern. Dữ liệu được quản lý riêng bởi các Data Manager.
- **Hệ thống EventBus:** Đã áp dụng kiến trúc Event-Driven, cho phép các thành phần giao tiếp với nhau qua sự kiện (ví dụ: sự kiện thay đổi ngôn ngữ) mà không bị ràng buộc chặt chẽ (loose coupling).
- **UI hỗ trợ Metadata:** Các hàm tạo UI hiện tại đã bắt đầu tiếp nhận và lưu trữ các metadata vào bản thân thành phần widget thay vì nhận văn bản cứng.

### Ý Nghĩa Của Các Khóa Metadata
- **`text_key`**: Là định danh duy nhất (ví dụ: `btn.save`, `lbl.status`) đại diện cho nội dung chữ của một thành phần. Thay vì hiển thị chữ "Lưu", UI chỉ giữ mã `btn.save`, hệ thống Localization sẽ dịch mã này ra "Lưu" (tiếng Việt) hoặc "Save" (tiếng Anh).
- **`tooltip_key`**: Tương tự như `text_key`, nhưng dùng cho phần chú thích hiện ra khi người dùng di chuột (hover) vào thành phần (`tooltip.refresh`).
- **Icon Metadata (`icon_key`)**: Mã định danh của biểu tượng. Icon cũng có thể đi kèm với tooltip riêng của nó (được nạp từ cơ sở dữ liệu), giúp các biểu tượng có thể tự giải thích ý nghĩa.

## 3. Quy Tắc Giải Quyết Xung Đột Tooltip (Resolver Rules)

Trong quá trình ghép nối các thành phần UI, sẽ có trường hợp cả nút bấm và biểu tượng bên trong đều có thể có tooltip riêng. Làm sao để hệ thống quyết định hiển thị gì?

Quy tắc ưu tiên hiển thị (Tooltip Priority) được xác định như sau:
**Icon Tooltip > Button Tooltip > Default Tooltip**

**Vì sao Tooltip Icon được ưu tiên cao nhất?**
- Biểu tượng (Icon) mang tính trực quan và gắn liền với dữ liệu cơ sở, thường có ngữ nghĩa rất cụ thể.
- Khi đặt một biểu tượng vào một nút bấm, người dùng có xu hướng muốn biết biểu tượng đó có ý nghĩa gì. Do đó, hệ thống sẽ ưu tiên lấy mô tả tooltip được gắn với chính cái icon đó, thay vì lấy tooltip tổng quát của cái nút bấm. Điều này đảm bảo tính nhất quán của dữ liệu trên toàn hệ thống mà không cần lập trình viên phải tự nhớ ghi đè.

---

## 4. Lộ Trình Triển Khai (Roadmap từ Sprint 32 đến Sprint 36)

Việc chuyển đổi sang hệ thống Metadata-Driven Localization UI sẽ được chia thành các giai đoạn (Sprint) rõ ràng, đi từ việc chuẩn hóa dữ liệu cho đến việc xây dựng các bộ quản lý và giải quyết tự động.

### Sprint 32: Chuẩn Hóa Dữ Liệu và Translation Key
**Mục tiêu:** Dọn dẹp mã nguồn, chuẩn bị dữ liệu văn bản và thiết lập hệ thống từ điển chuẩn mực.
- **Hoàn tất chuẩn hóa Translation Key:** Lên quy chuẩn đặt tên rõ ràng, dễ hiểu (ví dụ: `btn.save`, `lbl.search`, `menu.file`).
- **Audit và refactor hardcoded text:** Rà soát lại giao diện.
- **Chuẩn hóa `text_key` và `tooltip_key`:** Bắt đầu tạo dữ liệu dịch thuật tương ứng.

### Sprint 33: Thiết Kế LocalizationBinder
**Mục tiêu:** Quản lý việc cập nhật ngôn ngữ tự động và tập trung.
- **Thiết kế LocalizationBinder:** Tạo ra một lớp (layer) trung gian có khả năng tự động đọc các biến metadata từ các thành phần UI.
- **Quản lý tập trung Text và Tooltip:** Khi có thay đổi ngôn ngữ, LocalizationBinder sẽ tự động lấy bản dịch mới và làm mới (refresh) chữ, tooltip trên màn hình một cách tự động.

### Sprint 34: Thiết Kế TooltipBinder
**Mục tiêu:** Quy hoạch lại hoàn toàn cách hệ thống Tooltip hoạt động để không bị phân mảnh.
- **Thiết kế TooltipBinder:** Tập trung hóa việc gắn kết và cập nhật tooltip cho toàn bộ các thành phần hiển thị trong hệ thống.
- **Chuẩn hóa Tooltip Lifecycle:** Quản lý vòng đời của Tooltip một cách chuyên nghiệp (khi nào hiển thị, khi nào cập nhật, khi nào hủy bỏ) thông qua một kênh duy nhất.

### Sprint 35: Xây Dựng Resolver Layer
**Mục tiêu:** Xử lý tự động các logic lựa chọn dữ liệu hiển thị (như quy tắc ưu tiên tooltip).
- **Thiết kế PropertyResolver & TooltipResolver:** Là thành phần đứng giữa UI và LocalizationBinder, chuyên đảm nhiệm việc "suy luận".
- **Tập trung hóa các quy tắc:** Resolver này sẽ tự động phân tích metadata của nút bấm và đưa ra kết quả cuối cùng theo luật đã định (`Icon Tooltip > Button Tooltip > Default Tooltip`). Lập trình viên thiết kế giao diện sẽ không cần viết logic so sánh này trong từng giao diện riêng lẻ.

### Sprint 36: Đánh Giá Hệ Thống (Metadata-Driven Localization UI)
**Mục tiêu:** Rà soát và xác nhận sự chuyển đổi kiến trúc đã hoàn tất.
- **Đánh giá mức độ sẵn sàng:** Kiểm tra lại toàn bộ hệ thống Translation, Tooltip, Icon Metadata, Resolver Layer và Binder Layer.
- Khẳng định hệ thống giao diện đã hoàn toàn hoạt động theo cơ chế **Metadata-Driven**, nơi dữ liệu hiển thị hoàn toàn được nạp động, tách biệt khỏi mã nguồn giao diện.
