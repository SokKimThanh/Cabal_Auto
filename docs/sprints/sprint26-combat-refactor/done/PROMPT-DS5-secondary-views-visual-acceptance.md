# Session Prompt DS5: Secondary Views Và Visual Acceptance

**Timebox:** 25-30 phút  
**Priority:** Medium/Final Gate  
**Dependencies:** DS4

## Objective

Hoàn tất theme cho Activity Logs, Setup, Help, Stats và các dialog chính trong
scope; chạy visual/accessibility acceptance toàn app.

## Target Files

- Modify: `ui/views/activity_logs_frame.py`
- Modify: Setup/Help/Stats view hiện hành
- Modify: dialog/window chính theo danh sách kiểm kê trong session
- Modify/Add: UI smoke/visual tests

## Implementation

1. Activity Logs dùng panel/input dark, font mono resolver, scrollbar ttk; giữ
   một queue consumer và buffer 1.000 dòng.
2. Setup dùng full-width sections, không card lồng nhau; input/checkbox/combobox
   có focus/error/disabled rõ.
3. Help ưu tiên khả năng đọc, heading vừa phải, không marketing hero.
4. Stats dùng Treeview dark, heading/selection/empty state rõ.
5. Dialog phải đặt transient/focus đúng và text không bị cắt ở `vi/en`.
6. Không đổi logger/config/database/business callback.
7. Repository scan các file đã migrate: không còn Arial/màu hard-code làm style
   chính, trừ exception được ghi chú.

## Visual Acceptance Matrix

| View | 1366x768 | 1920x1080 | DPI 100/125/150/200 | vi/en |
| --- | --- | --- | --- | --- |
| Hunt | Required | Required | Required | Required |
| Logs | Required | Required | Required | Required |
| Setup | Required | Required | Required | Required |
| Help | Required | Required | 100/150 | Required |
| Stats | Required | Required | 100/150 | Required |

Kiểm tra empty/loading/ready/running/warning/error/disabled/focus states khi view
có state tương ứng.

## Automated Validation

```powershell
py -m pytest tests -m ui -q
py -m black --check app_gui.py lib/ui_style.py ui
py -m flake8 app_gui.py lib/ui_style.py ui
```

Nếu Tk test headless trên Linux: dùng `xvfb-run -a`. Trên Windows, chụp screenshot
ma trận chính và đo widget bounds; không chỉ kiểm tra `winfo_ismapped()`.

## Gate

PASSED khi:

- không view trắng, overlap hoặc text clipping;
- contrast/focus/disabled state đạt yêu cầu;
- `vi/en` và DPI matrix chính pass;
- callback, queue và runtime tests không regression;
- design tokens là nguồn style duy nhất trong phạm vi migrate.

Lỗi vượt 10 phút được ghi follow-up theo từng view; không refactor logic trong
final visual gate.
