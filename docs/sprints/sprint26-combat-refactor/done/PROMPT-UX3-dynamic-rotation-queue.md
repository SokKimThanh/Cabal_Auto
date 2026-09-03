# Session Prompt UX3: Configured Monster Rotation Queue

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependency:** CB4 (bao gồm CB4B hardening nếu được tách), CB2B và UX3A phải đạt gate trước khi bắt đầu

## Trạng thái Sẵn sàng

CB4 đã hoàn tất. UX3 có thể bắt đầu sau khi chạy nhanh Preflight Gate bên dưới trên branch hiện tại.

UX3 tiêu thụ contract canonical do CB4 sở hữu; không triển khai lại migration,
canonical validator, single writer hoặc atomic persistence.

## Objective

Sau khi CB4 đạt, tái cấu trúc panel Monster Rotation thành danh sách cấu hình rõ ràng, responsive và giàu thông tin DB. Người dùng có thể thêm, xóa và đổi thứ tự trong RAM; thay đổi chỉ được ghi khi nhấn **Áp dụng Tất cả Cài đặt**, qua single-writer config owner của CB4.

Đây là **configured rotation queue**, không phải danh sách target runtime. Panel không tự điều khiển mục tiêu và không nhận/xóa record theo trạng thái quái sống.

## Preflight Gate Bắt Buộc

Trước khi sửa UX3, xác nhận bằng code và test:

1. Config ở schema v3; `monster_rotation` là nguồn canonical duy nhất và normal-Hunt runtime không còn đọc `monster_list`.
2. UI load `monster_rotation` và giữ đủ `monster_id`, `name`, `priority`, `dungeon_id` qua một vòng load -> Apply All -> reload.
3. `HuntRunner`/runtime đọc từng rotation entry theo schema dict, không dùng dict làm key của monster library.
4. Shared canonical validator đã normalize/deduplicate rotation, và UI/runtime không có sanitizer song song.
5. `save_hunt_config()` được gọi qua single-writer owner, atomic, dọn temp file khi lỗi, và chỉ clear dirty state sau success.
6. Test migrator thống nhất một shape duy nhất, gồm migration `monster_list -> monster_rotation`, và pass.

Nếu bất kỳ mục nào fail: báo `BLOCKED_BY_CB4`, dừng UX3 và không thêm adapter song song để che lỗi schema.

## Target Files

- Modify: `ui/tabs/hunt_tab.py`
- Modify: `app_gui.py` cho các callback rotation hiện đang được sở hữu tại đây
- Modify: `ui/controllers/app_state_controller.py` chỉ để giữ round-trip schema canonical nếu CB4 chưa để lại serializer hoàn chỉnh
- Modify: `lib/i18n/translations.py`
- Reference: `dialogs/monster_picker.py` do UX3A tạo; UX3 chỉ mở picker và nhận callback/result.
- Reference only: `lib/features/hunt/hunt_config.py`
- Reference only: `database.py` public APIs
- Reference: `lib/ui_style.py`

Không dùng `lib/system/i18n.py`; translation hiện nằm trong `lib/i18n/translations.py`.

Không sửa `lib/features/monsters/monster_repo.py` để giả lập DB resolver. File này hiện chỉ quản lý fallback `monsters.json` và không có API CB4A.

## Phạm Vi Session

### 1. Layout Responsive

- Giữ panel trong layout responsive hiện tại của `HuntTab`; không ép kích thước `776 x 552`.
- Không thêm `minsize` khiến layout 1366x768 hoặc breakpoint hẹp bị tràn.
- Header gồm selector cho `rotation_mode` và các icon button: Thêm, Lên, Xuống, Xóa. Đây chỉ là thứ tự xử lý rotation (`sequence`/`priority`), không phải selector `target_policy` ba mode của UX3B.
- Nút Thêm mở `MonsterPickerDialog` của UX3A. UX3 nhận `{monster_id, name, dungeon_id}`, kiểm tra duplicate `(monster_id, dungeon_id)`, thêm `priority` rồi refresh panel; không giữ dialog legacy tự đọc `self.monsters`/`monsters.json`.
- Dùng widget cuộn hiện có hoặc `ttk.Treeview` nếu cần nhiều cột. Không tự viết Canvas list trong session này.
- Dùng token thực tế của `UIStyle`: `COLOR_TEXT`, `COLOR_SUBTEXT`, `COLOR_WARNING` và các token button hiện có.
- Không tham chiếu `TEXT_MAIN`, `TEXT_MUTED`, `STATE_WARN`, `BORDER_COLOR` vì chúng chưa tồn tại.

### 2. Contract Dữ Liệu

Persist duy nhất:

```python
{
    "monster_id": int,
    "name": str,
    "priority": int,
    "dungeon_id": str | None,
}
```

- `level` và `hp` chỉ là metadata hiển thị, không persist.
- Schema canonical không có `enabled`; bỏ checkbox/double-click toggle legacy thay vì giữ trạng thái không thể round-trip.
- Sau thêm/xóa/di chuyển, đánh lại `priority` liên tiếp từ 1 theo thứ tự UI.
- `rotation_mode` tiếp tục dùng các giá trị hiện có `sequence` và `priority`; UX3 không tạo, đổi hoặc persist `target_policy`.
- Không đổi nghĩa `priority` thành khoảng cách.

### 3. Metadata DB Và Fallback

Dùng public API hiện có trong `database.py`:

- `get_monster_by_id_api(str(monster_id))` khi ID hợp lệ;
- fallback `find_monster_by_name_api(name, dungeon_id)` khi cần tương thích dữ liệu cũ đã được CB4 migrate.

Format record đã resolve:

```text
[#<id>] <Tên quái> - Lv.<level> | HP: <hp>
```

Format chưa resolve:

```text
[Chưa rõ] <Tên gốc> - Lv.-- | HP: --
```

Không hiển thị HP giả `10000`. Không claim `is_placeholder` dùng chung với CB4A vì API đó chưa tồn tại. Metadata thiếu chỉ ảnh hưởng presentation, không làm mất rotation entry đã persist.

Cache metadata theo `(monster_id, name, dungeon_id)` trong vòng đời panel. Không truy vấn SQLite mỗi lần repaint hoặc select.

### 4. State Và Persistence

- Tiếp tục dùng một danh sách cấu hình trong RAM làm nguồn của panel.
- Thao tác thêm/xóa/di chuyển cập nhật RAM, refresh UI và mark `has_unsaved_changes=True` qua một helper thống nhất.
- Chỉ `on_global_apply()` lấy canonical snapshot, gọi serializer và gọi đúng một lần API của single-writer config owner. Không clear dirty state khi save thất bại.
- Không thêm trailing debounce 300ms hoặc đường ghi file thứ hai.
- Không ghi file trực tiếp từ `HuntTab`, controller của panel, hoặc callback UI.
- Không ghi metadata `level`, `hp`, trạng thái resolve hoặc cache xuống config.

### 5. Ranh Giới Runtime Và Thread

Ngoài phạm vi UX3:

- tự chèn quái do OCR/detection;
- tự xóa quái khi target chết;
- sắp xếp theo khoảng cách;
- cập nhật danh sách 5 FPS;
- điều khiển target tiếp theo.

`HuntOrchestrator` hiện chỉ có callback status/target text/clear UI, chưa có event contract cho các hành vi trên. UX3B bổ sung giao diện ba mode/hai danh sách sau khi CB2D có detection snapshot; CB2C thực thi policy và đồng bộ desired target với target thực tế.

## I18n

Thêm key song ngữ vào `GLOBAL_TRANSLATIONS` theo pattern hiện có:

- `monster_rotation_title`
- `monster_rotation_mode_sequence`
- `monster_rotation_mode_priority`
- `monster_rotation_add`
- `monster_rotation_remove`
- `monster_rotation_unknown`

Nếu hệ thống i18n đã hỗ trợ key có dấu chấm tại thời điểm triển khai, có thể dùng namespace `monster_rotation.*`, nhưng phải có test lookup trước.

## Validation & Testing

### Automated Tests

Thêm `tests/unit/test_monster_rotation_queue.py`:

1. **Canonical round-trip:** load 3 dict -> reorder -> Global Apply -> reload; giữ đúng ID/name/dungeon và priority 1..N.
2. **Không persist metadata:** dữ liệu hiển thị có level/hp nhưng config chỉ có bốn field canonical.
3. **Unknown display:** DB trả `None`; hiển thị `Lv.-- | HP: --`, không crash và không sửa entry persist.
4. **DB lookup cache:** refresh panel nhiều lần chỉ gọi resolver một lần cho mỗi cache key.
5. **Dirty state:** add/remove/move mark unsaved nhưng không gọi writer trước Global Apply; save failure giữ dirty state và không báo success.
6. **Priority normalization:** sau xóa/di chuyển, priority là 1..N theo thứ tự UI.
7. **Rotation-mode boundary:** selector chỉ round-trip `sequence`/`priority`, không mutation `target_policy` hoặc state UX3B.
8. **Picker integration:** nhận result UX3A, thêm đủ bốn field canonical và không leak metadata DB/picker state.
9. **Responsive regression:** panel không thêm minsize cố định làm hỏng layout rộng/hẹp hiện có.

Chạy thêm gate CB4:

```powershell
py -m pytest tests/test_migration.py tests/unit/features/hunt/test_config_migrator.py -q
py -m pytest tests/unit/test_monster_rotation_queue.py -q
py -m pytest tests/ui/tabs/test_hunt_tab_layout.py -q
```

### Manual Check

- 1366x768 ở layout rộng và hẹp hiện có.
- Chuyển `vi`/`en` không mất selection hoặc dữ liệu RAM.
- Add, Move Up/Down, Remove cập nhật dirty indicator.
- Đóng/mở hoặc reload trước Apply không được giả vờ đã persist.
- Apply All rồi reload giữ nguyên rotation canonical.

## Session Boundary Gate

**PASSED khi:**

- Preflight CB4, bao gồm hardening gate hoặc CB4B nếu tách session, đạt toàn bộ.
- Panel responsive, thao tác add/remove/reorder ổn định.
- Chỉ `monster_rotation` canonical được round-trip.
- Không persist metadata runtime.
- Không có auto-save ngoài Global Apply.
- Không có Tkinter update từ background thread.
- Toàn bộ test mục tiêu pass.

**BLOCKED/REVERTED khi:**

- `monster_list` và `monster_rotation` vẫn cùng điều khiển runtime.
- Runtime vẫn đọc rotation dict như ID.
- Session phải tự xây migration, atomic save hoặc event bridge để panel hoạt động.
- Có hai nguồn sự thật, hai đường ghi config, hoặc UX3 sửa `target_policy` vốn thuộc UX3B.
- Layout làm hồi quy breakpoint Hunt hiện tại.

Báo cáo `PASSED`, `BLOCKED_BY_CB4` hoặc `REVERTED` ở phút 25; phút 25-30 chỉ dành cho targeted repair và chạy lại test.
