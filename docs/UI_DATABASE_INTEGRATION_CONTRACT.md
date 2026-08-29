# UI - Database Integration Contract

## 1. Mục tiêu

Contract này đối chiếu UI main-screen roadmap với database roadmap. Nó ngăn việc UI session giả định rằng catalogue SQLite đã thay thế user configuration, hoặc DB session thay đổi shape data đang được HuntTab/SetupTab/runtime đọc.

## 2. Hiện trạng dữ liệu UI

| UI workflow | Consumer hiện tại | Source runtime hiện tại | Dữ liệu UI cần | Trạng thái DB catalogue |
| --- | --- | --- | --- | --- |
| Monster Rotation | HuntTab và monster runtime | `lib/data/monsters.json` qua `load_monster_library()` | name, enabled, priority, stats, template(s), `window_bounds` | `monsters` schema có 30 stats nhưng live rows hiện là 0; không chứa rotation/user template state |
| Quick Skill View | HuntTab và SkillRuntimeService | `lib/data/skills.json` qua `load_skill_library()` | name, key, type, cooldown, cast_time, image, optional buff timing | `skills` schema có sprite/class fields nhưng live rows hiện là 0; chưa có runtime key/cooldown/cast_time/image contract |
| Active Target / bounds | App/HuntTab | `hunt_cfg`, selected window, WindowSelectionService | window title/HWND/PID, normalized bounds, target region, runtime state | Không thuộc gameplay catalogue DB |
| Sidebar setup | SetupTab | `hunt_cfg` và config | mode, hotkey, template/region, hunt timing | Không thuộc class/skill catalogue DB |
| Timing recommendation | Monster manager/calculator | selected monster config | hp, defense, level, chosen skill timing | Có thể lookup monster stats từ DB sau khi seed, nhưng không được overwrite selected user config |

## 3. Quyết định kiến trúc

1. `lib/data/monsters.json`, `lib/data/skills.json`, `lib/data/hunt_config.json` vẫn là source of truth cho runtime/UI user configuration trong tất cả UX sessions hiện tại.
2. `classes`, `skills`, `class_skill_assignments`, `synergies`, `synergy_effects` trong SQLite là reference catalogue. Chúng chỉ được đọc để enrich, validate hoặc populate a selection UI sau DB7.
3. Không thay source của `SkillRuntimeService`, `load_skill_library()` hoặc `load_monster_library()` trong UX1-UX5 hay DB1-DB6.
4. DB7 phải cung cấp adapter/read-model, không trả trực tiếp raw SQLite rows cho UI. Adapter map catalogue fields sang explicit view model và giữ nguyên user-runtime fields.
5. Bounds/window selection, hotkey, target region, current hunt state và Bottom Logs không được chuyển vào class/skill catalogue tables.

## 4. UI-to-DB mapping

| UI zone | Feature | Được phép đọc DB | Không được phép thay đổi qua DB integration | Prerequisite |
| --- | --- | --- | --- | --- |
| A | Bounds readiness / Start/Stop | Không cần | `hunt_cfg`, normalized bounds, button callbacks | Không có |
| B | Monster Rotation | Monster reference stats để display/timing enrichment sau DB monster seed | rotation order, enabled state, templates, user-selected bounds | Canonical monster data seed + explicit adapter |
| B | Quick Skill View | skill icon/class/category catalogue sau DB2/DB3/DB6 | key binding, cooldown, cast time, image path, chosen slots | Class/skill seed + mapping manifest + adapter |
| B | Active Target & Status | Optional read-only class/skill display metadata | hunt runtime state, selected target, recovery policy | Không có |
| C1 | Managers / preset entries | catalogue search/filter data sau seed | user config persistence, hotkeys, setup mode | DB read service + adapter |
| C2 | Bottom Logs | Không cần catalogue DB | log source/threading/persistence | Existing thread-safe log source |

## 5. Adapter contract cho DB7

DB7 chỉ được triển khai sau DB2, DB3, DB5 và DB6 pass. Adapter phải có trách nhiệm rõ ràng:

| Adapter | Input | Output | Fallback |
| --- | --- | --- | --- |
| `MonsterCatalogueLookup` | stable monster ID/name từ user config | immutable reference stats/metadata | Không có DB row: giữ nguyên user config, trả no-match result |
| `SkillCatalogueLookup` | `skill_code` hoặc approved canonical mapping | icon/category/class references | Không có DB row/mapping: giữ nguyên user skill, không chặn hunt |
| `SkillRuntimeView` | user skill library record + optional catalogue record | runtime fields từ user library; reference fields từ catalogue | Không dùng catalogue để điền guess key/cooldown/cast_time/image |

Không join theo display name không chuẩn hóa. Không mutate `skills.json`/`monsters.json` khi render. Catalogue lookup phải read-only trong UI thread; bất kỳ DB read dài phải lấy data ngoài UI thread rồi chuyển snapshot qua `after(0, ...)` hoặc queue theo UI ownership contract.

## 6. Điều chỉnh prompt và dependency

- UX2B.2 Quick Skill Strip chỉ dùng `skills.json` và bindings hiện có. Không chờ catalogue DB.
- UX3/UX3B Manager entry points không đổi persistence sang DB.
- UX4 Active Status không đọc DB để quyết định warning/runtime state.
- DB7 chỉ thêm read adapter/fallback và focused tests. UI binding của adapter là session riêng sau DB7, không gộp vào DB7.
- Future preset/recommendation feature chỉ dùng class/skill catalogue khi mapping manifest được approved; nếu không, feature phải hiển thị unavailable/empty state, không suy diễn dữ liệu.

## 7. Validation

1. User library behavior: add/edit/select skill và monster vẫn đọc/ghi đúng JSON sau DB seed/DB7.
2. Empty/unseeded DB: UI vẫn mở, rotation/skills hiện như trước và hunt không bị block.
3. Seeded DB with no class-skill assignment: user skill vẫn usable, catalogue enrichment không bịa class/category.
4. Seeded DB with valid mapping: adapter trả đúng reference metadata nhưng không đổi user key, cooldown, cast_time hoặc image.
5. FK/mapping integrity: chạy queries trong `DATABASE_RELATIONSHIP_CONTRACT.md`.
6. Thread boundary: DB lookup không gọi Tkinter; render UI chỉ chạy trên Main Thread.