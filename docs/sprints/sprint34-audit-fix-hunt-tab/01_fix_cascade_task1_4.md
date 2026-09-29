# Prompt: Fix cascade Task 1 ↔ Task 4

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #1.

## 🎯 Scope
- Finding: #1 | Priority: P0 | Estimate: 2h
- Dependency: Independent
- Dependency Check: `grep -rn "get_combo_sequence" ui/panels/skill_panel.py`

## 🔍 Vấn đề cần fix
`SkillPanelController.get_combo_sequence()` và `get_buff_sequence()` đã được triển khai đầy đủ từ Task 1 nhưng không được gọi để truyền vào `SkillTimelineStrip` tại Task 4, dẫn đến UI render danh sách skill bị rỗng. Cần truyền dữ liệu vào lúc khởi tạo.

## 📂 Files cần sửa
- `ui/panels/skill_panel.py` — nơi có `SkillTimelineStrip(self.content_frame)`, grep: `grep -n "SkillTimelineStrip" ui/panels/skill_panel.py`

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/panels/skill_panel.py`
### Shared File (chỉ sửa subsection)
- `ui/components/skill_timeline_strip.py`
  - Được sửa: Phương thức khởi tạo/cập nhật dữ liệu từ controller nếu cần.
  - KHÔNG được sửa: Fallback render image (để cho task 02).

## ✅ Requirements
1. Dữ liệu từ controller (combo và buff sequence) phải được truyền vào hai instance của `SkillTimelineStrip` một cách chính xác.
   **Trace:** Source: Finding #1 / Debt D1
2. Giao diện sau khi khởi tạo phải hiển thị các kỹ năng động từ cấu hình JSON/Controller thay vì danh sách rỗng.
   **Trace:** Source: Finding #1

## 🚫 Out of scope
- Refactor cấu trúc chung của `SkillPanelController` đã hoàn thiện ở Task 1.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -rn "get_combo_sequence\|get_buff_sequence" ui/panels/skill_panel.py` → Output trả về vị trí hai hàm được gọi.
- [ ] AC2: UI Panel render các dải kỹ năng đúng thứ tự định nghĩa trong cấu hình.
- [ ] AC3: Không phá vỡ test hiện có của `test_skill_panel.py`.
- [ ] AC4: Không vi phạm nguyên tắc hardcode thông số config.

## 🧪 Verification
**Grep:** `grep -rn "get_combo_sequence" ui/panels/skill_panel.py` → Expected: Xuất hiện ít nhất một lượt gọi.
**Test:** `pytest tests/ui/panels/test_skill_panel.py -v` → Expected: X/Y passed.
**Manual:** Mở ứng dụng, mở tab Hunt, kiểm tra danh sách skill hiển thị trong phần combo và buff.

## 📤 Output format
1. Files đã sửa (không cần line number).
2. Diff tóm tắt (15 dòng).
3. Kết quả grep + pytest.
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Không tìm thấy instance của `SkillTimelineStrip` trong `skill_panel.py`.
- Cần sửa cấu trúc trả về của các method trong `SkillPanelController`.
- Giao diện UI bị thay đổi sai lệch quá lớn cần can thiệp file cấu trúc gốc (Ví dụ `ResponsiveGridBase`).

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-1.md` và `audit-batch-3.md`
- Spec gốc: `04_task_skill_panel.md`