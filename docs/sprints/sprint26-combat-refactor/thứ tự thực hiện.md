# LỘ TRÌNH THỰC HIỆN DỰ ÁN CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 16 PHIÊN)

**Tiêu chuẩn kiến trúc:** Four-Zone Command Center Architecture & Data-Driven Combat Engine  
**Quy chuẩn thời gian:** 20-30 phút/micro-session; phút 20/25 dừng để validation, phút 25-30 chỉ targeted repair hoặc revert.

---

## Ghi Chú Trước Khi Bắt Đầu

1. `PROMPT-CB4` phải chạy ở vị trí 08, trước UX3/UX4.2, vì các prompt UI này phụ thuộc schema canonical và không được tạo migration song song.
2. `PROMPT-CB3` và `PROMPT-CB3B` không nằm trong 16 phiên. CB3B được thay thế bởi UX4.1/UX4.2; CB3 gốc phải được xác nhận đã hoàn tất trước CB3C.
3. CB4A không nằm trong chuỗi chuẩn hóa và được thay thế bởi UX5.1/UX5.2. Prompt trước UX5 không được giả định `get_target_monster_info()` hoặc `is_placeholder` đã tồn tại.
4. `PROMPT-CB2C` nối danh sách `monster_rotation` của UX3 với target OCR/DB của CB2B. Đây là gate bảo đảm Orchestrator chỉ đánh đúng quái đang được yêu cầu.
5. `00-global-rules.md` vẫn phải được nạp kèm mỗi session; các nguyên tắc dưới đây không thay thế quy tắc combat/vision/thread-safety chi tiết.

---

## I. Nguyên Tắc Bắt Buộc

1. **Rollback:** Nếu test thất bại ở phút 30, hoàn tác bằng patch có rà soát; không dùng reset/checkout hủy diện rộng.
2. **Main Thread Safety:** Worker/service không gọi Tkinter trực tiếp; mọi UI update đi qua `schedule_ui_task()` hoặc `after(0, ...)`.
3. **UIStyle:** Dùng token thực tế trong `UIStyle`; không thêm mã màu tùy tiện hoặc tham chiếu token chưa tồn tại.
4. **Responsive:** Hỗ trợ tối thiểu 1366x768 và DPI 100%-200%; không ép kích thước panel cố định lớn hơn workspace.
5. **Dữ liệu:** SQLite `monsters.db` là nguồn metadata chính; fallback JSON chỉ dùng khi contract session quy định rõ.
6. **I18n:** Nhãn/nút/thông báo có key `vi`/`en` trong `GLOBAL_TRANSLATIONS` và tuân thủ yêu cầu đồng bộ DB trong global rules.
7. **Một nguồn sự thật:** Không duy trì đồng thời hai schema, hai pointer runtime hoặc hai đường ghi config cho cùng hành vi.

---

## II. Thứ Tự Thực Thi 16 Phiên

| Thứ tự | Mã Prompt | Phase | Mục tiêu | Timebox | Phụ thuộc |
| :---: | --- | --- | --- | :---: | --- |
| **01** | `PROMPT-UX1` | UX | Quick Action Bar: Window Selector, Refresh, Bounds readiness, Start/Stop debounce và i18n. | 20-25 | Window selection service |
| **02** | `PROMPT-UX2` | UX | Core Grid Shell và view swapping không mất state. | 25-30 | UX1 |
| **03** | `PROMPT-UX6` | UX | Activity log buffer/batch/file logging theo kiến trúc UI hiện hành. | 20-25 | UX2, HuntLogger |
| **04** | `PROMPT-CB5` | Combat | Window Scanner và ScreenCapture buffer an toàn. | 20-25 | Scanner, ScreenCapture |
| **05** | `PROMPT-CB1` | Combat | Target Bar alive/dead detector và HP percentage. | 25-30 | ScreenCapture |
| **06** | `PROMPT-CB2` | Combat | Sửa HuntOrchestrator loop, không spam target key trong attack mode. | 25-30 | CB1 |
| **07** | `PROMPT-CB2B` | Combat | OCR tên target, resolve ID/HP qua SQLite và cache kết quả. | 25-30 | CB2, database.py |
| **08** | `PROMPT-CB4` | Combat | Chuẩn hóa `skill_slots`, `buff_slots`, `monster_rotation`, migration và atomic save. | 20-25 | CB2B, hunt_config.py |
| **09** | `PROMPT-UX3` | UX | Configured Monster Rotation Queue: add/remove/reorder, metadata DB và Apply All. | 25-30 | CB4, CB2B |
| **10** | `PROMPT-CB2C` | Combat | So khớp desired monster ID với target OCR/DB; chỉ attack khi match và advance rotation sau completion gate. | 25-30 | CB1, CB2, CB2B, CB4, UX3 |
| **11** | `PROMPT-UX4.1` | UX | Dual-Lane Skill Strip cho combo và buff. | 20-25 | UX2, CB4 |
| **12** | `PROMPT-UX4.2` | UX | Smart routing, conflict warning và migration bổ sung. | 25-30 | UX4.1, CB4, SkillRuntime |
| **13** | `PROMPT-CB6` | Combat | Combo Bar timing detector và cooldown guard. | 25-30 | CB5, HuntOrchestrator |
| **14** | `PROMPT-CB3C` | Combat | Fast-Break và timing harmonization; SkillRuntime sở hữu skill pointer. | 25-30 | CB6, CB2C, CB3 gốc |
| **15** | `PROMPT-UX5.1` | UX | Active Target Card shell, fallback schema và image lifecycle. | 20-25 | UX2, CB2B |
| **16** | `PROMPT-UX5.2` | UX | Dynamic HP Canvas, throttling và window recovery. | 20-25 | UX5.1, CB1 |

---

## III. Luồng Phụ Thuộc

```text
[BƯỚC 1: SHELL VÀ UI NỀN]
01 UX1 -> 02 UX2 -> 03 UX6

[BƯỚC 2: CAPTURE, NHẬN DIỆN VÀ SCHEMA]
04 CB5 -> 05 CB1 -> 06 CB2 -> 07 CB2B -> 08 CB4

[BƯỚC 3: DANH SÁCH QUÁI VÀ ĐIỀU PHỐI ĐÁNH ĐÚNG TARGET]
08 CB4 -> 09 UX3 -> 10 CB2C
                  \-> configured monster_rotation
07 CB2B ----------> OCR/DB resolved target
05 CB1 -----------> alive/death confirmation
10 CB2C ----------> gate search -> attack

[BƯỚC 4: SKILL, COMBO VÀ TARGET CARD]
11 UX4.1 -> 12 UX4.2
13 CB6 -> 14 CB3C
15 UX5.1 -> 16 UX5.2
```

Luồng chức năng trọng tâm sau Session 10:

```text
UX3 monster_rotation
-> CB2C chọn desired monster
-> CB2 tap target_key trong search mode
-> CB1 xác nhận target bar alive
-> CB2B OCR tên + resolve monster_id qua DB
-> CB2C MATCHED: cho phép attack
-> CB2C MISMATCH/UNKNOWN: không attack, tiếp tục cycle
-> completion gate: advance desired pointer
```

---

## IV. Quy Trình Mỗi Session

1. Mở AI Assistant trong workspace hiện tại.
2. Nạp `00-global-rules.md`.
3. Nạp đúng một `PROMPT-xxx` theo thứ tự 01-16.
4. Kiểm tra dependency gate trước khi sửa; nếu fail, báo `BLOCKED` và dừng.
5. Triển khai production code và focused tests trong phút 00-20/25.
6. Chạy test/smoke/DPI check trong phút 20/25-30.
7. Chỉ chuyển session tiếp theo khi Session Boundary Gate đạt.
8. Báo `PASSED`, `BLOCKED` hoặc `REVERTED` kèm lệnh test và kết quả.
