# Sprint 32 - Prompt 004: Refactor Dynamic Text trên Panels

**Vai trò:** Frontend Engineer

**Ngữ cảnh:**
Khu vực Panels (`ui/panels/`) chứa rất nhiều text phức tạp (như "1 / 1", "— / —", các icon chữ "🟢").

**Yêu cầu công việc:**
1. Rà soát `monster_target_panel.py`, `skill_panel.py`, `target_status_panel.py`, `skill_stats_panel.py`.
2. Đối với các text tiêu đề Panel (như `text="🎯 Target Setup"`): tách icon và text, chuyển text sang translation key.
3. Đối với các text mang tính biến số (ví dụ: `text="1 / 1"` hoặc trạng thái `text="—"`): Chuyển thành cấu trúc translation có param. Ví dụ `text=self.app._t("lbl.pagination", current=1, total=1)`.
4. Các nút bấm bằng Emoji text ("➕", "🔒"): Xem xét chuyển đổi thành Icon key, hoặc nếu chưa sẵn sàng, giữ nguyên và đánh dấu `// TODO: Convert to icon_key`.

**Ràng buộc:**
- Các hàm update giao diện (`update_hp`, `update_page_info`) phải sử dụng chuỗi dịch thuật kèm param động thay vì hardcode format chuỗi trực tiếp.

**Kết quả mong đợi:**
- Panels sử dụng Localization và có khả năng hiển thị biến số tự động.
