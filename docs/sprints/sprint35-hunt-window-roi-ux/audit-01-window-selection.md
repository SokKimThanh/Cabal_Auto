# Audit: Game Window Selection Flow in Hunt Tab

## 1. Sơ đồ luồng (Window Selection Flow)
```text
User selects window from Dropdown (Setup/Top bar)
        |
        v
AppWindowController.on_window_combo_selected()
        |
        v
Validation Service (WindowSelectionService.validate_prerequisites)
        |
        v
If Valid:
  - Sets app.state_controller.hunt_selected = {hwnd, title, pid}
  - Saves to hunt_config.json
        |
        v
Scan/Hunt action triggered (Manual/Auto)
        |
        v
ScanController.run_scan() / HuntOrchestrator.start_hunt()
        |
        v
Uses app.state_controller.hunt_selected (via get_hunt_selected callback or get_hwnd)
        |
        v
If HWND valid -> Binds & Scans the specific Window
If HWND missing -> Fallbacks to AutoScanner.detect_window() (searches by title "Cabal", etc.)
```

## 2. Các nút Scan & Window Source

| Nút | Window Source | File | Hàm | Có Lock Window không? |
| --- | --- | --- | --- | --- |
| Nút "Scan" (Action Bar) | UI Variable (`hunt_selected` truyền qua `get_hwnd` vào `ScanController`) | `ui/components/action_bar_view.py` -> `lib/features/hunt/scan_controller.py` | `run_scan()` | Không lock toàn bộ hệ thống, nhưng ScanController dùng đúng `hwnd` truyền vào. Nếu mất kết nối, fallback tìm theo tên (`detect_window`). |
| Start Hunt (Action Bar) | UI Variable (`hunt_selected` truyền qua `get_hunt_selected` callback) | `ui/components/action_bar_view.py` -> `lib/features/hunt/hunt_orchestrator.py` | `start_hunt()` | Có, Orchestrator giữ `hwnd` và sử dụng `InputCapabilityManager` để bind window, có fallback về foreground nếu background lỗi. |
| (Auto) Background Loop | UI Variable (`hunt_selected`) | `lib/features/hunt/hunt_orchestrator.py` | Loop/Validate | Có, Orchestrator liên tục đọc lại `get_hunt_selected()` để kiểm tra window hợp lệ trong chu kỳ hunt. |

## 3. Câu hỏi & Trả lời (Audit Findings)

1. **Ai set `selected_window`?**
   - `AppWindowController` (`ui/controllers/app_window_controller.py`): Khi user chọn từ combobox, gọi `on_window_combo_selected`, sau đó lưu vào `app.state_controller.hunt_selected`.

2. **Ai đọc `selected_window` khi scan?**
   - Lớp trung gian `ScanController` (`lib/features/hunt/scan_controller.py`) gọi callback `get_hwnd()` để lấy `hwnd` và truyền vào `AutoScanner`.
   - `HuntOrchestrator` (`lib/features/hunt/hunt_orchestrator.py`) nhận callback `get_hunt_selected` để lấy dictionary window hiện tại.

3. **Có fallback về `active_window` (hay tự tìm window) không?**
   - **CÓ**. Trong `ScanController.run_scan()`, nếu `get_hwnd` trả về None hoặc HWND không hợp lệ, nó gọi `scanner.detect_window()` (trong `lib/features/hunt/scanner.py`), hàm này tự tìm cửa sổ theo title (ví dụ: "Cabal", "CABAL", "카발", v.v.).
   - Việc này gây ra rủi ro *quét nhầm* cửa sổ nếu người dùng cố ý chọn một cửa sổ khác nhưng app không lấy được hwnd.

4. **Có lock window trong suốt phiên scan không?**
   - **HuntOrchestrator**: CÓ. Khi Hunt bắt đầu, `HuntOrchestrator` liên tục validate `hwnd` từ `get_hunt_selected()`. Nếu `hwnd` bị thay đổi, nó sẽ detect sự sai lệch.
   - **ScanController**: KHÔNG khóa cứng. Mỗi lần click Scan, nó lấy lại `hwnd` từ UI, quét 1 frame và trả về. Không có cơ chế giữ handle (lock) liên tục trừ việc init `ScreenCapture` vào đúng `hwnd` đó.

## 4. Điểm mất đồng bộ (Desync Risks)
- `ScanController` có cơ chế fallback (`scanner.detect_window()`) nếu `hwnd` từ UI không hợp lệ. Điều này có thể khiến người dùng nhầm tưởng ứng dụng vẫn đang quét cửa sổ được chỉ định nhưng thực tế nó lại tìm và quét cửa sổ "Cabal" đầu tiên tìm thấy.
- Component Action Bar khi gọi Scan sử dụng callback gián tiếp (`get_hwnd()`), nếu callback này không trỏ đúng tới biến `hunt_selected` mới nhất, ScanController sẽ bị fallback về `detect_window()`.

## Danh sách file liên quan chính
- `ui/controllers/app_window_controller.py` (Line 237-244): Set `hunt_selected`.
- `lib/features/hunt/scan_controller.py` (Line 50-60): Get `hwnd`, fallback `detect_window`.
- `lib/features/hunt/hunt_orchestrator.py` (Line 76-77, 133-134): Đọc `hunt_selected` qua callback.
- `lib/features/hunt/scanner.py` (Line 42-63): Hàm `detect_window()` thực hiện quét cửa sổ bằng `find_window` theo string titles.
