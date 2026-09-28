# Build Feature Audit & Root Cause Analysis

## 1. Hiện trạng (Current State)
Chức năng Quản lý Build (`BuildManagerFrame`) và màn hình Thêm/Sửa Build (`BuildEditDialog`) đang gặp một số vấn đề về hiển thị dữ liệu và trải nghiệm người dùng (UX). Cụ thể, khi người dùng mở màn hình thêm/sửa Build và chọn một Class hợp lệ, danh sách Attack Skills và Buff Skills hiện ra trống trơn (như trong ảnh chụp).

Về mặt UX, giao diện không hiển thị tối ưu (màu nền danh sách dễ làm chìm text, thiếu tính năng lọc skill) và code còn chứa technical debt liên quan đến localization (i18n) và thiết kế responsive.

## 2. Phân tích chức năng Build (Business & Data Context)
- **Nghiệp vụ:** Chức năng Build dùng để nhóm một danh sách các Kỹ năng Tấn công (Attack Skills) và Kỹ năng Buff (Buff Skills) tương ứng với một Class cụ thể để chia sẻ (author, description, upvotes) hoặc để load vào `hunt_config` cho Auto Bot sử dụng qua `SkillRotation` builder.
- **Model / Database:** Bảng `builds` chứa: `build_id`, `class_id`, `author`, `description`, `upvote_count`, `attack_skill_ids` (JSON), `buff_skill_ids` (JSON).
- **Tính đầy đủ:** Các trường cơ bản đủ dùng cho việc map kỹ năng. Tuy nhiên, tính năng Apply Build (áp dụng build vào setup hiện tại) dường như chưa được hoàn thiện 100% trong `BuildManagerFrame` (chỉ in log `Apply build clicked...`).

## 3. Luồng dữ liệu và Root Cause (Skills List Empty)

### Luồng lấy dữ liệu (Data Flow)
1. Trong `BuildEditDialog`, khi Class thay đổi, `_load_skills()` được gọi.
2. `self.app.db_skill_service.get_skills_by_filter(class_id=class_id)` được truy vấn.
3. Trong `SkillService.get_skills_by_filter`, câu lệnh SQL join bảng `skills` với `class_skill_assignments`:
   `SELECT skills.*, st.name AS type FROM skills ... JOIN class_skill_assignments csa ON skills.skill_id = csa.skill_id WHERE csa.class_id = ?`
4. Result set trả về các kỹ năng có map với class này (e.g. 34 skills cho Class 1 - Blader).
5. Tuy nhiên, ở `BuildEditDialog`, code thực hiện:
   `atk_skills = [s for s in all_skills if s.get("skill_type_id") == 1]`
   `buff_skills = [s for s in all_skills if s.get("skill_type_id") == 2]`

### Root Cause
Các kỹ năng crawl về từ web (crawl_import) được insert vào bảng `skills` với cột `skill_type_id = NULL`. Phân loại kỹ năng (tấn công = 1, buff = 2) thực tế được lưu chính xác trong bảng quan hệ `class_skill_assignments` ở cột `csa.skill_type_id`.
Vì câu query trong `get_skills_by_filter` dùng `SELECT skills.*`, nó lấy `skill_type_id` bị NULL từ bảng `skills` thay vì giá trị đúng từ bảng `class_skill_assignments`. Do đó, cả hai list `atk_skills` và `buff_skills` ở `BuildEditDialog` đều filter ra mảng rỗng `[]`, dẫn đến UI hiển thị màu đen trống rỗng.

**Call Chain:** `UI Combobox` -> `_load_skills()` -> `get_skills_by_filter()` -> `DB SELECT skills.* (skill_type_id=None)` -> `atk_skills = []` -> `Listbox empty`.

## 4. Rà soát UX (BuildEditDialog & BuildManagerFrame)

### BuildEditDialog (Form thêm/sửa)
- **Layout & Responsive:** Class kế thừa trực tiếp từ `tk.Toplevel`, gọi `geometry("600x550")` và dùng grid layout cơ bản mà không dùng framework chuẩn của project như `ResponsiveGridBase` hay `ExpandedPanel`. Khung cứng nhắc, khi resize sẽ bị lỗi vùng chết.
- **Form:**
  - Thiếu mô tả cho trường "Author" và "Description".
  - Các ô nhập liệu dùng chiều rộng cứng (width=33).
- **Skill Selection:**
  - Khung `tk.Listbox` khó nhìn (màu select là primary trên nền đen surface), không trực quan.
  - Người dùng không có công cụ "Search" hoặc "Filter" bên trong list skill, phải cuộn tìm rất khó khăn khi class có hàng chục kỹ năng.
  - Cho phép người dùng vô tình tạo Build với danh sách rỗng (thiếu Validation ở Dialog).

### BuildManagerFrame (Màn hình chính)
- Có sử dụng `ResponsiveGridBase` nhưng khung Search Bar (`_create_search_bar`) đóng gói dạng `tk.Frame` cứng thay vì dùng Component chuẩn.
- Bảng Grid (Treeview) hiển thị tốt, hỗ trợ phân trang nhưng UI phân trang hơi thô.
- Cột Attack/Buff preview chỉ in ra JSON `[1, 2, 3]` ở phần Details, khó hiểu đối với end-user (nên hiển thị tên kỹ năng).

## 5. Technical Debt
- **i18n (Localization):**
  - Trong `BuildEditDialog`, rất nhiều chuỗi cứng (hardcoded text) như: `"Class (*):"`, `"Author:"`, `"Description:"`, `"Upvotes:"`, `"Lỗi"`, `"Vui lòng chọn Class hợp lệ."`.
  - Không sử dụng `app.bind_text(...)` để hỗ trợ chuyển đổi ngôn ngữ runtime.
- **Clean Code & UI Components:**
  - Không có `tk.Button` thừa (đã dùng `create_icon_button`), đây là điểm tốt.
  - Tuy nhiên, `BuildEditDialog` đang đi lệch chuẩn thiết kế Dialog chung (vẫn đang mix giữa `tk` và `ttk` manual thay vì UIStyle encapsulation hoàn chỉnh).

## 6. Đề xuất Cải tiến & Kế hoạch triển khai (Implementation Plan)

### Pha 1: Fix Root Cause & Data Pipeline (Backend)
- Sửa câu lệnh SQL trong `SkillService.get_skills_by_filter` khi truyền `class_id`: Cần select `COALESCE(skills.skill_type_id, csa.skill_type_id) AS skill_type_id` hoặc trả về đúng `csa.skill_type_id` để model nhận đúng loại kỹ năng.

### Pha 2: Cải tiến UX BuildEditDialog (Frontend)
- Cấu trúc lại `BuildEditDialog` dùng các layout cơ sở hỗ trợ co giãn.
- Thay thế `tk.Listbox` bằng component chọn kỹ năng trực quan hơn (hoặc thêm thanh Search text bên trên listbox).
- Ràng buộc Validation: Ít nhất 1 Attack Skill hoặc 1 Buff Skill phải được chọn trước khi Save.

### Pha 3: Xóa Technical Debt (i18n & Clean UI)
- Thêm các i18n keys còn thiếu (e.g. `lbl_class`, `lbl_author`, `lbl_description`, `err_invalid_class`, `err_empty_build`) vào `lib/i18n/translations.py` (cả EN và VN).
- Cập nhật `BuildEditDialog` để dùng `self.app._t` và `bind_text` cho mọi label và messagebox.

### Pha 4: Hoàn thiện CRUD Lifecycle
- Hoàn thiện nghiệp vụ nút "Apply Build" trong `BuildManagerFrame` (hiện đang là `print(...)`) để map Build IDs này vào Hunt Config và nạp lên tab Auto Scanner/Hunter.
- Cải thiện hiển thị Details: Parse ID thành Tên Kỹ Năng ở phần preview màn hình Manager.

---
*Báo cáo được tạo tự động thông qua quá trình truy vết codebase, database SQLite và luồng thực thi code thực tế.*
