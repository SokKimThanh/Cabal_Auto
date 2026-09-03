# Hunt Settings Apply Contract

## Purpose

Nút footer hiện có `on_global_apply()` chỉ áp dụng cấu hình của Hunt. Nhãn UI được đổi thành:

- `vi`: **Áp dụng Cài đặt Săn**
- `en`: **Apply Hunt Settings**

Key i18n vẫn giữ là `apply_all_settings` để tránh phá các call site hiện có; chỉ text hiển thị được đổi.

## Current Ownership

| Domain | Owner hiện tại | Đường ghi | Phạm vi |
| --- | --- | --- | --- |
| Hunt config | `App.on_global_apply()` + `AppStateController._hunt_from_ui()` | `save_hunt_config()` | `monster_rotation`, `skill_slots`, target/window settings, `target_policy`, hotkeys được expose trong App |
| Monster/skill library | `LibraryManagerController` / `LibraryManagerWindow` | `save_monster_library()`, `save_skill_library()` | CRUD thư viện và timing changes của Library Manager |
| Monster editor | `MonsterManagerWin` và controller | editor/service save path | Chi tiết monster, templates, column settings |
| Vision/template | Vision/setup owners | owner-specific save path | Template và capture configuration |
| Runtime detection | CB2D queue | Không ghi config | Snapshot transient, TTL, confidence, bbox |

`on_global_apply()` không phải transaction toàn ứng dụng. Nó không được coi là writer cho database, monster library, skill library, vision assets hoặc runtime snapshot.

## Current Flow

```text
HuntTab / Setup UI
    -> App.on_global_apply()
    -> AppStateController._hunt_from_ui()
    -> canonical hunt snapshot
    -> save_hunt_config()
    -> clear dirty state only on success
```

Rotation edits remain in RAM until the user presses this button. Picker/dialogs must not write `hunt_config.json` directly.

## Contract Invariants

1. The button label must describe Hunt scope, not all application settings.
2. The snapshot must contain canonical `monster_rotation` entries only:
   `monster_id`, `name`, `priority`, `dungeon_id`.
3. Runtime metadata such as level, HP, confidence, bbox, TTL and cache must not be persisted in Hunt config.
4. A save failure must preserve dirty state and must not show success.
5. Library Manager and Monster Manager keep their own save/apply ownership.
6. No second writer or hidden autosave may be added to make this button appear global.

## Future Database Persistence Option

The current contract continues to persist Hunt settings in `hunt_config.json`.
Moving configuration into the database is a possible future direction, but it is
not part of the current Apply Hunt Settings implementation.

Database persistence becomes useful when the app needs multiple Hunt profiles,
transactional updates across related settings, revision history, or
multi-machine synchronization. It must be introduced as a separate migration
and architecture change, not as an additional write path beside the JSON file.

Before adopting database persistence, define:

- a schema and one configuration repository/service owner;
- a one-time JSON-to-database migration with backup, validation and rollback;
- transaction boundaries for Hunt, skill and target configuration updates;
- revision/concurrency handling for stale UI snapshots and concurrent writers;
- the source-of-truth policy during backward compatibility and recovery;
- import/export behavior for users who still need a JSON configuration file.

`runtime_detection_snapshot`, `runtime_attack_queue`, confidence, bbox, TTL and
other per-session state must remain transient. They must not be inserted into
the persistent configuration tables merely because the configuration storage
is moved to the database.

Until this design is approved, `save_hunt_config()` remains the only persistent
writer for Hunt settings and the JSON file remains the canonical source.

## Future App-Wide Coordinator

If the product later needs one **Apply All Application Settings** action, introduce an explicit coordinator instead of expanding the current button implicitly. The coordinator must define:

- domain snapshot interfaces for Hunt, library, skills and Vision;
- validation order and an all-or-fail result contract;
- ownership of each file/database writer;
- rollback/backup semantics for partial failure;
- dirty state per domain and aggregate dirty state;
- UI success/failure reporting that names the domains actually committed.

Until those contracts exist, keep separate Apply actions and avoid claiming atomicity across domains.

## Acceptance Checks

- In `vi`, footer displays `Áp dụng Cài đặt Săn`.
- In `en`, footer displays `Apply Hunt Settings`.
- Adding/reordering/removing rotation changes only RAM until the button is pressed.
- Pressing the button writes Hunt config and preserves canonical rotation data.
- Library/Monster Manager changes are not falsely reported as committed by this button.
- Save failure leaves the dirty indicator active.

## Status

The label correction is implemented. The app-wide coordinator remains analysis-only and is intentionally deferred until a separate architecture session defines cross-domain transaction semantics.
