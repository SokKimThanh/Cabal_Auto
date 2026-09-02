# Session Prompt DS1: Tkinter-Safe Design Tokens

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependencies:** Session 01-20 đã đạt; đọc `DESIGN-SYSTEM-TKINTER-ADAPTER.md`

## Objective

Chuyển design system dark command-center thành token Python/Tkinter hợp lệ trong
`lib/ui_style.py`, giữ compatibility cho call site hiện tại nhưng chưa restyle
widget trong session này.

## Target Files

- Modify: `lib/ui_style.py`
- Create: `lib/ui_theme.py` nếu cần tách dataclass/font resolver
- Add: `tests/unit/ui/test_ui_theme_tokens.py`

Không sửa `app_gui.py`, view, callback hoặc geometry.

## Implementation

1. Tạo immutable semantic tokens cho background, border, text, green/blue/yellow/
   red state, spacing và stable dimensions theo adapter document.
2. Không chứa `rgba`, `linear-gradient`, CSS shadow, CSS font list hoặc unit
   `px/em/s` trong giá trị truyền cho Tkinter.
3. Thêm font resolver dùng `tkinter.font.families()`:
   - Rajdhani -> Segoe UI Semibold -> Segoe UI;
   - Inter -> Segoe UI;
   - JetBrains Mono -> Cascadia Mono -> Consolas.
4. Không yêu cầu font ngoài để app khởi động.
5. `UIStyle` re-export alias cũ (`BG_DEFAULT`, `COLOR_TEXT`, button tokens...) để
   code chưa migrate không lỗi import.
6. Semantic role mới phải rõ: app/sidebar/panel/input/toolbar/statusbar, primary/
   secondary/muted text, selected/info/ready/hunting/danger.
7. Giữ RGB tuple cho Win32 overlay riêng; không đổi nhầm sang hex Tk theme.
8. Thêm helper preblend alpha token thành hex trên background cố định; không nhận
   chuỗi `rgba()` tại runtime widget.

## Tests

- Mọi Tk color token là `#RRGGBB` hợp lệ.
- Contrast text chính và button quan trọng đạt ngưỡng đã định.
- Font resolver fallback deterministic khi font thiếu.
- Compatibility aliases tồn tại.
- Import token module không tạo Tk root.
- Overlay RGB tokens không bị thay đổi kiểu.

```powershell
py -m pytest tests/unit/ui/test_ui_theme_tokens.py -q
```

## Gate

PASSED khi token tests pass, không widget production nào bị restyle và không có
CSS-only value lọt vào Tkinter token. Nếu phạm vi kéo sang view, dừng session.
