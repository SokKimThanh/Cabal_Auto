# Task 9: Chuẩn hóa Hệ thống Icon (Standardize Icon System) cho Hunt Tab

## Bối cảnh (Context)
Dự án có quy định nghiêm ngặt về việc sử dụng hệ thống quản lý Icon (`IconHelper`, `UIElementRegistry`, database `icons`) để đảm bảo UI đồng nhất và có thể thay đổi icon theme mà không phải sửa code. Tuy nhiên, các Panel trong Tab Hunt (Target Setup, Active Skills, Target Status) đang bị lỗi "hardcode" rất nhiều emoji bằng text (như `🎯`, `➕`, `⏱`, `🔴`, `🟢`) và các nút bấm chưa tuân chuẩn thiết kế `create_icon_button`.

## Yêu cầu (Requirements)
1. Rà soát file `ui/panels/monster_target_panel.py`:
   - Thay thế toàn bộ `tk.Button` bằng hàm `create_icon_button(..., element_id="...")`.
   - Các icon như (Move Up, Move Down, Delete, Add) phải sử dụng các `button_type` chuẩn (như `red`, `blue`, `green_light`) hoặc fallback icon key tương ứng.
2. Rà soát file `ui/panels/skill_panel.py` và `ui/panels/target_status_panel.py`:
   - Loại bỏ các Emoji báo trạng thái (Ví dụ: Chấm tròn 🔴 / 🟢). Sử dụng `IconHelper` để tải ảnh trạng thái thực tế.
   - Các nhãn báo Cooldown, Cast Time (`⏱`, `🔄`) nên thay bằng `create_icon_label` hoặc xóa bỏ emoji và dùng text sạch.
3. Đảm bảo tất cả các widget tương tác đều truyền tham số `element_id` để đăng ký vào `UIElementRegistry`. Nếu là nút dùng chung có thể khai báo vào enum `CommonUI`.

## Rủi ro (Risks & Pitfalls)
- **Garbage Collection (Mất ảnh Icon):** Nếu bạn thay Emoji bằng `tk.Label(image=...)` thủ công, bạn PHẢI lưu reference (tham chiếu) của `PhotoImage` (ví dụ `lbl.image = img`) nếu không icon sẽ bị nhấp nháy hoặc biến mất thành ô trắng do Python xóa rác. Dùng `create_icon_button` sẽ tự động lo việc này, nhưng với Label thường thì bạn phải tự quản lý.
- Kiểm tra tính tương thích ngược của các lệnh `config(text="...")` cũ đang thao tác trực tiếp lên nút bấm (ví dụ code cũ đang đổi emoji từ ➕ sang ✓ khi thao tác).

## Unit Tests Cần Thêm (Unit Tests to Add)
- Kiểm tra `UIElementRegistry` xem các nút trong Tab Hunt có xuất hiện trong danh sách đăng ký không.
- Test thủ công đảm bảo Icon không bị mất đi sau khi di chuột (hover) hoặc sau khi đóng/mở lại tab.