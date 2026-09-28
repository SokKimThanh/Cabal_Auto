# Prompt 01 — Audit luồng chọn Game Window trong Tab Hunt

## Mục tiêu
Xác định chính xác thời điểm và cơ chế hệ thống bind cửa sổ game vào phiên quét.

## Root Cause (từ bug report)
Người dùng không biết hệ thống đang quét cửa sổ nào; nghi ngờ không có cơ chế lock window.

## Phạm vi
- CHỈ ĐỌC, KHÔNG SỬA CODE.
- Đọc: `ui/tabs/hunt_tab.py`, `lib/system/window_manager.py`, `lib/features/hunt/scanner.py`, mọi file có keyword `WindowManager`, `selected_window`, `active_window`, `game_window`.

## Công việc
1. Grep toàn repo:
   ```bash
   grep -rn "WindowManager\|selected_window\|active_window\|game_window\|bind_window" lib/ ui/
   ```
2. Vẽ luồng: User click → Window selection → Bind → Scan.
3. Xác định rõ:
   - Ai set `selected_window`?
   - Ai đọc `selected_window` khi scan?
   - Có fallback về `active_window` không?
   - Có lock window trong suốt phiên scan không?
4. Liệt kê từng nút Scan trong Hunt tab và biến window context tương ứng.

## Output
- Sơ đồ luồng dạng text.
- Bảng: `Nút | Window source | File | Hàm | Có lock?`
- Danh sách file/hàm liên quan (kèm line number).

## Tiêu chí hoàn thành
- Xác định được chính xác nơi bind window.
- Chỉ ra điểm mất đồng bộ (nếu có).
- Báo cáo lưu tại: `docs/sprints/sprint35-hunt-window-roi-ux/audit-01-window-selection.md`

## Commit
```
docs(sprint35): audit game window selection flow in Hunt tab
```
