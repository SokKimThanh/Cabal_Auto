# Đặc Tả Kỹ Thuật: Hệ Thống UI Composite & Tiêu Chuẩn Component (UI Component Management System)

## 1. Tổng Quan & Mục Tiêu

Hệ thống quản lý UI Component của ứng dụng được xây dựng dựa trên **Composite Pattern** kết hợp với **Event-Driven Architecture (Kiến trúc Hướng sự kiện)**.

Thay vì lưu cấu hình UI tĩnh (như vị trí, loại nút) vào Database, hệ thống sử dụng Python code để linh hoạt "lắp ghép" các component độc lập (Views, Panels, Buttons) lại với nhau. Cơ sở dữ liệu (SQLite) chỉ đóng vai trò là Nguồn Sự Thật Đơn Lẻ (Single Source of Truth - SSoT) cho **Dữ liệu cấu hình** và **Từ điển dịch thuật (i18n)**, tuyệt đối không chứa logic vẽ giao diện.

**Mục tiêu chính:**
- **Kiến trúc Lắp ghép (Composite Pattern):** Xây dựng giao diện bằng cách lắp ghép các widget nhỏ, độc lập thành các cụm lớn hơn (ví dụ: `ActionBarView`, `SidebarComponent`) mà không phụ thuộc vào God Class `App`.
- **Đồng bộ Giao diện Siêu tốc (Reactive Sync):** Sử dụng `EventBus` để đồng bộ trạng thái, ngôn ngữ, icon ngay lập tức trên toàn ứng dụng mà không cần render lại (destroy/recreate) hay query Database.
- **Tuân thủ Chặt chẽ MVC & UI Style V2:** Tách biệt View và Controller. Giao diện luôn nhất quán về màu sắc, kích thước, padding thông qua các helper từ namespace `ui.helpers.UIHelper`.
- **An toàn Bộ nhớ:** Quản lý vòng đời (Lifecycle) chặt chẽ, các UI component phải tự dọn dẹp (unbind) các listener khi bị hủy để tránh memory leak.

---

## 2. Nguyên Tắc Lắp Ghép (Composite & Zoning)

Ứng dụng không sử dụng mô hình "Hardcoded View Registry" tại `app_gui.py`. Việc quản lý không gian được chia thành các phân khu (Zone) chính thông qua `AppShell`, sau đó các View/Component tự do gắn vào đó:

- **Zone A (`shell_zone_a`):** Action Bar / Thanh công cụ trên cùng.
- **Zone B (`shell_zone_b`):** Vùng làm việc chính / Workspaces (Quản lý bởi `NavigationController`).
- **Zone C1 (`shell_zone_c1`):** Sidebar / Thanh điều hướng bên trái.

**Quy tắc Khởi tạo:**
1. Các thành phần giao diện (như nút, nhãn, combobox) phải là các **thuộc tính cục bộ (local attributes)** của View/Panel chứa nó.
2. Tuyệt đối không lưu trữ các UI widget (như `tk.Listbox`, `ttk.Button`) vào các Controller tập trung (như `AppStateController`).

---

## 3. Hệ Thống Đồng Bộ Giao Diện (Reactive Synchronization)

Khả năng đồng bộ giao diện (chuyển ngôn ngữ, cập nhật trạng thái) được thực hiện qua mô hình "Phát - Nhận" (Publisher - Subscriber) thay vì truy vấn cấu hình từ Database.

### 3.1. Đồng Bộ Ngôn Ngữ & Text (TranslationBinder)
- Không query Database khi vẽ UI.
- Thay vào đó, các component sử dụng cơ chế `TranslationBinder`. Khi ứng dụng đổi ngôn ngữ, `EventBus` phát ra `LanguageChangedEvent`.
- Mọi component đang hiển thị (đã subscribe) sẽ nhận được sự kiện, tra cứu vào bộ từ điển đang nạp sẵn trên RAM (Cache) và tự gọi lệnh `.config(text="chuỗi_mới")`.
- **Lợi ích:** Đồng bộ siêu tốc, không giật lag, không phá vỡ layout. Giữ nguyên trạng thái (`state=DISABLED` hay `NORMAL`) của nút.

### 3.2. Quản Lý Icon Động
- Quản lý bộ nhớ Garbage Collection (GC) nghiêm ngặt: Khi cập nhật ảnh động cho widget (như Button hay Label), phải luôn giữ một tham chiếu mạnh (strong reference) trong class (VD: `self._current_icon = new_photoimage`) trước khi gán cho widget. Nếu không, Python GC sẽ thu hồi ảnh và giao diện sẽ hiển thị vùng trắng.

### 3.3. Tooltip Tương Tác
- Tooltip không sử dụng tooltip mặc định của HĐH. Chúng được gắn thông qua hàm `ui.helpers.tooltip.attach_i18n_tooltip`.
- Nội dung Tooltip được dịch động (dynamic i18n) tại thời điểm hiển thị (display-time) thông qua callback, đảm bảo luôn đúng ngôn ngữ mới nhất.

---

## 4. Giao Tiếp Và Điều Phối (Decoupling with EventBus)

Để các UI Component hoàn toàn độc lập, chúng tuyệt đối không được chứa logic nghiệp vụ và không gọi trực tiếp qua lại giữa các Controller.

- **Kích hoạt Hành động:** Một thao tác bấm nút (Button Click) chỉ được làm duy nhất một việc: Gửi yêu cầu qua EventBus hoặc gọi một Controller chuyên biệt.
  - *Ví dụ Tốt:* `command=lambda: self.event_bus.emit(StartStopHuntEvent())`
  - *Ví dụ Tốt:* `command=lambda: self.skill_controller.set_preset(...)`
  - *Ví dụ Xấu:* `command=lambda: self.app.start_hunt()` (Coupling với God Class).
- **Phản hồi Giao diện:** Khi Controller xử lý xong logic dưới nền (Thread), nó sẽ đẩy kết quả cập nhật về UI bằng cách phát ra một Event mới hoặc cập nhật vào `AppStateController`. Các biến `tk.StringVar`, `tk.BooleanVar` của `AppStateController` sử dụng hàm `.trace_add()` để tự động phản ứng lại thay đổi và vẽ lại UI.
- **An toàn Luồng (Thread Safety):** Mọi sự kiện EventBus hoặc callback từ Thread nền yêu cầu thay đổi Tkinter UI phải được bọc trong `root.after(0, ...)` để đảm bảo chỉ chạy trên luồng chính (Main Thread).

---

## 5. Tiêu Chuẩn Giao Diện (UI Style V2)

Tất cả các Component khi khởi tạo phải tuân theo bộ quy chuẩn thẩm mỹ từ `lib.ui_style_v2.py`.

- **Style Role:** Sử dụng các Semantic Role chuẩn như `primary`, `danger`, `info`, `neutral`, `icon`. (Tham chiếu `ROLE_STYLES` trong `button_styles.py`).
- **Màu sắc & Padding:** Không hardcode màu sắc kiểu `#FFFFFF` hay khoảng cách tĩnh. Phải dùng hằng số định nghĩa sẵn (VD: `THEME_BG_PANEL`, `PADDING_MEDIUM`).
- **Helper Cốt lõi:** Sử dụng các hàm dựng sẵn trong thư mục `lib/ui/components/` (ví dụ: `create_icon_button`) thay vì tự tạo lại widget gốc `ttk.Button`, để đảm bảo mọi nút đều có cấu hình chuẩn mực nhất.

---

## 6. Xử Lý Vòng Đời & Rủi Ro (Lifecycle & Memory Risks)

### 6.1. Rò Rỉ Bộ Nhớ (Memory Leak)
- **Rủi ro:** Khi một component (như Panel cấu hình) bị hủy nhưng vẫn còn đăng ký lắng nghe sự kiện trên `EventBus`, hệ thống sẽ cố gọi hàm cập nhật trên một widget đã bị tiêu hủy, gây crash (`_tkinter.TclError`).
- **Giải pháp:** Bắt buộc áp dụng phương thức `unbind()`. Mọi View/Component phải lưu lại tham chiếu của listener khi `bind()`, và chủ động gọi `self.event_bus.unbind(event_type, self._listener)` trong hàm dọn dẹp (VD: `destroy()` hoặc `on_hide()`).

### 6.2. Treo Giao Diện (UI Freeze)
- **Rủi ro:** Sử dụng vòng lặp `while` quá nhanh hoặc `time.sleep()` trong các callback của UI.
- **Giải pháp:** Đối với các tác vụ thăm dò định kỳ (polling) hoặc background (như queue log), sử dụng `TaskScheduler` (`schedule_task`, `schedule_recurring_task`). Phân biệt rõ One-off task và Loop Task để tránh ngập lụt hàng đợi UI.

---

## 7. Giao Diện Quản Lý (Data Managers vs UI Component Manager)

Trong kiến trúc Composite hiện tại, khái niệm xây dựng một màn hình **"UI Component Manager"** (để kéo thả, cấu hình vị trí, gán hàm Action cho các nút) đã bị **hủy bỏ**.

Việc chỉnh sửa layout, định tuyến sự kiện (routing events) phải được thực hiện trực tiếp bằng code Python bởi Developer để đảm bảo tính an toàn, dễ review qua Git và tránh Over-engineering.

Thay vào đó, hệ thống tập trung vào việc xây dựng các **Data Managers** để quản lý "Nội dung" (dữ liệu) mà các UI Component đó sẽ tiêu thụ:
- **Icon Manager:** Quản lý kho icon, cập nhật ảnh, cấp phát các `icon_key`. Giao diện (Buttons/Labels) chỉ cần tham chiếu đến `icon_key` này, khi ảnh thay đổi trong Icon Manager, UI sẽ tự động tải lại (Reactive Sync).
- **Translation Manager (Dự kiến):** Giao diện cho phép Admin/User chỉnh sửa các bản dịch (i18n). Khi bản dịch thay đổi, EventBus sẽ kích hoạt việc cập nhật text trên toàn bộ Component.

**Tóm lại:** Layout và Logic (Nút bấm, Vị trí) được quản lý bằng Code. Nội dung (Hình ảnh, Chữ viết) được quản lý bằng các Data Managers độc lập.
