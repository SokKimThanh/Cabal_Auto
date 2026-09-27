# Prompt 006 - Integration Test & Cleanup

## 1. Mục tiêu (Objective)
Thực hiện viết kiểm thử tích hợp (Integration Test) cho luồng dữ liệu từ Build Manager tới Skill Panel. Kiểm tra và dọn dẹp các khoản nợ kỹ thuật (technical debt), tối ưu mã nguồn chưa được giải quyết trong các batch trước.

## 2. Phạm vi thay đổi (Scope)
- **Tests:** Bổ sung/cập nhật Regression Tests và Integration Tests cho module Build và tính năng Apply Build.
- **Cleanup:** Refactoring, xóa code thừa, dọn dẹp comment thừa.
- **Ngoài phạm vi:** Phát triển tính năng mới.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- Coverage cho các tính năng làm ở prompt 001-005 đạt tiêu chuẩn.
- Script `./check_debt.sh` không báo lỗi liên quan đến các module vừa code.
- Chạy Full Test Suite thành công.

## 4. Các rủi ro tiềm ẩn (Risks)
- Refactoring gây vỡ logic đã chạy ổn định ở các batch trước.

## 5. Kế hoạch Rollback (Rollback Plan)
- Revert các commit test hoặc refactor nếu chúng làm hỏng CI.

## 6. Impact Analysis
**Affected modules:**
- Toàn bộ flow liên quan đến Build (Testing only).

**Must not affect:**
- Logic Production.

**Regression checklist:**
- End-to-end full flow: Tạo Build -> Thêm Kỹ năng -> Lưu -> Apply -> Kiểm tra trên Lane -> Load lại Lane.

## 7. Acceptance Test
**Scenario 1: End-to-end test flow**
- **Given** Một headless/mocked test environment
- **When** Mô phỏng luồng tạo build và apply
- **Then** Tất cả assert đều Pass, không có Error logs.

## 8. Technical Debt Handling
**Trong batch này phải:**
- Xóa toàn bộ các TODO, comment nhắc việc phát sinh trong quá trình implement.
- Chuẩn hóa format code, linting.

## 9. Commit Strategy
- **Commit 1:** `test(build): add end-to-end integration test for apply build feature`
- **Commit 2:** `chore(build): refactor code and resolve minor technical debt`
