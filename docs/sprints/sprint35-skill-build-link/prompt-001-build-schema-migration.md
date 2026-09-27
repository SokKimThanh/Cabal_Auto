# Prompt 001 - Migrate Build Schema

## 1. Mục tiêu (Objective)
Cập nhật thiết kế CSDL và thực hiện migrate schema cho bảng Build để lưu trữ danh sách các kỹ năng (`attack_skill_ids` và `buff_skill_ids`). Chỉ tập trung vào thay đổi Database Schema và Data Model, không làm phần Service, UI, hay Event.

## 2. Phạm vi thay đổi (Scope)
- **Cơ sở dữ liệu:** Khảo sát schema hiện tại và viết script/migration thêm các trường `attack_skill_ids` và `buff_skill_ids`.
- **Model:** Cập nhật các entity/model định nghĩa cấu trúc Build trong code để mapping với các cột mới.
- **Ngoài phạm vi:** UI, Event, Service, Repository, tính năng Apply Build.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- Migration chạy thành công.
- Các build cũ (legacy data) vẫn được parse/load lên thành model mà không bị crash.
- Các Unit test liên quan đến Build Model chạy pass hoàn toàn.

## 4. Các rủi ro tiềm ẩn (Risks)
- Migration lỗi nếu các trường mới không có default hợp lệ khi gặp các bản ghi cũ (khuyến nghị dùng chuỗi rỗng `""`, `[]` hoặc `NULL`).

## 5. Kế hoạch Rollback (Rollback Plan)
- Execute down migration (chạy script đảo ngược schema).
- Hoặc Revert commit có chứa migration.

## 6. Impact Analysis
**Affected modules:**
- DB Migration Scripts
- Build model definitions

**Must not affect:**
- Preset storage
- Các service/repository hiện hành
- Hunt workflow hoặc bất kỳ UI nào

**Regression checklist:**
- Load các build cũ (dữ liệu đang có) không văng exception.

## 7. Acceptance Test
**Scenario 1: Kiểm tra cấu trúc CSDL**
- **Given** Migration đã chạy
- **When** Inspect bảng Build (qua sqlite/db client)
- **Then** Các cột `attack_skill_ids` và `buff_skill_ids` được tạo đúng kiểu dữ liệu.

**Scenario 2: Kiểm tra tương thích dữ liệu cũ**
- **Given** Một Build cũ chưa có dữ liệu kỹ năng
- **When** Parse dòng dữ liệu từ DB thành Model object
- **Then** Model tạo thành công với giá trị `attack_skill_ids` và `buff_skill_ids` là mảng rỗng (hoặc null an toàn).

## 8. Technical Debt Handling
**Trong batch này phải:**
- Đảm bảo typing cho các thuộc tính mới trong Build model được định nghĩa rõ ràng (ví dụ: `List[int]` hoặc `List[str]`).
- Xóa code parsing legacy không còn dùng trong Model (nếu có).

**Không được:**
- Thêm TODO, FIXME.
- Để lại workaround.
- Gộp quá nhiều thay đổi không liên quan.

## 9. Commit Strategy
- **Commit 1:** `feat(build): add supported skill fields to model`
- **Commit 2:** `feat(db): create migration script for build schema`
- **Commit 3:** `test(build): add tests for parsing old and new build models`
