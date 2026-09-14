# Tổng hợp các vấn đề tồn đọng Sprint 30 (Mức độ ưu tiên từ cao đến thấp)

Tài liệu này tổng hợp tất cả các lỗi, rủi ro, nợ kỹ thuật (technical debt) và công việc chưa hoàn thành từ các báo cáo review của Sprint 30. Ngôn ngữ được sử dụng là tiếng Việt đơn giản để cả người và AI đều dễ dàng đọc và xử lý tiếp.

## 1. Khởi tạo sai và Gắn trực tiếp biến vào UI (Vấn đề "God Class") - Cần sửa ngay
*Báo cáo liên quan: Prompt 002, Prompt 005*

**Vấn đề:** Mặc dù `AppStateController` đã tạo một chỗ chung để chứa các biến giao diện (`ui_vars` và `ui_widgets`), nhưng nhiều phần giao diện (tabs, panels) vẫn đang tự tạo các biến mới (như `tk.StringVar()`, `tk.BooleanVar()`, `tk.Listbox()`) và gắn trực tiếp vào `self.app` thay vì dùng chỗ chứa chung đó. Điều này phá vỡ việc đóng gói.

**Chi tiết các chỗ bị lỗi (cần sửa lại để dùng `AppStateController`):**
*   **ui/panels/monster_target_panel.py:**
    *   `self.app.monster_rotation_listbox = tk.Listbox(...)`
    *   `self.app.detected_monsters_listbox = tk.Listbox(...)`
    *   `self.app.monster_status_var = tk.StringVar()`
    *   `self.app.training_mode_hint_var = tk.StringVar()`
    *   Trực tiếp thay đổi từ điển `ui_vars` mà không qua hàm: `self.app.state_controller.ui_vars['target_policy'] = tk.StringVar(...)`
*   **ui/tabs/hunt_tab.py:**
    *   Gắn rất nhiều biến trực tiếp vào `self.app`: `hunt_mode_var`, `target_key_var`, `attack_press_var`, `target_cycle_var`, `search_interval_var`, `attack_interval_var`, `lost_timeout_var`, `attack_duration_var`, `template_var`, `bring_front_var`.
*   **ui/tabs/setup_tab.py:**
    *   Gắn rất nhiều biến trực tiếp vào `self.app`: `global_hotkey_enabled_var`, `global_hotkey_start_var`, `global_hotkey_stop_var`, `setup_target_key_var`, `setup_press_ms_var`, `setup_target_cycle_var`, `setup_search_interval_var`, `setup_attack_interval_var`, `setup_lost_timeout_var`, `setup_attack_duration_var`, `setup_template_var`.
*   **Lỗi gắn trực tiếp cửa sổ giao diện:**
    *   `ui/controllers/monster_manager_controller.py`: Đang gắn cửa sổ vào `self.app.monster_manager_win`.
    *   `ui/controllers/library_manager_controller.py`: Đang gắn cửa sổ vào `self.app.library_manager_win`.

**Giải pháp đề xuất:**
*   Khai báo và khởi tạo tất cả các biến này vào ngay trong hàm `__init__` của `AppStateController`.
*   Tại các view, dùng hàm `self.state_controller.get_ui_var(...)` hoặc truy xuất an toàn `self.state_controller.ui_widgets[...]` thay vì dùng `self.app.xxx`.

## 2. Rò rỉ UI Logic (UI Leak) trong AppStateController - Cần tách bạch ngay (Mới phát hiện)
*Báo cáo liên quan: Prompt 018*

**Vấn đề:** Các hàm `_refresh_slot_key_labels` và `_validate_slot_key_duplicates` bên trong `AppStateController` đang thao tác trực tiếp trên UI Widgets thông qua hàm `.config(text=...)` và `.config(fg=...)`. Data Controller không được quyền chạm vào View.

**Giải pháp đề xuất (Prompt 018):**
* Chuyển đổi logic 2 hàm trên thành việc phân tích và emit các Event (ví dụ: `on_skill_key_duplicates_detected`). Cập nhật View lắng nghe event này để tự `.config()`.

## 3. Cấu hình Hunt bị "hardcode" trong State Controller (Mới phát hiện)
*Báo cáo liên quan: Prompt 016*

**Vấn đề:** Hàm `build_hunt_config_from_state` quá lớn, đang nằm cứng trong `AppStateController` và chứa vô số giá trị cài đặt mặc định hardcode, vi phạm Nguyên lý SRP.

**Giải pháp đề xuất (Prompt 016):**
* Rút hàm tạo config này ra file `HuntConfigController` và chuyển đổi hardcode thành hằng số (Constants).

## 4. Quá tải Logic về Preset trong AppStateController (Mới phát hiện)
*Báo cáo liên quan: Prompt 017*

**Vấn đề:** `AppStateController` đang phải lo luôn việc quản lý (lưu, tải, đổi slot) Preset kỹ năng.

**Giải pháp đề xuất (Prompt 017):**
* Chuyển hết mớ logic này sang class có sẵn `SkillPresetController`, và chỉ dùng `AppStateController` làm kho lưu data.

## 5. Dọn dẹp __init__ của AppStateController (Mới phát hiện)
*Báo cáo liên quan: Prompt 015*

**Vấn đề:** Class sử dụng `getattr` với chính `self` của nó rất nhiều lần, vòng đời thuộc tính không rõ ràng.
**Giải pháp:** Khởi tạo tất cả trong `__init__` (như `self.skill_slot_key_labels = []`).
**Trạng thái:** Hoàn thành. `app_state_controller.py` đã được dọn dẹp sạch `getattr/hasattr` trên `self`, toàn bộ state variables đã được khai báo và khởi tạo trong `__init__`.

## 6. Các lỗi liên quan đến AppShell và Cấu hình cửa sổ chính (UI Layout)
*Báo cáo liên quan: Prompt 006*

**Vấn đề 1: Đổi tiêu đề khi đổi ngôn ngữ bị sót**
*   Trong file `app_gui.py` (khoảng dòng 1365, hàm `on_language_change`), vẫn còn đang gọi `self.title(self._t("app_title"))` trực tiếp. Tác vụ này lẽ ra phải do `AppShell` làm hoặc phải có hàm của `AppShell` cập nhật.

**Vấn đề 2: Bị mất bước kích hoạt Giao diện (Theme)**
*   Theo kế hoạch ban đầu, `UIStyleV2.apply(...)` phải được chạy trong `AppShell`. Tuy nhiên hàm này không còn thấy ở cả `app_gui.py` lẫn `app_shell.py`, và hàm `apply` cũng biến mất khỏi file `lib/ui_style_v2.py`. Cần kiểm tra lại hệ thống Theme đang được khởi tạo như thế nào.

**Vấn đề 3: Sai logic truyền tham số Khởi tạo**
*   Code hiện tại gọi `self.shell = AppShell(self)` (vì `App` kế thừa từ `tk.Tk`, nên `self` chính là cửa sổ gốc). Trong `AppShell.__init__` có một đoạn gán phức tạp `self.app = app if app is not None else root`. Cần sửa cho rõ ràng.

## 7. Mã kiểm thử tự động bị hỏng (Broken Integration Tests)
*Báo cáo liên quan: Prompt 004*

**Vấn đề:** Mã kiểm thử vòng lặp Hunt (`test_orchestrator_loop.py`) đang bị viết dạng đối phó và môi trường kiểm thử bị thiếu thư viện.
*   Thiếu thư viện `cv2` (opencv-python) trong môi trường chạy test, dẫn đến lỗi `ModuleNotFoundError` khi load `lib/vision/target_bar_detector.py`.
*   Mã kiểm tra tính đúng đắn (assert) bị đổi thành `assert True`, nghĩa là luôn báo đúng ngay cả khi chạy sai.
*   Kiến trúc Mock quá thủ công, cứng ngắc. Dễ bị hỏng nếu thứ tự chạy của các luồng (thread) bị đổi đi dù chỉ một chút.

**Giải pháp đề xuất:**
*   Cài đặt đầy đủ `opencv-python` cho môi trường test.
*   Bỏ `assert True`, viết lại các đoạn mã kiểm tra (assert) dựa vào việc theo dõi số lần hàm giả lập (mock callback) như `try_cast_skills` được gọi, độ tin cậy sẽ cao hơn.

## 8. Các điểm rò rỉ phụ của AppStateController
*Báo cáo liên quan: Prompt 001*

**Vấn đề:** Vẫn còn sót vài chỗ mà lớp quản lý trạng thái (`AppStateController`) tự với tay lấy dữ liệu từ ngoài vào, thay vì lấy qua kênh nội bộ, bao gồm:
*   Gọi `getattr(self.root.hunt_orchestrator, "hunt_running", False)`: `AppStateController` vẫn còn lén nhìn vào `hunt_orchestrator` thông qua biến gốc (root).
*   Gọi `getattr(self.root, "skills", [])`: Vẫn lấy thông tin danh sách kỹ năng từ `root`. Cần tách việc lưu thông tin này vào một chỗ chuẩn hơn.

## Post-Phase 1 Cleanup (Prompts 19-21)
If issues are found during the review phase of the new cleanup prompts (019-021), re-execute them in the following order to ensure dependencies remain stable.

1. **`sprint30-prompt-019-clean-imports-and-fallback.md`**
   - **Risk:** Syntax errors from removing imports or `try/except` blocks incorrectly; `_create_icon_btn_component` failing to load due to cyclic imports.
   - **Action:** Fix any syntax errors at the top of `app_gui.py` and ensure the helper file `lib/ui/helpers/fallback_components.py` is correctly imported.

2. **`sprint30-prompt-020-move-hotkey-diagnostics.md`**
   - **Risk:** Tracebacks when `AppLifecycleController` or `HotkeyController` tries to call the old method; UI not updating because state updates aren't bound correctly.
   - **Action:** Ensure all references to `_update_hotkey_diagnostics_ui` are completely wiped and replaced with the new controller method.

3. **`sprint30-prompt-021-move-training-mode-buttons.md`**
   - **Risk:** `MonsterTargetPanel` crashing on initialization if `self.btn_add` doesn't exist yet when the state callback fires.
   - **Action:** Ensure the UI variables are traced *after* all widgets are built in `_build_ui()`.
*   Gọi `getattr(self.root, "skills", [])`: Vẫn lấy thông tin danh sách kỹ năng từ `root`. Cần tách việc lưu thông tin này vào một chỗ chuẩn hơn.

# Phase 4 (God Class Final Decomposition)
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-022-extract-main-menu.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-023-decouple-action-and-status-bars.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-024-extract-vision-ui-handlers.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-025-extract-monster-rotation-logic.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-026-extract-skill-configuration-logic.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-027-extract-logging-and-helpers.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-028-finalize-app-class.md

# Phase 4 Run 2 (Re-execution for Stability)
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-022-extract-main-menu.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-023-decouple-action-and-status-bars.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-024-extract-vision-ui-handlers.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-025-extract-monster-rotation-logic.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-026-extract-skill-configuration-logic.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-027-extract-logging-and-helpers.md
docs/sprints/sprint30/prompt-god-class-decomposition/sprint30-prompt-028-finalize-app-class.md
