# Prompt 001 - Liên kết Dữ liệu Build với Lane Skills

## 1. Mục tiêu (Objective)
- Giải quyết bài toán gián đoạn trải nghiệm người dùng (UX) giữa chức năng "Quản lý Build" (Build Manager) và việc sắp xếp kỹ năng (Lane Skills).
- Cải thiện cơ sở dữ liệu Build để có thể lưu trữ danh sách các Skill (Attack Combo, Buff Lane).
- Thêm chức năng "Áp dụng Build" vào thẳng Skill Lane/Preset để tự động hóa việc gán kỹ năng.

## 2. Phạm vi thay đổi (Scope)
- **Cơ sở dữ liệu (Database):** Cập nhật schema lưu trữ Build để hỗ trợ mảng/danh sách `skill_ids` cho cả Attack và Buff.
- **Backend/Services:** Cập nhật các hàm CRUD của Build để xử lý dữ liệu kỹ năng.
- **UI - Build Manager:** Bổ sung giao diện chọn/chỉnh sửa kỹ năng trực tiếp trong cửa sổ tạo/sửa Build. Thêm nút "Áp dụng vào Lane".
- **UI - Skill Panel/Preset:** Nhận tín hiệu (Event) từ Build Manager để nạp dữ liệu kỹ năng vào lane hiện hành.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- Dữ liệu Build có thể lưu trữ và truy xuất đầy đủ cấu trúc của một Combo kỹ năng.
- Người dùng có thể xem chi tiết một Build và nhấn "Áp dụng" để các kỹ năng tự động được ném lên thanh Lane (Combo Chain / Buff Lane).
- Không làm vỡ cấu trúc Preset hiện tại.
- Vượt qua toàn bộ Unit Test và Integration Test.
- Không phát sinh Technical Debt mới (Code smell, hardcode configuration).

## 4. Các rủi ro tiềm ẩn (Risks)
- Việc thay đổi cấu trúc bảng lưu trữ Build có thể gây xung đột với các tính năng cũ đang truy vấn bảng này.
- Khi "Áp dụng Build", nếu dữ liệu class của Build không khớp với class hiện tại của nhân vật, có thể gây lỗi nạp kỹ năng sai.

## 5. Các điểm yếu hoặc sai lầm thường gặp cần tránh
- Quên validate (kiểm tra hợp lệ) class_id trước khi áp dụng Build vào Lane.
- Không sử dụng EventBus để truyền dữ liệu giữa Build Manager và Skill Panel, dẫn đến Tight Coupling (phụ thuộc cứng) giữa 2 UI.
- Quên thêm fallback khi database chưa được migrate lên schema mới.

## 6. Kế hoạch Rollback (Rollback Plan)
- Nếu thay đổi DB bị lỗi: Restore lại file DB (`monsters.db` hoặc file tương ứng) từ bản sao lưu.
- Nếu UI lỗi: Revert commit liên quan đến `build_manager_frame.py` và `skill_panel.py`.
- Tạo nhánh riêng (feature/sprint35-skill-build-link) để đảm bảo không làm hỏng nhánh chính (main).

---

## 7. Kế hoạch triển khai (Implementation Plan)
*Lưu ý: Kế hoạch này dùng cho Sub-agent / AI thực hiện.*
1. **Bước 1:** Khảo sát và viết script Migration cho bảng Build trong CSDL.
2. **Bước 2:** Cập nhật Service/Repository của Build.
3. **Bước 3:** Nâng cấp UI của BuildEditDialog (Thêm phần chọn kỹ năng).
4. **Bước 4:** Nâng cấp UI của BuildManagerFrame (Thêm nút Apply).
5. **Bước 5:** Tích hợp EventBus lắng nghe sự kiện `ApplyBuildEvent` tại `SkillPanelController`.

## 8. Báo cáo kết quả (Report)
*(Sẽ được điền sau khi hoàn thành)*
- **Kết quả:** ...
- **Vấn đề phát sinh:** ...
- **Bài học rút ra:** ...

## 9. Ghi chú kỹ thuật liên quan (Technical Notes)
- Để đảm bảo nguyên tắc Low Coupling, khi nút "Áp dụng" được nhấn, chỉ nên phát ra một Event `(Ví dụ: ApplyBuildToLaneEvent(build_data))`. Các Controller bên Hunt Tab sẽ tự động bắt Event này và xử lý.
- Cần chú ý file CSDL SQLite hiện tại có hỗ trợ kiểu JSON hay không, nếu không sẽ phải chuyển đổi danh sách ID thành chuỗi phân cách bằng dấu phẩy (comma-separated string).
