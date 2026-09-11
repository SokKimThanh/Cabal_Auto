# Đặc tả tính năng: Chọn Class Chủ động trên Skill Panel (Tab Hunt)

## 1. Vấn đề hiện tại
Trong tab Hunt, phần hiển thị và sắp xếp dữ liệu kỹ năng trên 2 lane (Attack Combo và Buff Lane) đang bị phụ thuộc vào kết quả của tiến trình `scan` (quét màn hình game) để xác định `class_id` của nhân vật.
Điều này dẫn đến các hệ luỵ:
- Ứng dụng rơi vào thế bị động: Người dùng phải chờ hệ thống scan thành công mới có thể cấu hình được kỹ năng.
- Nếu chưa scan được (hoặc game chưa mở), `class_id` mặc định bị ép về `1` (Blader), khiến danh sách dropdown kỹ năng hiển thị sai cho các class khác.
- Lỗi logic khi lưu/load preset vì không xác định được đúng class.

## 2. Mục tiêu (Mục đích)
- Chuyển quyền chủ động chọn class cho người dùng ngay tại giao diện cấu hình kỹ năng (Skill Panel).
- Ngắt sự phụ thuộc cứng vào hệ thống auto-scan, cho phép người dùng chuẩn bị sẵn preset/combo trước cả khi bật game.
- Khi tiến trình `scan` thực sự chạy và phát hiện class, hệ thống có thể đối chiếu hoặc cập nhật lại lựa chọn một cách mượt mà.

## 3. Thiết kế Giao diện (UI)
- **Vị trí**: Thêm một `ttk.Combobox` (hoặc dropdown) trên thanh tiêu đề của `SkillPanel` (gần nút Toggle "All Skills / Class Skills" hoặc phần Indicator Preset).
- **Thành phần**:
  - Nhãn (Label): "Class:"
  - Dropdown: Danh sách các Class lấy từ cơ sở dữ liệu `classes` (ID - Name). Ví dụ: `1 - Blader`, `2 - Wizard`, `3 - Warrior`...
- **Trạng thái**:
  - Giá trị mặc định khi khởi động: Sẽ cố gắng đọc từ cấu hình đã lưu (`hunt_cfg`), hoặc dựa theo `class_id` mặc định (`1`).
  - Khi người dùng thay đổi giá trị trong dropdown, giao diện sẽ kích hoạt sự kiện cập nhật (`_on_class_selected`).

## 4. Thiết kế Logic (Luồng dữ liệu)
### 4.1. Cập nhật `AppStateController`
- Biến `_current_class_id` vẫn đóng vai trò là "source of truth" cho state hiện tại.
- Bổ sung phương thức để thay đổi chủ động: `app_state_controller.set_current_class(class_id: int)`.
- Hàm này sẽ:
  1. Gán lại `self.root._current_class_id = class_id`.
  2. Kích hoạt tự động load default preset của class mới.
  3. Emit sự kiện (event) để yêu cầu UI làm mới danh sách kỹ năng trên 2 lane.

### 4.2. Xử lý trong `SkillPanel`
- **Khởi tạo**: Đọc danh sách classes thông qua `ClassService` và đưa vào Dropdown.
- **Sự kiện onChange**:
  - Gọi `app_state.set_current_class(new_id)`.
  - Tự động gọi lại `_on_toggle_skills()` hoặc logic refresh để Combobox của các kỹ năng (lane 1, lane 2) chỉ hiển thị kỹ năng của class vừa chọn.
  - Cập nhật UI (xóa/ẩn các kỹ năng hiện tại không thuộc class mới nếu đang bị gán cứng trên ô).

### 4.3. Tương tác với tính năng Auto-Scan
- Tính năng `scan` khi trả về dữ liệu class thực tế, thay vì ép ghi đè thẳng, nên thông báo (hoặc cập nhật nhẹ) UI.
- Nếu class scan được **khác** với class người dùng đang chọn thủ công, có thể hiển thị cảnh báo (Warning: Mismatched Class) hoặc chỉ ghi đè nếu người dùng chưa từng chủ động chỉnh sửa class.

## 5. Kế hoạch triển khai (Implementation Plan)
1. Cập nhật `SkillPanel` (`ui/panels/skill_panel.py`) bổ sung Component UI (Label + Combobox) cho việc chọn Class.
2. Viết hàm load danh sách class (`DbClassService.get_all_classes()`) và bind vào Combobox.
3. Tạo phương thức xử lý sự kiện khi thay đổi class trong dropdown để gọi hàm `load_preset_for_class` của `AppStateController`.
4. Viết test case (nếu có thể) cho việc thay đổi class chủ động ảnh hưởng tới combobox kỹ năng của 2 lane.
5. Cập nhật cấu hình lưu trữ (`hunt_cfg`) để ghi nhớ `class_id` cuối cùng người dùng đã chọn để lần sau mở app không bị reset về 1.

## 6. Các rủi ro và điểm yếu cần tránh (Pitfalls & Weaknesses to Avoid)

Để đảm bảo tính năng "Chọn Class Chủ động" hoạt động ổn định và không phá vỡ trải nghiệm người dùng, quá trình triển khai cần tuyệt đối tránh các điểm yếu và xử lý các vấn đề còn thiếu sau:

1. **Rủi ro mất dữ liệu chưa lưu (Unsaved Changes)**
   - **Vấn đề:** Người dùng đang tinh chỉnh combo kỹ năng cho Class A (nhưng chưa lưu), sau đó vô tình chọn sang Class B ở dropdown. Nếu ứng dụng lập tức load preset của Class B, toàn bộ thay đổi của Class A sẽ bị mất trắng.
   - **Cách giải quyết:** Cần kiểm tra cờ "unsaved changes" trước khi thực hiện đổi class. Nếu có thay đổi chưa lưu, phải hiển thị một hộp thoại xác nhận (Prompt) yêu cầu người dùng lưu lại hoặc đồng ý hủy bỏ các thay đổi trước khi chuyển đổi.

2. **Xử lý kỹ năng "mồ côi" trên UI (Orphaned/Mismatched Skills)**
   - **Vấn đề:** Khi đổi class, các ô kỹ năng đang được chọn (đã render trên giao diện) thuộc về class cũ. Việc không dọn dẹp hoặc dọn dẹp sai cách có thể dẫn đến lỗi ngoại lệ (như cố gắng cast skill không hợp lệ) hoặc lỗi hiển thị trên Tkinter.
   - **Cách giải quyết:** Khi chuyển sang class mới, phải làm sạch (clear) toàn bộ các lựa chọn kỹ năng hiện tại trên các lane (hoặc fallback về các kỹ năng mặc định/cơ bản của class mới). Đồng thời, danh sách các dropdown của từng ô kỹ năng (Combobox) phải được nạp lại tức thì chỉ với kỹ năng của class vừa chọn.

3. **Xung đột State với Auto-Scan đang chạy (Concurrency & State Conflict)**
   - **Vấn đề:** Trong quá trình auto-bot (nhân vật đang đánh quái), hệ thống scan liên tục quét màn hình. Nếu hệ thống scan bất ngờ nhận diện ra một class khác với class người dùng đang set thủ công (hoặc ngược lại, người dùng cố đổi class trong lúc bot đang chạy), sẽ gây xung đột luồng xử lý và có thể làm crash bot.
   - **Cách giải quyết:**
     - Khóa (Disable) dropdown chọn class nếu Bot/Auto-hunt đang ở trạng thái chạy (Active).
     - Chỉ cập nhật `class_id` từ hệ thống auto-scan nếu bot chưa chạy, hoặc đưa ra cảnh báo (Soft warning) trên UI thay vì âm thầm ghi đè dữ liệu người dùng đang cấu hình.

4. **Thiếu tiêu chuẩn Quốc tế hóa (i18n) và Styling (UIStyleV2)**
   - **Vấn đề:** Nếu các nhãn (Label như "Class:"), thông báo lỗi, hoặc cảnh báo đổi class bị hardcode bằng string, ứng dụng sẽ lỗi hiển thị khi chuyển đổi ngôn ngữ. Ngoài ra, việc lạm dụng config màu cứng sẽ vi phạm tiêu chuẩn thiết kế.
   - **Cách giải quyết:** Bắt buộc phải khai báo và sử dụng translation keys (ví dụ: `lbl_class_select`, `msg_unsaved_class_change`) theo chuẩn của `lib/i18n`. Sử dụng `UIStyleV2` thay cho các token font/color cũ.

5. **Trải nghiệm giao diện bị giật, nháy (UI Flickering)**
   - **Vấn đề:** Việc gọi sự kiện update làm render lại toàn bộ hàng loạt các widget kỹ năng ở lane 1 và lane 2 cùng lúc có thể khiến màn hình bị giật (flickering).
   - **Cách giải quyết:** Tối ưu luồng render: chỉ xóa và cập nhật `values` của các Combobox thay vì phá hủy (`destroy`) và tạo lại toàn bộ các frame kỹ năng từ đầu (chỉ update state thay vì recreate widget).
