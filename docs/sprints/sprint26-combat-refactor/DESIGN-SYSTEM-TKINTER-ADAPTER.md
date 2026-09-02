# Design System Adapter - Trợ Lý Săn Cabal Online

## Mục Tiêu

Chuyển design system đính kèm sang contract dùng được trong Tkinter, giữ một
nguồn token duy nhất và không đưa cú pháp CSS không được hỗ trợ vào widget native.

## Đánh Giá So Với App Hiện Tại

App hiện dùng:

- `lib/ui_style.py` với class `UIStyle`, font Segoe UI và palette sáng;
- `ui/helpers/button_styles.py` chứa một palette/font thứ hai;
- nhiều mã hex/font cục bộ trong `app_gui.py` và `ui/tabs/hunt_tab.py`;
- `tk.Frame`/`tk.Label`/`tk.Button`, `ttk.Combobox`/`ttk.Treeview`;
- shell gồm action bar, sidebar và `shell_zone_b` để swap view;
- Activity Logs đã là view riêng trong workspace.

Design system mới là dark command-center theme phù hợp domain, nhưng có token CSS
không dùng trực tiếp được trong Tkinter:

- `rgba(...)`, `linear-gradient(...)`;
- box-shadow/glow CSS;
- `border-radius` cho widget native;
- font string `"'Rajdhani', sans-serif"`;
- `letter-spacing` theo `em`;
- transition/easing CSS.

Các token này phải được chuyển thành fallback Tkinter-safe, không được truyền
thẳng vào `bg`, `fg`, `font` hoặc ttk style.

## Contract Token Tkinter

### Màu

Dùng solid hex:

| Vai trò | Token Tkinter | Giá trị |
| --- | --- | --- |
| App background | `BG_APP` | `#0b0d12` |
| Sidebar | `BG_SIDEBAR` | `#10131c` |
| Panel | `BG_PANEL` | `#111520` |
| Input/table | `BG_INPUT` | `#0d1018` |
| Toolbar | `BG_TOOLBAR` | `#0d1018` |
| Status bar | `BG_STATUSBAR` | `#080b10` |
| Border | `BORDER_DEFAULT` | `#1e2333` |
| Panel border | `BORDER_PANEL` | `#1e2535` |
| Primary text | `TEXT_PRIMARY` | `#e2e8f0` |
| Secondary text | `TEXT_SECONDARY` | `#94a3b8` |
| Muted text | `TEXT_MUTED` | `#6b7280` |
| Active green | `ACCENT_GREEN` | `#4ade80` |
| Green border | `ACCENT_GREEN_BORDER` | `#16a34a` |
| Blue selected | `ACCENT_BLUE` | `#1d4ed8` |
| Warning | `STATUS_READY` | `#eab308` |
| Danger | `STATUS_DANGER` | `#dc2626` |

Các token `rgba` được pre-compose lên background đích nếu thật sự cần state
subtle. Không alpha-blend runtime trong mỗi widget render.

### Gradient, Radius, Shadow

- Native Tk widgets dùng solid start/end color theo role, không giả gradient bằng
  nhiều frame trang trí.
- `ttk` dùng border/relief/focus state; không tuyên bố có radius nếu theme không
  hỗ trợ.
- Glow chỉ dùng cho canvas/custom draw đã có lý do chức năng; không tạo ảnh glow
  cho toàn bộ button.
- Selected state dùng border-left + solid background + text contrast.

### Font

Font resolver kiểm tra `tkinter.font.families()`:

1. Display: `Rajdhani`, fallback `Segoe UI Semibold`, sau đó `Segoe UI`.
2. Body: `Inter`, fallback `Segoe UI`.
3. Mono: `JetBrains Mono`, fallback `Cascadia Mono`, rồi `Consolas`.

Không hard-code CSS family string. Font size dùng point size Tkinter và được kiểm
tra ở DPI 100%-200%; không coi pixel CSS là point tương đương tuyệt đối.

### Spacing Và Kích Thước

Giữ scale 2/4/6/8/10/12/16/20/24/32 dưới token rõ tên. Stable controls dùng
minsize/aspect constraint, không dùng width character tùy tiện khi layout yêu cầu
pixel ổn định.

Các số cố định trong attachment là mục tiêu visual, không phải constraint cứng:

- sidebar mục tiêu 220px nhưng phải co theo breakpoint;
- monster/skill panel `520px` không được làm viewport 1366x768 overflow;
- toolbar/statusbar dùng requested height và DPI scaling;
- layout dùng grid weight/minsize đã được acceptance test.

## Kiến Trúc Style

`lib/ui_style.py` tiếp tục là public source of truth để tránh đổi toàn bộ import.
Có thể tách implementation token sang module nhỏ hơn nhưng `UIStyle` phải re-export
compatibility aliases trong giai đoạn migration.

Không để `ui/helpers/button_styles.py` tiếp tục sở hữu màu/font độc lập. Helper
button phải đọc token từ `UIStyle` hoặc module token owner.

Tạo một hàm cấu hình ttk tập trung, ví dụ:

```python
def configure_ttk_styles(root: tk.Misc) -> None:
    ...
```

Gọi đúng một lần sau root/Tk được tạo và gọi lại có kiểm soát nếu theme đổi.
Không tạo `ttk.Style()` riêng trong từng component.

## Component State Bắt Buộc

Mỗi component phải định nghĩa:

- normal;
- hover/active khi Tk hỗ trợ;
- selected;
- focus-visible;
- disabled;
- error/warning khi có ý nghĩa.

Không dùng màu làm tín hiệu duy nhất: giữ text/icon/status label tương ứng.

## Migration Boundary

- Không redesign và refactor logic trong cùng session style.
- Không đổi callback, queue, thread hoặc config schema.
- Không sửa geometry để che lỗi style.
- Không thay toàn app trong một patch; migration theo shell rồi từng view.
- Compatibility aliases chỉ xóa sau repository search và visual acceptance.

## Acceptance Chung

- 1366x768, 1920x1080; DPI 100%, 125%, 150%, 200%.
- Cả `vi` và `en`.
- Không text/control overlap hoặc clipping.
- Keyboard focus nhìn thấy được.
- Contrast tối thiểu WCAG AA cho text quan trọng.
- Không còn màu/font cục bộ trong các file đã migrate, trừ asset/semantic exception
  được ghi chú.
- Activity Logs, Hunt, Setup và dialog chính đều đọc được ở dark theme.
- Canvas/overlay Win32 giữ token RGB riêng và không bị đổi nhầm theo Tk theme.
