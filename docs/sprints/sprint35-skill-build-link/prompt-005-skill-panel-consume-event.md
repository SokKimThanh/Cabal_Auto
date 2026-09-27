# Prompt 005 - Skill Panel Event Consumption

## 1. Mục tiêu (Objective)
Cập nhật Skill Panel (hoặc Preset Lane Controller) để lắng nghe sự kiện `ApplyBuildToLaneEvent`, xử lý validate class, sau đó cập nhật dữ liệu kỹ năng lên thanh kỹ năng hiện tại trên UI và lưu lại preset đó.

## 2. Phạm vi thay đổi (Scope)
- **Controller/UI:** Đăng ký lắng nghe event từ EventBus tại Controller của SkillPanel.
- **Validation logic:** Kiểm tra dữ liệu class của Build có khớp với nhân vật hiện tại không.
- **Action:** Cập nhật các slot kỹ năng (Attack Combo, Buff) theo dữ liệu của event và gọi hàm lưu hiện tại (Preset/Save Lane).
- **Ngoài phạm vi:** UI Build Manager, DB Build, Event Emission.

## 3. Tiêu chí hoàn thành (Definition of Done - DoD)
- Lane kỹ năng cập nhật hiển thị chính xác các kỹ năng có trong Build vừa apply.
- Dữ liệu Preset hiện hành được lưu lại xuống DB.
- Cảnh báo (Warning) nếu Build apply có class khác với class đang active.

## 4. Các rủi ro tiềm ẩn (Risks)
- Render loop nếu việc update lane trigger lại các sự kiện lưu state liên tục.
- Crash UI do thao tác widget từ thread không phải main thread của GUI (nếu event bus chạy async).

## 5. Kế hoạch Rollback (Rollback Plan)
- Revert commit thay đổi trong `skill_panel_controller.py` hoặc class lắng nghe event.

## 6. Impact Analysis
**Affected modules:**
- Skill panel controller.
- Lane UI update logic.

**Must not affect:**
- Core build logic.
- Dữ liệu class khác.

**Regression checklist:**
- Thao tác kéo thả thủ công kỹ năng vẫn hoạt động bình thường.
- Chuyển tab/nhân vật không bị lỗi trạng thái.

## 7. Acceptance Test
**Scenario 1: Apply Build thành công**
- **Given** Skill Panel đang mở với class A, Event `ApplyBuildToLaneEvent` tới từ class A có 3 kỹ năng
- **When** Controller nhận event
- **Then** 3 kỹ năng được nạp lên Lane, UI render lại và Preset được lưu.

**Scenario 2: Sai Class**
- **Given** Skill Panel đang ở class A, Event apply Build thuộc class B tới
- **When** Controller nhận event
- **Then** Từ chối apply, hiển thị popup cảnh báo lỗi sai class.

## 8. Technical Debt Handling
**Trong batch này phải:**
- Đảm bảo event handler chạy trên MainThread/UIThread nếu có thay đổi giao diện.
- Tái sử dụng (reuse) các hàm populate lane hiện tại, không viết lại code nạp kỹ năng.

**Không được:**
- Xóa các logic lưu Preset cũ.

## 9. Commit Strategy
- **Commit 1:** `feat(ui): add listener for ApplyBuildToLaneEvent in skill panel`
- **Commit 2:** `feat(ui): implement validate and load build skills to lane`
