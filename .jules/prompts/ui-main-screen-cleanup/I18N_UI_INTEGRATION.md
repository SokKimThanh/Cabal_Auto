# Tích Hợp Ngôn Ngữ Vào Main Screen UI

## Mục tiêu

Mọi UI được tạo hoặc chỉnh sửa trong roadmap phải hiển thị đúng ngôn ngữ ứng dụng hiện tại. Main screen dùng cơ chế i18n hiện có, không tạo translation state riêng trong từng zone.

## Cơ chế hiện có có thể sử dụng

| Thành phần | Contract hiện tại | Ý nghĩa cho UX session |
| --- | --- | --- |
| `App._t(key, **kwargs)` | Gọi `lib.i18n.t(key, ns=GLOBAL_NS, ...)` | App Header, Vùng A và text global mới dùng `self._t(...)` |
| `lib.i18n.t(...)` | Lookup theo namespace/ngôn ngữ, fallback global rồi raw key | Raw key là tín hiệu thiếu translation cần sửa, không phải UI copy được phép hiển thị |
| `on_language_change()` | Lưu `cfg.ui.language`, gọi `set_default_lang`, đổi title và gọi `_build_ui()` | Widget được build lại phải lấy label theo ngôn ngữ mới |
| `SetupTab._t(...)` | Ủy quyền về `app._t(...)` | Setup/Sidebar text dùng `self._t(...)`, không hard-code text song ngữ mới |
| Window/manager namespace | `t(key, ns=..., lang=...)` và dictionaries đăng ký trong i18n package | Dialog/manager thuộc namespace riêng phải dùng namespace hiện có |

Hiện registry hỗ trợ `en` và `vi`. UI roadmap không được giả định ngôn ngữ thứ ba cho đến khi i18n roadmap cung cấp data, language selector và fallback contract tương ứng.

## Quy tắc bắt buộc

1. Không thêm user-visible string hard-code vào `app_gui.py`, `ui/tabs/*.py`, controller hoặc dialog.
2. Với label/status/action mới thuộc main screen, thêm key `en` và `vi` vào `GLOBAL_TRANSLATIONS` trong `lib/i18n/translations.py`, sau đó render qua `self._t(key)` hoặc `app._t(key)`.
3. Với text thuộc manager/window namespace, thêm key vào dictionary của namespace đó và render qua `_t(key, ns=...)` theo convention hiện có.
4. Không dịch business state bằng cách tự tạo dictionary trong widget hoặc callback. UI chỉ render key/text từ registry hiện có.
5. Không ghi `lang` trực tiếp vào state của từng zone. `App.lang` và registry default language là source of truth; rebuild language tạo lại widget theo state này.
6. Text động dùng placeholder có tên, ví dụ `window_ready_with_name`; không ghép text tiếng Anh/Việt bằng string concatenation trong UI.
7. Nếu key mới chưa có đủ `en` và `vi`, không merge UI feature. Tách một i18n micro-session hoặc bổ sung key trong cùng session nếu phạm vi vẫn dưới 30 phút.

## Phân bổ theo zone

| Zone | Text cần i18n | API render | Yêu cầu khi đổi ngôn ngữ |
| --- | --- | --- | --- |
| Header | title, language label, global context | `App._t` | title và selector label rebuild đúng |
| A: Quick Action Bar | Window selector, Refresh, Start, Stop, bounds state, recovery action, hotkey summary | `App._t` | các action và bounds state không còn raw key |
| B: Workspace | rotation/status/skill labels, runtime state, recovery action | `app._t` trong HuntTab | status dynamic render lại đúng text từ key/template |
| C1: Sidebar/Setup | section names, entry points, mode/disclosure labels | `SetupTab._t` / `app._t` | mode state giữ nguyên, text đổi theo lang |
| C2: Bottom Logs | empty state, collapse/expand, column/metadata labels | owner `_t`/`app._t` | history data giữ nguyên; UI chrome đổi lang |

## Runtime state và bounds copy

Các state sau cần translation key cho cả `en` và `vi`; không dùng raw enum/state string làm text UI:

| State | Copy cần có | Recovery copy |
| --- | --- | --- |
| valid bounds | `Window ready` + window name | Start Hunt / Capture region |
| no selected window | `Chưa chọn cửa sổ game` | Select window / Refresh |
| invalid/malformed bounds | `Không thể dùng biên cửa sổ` | Refresh / Select another window |
| minimized/unavailable window | game window unavailable reason | Restore game / Refresh / Reselect |
| invalid target region | region outside game window | Capture again / Edit region |
| hunt running | current target/running state | Stop Hunt |
| blocking error | concise reason | action specific to error |

## Validation cho session có UI text mới

1. Chạy `py -m pytest tests/unit/test_i18n_global_registration.py -v` khi thay `GLOBAL_TRANSLATIONS`; chạy registry integrity test nếu đã có trong branch.
2. Chạy smoke/import check hiện có.
3. Manual check: mở app ở `vi`, xác nhận label mới không là raw key; đổi sang `en`, xác nhận Header, zone bị sửa và widget rebuild đổi text; đổi lại `vi`, xác nhận state/config vẫn giữ nguyên.
4. Kiểm tra text dài hơn ở `en`/`vi` không cắt, wrap hợp lý, không đẩy Start/Stop hoặc bounds state ra khỏi Vùng A.
5. Báo cáo mỗi case là `passed`, `failed` hoặc `manual-only` trong final response.

## Timebox và tách session

- Nếu thay đổi UI chỉ dùng key đã tồn tại: thực hiện trong UX session đang chạy.
- Nếu cần tối đa 3 key đơn giản, cùng zone và dictionary đã rõ: có thể thêm trong UX session, miễn vẫn còn thời gian validation trước phút 25.
- Nếu cần nhiều hơn 3 key, text động cho nhiều state, namespace mới, thay language selector hoặc thay registry: không mở rộng UX session. Tạo i18n session riêng theo `.jules/i18n-sprint-roadmap.md`.
- Không dùng fallback raw key như giải pháp tạm để vượt timebox.