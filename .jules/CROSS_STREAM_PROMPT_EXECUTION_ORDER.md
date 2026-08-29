# Thứ Tự Chạy Prompt: Database, i18n và UI

## 1. Quy tắc điều phối

Đây là thứ tự chạy an toàn cho bốn stream `database-update`, `i18n-unification`, `ui-main-screen-cleanup` và `sprint25-monster-editor`. Một session chỉ bắt đầu khi dependency của nó `PASSED`, đã chạy validation bắt buộc và không để lại rollback/recovery chưa xử lý.

- Chỉ Wave 0 được chạy song song vì cả hai session chỉ đọc/audit.
- Không chạy hai session thay đổi `database.py`, `lib/db/schema.py`, `app_gui.py`, `lib/i18n/__init__.py`, hoặc cùng SQLite DB trong cùng worktree/branch.
- Mỗi session tối đa 30 phút; áp dụng global rules của prompt pack tương ứng.
- Session `ABORTED/REVERTED` phải được sửa bằng session mới hoặc chạy lại thành công trước khi dependency tiếp theo bắt đầu.
- Không dùng DB catalogue để thay JSON runtime UI trước DB7 và UI adapter session riêng.

## 2. Execution waves

| Wave | Chạy prompt theo thứ tự | Có thể song song | Điều kiện để qua wave |
| --- | --- | --- | --- |
| 0 | `DB0` và `P0` | Có, hai audit read-only | Có snapshot schema/source và i18n inventory rõ ràng |
| 1 | `I1A → I1B → I2A → I2B` | Không | Dict registration ổn định, audit test và i18n convention pass |
| 2 | `M25-0 → M25-1 → M25-2 → M25-3 → M25-4 → M25-5 → M25-6` | Không | Monster Editor full-field flow, pending changes, persistence và bilingual copy pass |
| 2B | `M25-X.1 → M25-X.2 → M25-X.3` | Không | Optional hardening wave; chỉ chạy sau M25-6 nếu cần proof thêm cho silent-data-loss boundaries |
| 3 | `DB1 → I3A` | Không | Gameplay schema additive và translations schema cùng schema-init contract |
| 4 | `UX1 → UX1B → UX2.1 → UX2.2 → UX2B.1 → UX2B.2 → UX3 → UX3B → UX4 → UX4B.1 → UX4B.2` | Không | Main screen layout/UI validation pass; vẫn dùng JSON runtime source |
| 5 | `DB2 → DB3 → DB4 → DB5 → DB6` | Không | Class, sprite catalogue, synergy, mapping manifest và verified mappings pass |
| 6 | `DB7 → I3B` | Không | DB adapter/fallback pass, sau đó i18n hydration startup/fallback pass |
| 7 | `I4A → I4B → DB8 → I5A → UX5` | Không | Consumer cleanup, language-scale tooling, DB integrity/docs, i18n consolidation và final UI roadmap pass |

`P0` là i18n baseline inventory trong `.jules/prompts/i18n-unification/`. `DB0` là database schema/source audit trong `.jules/prompts/database-update/`.

## 3. Lý do dependency giữa ba stream

| Dependency | Lý do |
| --- | --- |
| `I2B → UX1B/UX3B/UX4` | Các UI session này thêm hoặc thay đổi visible copy/status. i18n audit/convention phải tồn tại trước để key `en`/`vi` không bị raw-key leak. |
| `I2B → M25-0...M25-6` | Sprint 25 thêm/đổi visible `monster_editor` labels, group titles và validation text. Self-registration, registry audit và bilingual convention phải pass trước khi form fields mới được expose. |
| `M25-1 → M25-2/M25-3/M25-4` | Field metadata và round-trip helper phải ổn định trước khi xây form, advanced groups hoặc reference comboboxes. |
| `M25-1...M25-4 → M25-5/M25-6` | Manager callback/persistence chỉ được nhận candidate đầy đủ sau khi dialog load/collect/default/reference contract pass. |
| `M25-6 → M25-X` | Hardening wave chỉ kiểm tra regression sau full-field save/persistence và focused tests đã pass. |
| `M25 → DB1` | Sprint 25 dùng schema monster/dungeon/type hiện có và không cần class/skill catalogue. Chạy trước DB1 giảm rủi ro đồng thời sửa `database.py` và phân tách UI data-loss fix khỏi schema migration. |
| `DB1 → I3A` | Cả hai sửa schema-init của `monsters.db`; DB1 tạo identity/relationship migration trước, I3A chỉ thêm `translations` độc lập. |
| `I3A → I3B` | Hydration chỉ chạy sau khi translations schema/service/migration có mặt. |
| `UX2.2 → UX2B.1/UX3/UX4B.1` | Outer shell và child rebuild phải pass trước khi chỉnh Workspace, Sidebar hoặc Bottom Logs. |
| `UX2B.1 → UX2B.2/UX4` | Primary panels phải ổn định trước khi đặt Quick Skill Strip hoặc status render. |
| `DB2 + DB3 + DB5 → DB6` | Class, skill catalogue và verified mapping manifest phải tồn tại trước khi insert many-to-many mapping. |
| `DB2-DB6 → DB7` | UI/runtime adapter chỉ được lookup catalogue đã seed và mapping đã có evidence. |
| `DB7 → UI catalogue feature` | Không UI session nào đọc raw DB; feature UI dùng catalogue phải là session mới sau DB7. |
| `I3B → I4A` | Không xóa consumer manual registration trước khi central DB hydration + dict fallback hoạt động. |
| `I4A/I4B + DB8 → I5A` | Final i18n audit cần cả registration cleanup, language tooling và DB integrity evidence. |
| `UX stages → UX5` | UX5 roadmap chốt từ implementation evidence, không từ giả định. |

## 4. Handoff bắt buộc giữa waves

Mỗi session cuối wave phải báo cáo:

1. `PASSED` hoặc `ABORTED/REVERTED`.
2. Validation command/result và boundary cases.
3. Schema/source counts/FK result nếu là DB session.
4. Raw-key/fallback result nếu là i18n session.
5. Layout, i18n, Main Thread và JSON-runtime preservation result nếu là UI session.
6. Files changed và dependency được mở khóa hoặc vẫn blocked.

Không mở khóa session tiếp theo chỉ bằng app startup; phải có validation đặc thù trong prompt đang chạy.

## 5. Ngoại lệ và phần việc deferred

- Nếu DB5 không tạo được reproducible mapping manifest, `DB6` và `DB7` bị blocked. UI vẫn có thể hoàn thành các session không đọc catalogue DB vì JSON runtime là source of truth.
- Nếu I3B fallback trả raw key, dừng I4A/I4B và sửa hydration/fallback trước.
- Nếu UX2.2 hoặc UX2B.1 có layout breakage, dừng các UI session sau và recovery/revert theo UI global rules.
- Nếu M25-4 không lấy được reference data, form phải dùng empty/legacy-safe fallback; không block M25-5/M25-6 bằng cách sửa schema/reference seed trong cùng session.
- Nếu M25-5 phát hiện pending record bị mất qua refresh/filter/page, dừng M25-6 và sửa pending merge trước; persistence không được dùng để che data-loss bug.
- `UX5` đã có thể tồn tại như tài liệu đề xuất, nhưng chỉ được đánh dấu implementation-backed sau khi Wave 3 pass.