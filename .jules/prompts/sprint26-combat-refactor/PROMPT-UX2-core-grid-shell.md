# Session Prompt UX2: Build Four-Zone Core Grid Container & Migrate Shell

Timebox: 25–30 minutes.  
Priority: High – Establishes the 4-zone layout foundation with DPI resilience.

---

## Objective
Xây dựng container chính `main_shell` quản lý bằng `pack()` và chia lưới 4 vùng A, B, C1, C2 bằng `grid()` với thông số `weight` và `minsize` tường minh. Loại bỏ hoàn toàn Tab Notebook con lồng trong Vùng B, thiết lập cơ chế View Swapping an toàn cho các view có event bindings phức tạp, hỗ trợ DPI từ 100% đến 200% và song ngữ i18n đầy đủ.

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
  * **Hàng 2 (Vùng C2/D - Logs):** `rowconfigure(2, weight=0, minsize=36)`.
  * **Cột 0 (Vùng C1 - Sidebar):** `columnconfigure(0, weight=0, minsize=260)`.
  * **Cột 1 (Vùng B - Workspace):** `columnconfigure(1, weight=1, minsize=960)`.
- Áp dụng hệ số co giãn DPI (`scale_factor`) cho các giá trị `minsize` khi màn hình chạy ở DPI 150%, 175%, 200%.
- **CẤM:** Tuyệt đối không dùng lệnh `pack()` bên trong các container đã cấu hình `grid()` và ngược lại.

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
      # Hiện view mới
      target_view = self._views[view_key]
      target_view.grid(row=1, column=1, sticky="nsew")
      self._current_view = target_view
Tuyệt đối không gọi destroy() trên các view khi chuyển đổi để bảo toàn 100% dữ liệu form và event listeners.3. Tích Hợp Đa Ngôn Ngữ (i18n) Cho Toàn Bộ ShellĐăng ký đầy đủ key dịch thuật song ngữ (vi/en) cho tất cả các nút điều hướng trên Sidebar C1:sidebar.quick_setup, sidebar.monster_manager, sidebar.skill_manager, sidebar.system_config, sidebar.support.Khi đổi ngôn ngữ, gọi hàm update_shell_translations() để làm mới text của Sidebar và Shell mà không kích hoạt lại hàm khởi tạo view.Validation & Testing1. Automated Tests (tests/unit/test_shell_navigation.py)Test Full Loop View Swapping:Khởi tạo App -> Chuyển tuần tự: Hunt $\rightarrow$ Setup $\rightarrow$ MonsterManager $\rightarrow$ Help $\rightarrow$ Hunt.Nhập text vào một ô Entry trong Setup -> Chuyển sang Hunt rồi quay lại Setup -> Assert chuỗi text vừa nhập vẫn tồn tại 100%.Test Zero Geometry Conflict:Duyệt toàn bộ cây widget của main_shell -> Assert không có container nào chứa đồng thời cả pack_slaves() và grid_slaves().2. Visual & High-DPI CheckKiểm tra bố cục không bị tràn/đè khung ở các mức DPI: 100%, 125%, 150%, 175%, 200% (đặc biệt trên màn hình $1920 \times 1080$ và fallback $1280 \times 720$).Session Boundary GatePASSED nếu:Khung lưới 4 vùng hiển thị vững chắc, view swapping chuyển đổi mượt mà không làm mất dữ liệu người dùng.Không phát sinh lỗi _tkinter.TclError: cannot use geometry manager grid inside....Hỗ trợ đầy đủ ngôn ngữ vi và en trên toàn bộ Sidebar.REVERTED nếu:Xung đột geometry manager làm crash app hoặc mất dữ liệu khi chuyển tab.Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.