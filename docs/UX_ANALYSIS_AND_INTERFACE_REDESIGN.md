# Phân Tích và Thiết Kế Lại Giao Diện Chính của Ứng Dụng

## 1. Mục tiêu tài liệu

Tài liệu này nhằm đánh giá giao diện hiện tại của Cabal Auto Hunt, xác định các luồng thao tác quan trọng, và định hình lại bố cục màn hình chính theo nguyên tắc ưu tiên thực tế của người dùng:

- chức năng nào cần dùng thường xuyên phải nổi bật nhất
- chức năng phụ, không phải thao tác hàng ngày, phải giảm trọng tâm
- màn hình chính phải tập trung vào workflow hunt, không biến thành kho chứa cài đặt và popup
- người dùng phải hoàn thành hành động chính trong vài giây, với ít thao tác và ít nhầm lẫn

Mục tiêu cốt lõi là giúp người dùng thực hiện luồng hunt một cách trực quan, nhanh chóng và ổn định, đặc biệt khi làm việc trong phần mềm tự động hóa game có nhiều trạng thái và cảnh báo đồng thời.

---

## 2. Vấn đề cốt lõi của giao diện hiện tại

Ứng dụng hiện có các chức năng mạnh: hunt, monster rotation, skill manager, library manager, hotkey, template matching, overlay, setup wizard, stats và help. Tuy nhiên, các chức năng này đang bị phân tán giữa nhiều vùng UI khác nhau:

- thanh trên cùng
- các tab chính
- các cửa sổ manager riêng
- các popup cấu hình phụ
- trạng thái runtime ẩn trong logs, status bar hoặc cửa sổ phụ

Điều này khiến giao diện hiện tại không phản ánh đúng thứ tự ưu tiên của người dùng. Người dùng phải nhớ vị trí control, chuyển qua nhiều tab và nhiều màn hình để thực hiện hành động cốt lõi. Với một công cụ tự động hóa, điều này làm giảm tốc độ thao tác, tăng lỗi và làm trải nghiệm không mượt.

Workflow cốt lõi cần được hỗ trợ rõ ràng hơn:

1. chọn cửa sổ game
2. xác định mục tiêu / vùng hunt
3. chọn monster hoặc rotation
4. bắt đầu hunt
5. theo dõi trạng thái hoạt động
6. dừng, chỉnh sửa hoặc khởi động lại khi cần

---

## 3. Người dùng mục tiêu và hành vi chính

### 3.1 Người dùng mục tiêu

- người mới bắt đầu, cần hiểu flow nhanh
- người dùng trung bình, cần thao tác thường xuyên và rõ ràng
- người dùng nâng cao, cần tùy chọn cấu hình sâu nhưng không muốn bị làm chậm workflow chính

### 3.2 Hành vi chính

Khi đang dùng app, người dùng chủ yếu làm những việc sau:

- chọn cửa sổ game
- refresh danh sách window hoặc mục tiêu
- bắt đầu / dừng hunt
- thêm, xóa, sắp xếp monster trong rotation
- xem trạng thái target, target đang hoạt động, warning hoặc mất target
- mở manager / cửa sổ phụ khi cần cấu hình chuyên sâu

Những thao tác này là “core loop” và phải được ưu tiên trong bố cục chính.

---

## 4. Phân loại chức năng theo mức ưu tiên

### 4.1 Chức năng ưu tiên cao nhất

Nhóm này phải nằm ở vị trí dễ nhìn nhất, trực tiếp trên màn hình chính:

1. Chọn cửa sổ mục tiêu
2. Refresh danh sách cửa sổ
3. Start Hunt
4. Stop Hunt
5. Monster rotation / danh sách mục tiêu đang chạy
6. Trạng thái hunt hiện thời
7. Quick actions: thêm, xóa, di chuyển monster

Những tính năng này là “nút sống” của app.

### 4.2 Chức năng ưu tiên cao

Nhóm này không cần chiếm vị trí trung tâm nhưng cần dễ truy cập:

1. template / target area
2. hotkey toàn cục
3. thiết lập nhanh cho hunt
4. mode Beginner / Intermediate / Advanced
5. global apply hoặc apply nhanh

### 4.3 Chức năng ưu tiên trung bình

Nhóm này nên nằm ở panel phụ hoặc manager chuyên biệt:

1. Monster Manager
2. Skill Manager
3. Library Manager
4. Timing Calculator
5. Template management

### 4.4 Chức năng ưu tiên thấp

Nhóm này hỗ trợ hoặc báo cáo nhưng không nên chiếm tâm điểm của màn hình chính:

1. Stats tab
2. Help tab
3. log / debug / status chi tiết
4. cảnh báo kỹ thuật và troubleshooting

Các chức năng này nên dễ truy cập nhưng không làm mất trọng tâm của hunt.

---

## 5. Đánh giá giao diện hiện tại

### 5.1 Điểm mạnh

1. Chức năng nền tảng đã có đầy đủ
   - window detection
   - hunt workflow
   - monster rotation
   - skill config
   - library manager
   - setup wizard
   - hotkey support

2. Có sự phân tách tương đối rõ giữa nghiệp vụ và UI control
   - các tab và controller đang dần được tách rõ ràng hơn về trách nhiệm

3. Có vùng điều hướng nhanh ở thanh trên cùng
   - language, window selection, refresh, start/stop giúp workflow bắt đầu nhanh hơn

4. Có chế độ Beginner / Intermediate / Advanced
   - hỗ trợ giảm nhiễu khi người dùng mới bắt đầu

### 5.2 Điểm yếu

1. Chưa phản ánh đúng thứ tự ưu tiên của người dùng
   - các thao tác quan trọng bị rải rác trên nhiều khu vực

2. Chức năng phụ đang “dính” quá nhiều vào màn hình chính
   - người dùng phải quét nhiều nơi mới tìm được control cần dùng

3. Một số tab như Stats, Help hoặc các panel mạng lưới thị sai trọng tâm
   - chưa mang lại giá trị trực tiếp bằng workflow hunt

4. Thao tác “mỗi lần bắt đầu hunt” chưa đủ tập trung
   - người dùng không thấy ngay trạng thái hoạt động và mục tiêu hiện tại

5. Thiếu trạng thái toàn cảnh rõ ràng
   - người dùng nên nhìn vào màn hình và biết ngay app đang ở trạng thái nào: idle, hunting, warning, error, target lost

---

## 6. Luồng thao tác chính cần tối ưu hóa

### 6.1 Luồng bắt đầu sử dụng mới

1. mở app
2. chọn ngôn ngữ
3. chọn cửa sổ game
4. xác nhận template / vùng target
5. chọn monster hoặc rotation
6. bắt đầu hunt

Đây là workflow bắt đầu và phải dễ thực hiện ngay từ lần đầu mở app.

### 6.2 Luồng hunt đang chạy

1. kiểm tra target
2. xem trạng thái hunt
3. phát hiện target hoặc mất target
4. điều chỉnh rotation hoặc skill nếu cần
5. dừng / reset / chạy lại

Đây là chuỗi quan trọng nhất của phần mềm; giao diện chính phải hỗ trợ luồng này tốt nhất.

### 6.3 Luồng cấu hình phụ

1. mở manager
2. sửa monster / skill / timing
3. lưu
4. quay lại main screen

Đây là luồng cấu hình, không nên chiếm vị trí chính. Chúng phải dễ truy cập nhưng không làm nhiễu workflow chính.

---

## 7. Kiểm tra biên cửa sổ và vùng target

### 7.1 Vai trò trong workflow

Kiểm tra biên cửa sổ game (`window_bounds`) là điều kiện bắt buộc để hunt, overlay và template capture hoạt động đúng. Đây không phải là cài đặt phụ: người dùng cần biết app đang dùng đúng cửa sổ, biên cửa sổ còn hợp lệ và vùng target không vượt ra ngoài game window.

Luồng cần được hỗ trợ trên UI:

1. người dùng chọn hoặc refresh cửa sổ game
2. app đọc và chuẩn hóa biên cửa sổ theo dạng `[x, y, width, height]`
3. UI hiển thị cửa sổ đã chọn và trạng thái biên hợp lệ / không hợp lệ
4. khi người dùng capture hoặc chỉnh target region, vùng chọn phải bị giới hạn trong biên cửa sổ game
5. trước khi Start Hunt, app phải cảnh báo rõ nếu chưa chọn window, biên không hợp lệ hoặc cửa sổ đang minimized

### 7.2 Quy tắc UX bắt buộc

- hiển thị target window hiện tại gần action chọn window
- hiển thị trạng thái biên dưới dạng dễ hiểu: `Ready`, `Missing`, `Invalid` hoặc `Window minimized`
- sau khi refresh hoặc đổi window, UI phải cập nhật lại biên đang dùng
- không cho người dùng hiểu nhầm rằng biên cũ vẫn hợp lệ sau khi cửa sổ đổi vị trí, bị thu nhỏ hoặc bị minimize
- target/template region phải được kiểm tra nằm trong game window khi UI có khả năng kiểm tra
- cảnh báo phải chỉ rõ hành động khắc phục: refresh window, chọn lại window hoặc restore game window

### 7.3 Điều kiện biên cần kiểm tra

1. Chưa chọn cửa sổ game.
2. Dữ liệu biên thiếu hoặc sai định dạng.
3. Width hoặc height không lớn hơn 0.
4. Cửa sổ bị minimize, nhận tọa độ Windows không hợp lệ như `-32000`.
5. Cửa sổ game đã thay đổi vị trí hoặc kích thước sau lần chọn trước.
6. Target region rỗng, quá nhỏ hoặc nằm một phần / toàn bộ ngoài biên game window.
7. Không thể lấy lại thông tin cửa sổ theo HWND/PID đã lưu.

### 7.4 Trạng thái và hành động mong đợi

| Tình trạng | UI cần hiển thị | Hành động khả dụng |
| --- | --- | --- |
| Chưa chọn window | `Chưa chọn cửa sổ game` | Chọn window, Refresh |
| Biên hợp lệ | `Window ready` | Start Hunt, Capture region |
| Biên không hợp lệ | `Không thể dùng biên cửa sổ` | Refresh, chọn lại window |
| Cửa sổ minimized | `Game window đang thu nhỏ` | Restore game, Refresh |
| Region không hợp lệ | `Vùng target nằm ngoài game window` | Chọn lại region |
| Không tìm thấy cửa sổ | `Không tìm thấy cửa sổ đã chọn` | Refresh, chọn window khác |

Không cần thay đổi config shape để đạt được các yêu cầu này. UI phải sử dụng luồng chuẩn hóa và cập nhật bounds hiện có, không tạo thêm nguồn dữ liệu biên thứ hai.

---

## 8. Thiết kế lại bố cục màn hình chính theo thứ tự ưu tiên

### 8.1 Bố cục đề xuất

Màn hình chính nên chia thành 3 vùng rõ ràng:

#### Vùng A: Quick Action Bar
Vị trí: hàng trên cùng

Chứa các control thao tác nhanh nhất:

- chọn cửa sổ game
- refresh
- trạng thái biên cửa sổ / target window
- start hunt
- stop hunt
- language selector
- trạng thái hotkey / warning ngắn gọn

Mục tiêu: cho phép người dùng bắt đầu làm việc trong vài giây.

#### Vùng B: Active Hunt Workspace
Vị trí: phần lớn không gian giữa màn hình

Chứa các dữ liệu đang hoạt động:

- monster rotation hiện hành
- target info / active target status
- skill slot quick view
- trạng thái hunt
- quick actions thêm/xóa/di chuyển monster

Mục tiêu: tập trung thông tin và giữ workflow hunt ở trung tâm.

#### Vùng C1: Secondary Configuration Sidebar
Vị trí: cột bên trái, ngay dưới Quick Action Bar

Chứa entry point cho setup, hotkey, template/target bounds, manager, stats và help. Sidebar chỉ là điều hướng và cấu hình mở khi cần; không hiển thị đồng thời toàn bộ deep configuration.

#### Vùng C2: Bottom Status / Secondary Logs
Vị trí: đáy cửa sổ, bên dưới Active Hunt Workspace

Chứa log gần đây, status kỹ thuật và cảnh báo chi tiết có thể mở rộng. Vùng này không được cạnh tranh với trạng thái hành động đang hiển thị trong Active Target & Status.

Mục tiêu của hai vùng C: giữ chức năng đầy đủ nhưng đưa cấu hình sâu và thông tin kỹ thuật ra khỏi trọng tâm của hunt.

### 8.2 Nguyên tắc thiết kế

- primary actions phải lớn, rõ, dễ thấy
- secondary settings phải nằm ở mức thứ yếu
- vùng status phải dễ hiểu trong một lần nhìn
- người mới phải thấy flow rõ: chọn game → chọn monster → bắt đầu
- các manager chuyên biệt là “mở khi cần”, không nên lộ quá nhiều trên màn hình chính

---

### 8.3 Phân bổ kích thước chuẩn cho Desktop 1920x1080

Phần này là baseline thiết kế bắt buộc cho các session UI, giả định cửa sổ ứng dụng maximize trên Desktop `1920x1080 pixels` với Windows DPI `100%`, không tính viền hệ điều hành. Đây không phải phép kiểm tra pixel tuyệt đối: ở DPI `125%-150%`, kích thước render có thể chênh lệch nhẹ do Tk scaling trong hierarchy, min size, khả năng đọc, focus, không overlap và fallback responsive vẫn đúng. Layout chuẩn có bốn vùng: App Header, Quick Action Bar, Secondary Configuration Sidebar và vùng trung tâm gồm Active Hunt Workspace + Bottom Status / Secondary Logs.

#### Khung tổng thể

| Khu vực | Tọa độ chuẩn | Kích thước mục tiêu | Mục đích |
| --- | --- | --- | --- |
| App Header | `x=0, y=0` | `1920 x 56 px` | Tên app, language và trạng thái tổng quát |
| Vùng A: Quick Action Bar | `x=0, y=56` | `1920 x 80 px` | Chọn window, Refresh, bounds state, Start, Stop |
| Vùng C1: Secondary Sidebar | `x=0, y=136` | `280 x 944 px` | Setup, manager, template, hotkey, stats, help |
| Vùng B: Active Hunt Workspace | `x=280, y=136` | `1640 x 744 px` | Rotation, active target, hunt status và quick skill view |
| Vùng C2: Bottom Status / Logs | `x=280, y=880` | `1640 x 200 px` | Log gần đây, trạng thái kỹ thuật và cảnh báo chi tiết |

Tổng chiều cao nội dung dưới header và action bar là $1080 - 56 - 80 = 944$ px. Workspace có chiều cao $944 - 200 = 744$ px. Sidebar kéo dài toàn bộ `944 px` dưới top bar; bottom logs chỉ nằm dưới workspace, không nằm dưới sidebar.

#### Vùng A: Quick Action Bar - 80 px

Quick Action Bar dùng một hàng cao cố định `80 px`, padding ngang `32 px`, khoảng cách control `12 px`. Đây là vùng duy nhất chứa các action điều khiển hunt tức thời.

| Thành phần | Kích thước mục tiêu | Vị trí và ưu tiên |
| --- | --- | --- |
| Window selector | `420 x 36 px` | Mép trái, control đầu tiên |
| Refresh | `44 x 36 px` | Ngay sau Window selector |
| Bounds state | tối thiểu `260 x 36 px` | Ngay sau Refresh; luôn nhìn thấy |
| Start Hunt | `160 x 44 px` | Primary action khi idle |
| Stop Hunt | `160 x 44 px` | Primary action khi running; disabled khi idle |
| Hotkey / warning summary | tối thiểu `260 x 36 px` | Mép phải hoặc vùng còn lại |

Start và Stop không được thu nhỏ dưới `140 x 40 px`. Bounds state phải có đủ không gian cho trạng thái và recovery action ngắn như `Refresh` hoặc `Restore game` mà không cắt chữ.

#### Vùng C1: Secondary Configuration Sidebar - 280 px

Sidebar rộng cố định `280 px`, padding ngang `16 px`, padding dọc `20 px`. Sidebar dùng để điều hướng và mở cấu hình, không phải nơi hiển thị chi tiết runtime.

| Nhóm | Hành vi |
| --- | --- |
| Quick setup | Mode selector và common settings; chỉ mở nội dung cần dùng thường xuyên |
| Managers | Monster, Skill, Library và Timing là entry point mở cửa sổ/panel chuyên biệt |
| Configuration | Template, target region và hotkey có entry point rõ ràng; feedback biên vẫn phải hiện ở Vùng A/B |
| Support | Stats, Help và debug là action phụ ở cuối sidebar |

Sidebar phải dùng surface thứ yếu (`BG_PANEL` hoặc `BG_SECTION`), nhắm tới `280 px`, có `minsize=250 px` và không được rộng hơn `300 px` tại baseline 1920px. Dùng grid weight/content measurement để xử lý DPI scaling, không ép đúng `280 px` bằng tọa độ tuyệt đối.

#### Vùng B: Active Hunt Workspace - 1640 x 744 px

Workspace dùng padding `32 px` ngang, `24 px` dọc và gap `24 px`. Chiều rộng nội dung là $1640 - 32 - 32 = 1576$ px. Hai panel trọng tâm chia đều: $\frac{1576 - 24}{2} = 776$ px mỗi panel.

| Khu vực nội bộ | Kích thước mục tiêu | Nội dung |
| --- | --- | --- |
| Monster Rotation | `776 x 552 px` | Danh sách rotation, add/remove, move up/down và manager entry point |
| Active Target & Status | `776 x 552 px` | Hunt state, target hiện tại, bounds summary, warning và action needed |
| Quick Skill View | `1576 x 120 px` | Skill slot tóm tắt, cooldown/state và quick configuration entry point |

Hai panel trên cùng dùng chiều cao `552 px`; Quick Skill View cao `120 px` nằm bên dưới, với gap dọc `24 px`. Monster Rotation và Active Target & Status phải cuộn độc lập khi nội dung vượt chiều cao; Quick Skill View chỉ là tóm tắt, không thay thế Skill Manager.

#### Vùng C2: Bottom Status / Secondary Logs - 1640 x 200 px

Bottom panel cao cố định `200 px`, nằm sát đáy workspace. Mặc định hiển thị log gần đây và cảnh báo kỹ thuật cần đối chiếu; có thể mở rộng theo hành động rõ ràng của người dùng, nhưng không tự mở rộng làm giảm Active Hunt Workspace dưới `360 px`.

| Thành phần | Hành vi |
| --- | --- |
| Recent activity | Hiển thị số dòng giới hạn, cuộn độc lập |
| Technical detail | Metadata, debug detail và diagnostics thứ yếu |
| Warning history | Chỉ bổ sung ngữ cảnh; warning đang chặn Start Hunt vẫn phải ở Vùng A/B |

#### Ngưỡng responsive tối thiểu

| Kích thước cửa sổ | Hành vi bắt buộc |
| --- | --- |
| Rộng từ `1600 px` | Giữ Sidebar `280 px`, hai panel chính cân bằng và Quick Skill View dạng dải ngang |
| Rộng `1280-1599 px` | Sidebar có thể giảm tới `250 px`; hai panel chính vẫn tối thiểu `520 px` hoặc xếp dọc trong workspace |
| Rộng dưới `1280 px` | Sidebar thu gọn thành navigation/accordion; Active Target, Rotation và Quick Skill View xếp dọc; không ẩn bounds state hoặc Start / Stop |
| Cao dưới `900 px` | Bottom logs thu gọn mặc định; workspace và sidebar được cuộn; Quick Action Bar luôn thấy |

### 8.4 Quy tắc triển khai kích thước

- dùng `grid` với `weight`, `minsize` và `sticky="nsew"`; không phụ thuộc vào tọa độ tuyệt đối dù spec có tọa độ baseline
- xem kích thước baseline là design target tại Windows DPI `100%`; tại DPI `125%-150%`, đánh giá bằng hierarchy, readable/focusable control, không overlap, min size và fallback responsive, không so sánh pixel tuyệt đối
- dùng `minsize` cho Sidebar (`250 px`), Start, Stop, window selector và bounds state để control không biến mất hoặc bị cắt khi resize
- giữ hierarchy cố định: App Header → Quick Action Bar → Sidebar + Workspace → Bottom Logs
- panel phụ không được tự tăng chiều cao làm giảm Monster Rotation hoặc Active Target & Status dưới `360 px`
- status text dài phải wrap hoặc được rút gọn có tooltip; không làm thay đổi chiều cao Quick Action Bar
- không chuyển warning chặn Start Hunt xuống Sidebar hoặc Bottom Logs

---

## 9. Quy luật màu sắc bắt buộc (Visual Design)

### 9.1 Nguồn palette duy nhất

Mọi session cải tiến UI phải dùng palette tập trung trong `lib/ui_style.py` (`UIStyle`). Không tự tạo mã màu mới trong `app_gui.py`, tab, controller hoặc popup, trừ khi có cập nhật đồng thời vào `UIStyle` và nêu rõ lý do trong review.

| Vai trò thị giác | Token `UIStyle` | Màu | Được dùng cho |
| --- | --- | --- | --- |
| Primary action | `BTN_PRIMARY_BG` | `#2E7D32` | Start Hunt và action xác nhận có tác động chính |
| Danger action | `BTN_DANGER_BG` | `#F44336` | Stop Hunt, xóa hoặc hành động có tính phá hủy |
| Warning | `COLOR_WARNING` | `#FF7043` | Biên không hợp lệ, target lost, config cần xử lý |
| Information | `BTN_INFO_BG` / `COLOR_INFO` | `#1976D2` | Refresh, thông tin trạng thái, hướng dẫn không khẩn cấp |
| Accent / ready | `BTN_ACCENT_BG` / `COLOR_ACCENT` | `#00897B` / `#4CAF50` | Bounds hợp lệ, target ready, success state |
| Neutral / secondary | `BTN_NEUTRAL_BG` / `COLOR_MUTED` | `#757575` | Action phụ, disabled context, metadata |
| Base surface | `BG_DEFAULT` / `BG_PANEL` / `BG_SECTION` | `#FFFFFF` / `#F5F5F5` / `#E3F2FD` | Nền app, panel phụ, vùng nhóm thông tin |
| Body text | `COLOR_TEXT` / `COLOR_SUBTEXT` | `#212121` / `#666666` | Nội dung chính và metadata |

### 9.2 Ngữ nghĩa màu bắt buộc

- xanh lá chỉ dành cho hành động khởi chạy / xác nhận hoặc trạng thái sẵn sàng; Start Hunt là primary action duy nhất ở trạng thái idle
- đỏ chỉ dành cho Stop Hunt, lỗi nghiêm trọng hoặc hành động phá hủy; không dùng đỏ để trang trí hoặc cho action thông thường
- cam chỉ dành cho warning cần người dùng xử lý nhưng app chưa ở lỗi chặn
- xanh dương dùng cho thông tin, Refresh và action trung tính; không được cạnh tranh thị giác với Start Hunt
- xám dùng cho action phụ, metadata và trạng thái disabled; không dùng xám cho warning/error
- không dùng màu làm tín hiệu duy nhất: trạng thái luôn cần text, icon hoặc label rõ ràng đi kèm

### 9.3 Áp dụng cho workflow hunt và kiểm tra biên

| Trạng thái | Màu | Nội dung bắt buộc | Action / recovery |
| --- | --- | --- | --- |
| Chưa chọn window | Neutral hoặc Warning | `Chưa chọn cửa sổ game` | Chọn window hoặc Refresh |
| Bounds hợp lệ | Accent / ready | `Window ready` và tên window | Có thể Start Hunt / Capture region |
| Bounds thiếu hoặc sai | Warning | `Không thể dùng biên cửa sổ` | Refresh hoặc chọn lại window |
| Window minimized / unavailable | Warning hoặc Danger nếu Start bị chặn | Trạng thái và lý do | Restore game hoặc chọn lại window |
| Target region không hợp lệ | Warning | `Vùng target nằm ngoài game window` | Capture / chỉnh lại region |
| Hunt đang chạy | Accent / ready | `Running` và target hiện tại | Stop Hunt luôn thấy |
| Hunt lỗi chặn | Danger | Lý do lỗi ngắn gọn | Recovery action rõ ràng |

Warning và error phải dễ nhận biết ở Active Target & Status và Quick Action Bar khi có tác động đến Start Hunt. Không đặt background đỏ hoặc cam phủ toàn bộ workspace; chỉ tô vùng status, border hoặc callout liên quan để giữ màn hình dễ quét.

### 9.4 Phân cấp thị giác và surface

- App header dùng `BG_TITLE` với chữ trắng, không đặt nhiều màu action cạnh nhau trong header
- Quick Action Bar dùng `BG_DEFAULT`; Start/Stop là điểm nhấn màu mạnh nhất của hàng này
- Active Hunt Workspace ưu tiên nền `BG_DEFAULT`; mỗi panel có thể dùng border trung tính hoặc `BG_PANEL`, không dùng card lồng trong card
- Secondary Configuration Panel dùng `BG_PANEL` hoặc `BG_SECTION` để giảm trọng tâm so với workspace
- chỉ dùng một màu nhấn mạnh cho một action tại một thời điểm; khi hunt idle là Start, khi hunt running là Stop
- hover, pressed và disabled phải dùng token tương ứng trong `UIStyle`, không làm đổi ngữ nghĩa action

### 9.5 Khả năng đọc và accessibility

- dùng foreground đã định nghĩa trong `UIStyle` trên button background tương ứng; không tự chọn text màu nhạt trên nền màu
- giữ tương phản tối thiểu WCAG AA cho text thường, mục tiêu là $4.5:1$ hoặc cao hơn
- status/warning dài phải wrap trong vùng đã định, không dùng chỉ màu nền để chứa toàn bộ nội dung
- disabled control dùng `BTN_DISABLED_BG` và `BTN_DISABLED_FG`, đồng thời nêu lý do disabled gần control nếu Start Hunt bị chặn bởi bounds hoặc validation
- focus keyboard phải thấy được bằng border hoặc focus style rõ ràng, đặc biệt với Window selector, Refresh, Start và Stop

### 9.6 Điều cấm

- không thêm gradient, màu neon hoặc decorative color không có ý nghĩa vận hành
- không dùng nhiều hơn một màu trạng thái mạnh trong cùng một control
- không dùng màu primary/danger cho tab, panel hoặc text trang trí
- không hard-code hex color mới ngoài `UIStyle`
- không để màu của status thay đổi layout, kích thước control hoặc thứ tự ưu tiên của Quick Action Bar

### 9.7 Kiểm tra Visual Design trong mỗi session

Mỗi session có thay đổi giao diện phải xác nhận:

1. control mới hoặc control đổi vị trí dùng token `UIStyle` đúng ngữ nghĩa
2. Start, Stop, Refresh và bounds state không dùng trùng màu gây nhầm mức ưu tiên
3. valid / warning / error bounds vẫn có text và recovery action, không chỉ có màu
4. disabled state và keyboard focus vẫn đọc được trên nền tương ứng
5. không có mã màu hard-code mới ngoài trường hợp đã cập nhật `UIStyle`

---

## 10. Quản lý giao diện và ownership

Thiết kế UI chỉ bền vững khi từng vùng có owner rõ ràng. Composition root trong `app_gui.py` quản lý outer layout và liên kết callback; `HuntTab` quản lý widget trong Hunt Workspace; `SetupTab` quản lý setup/disclosure; controller/service quản lý business state và không trực tiếp tạo hoặc cập nhật Tkinter widget.

### 10.1 Contract quản lý bắt buộc

- chỉ Main Thread được gọi Tkinter methods; worker thread và service chuyển data qua `after(0, ...)` hoặc `queue.Queue`
- UI render từ source of truth hiện có, không tạo state config/runtime/window bounds trùng lặp
- `app_gui.py` chỉ sở hữu App Header, Quick Action Bar và bốn outer zones; không đưa chi tiết Rotation, Setup hoặc Logs vào composition root nếu zone owner có thể quản lý
- `HuntTab` chỉ quản lý Vùng B; `SetupTab` hoặc module tách có chủ đích quản lý Vùng C1; Bottom Logs có owner/lifecycle riêng nếu được tách
- selection và chuẩn hóa bounds vẫn thuộc controller/service hiện có; UI chỉ hiển thị kết quả đã chuẩn hóa
- UI chỉ giao tiếp giữa các zone qua callback public hoặc controller/service đã xác định, không thao tác trực tiếp widget của zone khác

### 10.2 Lifecycle và rebuild

- khi đổi ngôn ngữ, rebuild UI phải hủy widget/binding cũ và không để controller/service giữ reference widget đã hủy
- callback chạy muộn phải kiểm tra widget còn tồn tại trước khi render
- tooltip, modal, `after` polling hoặc queue polling do zone tạo phải có cleanup khi app/zone bị dispose
- không thêm polling loop mới trong session UX nếu chưa xác định owner, cleanup path và test shutdown

Chi tiết ownership matrix và checklist session nằm trong [UI_MANAGEMENT_AND_OWNERSHIP.md](../.jules/prompts/ui-main-screen-cleanup/UI_MANAGEMENT_AND_OWNERSHIP.md).

### 10.3 Cách chỉnh sửa cụ thể theo từng khu vực

Mỗi zone phải được chỉnh sửa theo widget nguồn, owner, layout budget và non-goal rõ ràng; không chỉ thay đổi bố cục theo cảm tính. Playbook chi tiết cho App Header, Vùng A, C1, B và C2 nằm trong [UI_ZONE_IMPLEMENTATION_PLAYBOOK.md](../.jules/prompts/ui-main-screen-cleanup/UI_ZONE_IMPLEMENTATION_PLAYBOOK.md).

Trình tự áp dụng bắt buộc là: hoàn thiện action bar → hiển thị bounds readiness → dựng outer shell → bố trí Hunt Workspace → xử lý Sidebar → làm rõ runtime status → thêm Bottom Logs. Không bắt đầu Bottom Logs khi chưa có data source thread-safe và lifecycle cleanup rõ ràng.

---

## 11. Định nghĩa “thao tác quan trọng” và “thao tác phụ”

### 11.1 Thao tác quan trọng, thường xuyên dùng, không thể thiếu

Những hành động dưới đây nên được ưu tiên trên main screen:

1. chọn target window
2. refresh danh sách window
3. start hunt
4. stop hunt
5. thêm / xóa / sắp xếp monster
6. xem trạng thái hunt hiện tại
7. xem target đang được nhắm / mất target / warning
8. chỉnh sửa cấu hình nhanh khi cần
9. kiểm tra biên cửa sổ và target region trước khi hunt

Các thao tác này là nhịp sống của phần mềm. Nếu không dễ thao tác, trải nghiệm sẽ giảm mạnh dù ứng dụng có rất nhiều chức năng.

### 11.2 Thao tác phụ

Những tính năng sau nên ở mức dễ truy cập nhưng không chiếm ưu tiên:

- deep tuning config
- log chi tiết
- help / tutorial
- stats dài hạn
- screen-specific manager

---

## 12. Chức năng nên hiển thị trực tiếp trên màn hình chính trong tương lai

### 12.1 Bắt buộc phải hiển thị trực tiếp

1. trạng thái hunt hiện thời
   - idle
   - running
   - warning
   - error
   - target lost

2. target window hiện tại
3. danh sách monster rotation active
4. nút start / stop rõ ràng
5. warning và “action needed” ngắn gọn
6. trạng thái biên cửa sổ game và target region

### 12.2 Nên hiển thị trực tiếp nhưng có thể giảm trọng tâm

1. quick view skill slots
2. quick config cho hunt mode
3. status của hotkey / keyboard shortcut
4. thông tin template hoặc target region

### 12.3 Nên nằm ở panel phụ hoặc manager chuyên biệt

1. full stats dashboard
2. full help documentation
3. advanced debug logs
4. detail tuning for templates / timings / libraries

---

## 13. Mục tiêu UX cần hướng đến

Giao diện của app nên giúp người dùng đạt được bốn điều trong từng phiên làm việc:

1. bắt đầu nhanh
2. hiểu trạng thái ngay lập tức
3. điều chỉnh khi cần mà không bị lạc trong menu
4. phát hiện và sửa lỗi biên cửa sổ trước khi hunt chạy sai vùng

Nói ngắn gọn: main screen phải là một “command center” cho hunt, không phải một dashboard rải rác với quá nhiều cài đặt.

---

## 14. Tiêu chí hoàn thành cho cải tiến giao diện

Mỗi lần cải thiện UI phải thỏa mãn các tiêu chí sau:

- primary controls rõ ràng hơn so với secondary settings
- action loop chính (select window → start → monitor → stop) luôn dễ thấy
- trạng thái hunt dễ được hiểu trong một lần nhìn
- target window, window bounds và lỗi biên quan trọng có thể được nhận biết và xử lý từ màn hình chính
- màu của action và status tuân thủ quy luật Visual Design, không tạo nhiễu hoặc làm sai nghĩa runtime state
- zone UI, source of truth và lifecycle cleanup có owner rõ ràng; không có worker/service gọi Tkinter trực tiếp
- không xóa tính năng đang có, chỉ thay đổi mức độ ưu tiên và nhóm hiển thị
- không làm vỡ behavior hiện tại, hotkey, config hoặc runtime flow

---

## 15. Kế hoạch thực hiện khuyến nghị

Tốt nhất là cải tiến theo từng bước nhỏ để dễ review và dễ rollback:

1. ưu tiên các action hunt chính lên top bar và panel chính
2. tái tổ chức layout theo 3 vùng rõ ràng
3. ẩn hoặc giảm trọng tâm cài đặt nâng cao
4. làm rõ trạng thái hunt và warning
5. đưa kiểm tra biên cửa sổ / target region vào luồng chọn window, capture và Start Hunt
6. áp dụng palette và quy luật màu sắc nhất quán cho action, status, warning và disabled state
7. định nghĩa roadmap cho các tính năng future-facing trên màn hình chính

Việc cải tiến UI nên tránh “đổi cả màn hình trong một lần” mà nên tập trung từng tầng ưu tiên, để người dùng không mất quen và không làm vỡ hành vi hiện tại.

Roadmap chi tiết về zone allocation, ownership, dynamic layout/DPI, readiness recovery và feature sequencing nằm trong [MAIN_SCREEN_FUTURE_ROADMAP.md](MAIN_SCREEN_FUTURE_ROADMAP.md).

---

## 16. Kết luận

Giao diện hiện tại có nền tảng chức năng đủ mạnh, nhưng nó chưa tối ưu hóa đúng thứ tự ưu tiên của người dùng. Vấn đề không nằm ở thiếu tính năng, mà ở việc các tính năng đúng mục đích chưa được sắp xếp theo trọng tâm hoạt động thực tế.

Nếu màn hình chính được tổ chức lại theo cấu trúc: primary actions → active hunt context → secondary settings, thì ứng dụng sẽ trở nên dễ dùng hơn, rõ ràng hơn, và phù hợp với workflow của người dùng game automation hơn rất nhiều.

