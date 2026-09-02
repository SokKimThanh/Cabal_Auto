# Session Prompt DS4: Hunt Workspace Theme

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependencies:** DS3, UX3B, UX4.2, UX5.2

## Objective

Áp design system cho Hunt workspace sau khi cấu trúc ba mode, skill lanes và
Target Card đã ổn định. Không thay đổi combat state machine hoặc persistence.

## Target Files

- Modify: `ui/tabs/hunt_tab.py`
- Modify: các component Hunt được UX3B/UX4/UX5 tạo
- Modify/Add: Hunt visual/layout tests

## Visual Contract

- Segmented control ba mode cố định, selected rõ và không dùng dropdown.
- Configured/detected list dùng panel/input neutral, row 36px preferred nhưng co
  theo DPI/content.
- DB-match, unknown, active target, selected row có semantic state khác nhau và
  không chỉ dựa vào màu.
- Drag/drop destination có focus/highlight rõ; unknown không hiện affordance thêm.
- Skill cards/lanes dùng typography gọn, không card lồng card.
- Target status/HP có priority thị giác nhưng không dùng hero-sized text.
- Warning `any_target` dùng yellow/orange, không modal lặp.
- Treeview/Combobox/Scrollbar theo ttk dark theme.

## Implementation Rules

1. Xóa màu/font hard-code trong vùng đã migrate, dùng DS1/DS2 roles.
2. Không ép panel width 520 hoặc row height 36 thành minsize gây overflow.
3. Layout rộng/hẹp từ UX3B phải giữ nguyên behavior.
4. Runtime reconcile không tạo widget churn vì style.
5. Icon button lạ có tooltip; keyboard promotion/Enter vẫn hoạt động.
6. Không dùng Canvas gradient/shadow trang trí.

## Validation

```powershell
py -m pytest tests/ui/tabs/test_hunt_tab_layout.py tests/ui/tabs/test_hunt_target_modes.py -q
py -m pytest tests/unit/test_monster_rotation_queue.py -q
```

Manual matrix: `vi/en`, ba target mode, empty/loading/error/populated states,
1366x768 và 1920x1080, DPI 100/125/150/200.

## Gate

PASSED khi mọi state đọc được, không overlap/clipping/layout shift và toàn bộ
drag/keyboard/callback behavior giữ nguyên.
