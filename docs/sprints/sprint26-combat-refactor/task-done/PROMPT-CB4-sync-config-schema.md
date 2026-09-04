# Session Prompt CB4: Synchronize Skill & Monster Config Schema

Timebox: 25-30 minutes.

## Post-PR #221 Review Status

**Verdict: PARTIAL PASS - TARGETED CB4 RERUN REQUIRED.**

PR #221 đã hoàn tất một phần quan trọng:

- `app_gui.py` load `monster_rotation` thay cho `monster_list` ở panel UX3;
- `HuntRunner` đã đọc rotation entry dạng dict thay vì dùng cả dict làm ID;
- `save_hunt_config()` đã chuyển sang temp file + `os.replace()`;
- 22 test migration chạy pass trên `origin/main`.

Không chạy lại mù toàn bộ implementation đã đúng. Chạy targeted follow-up cho
các blocker sau trước UX3B, CB2D, CB2C và CB3D:

1. Migrator hiện chỉ migrate legacy `monsters`, trong khi dữ liệu thật đang dùng
   key `monster_list`. Phải migrate `monster_list -> monster_rotation` không mất
   ID/name/priority và xóa hoặc cô lập key legacy sau khi thành công.
2. `monster_list` vẫn được đọc/ghi bởi `DataSyncManager`, `auto_hunt.py`,
   lifecycle và setup wizard. Phải xác định path nào còn active; normal Hunt
   runtime chỉ được dùng `monster_rotation`. Compatibility adapter chỉ được phép
   nằm tại migration boundary, không làm nguồn runtime thứ hai.
3. Config hiện có thể đồng thời chứa `monster_list` và `monster_rotation`; cần
   conflict precedence deterministic. `monster_rotation` canonical hợp lệ thắng;
   legacy chỉ backfill khi canonical trống, không merge tạo duplicate.
4. `CURRENT_SCHEMA_VERSION=2` và early return khiến config v2 bỏ qua mọi
   normalization mới. Vì `target_policy` và skill acknowledgment metadata được
   thêm sau PR #221, bump schema lên **3** và luôn chạy current-schema sanitizer
   sau versioned migration.
5. Atomic save chưa xóa temp file nếu dump/replace lỗi. Thêm cleanup trong
   `finally`, không để file rác; backup logic phải hỗ trợ migration `2 -> 3`,
   không hard-code chỉ `new_version == 2`.
6. UX3 trong PR #221 gọi `_schedule_save()` sau add/remove/reorder và tự ghi sau
   300ms, trái với UX hiện tại chỉ commit bằng Apply All. Chỉ giữ một commit path:
   thao tác mark dirty, `on_global_apply()` mới save.
7. Hai UX3 tests dùng fixture `mocker` nhưng `pytest-mock` không có trong
   `requirements.txt`; hiện kết quả là **22 passed, 2 errors**. Thay bằng
   `monkeypatch`/`unittest.mock` hoặc khai báo dependency đúng rồi chạy lại.
8. `target_policy`, `ack_strategy`, `hotbar_roi`, `ack_timeout_ms` chưa tồn tại
   trong production/tests của PR #221 và phải được normalize theo contract dưới.

Lưu ý branch: PR #221 nằm trong `origin/main`. Nếu đang ở feature/docs branch
không chứa merge `644156f`, phải cập nhật branch từ `origin/main` trước khi đánh
giá hoặc sửa; không kết luận từ source cũ trên branch chưa đồng bộ.

Objective:
Resolve data mismatch between `config_migrator.py`, `hunt_config.json`, `app_gui.py`, and `HuntOrchestrator`. Standardize on `skill_slots` and unified `monster_rotation`.

Target Files:

- Modify: `lib/features/hunt/config_migrator.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py`

## Implementation Details

1. Standardize schema fields:
   - Use `skill_slots: List[Dict[str, Any]]` as canonical source for active attack keys, cast times, and cooldowns. Each entry: `{"id": str, "key": str, "cast_time": float, "cooldown": float, "type": "attack"|"buff", ...}` (extend as needed by CB3B's dual-lane fields, e.g. `duration_sec` for buffs).
   - Preserve optional delivery-verification metadata for later CB3D integration: `ack_strategy: "combo"|"hotbar_cooldown"|"none"`, normalized `hotbar_roi: [x, y, w, h] | None`, and `ack_timeout_ms: int`. Defaults are `none`, `None`, and `500`; these fields configure observation only and must not be interpreted as proof that a cast succeeded.
   - Use `monster_rotation: List[Dict[str, Any]]` as the canonical unified structure for the hunt's target/monster priority list. Each entry: `{"monster_id": int, "name": str, "priority": int, "dungeon_id": Optional[str]}`, ordered by ascending `priority` (lower number = higher priority). This replaces any prior ad-hoc or per-feature monster-list representations scattered across `hunt_config.json` — confirm and enumerate exactly which legacy fields/keys currently hold this data (e.g. an old `target_list` or `monster_ids` array) before writing the migration mapping in step 2, since this schema was previously undefined and needs a concrete source-to-target field mapping.
   - Add top-level `target_policy: "configured_only" | "all_resolved" | "any_target"`, default `configured_only`. This field selects hunt behavior; it does not change the `monster_rotation` schema. Invalid or missing values normalize to `configured_only`.
   - Set top-level `schema_version: 3` for this follow-up. Treat absence as v1 and the PR #221 schema as v2. Version 3 adds `target_policy` and normalized skill acknowledgment metadata while completing `monster_list -> monster_rotation` migration.
   - Remove legacy fallback lookups for `attack_keys` and raw `skills` dict **only after** confirming migration runs unconditionally on load (see step 2) — do not remove the fallback and the auto-migration-on-load behavior in the same step without verifying order; a config that somehow bypasses migration and hits code with no fallback will crash.
2. In `config_migrator.py`:
   - Ensure migration safely translates older `skills: {}` or `attack_keys: []` into standardized `skill_slots`, and both real legacy keys `monster_list`/`monsters` into `monster_rotation`.
   - Legacy monster precedence: keep a valid, non-empty canonical `monster_rotation`; only backfill from `monster_list`/`monsters` when canonical is empty. Deduplicate by `(monster_id, dungeon_id)` and normalize priorities to `1..N`.
   - Conflict precedence: if a legacy config contains both `skills: {}` and `attack_keys: []` with overlapping/conflicting entries for the same key, `skills: {}` takes precedence (it carries richer per-skill metadata like cast_time/cooldown); `attack_keys` entries are only used to fill in keys not already present via `skills`.
   - Idempotency: apply versioned migrations only when the stored version is older than 3, then always run a lightweight current-schema sanitizer. Running migrate/sanitize twice must produce the same value; do not early-return before validating `target_policy` and optional skill acknowledgment fields.
   - Backup before overwrite: before writing any migrated version (including `2 -> 3`), copy the existing `hunt_config.json` to `hunt_config.json.bak`. Do not hard-code backup/write behavior to `new_version == 2`.
   - Ensure migration runs automatically as the first step of `hunt_config.py`'s load path (i.e. `load_hunt_config()` always calls the migrator before any other field is read), so no other code path can observe a pre-migration config shape.
   - Malformed/partial legacy entries: if an individual `skills`/`attack_keys` entry is missing a required field (e.g. no `key` or no `cast_time`), skip that single entry with a logged warning rather than raising or aborting the whole migration.
3. In `app_gui.py`:
   - Ensure `on_hunt_start()` exports `skill_slots` in exact format expected by `HuntOrchestrator.prepare_skill_runtime` (per the schema in step 1), and likewise exports `monster_rotation` in the format `HuntOrchestrator` expects for target prioritization.
   - Add/remove/reorder only update RAM and mark unsaved. Remove the PR #221 `_schedule_save()` auto-write path; `on_global_apply()` is the single user-facing commit point.
4. In legacy consumers:
   - Update active normal-Hunt paths in `DataSyncManager`, `ui/windows/auto_hunt.py`, lifecycle and setup wizard to consume canonical `monster_rotation`, or isolate them behind a one-way migration adapter.
   - Preserve `training_monster_list` only if training mode still requires it; it must not become a second normal-Hunt rotation source.
5. In `hunt_config.py`:
   - Keep atomic `os.replace()` from PR #221, but close/unlink the temp file on every failure path.
   - Ensure the parent directory exists, flush/close before replace, and return failure without leaving partial canonical files.

## Validation

- Run: `python tests/test_migration.py`
- Test loading legacy `hunt_config.json` and verify clean export without data loss.
- (Added) Idempotency test: run the migrator twice on the same legacy config; assert the second run is a no-op and produces byte-identical output to the first run's result.
- (Added) Backup test: run migration, assert `hunt_config.json.bak` exists and matches the pre-migration content.
- (Added) Conflict precedence test: construct a legacy config with both `skills` and `attack_keys` defining different `cast_time`/`key` for the same skill; assert the `skills`-derived value wins.
- (Added) Malformed entry test: construct a legacy config with one skill entry missing `cast_time`; assert migration completes, that entry is skipped with a logged warning, and all other entries migrate correctly.
- (Added) `monster_rotation` migration test: construct a legacy config using the old monster-list field(s) identified in step 1; assert it migrates into the new `monster_rotation` schema with correct `priority` ordering.
- (Added) Real legacy key test: migrate `monster_list` entries from the current config shape and assert no data loss.
- (Added) Conflict precedence test: valid canonical rotation wins over non-empty legacy data without duplicate merge.
- (Added) Runtime consumer search test: normal-Hunt production paths no longer read/write `monster_list` outside the migration compatibility boundary.
- (Added) Schema `2 -> 3` test: v2 config receives `target_policy` and skill acknowledgment defaults despite previously satisfying `schema_version >= 2`.
- (Added) Current-schema sanitizer idempotency test: malformed v3 policy/ROI normalizes once and the second run is value-identical.
- (Added) Atomic failure cleanup test: force dump/replace failure and assert original file remains valid and no temp file is left behind.
- (Added) Apply All ownership test: add/remove/reorder marks dirty but does not call save until `on_global_apply()`.
- (Added) `target_policy` validation test: missing/invalid values normalize to `configured_only`; all three supported values round-trip unchanged.
- (Added) Skill acknowledgment metadata test: valid optional `ack_strategy`, `hotbar_roi`, and `ack_timeout_ms` survive migration/round-trip; malformed ROI or unknown strategy normalize safely to `none`/`None`.

## Session Boundary Gate

- Verify no unhandled `KeyError` when loading empty or partially filled configuration files.
- Confirm migration is idempotent and runs unconditionally before any other config read.
- Confirm a `.bak` backup is written before any overwrite of the config file.
- Confirm `monster_rotation`'s schema and its legacy-field source mapping were concretely defined (not left as a placeholder) before implementation.
- Confirm `target_policy` has one of exactly three supported values and defaults fail-safe to `configured_only`.
- Confirm no active normal-Hunt consumer uses `monster_list` after migration.
- Confirm v2 configs migrate to v3 and current-schema sanitizer runs without destructive reprocessing.
- Confirm atomic-save failure leaves the original JSON readable and cleans temp files.
- Confirm UX3 tests run without undeclared fixtures and the focused result has no errors/skips hiding the gate.
- Report `PASSED`, `BLOCKED_LEGACY_CONSUMER`, or `REVERTED`; do not proceed to UX3B/CB2D/CB2C/CB3D on partial pass.

## Hardening Bổ Sung Sau CB4

**Note phạm vi:** Đây là yêu cầu **bổ sung sau khi** targeted CB4 rerun ở trên
đã pass. Mục này **không thay đổi** acceptance criteria/gate của CB4 trong phần
`Session Boundary Gate`; đây là hardening follow-up bắt buộc sau CB4, không phải
tiêu chí pass/fail mới để diễn giải lại kết quả rerun CB4.

Phần này là phần tiếp nối bắt buộc của targeted rerun. Không tạo schema hoặc
service song song; mọi thay đổi phải củng cố nguồn cấu hình canonical đã định
nghĩa ở trên.

### 1. Chốt Contract Buff

Trước khi code, chọn và ghi rõ một trong hai phương án:

- **Phương án mặc định:** buff nằm chung trong `skill_slots` với
   `type="buff"`; không tạo top-level `buff_slots`.
- Chỉ dùng `buff_slots` riêng nếu UX4.1/SkillRuntime đã có consumer và migration
   đầy đủ cho nó.

Không được để roadmap nói `buff_slots` nhưng runtime chỉ đọc `skill_slots`.
Nếu dùng chung, sanitizer phải chấp nhận `type="attack"|"buff"`, giữ
`duration_sec`/`pre_refresh_sec` cho buff và loại giá trị type không hợp lệ.

### 2. Chốt Contract Training Monsters

- `training_monster_list` chỉ phục vụ training mode, không phải normal Hunt
   rotation và không được CB2C dùng làm configured target source.
- Xác định schema riêng và owner hiện tại của training list trước khi sửa.
- Không trộn training record vào `monster_rotation` chỉ để tái sử dụng UI.
- Lifecycle/setup wizard phải kiểm tra đúng list theo mode; normal Hunt readiness
   chỉ dựa vào canonical `monster_rotation`.
- Nếu training mode được loại bỏ ở sprint khác, migration phải preserve dữ liệu
   cũ hoặc backup trước khi xóa; không silently drop.

### 3. Single-Writer Config Service

`os.replace()` chỉ ngăn file JSON bị ghi dở; nó không ngăn hai writer cùng
read-modify-write và ghi đè thay đổi của nhau.

Yêu cầu:

- Chọn một service/module duy nhất sở hữu ghi `hunt_config.json`.
- Mọi App/controller/service gọi API của owner này, không tự mở file để ghi.
- Bảo vệ read-modify-write trong process bằng `threading.RLock`.
- API nhận full canonical snapshot hoặc mutation callback có contract rõ; không
   trộn hai kiểu tùy tiện.
- Có revision/generation trong RAM để phát hiện stale write nếu hai thao tác cập
   nhật từ snapshot khác nhau trong cùng một process và cùng vòng đời chạy hiện
   tại; cơ chế này không bảo vệ qua app restart hoặc giữa nhiều process.
- Không giữ lock trong lúc gọi Tkinter, messagebox hoặc callback bên ngoài.
- Nếu cần hỗ trợ nhiều process ghi cùng file, báo follow-up riêng cho persisted
   revision trong JSON và/hoặc OS file lock; `RLock` chỉ bảo vệ trong một process.

### 4. Durability Và Atomic Save Failure

Quy trình ghi bắt buộc:

1. Tạo temp file trong cùng thư mục với file đích.
2. Serialize UTF-8 với `ensure_ascii=False`.
3. `flush()` và `os.fsync()` temp file trước khi đóng.
4. `os.replace()` temp sang file đích.
5. `fsync()` thư mục cha của file đích sau `os.replace()` để rename bền vững
   sau crash trên filesystem/OS có yêu cầu bước này; nếu platform không hỗ trợ
   directory `fsync`, phải xử lý best-effort và ghi chú rõ giới hạn durability.
6. Trong `finally`, đóng descriptor và xóa temp còn sót nếu replace chưa thành
   công.

Nếu serialize, fsync temp file, fsync thư mục cha hoặc replace thất bại:

- file canonical cũ vẫn phải đọc được;
- trả kết quả failure có error detail cho caller;
- không xóa dirty state;
- không hiển thị thông báo đã lưu thành công;
- không để file temp tích lũy.

### 5. Backup Semantics

- Ở đây, "một lần load" nghĩa là **một lần gọi `load_config()` cho một file
   config cụ thể** (một invocation độc lập), không phải suốt vòng đời process hay
   mỗi lần UI reopen cùng dữ liệu đã load sẵn.
- `.bak` phải là byte snapshot của file canonical **ngay trước khi áp dụng bất kỳ
   bước migration nào**, và trigger chính xác là: trong một lần `load_config()`,
   sau khi file canonical đã đọc + parse thành công, migrator lần đầu tiên phát
   hiện schema/version cũ hơn schema hiện tại cho document đó.
- Trong một lần `load_config()`, chỉ được tạo hoặc ghi đè `.bak` **tối đa một
   lần** tại thời điểm trigger ở trên; các bước migration tiếp theo trong cùng
   invocation không được tạo backup mới.
- Không được tạo/ghi đè backup nếu file nguồn đọc lỗi, parse lỗi, malformed, hoặc
   document đã ở schema hiện tại và không cần migration.
- Không thay backup tốt bằng file malformed hoặc bằng nội dung đã migrate.
- Migration failure phải giữ cả canonical cũ và backup đọc được.
- Normal Apply All không ghi đè migration backup; nếu cần backup cho save thường,
   dùng policy/tên file khác.

### 6. Canonical Validation

Tạo một sanitizer/validator dùng chung thay vì để migrator, UI và runtime tự
normalize khác nhau.

Đối với `monster_rotation`:

- `monster_id` phải là integer dương; ID `0`, âm hoặc không parse được không được
   vào configured attack list;
- `name` là chuỗi đã strip và không được dùng thay ID để cho phép attack;
- `priority` được normalize liên tiếp `1..N` theo thứ tự canonical;
- deduplicate theo `(monster_id, dungeon_id)`;
- `dungeon_id` là `str | None`, chuỗi rỗng normalize thành `None`;
- entry malformed bị loại với warning có index/reason, không làm hỏng toàn config.

Đối với `skill_slots`:

- key/ID/type/cooldown/cast time có kiểu và range hợp lệ;
- giữ optional acknowledgment metadata theo contract CB3D;
- normalized ROI phải có bốn số hữu hạn, width/height dương và nằm trong miền
   tọa độ đã chọn;
- timeout/cooldown không được âm.

Sanitizer phải idempotent và không mutate object đầu vào ngoài contract đã công
bố; ưu tiên trả canonical copy để runtime snapshot không bị thay đổi ngầm.

### 7. Apply All Và Dirty State

- Add/remove/reorder/mode change chỉ cập nhật RAM và mark dirty.
- `on_global_apply()` lấy một canonical snapshot rồi gọi single writer đúng một
   lần.
- Chỉ clear dirty state và hiển thị success khi save trả thành công.
- Save failure giữ nguyên dirty state và dữ liệu UI để người dùng retry.
- Nếu người dùng đóng app/view khi còn dirty, dùng flow xác nhận hiện có; không
   auto-save ngầm.
- Migration-on-load là ngoại lệ hệ thống có backup; không được dùng làm lý do để
   UX3 tự ghi sau mỗi thao tác.

### 8. Round-Trip Và Concurrency Tests

Bổ sung focused tests:

1. `load -> edit -> Apply All -> reload` giữ nguyên rotation, `target_policy`,
    skill/buff metadata và Unicode tiếng Việt.
2. Duplicate/invalid rotation entry được normalize đúng và warning được ghi.
3. Training list không ảnh hưởng normal Hunt readiness/runtime source.
4. Save failure giữ dirty state và không hiển thị success.
5. Hai thread update các field độc lập qua single writer không tạo JSON lỗi hoặc
    lost update.
6. Stale revision bị từ chối hoặc retry theo policy, không ghi đè im lặng.
7. Force lỗi serialize/fsync/replace: canonical cũ và `.bak` vẫn đọc được, temp
    file được dọn.
8. Unicode name và đường dẫn ảnh round-trip không bị escape/mất dữ liệu.
9. Search production code xác nhận không còn direct writer ngoài config owner.
10. Search normal Hunt code xác nhận legacy `monster_list`, `skills`,
      `attack_keys` chỉ còn ở migration boundary hoặc tài liệu/test legacy.

### Hardening Gate

CB4 chỉ được coi là hoàn tất toàn bộ khi:

- buff và training schema có owner/contract duy nhất;
- single writer bảo vệ read-modify-write;
- atomic save có fsync và cleanup failure path;
- backup không bị ghi đè bằng dữ liệu lỗi/đã migrate;
- validator canonical được dùng chung;
- Apply All failure không clear dirty state;
- round-trip/concurrency/failure tests pass;
- không còn normal-Hunt legacy consumer hoặc direct config writer ngoài boundary
   đã ghi rõ.

Nếu phần này vượt timebox còn lại, tách thành `CB4B Config Hardening` và giữ các
session phụ thuộc ở trạng thái `BLOCKED_BY_CB4_HARDENING`; không đánh dấu CB4
`PASSED` một phần rồi tiếp tục CB2D/UX3B/CB2C/CB3D.
