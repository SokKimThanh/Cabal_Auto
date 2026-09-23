# Prompt: Fix TclError fallback crash

## 📖 Context
Đọc `00_context_audit_summary.md` trước. Task này fix Finding #4.

## 🎯 Scope
- Finding: #4 | Priority: P0 | Estimate: 1h
- Dependency: Independent
- Dependency Check: `grep -rn "create_image" ui/components/skill_timeline_strip.py`

## 🔍 Vấn đề cần fix
Trong `SkillTimelineStrip`, khi `IconHelper` không tìm thấy file PNG và trả về string emoji, phương thức `create_image(image=string_emoji)` của Tkinter sẽ văng `_tkinter.TclError`, dẫn đến crash ứng dụng. Cần sửa logic fallback: dùng text thay vì image nếu dữ liệu trả về là string.

## 📂 Files cần sửa
- `ui/components/skill_timeline_strip.py` — nơi có `create_image(..., image=img)`, grep: `grep -n "create_image.*image=" ui/components/skill_timeline_strip.py`

## 📂 File Ownership
### Primary Owner (toàn quyền)
- `ui/components/skill_timeline_strip.py`
### Shared File (chỉ sửa subsection)
- KHÔNG CÓ

## ✅ Requirements
1. Kiểm tra kiểu dữ liệu của biến `img` trả về từ `icon_helper.get_icon()`. Nếu là text/string thì sử dụng hàm `create_text()`, ngược lại mới dùng `create_image()`.
   **Trace:** Source: Finding #4
2. Ngăn chặn 100% rủi ro `_tkinter.TclError` trong trường hợp máy thiếu file icon.
   **Trace:** Source: Finding #4

## 🚫 Out of scope
- Sửa đổi thư viện `icon_helper.py`.

## 🧪 Acceptance Criteria
- [ ] AC1: `grep -n "create_text" ui/components/skill_timeline_strip.py` → Output trả về vị trí xử lý fallback text.
- [ ] AC2: Xử lý fallback không làm crash ứng dụng khi chạy app trên máy bị thiếu icon resource.
- [ ] AC3: Pass toàn bộ unit tests hiện có trong `test_skill_timeline_strip.py`.
- [ ] AC4: Không hardcode icon trực tiếp, tuân thủ convention.

## 🧪 Verification
**Grep:** `grep -n "isinstance(.*str)" ui/components/skill_timeline_strip.py` → Expected: Kiểm tra chuỗi trước khi render.
**Test:** `pytest tests/unit/ui/components/test_skill_timeline_strip.py -v` → Expected: Pass.
**Manual:** Rename thư mục chứa PNG tạm thời, mở Hunt tab và xác minh app dùng ký tự chữ thay vì crash.

## 📤 Output format
1. Files đã sửa (không cần line number).
2. Diff tóm tắt (15 dòng).
3. Kết quả grep + pytest.
4. Blocker nếu có.

## 🛑 Stop Conditions
DỪNG và báo user nếu:
- Cách render bằng `create_text` không hoạt động như mong đợi do thiết lập font.
- Phát hiện crash do lỗi TclError khác bên ngoài file.
- Không thể mô phỏng trường hợp fallback thông qua unit test.

## 🔗 Reference
- Context: `00_context_audit_summary.md`
- Audit: `audit-batch-2.md`
- Spec gốc: `03_task_skill_timeline.md`