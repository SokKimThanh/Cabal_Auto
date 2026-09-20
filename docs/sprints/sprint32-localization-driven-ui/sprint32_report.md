# Đánh giá hiện trạng ứng dụng và tính khả thi - Sprint 32: Chuẩn Hóa Dữ Liệu và Translation Key

## 1. Hiện Trạng Hệ Thống
Từ kết quả rà soát codebase (`ui/views`, `ui/panels`, `ui/tabs`), chúng ta thấy ứng dụng hiện vẫn sử dụng rất nhiều **hardcoded text** cho các thành phần UI (Label, Button, Heading của Treeview). Các vị trí hardcoded điển hình bao gồm:
- **Tiêu đề cột (Headings) của Treeview**: `build_manager_frame`, `scan_history_frame`, `class_manager_frame`, `monster_manager_frame`, `stats_tab`.
- **Nhãn dán (Labels) trong Form/Panel**: Các nhãn như "Class", "Author", "STR", "INT", "Target Setup", "Active Skills", ...
- **Nút bấm (Buttons)**: "Save", "Cancel", "Next", "Prev", ...
- **Ký hiệu/Biểu tượng thuần Text**: Các nút như "➕", "↑", "↓", "✓", "🔒", cũng như trạng thái hiển thị như "1 / 1", "— / —".

**Điểm cộng hiện tại:**
- Hệ thống đã có bộ phận Localization cơ bản (ví dụ: `self.app._t("btn_refresh")` được sử dụng lác đác, lớp `TranslationBinder` cũng đã tồn tại để bind i18n cho widget).
- Kiến trúc dựa trên sự kiện (Event-driven) và Composite Component rất phù hợp để triển khai Metadata-driven UI.

## 2. Tính Khả Thi Của "Metadata-Driven Localization UI" (Sprint 32)
Dựa vào hiện trạng, tài liệu đặc tả của Sprint 32 là **Hoàn toàn khả thi và vô cùng cần thiết**.
Tuy nhiên, để đảm bảo mỗi phiên làm việc được tối ưu (mỗi prompt dưới 30 phút), cần phải chia nhỏ công việc một cách cẩn thận theo nguyên tắc:
1. **Audit & Standardize (Kiểm toán & Chuẩn hoá)**: Làm sạch danh sách các text đang bị hardcode và quy hoạch key (ví dụ: `lbl.*`, `btn.*`, `tree.*`).
2. **Refactor theo từng khu vực**: Tách riêng ra từng màn hình/panel để refactor, tránh việc thay đổi một lúc quá nhiều file dẫn đến merge conflict hoặc hồi quy.
3. **Migrate Metadata Component**: Đảm bảo các component tuỳ chỉnh được truyền Metadata thay vì truyền text cứng.

## 3. Danh Sách Các Prompt Dự Kiến (Cắt nhỏ <30 phút)
*Lưu ý: Danh sách chi tiết các file sẽ được sinh ra ở Bước 1.*
1. **Audit Hardcoded Text & Đề xuất Dictionary Template**: Tạo bảng ánh xạ các Text hiện tại sang các `text_key` chuẩn mực.
2. **Refactor Treeview Headings**: Thay thế text cứng trên các cấu trúc bảng (Treeview).
3. **Refactor Form Labels (Manager Frames)**: Refactor Text trên các `class_manager_frame`, `monster_manager_frame`, `skill_manager_frame`, `build_manager_frame`.
4. **Refactor Panels (Target, Skill, Stats)**: Refactor các text hiển thị động, các label nhỏ lẻ bên trong `ui/panels/`.
5. **Refactor Nút Bấm & Metadata Input**: Sửa đổi cấu trúc truyền text vào các nút, đưa tham số `text_key` vào các helper sinh Component (nếu cần).

## Task Summary
Sửa lỗi nút Refresh (Làm mới) trên màn hình Icon Manager làm mất ngữ cảnh layout, đồng thời khắc phục lỗi hiển thị của component EmptyState.

## Work Completed
- Cập nhật logic `_on_refresh` trong `ui/views/icon_manager_frame.py` để clear selection và form data mà không ép giao diện nhảy về lại trạng thái "chưa chọn icon" ban đầu.
- Sửa lỗi text dài bị cắt cụt trong `ui/components/empty_state.py` và tăng chiều cao của component xem trước ảnh.
- Ẩn EmptyState bằng `grid_remove` khi có ảnh được hiển thị để tránh hiện tượng chồng lấp.

## Key Decisions
- Thay vì hardcode kích thước hiển thị (wraplength) của text trong EmptyState, thay đổi thành tham số mặc định và cho phép tuỳ chỉnh (ví dụ `wraplength=450` cho phần preview) để duy trì tính đa dụng của component này.
- Khi người dùng nhấn Làm mới, chỉ clear các trường dữ liệu và danh sách tìm kiếm, thay vì huỷ toàn bộ khung nhìn form và đưa giao diện về trạng thái hoàn toàn trống.

## Changes Made
- Sửa đổi `ui/views/icon_manager_frame.py`: bỏ `self.empty_state_frame.tkraise()` trong `_on_refresh`.
- Cập nhật `ui/components/empty_state.py`: nhận tham số `wraplength`.
- Cập nhật `ui/components/icon_preview_component.py`: tăng `height` lên 260, truyền `wraplength=450` vào `EmptyState`, thêm lệnh `grid_remove` cho `empty_preview` khi render ảnh thực.

## Issues / Risks
- Không ghi nhận rủi ro đáng kể nào do các unit test đã được cập nhật/xác nhận thành công.

## Next Steps
- Tiếp tục các task theo tiến độ của Sprint 32 (ví dụ: refactor Treeview Headings và Form Labels).
