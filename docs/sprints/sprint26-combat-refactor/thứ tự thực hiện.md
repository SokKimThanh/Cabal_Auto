# LỘ TRÌNH CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 25 PHIÊN)

**Kiến trúc:** Four-Zone Command Center & Data-Driven Combat Engine  
**Timebox:** 20-30 phút/session; phút 20/25 validation, phút 25-30 chỉ targeted repair hoặc revert.

## Ghi Chú Bắt Buộc

1. CB4 chạy trước UX3A/UX3 để thống nhất schema; không tạo migration song song.
2. DB chỉ cung cấp metadata, không tự nhận diện hình ảnh. CB2D chỉ nhận quái có visual template map DB hợp lệ.
3. UX3A sở hữu DB picker; UX3 quản lý configured list; CB2D tạo detection snapshot; UX3B hiển thị ba mode/hai list và promotion.
4. CB2E chỉ dùng Windows user-mode APIs. Game không nhận background message thì báo `UNSUPPORTED`, không injection/hook/driver và không fallback âm thầm sang global input.
5. CB2C là owner duy nhất của active desired source/pointer và gate cho phép attack.
6. CB3D phân biệt transport `SENT` với game acknowledgment `ACCEPTED`; chỉ accepted mới commit skill cooldown/pointer/stats.
7. `monster_rotation` là persist; detection snapshot và attack queue là transient.
8. CB3 gốc phải được xác nhận hoàn tất trước CB3C.
9. DS1-DS5 là phase visual migration riêng, chỉ chạy sau UX5.2 để không restyle
   widget đang tiếp tục bị tái cấu trúc.
10. `DESIGN-SYSTEM-TKINTER-ADAPTER.md` là nguồn chuyển đổi bắt buộc; không truyền
   token CSS như `rgba`, gradient, shadow hoặc CSS font string vào Tkinter.
11. Nạp `00-global-rules.md` kèm mỗi session.

## Ba Chế Độ Săn

| UI | `target_policy` | Nguồn được phép đánh | Identity gate |
| --- | --- | --- | --- |
| Quái đã chọn | `configured_only` | `monster_rotation` | OCR/DB ID phải khớp configured ID |
| Tự nhận diện | `all_resolved` | Runtime candidate đã DB-match | OCR/DB ID phải khớp candidate còn TTL |
| Mọi mục tiêu | `any_target` | Target có Target Bar hợp lệ | CB1 alive gate, không yêu cầu ID |

Unknown vẫn xuất hiện trong danh sách phát hiện nhưng không được promote hoặc đánh trong hai mode kiểm tra danh tính. `any_target` là opt-in và phải cảnh báo rằng danh tính không được kiểm tra.

## Trạng Thái Gửi Và Nhận Skill

```text
READY -> RESERVED -> SENT -> WAITING_ACK
                              |-> ACCEPTED: commit cooldown/pointer/success
                              |-> REJECTED: failure policy
                              |-> UNVERIFIED: không ghi success, quarantine/pause
                              |-> CANCELLED: target chết hoặc Stop
```

Windows API trả thành công chỉ chứng minh `SENT`, không chứng minh game đã cast. Không dùng riêng Target Bar alive, hết cast time hoặc không có exception làm acknowledgment.

## Nguyên Tắc Chung

1. Worker/service không gọi Tkinter trực tiếp; dùng `schedule_ui_task()`/`after()`.
2. Không duy trì hai schema, hai runtime pointer hoặc hai đường ghi config.
3. Runtime detection không tự ghi vào `monster_rotation`.
4. Promote detected -> configured chỉ nhận DB-match, chống trùng và mark unsaved.
5. Mode được snapshot khi Start và không đổi giữa combat.
6. Skill pending không được gửi lặp mỗi worker tick.
7. Không fallback background -> foreground hoặc input API khác nếu người dùng chưa chọn.
8. Hỗ trợ tối thiểu 1366x768 và DPI 100%-200%.
9. Nếu dependency gate fail, báo `BLOCKED`; không mở rộng session để vá dependency.

## Thứ Tự Thực Thi

| # | Prompt | Phase | Kết quả chính | Phụ thuộc |
| :---: | --- | --- | --- | --- |
| 01 | `PROMPT-UX1` | UX | Quick Action Bar và Start/Stop debounce. | Window service |
| 02 | `PROMPT-UX2` | UX | Core shell và view swapping. | UX1 |
| 03 | `PROMPT-UX6` | UX | Activity logging theo kiến trúc UI hiện hành. | UX2, HuntLogger |
| 04 | `PROMPT-CB5` | Combat | Window scanner và ScreenCapture buffer. | ScreenCapture |
| 05 | `PROMPT-CB1` | Combat | Target Bar alive/dead và HP%. | CB5 |
| 06 | `PROMPT-CB2` | Combat | Hunt loop không spam target key trong attack. | CB1 |
| 07 | `PROMPT-CB2B` | Combat | OCR target name và resolve DB ID/HP. | CB2, database.py |
| 08 | `PROMPT-CB4` | Data | Canonical config, `target_policy`, skill ack metadata, migration và atomic save. | CB2B |
| 09 | `PROMPT-UX3A` | UX | DB Monster Picker dialog, chỉ trả canonical selection. | CB4, CB2B |
| 10 | `PROMPT-UX3` | UX | Configured rotation: picker integration, add/remove/reorder, DB metadata, Apply All. | CB4, CB2B, UX3A |
| 11 | `PROMPT-CB2D` | Vision | Detection snapshot và resolved runtime attack queue. | CB5, CB2B, CB4, UX3 |
| 12 | `PROMPT-UX3B` | UX | Segmented three-mode UI, two lists và detected-to-configured promotion. | CB4, UX3A, UX3, CB2D |
| 13 | `PROMPT-CB2E` | System | Background HWND input capability và fail-closed backend. | CB5, CB2 |
| 14 | `PROMPT-CB2C` | Combat | Thực thi ba policy; chỉ attack khi active policy cho phép. | CB1, CB2, CB2B, CB2D, CB2E, CB4, UX3, UX3B |
| 15 | `PROMPT-UX4.1` | UX | Dual-Lane Skill Strip. | UX2, CB4 |
| 16 | `PROMPT-UX4.2` | UX | Smart routing và conflict migration. | UX4.1, CB4 |
| 17 | `PROMPT-CB6` | Combat | Combo Bar timing trigger, không tự commit cast success. | CB5, Orchestrator |
| 18 | `PROMPT-CB3D` | Combat | Skill delivery acknowledgment, reservation/commit và truthful stats. | CB1, CB2E, CB4, UX4.2, CB6 |
| 19 | `PROMPT-CB3C` | Combat | Fast-Break và timing harmonization trên cast transaction đã xác minh. | CB6, CB3D, CB2C, CB3 gốc |
| 20 | `PROMPT-UX5.1` | UX | Active Target Card và image lifecycle. | UX2, CB2B |
| 21 | `PROMPT-UX5.2` | UX | Dynamic HP Canvas và window recovery. | UX5.1, CB1 |
| 22 | `PROMPT-DS1` | Design | Tkinter-safe tokens, font resolver và compatibility aliases. | Session 01-21 |
| 23 | `PROMPT-DS2` | Design | Central ttk theme và semantic component primitives. | DS1 |
| 24 | `PROMPT-DS3` | Design | Dark shell, sidebar, action bar và bottom chrome. | DS1, DS2 |
| 25 | `PROMPT-DS4` | Design | Hunt workspace, three-mode lists, skills và target card theme. | DS3, UX3B, UX4.2, UX5.2 |
| 26 | `PROMPT-DS5` | Design | Secondary views, dialogs và visual/accessibility acceptance. | DS4 |

## Luồng Target Và Scene Detection

```text
UX3A DB picker -> UX3 configured monster_rotation
             |
CB2D frame -> visual detection -> DB mapping
             |
             +-> runtime_detection_snapshot -> UX3B detected list
             |                                  +-> promote DB-match
             +-> runtime_attack_queue ----------+
                                                v
CB2B target OCR/DB ID -----------------------> CB2C policy coordinator
                                                |
CB2E targeted input backend <-------------------+
                                                |
                     configured_only: match configured ID
                     all_resolved: match runtime DB candidate
                     any_target: CB1 alive gate, no identity gate
                                                |
                                                v
                                         allow/deny attack
```

## Luồng Gửi Và Xác Minh Skill

```text
CB2C cho phép attack
-> SkillRuntime reserve skill (chưa advance)
-> CB6 chọn hit-zone nếu Combo mode
-> CB2E gửi skill key tới backend
-> TransportStatus SENT/FAILED
-> CB3D quan sát frame hậu kiểm
   -> hotbar cooldown delta hoặc combo progression
   -> ACCEPTED: commit cooldown + pointer + accepted stats
   -> UNVERIFIED: không success, pause/quarantine theo policy
   -> REJECTED: bounded retry/stop theo policy
   -> CANCELLED: target chết/Stop
-> CB3C xử lý timing/fast-break mà không double-advance
```

Không được coi các tín hiệu sau là cast success: `PostMessage=True`, `SendInput` không lỗi, Target Bar còn sống, hết `cast_time`, hoặc HP giảm không gắn được với skill cụ thể.

## Background Input

```text
CB2E SUPPORTED
-> không focus game
-> gửi target/skill key tới selected HWND
-> chuột/bàn phím vật lý vẫn dùng được

CB2E UNVERIFIED/UNSUPPORTED
-> background mode không Start
-> người dùng chủ động chọn foreground mode nếu chấp nhận
-> không fallback âm thầm
```

## Luồng Thay Đổi Giao Diện

```text
21 UX5.2 hoàn tất cấu trúc chức năng
-> 22 DS1 chuyển design tokens sang Tkinter-safe values
-> 23 DS2 cấu hình ttk + button/component semantic roles
-> 24 DS3 áp theme cho shell/sidebar/action bar/footer
-> 25 DS4 áp theme cho Hunt workspace và mọi runtime state
-> 26 DS5 áp secondary views + chạy visual/accessibility gate
```

Design direction:

- dark neutral command-center, không dark-blue một màu;
- green chỉ cho active/hunting/primary, blue cho selected/info, yellow cho ready,
   red cho stop/danger;
- solid colors thay CSS gradient/shadow trên widget native;
- font resolver có fallback, không bắt buộc Rajdhani/Inter phải được cài;
- không đổi business logic, callback, queue hoặc geometry ownership trong session
   style.

## Quy Trình Mỗi Session

1. Nạp `00-global-rules.md` và đúng một prompt theo thứ tự 01-26.
2. Kiểm tra dependency/preflight trước khi sửa.
3. Phút 00-20/25: production code và focused tests.
4. Phút 20/25-30: test, smoke và targeted repair.
5. Chỉ chạy session kế tiếp khi gate đạt.
6. Báo `PASSED`, `BLOCKED`, `UNVERIFIED`, `UNSUPPORTED` hoặc `REVERTED` kèm bằng chứng.
