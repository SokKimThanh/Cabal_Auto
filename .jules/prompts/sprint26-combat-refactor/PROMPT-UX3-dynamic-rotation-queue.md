# Session Prompt UX3: Implement Dynamic Monster Rotation Queue Panel (Zone B Left)

Timebox: 25–30 minutes.
Priority: High – Modernizes monster list into an interactive, high-performance priority queue.

---

## Objective
Tái cấu trúc Panel 1 bên trái của Vùng B (kích thước 776 x 552 px) thành bảng danh sách Luân Chuyển Quái dạng Hàng đợi động (Dynamic Queue). Tích hợp cơ chế phân biệt trực quan quái thật/fallback, hiển thị khoảng cách thời gian thực (rate-limited), đồng bộ an toàn luồng với `hunt_config.json`, hỗ trợ DPI 100% – 200% và song ngữ i18n đầy đủ.

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (Panel Monster Rotation)
- Modify: `lib/features/monsters/monster_repo.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Reference: `lib/ui_style.py`, `lib/system/i18n.py`

---

## Implementation Details

### 0. Phạm vi dữ liệu: persist vs runtime (đối chiếu schema CB4)
- Schema `monster_rotation` đã chốt ở CB4 chỉ gồm `{monster_id, name, priority, dungeon_id}` — đây là phần **duy nhất** được ghi xuống `hunt_config.json`.
- `level`, `HP`, và khoảng cách (`d: <Range>m`) hiển thị trên mỗi dòng là **dữ liệu tra cứu/tính toán thời gian thực**, lấy qua `get_target_monster_info()` (CB4A) và module ước lượng khoảng cách — **không** được ghi vào `hunt_config.json`. Debounced save (mục 3) chỉ serialize danh sách theo đúng schema CB4 (id/tên/priority/dungeon_id theo thứ tự hiện tại trên UI), không kèm các trường runtime này.
- Nguồn dữ liệu khoảng cách `d: <Range>m` **phải được xác định cụ thể trước khi code**: nếu chưa có module ước lượng khoảng cách thực (từ minimap hoặc toạ độ world), phiên này chỉ nên hiển thị khoảng cách ở dạng **placeholder rõ ràng** (ví dụ ẩn cột này hoặc hiển thị `d: --`) cho tới khi có nguồn dữ liệu thật, thay vì bịa số liệu trông như thật. Nếu đã có nguồn (từ một session khác chưa liệt kê ở đây), ghi rõ tên hàm/module cung cấp giá trị này trong Target Files.

### 1. Bố Cục Panel & DPI Scaling Guard (776 x 552 px)
- Container: `tk.Frame` nằm ở cột 0 của Vùng B với `sticky="nsew"`, `minwidth=360px`.
- Header Bar:
  * Dropdown chọn chế độ: `Sequence` (Tuần tự — theo đúng field `priority` tĩnh đã lưu) / `Priority (Khoảng cách)` (sắp xếp lại **chỉ trên hiển thị** theo khoảng cách gần nhất tại thời điểm hiện tại, không ghi đè field `priority` tĩnh trong config trừ khi người dùng chủ động kéo-thả sắp xếp lại thủ công).
  * Bộ công cụ thao tác: Nút thêm quái `[+]`, Nút đẩy lên `[▲]`, Nút đẩy xuống `[▼]`, Nút gỡ `[Xóa]`.
- Bảng danh sách cuộn độc lập:
  * Tùy biến Listbox/Canvas phẳng với viền 1px `UIStyle.BORDER_COLOR`.
  * Hỗ trợ tự động scale padding và font chữ khi Windows DPI đạt 150%, 175%, 200%.

### 2. Định Dạng Dòng Hiển Thị & Phân Biệt Record
- **Dữ liệu chuẩn từ DB:**
  * Format: `☑ [#<id>] <Tên Quái> - Lv.<Level> | HP: <Max_HP> [d: <Range>m hoặc "--" nếu chưa có nguồn]`
  * Màu sắc: Text chính `UIStyle.TEXT_MAIN`, Badge ID màu xanh dương/cyan.
- **Dữ liệu Fallback / Chưa nhận diện:**
  * Format: `⚠ [#0 - Chưa rõ] <Tên Gốc> - Lv.N/A | HP: 10000`
  * Dùng lại cờ `is_placeholder` từ `get_target_monster_info()` (CB4A) để xác định một record có phải fallback hay không — không tự viết logic phát hiện fallback riêng (VD: kiểm tra `id == 0`) ở đây, tránh hai nơi có hai cách định nghĩa "fallback" khác nhau.
  * Màu sắc: Badge màu cam `UIStyle.STATE_WARN`, Text phụ màu xám mờ `UIStyle.TEXT_MUTED`.

### 3. State Management & Thread-Safe Config Sync
- Tạo lớp `MonsterQueueController`:
  * Lưu trữ danh sách mục tiêu hiện tại trong RAM.
  * Khi người dùng thêm/xóa/đổi thứ tự trên UI: cập nhật ngay danh sách hiển thị và lên lịch ghi đè xuống `hunt_config.json` bằng **trailing debounce 300ms** — mỗi thao tác mới sẽ reset lại bộ đếm thời gian, chỉ thực sự ghi file 300ms sau thao tác **cuối cùng** trong chuỗi thao tác liên tiếp (không phải ghi theo chu kỳ cố định).
  * Ghi file an toàn với luồng đọc song song: viết vào file tạm (VD: `hunt_config.json.tmp`) rồi `os.replace()` sang `hunt_config.json` (atomic rename), để Hunt Thread (đang đọc config đồng thời) không bao giờ đọc phải file đang ghi dở.
- Cập nhật từ luồng Săn (Hunt Thread):
  * Khi quét thấy quái mới: tự động chèn vào hàng đợi hiển thị (không phải hàng đợi persist — xem mục 0) và tính khoảng cách nếu có nguồn (Cập nhật UI tối đa 5 FPS / mỗi 200ms). Việc cập nhật hiển thị 200ms này **không** kích hoạt debounced save 300ms ở trên, vì đây là dữ liệu runtime, không phải thay đổi cấu hình của người dùng.
  * Khi quái chết: xóa ngay lập tức khỏi UI qua `schedule_ui_task()`. Panel chỉ **phản ánh** mục tiêu tiếp theo mà `HuntOrchestrator` đã tự quyết định chọn (theo CB2/CB3) — panel không tự gửi lệnh đổi mục tiêu hay điều khiển hành vi săn; đây là điểm quan trọng để tránh lặp lại vấn đề "hai nguồn sự thật cùng điều khiển một hành vi" đã gặp ở CB3C.

### 4. Đa Ngôn Ngữ (i18n)
- Đăng ký đầy đủ key dịch song ngữ (`vi`/`en`) trong namespace `monster_rotation`:
  * `monster_rotation.title`, `monster_rotation.mode_sequence`, `monster_rotation.mode_priority`, `monster_rotation.add_btn`, `monster_rotation.remove_btn`, `monster_rotation.unknown_badge`.

---

## Validation & Testing

### 1. Automated Tests (`tests/unit/test_monster_rotation_queue.py`)
- **Test Debounced JSON Sync:** Thực hiện liên tiếp 5 thao tác đổi vị trí và xóa quái trong 100ms → Assert file `hunt_config.json` chỉ được ghi đúng 1 lần, 300ms sau thao tác cuối cùng (không phải 300ms sau thao tác đầu tiên), và lưu đúng mảng `monster_rotation` theo schema CB4 (không kèm `level`/`hp`/`distance`).
- **Test Dynamic Death Queue:** Khởi tạo hàng đợi gồm 3 quái → Giả lập tín hiệu báo quái chết liên tiếp → Assert UI gỡ bỏ chính xác từng dòng mà không bị lỗi `IndexError` hay vỡ Listbox.
- **Test Fallback Record Display:** Nạp record khuyết thiếu `{"name": "Unknown Mob"}` → Assert danh sách hiển thị đúng badge `[#0 - Chưa rõ]` và cấp độ `Lv.N/A`, dựa trên cờ `is_placeholder` trả về từ `get_target_monster_info()`.
- (Added) **Test Priority Mode Không Ghi Đè Config:** Chọn chế độ `Priority (Khoảng cách)`, để hàng đợi tự sắp xếp lại theo khoảng cách runtime mà người dùng không thao tác thủ công → Assert `hunt_config.json` **không** bị ghi lại với thứ tự mới (field `priority` tĩnh giữ nguyên), vì đây chỉ là sắp xếp hiển thị.
- (Added) **Test Concurrent Read/Write Safety:** Giả lập Hunt Thread liên tục đọc `hunt_config.json` trong khi UI thread đang trigger debounced save nhiều lần → Assert không có lần đọc nào nhận về JSON không hợp lệ/nội dung dở dang (verify qua atomic rename).

### 2. Visual & DPI Check
- Kiểm tra danh sách hiển thị sắc nét, không bị mất icon/chữ ở các mức DPI: 100%, 125%, 150%, 175%, 200%.
- Kiểm tra chuyển đổi ngôn ngữ `vi` <-> `en` làm mới text toàn bộ panel ngay lập tức.

---

## Session Boundary Gate
- **PASSED nếu:**
  * Panel hiển thị chuẩn kích thước, thanh cuộn hoạt động mượt mà, danh sách cập nhật động theo thời gian thực.
  * Phân biệt rõ ràng quái thật và quái fallback (dùng chung cờ `is_placeholder` với CB4A).
  * `hunt_config.json` chỉ lưu đúng phần dữ liệu tĩnh theo schema CB4, không lẫn dữ liệu runtime.
  * Ghi file dùng atomic rename, không có race với Hunt Thread.
  * Vượt qua toàn bộ automated tests đồng bộ file JSON.
- **REVERTED nếu:**
  * Lỗi văng `IndexError` khi quái chết nhanh hoặc làm hỏng cấu trúc `hunt_config.json`.
  * Chế độ "Priority (Khoảng cách)" vô tình ghi đè field `priority` tĩnh khi không có thao tác thủ công.
  * Báo cáo kết quả PASSED/REVERTED ở phút thứ 25.