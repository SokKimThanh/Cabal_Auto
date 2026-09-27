# Prompt 002 - Update Build Repository & Service

## 1. Mục tiêu (Objective)
Cập nhật Repository và Service xử lý dữ liệu Build để có thể lưu trữ (persist) và tải (load) các thông tin `attack_skill_ids` và `buff_skill_ids` đã được thêm vào Model ở batch trước.

## 2. Phạm vi thay đổi (Scope)
- **Repository:** Cập nhật các câu truy vấn Insert/Update/Select của `BuildRepository` để map và lưu trữ danh sách kỹ năng. Xử lý serialize/deserialize (nếu dùng JSON).
- **Service:** Cập nhật `BuildService` để truyền/nhận đúng cấu trúc dữ liệu kỹ năng từ các lớp cao hơn xuống DB.
- **Ngoài phạm vi:** DB Migration, UI, Event, tích hợp Lane.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- `Build.attack_skill_ids` và `Build.buff_skill_ids` được lưu trữ thành công xuống database qua các hàm Save/Update.
- Tải lại (Load) Build từ database qua Repository trả về đúng danh sách kỹ năng đã lưu.
- Unit Test cho Repository và Service pass hoàn toàn.

## 4. Các rủi ro tiềm ẩn (Risks)
- Serialization lỗi khi lưu trữ danh sách (list) vào CSDL.
- Lỗi NullPointer/Type mismatch khi truy xuất các bản ghi cũ từ repository nếu không parse đúng fallback.

## 5. Kế hoạch Rollback (Rollback Plan)
- Revert các commit chỉnh sửa `BuildRepository` và `BuildService`.

## 6. Impact Analysis
**Affected modules:**
- Build repository
- Build service

**Must not affect:**
- Database schema (đã chốt ở prompt 1).
- Các UI components.
- Preset logic.

**Regression checklist:**
- Save old build (bản ghi không có skill).
- Load old build.
- Xóa build.

## 7. Acceptance Test
**Scenario 1: Lưu dữ liệu kỹ năng mới**
- **Given** Model Build có 5 attack_skills và 2 buff_skills
- **When** Gọi repository/service để Save()
- **Then** Hàm trả về thành công và kiểm tra DB có lưu trữ đúng dữ liệu.

**Scenario 2: Load dữ liệu build đầy đủ**
- **Given** Database có bản ghi Build với đầy đủ kỹ năng
- **When** Gọi repository/service để Load()
- **Then** Object Build trả về có đủ danh sách các kỹ năng tương ứng.

## 8. Technical Debt Handling
**Trong batch này phải:**
- Xóa code duplication liên quan đến Build loading (nếu có).
- Bổ sung test coverage cho các hàm thao tác với `BuildRepository`.

**Không được:**
- Bỏ qua các trường hợp ngoại lệ liên quan đến JSON parsing.
- Thêm TODO, FIXME.

## 9. Commit Strategy
- **Commit 1:** `feat(build): support persist skill assignments in repository`
- **Commit 2:** `feat(build): handle skill mappings in build service`
- **Commit 3:** `test(build): add repository/service coverage for skills`
