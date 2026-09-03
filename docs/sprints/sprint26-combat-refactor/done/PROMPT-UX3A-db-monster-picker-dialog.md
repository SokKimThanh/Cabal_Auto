# Session Prompt UX3A: DB Monster Picker Dialog

**Timebox:** 20-25 phút  
**Priority:** High  
**Dependency:** CB4 (bao gồm CB4B hardening nếu được tách) và CB2B đã đạt gate

## Objective

Thay dialog legacy **Thêm Quái Vào Luân Chuyển** bằng một DB-backed picker tái sử dụng được. Dialog là UI chọn dữ liệu, chỉ trả payload canonical chưa có priority cho caller; không tự mutation `monster_rotation`, không mark dirty và không ghi config.

UX3 sở hữu việc nhận payload, chống trùng, thêm priority, refresh queue và Apply All. UX3B không tạo picker thứ hai.

## Preflight Gate Bắt Buộc

1. CB4 schema v3 và canonical validator đang hoạt động.
2. `database.py` export `get_all_monsters_api(limit)` và `search_monsters_api(keyword, limit)`; record trả về có `id`, `name`, `level`, `hp`, `dungeonId` hoặc mapping dungeon tương đương.
3. UI chạy ở Main Thread; DB lookup không được thực hiện từ background thread rồi cập nhật Tkinter trực tiếp.
4. Dialog legacy trong `App._on_monster_add_smart()` được xác định là entry point cần thay thế, không để song song hai dialog chọn quái.

Nếu fail, báo `BLOCKED_BY_CB4` hoặc `BLOCKED_BY_DATABASE_API`; không tạo JSON-library fallback để che lỗi DB.

## Target Files

- Create: `dialogs/monster_picker.py`
- Modify: `app_gui.py` chỉ để thay entry point legacy bằng picker mới và nhận callback/result; không thêm persistence tại đây.
- Modify: `lib/i18n/translations.py`
- Create: `tests/unit/dialogs/test_monster_picker.py`
- Reference only: `database.py` public APIs
- Reference: `lib/ui_style.py`

Không sửa `lib/features/monsters/monster_repo.py`; `monsters.json` không phải nguồn của picker. Không sửa `ui/tabs/hunt_tab.py`, serializer, migrator hoặc `HuntOrchestrator` trong UX3A.

## Contract Kết Quả

Expose một dialog/class có API rõ ràng, ví dụ:

```python
class MonsterPickerDialog(tk.Toplevel):
    def __init__(self, parent, lang, on_select): ...

# Callback chỉ nhận copy immutable theo nghĩa caller không được dựa vào state widget.
on_select({
    "monster_id": 101,
    "name": "Slime Xanh",
    "dungeon_id": "dungeon-1",
})
```

- `monster_id` là integer dương từ DB; không trả record thiếu ID.
- `name` là tên DB đã strip.
- `dungeon_id` là `str | None`; map `dungeonId` của DB sang tên canonical này.
- Không trả/persist `priority`, `enabled`, `training_mode`, `level`, `hp`, confidence, template hay state widget.
- Caller có thể hủy dialog; hủy không gọi callback.
- Callback chỉ được gọi đúng một lần cho mỗi thao tác xác nhận thành công.

## UI Và Hành Vi

### 1. Layout

- Giữ title `monster_add_title`; dialog có label hướng dẫn, ô tìm kiếm, Treeview/list có scrollbar và nút xác nhận/hủy.
- Không ép `minsize`; vị trí phải ở trong viewport và không dùng `-topmost` toàn hệ thống.
- Dùng `transient(parent)` và `grab_set()`; mọi đường đóng phải giải phóng grab hoặc destroy dialog.
- Dùng `UIStyle` và i18n; không hard-code chuỗi song ngữ mới trong widget.

### 2. Dữ Liệu Hiển Thị

- Khi mở, load tối đa 100 record qua `get_all_monsters_api(100)`.
- Khi người dùng gõ, debounce Main Thread tối đa một lookup pending và gọi `search_monsters_api(keyword, limit=50)`; query rỗng quay về danh sách ban đầu.
- Row hiển thị tối thiểu: `[#<id>] <name> - Lv.<level> | HP: <hp>` và có thể thêm dungeon khi có.
- DB trả `[]` hiển thị empty state `monster_picker_empty`; không crash, không fallback sang `monsters.json`.
- DB lookup lỗi hiển thị non-modal error state `monster_picker_load_failed`; giữ dialog hoạt động để retry search.
- Cache kết quả theo normalized query trong vòng đời dialog; không truy vấn lại khi query chưa đổi.

### 3. Tương Tác

- Double-click row, Enter trên selection và nút Add cùng gọi một method xác nhận duy nhất.
- Không có selection thì nút Add disabled hoặc method no-op có status; không dùng messagebox gây chặn.
- Escape, Cancel và window close hủy dialog an toàn.
- UX3 sẽ kiểm tra duplicate `(monster_id, dungeon_id)`; UX3A không tự biết queue hay ngăn lựa chọn vì không sở hữu configured state.

## I18n

Thêm `vi/en` vào `GLOBAL_TRANSLATIONS`:

- `monster_picker_title`
- `monster_picker_instruction`
- `monster_picker_search_label`
- `monster_picker_results`
- `monster_picker_empty`
- `monster_picker_load_failed`
- `monster_picker_confirm`
- `monster_picker_cancel`

Giữ các key legacy đang còn consumer cho đến khi repository search xác nhận không còn dùng; không xóa i18n key chỉ vì UX3A thay dialog.

## Automated Tests

Thêm `tests/unit/dialogs/test_monster_picker.py`:

1. Initial load gọi `get_all_monsters_api(100)` và render record DB.
2. Search gọi `search_monsters_api()` với keyword normalized; query giống nhau dùng cache.
3. Row render đúng ID, tên, level, HP; `dungeonId` map sang `dungeon_id` trong result.
4. Confirm qua nút, double-click và Enter gọi cùng confirm method và callback đúng một lần.
5. Callback chỉ nhận ba field contract; không lộ `level`, `hp` hoặc record DB gốc.
6. Empty result và DB exception hiển thị state an toàn, không fallback `monsters.json`.
7. Cancel/Escape/WM close không gọi callback và không để modal grab tồn tại.
8. Không có selection không mutation và không callback.
9. Chuyển `vi/en` hiển thị key đã dịch.

Chạy:

```powershell
py -m pytest tests/unit/dialogs/test_monster_picker.py -q
py -m pytest tests/unit/test_i18n_global_registration.py -q
```

## Manual Check

1. Mở `+` từ Monster Rotation khi `monsters.json` rỗng nhưng DB có dữ liệu; kết quả DB vẫn hiện.
2. Tìm theo một phần tên; kết quả cập nhật và không chớp/freeze UI.
3. Xác nhận row trả về UX3; UX3 xử lý thêm vào queue ở session kế tiếp.
4. Hủy dialog rồi mở Monster Manager/Library Manager; không có modal vô hình chặn click.
5. Popup nằm trong màn hình ở 1366x768 và không làm toàn màn hình chớp sáng.

## Session Boundary Gate

**PASSED khi:**

- Picker chỉ đọc từ public DB APIs và không dùng `monsters.json`.
- Result/callback chỉ chứa ba field canonical selection.
- Confirm/cancel/modal lifecycle ổn định.
- I18n `vi/en` và focused tests pass.
- Không có config write, rotation mutation, runtime target behavior hoặc Tkinter update từ worker.

**BLOCKED/REVERTED khi:**

- DB API chưa đủ để browse/search records.
- Picker tự thêm `priority`, `enabled`, `training_mode` hoặc ghi config.
- Code giữ cả picker legacy JSON và picker DB cùng active.
- Modal grab còn tồn tại sau mọi đường đóng.

Báo cáo `PASSED`, `BLOCKED_BY_CB4`, `BLOCKED_BY_DATABASE_API` hoặc `REVERTED` ở phút 20; phần thời gian còn lại chỉ dành cho targeted repair và chạy lại test.
