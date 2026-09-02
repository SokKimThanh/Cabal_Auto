# Session Prompt UX3: Configured Monster Rotation Queue

**Timebox:** 25-30 phút  
**Priority:** High  
**Dependency:** CB4 và CB2B phải đạt gate trước khi bắt đầu

## Trạng thái đối chiếu mã nguồn

Tại thời điểm review, session này **chưa sẵn sàng để chạy**:

- UI trong `app_gui.py` đang load và thao tác `monster_list` qua `monster_rotation_list`.
- `AppStateController._hunt_from_ui()` lại serialize sang `monster_rotation` với schema `{monster_id, name, priority, dungeon_id}`.
- `ui/windows/auto_hunt.py` vẫn đọc `monster_list`.
- `HuntRunner._hunt_locate_target()` đọc `monster_rotation` nhưng đang lặp từng phần tử như một ID, trong khi schema v2 quy định phần tử là dict.
- `save_hunt_config()` đang ghi trực tiếp, chưa dùng temp file + `os.replace()`.
- Hai nhóm test migrator hiện còn kỳ vọng shape `monster_rotation` khác nhau.
- Không tồn tại `get_target_monster_info()` hoặc `is_placeholder` trong source.
- Không có nguồn khoảng cách quái và không có callback queue cho sự kiện quái mới/quái chết từ `HuntOrchestrator`.

Không được đánh dấu UX3 `PASSED` trước khi CB4 giải quyết các điểm schema/runtime ở trên. UX3 không tự triển khai lại migration hoặc atomic persistence của CB4.

## Objective

Sau khi CB4 đạt, tái cấu trúc panel Monster Rotation thành danh sách cấu hình rõ ràng, responsive và giàu thông tin DB. Người dùng có thể thêm, xóa và đổi thứ tự trong RAM; thay đổi chỉ được ghi khi nhấn **Áp dụng Tất cả Cài đặt**, phù hợp mô hình lưu hiện tại.

Đây là **configured rotation queue**, không phải danh sách target runtime. Panel không tự điều khiển mục tiêu và không nhận/xóa record theo trạng thái quái sống.

## Preflight Gate Bắt Buộc

Trước khi sửa UX3, xác nhận bằng code và test:

1. `monster_rotation` là nguồn canonical duy nhất; runtime không còn đọc `monster_list`.
2. UI load `monster_rotation` và giữ đủ `monster_id`, `name`, `priority`, `dungeon_id` qua một vòng load -> Apply All -> reload.
3. `HuntRunner`/runtime đọc từng rotation entry theo schema dict, không dùng dict làm key của monster library.
4. `save_hunt_config()` đã atomic ở tầng dùng chung nếu CB4 yêu cầu atomic write.
5. Test migrator thống nhất một shape duy nhất và pass.

Nếu bất kỳ mục nào fail: báo `BLOCKED_BY_CB4`, dừng UX3 và không thêm adapter song song để che lỗi schema.

## Target Files

- Modify: `ui/tabs/hunt_tab.py`
- Modify: `app_gui.py` cho các callback rotation hiện đang được sở hữu tại đây
- Modify: `ui/controllers/app_state_controller.py` chỉ để giữ round-trip schema canonical nếu CB4 chưa để lại serializer hoàn chỉnh
- Modify: `lib/i18n/translations.py`
- Reference only: `lib/features/hunt/hunt_config.py`
- Reference only: `database.py` public APIs
- Reference: `lib/ui_style.py`

Không dùng `lib/system/i18n.py`; translation hiện nằm trong `lib/i18n/translations.py`.

Không sửa `lib/features/monsters/monster_repo.py` để giả lập DB resolver. File này hiện chỉ quản lý fallback `monsters.json` và không có API CB4A.

## Phạm Vi Session

### 1. Layout Responsive

- Giữ panel trong layout responsive hiện tại của `HuntTab`; không ép kích thước `776 x 552`.
- Không thêm `minsize` khiến layout 1366x768 hoặc breakpoint hẹp bị tràn.
- Header gồm mode selector và các icon button: Thêm, Lên, Xuống, Xóa.
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
- `rotation_mode` tiếp tục dùng các giá trị hiện có `sequence` và `priority`.
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
- Chỉ `on_global_apply()` gọi serializer và `save_hunt_config()`.
- Không thêm trailing debounce 300ms hoặc đường ghi file thứ hai.
- Không ghi file trực tiếp từ `HuntTab` hoặc controller của panel.
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

1. **Canonical round-trip:** load 3 dict -> reorder -> Global Apply serializer -> reload; giữ đúng ID/name/dungeon và priority 1..N.
2. **Không persist metadata:** dữ liệu hiển thị có level/hp nhưng config chỉ có bốn field canonical.
3. **Unknown display:** DB trả `None`; hiển thị `Lv.-- | HP: --`, không crash và không sửa entry persist.
4. **DB lookup cache:** refresh panel nhiều lần chỉ gọi resolver một lần cho mỗi cache key.
5. **Dirty state:** add/remove/move mark unsaved nhưng không gọi `save_hunt_config()` trước Global Apply.
6. **Priority normalization:** sau xóa/di chuyển, priority là 1..N theo thứ tự UI.
7. **Responsive regression:** panel không thêm minsize cố định làm hỏng layout rộng/hẹp hiện có.

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

- Preflight CB4 đạt toàn bộ.
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
- Có hai nguồn sự thật hoặc hai đường ghi config.
- Layout làm hồi quy breakpoint Hunt hiện tại.

Báo cáo `PASSED`, `BLOCKED_BY_CB4` hoặc `REVERTED` ở phút 25; phút 25-30 chỉ dành cho targeted repair và chạy lại test.
