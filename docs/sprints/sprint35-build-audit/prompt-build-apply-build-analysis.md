# Prompt 07: Build Apply Build Analysis

## Mục tiêu
Audit chức năng Apply Build.

## Phạm vi
- `BuildManagerFrame` (Nút Apply Build)
- Workflow Apply Build

## Root Cause liên quan
(Trích từ báo cáo gốc): Tính năng Apply Build (áp dụng build vào setup hiện tại) dường như chưa được hoàn thiện 100% trong `BuildManagerFrame`, hiện tại chỉ in ra log console (`Apply build clicked...`).

## Công việc cần thực hiện
- Truy vết nút Apply Build.
- Tìm call chain.
- Tìm điểm dừng hiện tại.
- Xác định object cần cập nhật.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Trả lời rõ quy trình hiện tại đang thiếu ở đâu dựa trên luồng:
  `Build -> Hunt Config -> Rotation -> Hunter`

## Commit Message
`docs(build): audit apply build workflow`
