# Session Prompt R3: Daily Execution And Validation Gate

**Cadence:** Chạy mỗi ngày sau UX3B hoặc bất cứ khi nào tiếp tục một prompt chức năng  
**Timebox:** Tối đa 30 phút cho một prompt chính  
**Priority:** Process/Quality gate  
**Dependency:** Prompt chức năng đang được chọn và các dependency của prompt đó

## Objective

Chuẩn hóa cách thực hiện Sprint 26 theo nhịp hằng ngày: mỗi ngày chỉ chạy một prompt chức năng chính, dành thời gian còn lại cho validation, targeted repair, báo cáo gate và chuẩn bị prompt tiếp theo.

R3 không triển khai thay cho CB2E, CB2C, UX4, CB3, UX5 hoặc DS. R3 kiểm soát phạm vi, bằng chứng và điều kiện chuyển phiên.

## Daily Capacity Rule

### Quy tắc mặc định

- Một ngày chỉ chạy **một prompt chức năng chính**.
- Không gộp hai prompt có thay đổi production, dependency hoặc runtime state trong cùng ngày.
- Không bắt đầu prompt kế tiếp nếu prompt hiện tại chưa có verdict rõ ràng.
- R1/R2 hoặc docs-only có thể chạy riêng trong ngày khác; không dùng chúng để che một feature gate đang fail.

### Ngoại lệ hạn chế

Chỉ chạy prompt thứ hai trong cùng ngày khi tất cả điều kiện sau đúng:

- Prompt thứ hai là docs-only, audit-only hoặc maintenance độc lập.
- Prompt chính đã pass focused tests và manual smoke.
- Không có thay đổi production chưa validate.
- Không chia nhỏ validation của prompt chính để lấy thời gian cho prompt thứ hai.

## 30-Minute Operating Loop

### Phút 00-05: Preflight

1. Xác nhận branch, dirty worktree và prompt chính của ngày.
2. Đọc `00-global-rules.md` và prompt đang chạy.
3. Kiểm tra dependencies đã đạt gate; nếu chưa, báo `BLOCKED_BY_<DEPENDENCY>` và dừng feature work.
4. Chụp baseline focused test hoặc smoke command trước thay đổi nếu cần.

### Phút 05-20: Implementation

1. Chỉ sửa scope và target files của prompt chính.
2. Không kéo task kế tiếp vào để “tiện tay” sửa.
3. Giữ ownership, schema, thread boundary và writer contract hiện có.
4. Nếu phát hiện blocker ngoài scope, ghi lại cho R1/R2 hoặc prompt remediation riêng.

### Phút 20-25: Focused Validation

Ưu tiên theo thứ tự:

1. Test hẹp nhất của behavior vừa sửa.
2. Test module liên quan.
3. Compile/type/lint nếu phù hợp.
4. Startup smoke hoặc manual UI check cho thay đổi giao diện.

Validation phải có command và kết quả thật; không dùng code inspection thay cho test khi test có thể chạy.

### Phút 25-30: Targeted Repair And Gate

- Chỉ sửa lỗi trực tiếp do validation vừa phát hiện.
- Chạy lại đúng focused check sau repair.
- Không bắt đầu feature mới trong 5 phút cuối.
- Cập nhật verdict, files, tests, known gaps và prompt được phép chạy tiếp theo.

## Time Remaining Policy

Thời gian còn lại sau implementation chỉ dùng cho:

- focused tests và integration tests có liên quan;
- startup/manual smoke ở viewport và mode bị ảnh hưởng;
- sửa lỗi trực tiếp, nhỏ và có thể kiểm chứng;
- kiểm tra dirty state, persistence, thread/UI boundary và backward compatibility;
- cập nhật docs/status/manifest;
- chuẩn bị dependency checklist cho ngày kế tiếp.

Không dùng thời gian còn lại để:

- thêm feature mới;
- chạy một prompt phụ thuộc khác;
- refactor diện rộng;
- đổi schema/writer để né test fail;
- đánh dấu `PASSED` khi còn test lỗi, fixture lỗi chưa phân loại hoặc dependency chưa đạt.

## Prompt Selection After UX3B

Dùng thứ tự dependency hiện tại:

1. `CB2E`: background HWND input và fail-closed capability.
2. `CB2C`: target policy, desired target source và attack gate.
3. `UX4.1`: dual-lane skill strip.
4. `UX4.2`: smart routing và migration.
5. `CB6`: combo bar timing trigger.
6. `CB3D`: delivery acknowledgment.
7. `CB3C`: fast-break/timing harmonization.
8. `UX5.1`, sau đó `UX5.2`.
9. `DS1` đến `DS5` sau khi cấu trúc chức năng ổn định.

Không gộp `CB2E + CB2C`, `CB3D + CB3C` hoặc các prompt có cùng runtime ownership trong một ngày.

## Daily Report Contract

Mỗi ngày phải báo cáo:

```text
Date:
Prompt chính:
Dependency preflight: PASS/BLOCKED
Implementation files:
Focused commands:
Validation result:
Manual smoke:
Known gaps:
Verdict: PASSED/PARTIAL/BLOCKED/UNVERIFIED/REVERTED
Next allowed prompt:
```

`PARTIAL` không được coi là dependency đạt. `UNVERIFIED` chỉ dùng khi môi trường không cho phép kiểm tra; phải ghi rõ bằng chứng còn thiếu.

## Daily Boundary Gate

**PASSED khi:**

- Chỉ một prompt chức năng chính được thực hiện trong ngày.
- Dependency được kiểm tra trước implementation.
- Focused validation chạy trước khi chuyển task.
- Lỗi validation được sửa trong cùng scope hoặc ghi thành blocker rõ ràng.
- Có verdict và command evidence.
- Không có thay đổi ngoài scope chưa được phân loại.

**BLOCKED khi:**

- Prompt đang chọn phụ thuộc vào gate chưa đạt.
- Có production test fail nhưng chưa biết là code hay fixture.
- Người thực hiện muốn gộp prompt thứ hai để bỏ qua validation.
- Cần thay đổi ownership/schema/writer ngoài scope để tiếp tục.
- Không thể chứng minh startup/runtime không hồi quy.

Kết thúc mỗi ngày bằng một verdict rõ ràng; không để trạng thái “đã làm gần xong” thay cho gate.
