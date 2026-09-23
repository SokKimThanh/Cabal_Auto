# Prompt: Decouple D1 config

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Tech Debt D1.


## 🔄 Trạng thái hiện tại
- 🔴 **Chưa hoàn thành**: `hunt_cfg` vẫn được gọi trực tiếp (`.get(...)`) ở khắp các layer giao diện thay vì qua controller.
- **Hành động**: Tiến hành tách rời luồng đọc/ghi config ra khỏi các file UI.

## 🎯 Scope
- Finding: D1 | Priority: P1 | Estimate: 6h
- Dependency: Task 01 đến 05 hoàn thiện
- Dependency Check: `grep -rn "hunt_cfg.get" ui/`

## 🔍 Vấn đề cần fix
Việc các file UI sử dụng trực tiếp `hunt_cfg.get(...)` tạo ra sự phụ thuộc chặt chẽ (tight coupling) giữa giao diện và cấu trúc cấu hình. Đặc biệt trong `skill_panel.py`, `hunt_tab.py`, và `setup_tab.py`. Cần dời toàn bộ logic đọc/ghi cấu hình này vào Controller/Service tương ứng.

## 📂 Files cần sửa
- `ui/panels/skill_panel.py` — grep: `grep -n "hunt_cfg.get" ui/panels/skill_panel.py`
- `ui/tabs/hunt_tab.py` — grep: `grep -n "hunt_cfg.get" ui/tabs/hunt_tab.py`
- `ui/tabs/setup_tab.py` — grep: `grep -n "hunt_cfg.get" ui/tabs/setup_tab.py`
- `ui/controllers/skill_panel_controller.py` — Chứa logic đọc/ghi.
- Thêm controller nếu thiếu ở các tab khác.

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/controllers/skill_panel_controller.py`
- `ui/panels/skill_panel.py`
- `ui/tabs/setup_tab.py`
### Shared File (chỉ sửa subsection)
- `ui/tabs/hunt_tab.py` (chỉ thay thế các truy xuất config).

## ✅ Requirements
1. Tuyệt đối không còn lời gọi `hunt_cfg.get` trực tiếp trong các file UI (*.py trong `ui/`).
   **Trace:** Source: Debt D1
2. Mọi thao tác đọc/ghi config từ UI phải đi qua Controller, ví dụ `controller.is_combo_enabled()`.
   **Trace:** Source: Debt D1
3. Các cấu hình khi thay đổi từ UI phải lưu lại bằng `save_hunt_config()`.
   **Trace:** Source: Finding #4 / Debt D1

## 🚫 Out of scope
- Cấu trúc lại toàn bộ hệ thống schema Pydantic.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -rn "hunt_cfg\.get" ui/` → Trả về rỗng.
- [ ] AC2: `grep -rn "save_hunt_config" ui/` → Trả về rỗng (tất cả phải nằm ở Controller/Service).
- [ ] AC3: Giao diện (Toggle Combo, Set ROI) vẫn lưu trữ và load đúng trạng thái khi restart.
- [ ] AC4: Không phá vỡ Unit test hiện tại của Controller.

## 🧪 Verification
**Grep:** `grep -rn "hunt_cfg" ui/` → Expected: Không còn truy xuất trực tiếp ngoại trừ việc truyền obj vào controller.
**Test:** `pytest tests/ui/controllers/ -v` → Expected: Pass toàn bộ các hàm get/set.
**Manual:** Bật toggle combo, đóng app, mở lại, kiểm tra trạng thái lưu đúng.

## 📤 Output format
1. Danh sách file thay đổi.
2. Diff logic controller và giao diện.
3. Kết quả grep.
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Cấu trúc Pydantic cần được thay đổi để khớp với Controller.
- Thiếu Test cho các luồng write config mới.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-1.md` và `audit-batch-3.md`