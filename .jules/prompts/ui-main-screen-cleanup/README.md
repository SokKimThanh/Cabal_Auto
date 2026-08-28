# Prompt Jules Cho Cải Thiện Giao Diện Chính

Thư mục này chứa bộ prompt nhỏ để Jules làm các task UX cleanup trên màn hình chính, theo hướng ưu tiên thao tác quan trọng, giảm nhiễu chức năng phụ, và làm rõ luồng chính của người dùng.

## Mục tiêu tổng thể

- ưu tiên các thao tác thường dùng và không thể thiếu lên vùng dễ nhìn nhất
- giảm sự tản mát của chức năng phụ trên màn hình chính
- tạo một “command center” cho hunt, thay vì để màn hình chính trở thành kho chứa cài đặt và popup
- giữ nguyên logic hunt hiện có, không phá vỡ flow đang vận hành tốt
- khuyến khích cải tiến UI nhỏ, rõ ràng, dễ review và dễ rollback

## Mục tiêu thiết kế của bộ prompt

1. Màn hình chính phải đọc như workflow hướng hành động, không phải dashboard hỗn hợp.
2. Người dùng phải thấy ngay thứ tự ưu tiên: chọn window → xem trạng thái → bắt đầu hunt → monitor → dừng / sửa.
3. Cài đặt nâng cao không được cạnh tranh vị trí với tác vụ chính.
4. Các thành phần phụ vẫn tồn tại, nhưng phải ở mức độ ưu tiên thấp hơn.

## Quản lý giao diện

Trước khi chạy một prompt, Jules phải đọc [UI_MANAGEMENT_AND_OWNERSHIP.md](UI_MANAGEMENT_AND_OWNERSHIP.md). Tài liệu này xác định owner cho từng zone, source of truth, lifecycle khi rebuild/close và quy tắc Main Thread cho Tkinter.

Để biết chính xác cần sửa widget nào, đặt ở zone nào, giữ callback nào và không được làm gì trong từng session, Jules phải đọc thêm [UI_ZONE_IMPLEMENTATION_PLAYBOOK.md](UI_ZONE_IMPLEMENTATION_PLAYBOOK.md).

## Layout baseline bắt buộc

Trên Desktop `1920x1080` ở Windows DPI `100%`, mọi prompt phải nhắm tới cấu trúc bốn vùng trong UX spec. Đây là baseline thiết kế, không phải phép so sánh pixel tuyệt đối ở DPI khác.

| Vùng | Kích thước baseline | Trách nhiệm |
| --- | --- | --- |
| App Header | `1920 x 56 px` | App identity, language và global context |
| Vùng A: Quick Action Bar | `1920 x 80 px` | Window selector, Refresh, bounds state, Start, Stop |
| Vùng C1: Secondary Sidebar | `280 x 944 px` | Setup, manager, template, hotkey, stats và help entry points |
| Vùng B: Active Hunt Workspace | `1640 x 744 px` | Rotation, active target/status và quick skill view |
| Vùng C2: Bottom Status / Logs | `1640 x 200 px` | Recent activity, diagnostics và secondary logs |

Trong Workspace, Monster Rotation và Active Target & Status nhắm tới `776 x 552 px`; Quick Skill View nhắm tới dải ngang `1576 x 120 px` phía dưới. Dùng `grid`, `weight`, `minsize` và responsive fallback để giữ hierarchy ở DPI `100%-150%`; không ép đúng pixel bằng tọa độ tuyệt đối. Không thay đổi baseline hoặc min-size nếu chưa cập nhật UX spec trước.

## Bộ prompt trong thư mục

1. `UX1-prioritize-primary-hunt-actions.md`
2. `UX1B-bounds-readiness-state.md`
3. `UX2.1-core-grid-construction.md`
4. `UX2.2-content-migration.md`
5. `UX2B.1-primary-panels-split.md`
6. `UX2B.2-quick-skill-strip.md`
7. `UX3-progressive-disclosure-for-advanced-config.md`
8. `UX3B-progressive-disclosure-setup.md`
9. `UX4-status-and-warning-focus.md`
10. `UX4B.1-ui-collapsible-container.md`
11. `UX4B.2-log-data-integration.md`
12. `UX5-future-main-screen-roadmap.md`

`UX2-reorganize-main-screen-layout.md`, `UX2B-hunt-workspace-layout.md` và `UX4B-bottom-status-logs.md` chỉ là epic index; không chạy trực tiếp như một session.

## Thứ tự chạy đề xuất

Chi tiết timebox và dependency nằm trong [SESSION_WORKLOAD_AND_PRIORITY.md](SESSION_WORKLOAD_AND_PRIORITY.md). Chỉ chạy các micro-session bên dưới; không chạy epic index.

1. `UX1` — Quick Action Bar, `25-30 phút`
2. `UX1B` — bounds readiness state, `25-30 phút`
3. `UX2.1` — Core Grid Construction, `25-30 phút`
4. `UX2.2` — Content Migration, `25-30 phút`
5. `UX2B.1` — Primary Panels Split, `25-30 phút`
6. `UX2B.2` — Quick Skill Strip, `25-30 phút`
7. `UX3` — Sidebar navigation, `25-30 phút`
8. `UX3B` — Setup progressive disclosure, `25-30 phút`
9. `UX4` — Active Target & Status, `25-30 phút`
10. `UX4B.1` — UI Collapsible Container, `20-25 phút`
11. `UX4B.2` — Log Data Integration, `25-30 phút`
12. `UX5` — roadmap documentation, `15-20 phút`

## Nguyên tắc review

- không thêm tab mới nếu không thật sự cần thiết
- không phá vỡ workflow hunt hiện có
- không thay đổi config shape hoặc API hiện có
- không đổi baseline bốn vùng hoặc kích thước tối thiểu nếu UX spec chưa được cập nhật trước
- không để controller, service hoặc background worker gọi Tkinter trực tiếp
- không thao tác trực tiếp widget thuộc zone khác; dùng callback/controller contract
- nếu cần ẩn cài đặt nâng cao, phải giữ đường đi thay thế rõ ràng
- mỗi session nên là một thay đổi nhỏ, dễ kiểm tra bằng smoke test
- dừng mở rộng scope ở phút thứ `25`; chạy validation và chuyển phần còn lại sang session phụ thuộc
- nếu smoke/import check vẫn fail ở phút `30`, hoàn tác chỉ thay đổi do session tạo bằng patch có review, chạy lại check, rồi báo cáo nguyên nhân và phần việc deferred
- ưu tiên cải tiến layout, hierarchy và emphasis trước khi “sửa” sâu logic

## Files cần ưu tiên

- `app_gui.py`
- `ui/tabs/hunt_tab.py`
- `ui/tabs/setup_tab.py`
- `ui/tabs/stats_tab.py`
- `ui/tabs/help_tab.py`
- các controller hoặc helper liên quan đến UI state nếu cần

## Validation khuyến nghị

- smoke test kiểm tra app mở được
- kiểm tra tab Hunt hiển thị đúng trọng tâm hành động chính
- kiểm tra các nút Start / Stop / chọn window vẫn hoạt động
- kiểm tra không có lỗi import hoặc binding UI mới
- nếu cần kiểm tra thủ công, nên ghi rõ bước thực hiện trong final response
- tại `1920x1080`, kiểm tra vị trí, kích thước và thứ tự thị giác của mọi vùng bị tác động

## Session Boundary Gate

Mỗi prompt session phải kết thúc bằng kiểm tra biên phù hợp với thay đổi vừa thực hiện. Đây là yêu cầu bắt buộc, không phải bước tùy chọn sau smoke test.

- trước khi sửa, chọn tối thiểu 3 case biên cụ thể
- sau khi sửa, kiểm tra và báo cáo từng case là `passed`, `failed` hoặc `manual-only`
- với thay đổi liên quan đến main hunt flow, luôn xét các trạng thái: biên hợp lệ, chưa chọn window, biên sai hoặc thiếu, game window minimized/không còn tồn tại, và target region vượt biên khi có liên quan
- báo cáo recovery action: Refresh, chọn lại window, restore game window, hoặc capture lại region
- không tạo state biên UI riêng; dùng luồng chuẩn hóa bounds hiện có

## Definition of done cho một task UX

Một task được coi là hoàn thành khi:

- người dùng thấy ngay các thao tác chính trên màn hình
- các panel phụ không “đè” lên workflow chính
- tín hiệu trạng thái rõ ràng hơn trước
- không làm mất behavior, config hay hotkey hiện tại
- Session Boundary Gate đã được thực hiện và kết quả từng case được báo cáo

---

Mục tiêu không phải là “đổi giao diện cho đẹp”, mà là “làm cho workflow hunt rõ, nhanh và đáng tin cậy hơn cho người dùng.”
