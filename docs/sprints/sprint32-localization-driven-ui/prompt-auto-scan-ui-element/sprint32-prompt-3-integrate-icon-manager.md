# Tích hợp Registry vào Icon Manager (Phase 3/4)

## Mục tiêu
Trích xuất danh sách metadata từ Registry và hợp nhất (merge) với dữ liệu lịch sử từ Database để hiển thị vào Combobox trong Form `Icon Manager`.

## Khối lượng công việc ước tính
< 30 phút

## Yêu cầu chi tiết

### 1. Cập nhật `IconManagerFrame._load_all_usage_ids()`
- Hàm này hiện đang gọi DB: `SELECT DISTINCT ui_element_id FROM icon_usages`.
- Hãy gọi thêm: `registry_items = UIElementRegistry.instance().get_all()`.
- Chuyển đổi các object `UIElementDescriptor` thành chuỗi hiển thị theo format: `f"{desc.module}/{desc.screen}/{desc.element_id}"`.
- Hợp nhất (Merge) 2 danh sách lại với nhau. Sử dụng `set` để loại bỏ các phần tử trùng lặp (ví dụ một ID đã lưu trong DB và đồng thời cũng đang có mặt trên UI qua Registry).

### 2. Điều chỉnh UX của Combobox
- Vì danh sách hiển thị giờ là `module/screen/element_id`, khi người dùng chọn một item và nhấn Save, đảm bảo rằng giá trị được lưu xuống CSDL chỉ là phần `element_id` (nếu đây là yêu cầu thiết kế hiện tại), hoặc lưu toàn bộ chuỗi phụ thuộc vào cấu trúc DB của `icon_usages`.
- (Hãy đọc kỹ file `proposal-auto-scan-ui-elements.md` và mã nguồn hiện tại của DB để quyết định đúng: Nếu DB chỉ lưu `element_id`, bạn phải parse chuỗi Combobox để lấy ra ID gốc trước khi gọi `IconService.save()`).

## Rủi ro tiềm ẩn (Cần tránh)
- **Race Condition / Format Mismatch:** Dữ liệu cũ trong DB đang là `btn_save`. Dữ liệu từ Registry đưa lên là `build_manager/settings/btn_save`. Nếu chỉ gộp đơn thuần bằng `set()`, danh sách sẽ chứa cả 2 (bị duplicate về mặt ý nghĩa). Hãy chuẩn hóa dữ liệu từ DB (hoặc ngược lại) trước khi gộp để đảm bảo tính duy nhất.
- **Lưu rác vào Database:** Bắt sự kiện `<FocusOut>` hoặc quá trình Save để chắc chắn rằng ta không lưu nguyên cụm `module/screen/element_id` vào cột `element_id` của DB (trừ khi được chỉ định thiết kế lại DB).
