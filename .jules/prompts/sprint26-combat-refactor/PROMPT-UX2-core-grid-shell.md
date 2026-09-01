# Session Prompt UX2: Build Four-Zone Core Grid Container & Migrate Shell

Timebox: 25–30 minutes.
Priority: High – Establishes the 4-zone layout foundation with DPI resilience.

---

## Objective
Xây dựng container chính `main_shell` quản lý bằng `pack()` (khi gắn vào `root`) và chia lưới 4 vùng A, B, C1, C2 bằng `grid()` với thông số `weight` và `minsize` tường minh. Loại bỏ hoàn toàn Tab Notebook con lồng trong Vùng B, thiết lập cơ chế View Swapping an toàn cho các view có event bindings phức tạp, hỗ trợ DPI từ 100% đến 200% và song ngữ i18n đầy đủ.

## Target Files
- Modify: `app_gui.py`
- Modify: `ui/main_shell.py` (hoặc module điều phối layout)
- Reference: `lib/ui_style.py`, `lib/system/i18n.py`

---

## Implementation Details

### 1. Phân Bổ Khung Lưới 4 Vùng (Explicit minsize & DPI Guard)
- Khởi tạo `main_shell = tk.Frame(root, bg=UIStyle.BG_APP)`.
- Thiết lập thông số hàng và cột chi tiết:
  * **Hàng 0 (Vùng A - Action Bar):** `rowconfigure(0, weight=0, minsize=80)`.
  * **Hàng 1 (Nội dung chính):** `rowconfigure(1, weight=1, minsize=540)`.
  * **Hàng 2 (Vùng C2 - Logs, footer full-width):** `rowconfigure(2, weight=0, minsize=36)`.
  * **Cột 0 (Vùng C1 - Sidebar):** `columnconfigure(0, weight=0, minsize=260)`.
  * **Cột 1 (Vùng B - Workspace):** `columnconfigure(1, weight=1, minsize=960)`.
  * (Đặt lại tên nhất quán: chỉ dùng A/B/C1/C2 theo đúng Objective — bỏ ký hiệu "D" nếu xuất hiện ở bất kỳ đâu trong code/comment, tránh gây nhầm với một vùng thứ 5 không tồn tại.)
- Áp dụng hệ số co giãn DPI theo một công thức thống nhất cho **mọi** mức DPI, không chỉ ở các mốc cao: `scale_factor = dpi_percent / 100.0`, nhân trực tiếp vào từng giá trị `minsize` trước khi truyền vào `rowconfigure`/`columnconfigure`. Điều này đảm bảo 100%/125% cũng được tính nhất quán (ở 100%, `scale_factor = 1.0` nên không đổi gì, đúng như mong đợi), thay vì liệt kê rời rạc theo từng mốc DPI cụ thể (150%, 175%, 200%).
- **CẤM (làm rõ phạm vi):** Tuyệt đối không dùng `pack()` và `grid()` làm con của **cùng một container cha**. Quy tắc này không cấm việc bản thân `main_shell` (một container hoàn chỉnh) được gắn vào `root` bằng `pack()`, miễn là toàn bộ các widget con **bên trong** `main_shell` dùng nhất quán `grid()` với nhau.

### 2. View Manager & Cơ Chế View Swapping An Toàn
- Khởi tạo các view độc lập trong Vùng B và lưu vào từ điển `self._views`:
  * `'hunt'`: `HuntWorkspaceFrame` (Mặc định hiển thị).
  * `'setup'`: `SetupContentFrame`.
  * `'monster_manager'`: `MonsterManagerFrame`.
  * `'help'`: `HelpSupportFrame`.
- Triển khai hàm `switch_view(view_key: str)`:
  ```python
  def switch_view(self, view_key: str):
      if view_key not in self._views:
          return
      # Ẩn view hiện tại bằng grid_remove (giữ nguyên bindings và state)
      if self._current_view:
          self._current_view.grid_remove()
          if hasattr(self._current_view, "on_view_hidden"):
              self._current_view.on_view_hidden()
      # Hiện view mới
      target_view = self._views[view_key]
      target_view.grid(row=1, column=1, sticky="nsew")
      self._current_view = target_view
      if hasattr(target_view, "on_view_shown"):
          target_view.on_view_shown()
  ```
- Tuyệt đối không gọi `destroy()` trên các view khi chuyển đổi để bảo toàn 100% dữ liệu form và event listeners.
- **View tự polling UI không được chạy nền vô ích khi bị ẩn**: bất kỳ view nào tự lên lịch định kỳ qua `self.after(...)` để cập nhật UI của chính nó (ví dụ đọc trạng thái để refresh label) phải triển khai `on_view_hidden()`/`on_view_shown()` để tạm dừng/tiếp tục vòng lặp `after()` nội bộ theo trạng thái hiển thị, tránh việc tất cả các view cùng chạy self-polling song song ngay từ lúc app khởi động dù người dùng chỉ nhìn thấy một view tại một thời điểm.
- **Không được nhầm lẫn giữa việc ẩn view UI và việc dừng nghiệp vụ nền**: `grid_remove()` trên `HuntWorkspaceFrame` chỉ ẩn giao diện, tuyệt đối không được (trực tiếp hay gián tiếp qua `on_view_hidden`) tạm dừng, dừng, hoặc can thiệp vào `HuntOrchestrator`/worker thread đang chạy — luồng săn (nếu đang chạy) phải tiếp tục hoạt động bình thường bất kể người dùng đang xem view nào. `on_view_hidden()` của `HuntWorkspaceFrame` chỉ nên dừng các vòng lặp cập nhật UI cục bộ (progressbar, label...), không chạm vào tầng orchestrator.
- **Global hotkey hook (đăng ký ở tầng app theo CB3B) độc lập với vòng đời view**: không đăng ký lại hoặc huỷ global hotkey trong `on_view_shown`/`on_view_hidden` — các hotkey đó thuộc phạm vi ứng dụng, không thuộc phạm vi từng view. Binding cục bộ trên widget (event của riêng view) tự nhiên sẽ không kích hoạt khi view bị ẩn/không focus, đó là hành vi bình thường và không cần xử lý thêm.

### 3. Tích Hợp Đa Ngôn Ngữ (i18n) Cho Toàn Bộ Shell
- Đăng ký đầy đủ key dịch thuật song ngữ (vi/en) cho tất cả các nút điều hướng trên Sidebar C1: `sidebar.quick_setup`, `sidebar.monster_manager`, `sidebar.skill_manager`, `sidebar.system_config`, `sidebar.support`.
- Khi đổi ngôn ngữ, gọi hàm `update_shell_translations()` để làm mới text của Sidebar và Shell mà không kích hoạt lại hàm khởi tạo view.

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_shell_navigation.py`)
- Test Full Loop View Swapping: Khởi tạo App → Chuyển tuần tự: Hunt → Setup → MonsterManager → Help → Hunt.
- Nhập text vào một ô Entry trong Setup → Chuyển sang Hunt rồi quay lại Setup → Assert chuỗi text vừa nhập vẫn tồn tại 100%.
- Test Zero Geometry Conflict: Duyệt toàn bộ cây widget của `main_shell` → Assert không có container nào chứa đồng thời cả `pack_slaves()` và `grid_slaves()`.
- (Added) Test Hunt Continues While Hidden: Bắt đầu một phiên hunt giả lập (mock orchestrator ở trạng thái `RUNNING`) → chuyển sang view `setup` → Assert orchestrator vẫn ở trạng thái `RUNNING` và worker thread không bị dừng/tạm ngưng, chỉ có UI của `HuntWorkspaceFrame` ngừng cập nhật.
- (Added) Test View Hidden Stops Self-Polling: Gắn một `after()` polling giả lập vào một view mock → ẩn view → Assert vòng lặp `after()` nội bộ của view đó dừng lại; hiện lại view → Assert vòng lặp tiếp tục.

### 2. Visual & High-DPI Check
- Kiểm tra bố cục không bị tràn/đè khung ở các mức DPI: 100%, 125%, 150%, 175%, 200% (đặc biệt trên màn hình 1920x1080 và fallback 1280x720), xác nhận `minsize` co giãn đúng theo công thức `scale_factor` thống nhất ở mọi mốc, không chỉ 3 mốc cao.

## Session Boundary Gate

**PASSED nếu:**
- Khung lưới 4 vùng hiển thị vững chắc, view swapping chuyển đổi mượt mà không làm mất dữ liệu người dùng.
- Không phát sinh lỗi `_tkinter.TclError: cannot use geometry manager grid inside...`.
- Hỗ trợ đầy đủ ngôn ngữ vi và en trên toàn bộ Sidebar.
- Luồng hunt (nếu đang chạy) không bị ảnh hưởng bởi việc chuyển view.
- View bị ẩn không tiếp tục self-polling UI ở tầng nền.

**REVERTED nếu:**
- Xung đột geometry manager làm crash app hoặc mất dữ liệu khi chuyển tab.
- Chuyển view vô tình làm gián đoạn luồng hunt đang chạy.
- Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.