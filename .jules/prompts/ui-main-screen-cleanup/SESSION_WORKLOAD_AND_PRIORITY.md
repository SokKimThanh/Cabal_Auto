# Đánh Giá Khối Lượng Và Thứ Tự Thực Hiện

## Kết luận

Không chạy nguyên trạng các prompt UX1-UX4 như một session duy nhất. Mỗi prompt hiện mô tả một epic UI, trong khi một session Jules chỉ có ngân sách `30 phút`, bao gồm đọc code, sửa code, chạy validation và kiểm tra biên.

Mục tiêu của một session là hoàn thành một thay đổi nhỏ có thể xác minh được, không phải hoàn thành một vùng UI đầy đủ. Nếu hết `25 phút`, dừng mở rộng scope, chạy validation và ghi phần còn lại thành session tiếp theo.

Nếu validation vẫn fail ở phút `30`, session phải đưa app về trạng thái runnable bằng cách hoàn tác **chỉ các edit do session đó tạo** qua patch có review. Không dùng `git reset`, `git checkout --` hoặc discard worktree vì có thể xóa thay đổi ngoài scope của user. Sau recovery, phải chạy lại smoke/import check và báo cáo failure root cause cùng next slice đã deferred.

## Cơ sở đánh giá

| Khu vực | Thực trạng kỹ thuật | Rủi ro thời gian |
| --- | --- | --- |
| `app_gui.py` | Top controls, `Notebook`, global apply và status bar đang dùng `pack` trong cùng một composition root | Di chuyển nhiều vùng cùng lúc dễ vượt 30 phút và vỡ resize/binding |
| `ui/tabs/hunt_tab.py` | Status, Monster Rotation và skill UI được xây trong cùng `_build_ui()` | Chỉnh hierarchy một panel có thể làm được; tái cấu trúc toàn workspace là quá lớn |
| `ui/tabs/setup_tab.py` | Mode visibility, hotkeys, advanced settings và template config cùng nằm trong tab | Chỉ nên thay đổi một lớp disclosure hoặc entry point mỗi session |
| Window/bounds flow | Selection và bounds update đi qua controller/service riêng | UI chỉ được hiển thị lại state hiện có; không được tạo state bounds mới |

## Điều kiện vào cho mọi session

Trước khi bắt đầu bất kỳ session nào, đọc [UI_MANAGEMENT_AND_OWNERSHIP.md](UI_MANAGEMENT_AND_OWNERSHIP.md) và [UI_ZONE_IMPLEMENTATION_PLAYBOOK.md](UI_ZONE_IMPLEMENTATION_PLAYBOOK.md), rồi ghi rõ zone owner, widget nguồn, source of truth, Main Thread update path, lifecycle/cleanup case. Nếu chưa xác định được năm mục này trong 10 phút đầu, dừng implementation và tạo session recon ngắn thay vì sửa widget trực tiếp.

## Backlog theo ưu tiên

| Thứ tự | Session | Timebox | Phạm vi tối đa | Dependency | Quyết định |
| --- | --- | ---: | --- | --- | --- |
| P0 | UX1 | 25-30 phút | Chỉ Quick Action Bar: thứ tự, kích thước, visual hierarchy cho controls đang có | Không | Làm trước |
| P0 | UX1B | 25-30 phút | Thêm/hoàn thiện bounds readiness state cạnh Window selector, dùng state chuẩn hiện có | UX1 | Làm ngay sau UX1 |
| P1 | UX2.1 | 25-30 phút | Chỉ tạo 4 parent frame rỗng với grid, weight, minsize; không di chuyển widget | UX1B | Làm sau khi P0 pass |
| P1 | UX2.2 | 25-30 phút | Chỉ reparent Quick Action Bar và Notebook vào container đã có | UX2.1 | Làm sau UX2.1 pass |
| P1 | UX2B.1 | 25-30 phút | Chỉ chia grid Monster Rotation và Active Target & Status; giữ skills ở vị trí tạm | UX2.2 | Làm sau UX2.2 pass |
| P1 | UX2B.2 | 25-30 phút | Chỉ di chuyển và style skills vào Quick Skill Strip `120 px` | UX2B.1 | Làm sau UX2B.1 pass |
| P1 | UX3 | 25-30 phút | Chỉ Sidebar navigation/entry points; không chuyển cả SetupTab | UX2.2 | Làm sau content migration |
| P1 | UX3B | 25-30 phút | Chỉ progressive disclosure trong SetupTab; không chuyển Sidebar/manager | UX3 | Làm sau Sidebar pass |
| P2 | UX4 | 25-30 phút | Chỉ Active Target & Status: ready/warning/error copy, màu và recovery action | UX1B, UX2B.1 | Làm sau primary panels pass |
| P2 | UX4B.1 | 20-25 phút | Chỉ tạo Bottom Logs container `200 px` và expand/collapse; không nối dữ liệu log | UX2.2 | Làm sau shell pass |
| P2 | UX4B.2 | 25-30 phút | Chỉ nối source log thread-safe và render text vào container đã có | UX4B.1 | Làm sau container pass |
| P3 | UX5 | 15-20 phút | Documentation-only roadmap và zone allocation table | UX1-UX4B.2 | Làm cuối |

`UX1B`, `UX2.1`, `UX2.2`, `UX2B.1`, `UX2B.2`, `UX3B`, `UX4B.1` và `UX4B.2` là session follow-up bắt buộc được tách từ các epic hiện có. Không gộp chúng vào UX1, UX2, UX2B, UX3 hoặc UX4B.

## Chi tiết session có thể hoàn thành trong 30 phút

### UX1 - Quick Action Bar

- Chỉ sửa composition của top controls đã tồn tại trong `app_gui.py`.
- Không đổi callback, hotkey, config, `Notebook`, HuntTab hay SetupTab.
- Mục tiêu: action order, min size, token màu và không clipping ở baseline `1920x1080`.
- Dừng session khi action bar đúng `80 px`; không bắt đầu tạo bounds widget mới nếu chưa có state binding rõ ràng.

### UX1B - Bounds readiness state

- Chỉ dùng `normalize_window_bounds_value` và `WindowSelectionService.update_bounds` qua flow có sẵn.
- Hiển thị một state cạnh Window selector: ready, missing, invalid hoặc minimized/unavailable khi runtime data cho phép.
- Không thay đổi config shape; không chuyển layout tổng thể.
- Xác minh valid bounds, no selected window và invalid/minimized window.

### UX2.1 - Core Grid Construction

- Chỉ tạo 4 parent frame rỗng: Quick Action Bar, Secondary Sidebar, Active Hunt Workspace và Bottom Status / Logs.
- Chỉ cấu hình `grid`, row/column `weight`, `minsize` và `sticky="nsew"` cho outer shell.
- Không di chuyển, reparent, destroy hoặc đổi callback/binding của bất kỳ widget hiện có nào.
- Exit condition: app khởi động, shell resize không overlap, và UI cũ vẫn hoạt động trong container hiện tại.

### UX2.2 - Content Migration

- Chỉ reparent Quick Action Bar và `Notebook` hiện có vào các container được tạo trong UX2.1.
- Giữ nguyên widget instance, callback, binding, hotkey, config và window/bounds source of truth.
- Không thay đổi layout bên trong HuntTab/SetupTab, không tạo Sidebar content, không tạo Bottom Logs content.
- Exit condition: Quick Action Bar và Notebook hiển thị trong parent mới, app khởi động, và controls/tab hiện có vẫn hoạt động.

### UX2B.1 - Primary Panels Split

- Chỉ cấu hình grid nội bộ cho Monster Rotation và Active Target & Status trong HuntTab.
- Giữ widget skills ở vị trí tạm thời hiện có; không di chuyển hoặc style lại skills trong session này.
- Không động Sidebar, SetupTab, Bottom Logs, config, callback hay hunt logic.
- Exit condition: hai primary panel hiển thị cùng lúc, list rotation cuộn độc lập và status không bị che.

### UX2B.2 - Quick Skill Strip

- Chỉ di chuyển và style widget skills hiện có vào Quick Skill View strip mục tiêu cao `120 px`.
- Giữ nguyên skill `StringVar`, combobox binding, clear action, skill stats behavior và manager entry point.
- Không đổi layout primary panels, không chỉnh status runtime hoặc tạo Skill Manager mới.
- Exit condition: skill strip không cạnh tranh thị giác với primary panels, không bị cắt và không làm panel chính thấp hơn `360 px`.

### UX3 - Sidebar navigation

- Chỉ tạo entry points cho Setup/Managers/Support.
- Không kết hợp việc chuyển tab, tạo manager mới, disclosure hoặc sửa mode persistence.
- Warning chặn Start Hunt không được chuyển vào Sidebar.

### UX3B - Setup progressive disclosure

- Chỉ chỉnh visibility common vs advanced settings trong SetupTab, giữ nguyên mode persistence.
- Không tạo/move Sidebar navigation, manager window hoặc runtime bounds state.
- Warning chặn Start Hunt không được chuyển vào Setup disclosure.

### UX4 - Active status

- Chỉ sửa status display/copy/visual hierarchy trong Active Target & Status.
- Mỗi state phải có text, màu token `UIStyle` và recovery action.
- Không tạo logging infrastructure và không chuyển logs.

### UX4B.1 - UI Collapsible Container

- Chỉ tạo Bottom Logs frame mục tiêu cao `200 px` cùng action expand/collapse.
- Không kết nối source log, không render log text, không đổi format log, persistence hay background thread.
- Khi chiều cao cửa sổ dưới `900 px`, trạng thái mặc định là collapsed.
- Exit condition: container không overlap Workspace/Sidebar, expand/collapse không làm primary panels thấp hơn `360 px`.

### UX4B.2 - Log Data Integration

- Chỉ kết nối Bottom Logs container đã có với source log thread-safe hiện hữu và render text bounded/scrollable.
- Không tạo worker, polling loop, logging infrastructure hoặc thay đổi log format/persistence.
- Dữ liệu từ worker phải đi qua Main Thread scheduler hoặc `queue.Queue`, có cleanup path khi destroy.
- Exit condition: empty state, repeated/long log entries và close/rebuild không làm lỗi UI; warning blocking vẫn ở Vùng A/B.

### UX5 - Roadmap

- Documentation-only; không sửa Python UI.
- Mỗi feature đề xuất phải có zone, visual priority, layout budget, dependency và lý do không thuộc Vùng A/B.

## Quy tắc dừng và chuyển việc

1. Không mở file ngoài phạm vi session sau phút thứ 10, trừ khi validation chỉ ra blocker trực tiếp.
2. Không bắt đầu session phụ thuộc khi session trước chưa pass smoke test và Session Boundary Gate.
3. Nếu thay đổi cần hơn hai module hoặc cần sửa callback/config, tách thành session mới thay vì tiếp tục.
4. Nếu validation còn fail ở phút `25`, chỉ sửa lỗi trực tiếp trong 5 phút còn lại; không bắt đầu feature/UI polish mới.
5. Nếu validation vẫn fail ở phút `30`, áp dụng recovery protocol và chạy lại check trước khi kết thúc session.
6. Nếu không thể chạy GUI thủ công trong timebox, hoàn thành validation tự động và ghi `manual-only`; không suy đoán kết quả UI.
7. UX5 chỉ bắt đầu khi layout implementation sessions đã cung cấp evidence hoặc khi roadmap được đánh dấu là đề xuất chưa triển khai.

## Tiêu chí ưu tiên

- P0: ngăn thao tác sai hoặc làm luồng hunt rõ hơn ngay lập tức.
- P1: tạo nền layout để các thay đổi sau không phải làm lại.
- P2: tăng khả năng quan sát và hỗ trợ troubleshooting, không thay đổi core workflow.
- P3: tài liệu hóa định hướng sau khi có evidence từ implementation.