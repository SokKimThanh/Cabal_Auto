# Playbook Chỉnh Sửa UI Theo Từng Khu Vực

## Cách dùng

Đọc tài liệu này sau `UI_MANAGEMENT_AND_OWNERSHIP.md` và trước prompt session. Mỗi session chỉ thực hiện khu vực hoặc slice được giao. Không gộp thay đổi của hai khu vực vào cùng một session, trừ UX2 chỉ tạo outer shell.

## Quy tắc DPI và tolerance

Các kích thước `1920x1080` trong playbook là mục tiêu thiết kế khi Windows DPI ở `100%`, không phải điều kiện pass/fail theo pixel tuyệt đối. Ở DPI `125%-150%`, widget có thể chênh lệch vài pixel do Tk scaling; pass khi hierarchy, min size, khả năng đọc, focus, không overlap và responsive fallback vẫn đúng.

Target dimensions (for example, Sidebar `280 px`) are baselines for 100% scaling at `1920x1080`. Use `minsize` and grid `weight` to keep the layout stable and flexible across different resolutions and DPI scaling factors (`125%`, `150%`). Do not hardcode absolute widths that break when scaled.

- Sidebar nhắm tới `280 px`, `minsize=250 px`, tối đa `300 px` ở baseline; dùng grid weight/content measurement để co giãn an toàn.
- Header, Action Bar và Bottom Logs giữ chiều cao mục tiêu, nhưng không cắt text/control do font scaling; ưu tiên wrap, collapse hoặc scroll theo spec.
- Không dùng `place()` hoặc tọa độ tuyệt đối để ép layout khớp pixel.

## Bản đồ UI hiện tại sang layout mục tiêu

| UI hiện tại | Chủ sở hữu hiện tại | Khu vực mục tiêu | Cách xử lý |
| --- | --- | --- | --- |
| `top` frame, language combobox, `win_combo`, Refresh, `hunt_start_btn`, `hunt_stop_btn` | `App._build_ui()` | Vùng A | Giữ callback; sắp lại thứ tự, kích thước và thêm bounds display qua UI hook |
| `notebook`, `tab_hunt`, `tab_setup`, `tab_stats`, `tab_help` | `App._build_ui()` | Vùng B/C1 tạm thời | Giữ tương thích trong UX2; chỉ giảm emphasis hoặc tách nội dung ở session riêng |
| Hunt status frame, `monster_frame`, `skill_frame_outer`, `skill_stats_frame` | `HuntTab._build_ui()` | Vùng B | Dùng grid nội bộ để ưu tiên Rotation + Active Status; skills là strip thấp hơn |
| Mode frame, hotkey frame, advanced frame, window/template frame | `SetupTab._build_ui()` | Vùng C1 | Chỉ dùng entry point hoặc progressive disclosure; không chuyển tất cả deep settings cùng lúc |
| `_db_status_bar` | `App._build_ui()` | C2 tạm thời | Có thể giữ như global status; không tự coi nó là nguồn recent logs |

## 1. App Header - 1920 x 56 px

### Mục tiêu UI

- Hiển thị identity ứng dụng, language selector và global context ngắn gọn.
- Không đặt Start/Stop, bounds warning chi tiết, manager entry point hoặc deep settings ở đây.

### Cách chỉnh sửa

1. Trong `App._build_ui()`, tạo `header_frame` làm child trực tiếp của App/root layout.
2. Đặt chiều cao `56 px`, tắt geometry propagation phù hợp và dùng surface `UIStyle.BG_TITLE`.
3. Đặt title bên trái; language selector và global metadata ở bên phải.
4. Giữ callback đổi ngôn ngữ hiện có. Rebuild phải tạo lại toàn bộ widget header sau khi children cũ đã bị destroy.

### Không làm trong zone này

- Không đưa window selection, Refresh, Start hoặc Stop vào header.
- Không đặt logic state/hunt/config vào widget header.

### Kiểm tra

- Đổi language rebuild được header mà không giữ widget reference cũ.
- Header luôn `56 px` tại baseline và không cắt selector.

## 2. Vùng A - Quick Action Bar, 1920 x 80 px

### Widget nguồn

- `win_combo_var`, `win_combo`
- `refresh_btn`
- `hunt_start_btn`, `hunt_stop_btn`
- separator hiện có trong `App._build_ui()`

### Mục tiêu UI

Người dùng hoàn thành luồng chọn game window → kiểm tra readiness → Start/Stop mà không mở tab hoặc scan vùng phụ.

### Thứ tự và kích thước bắt buộc

| Thứ tự | Control | Kích thước / hành vi |
| ---: | --- | --- |
| 1 | Window selector | `420 x 36 px`; vẫn bind click và `<<ComboboxSelected>>` như hiện tại |
| 2 | Refresh | `44 x 36 px`; giữ callback `on_hunt_refresh_windows` |
| 3 | Bounds readiness | tối thiểu `260 x 36 px`; text state + recovery action |
| 4 | Start Hunt | `160 x 44 px`; xanh primary khi idle |
| 5 | Stop Hunt | `160 x 44 px`; đỏ danger khi running, disabled khi idle |
| 6 | Hotkey/warning summary | tối thiểu `260 x 36 px`; metadata, không thay warning blocking ở bounds state |

### Cách chỉnh sửa

1. UX1 chỉ sắp lại visual hierarchy, gap `12 px`, padding ngang `32 px`, min size và màu token của controls đang có.
2. UX1B tạo một widget bounds display do App/Vùng A sở hữu. Widget chỉ render state đã chuẩn hóa; không ghi vào config.
3. Gắn refresh display vào hook UI đã tồn tại, ví dụ `_update_window_bounds_display`, sau select-window và refresh-window thành công.
4. Khi bounds bị thiếu/sai/minimized, text phải nêu action: chọn window, Refresh hoặc Restore game. Không chỉ đổi màu.
5. Giữ nguyên callback Start/Stop. Chỉ disable Start nếu flow hiện hữu đã coi prerequisite là blocking; không tự thay đổi policy runtime trong UI session.

### Không làm trong zone này

- Không di chuyển Monster Rotation, skill setup, SetupTab hoặc logs vào action bar.
- Không tạo `window_bounds`/`hunt_selected` state thứ hai.
- Không đổi hotkey hoặc signature callback.

### Kiểm tra

- Valid selected window: state cập nhật sau select và Refresh.
- No window: state có recovery action.
- Minimized/invalid state khi runtime hiện có cung cấp dữ liệu: state có recovery action.
- `1920x1080`: không control nào wrap, clip hoặc nhỏ hơn kích thước tối thiểu.

## 3. Vùng C1 - Secondary Configuration Sidebar, 280 x 944 px

### Widget nguồn

- Mode selector, hotkey, advanced settings và template/window settings trong `SetupTab._build_ui()`.
- Entry point manager hiện có; không tạo manager mới.

### Mục tiêu UI

Sidebar cho phép mở setup và manager khi cần, nhưng không biến thành form cấu hình đầy đủ luôn hiển thị.

### Cách chỉnh sửa

1. UX2 chỉ tạo `sidebar_container` ở outer shell, rộng `280 px`, `minsize=250 px`, nền `UIStyle.BG_PANEL` hoặc `UIStyle.BG_SECTION`.
2. UX3 chỉ tạo navigation slice: các action mở Setup/Monster/Skill/Library/Timing/Stats/Help từ callback đã có.
3. UX3B mới xử lý disclosure slice trong SetupTab, dùng mode/accordion để chỉ hiện common settings trước.
4. Sắp thứ tự sidebar: Quick Setup → Managers → Configuration → Support.
5. Giữ template/target-region và hotkey là entry point. Bounds warning blocking vẫn render ở Vùng A/B.
6. Sidebar content dài phải cuộn trong sidebar, không làm workspace hẹp hơn baseline.

### Không làm trong zone này

- Không chuyển tất cả form của SetupTab vào sidebar trong một session.
- Không để Sidebar điều khiển trực tiếp Start/Stop hoặc window runtime.
- Không dùng green/red cho navigation bình thường.

### Kiểm tra

- Beginner: common setting thấy ngay; warning bounds vẫn thấy ở A/B.
- Advanced: entry point deep setting vẫn truy cập được và không làm rộng sidebar quá `300 px`.
- Resize `1280-1599 px`: sidebar chỉ giảm tới `250 px` hoặc content chuyển accordion.

## 4. Vùng B - Active Hunt Workspace, 1640 x 744 px

### Widget nguồn

- `status_frame`, `hunt_status`, `hunt_target_info`
- `monster_frame`, `monster_rotation_listbox`, add/move/delete actions
- `skill_frame_outer`, skill slots, `skill_stats_frame`

### Mục tiêu UI

Đây là command center. Rotation và Active Target/Status cùng hiện để người dùng nhìn thấy configuration đang chạy lẫn trạng thái runtime trong một lần nhìn.

### Layout nội bộ bắt buộc

| Panel | Kích thước baseline | Cách dùng |
| --- | --- | --- |
| Monster Rotation | `776 x 552 px` | Listbox scroll độc lập, add/move/delete và manager entry point |
| Active Target & Status | `776 x 552 px` | Hunt state, target hiện tại, bounds summary, warning và recovery action |
| Quick Skill View | `1576 x 120 px` | Slot/key/cooldown tóm tắt hoặc entry point; không thay Skill Manager |

### Cách chỉnh sửa

1. UX2B đổi layout nội bộ của HuntTab sang grid theo hai panel primary; không đổi `StringVar`, listbox binding hoặc callback hiện có.
2. Tách status display khỏi hàng status mỏng hiện tại thành Active Target & Status panel nếu có thể chỉ bằng di chuyển widget/view layer; không thay đổi business state.
3. Rotation list dùng `sticky="nsew"`, row/column weight và scrollbar độc lập.
4. Skill slots/stats được giảm visual weight và đặt thành Quick Skill View strip. Nếu không thể ghép an toàn trong timebox, giữ widget hiện hữu và chỉ tạo container/entry point cho session sau.
5. UX4 chỉ sửa render text/màu/icon cho ready, warning, error và recovery action. Không tạo runtime status mới.

### Không làm trong zone này

- Không chuyển log technical detail vào Workspace.
- Không thay hunt loop, monster persistence, skill selection behavior hoặc config shape.
- Không dùng màu warning/danger làm nền toàn panel.

### Kiểm tra

- Empty rotation: layout ổn định, add action còn truy cập được.
- Long rotation: list scroll không đẩy status panel ra ngoài.
- Valid/no/invalid bounds: warning hoặc ready state vẫn nhìn thấy ở A/B.
- `1920x1080`: hai panel primary cùng hiện, Quick Skill View nằm phía dưới.

## 5. Vùng C2 - Bottom Status / Secondary Logs, 1640 x 200 px

### Widget nguồn

- `_db_status_bar` chỉ là global DB status hiện tại, không mặc định là log source.
- Chỉ dùng source recent activity đã tồn tại và thread-safe. Nếu chưa xác định source, session chỉ tạo container/empty state và ghi blocker.

### Mục tiêu UI

Cho phép xem lịch sử kỹ thuật ngắn gọn mà không buộc người dùng mở debug log, đồng thời không lấy mất attention khỏi state cần hành động trong A/B.

### Cách chỉnh sửa

1. UX2 tạo `bottom_logs_container` ở outer shell, đặt `200 px` và không đè Sidebar/Workspace.
2. UX4B thêm scrollable recent activity view nếu source dữ liệu có sẵn; giới hạn số dòng render trong UI.
3. Khi chiều cao dưới `900 px`, panel mặc định collapsed qua action rõ ràng. Không tự mở rộng vì log dài.
4. UI owner nhận log snapshot qua Main Thread. Không truy cập trực tiếp background log writer hoặc thêm worker/polling loop không có cleanup.
5. Dùng surface neutral; warning/error chỉ highlight trên từng entry cùng text, không tô toàn panel.

### Không làm trong zone này

- Không biến Bottom Logs thành nơi duy nhất chứa warning chặn Start.
- Không đổi log format, persistence, background thread hay logging framework.

### Kiểm tra

- Không có log: empty state ổn định.
- Log dài/lặp: scroll riêng, panel vẫn `200 px`.
- Bounds warning blocking vẫn ở A/B dù log panel collapsed.
- Close/rebuild: không còn callback/polling cố render vào widget đã destroy.

## Trình tự chỉnh sửa bắt buộc

1. UX1: Visual hierarchy Vùng A.
2. UX1B: Bounds readiness state Vùng A.
3. UX2: Outer shell cho bốn vùng.
4. UX2B: Layout Vùng B.
5. UX3: Sidebar navigation Vùng C1.
6. UX3B: Progressive disclosure trong SetupTab.
7. UX4: Status rendering Vùng B.
8. UX4B: Bottom Logs Vùng C2 khi có source thread-safe.
9. UX5: Roadmap dựa trên evidence đã có.