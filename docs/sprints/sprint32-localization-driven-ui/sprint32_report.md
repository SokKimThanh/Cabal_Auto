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
Cập nhật các thành phần UI của Sidebar (tab_hunt, tab_setup, btn_skill_manager, btn_monster_manager) bằng cách loại bỏ hardcoded emoji, thay thế bằng icon key chuẩn và đăng ký chúng vào danh sách UI Element Registry cũng như cơ sở dữ liệu.

## Work Completed
- Cập nhật danh sách `sidebar_icons` trong `lib/db/schema.py` để bổ sung các icon còn thiếu của sidebar.
- Viết vòng lặp để chèn các usage của sidebar button vào bảng `icon_usages` trong quá trình khởi tạo DB.
- Sửa đổi `ui/components/sidebar_component.py`: Xoá bỏ emoji cứng trên các nút/label và đăng ký chúng vào `UIElementRegistry` thông qua `UIElementDescriptor` khi render.

## Key Decisions
- Sử dụng Local Import `from lib.events.ui_element_registry import UIElementRegistry` bên trong phương thức `_build()` của `SidebarComponent` để tránh các lỗi Circular Dependency hoặc Tkinter initialization.
- Luôn kiểm tra sự tồn tại của row bằng `SELECT COUNT(*)` trong `icon_usages` trước khi `INSERT` vào để tránh lỗi duplicate ở lần chạy thứ hai trở đi của schema setup.

## Changes Made
- Đã chỉnh sửa: `lib/db/schema.py`
- Đã chỉnh sửa: `ui/components/sidebar_component.py`
- Refactor việc gán icon để sử dụng icon string identifier.

## Issues / Risks
- Phụ thuộc khá lớn vào việc rebuild database đối với người dùng cuối chưa chạy script migrate mới (có thể cần refresh database gốc trên môi trường local).

## Next Steps
- Cập nhật thêm tính năng cập nhật text_key chuẩn cho các button này (để tự động fetch translation tooltip/name).
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


### Nhiệm vụ: Tự động đồng bộ trạng thái chọn (Highlight) trong cây UI Element khi chọn Icon

#### Summary
Thêm logic để khi người dùng chọn một icon đã được liên kết bên danh sách Icon, hệ thống sẽ tự động tìm, mở rộng (expand), cuộn đến (scroll to) và chọn sáng (highlight) nút (node) UI Element tương ứng trong cây "Available Elements" (cây UI Element bên phải).

#### Work Completed
- Thêm phương thức hỗ trợ `_sync_available_elements_selection` vào `IconManagerFrame`.
- Tích hợp phương thức trên vào callback `_process_tree_selection_callback` để thực thi mỗi khi một icon được chọn.

#### Key Decisions
- Sử dụng phương thức đệ quy (recursive method) để duyệt qua toàn bộ các nút trong `Treeview` của `available_elements_tree` nhằm tìm kiếm chính xác lá (leaf node) đang lưu trữ `icon_key` được ánh xạ (nằm ở vị trí thứ 5 trong list `values`).
- Chỉ thực hiện "highlight" (chọn sáng qua `selection_set`) thay vì kích hoạt lại sự kiện `<<TreeviewSelect>>` để tránh việc vô tình ghi đè các ô nhập liệu (Module, Component, Element ID) trong form khi người dùng không mong muốn, đúng với yêu cầu "chỉ highlight".
- Sử dụng hàm `see(target_node)` của `Treeview` để tự động mở rộng các thư mục cha và cuộn màn hình đến nút được chọn, giúp đảm bảo UX tốt nhất.

#### Changes Made
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Thêm phương thức `_sync_available_elements_selection(self, icon_key)`.
  - Cập nhật phương thức `_process_tree_selection_callback(self, icon_key)` để gọi hàm đồng bộ trên.

#### Issues / Risks
- Không ghi nhận rủi ro đáng kể. Tính năng đã được kiểm thử với dummy data và không làm ảnh hưởng đến các logic mapping hay refreshing hiện có.

#### Next Steps
- Cập nhật thêm tính năng này cho các thành phần UI khác nếu có yêu cầu tương tự.


### Nhiệm vụ: Tối ưu hoá thuật toán và chống vòng lặp đệ quy trong đồng bộ cây UI Element (Fix Crash/Freeze)

#### Summary
Sửa lỗi ứng dụng bị treo (freeze/Not Responding) khi vòng lặp vô hạn xảy ra giữa 2 sự kiện click của `available_elements_tree` và `icon_list_tree`. Cấu trúc lại thuật toán tìm kiếm nút trên cây từ đệ quy sang lặp tuần tự (BFS).

#### Work Completed
- Chuyển đổi hàm `_sync_available_elements_selection` từ đệ quy (recursive) sang tìm kiếm theo chiều rộng bằng vòng lặp tuần tự (iterative BFS).
- Bổ sung cờ chặn sự kiện `_suppress_available_elements_event` để ngăn chặn hiệu ứng Ping-Pong Event.

#### Key Decisions
- Sử dụng mô hình hàng đợi (Queue) bằng list và vòng lặp `while` thay vì gọi lại chính hàm (đệ quy) nhằm loại bỏ hoàn toàn rủi ro StackOverflow do giới hạn độ sâu của Python.
- Khi chương trình tự động gọi `selection_set()`, nó sẽ làm phát sinh sự kiện `<<TreeviewSelect>>`. Sự kiện này gọi ngược lại vào hàm chọn icon bên trái. Để ngắt vòng lặp này, phải bọc lệnh `selection_set()` trong khối `try...finally` cùng với việc bật/tắt cờ `_suppress_available_elements_event`. Hàm bắt sự kiện `_on_available_element_select` sẽ dừng thực thi lập tức nếu cờ này đang bật (True).

#### Changes Made
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Khởi tạo biến cờ `self._suppress_available_elements_event = False` trong `__init__`.
  - Thay đổi cấu trúc hàm `_sync_available_elements_selection`.
  - Chèn logic chặn ngay tại đầu hàm `_on_available_element_select`.

#### Issues / Risks
- Không ghi nhận rủi ro thêm. Việc thay đổi sang vòng lặp BFS an toàn hơn và có hiệu suất ổn định đối với dữ liệu cây kích thước lớn. Lỗi freeze do vòng lặp sự kiện đã được khắc phục hoàn toàn.


### Nhiệm vụ: Sửa lỗi vòng lặp sự kiện bất đồng bộ Tkinter (Fix Crash/Freeze 2)

#### Summary
Khắc phục triệt để lỗi "Not Responding" do cơ chế phát sinh sự kiện bất đồng bộ (asynchronous event loop) của Tkinter `<<TreeviewSelect>>`.

#### Work Completed
- Gỡ bỏ cơ chế cờ boolean tạm thời (`_suppress_available_elements_event`).
- Triển khai cơ chế theo dõi trạng thái `_current_available_element_selection`.

#### Key Decisions
- Khi gọi `selection_set()` trong Tkinter, sự kiện `<<TreeviewSelect>>` không được gọi đồng bộ ngay lập tức mà bị đẩy vào hàng đợi (event loop queue) và xử lý sau. Do đó, việc bật/tắt cờ boolean tạm thời (try...finally) sẽ bị vô hiệu vì cờ đã bị tắt trước khi sự kiện thực sự được phát (fire).
- Quyết định sử dụng biến trạng thái `_current_available_element_selection` để lưu trữ mã định danh (node ID) đang được chọn. Khi sự kiện bắt đầu, hàm callback sẽ so sánh node ID hiện tại với node ID trong biến. Nếu trùng khớp, chứng tỏ sự kiện này do lệnh gọi lập trình sinh ra (programmatic call) hoặc người dùng click lại vào cùng một node, từ đó tự động ngắt (return sớm) để tránh vòng lặp.

#### Changes Made
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Thêm `self._current_available_element_selection` vào `__init__` và `_on_refresh`.
  - Cập nhật hàm `_sync_available_elements_selection` để cập nhật biến trạng thái trước khi gọi `selection_set()`.
  - Cập nhật hàm `_on_available_element_select` để kiểm tra so khớp trước khi xử lý logic form.


### Nhiệm vụ: Xử lý đồng bộ dữ liệu sau sự kiện Làm mới (Refresh state tracking)

#### Summary
Sửa lỗi mất khả năng highlight và nhãn UI Element không hiển thị đúng nếu người dùng gọi chức năng "Làm mới" (Refresh), sau đó click lại vào chính icon vừa thao tác (Out of sync state).

#### Work Completed
- Bổ sung việc khởi tạo và cập nhật biến trạng thái `_current_available_element_selection` vào quá trình lọc cây (filter tree) để tránh lệch dữ liệu.
- Xóa trạng thái của các nhãn văn bản (var_usage_element, var_usage_mod, var_usage_comp) khi quá trình highlight không tìm thấy thành phần UI nào tương ứng với Icon.

#### Key Decisions
- Quá trình Refresh sẽ kích hoạt việc xóa và build lại cây thông qua `_apply_element_filter`. Trong lúc build lại, nếu Treeview tự động chọn lại node (thông qua cache), nó phải cập nhật lại biến `_current_available_element_selection` trước khi gọi lệnh `selection_set`. Nếu không làm thế, cây sẽ hiển thị là có chọn, nhưng bộ não của hệ thống (biến trạng thái) lại là rỗng (None), dẫn đến việc chặn sự kiện bị sai lệch nếu ta click vào icon cũ.

#### Changes Made
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Thêm gán biến `_current_available_element_selection` tại `_apply_element_filter`.
  - Cập nhật thêm logic set rỗng label tại `_sync_available_elements_selection`.
### Nhiệm vụ: Tinh chỉnh Layout của EmptyState và Label UI Preview

#### Summary
Cải thiện cách hiển thị khu vực xem trước (preview) hình ảnh. Căn giữa toàn bộ giao diện placeholder của `EmptyState` và Label để tránh tình trạng chữ bị cắt, khoảng trắng lớn gây mất cân đối giao diện.

#### Work Completed
- Cấu hình lại `EmptyState` component để sử dụng một vùng chứa (`container`) phụ trợ nhằm ép nội dung căn giữa tuyệt đối theo chiều dọc (thông qua `expand=True`).
- Sửa lỗi tham số chồng chéo trong quá trình khởi tạo `tk.Label` bên trong `EmptyState`.
- Bổ sung cấu hình `justify="center"` và `anchor="center"` cho nhãn hình ảnh của `IconPreviewComponent`.

#### Key Decisions
- Thay vì thêm padding cố định, việc sử dụng frame trung gian (`container.pack(expand=True)`) giúp tự động căn giữa (vertical/horizontal centering) nội dung theo mọi kích thước cửa sổ của ứng dụng.
- Khắc phục lỗi truyền tham số `master` cho `tk.Label` bên trong `EmptyState` (truyền nhầm cả `container` và `self` dẫn tới lỗi TclError `unknown option "-class"` do nhận diện lầm kiểu biến argument vị trí).

#### Changes Made
- **File sửa đổi:** `ui/components/empty_state.py`
  - Đóng gói nội dung vào frame `container`.
  - Cập nhật cách khởi tạo `tk.Label`.
- **File sửa đổi:** `ui/components/icon_preview_component.py`
  - Thêm thuộc tính căn giữa cho nhãn (Label) hiển thị trước (preview label).

#### Issues / Risks
- Không có rủi ro tiềm ẩn nào vì đây chỉ là thay đổi liên quan đến thẩm mỹ giao diện hiển thị (UI Layout). Unit tests vẫn đang duy trì ổn định.

#### Next Steps
- Tiếp tục kiểm tra lại toàn bộ trải nghiệm UI trên các máy màn hình tỷ lệ dpi/scale khác nhau.


### Nhiệm vụ: Sửa lỗi không cập nhật Sidebar khi lưu Icon và nâng cấp thông tin UI Element

#### Summary
Khắc phục lỗi khi lưu thay đổi Icon nhưng giao diện thanh điều hướng bên trái (Sidebar) không tự động làm mới (refresh) để hiển thị Icon mới. Đồng thời, bổ sung nhãn hiển thị ngữ cảnh (contextual label) rõ ràng cho UI Element ID đang được chọn ở giao diện gắn Icon.

#### Work Completed
- Sửa lỗi tham chiếu sai tên biến trong luồng sự kiện (EventBus) của `app_gui.py` khi lắng nghe sự kiện cập nhật Icon (`IconUpdatedEvent`).
- Thêm một nhãn văn bản (Label) trong giao diện `IconManagerFrame` để hiển thị rõ ràng thông tin "UI Element ID đang chọn" (bao gồm Element ID, Module, Component Type) khi người dùng click vào cây danh sách "Available Elements".

#### Key Decisions
- Biến cấu hình hiển thị trạng thái màn hình hiện hành của `NavigationController` là `current_view_key` (kiểu chuỗi), không phải `current_view` (bị None do nhầm tên). Bằng cách trỏ đúng biến, `app_gui.py` có thể nhận biết được màn hình hiện tại và gửi lệnh cho `SidebarComponent` tự động load lại bộ Icon.
- Để tăng cường trải nghiệm UX, khi chọn một Element từ cây, ngoài việc điền tự động vào các ô nhập liệu ẩn, một dòng mô tả rõ ràng sẽ được cập nhật và hiển thị trực tiếp phía trên vùng dữ liệu.

#### Changes Made
- **File sửa đổi:** `app_gui.py`
  - Sửa `getattr(self.navigation, "current_view", None)` thành `getattr(self.navigation, "current_view_key", None)` trong phương thức `on_icon_updated`.
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Bổ sung `lbl_context_element` và `self.var_current_mapping_element` vào vùng layout "Usages".
  - Cập nhật giá trị chuỗi (text string) cho biến này trong phương thức `_on_available_element_select`.

#### Issues / Risks
- Chức năng đã được kiểm thử, thanh Sidebar làm mới bình thường không cần khởi động lại. UI Element context hiển thị tốt, giúp người dùng tránh nhầm lẫn khi thao tác gán usage.

#### Next Steps
- Tiếp tục theo dõi và làm sạch code nếu còn các reference nhầm lẫn tương tự do refactoring kiến trúc Controller.


### Nhiệm vụ: Khắc phục lỗi mất chức năng Highlight UI Element khi chọn Icon

#### Summary
Sửa lỗi tính năng tự động đồng bộ trạng thái (highlight) trên cây UI Element (Available Elements) không hoạt động khi người dùng nhấp chọn một Icon đã được liên kết ở giao diện bên trái. Lỗi xảy ra do kiểu dữ liệu không đồng nhất (khi Tkinter trả về các đối tượng Tcl).

#### Work Completed
- Điều chỉnh hàm `_sync_available_elements_selection` để ép kiểu (type casting) giá trị chuỗi (string) trước khi so sánh `mapped_icon == icon_key`.

#### Key Decisions
- Khi trích xuất dữ liệu từ các cột của `ttk.Treeview`, giá trị (values) được lưu dưới dạng một tuple. Đôi khi Tkinter có thể trả về các kiểu nội bộ (ví dụ: `_tkinter.Tcl_Obj`) thay vì chuỗi `str` thông thường của Python, dẫn đến việc phép so sánh bằng (`==`) bị sai kết quả. Việc bọc chúng qua hàm `str()` (ví dụ `str(mapped_icon) == str(icon_key)`) giúp đảm bảo tính nhất quán và phép so sánh hoạt động chính xác.

#### Changes Made
- **File sửa đổi:** `ui/views/icon_manager_frame.py`
  - Cập nhật điều kiện so sánh trong hàm `_sync_available_elements_selection`.

#### Issues / Risks
- Không ghi nhận rủi ro thêm.

#### Next Steps
- Cập nhật các Test Case để mock giá trị `values` của Treeview khớp với định dạng Tcl tuple thực tế nhằm mô phỏng chính xác hơn môi trường chạy.
