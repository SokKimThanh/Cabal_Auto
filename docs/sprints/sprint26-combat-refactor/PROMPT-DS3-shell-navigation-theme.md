# Session Prompt DS3: Shell, Sidebar Và Action Bar Theme

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependencies:** DS1, DS2

## Objective

Áp dark command-center theme cho shell ổn định hiện tại: root background,
sidebar, action bar, view workspace, Global Apply và DB Status. Không thay đổi
view swapping hoặc business callbacks.

## Target Files

- Modify: `app_gui.py`
- Modify: shell/navigation tests
- Reference: `lib/ui_style.py`, `ui/theme/ttk_theme.py`

## Visual Contract

- Sidebar tối, chiều rộng preferred 220px nhưng không phá breakpoint/minsize.
- Action bar là một hàng: Window, Refresh, Scan, Readiness, Start/Stop, Language.
- Selected sidebar dùng solid background + border-left + text/icon state.
- Start xanh, Stop đỏ tại cùng vị trí; Scan/Refresh là icon button có tooltip.
- Workspace dùng app/panel neutral, không card nổi lồng nhau.
- Global Apply và DB Status có bottom chrome rõ, không overlap `main_shell`.
- Hunt/Logs/Setup/Help selected state hoạt động qua `switch_view()`.

## Implementation Rules

1. Gọi ttk theme registry đúng một lần sau root init.
2. Thay hard-coded shell colors/font bằng DS1 tokens.
3. Không dùng CSS gradient/rgba/shadow; dùng solid semantic colors.
4. Không thay `pack/grid` ownership đã fix; style không được làm mất
   `main_shell.pack(...)`.
5. Stable dimensions không thay đổi khi status text/icon đổi.
6. Ngôn ngữ dài phải co readiness trước, không đẩy Start khỏi viewport.
7. Focus/hover/disabled states phải nhìn thấy trên nền tối.

## Validation

```powershell
py -m pytest tests/unit/test_action_bar.py tests/unit/ui/test_shell_navigation.py -q
```

Runtime probe phải xác nhận `main_shell`, sidebar, action bar, workspace và bottom
chrome đều mapped/kích thước > 0.

Manual: 1366x768 và 1920x1080, `vi/en`, chuyển tất cả sidebar view, Start/Stop
state, tab keyboard focus.

## Gate

PASSED khi shell không trắng/clip/overlap, selected state đúng và callback không
đổi. REVERT nếu style migration thay đổi geometry ownership hoặc view state.
