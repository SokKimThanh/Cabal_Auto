# Prompt Jules Cho Đợt Dọn Nợ Kiến Trúc

Thư mục này chứa các prompt đã được tách nhỏ. Mỗi file tương ứng với một việc vừa đủ cho một session Jules, để tránh nhồi quá nhiều thay đổi vào cùng một lần.

Cách dùng đơn giản:

1. Mở file `00-global-rules.md`.
2. Copy toàn bộ nội dung trong file đó vào Jules trước.
3. Chọn đúng một file công việc, ví dụ `S1A-extract-app-state-controller.md`.
4. Copy nội dung file công việc đó vào cùng session Jules.
5. Chờ Jules làm xong, review diff, chạy test, rồi mới chuyển sang file tiếp theo.

Không nên copy toàn bộ thư mục này vào một session.

## Thứ Tự Chạy Đề Xuất

| Thứ tự | File | Có thể chạy song song? | Cần xong trước |
| --- | --- | --- | --- |
| 0 | `P0-baseline-architecture-and-smoke-inventory.md` | Không | Không có |
| 1 | `S1A-extract-app-state-controller.md` | Không | P0 xong |
| 2 | `S1B-extract-app-window-controller.md` | Cẩn thận | S1A sạch |
| 3 | `S1C-extract-app-lifecycle-controller.md` | Cẩn thận | S1A sạch; nếu đụng cùng vùng với S1B thì chạy sau S1B |
| 4 | `S2A-centralize-hunt-config-migration.md` | Một phần | Sprint 1 đã merge sạch |
| 5 | `S2B-add-hunt-config-validator.md` | Một phần | Sprint 1 đã merge sạch; thống nhất tên hàm/API với S2A |
| 6 | `S2C-extract-hunt-orchestrator.md` | Chưa nên chạy ngay | S2A/S2B đã ổn định API |
| 7 | `S2D-extract-window-selection-service.md` | Chưa nên chạy ngay | S2B xong hoặc API validator đã ổn |
| 8 | `S3A-define-runtime-bridge-controller-interfaces.md` | Không | Sprint 1 đã merge sạch |
| 9 | `S3B-extract-hotkey-controller.md` | Có | S3A xong |
| 10 | `S3C-extract-overlay-controller.md` | Có | S3A xong |
| 11 | `S3D-extract-window-tracker-controller.md` | Có | S3A xong |
| 12 | `S4A-extract-library-manager-controller.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge sạch |
| 13 | `S4B-extract-monster-manager-controller-and-service.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge sạch |
| 14 | `S4C-extract-skill-manager-controller-and-service.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge sạch |
| 15 | `S4D-migrate-quick-monster-editor-into-monster-manager-win.md` | Không | S4C xong (tránh đụng chung vùng modal window với S4C) |
| 16 | `S4E-split-skill-editor-into-skill-manager-win.md` | Không | S4D xong (đụng chung vùng modal window Sprint 4, ưu tiên xong S4D để có mẫu tham khảo) |
| 17 | `S5A-remove-dead-compatibility-shims.md` | Không | Tất cả sprint trước đã merge sạch |
| 18 | `S5B-document-boundaries-and-final-smoke.md` | Không | S5A xong |

## Cách Chạy Song Song An Toàn

Chạy song song nghĩa là mở nhiều session Jules khác nhau, mỗi session chỉ nhận một file prompt riêng.

Nên chạy theo nhóm này:

- Chạy `P0` một mình trước để Jules hiểu hiện trạng và tìm test/smoke check có sẵn.
- Chạy `S1A` một mình vì nó đụng nền tảng state của app.
- Sau `S1A`, có thể chạy `S1B` và `S1C` song song nếu chúng không cùng sửa một vùng trong `app_gui.py`. Nếu cùng đụng `App.__init__` hoặc `on_close`, chạy lần lượt.
- Sau khi Sprint 1 sạch, có thể chạy `S2A` và `S2B` song song, nhưng phải thống nhất tên hàm/API migrator và validator.
- Chạy `S2C` sau khi API config đã ổn. Chạy `S2D` sau `S2B`.
- Chạy `S3A` trước. Sau đó `S3B`, `S3C`, `S3D` có thể chạy song song vì mỗi file xử lý một controller khác nhau.
- `S4A`, `S4B`, `S4C` có thể chạy song song nếu Sprint 1 đã tách lifecycle/modal đủ rõ. Nếu bị conflict ở `app_gui.py`, ưu tiên merge `S4A` trước.
- `S5A` và `S5B` luôn chạy sau cùng, theo thứ tự.

## Cách Review Sau Mỗi Session

Sau khi Jules trả patch, đừng merge ngay. Hãy kiểm tra theo thứ tự:

1. Diff có nằm đúng phạm vi prompt không?
2. Có xóa nhầm code, callback, import, public attribute, hoặc fallback tương thích không?
3. Nếu có xóa code, Jules đã chứng minh code đó không còn caller chưa?
4. Các edge case trong `00-global-rules.md` đã được kiểm tra chưa?
5. Validation command Jules chạy có đúng và đủ hẹp không?
6. Các file dễ conflict như `app_gui.py`, `ui/controllers/app_runtime_bridge.py`, `ui/controllers/__init__.py` có bị đụng bởi session khác không?

Nếu session xóa code nhưng không có bằng chứng rõ ràng, hãy giữ lại đường tương thích cũ và tạo một prompt cleanup nhỏ hơn sau.

## Dấu Hiệu Cần Dừng Lại

Dừng merge và yêu cầu Jules làm lại nhỏ hơn nếu thấy một trong các dấu hiệu này:

- Một session sửa quá nhiều file ngoài danh sách `Files in scope`.
- `app_gui.py` bị nhét thêm logic mới thay vì được làm mỏng đi.
- `app_runtime_bridge.py` bắt đầu chứa logic thật thay vì chỉ forward/delegate.
- Test không chạy hoặc Jules chỉ nói chung chung là “should work”.
- Code fallback cũ bị xóa nhưng không có search reference hoặc validation chứng minh an toàn.
- Patch trộn nhiều việc: vừa lifecycle, vừa hunt, vừa overlay, vừa modal.

Mục tiêu của bộ prompt này là trả nợ kiến trúc bằng nhiều bước nhỏ, dễ review, dễ rollback, và không làm mất hành vi đang chạy ổn.
