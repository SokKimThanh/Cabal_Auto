# Session 09 - Nghiệm Thu Responsive Và DPI

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 25-30 phút
- **Ưu tiên:** P0-P2
- **Phụ thuộc:** Session 01 đến Session 08, Session 10 và Session 11 — chỉ chạy sau khi toàn bộ thay đổi layout/style/log/action bar/footer đã merge.
- **Tham chiếu tài liệu gốc:** Đề Xuất Khắc Phục Giao Diện Hunt Hiện Tại (v2), mục 4.6 và toàn bộ mục 7 (tiêu chí nghiệm thu), mục 6 (bước "bổ sung kiểm thử GUI và kiểm tra thủ công trên nhiều DPI")
- **AC liên quan:** AC-1 đến AC-19 và AC-F1 đến AC-F3

## Mục tiêu duy nhất

Chạy nghiệm thu tổng, bổ sung các test tích hợp UI còn thiếu và ghi nhận rõ AC nào đạt hoặc chưa đạt.

## Phạm vi

- test UI liên quan đến Hunt và Bottom Logs
- chỉ sửa production code khi lỗi là hồi quy nhỏ, cục bộ và có thể xác nhận trong timebox
- không refactor trong session nghiệm thu

## Các bước thực hiện

1. Chạy toàn bộ test Bottom Logs và toàn bộ test UI có marker `ui` (không lọc `-k`) để không bỏ sót test của Session 05 (khởi tạo cửa sổ) hay Session 08 (selected state, đặt tên có thể không chứa `hunt`/`bottom_logs`).
2. Xác nhận geometry 1366x768: ngoài việc widget được map và có kích thước lớn hơn 0, đo biên thực tế để chứng minh đáy Skill/Hunt không vượt đỉnh Logs hoặc đáy vùng client.
3. Ở cả trạng thái Logs thu và mở, xác nhận Global Apply và DB Status nằm hoàn toàn trong client area; đáy `main_shell` không chồng lên đỉnh bottom chrome.
4. Kiểm tra thủ công ở 100%, 125% và 150% DPI nếu môi trường cho phép, cho cả hai ngôn ngữ.
5. Kiểm tra cả tiếng Anh và tiếng Việt ở từng mức DPI đã kiểm tra, không chỉ ở 100%.
6. Chạy Black và Flake8 trên các file Python đã thay đổi trong chuỗi session, kể cả `lib/ui_style.py` nếu Session 08 đã sửa file này.
7. Lập bảng kết quả AC-1 đến AC-19 và AC-F1 đến AC-F3.

## Lệnh kiểm thử

```powershell
py -m pytest tests/unit/test_bottom_logs.py -q
py -m pytest tests -m ui -q
py -m black --check app_gui.py ui/tabs/hunt_tab.py lib/system/hunt_logger.py lib/ui_style.py
py -m flake8 app_gui.py ui/tabs/hunt_tab.py lib/system/hunt_logger.py lib/ui_style.py
```

Trước khi chạy, xác nhận không còn test file riêng nào từ Session 01-08 nằm ngoài hai lệnh pytest ở trên (ví dụ test khởi tạo cửa sổ của Session 05 nếu được đặt ở vị trí khác `tests/unit/test_bottom_logs.py` và không có marker `ui`); nếu có, chạy thêm lệnh cho file đó.

Trên Linux headless:

```bash
xvfb-run -a pytest tests/unit/test_bottom_logs.py
xvfb-run -a pytest tests -m ui
```

## Ma trận nghiệm thu tối thiểu

| Kích thước/DPI | Ngôn ngữ | Logs | Kết quả |
| --- | --- | --- | --- |
| 1366x768 / 100% | vi | thu/mở | Chưa chạy |
| 1366x768 / 100% | en | thu/mở | Chưa chạy |
| 1366x768 / 125% | vi | thu | Chưa chạy |
| 1366x768 / 125% | en | thu | Chưa chạy |
| 1366x768 / 150% | vi | thu | Chưa chạy |
| 1366x768 / 150% | en | thu | Chưa chạy |

Nếu timebox không đủ để chạy hết cả sáu dòng, ưu tiên chạy đủ cột `vi` (ngôn ngữ chính) ở cả ba mức DPI trước, sau đó `en` ở 100% và 125% tối thiểu; ghi rõ dòng nào bị bỏ qua và lý do trong báo cáo thay vì để trống không giải thích.

## Điều kiện hoàn tất

- Có kết quả rõ ràng cho AC-1 đến AC-19 và AC-F1 đến AC-F3.
- AC-9 chỉ được coi là đạt khi cả ba dòng DPI (100%, 125%, 150%) trong ma trận đều Pass, không chỉ dòng 100%.
- Test tự động mục tiêu pass hoặc blocker được ghi kèm output cần thiết.
- Không còn lỗi cắt/chồng widget ở cấu hình bắt buộc 1366x768 / 100%.
- Trạng thái Logs thu gọn chỉ đạt khi toàn bộ Skill/Hunt nằm phía trên Logs; ảnh chỉ còn header Logs nhưng mất hàng Skill là Fail.
- Footer chỉ đạt khi Global Apply và DB Status nằm trọn trong vùng client ở cả hai trạng thái Logs; `winfo_ismapped()` riêng lẻ không đủ để kết luận Pass.

## Điểm dừng bắt buộc

Lỗi vượt quá 10 phút sửa phải được ghi thành follow-up riêng; không kéo dài session nghiệm thu để refactor.

## Báo cáo Jules cần để lại

- Lệnh đã chạy và kết quả.
- Diff của các fix hồi quy đã áp dụng trong session này (nếu có).
- Bảng AC đạt/chưa đạt.
- Ma trận DPI/ngôn ngữ đã cập nhật, kèm lý do cho bất kỳ dòng nào bị bỏ qua.
- Follow-up cụ thể cho mọi lỗi còn lại.
