# i18n - Database Compatibility Contract

## 1. Kết luận

i18n có thể dùng cùng SQLite database với gameplay catalogue, nhưng `translations` là dữ liệu UI copy độc lập. Bảng này không có foreign key tới `classes`, `skills`, `monsters`, `dungeons`, `synergies`, `scans` hoặc `builds`.

Translation lookup phải không chặn hunt/UI startup. Nếu database translation không tồn tại, trống, lỗi migration hoặc query thất bại, registry dict đã self-register là fallback bắt buộc.

## 2. Ownership và schema boundary

| Thành phần | Owner | Source of truth | Không được làm |
| --- | --- | --- | --- |
| `translations` schema / service | i18n Sprint 3 | `(namespace, key, lang) → text` | Không chứa game stats, config runtime, sprite metadata hoặc user setting |
| Gameplay catalogue schema | Database update DB1-DB8 | classes, skills, mappings, synergies, monsters | Không tạo/cập nhật UI copy khi seed gameplay |
| UI language render | `lib.i18n.t()` / `App._t()` | in-memory registry hydrated từ DB hoặc dict fallback | Không query SQLite trực tiếp trong widget render/callback |
| Runtime config | `skills.json`, `monsters.json`, `hunt_config.json` | user selections/timing/bounds/hotkeys | Không bị translation migration ghi đè |

Schema translation tối thiểu:

```sql
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    lang TEXT NOT NULL,
    text TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(namespace, key, lang)
);
```

Không thêm FK từ `translations.namespace/key` vào catalogue tables. Namespace/key là stable UI contract, không phải database display-name relationship. Ví dụ metadata catalog có thể dùng key `class.blader.name` hoặc `skill.axe_attack_a.name`, nhưng translation record vẫn chỉ phụ thuộc source code ổn định, không phụ thuộc numeric `class_id`/`skill_id` có thể khác giữa DB instances.

## 3. Migration coordination

1. DB1 và i18n I3A đều sửa schema khởi tạo của cùng `monsters.db`; không chạy song song trên cùng branch/worktree.
2. DB1 phải hoàn thành/merge trước I3A, hoặc I3A phải rebase trên DB1 và đưa translation schema vào cùng schema-init contract, không duplicate migration logic trong `database.py`.
3. I3A chỉ thêm `translations` cùng index/unique constraint; không sửa gameplay table/foreign key.
4. I3B chỉ hydrate in-memory registry sau schema readiness. Không được làm DB query trên mỗi call `t()` hay trong Tkinter render path.
5. DB7 catalogue adapter không đọc `translations`; i18n hydration không đọc catalogue mappings. Hai service chỉ chia connection lifecycle/schema-init policy.

## 4. Fallback và third-language safety

Registry hiện tại lookup `requested language → default language → global namespace → raw key`. Khi user đặt default language là pilot `zh`/`ko`, key không có trong pilot namespace có thể rơi xuống raw key, không tự fallback về `en` hoặc `vi`.

Do đó I4B không được thêm pilot language vào language selector toàn app chỉ với 10 global keys. Chỉ có hai đường an toàn:

1. Pilot giới hạn trong test/tool gọi explicit namespace/language có đầy đủ reachable keys; language selector không expose pilot language.
2. Tách session riêng để implement và test fallback chain rõ ràng, ví dụ `requested → en → vi → key`, rồi mới expose pilot language toàn app.

Mục tiêu “thêm language chỉ bằng data” chỉ hợp lệ sau khi fallback contract đã tồn tại **hoặc** pilot có coverage đầy đủ cho tất cả namespace/key có thể render trong screen được expose.

## 5. Validation cross-roadmap

1. Empty/missing `translations` table: dict self-registration vẫn trả copy `en`/`vi`, không raw key.
2. Translation DB error: app startup không fail; error được log một lần, fallback tiếp tục hoạt động.
3. Gameplay DB empty/unseeded: i18n vẫn render; UI JSON runtime vẫn hoạt động.
4. Gameplay seed/migration: row count trong `translations` không đổi ngoài session i18n được phép.
5. Translation migration: row count/foreign keys của classes, skills, mappings, synergies, monsters không đổi.
6. Pilot third language: test missing-key behavior trước khi expose selector; không chấp nhận raw key trên UI screen được expose.
7. Startup: hydration xảy ra trước visible UI render; UI thread không block trên per-widget DB lookup.