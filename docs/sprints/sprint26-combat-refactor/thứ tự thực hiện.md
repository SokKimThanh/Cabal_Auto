# LỘ TRÌNH CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 19 PHIÊN)

**Kiến trúc:** Four-Zone Command Center & Data-Driven Combat Engine  
**Timebox:** 20-30 phút/session; phút 20/25 validation, phút 25-30 chỉ targeted repair hoặc revert.

## Ghi Chú Bắt Buộc

1. CB4 chạy trước UX3 để thống nhất schema; không tạo migration song song.
2. CB3 gốc phải được xác nhận hoàn tất trước CB3C.
3. DB chỉ cung cấp metadata, không tự nhận diện hình ảnh. CB2D chỉ nhận quái có visual template map DB hợp lệ.
4. UX3 quản lý configured list; CB2D tạo detection snapshot; UX3B hiển thị ba mode/hai list và promotion.
5. CB2E chỉ dùng Windows user-mode APIs. Game không nhận background message thì báo `UNSUPPORTED`, không injection/hook/driver và không fallback âm thầm sang global input.
6. CB2C là owner duy nhất của active desired source/pointer và gate cho phép attack.
7. `monster_rotation` là persist; detection snapshot và attack queue là transient.
8. Nạp `00-global-rules.md` kèm mỗi session.

## Ba Chế Độ Săn

| UI | `target_policy` | Nguồn được phép đánh | Identity gate |
| --- | --- | --- | --- |
| Quái đã chọn | `configured_only` | `monster_rotation` | OCR/DB ID phải khớp configured ID |
| Tự nhận diện | `all_resolved` | Runtime candidate đã DB-match | OCR/DB ID phải khớp candidate còn TTL |
| Mọi mục tiêu | `any_target` | Target có Target Bar hợp lệ | CB1 alive gate, không yêu cầu ID |

Unknown vẫn xuất hiện trong danh sách phát hiện nhưng không được promote hoặc đánh trong hai mode kiểm tra danh tính. `any_target` là opt-in và phải cảnh báo rằng danh tính không được kiểm tra.

## Nguyên Tắc Chung

1. Worker/service không gọi Tkinter trực tiếp; dùng `schedule_ui_task()`/`after()`.
2. Không duy trì hai schema, hai runtime pointer hoặc hai đường ghi config.
3. Runtime detection không tự ghi vào `monster_rotation`.
4. Promote detected -> configured chỉ nhận DB-match, chống trùng và mark unsaved.
5. Mode được snapshot khi Start và không đổi giữa combat.
6. Hỗ trợ tối thiểu 1366x768 và DPI 100%-200%.
7. Nếu dependency gate fail, báo `BLOCKED`; không mở rộng session để vá dependency.

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
| 08 | `PROMPT-CB4` | Data | Canonical config, `target_policy`, migration và atomic save. | CB2B |
| 09 | `PROMPT-UX3` | UX | Configured rotation: add/remove/reorder, DB metadata, Apply All. | CB4, CB2B |
| 10 | `PROMPT-CB2D` | Vision | Detection snapshot và resolved runtime attack queue. | CB5, CB2B, CB4, UX3 |
| 11 | `PROMPT-UX3B` | UX | Segmented three-mode UI, two lists và detected-to-configured promotion. | CB4, UX3, CB2D |
| 12 | `PROMPT-CB2E` | System | Background HWND input capability và fail-closed backend. | CB5, CB2 |
| 13 | `PROMPT-CB2C` | Combat | Thực thi ba policy; chỉ attack khi active policy cho phép. | CB1, CB2, CB2B, CB2D, CB2E, CB4, UX3, UX3B |
| 14 | `PROMPT-UX4.1` | UX | Dual-Lane Skill Strip. | UX2, CB4 |
| 15 | `PROMPT-UX4.2` | UX | Smart routing và conflict migration. | UX4.1, CB4 |
| 16 | `PROMPT-CB6` | Combat | Combo Bar timing detector. | CB5, Orchestrator |
| 17 | `PROMPT-CB3C` | Combat | Fast-Break và timing harmonization. | CB6, CB2C, CB3 gốc |
| 18 | `PROMPT-UX5.1` | UX | Active Target Card và image lifecycle. | UX2, CB2B |
| 19 | `PROMPT-UX5.2` | UX | Dynamic HP Canvas và window recovery. | UX5.1, CB1 |

## Luồng Chức Năng Trọng Tâm

```text
UX3 configured monster_rotation
             |
             v
CB2D frame -> visual detection -> DB mapping
             |
             +-> runtime_detection_snapshot -> UX3B detected list
             |                                  |
             |                                  +-> drag/+ /double-click/Enter
             |                                  +-> configured list (pending Apply)
             |
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

## Chuyển Mode Và Danh Sách

```text
Quái đã chọn
-> chỉ configured list
-> người dùng thêm từ DB
-> Apply All mới persist

Tự nhận diện
-> detected list + configured list
-> DB-match tự vào runtime queue
-> unknown vẫn hiển thị nhưng không attack/promote
-> kéo DB-match sang configured list để dùng về sau

Mọi mục tiêu
-> không cần configured/runtime identity match
-> CB1 xác nhận Target Bar sống thì được đánh
-> không tạo ID giả, không ghi DB/config
```

Mode được khóa khi Hunt chạy. Stop mới cho phép đổi mode. Chuyển mode không xóa configured list hoặc detection snapshot.

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

## Quy Trình Mỗi Session

1. Nạp `00-global-rules.md` và đúng một prompt theo thứ tự 01-19.
2. Kiểm tra dependency/preflight trước khi sửa.
3. Phút 00-20/25: production code và focused tests.
4. Phút 20/25-30: test, smoke và targeted repair.
5. Chỉ chạy session kế tiếp khi gate đạt.
6. Báo `PASSED`, `BLOCKED`, `UNVERIFIED`, `UNSUPPORTED` hoặc `REVERTED` kèm bằng chứng.
