# Database Update Prompt Pack

Bộ prompt này cập nhật SQLite dựa trên dữ liệu hiện có, theo hướng additive, idempotent và có kiểm thử. Source of truth cho mục tiêu và tình trạng ban đầu là [DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md](../../../docs/DATABASE_SKILL_CLASS_UPDATE_ROADMAP.md).

Khi chạy cùng i18n và UI cleanup, tuân theo [CROSS_STREAM_PROMPT_EXECUTION_ORDER.md](../../CROSS_STREAM_PROMPT_EXECUTION_ORDER.md). Đặc biệt: `DB1` phải pass trước i18n `I3A`; `DB7` không tự mở khóa UI catalogue binding.

Trước khi chạy bất kỳ session nào, bắt buộc đọc [DATABASE_SOURCE_DATA_MANIFEST.md](../../../docs/DATABASE_SOURCE_DATA_MANIFEST.md). Mỗi prompt chỉ được dùng source ID đã chỉ định; file tên tương tự, user library và bundle không được manifest cho phép là forbidden input.

## Thứ tự thực hiện

1. `DB0-schema-and-source-audit.md`
2. `DB1-additive-schema-migration.md`
3. `DB2-seed-classes.md`
4. `DB3-seed-skill-sprite-catalogue.md`
5. `DB4-seed-bm3-synergies.md`
6. `DB5-class-skill-mapping-audit.md`
7. `DB6-import-verified-class-skill-mappings.md`
8. `DB7-runtime-integration.md`
9. `DB8-integrity-tests-and-docs.md`

Không chạy session sau khi dependency chưa pass. `DB5` có thể block DB6 nếu không có manifest mapping có source evidence; không tự suy diễn mapping từ tên skill/icon.