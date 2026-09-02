# Session Prompt DS2: Ttk Theme Và Component Primitives

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependencies:** DS1

## Objective

Tạo một registry `ttk.Style` và component primitives dùng token DS1, loại bỏ
palette/font song song trong button helper mà chưa restyle toàn bộ app.

## Target Files

- Create/Modify: `ui/theme/ttk_theme.py`
- Modify: `ui/helpers/button_styles.py`
- Modify: icon button helper hiện có nếu cần semantic role
- Add: `tests/unit/ui/test_ttk_theme.py`
- Add: `tests/unit/ui/test_button_style_roles.py`

## Implementation

1. `configure_ttk_styles(root)` được gọi idempotently và sở hữu Style cho Frame,
   Label, Combobox, Treeview, Scrollbar, Checkbutton và focus/selected/disabled.
2. Dùng một named ttk theme derived từ theme khả dụng; không tạo `ttk.Style()`
   riêng trong mỗi component.
3. Button helper nhận semantic role `primary`, `danger`, `info`, `neutral`,
   `warning`, `icon`; không sở hữu hex/font riêng.
4. Giữ API compatibility trong giai đoạn migration nhưng alias phải đọc token
   DS1.
5. Focus-visible rõ, disabled state không mất text, selection có contrast.
6. Không mô phỏng gradient/radius/shadow bằng widget lồng nhau.
7. Không đổi callback, layout manager hoặc kích thước parent.

## Tests

- Registry gọi hai lần không tạo lỗi hoặc drift.
- Tất cả semantic role trả style đầy đủ.
- `button_styles.py` không còn Arial/màu hard-code làm nguồn chính.
- Combobox dropdown và Treeview heading/selection dùng dark token.
- Keyboard focus state khác normal state.

```powershell
py -m pytest tests/unit/ui/test_ttk_theme.py tests/unit/ui/test_button_style_roles.py -q
```

## Gate

PASSED khi primitives độc lập chạy được trên Windows/headless mock phù hợp và
không có visual migration diện rộng trong cùng session.
