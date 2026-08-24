# Prompt Jules Cho Đợt Dọn Nợ Kiến Trúc

Thư mục này chứa các prompt đã được tách nhỏ. Mỗi file tương ứng với một việc vừa đủ cho một session Jules, để tránh nhồi quá nhiều thay đổi vào cùng một lần.

Cách dùng đơn giản:

1. Mở file `00-global-rules.md`.
2. Copy toàn bộ nội dung trong file đó vào Jules trước.
3. Chọn đúng một file công việc, ví dụ `S1A-extract-app-state-controller.md`.
4. Copy nội dung file công việc đó vào cùng session Jules.
5. Chờ Jules làm xong, review diff, chạy test, rồi mới chuyển sang file tiếp theo.

Không nên copy toàn bộ thư mục này vào một session.

## Quy Tắc Mới: So Với Code Gốc Trước Khi Tin Code Đã Tách

Khi Jules tách code từ `app_gui.py` sang module mới, không được chỉ nhìn file mới rồi kết luận là ổn. Phải so lại với code gốc hoặc phần code trước khi tách.

Mục tiêu là trả lời 3 câu hỏi đơn giản:

1. Hành vi cũ đang nằm ở đâu?
2. Hành vi đó đã được chuyển sang module mới nào?
3. Có phần nào bị mất, bị thay bằng `pass`, stub, placeholder, hoặc wrapper rỗng không?

Những phần dễ bị mất nhất cần kiểm tra:

- Callback của nút, menu, hotkey, combobox, listbox, bind phím/chuột.
- Thuộc tính public trên `App` mà tab/window khác còn dùng.
- Import bị xóa nhưng vẫn còn nơi gọi.
- Đường xử lý cũ để giữ tương thích với config hoặc dữ liệu legacy.
- Logic migrate config, validate config, cleanup khi đóng app, destroy overlay/hotkey/window.
- Helper method cũ bị chuyển sang tab/window/controller mới.

Nếu Jules không tìm thấy hành vi cũ trong module mới, coi như có nguy cơ mất code. Khi đó phải khôi phục, hoặc dừng lại và báo rõ phần nào cần xử lý bằng prompt nhỏ hơn.

## P0B Là Gì?

`P0B-original-vs-module-lost-code-audit.md` là prompt kiểm tra, không phải prompt sửa code lớn.

Dùng P0B khi:

- Sau một PR tách module lớn.
- Khi nghi có code bị mất so với file gốc.
- Trước khi chạy cleanup hoặc xóa code tương thích cũ.

Nếu P0B phát hiện nhiều nhóm lỗi, không sửa tất cả trong một PR. Hãy chia theo nhóm nhỏ, ví dụ:

- `hunt_config`: sửa trong một PR riêng.
- `window_selection`: sửa trong một PR riêng.
- `destroy/on_close`: để dành cho lifecycle controller hoặc PR riêng.

P0B có thể chạy nhiều lần trong toàn bộ đợt trả nợ kiến trúc.

## Quy Tắc Mới: Chỉ Dùng Cách Mới Nếu Tốt Hơn

Việc tách module không tự động làm code tốt hơn. Cách viết mới chỉ nên được giữ nếu nó đơn giản hơn, rõ hơn, dễ test hơn, hoặc ít gây lỗi hơn cách cũ.

Nếu code mới sau khi tách bị rườm rà hơn, ví dụ có quá nhiều lớp trung gian, nhiều hàm chỉ gọi tiếp nhau, hoặc logic bị lặp ở nhiều file, thì Jules phải cải thiện trong phạm vi prompt hiện tại. Nếu không cải thiện được ngay, Jules phải ghi rõ follow-up nhỏ cần làm.

Nói ngắn gọn: tách module để code dễ hiểu hơn, không phải để tạo thêm vòng lặp khó dò.

## Thứ Tự Chạy Đề Xuất

| Thứ tự | File | Có thể chạy song song? | Cần xong trước |
| --- | --- | --- | --- |
| 0 | `P0-baseline-architecture-and-smoke-inventory.md` | Không | Không có |
| 0.5 | `P0B-original-vs-module-lost-code-audit.md` | Không | Chạy sau PR tách module lớn, khi nghi mất code, hoặc trước cleanup/xóa code tương thích |
| 1 | `S1A-extract-app-state-controller.md` | Không | P0 xong |
| 2 | `S1B-extract-app-window-controller.md` | Cẩn thận | S1A đã xong, test pass, diff đã review |
| 3 | `S1C-extract-app-lifecycle-controller.md` | Cẩn thận | S1A đã xong, test pass, diff đã review; nếu đụng cùng vùng với S1B thì chạy sau S1B |
| 4 | `S2A-centralize-hunt-config-migration.md` | Một phần | Sprint 1 đã merge xong, không còn conflict/lỗi test |
| 5 | `S2B-add-hunt-config-validator.md` | Một phần | Sprint 1 đã merge xong, không còn conflict/lỗi test; thống nhất tên hàm/API với S2A |
| 6 | `S2C-extract-hunt-orchestrator.md` | Chưa nên chạy ngay | S2A/S2B đã ổn định API |
| 7 | `S2D-extract-window-selection-service.md` | Chưa nên chạy ngay | S2B xong hoặc API validator đã ổn |
| 8 | `S3A-define-runtime-bridge-controller-interfaces.md` | Không | Sprint 1 đã merge xong, không còn conflict/lỗi test |
| 9 | `S3B-extract-hotkey-controller.md` | Có | S3A xong |
| 10 | `S3C-extract-overlay-controller.md` | Có | S3A xong |
| 11 | `S3D-extract-window-tracker-controller.md` | Có | S3A xong |
| 12 | `S4A-extract-library-manager-controller.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge xong, không còn conflict/lỗi test |
| 13 | `S4B-extract-monster-manager-controller-and-service.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge xong, không còn conflict/lỗi test |
| 14 | `S4C-extract-skill-manager-controller-and-service.md` | Có, nhưng cần review kỹ | Sprint 1 đã merge xong, không còn conflict/lỗi test |
| 15 | `S5A-remove-dead-compatibility-shims.md` | Không | Tất cả sprint trước đã merge xong, không còn conflict/lỗi test |
| 16 | `S5B-document-boundaries-and-final-smoke.md` | Không | S5A xong |

## Cách Chạy Song Song An Toàn

Chạy song song nghĩa là mở nhiều session Jules khác nhau, mỗi session chỉ nhận một file prompt riêng.

Nên chạy theo nhóm này:

- Chạy `P0` một mình trước để Jules hiểu hiện trạng và tìm test/smoke check có sẵn.
- Chạy `P0B` sau mỗi đợt tách module lớn, hoặc ngay khi nghi có code bị mất so với file gốc.
- Chạy `S1A` một mình vì nó đụng nền tảng state của app.
- Sau `S1A`, có thể chạy `S1B` và `S1C` song song nếu chúng không cùng sửa một vùng trong `app_gui.py`. Nếu cùng đụng `App.__init__` hoặc `on_close`, chạy lần lượt.
- Sau khi Sprint 1 sạch, có thể chạy `S2A` và `S2B` song song, nhưng phải thống nhất tên hàm/API migrator và validator.
- Chạy `S2C` sau khi API config đã ổn. Chạy `S2D` sau `S2B`.
- Nếu sau Sprint 2 thấy hàm cũ trong `app_gui.py` biến mất hoặc chỉ còn `pass`, chạy lại `P0B` trước khi tiếp tục.
- Chạy `S3A` trước. Sau đó `S3B`, `S3C`, `S3D` có thể chạy song song vì mỗi file xử lý một controller khác nhau.
- `S4A`, `S4B`, `S4C` có thể chạy song song nếu Sprint 1 đã tách lifecycle/modal đủ rõ. Nếu bị conflict ở `app_gui.py`, ưu tiên merge `S4A` trước.
- `S5A` và `S5B` luôn chạy sau cùng, theo thứ tự.
- Trước `S5A`, nên chạy `P0B` một lần nữa để chắc không cleanup nhầm code còn cần dùng.

## Cách Review Sau Mỗi Session

Sau khi Jules trả patch, đừng merge ngay. Hãy kiểm tra theo thứ tự:

1. Diff có nằm đúng phạm vi prompt không?
2. Có xóa nhầm code, callback, import, public attribute, hoặc fallback tương thích không?
3. Nếu có xóa code, Jules đã chứng minh code đó không còn caller chưa?
4. Jules đã so code gốc với module mới chưa?
5. Có hành vi cũ nào bị thay bằng `pass`, stub, placeholder, hoặc wrapper rỗng không?
6. Cách viết mới có đơn giản hơn, rõ hơn, dễ test hơn, hoặc ít gây lỗi hơn không?
7. Các edge case trong `00-global-rules.md` đã được kiểm tra chưa?
8. Validation command Jules chạy có đúng và đủ hẹp không?
9. Các file dễ conflict như `app_gui.py`, `ui/controllers/app_runtime_bridge.py`, `ui/controllers/__init__.py` có bị đụng bởi session khác không?

Nếu session xóa code nhưng không có bằng chứng rõ ràng, hãy giữ lại đường tương thích cũ và tạo một prompt cleanup nhỏ hơn sau.

## Dấu Hiệu Cần Dừng Lại

Dừng merge và yêu cầu Jules làm lại nhỏ hơn nếu thấy một trong các dấu hiệu này:

- Một session sửa quá nhiều file ngoài danh sách `Files in scope`.
- `app_gui.py` bị nhét thêm logic mới thay vì được làm mỏng đi.
- `app_runtime_bridge.py` bắt đầu chứa logic thật thay vì chỉ forward/delegate.
- Test không chạy hoặc Jules chỉ nói chung chung là “should work”.
- Code fallback cũ bị xóa nhưng không có search reference hoặc validation chứng minh an toàn.
- Method cũ có logic thật nhưng bản mới chỉ còn `pass`, stub, placeholder, hoặc gọi vòng qua nhiều lớp mà không thấy logic thật ở đâu.
- Module mới phức tạp hơn code cũ nhưng không tăng khả năng test, không giảm trùng lặp, và không gom logic về đúng chủ sở hữu.
- Patch trộn nhiều việc: vừa lifecycle, vừa hunt, vừa overlay, vừa modal.

Mục tiêu của bộ prompt này là trả nợ kiến trúc bằng nhiều bước nhỏ, dễ review, dễ rollback, và không làm mất hành vi đang chạy ổn.
