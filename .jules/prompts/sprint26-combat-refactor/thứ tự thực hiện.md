# LỘ TRÌNH THỰC HIỆN DỰ ÁN CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 15 PHIÊN)

**Tiêu chuẩn kiến trúc:** Four-Zone Command Center Architecture & Data-Driven Combat Engine  
**Quy chuẩn thời gian:** Timebox nghiêm ngặt 20–30 phút / micro-session (Minute 20/25: Stop & Validation, Minute 25–30: Targeted Repair / Revert)

---

## I. NGUYÊN TẮC VÀ QUY TẮC BẮT BUỘC (GLOBAL RULES)

1. **Quy tắc Rollback:** Nếu bài kiểm tra (Smoke Test / Unit Test) thất bại ở phút 30, hoàn tác ngay thay đổi của session bằng patch có rà soát, không dùng lệnh hủy diện rộng (`git reset --hard` hay `git checkout -- .`).
2. **An toàn Giao diện (Main Thread Safety):** Tuyệt đối không gọi các phương thức Tkinter trực tiếp từ luồng nền (Worker/Service); toàn bộ cập nhật UI bắt buộc phải bọc qua `schedule_ui_task()` hoặc `self.after(0, ...)`.
3. **Bảng màu & Kiểu dáng (UIStyle Tokens):** Sử dụng chuẩn Semantic Tokens từ `UIStyle` (xanh lá `Ready`/`Start`, đỏ `Danger`/`Stop`, cam `Warning`, xám `Neutral`), không thêm mã màu hex tùy tiện vào view.
4. **Độ phân giải & DPI Scaling (100% – 200%):** Bố cục chuẩn 1920 × 1080 (fallback tối thiểu 1280 × 720), kích hoạt DPI Awareness, sử dụng `grid()`, `weight`, `minsize` và tính toán tọa độ tương đối.
5. **Nguồn Dữ liệu Thực tế:** Kết hợp hai tầng tra cứu giữa CSDL SQLite `monsters.db` (3,948 quái) và fallback an toàn sang `lib/data/monsters.json`.
6. **Đa Ngôn Ngữ (i18n):** Toàn bộ nhãn, nút bấm, thông báo lỗi phải đăng ký đầy đủ key song ngữ `vi` và `en` trong `GLOBAL_TRANSLATIONS`.

---

## II. BẢNG THỨ TỰ THỰC THI CHI TIẾT 15 PHIÊN (STEP-BY-STEP EXECUTION ORDER)

| Thứ tự | Mã Prompt | Phân loại | Tên nhiệm vụ & Mục tiêu kỹ thuật | Thời gian | Phụ thuộc (Dependencies) |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | `PROMPT-UX1` | Phase UX | **Quick Action Bar (Vùng A):** Gộp Header thành thanh 80px; chuẩn hóa Window Selector, nút Refresh, Widget kiểm tra Bounds readiness kèm logic khôi phục Minimize (-32000), nút Start/Stop Debounce và i18n động. | 20–25 phút | `lib/features/hunt/window_selection_service.py` |
| **02** | `PROMPT-UX2` | Phase UX | **Core Grid Shell:** Tạo container `main_shell` bằng `pack()`, chia 4 vùng (A, B, C1, C2/D) bằng `grid()` với weight/minsize tường minh; cơ chế View Swapping tráo frame không làm mất state. | 25–30 phút | `PROMPT-UX1` |
| **03** | `PROMPT-UX6` | Phase UX | **Collapsible Bottom Logs (Vùng C2/D):** Tạo khung nhật ký 1640 × 200 px có nút thu gọn/mở rộng `[▲]/[▼]`, Circular Buffer giới hạn 1000 dòng chống tràn RAM, Batch Insert (50 dòng/tick) và ghi file log xoay vòng. | 20–25 phút | `PROMPT-UX2`, `lib/system/hunt_logger.py` |
| **04** | `PROMPT-CB5` | Phase Combat | **Window Scanner & ScreenCapture Fix:** Sửa lỗi crash `info.get('style')` khi duyệt `WindowInfo` và thêm bộ đệm `get_latest_frame()` chống tràn bộ nhớ GDI. | 20–25 phút | `lib/features/hunt/scanner.py`, `lib/system/screen_capture.py` |
| **05** | `PROMPT-CB1` | Phase Combat | **Target Bar Health Detector:** Tạo `lib/vision/target_bar_detector.py` đọc vùng ROI thanh máu ở đỉnh màn hình để xác định trạng thái sống/chết chính xác 100%. | 25–30 phút | `lib/system/screen_capture.py` |
| **06** | `PROMPT-CB2` | Phase Combat | **Fix Hunt Orchestrator Loop:** Xóa lệnh spam phím `Z` khi đang đánh, loại bỏ điều kiện khóa cứng `attack_min_duration_sec` để chấm dứt tình trạng chạy lung tung kéo quái. | 25–30 phút | `PROMPT-CB1`, `lib/features/hunt/hunt_orchestrator.py` |
| **07** | `PROMPT-CB2B`| Phase Combat | **Target Name Reader & ID Resolver:** Cắt ROI tên quái trên thanh Target Bar, đọc bằng OCR nhanh và tra cứu CSDL `monsters.db` lấy ID #xxxx và Max HP. | 25–30 phút | `PROMPT-CB2`, `database.py` |
| **08** | `PROMPT-UX3` | Phase UX | **Dynamic Monster Rotation Queue (Vùng B - Trái):** Tái cấu trúc Panel trái 776 × 552 px thành hàng đợi động; phân biệt trực quan quái thật vs quái fallback, hiển thị khoảng cách (rate-limit 5 FPS) và Debounced JSON sync. | 25–30 phút | `PROMPT-UX2`, `PROMPT-CB2B` |
| **09** | `PROMPT-UX4.1` | Phase UX | **Dual-Lane Skill Strip Layout (Vùng B - Dưới):** Dựng khung dải kỹ năng 1576 × 120 px chia 2 làn (Combo Chain & Buff Lane), Compact Cards với huy hiệu `⚡ <cast>s` và `⏳ <cd>s`, bộ điều khiển Auto Combo. | 20–25 phút | `PROMPT-UX2` |
| **10** | `PROMPT-UX4.2` | Phase UX | **Smart Routing, Conflict & Migration:** Logic điều hướng 2 chiều thông minh kèm Debounced Toast, cảnh báo mềm khi trùng phím tắt (Hover Tooltip), tự động migrate file config cũ/rác. | 25–30 phút | `PROMPT-UX4.1`, `lib/features/skills/runtime.py` |
| **11** | `PROMPT-CB4` | Phase Combat | **Sync Config Schema:** Chuẩn hóa và đồng bộ schema `skill_slots`, `buff_slots`, `monster_rotation` giữa `hunt_config.json`, `config_migrator.py` và `app_gui.py`. | 20–25 phút | `PROMPT-UX4.2`, `lib/features/hunt/hunt_config.py` |
| **12** | `PROMPT-CB6` | Phase Combat | **Cabal Combo Bar Timing Detector:** Tạo `lib/features/combo/combo_timing_detector.py` quét cột điểm ảnh tại vùng 2 vạch thanh Combo Bar, tích hợp Cooldown Guard chống double-press. | 25–30 phút | `PROMPT-CB5`, `lib/features/hunt/hunt_orchestrator.py` |
| **13** | `PROMPT-CB3C`| Phase Combat | **Fast-Break & Timing Harmonization:** Ngắt hoạt ảnh tung chiêu ngay khi quái chết (Target Bar tắt) để giữ chuỗi Combo 20+; phân định rõ chế độ Timing thường vs Timing Combo. | 25–30 phút | `PROMPT-CB6`, `lib/features/hunt/timing_calculator.py` |
| **14** | `PROMPT-UX5.1` | Phase UX | **Target Card Shell & Fallback Schema (Vùng B - Phải):** Dựng khung thẻ mục tiêu 776 × 552 px, adapter fallback toàn diện cho schema CSDL (tránh `KeyError`), cơ chế giải phóng bộ nhớ Tkinter Image triệt để. | 20–25 phút | `PROMPT-UX2`, `PROMPT-CB2B` |
| **15** | `PROMPT-UX5.2` | Phase UX | **Canvas Dynamic HP & Window Recovery:** Thanh máu Canvas Segmented Step-Fill, HP Throttling (10 FPS), Graceful Death Delay (200ms) và bộ điều khiển khôi phục Minimize kèm Retry 3 bước. | 25–30 phút | `PROMPT-UX5.1`, `PROMPT-CB1` |

---

## III. SƠ ĐỒ LUỒNG PHỤ THUỘC (DEPENDENCY PIPELINE)

```text
[BƯỚC 1: DỰNG SHELL GIAO DIỆN 4 VÙNG NỀN TẢNG]
├── 01. PROMPT-UX1 (Quick Action Bar 80px & Recovery Bindings)
├── 02. PROMPT-UX2 (Khung lưới 4 vùng & View Swapping Stack)
└── 03. PROMPT-UX6 (Khung nhật ký Circular Buffer & Batch Insert)
│
▼
[BƯỚC 2: HẠ TẦNG LOGIC CHIẾN ĐẤU & NHẬN DIỆN CỐT LÕI]
├── 04. PROMPT-CB5 (Vá lỗi Scanner & Bộ đệm ScreenCapture)
├── 05. PROMPT-CB1 (Bộ đọc thanh máu Target Bar ROI)
├── 06. PROMPT-CB2 (Sửa vòng lặp săn, bỏ spam phím Z)
└── 07. PROMPT-CB2B (Đọc tên quái OCR & Ánh xạ ID SQLite 3948 quái)
│
▼
[BƯỚC 3: GHÉP NỐI DỮ LIỆU VÀO VÙNG SĂN TRUNG TÂM]
├── 08. PROMPT-UX3 (Bảng luân chuyển quái động theo ID CSDL)
├── 09. PROMPT-UX4.1 (Giao diện dải kỹ năng Dual-Lane Compact Cards)
├── 10. PROMPT-UX4.2 (Smart Routing 2 chiều, Soft Conflict & JSON Migration)
└── 11. PROMPT-CB4 (Đồng bộ Schema cấu hình hunt_config.json)
│
▼
[BƯỚC 4: TỐI ƯU COMBO ENGINE & THẺ MỤC TIÊU THỜI GIAN THỰC]
├── 12. PROMPT-CB6 (Bắt nhịp vạch sáng thanh Combo Bar Cabal)
├── 13. PROMPT-CB3C (Cơ chế Fast-Break ngắt chiêu giữ chuỗi Combo)
├── 14. PROMPT-UX5.1 (Khung Thẻ mục tiêu, Schema Fallback & Zero-Leak Image)
└── 15. PROMPT-UX5.2 (Thanh máu Canvas Step-Fill, HP Throttling & Minimize Recovery)
```

---

## IV. QUY TRÌNH TIẾN HÀNH MỖI PHIÊN LÀM VIỆC (WORKFLOW CHECKLIST)

1. **Chuẩn bị:** Mở AI Assistant trong môi trường phát triển (Cursor / VS Code).
2. **Nạp Ngữ cảnh Nền tảng:** Dán khối quy tắc chung `00-global-rules.md`.
3. **Nạp Nhiệm vụ Phiên:** Dán tiếp nội dung file `PROMPT-xxx` tương ứng theo đúng thứ tự từ **01 đến 15**.
4. **Triển khai Mã nguồn (Phút 00 – 20/25):** Thực hiện viết mã nguồn và Unit Tests tương ứng.
5. **Đánh giá & Thử nghiệm (Phút 20/25 – 30):** Chạy kiểm thử tự động (Pytest / Smoke Test / High-DPI Test).
6. **Nghiệm thu (Gate Check):** Nếu toàn bộ tiêu chí tại `Session Boundary Gate` đạt chuẩn, chuyển tiếp sang phiên tiếp theo.# LỘ TRÌNH THỰC HIỆN DỰ ÁN CABAL AUTO HUNT ASSISTANT (CHUẨN HÓA 15 PHIÊN)

**Tiêu chuẩn kiến trúc:** Four-Zone Command Center Architecture & Data-Driven Combat Engine  
**Quy chuẩn thời gian:** Timebox nghiêm ngặt 20–30 phút / micro-session (Minute 20/25: Stop & Validation, Minute 25–30: Targeted Repair / Revert)

---

## I. NGUYÊN TẮC VÀ QUY TẮC BẮT BUỘC (GLOBAL RULES)

1. **Quy tắc Rollback:** Nếu bài kiểm tra (Smoke Test / Unit Test) thất bại ở phút 30, hoàn tác ngay thay đổi của session bằng patch có rà soát, không dùng lệnh hủy diện rộng (`git reset --hard` hay `git checkout -- .`).
2. **An toàn Giao diện (Main Thread Safety):** Tuyệt đối không gọi các phương thức Tkinter trực tiếp từ luồng nền (Worker/Service); toàn bộ cập nhật UI bắt buộc phải bọc qua `schedule_ui_task()` hoặc `self.after(0, ...)`.
3. **Bảng màu & Kiểu dáng (UIStyle Tokens):** Sử dụng chuẩn Semantic Tokens từ `UIStyle` (xanh lá `Ready`/`Start`, đỏ `Danger`/`Stop`, cam `Warning`, xám `Neutral`), không thêm mã màu hex tùy tiện vào view.
4. **Độ phân giải & DPI Scaling (100% – 200%):** Bố cục chuẩn 1920 × 1080 (fallback tối thiểu 1280 × 720), kích hoạt DPI Awareness, sử dụng `grid()`, `weight`, `minsize` và tính toán tọa độ tương đối.
5. **Nguồn Dữ liệu Thực tế:** Kết hợp hai tầng tra cứu giữa CSDL SQLite `monsters.db` (3,948 quái) và fallback an toàn sang `lib/data/monsters.json`.
6. **Đa Ngôn Ngữ (i18n):** Toàn bộ nhãn, nút bấm, thông báo lỗi phải đăng ký đầy đủ key song ngữ `vi` và `en` trong `GLOBAL_TRANSLATIONS`.

---

## II. BẢNG THỨ TỰ THỰC THI CHI TIẾT 15 PHIÊN (STEP-BY-STEP EXECUTION ORDER)

| Thứ tự | Mã Prompt | Phân loại | Tên nhiệm vụ & Mục tiêu kỹ thuật | Thời gian | Phụ thuộc (Dependencies) |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | `PROMPT-UX1` | Phase UX | **Quick Action Bar (Vùng A):** Gộp Header thành thanh 80px; chuẩn hóa Window Selector, nút Refresh, Widget kiểm tra Bounds readiness kèm logic khôi phục Minimize (-32000), nút Start/Stop Debounce và i18n động. | 20–25 phút | `lib/features/hunt/window_selection_service.py` |
| **02** | `PROMPT-UX2` | Phase UX | **Core Grid Shell:** Tạo container `main_shell` bằng `pack()`, chia 4 vùng (A, B, C1, C2/D) bằng `grid()` với weight/minsize tường minh; cơ chế View Swapping tráo frame không làm mất state. | 25–30 phút | `PROMPT-UX1` |
| **03** | `PROMPT-UX6` | Phase UX | **Collapsible Bottom Logs (Vùng C2/D):** Tạo khung nhật ký 1640 × 200 px có nút thu gọn/mở rộng `[▲]/[▼]`, Circular Buffer giới hạn 1000 dòng chống tràn RAM, Batch Insert (50 dòng/tick) và ghi file log xoay vòng. | 20–25 phút | `PROMPT-UX2`, `lib/system/hunt_logger.py` |
| **04** | `PROMPT-CB5` | Phase Combat | **Window Scanner & ScreenCapture Fix:** Sửa lỗi crash `info.get('style')` khi duyệt `WindowInfo` và thêm bộ đệm `get_latest_frame()` chống tràn bộ nhớ GDI. | 20–25 phút | `lib/features/hunt/scanner.py`, `lib/system/screen_capture.py` |
| **05** | `PROMPT-CB1` | Phase Combat | **Target Bar Health Detector:** Tạo `lib/vision/target_bar_detector.py` đọc vùng ROI thanh máu ở đỉnh màn hình để xác định trạng thái sống/chết chính xác 100%. | 25–30 phút | `lib/system/screen_capture.py` |
| **06** | `PROMPT-CB2` | Phase Combat | **Fix Hunt Orchestrator Loop:** Xóa lệnh spam phím `Z` khi đang đánh, loại bỏ điều kiện khóa cứng `attack_min_duration_sec` để chấm dứt tình trạng chạy lung tung kéo quái. | 25–30 phút | `PROMPT-CB1`, `lib/features/hunt/hunt_orchestrator.py` |
| **07** | `PROMPT-CB2B`| Phase Combat | **Target Name Reader & ID Resolver:** Cắt ROI tên quái trên thanh Target Bar, đọc bằng OCR nhanh và tra cứu CSDL `monsters.db` lấy ID #xxxx và Max HP. | 25–30 phút | `PROMPT-CB2`, `database.py` |
| **08** | `PROMPT-UX3` | Phase UX | **Dynamic Monster Rotation Queue (Vùng B - Trái):** Tái cấu trúc Panel trái 776 × 552 px thành hàng đợi động; phân biệt trực quan quái thật vs quái fallback, hiển thị khoảng cách (rate-limit 5 FPS) và Debounced JSON sync. | 25–30 phút | `PROMPT-UX2`, `PROMPT-CB2B` |
| **09** | `PROMPT-UX4.1` | Phase UX | **Dual-Lane Skill Strip Layout (Vùng B - Dưới):** Dựng khung dải kỹ năng 1576 × 120 px chia 2 làn (Combo Chain & Buff Lane), Compact Cards với huy hiệu `⚡ <cast>s` và `⏳ <cd>s`, bộ điều khiển Auto Combo. | 20–25 phút | `PROMPT-UX2` |
| **10** | `PROMPT-UX4.2` | Phase UX | **Smart Routing, Conflict & Migration:** Logic điều hướng 2 chiều thông minh kèm Debounced Toast, cảnh báo mềm khi trùng phím tắt (Hover Tooltip), tự động migrate file config cũ/rác. | 25–30 phút | `PROMPT-UX4.1`, `lib/features/skills/runtime.py` |
| **11** | `PROMPT-CB4` | Phase Combat | **Sync Config Schema:** Chuẩn hóa và đồng bộ schema `skill_slots`, `buff_slots`, `monster_rotation` giữa `hunt_config.json`, `config_migrator.py` và `app_gui.py`. | 20–25 phút | `PROMPT-UX4.2`, `lib/features/hunt/hunt_config.py` |
| **12** | `PROMPT-CB6` | Phase Combat | **Cabal Combo Bar Timing Detector:** Tạo `lib/features/combo/combo_timing_detector.py` quét cột điểm ảnh tại vùng 2 vạch thanh Combo Bar, tích hợp Cooldown Guard chống double-press. | 25–30 phút | `PROMPT-CB5`, `lib/features/hunt/hunt_orchestrator.py` |
| **13** | `PROMPT-CB3C`| Phase Combat | **Fast-Break & Timing Harmonization:** Ngắt hoạt ảnh tung chiêu ngay khi quái chết (Target Bar tắt) để giữ chuỗi Combo 20+; phân định rõ chế độ Timing thường vs Timing Combo. | 25–30 phút | `PROMPT-CB6`, `lib/features/hunt/timing_calculator.py` |
| **14** | `PROMPT-UX5.1` | Phase UX | **Target Card Shell & Fallback Schema (Vùng B - Phải):** Dựng khung thẻ mục tiêu 776 × 552 px, adapter fallback toàn diện cho schema CSDL (tránh `KeyError`), cơ chế giải phóng bộ nhớ Tkinter Image triệt để. | 20–25 phút | `PROMPT-UX2`, `PROMPT-CB2B` |
| **15** | `PROMPT-UX5.2` | Phase UX | **Canvas Dynamic HP & Window Recovery:** Thanh máu Canvas Segmented Step-Fill, HP Throttling (10 FPS), Graceful Death Delay (200ms) và bộ điều khiển khôi phục Minimize kèm Retry 3 bước. | 25–30 phút | `PROMPT-UX5.1`, `PROMPT-CB1` |

---

## III. SƠ ĐỒ LUỒNG PHỤ THUỘC (DEPENDENCY PIPELINE)

```text
[BƯỚC 1: DỰNG SHELL GIAO DIỆN 4 VÙNG NỀN TẢNG]
├── 01. PROMPT-UX1 (Quick Action Bar 80px & Recovery Bindings)
├── 02. PROMPT-UX2 (Khung lưới 4 vùng & View Swapping Stack)
└── 03. PROMPT-UX6 (Khung nhật ký Circular Buffer & Batch Insert)
│
▼
[BƯỚC 2: HẠ TẦNG LOGIC CHIẾN ĐẤU & NHẬN DIỆN CỐT LÕI]
├── 04. PROMPT-CB5 (Vá lỗi Scanner & Bộ đệm ScreenCapture)
├── 05. PROMPT-CB1 (Bộ đọc thanh máu Target Bar ROI)
├── 06. PROMPT-CB2 (Sửa vòng lặp săn, bỏ spam phím Z)
└── 07. PROMPT-CB2B (Đọc tên quái OCR & Ánh xạ ID SQLite 3948 quái)
│
▼
[BƯỚC 3: GHÉP NỐI DỮ LIỆU VÀO VÙNG SĂN TRUNG TÂM]
├── 08. PROMPT-UX3 (Bảng luân chuyển quái động theo ID CSDL)
├── 09. PROMPT-UX4.1 (Giao diện dải kỹ năng Dual-Lane Compact Cards)
├── 10. PROMPT-UX4.2 (Smart Routing 2 chiều, Soft Conflict & JSON Migration)
└── 11. PROMPT-CB4 (Đồng bộ Schema cấu hình hunt_config.json)
│
▼
[BƯỚC 4: TỐI ƯU COMBO ENGINE & THẺ MỤC TIÊU THỜI GIAN THỰC]
├── 12. PROMPT-CB6 (Bắt nhịp vạch sáng thanh Combo Bar Cabal)
├── 13. PROMPT-CB3C (Cơ chế Fast-Break ngắt chiêu giữ chuỗi Combo)
├── 14. PROMPT-UX5.1 (Khung Thẻ mục tiêu, Schema Fallback & Zero-Leak Image)
└── 15. PROMPT-UX5.2 (Thanh máu Canvas Step-Fill, HP Throttling & Minimize Recovery)
```

---

## IV. QUY TRÌNH TIẾN HÀNH MỖI PHIÊN LÀM VIỆC (WORKFLOW CHECKLIST)

1. **Chuẩn bị:** Mở AI Assistant trong môi trường phát triển (Cursor / VS Code).
2. **Nạp Ngữ cảnh Nền tảng:** Dán khối quy tắc chung `00-global-rules.md`.
3. **Nạp Nhiệm vụ Phiên:** Dán tiếp nội dung file `PROMPT-xxx` tương ứng theo đúng thứ tự từ **01 đến 15**.
4. **Triển khai Mã nguồn (Phút 00 – 20/25):** Thực hiện viết mã nguồn và Unit Tests tương ứng.
5. **Đánh giá & Thử nghiệm (Phút 20/25 – 30):** Chạy kiểm thử tự động (Pytest / Smoke Test / High-DPI Test).
6. **Nghiệm thu (Gate Check):** Nếu toàn bộ tiêu chí tại `Session Boundary Gate` đạt chuẩn, chuyển tiếp sang phiên tiếp theo.