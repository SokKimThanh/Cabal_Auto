# Sprint 30: Prompt Review - Remove UI Code From State

## Review Prompt Instruction

**Reviewer Role:** Technical Lead / Senior Architect
**Task to Review:** Kết quả thực thi của `sprint30-prompt-018-remove-ui-code-from-state.md`
**Target Files:** `ui/controllers/app_state_controller.py`, và file View giao diện chứa logic Skill (như `SkillPanel` hoặc `app_gui.py`).

**Review Criteria (Checklist):**
1. Mở file `app_state_controller.py`, xem xét hai hàm `_refresh_slot_key_labels` và `_validate_slot_key_duplicates` (nếu còn). CÓ CÒN lệnh `.config(...)` hay bất kỳ thư viện UI `tkinter` nào bị dính líu (như import `tk`) trong scope của hai hàm đó không?
2. Kiểm tra xem 2 hàm đó có phát ra (emit) Event chính xác không.
3. Chuyển sang file View tương ứng (thường là nơi hiển thị Skill Slots). Mở code ra kiểm tra: View đã gọi `.register_callback()` hoặc bind Event của Controller để tự gọi hàm `.config(fg=...)` tương ứng chưa?
4. Đảm bảo mảng chứa Tkinter Widgets (ví dụ `skill_slot_key_labels`) đã được gỡ bỏ khỏi Controller và chuyển thành một biến quản lý local bên trong View.

**Status / Feedback:**
- [ ] PASS: Ranh giới MVC (Model/Controller - View) được phân tách hoàn toàn sạch sẽ. Controller không dính tí UI nào.
- [ ] FAIL (Cần ghi rõ lỗi và đề xuất chạy lại).