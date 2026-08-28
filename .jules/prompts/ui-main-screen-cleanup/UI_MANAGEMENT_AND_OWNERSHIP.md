# Quản Lý Giao Diện Và Ownership Contract

## Mục đích

Tài liệu này quy định cách quản lý giao diện trong quá trình UX cleanup. Mục tiêu là cải thiện layout mà không làm `app_gui.py` thành nơi chứa mọi widget, mọi state và mọi callback; đồng thời không cho background thread hoặc service cập nhật Tkinter trực tiếp.

## Ownership hiện tại và hướng quản lý

| Thành phần | Chủ sở hữu | Được phép quản lý | Không được phép quản lý |
| --- | --- | --- | --- |
| Application shell | `App._build_ui()` trong `app_gui.py` | Tạo root zones, top-level container, `Notebook`, composition và liên kết callback có sẵn | Logic hunt, parse config sâu, runtime loop, direct UI call từ worker |
| Vùng A: Quick Action Bar | `app_gui.py` | Window selector, Refresh, Start/Stop, bounds readiness display, top-level action layout | Monster rotation, manager form, log history chi tiết |
| Vùng B: Hunt Workspace | `ui/tabs/hunt_tab.py` | Widget nội bộ Hunt, Monster Rotation, active status và quick skill view | Tạo root shell, ghi config trực tiếp ngoài callback established |
| Vùng C1: Sidebar / setup content | `ui/tabs/setup_tab.py` hoặc module UI chuyên biệt khi được tách có chủ đích | Mode visibility, setup entry point, advanced disclosure | Window selection runtime, Start/Stop runtime state |
| Vùng C2: Bottom Logs | Module UI sở hữu log view hoặc `app_gui.py` tạm thời khi chưa tách | Chỉ render snapshot log/status từ source hiện có | Format log, persistence, worker-thread logging, blocking runtime warning source |
| Window selection + bounds | `AppWindowController` và `WindowSelectionService` | Chọn window, chuẩn hóa/cập nhật bounds và persistence hiện có | Tạo widget UI mới hoặc tự quản lý layout widget |
| Hunt runtime / status source | Controller/orchestrator hiện có | Business state và callback data | Gọi Tkinter trực tiếp từ background thread |

## Quy tắc cập nhật UI

1. Chỉ Main Thread được gọi Tkinter widget methods (`configure`, `set`, `insert`, `grid`, `pack`, dialog, Treeview, Label).
2. Background worker, controller hoặc service chỉ trả dữ liệu/callback-safe event. `App` hoặc tab owner nhận event qua scheduler UI đã có (`after(0, ...)`) hoặc `queue.Queue`.
3. UI owner render dữ liệu bằng một method cục bộ rõ ràng, ví dụ `refresh_bounds_state(...)` hoặc `render_hunt_status(...)`. Method render không được tự chạy business logic.
4. Không lưu state UI trùng với config/runtime source. Với bounds, UI đọc state đã được chuẩn hóa qua `normalize_window_bounds_value` và `WindowSelectionService.update_bounds`.
5. Không để widget của một zone bị thao tác trực tiếp từ tab/zone khác. Giao tiếp qua callback public hoặc controller/service đang sở hữu state.

## Quy tắc lifecycle

- `App._build_ui()` có thể bị gọi lại khi đổi ngôn ngữ; mọi top-level widget cũ bị hủy trước khi tạo lại.
- Tab owner phải tạo lại widget và binding của chính tab đó sau rebuild; không giữ reference widget cũ trong controller/service.
- Callback scheduled sau destroy phải kiểm tra widget còn tồn tại trước khi render.
- Mọi `after` định kỳ, queue polling, tooltip hoặc modal do zone tạo phải được hủy/dừng khi app hoặc zone bị dispose.
- Không thêm polling loop mới trong một UX session nếu chưa có owner, cleanup path và kiểm tra shutdown.

## Quy tắc layout và component

- `app_gui.py` quản lý grid/pack của 4 outer zones; mỗi tab chỉ quản lý layout bên trong zone của nó.
- Không trộn `pack` và `grid` trong cùng một parent container.
- Không reparent widget đang có giữa các parent trong cùng session nếu callback/binding chưa được kiểm tra; ưu tiên tạo container tương thích hoặc tách session.
- Component dùng lại phải nhận data và callback rõ ràng, không truy cập ngầm state của App ngoài contract đã khai báo.
- UI color/size sử dụng `UIStyle`; layout baseline lấy từ UX spec.

## Checklist bắt buộc cho mọi session

1. Nêu zone và UI owner bị thay đổi.
2. Nêu source of truth cho dữ liệu hiển thị.
3. Nêu cách event từ controller/worker trở về Main Thread.
4. Xác nhận không tạo state bounds/config/runtime trùng lặp.
5. Xác nhận rebuild đổi ngôn ngữ, close/dispose và callback muộn không làm cập nhật widget đã bị hủy.
6. Báo cáo widget/binding nào được tạo, di chuyển hoặc hủy.

## Khi nào được tách module mới

Chỉ tách module UI mới khi nó có một owner rõ ràng, ví dụ Bottom Logs cần polling lifecycle riêng hoặc Sidebar đủ lớn để không còn phù hợp trong SetupTab. Module mới phải có:

- parent/container rõ ràng
- input data và callback rõ ràng
- method `build`/`destroy` hoặc lifecycle tương đương
- không chứa business logic hoặc direct worker-thread UI call
- validation import/startup và cleanup path