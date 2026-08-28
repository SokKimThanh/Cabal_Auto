# Roadmap Tương Lai Cho Màn Hình Chính

## 1. Phạm vi và trạng thái

Tài liệu này là output của session UX5. Đây là roadmap đề xuất, không phải xác nhận rằng các micro-session layout đã được triển khai. Mọi UI thay đổi sau roadmap phải đi theo thứ tự và timebox trong [SESSION_WORKLOAD_AND_PRIORITY.md](../.jules/prompts/ui-main-screen-cleanup/SESSION_WORKLOAD_AND_PRIORITY.md), cùng ownership rules trong [UI_MANAGEMENT_AND_OWNERSHIP.md](../.jules/prompts/ui-main-screen-cleanup/UI_MANAGEMENT_AND_OWNERSHIP.md).

Mục tiêu là biến màn hình chính thành command center cho luồng:

1. chọn game window
2. xác nhận readiness của bounds/target region
3. chọn và điều chỉnh monster rotation
4. Start Hunt
5. theo dõi trạng thái và xử lý warning
6. Stop Hunt hoặc mở cấu hình chuyên sâu khi cần

## 2. Layout budget động

Các kích thước dưới đây là visual-weight baseline khi cửa sổ maximize tại `1920x1080` với Windows DPI `100%`. Chúng không phải pixel bắt buộc trong runtime.

| Zone | Baseline 100% DPI | Quy tắc co giãn |
| --- | --- | --- |
| App Header | cao mục tiêu `56 px` | giữ identity/language; text không bị cắt khi font scale |
| Vùng A: Quick Action Bar | cao mục tiêu `80 px` | giữ Start/Stop, Window selector, Refresh và bounds state luôn thấy |
| Vùng C1: Sidebar | rộng mục tiêu `280 px`, `minsize=250 px` | dùng grid `weight`; tối đa `300 px` ở baseline; dưới `1280 px` thu gọn accordion/navigation |
| Vùng B: Workspace | phần lớn diện tích còn lại, mục tiêu `1640 x 744 px` | dùng grid `weight`; primary panels xếp dọc nếu không đủ chiều rộng |
| Vùng C2: Bottom Logs | cao mục tiêu `200 px` | có collapse rõ ràng; mặc định collapsed khi cao dưới `900 px` |

Tại Windows DPI `125%-150%`, đánh giá bằng hierarchy, minsize, khả năng đọc, keyboard focus, không overlap và responsive fallback. Không dùng `place()` hoặc width/height tuyệt đối để ép layout khớp baseline.

## 3. Zone allocation table

Mỗi feature chỉ có một zone hiển thị chính. Không tạo bản sao UI của config/runtime state ở zone khác.

| Feature | Zone | Visual priority | Layout budget và responsive behavior | Owner / source of truth | Dependency |
| --- | --- | --- | --- | --- | --- |
| Window selector | A | P0 | Giữ rộng đủ tên window; không ẩn khi hẹp | App UI / AppWindowController selection | UX1, UX2.2 |
| Refresh window list | A | P0 | Icon/button cạnh selector; không co xuống sidebar | App UI / window-list flow hiện có | UX1, UX2.2 |
| Bounds readiness | A | P0 | Text wrap/rút gọn có tooltip; không bị đẩy xuống logs | App UI render / normalized bounds từ WindowSelectionService | UX1B |
| Start Hunt / Stop Hunt | A | P0 | Luôn keyboard focusable; Start dominant khi idle, Stop dominant khi running | App UI / callback hunt hiện có | UX1, UX2.2 |
| Hunt state + active target | B | P0 | Primary panel; xếp dọc dưới `1280 px` | HuntTab render / runtime status hiện có | UX2B.1, UX4 |
| Monster rotation + quick actions | B | P0 | Primary panel, list scroll độc lập; không bị logs ép thấp hơn `360 px` | HuntTab / rotation config & callbacks hiện có | UX2B.1 |
| Quick skill slots/status | B | P1 | Strip dưới primary panels; collapse/scroll nội bộ nếu DPI làm thiếu cao | HuntTab / existing skill vars and bindings | UX2B.2 |
| Quick setup and mode entry | C1 | P1 | Sidebar `minsize=250 px`; thu gọn navigation/accordion khi hẹp | SetupTab / existing setup config | UX3, UX3B |
| Manager entry points | C1 | P1 | Nhóm Quick Setup → Managers → Configuration → Support | Existing manager callbacks | UX3 |
| Template/target-region configuration entry | C1 | P1 | Entry point, không hiển thị deep form mặc định | SetupTab / config flow hiện có | UX3B |
| Hotkey summary/config entry | C1 | P1 | Summary nhỏ; full configuration mở khi cần | SetupTab / hotkey config hiện có | UX3B |
| Recent activity | C2 | P2 | Bounded, scrollable, collapsed ở chiều cao thấp | Bottom Logs UI / existing thread-safe source only | UX4B.1, UX4B.2 |
| Technical diagnostics | C2 | P3 | Chỉ mở rộng theo thao tác người dùng; không thay primary status | Bottom Logs UI / existing source only | UX4B.2 |
| Warning history | C2 | P3 | Chỉ lịch sử; warning chặn Start vẫn ở A/B | Bottom Logs UI / existing runtime messages | UX4, UX4B.2 |
| Run summary dashboard | C2 | P3 | Compact summary; không thay Stats chuyên sâu | New view owner / existing aggregated runtime data only | Sau UX4B.2 |
| Hunt presets | C1 | P2 | Entry point/sidebar; apply result phản ánh ở A/B | Dedicated preset service, not UI state | Sau UX3B |
| Smart recommendations | B | P3 | Một recommendation actionable, dismissible; không tạo panel cố định | Recommendation service / explicit runtime inputs | Sau status data ổn định |
| Pause / Resume / Skip | A | P2 | Chỉ thêm khi runtime action và hotkey contract tồn tại | Hunt controller/orchestrator | Sau khi runtime hỗ trợ |

## 4. Roadmap theo giai đoạn

### Giai đoạn 0: Nền an toàn và layout

Thực hiện `UX1 → UX1B → UX2.1 → UX2.2`. Kết quả mong đợi là action loop P0 hoạt động trong outer shell mới nhưng không thay đổi hunt logic, config shape hoặc bounds normalization.

Điều kiện qua giai đoạn:

- Window selector, Refresh, Start và Stop còn callback/binding.
- bounds readiness chỉ đọc dữ liệu đã chuẩn hóa; không có UI-owned `window_bounds`.
- layout không overlap tại baseline và vẫn usable tại DPI `125%-150%`.

### Giai đoạn 1: Workspace và Sidebar

Thực hiện `UX2B.1 → UX2B.2 → UX3 → UX3B`. Kết quả là Monster Rotation và Active Target/Status có priority cao nhất trong workspace; setup/manager chuyển thành entry point phụ.

Điều kiện qua giai đoạn:

- rotation list scroll độc lập khi dài.
- skills nằm ở strip phụ, không che primary panels.
- sidebar không rộng quá budget và không chứa warning blocking.
- Beginner/Intermediate/Advanced giữ nguyên persistence và route cấu hình.

### Giai đoạn 2: Runtime observability

Thực hiện `UX4 → UX4B.1 → UX4B.2`. Kết quả là user hiểu trạng thái ngay trong B; C2 chỉ cung cấp recent activity/technical history.

Điều kiện qua giai đoạn:

- blocking warning có text và recovery action tại A/B.
- Bottom Logs không tự mở rộng làm giảm primary panels dưới `360 px`.
- log rendering dùng source thread-safe hiện hữu, Main Thread delivery và cleanup rõ ràng.

### Giai đoạn 3: Cải tiến sau khi có evidence

Chỉ thực hiện sau khi Giai đoạn 0-2 đã pass smoke, boundary và manual layout checks:

1. Compact run summary tại C2.
2. Hunt preset entry point tại C1, với preset service/source of truth riêng.
3. Pause/Resume/Skip tại A, chỉ khi controller/hotkey contract đã hỗ trợ.
4. Smart recommendation đơn lẻ tại B, chỉ khi có input runtime đáng tin cậy và user có thể dismiss.

Không đưa full Stats, Help, full template manager, full skill manager hoặc debug dashboard vào A/B.

## 5. Primary readiness và recovery

| Runtime condition | Nơi hiển thị chính | Nội dung | Recovery action | Source of truth |
| --- | --- | --- | --- | --- |
| Bounds hợp lệ | A và B summary | `Window ready`, tên window | Start Hunt / Capture region | normalized bounds hiện có |
| Chưa chọn window | A và B summary | `Chưa chọn cửa sổ game` | Chọn window hoặc Refresh | selected-window state hiện có |
| Bounds sai/thiếu | A và B summary | `Không thể dùng biên cửa sổ` | Refresh hoặc chọn lại window | normalized bounds hiện có |
| Window minimized/unavailable | A và B summary | Lý do không thể hunt | Restore game, Refresh hoặc chọn lại window | window lookup/runtime state hiện có |
| Target region không hợp lệ | A/B warning, C1 entry point | `Vùng target nằm ngoài game window` | Capture/chỉnh lại region | existing target-region validation |
| Hunt running | A và B | target hiện tại và `Running` | Stop Hunt | hunt runtime state hiện có |
| Hunt blocking error | A và B | lỗi ngắn gọn | recovery theo lỗi | hunt runtime state hiện có |

Không condition nào trong bảng được giải quyết bằng một state UI mới hoặc bằng cách chỉ ghi log ở C2. C2 chỉ được lưu history/context sau khi A/B đã có state actionable.

## 6. Kiến trúc và lifecycle

- `App._build_ui()` sở hữu outer layout, Header và Vùng A; không sở hữu business state.
- `HuntTab` sở hữu render trong Vùng B; controller/orchestrator vẫn sở hữu runtime state.
- `SetupTab` hoặc UI module tách có chủ đích sở hữu C1; manager logic ở service/window hiện có.
- C2 chỉ render snapshot từ source thread-safe. Worker/service không gọi Tkinter trực tiếp; delivery qua `after(0, ...)` hoặc `queue.Queue`.
- Rebuild language, close/dispose và callback chạy muộn phải không render vào widget đã destroy.
- Khi không có source log thread-safe rõ ràng, UX4B.2 bị blocked; không thay bằng polling/worker mới trong session UI.

## 7. Quyết định chống feature bloat

Không thêm feature mới vào main screen nếu feature đó không thỏa ít nhất một điều kiện:

1. được dùng ở core loop mỗi phiên hunt;
2. ngăn thao tác sai hoặc cho recovery của trạng thái blocking;
3. giảm số bước để bắt đầu/dừng/monitor hunt;
4. có source of truth, owner và lifecycle rõ ràng.

Nếu không thỏa, feature phải ở C1, C2, manager chuyên biệt hoặc chỉ nằm trong roadmap.

## 8. Xác nhận UX5

- Zone allocation: passed. Mỗi feature đề xuất đã có đúng một zone chính, priority, layout budget, owner/source và dependency.
- Bounds boundary model: passed. Valid, missing, invalid/minimized và invalid target region đều có primary display/recovery; không tạo bounds UI state thứ hai.
- Dynamic layout: passed. Baseline `1920x1080` được định nghĩa là visual-weight target tại 100% DPI; grid/minsize/weight và responsive fallback là điều kiện thực thi.
- UI implementation evidence: deferred. UX5 không sửa Python UI; các giai đoạn implementation phải cung cấp smoke, boundary, visual và lifecycle evidence trước khi mở feature Giai đoạn 3.