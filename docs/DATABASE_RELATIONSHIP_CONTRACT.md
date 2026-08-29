# Relationship Contract Cho CSDL Gameplay

## 1. Phạm vi

Contract này định nghĩa quan hệ chính xác giữa các bảng gameplay. Nó áp dụng cho DB1, DB4, DB6 và DB8; không được thay foreign-key action, key strategy hoặc seed order chỉ vì dữ liệu nguồn có tên gần giống.

## 2. Quan hệ và cardinality

| Parent | Child | Cardinality | Khóa liên kết | Delete action | Quy tắc |
| --- | --- | --- | --- | --- | --- |
| `dungeons` | `monsters` | 1 : N | `monsters.dungeonId → dungeons.id` | `SET NULL` | Monster có thể không có dungeon |
| `monster_type` | `monsters` | 1 : N | `monsters.serverBossType → monster_type.value` | `SET NULL` | `serverBossType` luôn giữ string hoặc `NULL` |
| `classes` | `skills` | 0..1 : N legacy | `skills.class_id → classes.class_id` | `RESTRICT` | Legacy field giữ tương thích; không dùng làm mapping canonical |
| `classes` | `class_skill_assignments` | 1 : N | `class_skill_assignments.class_id → classes.class_id` | `CASCADE` | Class delete chỉ xóa mapping, không xóa skill catalogue |
| `skills` | `class_skill_assignments` | 1 : N | `class_skill_assignments.skill_id → skills.skill_id` | `CASCADE` | Skill delete chỉ xóa mapping liên quan |
| `classes` | `synergies` | 1 : N | `synergies.class_id → classes.class_id` | `RESTRICT` | Không xóa class nếu còn synergy source data |
| `synergies` | `synergy_effects` | 1 : N | `synergy_effects.synergy_id → synergies.synergy_id` | `CASCADE` | Effect không tồn tại nếu không có synergy parent |
| `monsters` | `scans` | 1 : N | `scans.monster_id → monsters.id` | `CASCADE` | Scan chỉ là runtime/audit history |
| `skills` | `scans` | 1 : N | `scans.skill_id → skills.skill_id` | `RESTRICT` | Không xóa catalogue skill đang được scan tham chiếu |
| `classes` | `scans` / `builds` | 1 : N | `class_id → classes.class_id` | `RESTRICT` | Không xóa class còn được user/runtime data tham chiếu |

## 3. Quan hệ many-to-many class-skill

`class_skill_assignments` là quan hệ canonical giữa game class và game skill. Một class có nhiều skills; một catalogue skill có thể được gán cho nhiều classes khi source evidence xác nhận. `skills.class_id` không bị xóa trong migration đầu vì có thể còn caller legacy, nhưng không được dùng để kết luận coverage class-skill.

| Cột | Ràng buộc | Ý nghĩa |
| --- | --- | --- |
| `class_id` | `NOT NULL`, FK `CASCADE` | Class đã được DB2 seed |
| `skill_id` | `NOT NULL`, FK `CASCADE` | Skill catalogue đã được DB3 seed |
| `(class_id, skill_id)` | Composite primary key | Không duplicate assignment |
| `category` | `NOT NULL` | `bm1`, `bm2`, `bm3`, `attack`, `buff`, `debuff`, `passive`, `utility` khi source xác nhận |
| `source_ref` | `NOT NULL` | Stable locator/manifests từ DB5 |
| `is_recommended` | `NOT NULL DEFAULT 0` | Chỉ `1` khi source xác nhận recommendation |

Không insert assignment nếu class code hoặc skill code không resolve duy nhất. Record unresolved phải vào DB5 coverage report, không dùng fallback display name.

## 4. Thứ tự tạo schema và seed

1. DB1 tạo additive schema, unique indexes và relation tables.
2. DB2 seed `classes` với `class_code` unique.
3. DB3 seed `skills` với `skill_code` unique.
4. DB4 seed `synergies` rồi `synergy_effects`; class phải tồn tại trước.
5. DB5 tạo/approve mapping manifest từ source evidence.
6. DB6 seed `class_skill_assignments`; class và skill phải tồn tại trước.
7. DB7 chỉ đọc catalogue/mapping sau khi integrity checks pass.

Mỗi multi-table import dùng `BEGIN TRANSACTION`; lỗi parser, missing parent hoặc duplicate identity phải rollback toàn bộ batch đó.

## 5. Identity, uniqueness và provenance

- `classes.class_code` là normalized class source slug và unique khi không null.
- `skills.skill_code` là sprite catalogue source key và unique khi không null.
- Synergy identity dùng tối thiểu `(class_id, name, activation_sequence)` trong importer/manifest; không dùng row order làm identity.
- Effect identity dùng parent synergy cùng source position/raw fields trong importer; không dedupe theo `stat` đơn lẻ.
- Mọi importer ghi source ID, exact path, parser hash/version, accepted/rejected/duplicate counts.

## 6. Integrity queries bắt buộc

```sql
PRAGMA foreign_key_check;

SELECT class_code, COUNT(*)
FROM classes
WHERE class_code IS NOT NULL
GROUP BY class_code
HAVING COUNT(*) > 1;

SELECT skill_code, COUNT(*)
FROM skills
WHERE skill_code IS NOT NULL
GROUP BY skill_code
HAVING COUNT(*) > 1;

SELECT csa.class_id, csa.skill_id
FROM class_skill_assignments AS csa
LEFT JOIN classes AS c ON c.class_id = csa.class_id
LEFT JOIN skills AS s ON s.skill_id = csa.skill_id
WHERE c.class_id IS NULL OR s.skill_id IS NULL;

SELECT se.effect_id
FROM synergy_effects AS se
LEFT JOIN synergies AS syn ON syn.synergy_id = se.synergy_id
WHERE syn.synergy_id IS NULL;

SELECT syn.synergy_id
FROM synergies AS syn
LEFT JOIN classes AS c ON c.class_id = syn.class_id
WHERE syn.class_id IS NOT NULL AND c.class_id IS NULL;
```

Mọi query trên phải trả empty result, trừ row-count query có expected values do source parser tạo ra.