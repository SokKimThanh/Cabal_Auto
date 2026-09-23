# Prompt: Sweep emoji standardize icon

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #2.

## 🎯 Scope
- Finding: #2 | Priority: P1 | Estimate: 8h
- Dependency: Independent (Thực hiện trọn 1 ngày)
- Dependency Check: `grep -rn -P "[🔴🟢🎯➕⏱🔄ℹ️⚠️🔍⚔️📊📈⊕👹✏️⌛]" ui/ lib/features/hunt/`

## 🔍 Vấn đề cần fix
Toàn bộ mã nguồn vẫn còn hơn 20 chỗ hardcode emoji trên các nút, nhãn và event bus, vi phạm chuẩn thiết kế. Cần quét toàn bộ và chuẩn hóa, thay thế chúng bằng `IconHelper` và `create_icon_button` hoặc system icon thay thế.

## 📂 Files cần sửa
- `ui/panels/monster_target_panel.py` — grep: `grep -n -P "[🎯✓]" ui/panels/monster_target_panel.py`
- `ui/components/hunt_status_ticker.py` — grep: `grep -n -P "[ℹ️🔄⚠️🔍]" ui/components/hunt_status_ticker.py`
- `ui/panels/skill_panel.py` — grep: `grep -n -P "[⚔️]" ui/panels/skill_panel.py`
- `ui/panels/target_status_panel.py` — grep: `grep -n -P "[📊⊕]" ui/panels/target_status_panel.py`
- `ui/panels/skill_stats_panel.py` — grep: `grep -n -P "[📈]" ui/panels/skill_stats_panel.py`
- `ui/tabs/hunt_tab.py` — thay thế `tk.Button` bằng `create_icon_button`
- `ui/components/combo_rhythm_bar.py`
- `ui/components/status_badge.py`
- `lib/features/hunt/monster_manager_win.py` — grep: `grep -n -P "[👹🔍ℹ️✏️📊⌛]" lib/features/hunt/monster_manager_win.py`
- `lib/features/hunt/hunt_orchestrator.py`

## 📂 File Ownership
### Primary Owner (toàn quyền)
- Các file có số lượng lỗi lớn không nằm trong phần Shared Access dưới đây.
### Shared File (chỉ sửa subsection)
- Tất cả các file đề cập (chỉ được thay đổi string/emoji/tk.Button thành icon_helper code, không chạm vào logic hoặc flow của component).

## ✅ Requirements
1. Tuyệt đối không còn emoji cứng như 🔴, 🟢, ⚠️ trong codebase UI.
   **Trace:** Source: Finding #2 / Debt D6
2. Các nút (Button) trong các Panel trên UI phải sử dụng thư viện `create_icon_button`.
   **Trace:** Source: Finding #2
3. Các string hiển thị cố định phải dùng hàm chuyển đổi đa ngôn ngữ `_t()`.
   **Trace:** Source: Finding #2 / Debt D6

## 🚫 Out of scope
- Cập nhật thư viện `icon_helper.py` hiện tại (thư viện đã chuẩn).
- Tái cấu trúc logic nội bộ của các Panel ngoài việc sửa hiển thị.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -rn -P "[🔴🟢🎯➕⏱🔄ℹ️⚠️🔍⚔️📊📈⊕👹✏️⌛]" ui/ lib/features/hunt/` → Trả về 0 kết quả (ngoại trừ comment/documentation).
- [ ] AC2: `grep -rn "create_icon_button" ui/` → Output tăng lên so với ban đầu.
- [ ] AC3: Test hiện có cho toàn bộ component (ví dụ test combo bar, status panel) tiếp tục pass.
- [ ] AC4: Mọi chuỗi hiển thị tĩnh đều được bao bọc bởi `_t("...")`.

## 🧪 Verification
**Grep:** `grep -rn -P "[🔴🟢🎯➕⏱🔄ℹ️⚠️🔍⚔️📊📈⊕👹✏️⌛]" ui/ lib/features/hunt/` → Expected: Rỗng.
**Test:** `pytest -v tests/ui/` → Expected: Toàn bộ pass.
**Manual:** Mở ứng dụng, kiểm tra tất cả các UI component để đảm bảo icon được load và hiển thị mượt mà.

## 📤 Output format
1. Danh sách file đã sửa.
2. Diff tóm tắt thay đổi chung.
3. Kết quả grep check rỗng.
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Component icon thay thế không tương thích với widget cũ (`ttk.Label` vs `tk.Label`).
- Phát hiện emoji bị hardcode trong DB hoặc file cấu hình, không nằm trong code Python.
- Test hiện có fail vì nguyên nhân không phải UI hiển thị thay đổi.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-4.md`
- Tiêu chuẩn D6.