# Prompt 004 - Apply Build Event Emission

## 1. Mục tiêu (Objective)
Cài đặt logic cho nút "Apply" trên UI Build Manager, thực hiện phát (emit) một Event chứa thông tin dữ liệu của Build thông qua EventBus để các thành phần khác có thể bắt lấy xử lý.

## 2. Phạm vi thay đổi (Scope)
- **UI Action:** Cập nhật hàm xử lý khi click nút "Apply Build".
- **Event definitions:** Định nghĩa event mới (ví dụ: `ApplyBuildToLaneEvent`).
- **Logic:** Phát (emit) event lên EventBus kèm theo dữ liệu `build_data`.
- **Ngoài phạm vi:** Database logic, logic nhận và vẽ lại UI bên Skill Panel.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- Nhấn Apply Build sẽ phát ra Event đúng cấu trúc.
- Thông báo (nếu có) phản hồi thao tác thành công.
- Tuân thủ nguyên tắc Low Coupling: Không gọi trực tiếp hàm của SkillPanel.

## 4. Các rủi ro tiềm ẩn (Risks)
- Truyền sai tham chiếu dữ liệu gây lỗi (ví dụ: truyền nguyên object Build mà object đó sau đó bị biến đổi).

## 5. Kế hoạch Rollback (Rollback Plan)
- Revert commit xử lý action apply và file định nghĩa Event.

## 6. Impact Analysis
**Affected modules:**
- Build manager frame actions.
- Event definitions/bus.

**Must not affect:**
- Skill panel rendering.
- Build logic.

**Regression checklist:**
- Thao tác UI cũ không bị lock hay block.

## 7. Acceptance Test
**Scenario 1: Kích hoạt Apply Build**
- **Given** User đang ở giao diện xem Build có danh sách kỹ năng
- **When** Click "Apply Build"
- **Then** `ApplyBuildToLaneEvent` được bắn ra EventBus với payload là Build đó.

## 8. Technical Debt Handling
**Trong batch này phải:**
- Đảm bảo Event class mới được khai báo tại file quy chuẩn dùng chung.

**Không được:**
- Pass object UI context vào Event payload.
- Import vòng (circular import) giữa UI Build và UI Lane.

## 9. Commit Strategy
- **Commit 1:** `feat(event): define ApplyBuildToLaneEvent`
- **Commit 2:** `feat(ui): emit apply event from build manager on click`
