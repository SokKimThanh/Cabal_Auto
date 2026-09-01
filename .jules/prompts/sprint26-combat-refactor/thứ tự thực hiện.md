# LỘ TRÌNH THỰC HIỆN DỰ ÁN CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 15 PHIÊN)

**Tiêu chuẩn kiến trúc:** Four-Zone Command Center Architecture & Data-Driven Combat Engine
**Quy chuẩn thời gian:** Timebox nghiêm ngặt 20–30 phút / micro-session (Minute 20/25: Stop & Validation, Minute 25–30: Targeted Repair / Revert)

---

## ⚠ Ghi chú trước khi bắt đầu

1. **Về thứ tự `PROMPT-CB4`:** Bản gốc của lộ trình này xếp `PROMPT-CB4` (chuẩn hóa schema `skill_slots`/`buff_slots`/`monster_rotation`, `config_migrator.py`, backup `.bak`, atomic write) ở vị trí 11, sau cả `UX3` và `UX4.2`. Tuy nhiên nội dung chi tiết của `UX3` và `UX4.2` đều giả định hạ tầng schema/migrator của `CB4` **đã tồn tại từ trước** để tái sử dụng (không tạo luồng migration song song). Bản chỉnh sửa dưới đây **chuyển `CB4` lên vị trí 08**, ngay sau `CB2B`, và dời `UX3`/`UX4.1`/`UX4.2` xuống một bậc.
2. **Về `PROMPT-CB3` và `PROMPT-CB3B`:** Hai mã này không có mặt trong danh sách 15 phiên chuẩn hóa. Điều này phù hợp với nhận định rằng `CB3B` (Dual-Lane Skill Config) đã được thay thế bởi `UX4.1`/`UX4.2`, và `CB4A` (Target Card + HP Visualizer, cũng không có mặt) đã được thay thế bởi `UX5.1`/`UX5.2`. Riêng `CB3` (Fast-Break Skill Casting gốc, nền tảng cho `CB3C` ở vị trí 13) cần được **xác nhận đã hoàn thành ở một sprint trước đó**, ngoài phạm vi 15 phiên này — nếu chưa, cần bổ sung một phiên `CB3` trước `CB3C`.
3. **Về quan hệ với `00-global-rules.md`:** Mục I bên dưới chỉ là các nguyên tắc kiến trúc/UI chung cấp cao. Các quy tắc chiến đấu/vision cụ thể (Target Key Logic, khoảng polling Fast-Break, thread-safety cho Screen Capture buffer) và yêu cầu Database Synchronization cho i18n nằm trong `00-global-rules.md` riêng, **vẫn phải dán kèm mỗi phiên theo đúng Mục IV bên dưới** — 6 mục trong file này không thay thế cho `00-global-rules.md`.

---

## I. NGUYÊN TẮC VÀ QUY TẮC BẮT BUỘC (GLOBAL RULES — cấp kiến trúc/UI chung)

1. **Quy tắc Rollback:** Nếu bài kiểm tra (Smoke Test / Unit Test) thất bại ở phút 30, hoàn tác ngay thay đổi của session bằng patch có rà soát, không dùng lệnh hủy diện rộng (`git reset --hard` hay `git checkout -- .`).
2. **An toàn Giao diện (Main Thread Safety):** Tuyệt đối không gọi các phương thức Tkinter trực tiếp từ luồng nền (Worker/Service); toàn bộ cập nhật UI bắt buộc phải bọc qua `schedule_ui_task()` hoặc `self.after(0, ...)`.
3. **Bảng màu & Kiểu dáng (UIStyle Tokens):** Sử dụng chuẩn Semantic Tokens từ `UIStyle` (xanh lá `Ready`/`Start`, đỏ `Danger`/`Stop`, cam `Warning`, xám `Neutral`), không thêm mã màu hex tùy tiện vào view.
4. **Độ phân giải & DPI Scaling (100% – 200%):** Bố cục chuẩn 1920 × 1080 (fallback tối thiểu 1280 × 720), kích hoạt DPI Awareness, sử dụng `grid()`, `weight`, `minsize` và tính toán tọa độ tương đối.
5. **Nguồn Dữ liệu Thực tế:** Kết hợp hai tầng tra cứu giữa CSDL SQLite `monsters.db` (3,948 quái) và fallback an toàn sang `lib/data/monsters.json`.
6. **Đa Ngôn Ngữ (i18n):** Toàn bộ nhãn, nút bấm, thông báo lỗi phải đăng ký đầy đủ key song ngữ `vi` và `en` trong `GLOBAL_TRANSLATIONS` (yêu cầu đồng bộ thêm vào DB — xem `00-global-rules.md`).

---

## II. BẢNG THỨ TỰ THỰC THI CHI TIẾT 15 PHIÊN (STEP-BY-STEP EXECUTION ORDER — ĐÃ SẮP XẾP LẠI)

| Thứ tự | Mã Prompt | Phân loại | Tên nhiệm vụ & Mục tiêu kỹ thuật | Thời gian | Phụ thuộc (Dependencies) |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | `PROMPT-UX1` | Phase UX | **Quick Action Bar (Vùng A):** Gộp Header thành thanh 80px; chuẩn hóa Window Selector, nút Refresh, Widget kiểm tra Bounds readiness kèm logic khôi phục Minimize (-32000), nút Start/Stop Debounce và i18n động. | 20–25 phút | `lib/features/hunt/window_selection_service.py` |
| **02** | `PROMPT-UX2` | Phase UX | **Core Grid Shell:** Tạo container `main_shell` bằng `pack()`, chia 4 vùng (A, B, C1, C2/D) bằng `grid()` với weight/minsize tường minh; cơ chế View Swapping tráo frame không làm mất state. | 25–30 phút | `PROMPT-UX1` |
| **03** | `PROMPT-UX6` | Phase UX | **Collapsible Bottom Logs (Vùng C2/D):** Tạo khung nhật ký 1640 × 200 px có nút thu gọn/mở rộng `[▲]/[▼]`, Circular Buffer giới hạn 1000 dòng (cả tầng hiển thị lẫn hàng đợi) chống tràn RAM, Batch Insert (50 dòng/tick) và ghi file log xoay vòng. | 20–25 phút | `PROMPT-UX2`, `lib/system/hunt_logger.py` |
| **04** | `PROMPT-CB5` | Phase Combat | **Window Scanner & ScreenCapture Fix:** Sửa lỗi crash `info.get('style')` khi duyệt `WindowInfo` và thêm bộ đệm `get_latest_frame()` chống tràn bộ nhớ GDI, kèm lock bảo vệ buffer. | 20–25 phút | `lib/features/hunt/scanner.py`, `lib/system/screen_capture.py` |
| **05** | `PROMPT-CB1` | Phase Combat | **Target Bar Health Detector:** Tạo `lib/vision/target_bar_detector.py` đọc vùng ROI thanh máu ở đỉnh màn hình để xác định trạng thái sống/chết chính xác. | 25–30 phút | `lib/system/screen_capture.py` |
| **06** | `PROMPT-CB2` | Phase Combat | **Fix Hunt Orchestrator Loop:** Xóa lệnh spam phím `Z` khi đang đánh, loại bỏ điều kiện khóa cứng `attack_min_duration_sec`, chỉ tap khi ở search mode (không giữ nhánh tap riêng cho ALIVE→DEAD). | 25–30 phút | `PROMPT-CB1`, `lib/features/hunt/hunt_orchestrator.py` |
| **07** | `PROMPT-CB2B`| Phase Combat | **Target Name Reader & ID Resolver:** Cắt ROI tên quái trên thanh Target Bar, đọc bằng OCR nhanh và tra cứu CSDL `monsters.db` lấy ID #xxxx và Max HP. | 25–30 phút | `PROMPT-CB2`, `database.py` |
| **08** | `PROMPT-CB4` | Phase Combat | **Sync Config Schema (chuyển lên sớm hơn):** Chuẩn hóa và đồng bộ schema `skill_slots`, `buff_slots`, `monster_rotation` giữa `hunt_config.json`, `config_migrator.py` và `app_gui.py`, kèm `schema_version`, backup `.bak`, atomic write — dựng hạ tầng này **trước** khi UX3/UX4.2 cần tái sử dụng. | 20–25 phút | `PROMPT-CB2B`, `lib/features/hunt/hunt_config.py` |
| **09** | `PROMPT-UX3` | Phase UX | **Dynamic Monster Rotation Queue (Vùng B - Trái):** Tái cấu trúc Panel trái 776 × 552 px thành hàng đợi động theo đúng schema `monster_rotation` đã có từ CB4; phân biệt trực quan quái thật vs quái fallback, hiển thị khoảng cách (rate-limit 5 FPS) và Debounced JSON sync (atomic write). | 25–30 phút | `PROMPT-CB4`, `PROMPT-CB2B` |
| **10** | `PROMPT-UX4.1` | Phase UX | **Dual-Lane Skill Strip Layout (Vùng B - Dưới):** Dựng khung dải kỹ năng 1576 × 120 px chia 2 làn (Combo Chain & Buff Lane), Compact Cards với huy hiệu `⚡ <cast>s` và `⏳ <cd>s`, bộ điều khiển Auto Combo. Chỉ tầng UI, dùng field name theo schema `skill_slots`/`buff_slots` đã có từ CB4. | 20–25 phút | `PROMPT-UX2`, `PROMPT-CB4` |
| **11** | `PROMPT-UX4.2` | Phase UX | **Smart Routing, Conflict & Migration:** Logic điều hướng 2 chiều thông minh kèm Debounced Toast, cảnh báo mềm khi trùng phím tắt (Hover Tooltip, bao gồm cả `combo_start_key`), bổ sung rule vào `config_migrator.py` đã có từ CB4 (không tạo luồng migration song song). | 25–30 phút | `PROMPT-UX4.1`, `PROMPT-CB4`, `lib/features/skills/runtime.py` |
| **12** | `PROMPT-CB6` | Phase Combat | **Cabal Combo Bar Timing Detector:** Tạo `lib/features/combo/combo_timing_detector.py` quét cột điểm ảnh tại vùng 2 vạch thanh Combo Bar, tích hợp Cooldown Guard (có thể ngắt sớm khi target chết) chống double-press. | 25–30 phút | `PROMPT-CB5`, `lib/features/hunt/hunt_orchestrator.py` |
| **13** | `PROMPT-CB3C`| Phase Combat | **Fast-Break & Timing Harmonization:** Ngắt hoạt ảnh tung chiêu ngay khi quái chết (Target Bar tắt) để giữ chuỗi Combo 20+; phân định rõ chế độ Timing thường vs Timing Combo; `SkillRuntime` sở hữu duy nhất con trỏ rotation khi Combo Mode bật. | 25–30 phút | `PROMPT-CB6`, `lib/features/hunt/timing_calculator.py`, *(giả định `PROMPT-CB3` gốc đã hoàn thành — xem ghi chú đầu file)* |
| **14** | `PROMPT-UX5.1` | Phase UX | **Target Card Shell & Fallback Schema (Vùng B - Phải):** Dựng khung thẻ mục tiêu 776 × 552 px, adapter fallback toàn diện cho schema CSDL (tránh `KeyError`, kèm cờ `is_placeholder`), cơ chế giải phóng bộ nhớ Tkinter Image triệt để (một `Label` duy nhất, không churn loại widget). | 20–25 phút | `PROMPT-UX2`, `PROMPT-CB2B` |
| **15** | `PROMPT-UX5.2` | Phase UX | **Canvas Dynamic HP & Window Recovery:** Thanh máu Canvas Segmented Step-Fill, HP Throttling (trần cứng 10 FPS + ngưỡng delta 0.5%), Graceful Death Delay (200ms, có `after_cancel` chống race khi đổi mục tiêu nhanh) và bộ điều khiển khôi phục Minimize kèm Retry 3 bước bất đồng bộ (dùng chung logic với `UX1`). | 25–30 phút | `PROMPT-UX5.1`, `PROMPT-CB1` |

---

## III. SƠ ĐỒ LUỒNG PHỤ THUỘC (DEPENDENCY PIPELINE — ĐÃ CẬP NHẬT)

```text
[BƯỚC 1: DỰNG SHELL GIAO DIỆN 4 VÙNG NỀN TẢNG]
├── 01. PROMPT-UX1 (Quick Action Bar 80px & Recovery Bindings)
├── 02. PROMPT-UX2 (Khung lưới 4 vùng & View Swapping Stack)
└── 03. PROMPT-UX6 (Khung nhật ký Circular Buffer & Batch Insert)
│
▼
[BƯỚC 2: HẠ TẦNG LOGIC CHIẾN ĐẤU, NHẬN DIỆN CỐT LÕI & SCHEMA CẤU HÌNH]
├── 04. PROMPT-CB5 (Vá lỗi Scanner & Bộ đệm ScreenCapture)
├── 05. PROMPT-CB1 (Bộ đọc thanh máu Target Bar ROI)
├── 06. PROMPT-CB2 (Sửa vòng lặp săn, bỏ spam phím Z)
├── 07. PROMPT-CB2B (Đọc tên quái OCR & Ánh xạ ID SQLite 3948 quái)
└── 08. PROMPT-CB4 (Đồng bộ Schema cấu hình — CHUYỂN LÊN SỚM HƠN, làm nền cho Bước 3)
│
▼
[BƯỚC 3: GHÉP NỐI DỮ LIỆU VÀO VÙNG SĂN TRUNG TÂM (dùng schema đã có từ CB4)]
├── 09. PROMPT-UX3 (Bảng luân chuyển quái động theo schema monster_rotation của CB4)
├── 10. PROMPT-UX4.1 (Giao diện dải kỹ năng Dual-Lane Compact Cards)
└── 11. PROMPT-UX4.2 (Smart Routing 2 chiều, Soft Conflict & bổ sung rule vào migrator CB4)
│
▼
[BƯỚC 4: TỐI ƯU COMBO ENGINE & THẺ MỤC TIÊU THỜI GIAN THỰC]
├── 12. PROMPT-CB6 (Bắt nhịp vạch sáng thanh Combo Bar Cabal)
├── 13. PROMPT-CB3C (Cơ chế Fast-Break ngắt chiêu giữ chuỗi Combo — giả định CB3 gốc đã có)
├── 14. PROMPT-UX5.1 (Khung Thẻ mục tiêu, Schema Fallback & Zero-Leak Image)
└── 15. PROMPT-UX5.2 (Thanh máu Canvas Step-Fill, HP Throttling & Minimize Recovery)
```

---

## IV. QUY TRÌNH TIẾN HÀNH MỖI PHIÊN LÀM VIỆC (WORKFLOW CHECKLIST)

1. **Chuẩn bị:** Mở AI Assistant trong môi trường phát triển (Cursor / VS Code).
2. **Nạp Ngữ cảnh Nền tảng:** Dán khối quy tắc chung `00-global-rules.md` (bắt buộc — chứa các quy tắc chiến đấu/vision/thread-safety cụ thể không lặp lại ở Mục I của file này).
3. **Nạp Nhiệm vụ Phiên:** Dán tiếp nội dung file `PROMPT-xxx` tương ứng theo đúng thứ tự **đã sắp xếp lại** từ **01 đến 15** ở Mục II.
4. **Triển khai Mã nguồn (Phút 00 – 20/25):** Thực hiện viết mã nguồn và Unit Tests tương ứng.
5. **Đánh giá & Thử nghiệm (Phút 20/25 – 30):** Chạy kiểm thử tự động (Pytest / Smoke Test / High-DPI Test).
6. **Nghiệm thu (Gate Check):** Nếu toàn bộ tiêu chí tại `Session Boundary Gate` đạt chuẩn, chuyển tiếp sang phiên tiếp theo.