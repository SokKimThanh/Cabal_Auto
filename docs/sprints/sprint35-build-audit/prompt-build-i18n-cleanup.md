# Prompt 05: Build i18n Cleanup

## Mục tiêu
Dọn dẹp i18n Build module.

## Phạm vi
- `BuildEditDialog`
- `BuildManagerFrame`
- Dữ liệu ngôn ngữ (Translations)

## Root Cause liên quan
(Trích từ báo cáo gốc): Trong `BuildEditDialog`, rất nhiều chuỗi cứng (hardcoded text) như: `"Class (*):"`, `"Author:"`, `"Description:"`, `"Upvotes:"`, `"Lỗi"`, `"Vui lòng chọn Class hợp lệ."`. Không sử dụng `app.bind_text(...)` hoặc `self.app._t(...)` để hỗ trợ chuyển đổi ngôn ngữ runtime.

## Công việc cần thực hiện
- Tìm hardcoded text.
- Tìm missing key.
- Tìm unused key.
- Đề xuất key mới.
- Áp dụng `self.app._t(...)` và `bind_text(...)`.

## Tiêu chí hoàn thành (Tiêu chí pass)
- Toàn bộ text cứng trong module Build được thay thế bằng hệ thống i18n.
- Chuyển đổi ngôn ngữ hoạt động bình thường.

## Commit Message
`refactor(build): complete i18n integration`
