# Session 11 - Bảo Đảm Footer Luôn Nằm Trong Cửa Sổ

> **Kết quả đối chiếu code:** Footer không nằm trong container Logs.
> `shell_zone_c2` là con của `main_shell`, còn Global Apply và DB Status là các
> sibling được pack trực tiếp vào root `App`. `_toggle_bottom_logs()` chỉ ẩn/hiện
> `logs_content_frame`. Không triển khai theo giả thuyết "collapse Logs ẩn cả
> footer" vì giả thuyết đó sai với code hiện tại.

## Thông tin session

- **Người xử lý:** Jules
- **Timebox:** 20-25 phút
- **Ưu tiên:** P0
- **Phụ thuộc:** Session 04 và Session 07 đã merge
- **Tương thích:** Session 10 có thể chạy trước hoặc sau; không được đưa Scan trở lại footer
- **AC liên quan:** AC-F1, AC-F2, AC-F3

## Cây widget đã xác nhận

```text
App (root)
├── main_shell                         pack(fill="both", expand=True)
│   └── shell_zone_c2 (Logs)           grid row 2
│       ├── logs_header_frame
│       └── logs_content_frame
├── apply_frame (Global Apply)         pack(side="bottom")
│   ├── unsaved_indicator_label
│   └── global_apply_btn
└── _db_status_bar                     pack(side="bottom")
```

Trước Session 10, `btn_manual_scan` cũng nằm trong `apply_frame`. Sau Session 10,
Scan phải nằm trên action bar và không còn là điều kiện của footer.

## Lỗi cần tái hiện

Ở 1366x768, khi thu/mở Logs:

- Global Apply hoặc DB Status có thể vẫn mapped nhưng bị cắt, nằm sát/vượt đáy
  client hoặc biến mất khỏi phần nhìn thấy.
- `main_shell` có các row tối thiểu, trong khi hai footer root-level cũng yêu cầu
  chiều cao riêng; tổng requested height có thể vượt chiều cao client.
- `main_shell` được pack trước các widget `side="bottom"`; cần kiểm tra cách root
  phân chia cavity thay vì suy luận từ `winfo_ismapped()`.

## Mục tiêu duy nhất

Đảm bảo Global Apply và DB Status luôn được cấp vùng hình học nằm hoàn toàn trong
client area của root, không bị `main_shell` hoặc thay đổi chiều cao Logs đẩy ra
ngoài cửa sổ.

## File trong phạm vi

- `app_gui.py`
- `tests/unit/test_bottom_logs.py`
- Có thể thêm test UI geometry riêng nếu fixture hiện tại không phù hợp.

Không đổi callback Apply, nội dung status, nghiệp vụ Scan hoặc bố cục Hunt. Không
đưa footer vào `main_shell` hoặc `shell_zone_c2`.

## Giả thuyết cục bộ

Footer đã độc lập về ownership nhưng chưa được bảo vệ về geometry. Root đang trộn
`main_shell` mở rộng với các sibling `pack(side="bottom")`, trong khi tổng minsize
có thể lớn hơn client height. Root cần dành chỗ cho bottom chrome trước, sau đó
chỉ cấp phần chiều cao còn lại cho `main_shell`.

## Các bước thực hiện

1. Trước khi sửa, ghi số đo sau `update_idletasks()` ở trạng thái Logs thu và mở:
   - root: `winfo_rooty()`, `winfo_height()`;
   - `main_shell`, Global Apply frame và `_db_status_bar`: `winfo_rooty()`,
     `winfo_height()`, `winfo_reqheight()`.
2. Viết test tái hiện ở geometry 1366x768, không mock `winfo_height()`.
3. Lưu Apply frame thành thuộc tính ổn định như `self.global_apply_frame` để test
   và lifecycle tham chiếu đúng widget.
4. Tạo bottom chrome root-level rõ ràng hoặc chuyển root sang layout có content
   row `weight=1` và footer row `weight=0`. Footer vẫn phải ở ngoài Logs.
5. Root phải dành chỗ cho bottom chrome trước; `main_shell` chỉ nhận phần còn lại.
   Không sửa bằng cách tăng geometry vượt màn hình 1366x768.
6. Giữ `_toggle_bottom_logs()` chỉ tác động `logs_content_frame` và row Logs.
7. Nếu Session 10 đã chạy, không đưa `btn_manual_scan` trở lại footer.
8. Toggle Logs ít nhất hai chu kỳ và xác nhận footer không bị tạo lại.

## Kiểm thử bắt buộc

```powershell
py -m pytest tests/unit/test_bottom_logs.py -q
py -m pytest tests -m ui -k "footer or bottom_logs" -q
```

Nếu thêm test file riêng cho footer, chạy kèm file đó và nêu rõ trong báo cáo.

## Kiểm tra thủ công nhanh

1. Chạy `py .\app_gui.py` ở 1366x768.
2. Ghi nhận đáy root và đáy DB Status; DB Status phải nằm trọn trong cửa sổ.
3. Thu Logs, xác nhận Global Apply và DB Status vẫn nằm trọn trong client area.
4. Mở Logs, xác nhận footer không bị đẩy xuống, cắt hoặc mất.
5. Lặp lại chu kỳ và nhấn thử "Áp dụng Tất cả Cài đặt".
6. Xác nhận Scan nằm đúng nơi theo trạng thái Session 10.

## Tiêu chí nghiệm thu

- **AC-F1:** Global Apply frame và DB Status đều mapped khi Logs thu và mở.
- **AC-F2:** Với mỗi footer widget:
  `widget.winfo_rooty() >= root.winfo_rooty()` và
  `widget.winfo_rooty() + widget.winfo_height() <= root.winfo_rooty() + root.winfo_height()`.
- **AC-F3:** Đáy `main_shell` không vượt đỉnh bottom chrome sau ít nhất hai chu kỳ
  toggle Logs.
- Nút Apply giữ callback cũ và không bị tạo lại khi toggle.
- AC-7, AC-8, AC-18 và AC-19 không hồi quy.
- Không tăng minimum window height vượt vùng làm việc của màn hình 768px.

## Điểm dừng bắt buộc

Không thiết kế lại footer, không thay đổi auto-save và không sửa nghiệp vụ
Scan/Apply. Nếu số đo chứng minh footer đã nằm hoàn toàn trong client ở cả hai
trạng thái, không refactor theo giả thuyết; ghi số đo và điều tra geometry/nhánh
tạo ra ảnh lỗi.

## Báo cáo Jules cần để lại

- Cây widget và chiến lược pack/grid trước/sau.
- Số đo biên root, `main_shell` và footer khi Logs thu/mở.
- Diff production code và test.
- Kết quả test tái hiện lỗi trước và sau khi sửa.
- Ảnh chụp footer ở trạng thái Logs thu gọn, trước và sau khi sửa.
- Trạng thái AC-F1, AC-F2, AC-F3, AC-7, AC-8, AC-18 và AC-19.
