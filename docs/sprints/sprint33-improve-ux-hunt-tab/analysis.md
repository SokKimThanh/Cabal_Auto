# Phân tích Hiện trạng Hệ thống Auto Hunt - MVC Architecture

## 1. Mục tiêu Tài liệu
Phân tích hiện trạng mã nguồn, sự phụ thuộc giữa giao diện (UI) và logic (Background Threads) của hệ thống săn quái tự động (Auto Hunt) để tìm ra nguyên nhân gây crash và đề xuất cơ sở thiết kế.

## 2. Bảng Đánh giá Bottlenecks & Nợ Kỹ thuật

Các điểm nghẽn và nợ kỹ thuật (tight coupling) chính được phát hiện trong mã nguồn:

| Component | Vấn đề cốt lõi | Vị trí (File) | Mức độ |
|---|---|---|---|
| `SkillPanel` | Giữ `combo_dropdowns` & `combo_hotkeys` gây phình to code (khoảng 270 dòng) và dư thừa logic tương thích ngược. Khó maintain. | `ui/panels/skill_panel.py:110-120` | HIGH |
| `TargetStatusPanel` | UI override hàm `tk.Label.config` và `hp_canvas.itemconfig` để lắng nghe sự kiện, dẫn đến race condition nếu thread nền chạy quá nhanh. | `ui/panels/target_status_panel.py:130-160` | HIGH |
| `HuntOrchestrator` | Gọi trực tiếp logic giả lập phím và chờ xử lý hình ảnh trong cùng một scope, có nguy cơ block thread của `CabalComboDetector`. | `lib/features/hunt/hunt_orchestrator.py` | HIGH |
| Luồng Drag&Drop Skill | Đứt gãy luồng UX. UI dùng Combobox tĩnh thay vì Grid List → Timeline. Không hỗ trợ cập nhật danh sách Available Skills real-time. | `ui/panels/skill_panel.py` | MEDIUM |
| Python GIL & Threading | `VisionEngine` và Giao diện UI đều chạy chung trên 1 process Python (với Thread). Việc quét khung hình >30fps sẽ khiến UI bị đơ (frozen) hoặc lag (khoảng 40% CPU usage cho UI). | Toàn hệ thống | CRITICAL |

## 3. Kiến trúc Luồng Dữ liệu Hiện tại (Pipeline As-Is)

Hiện tại hệ thống hoạt động thông qua các Pipeline bất đồng bộ đa luồng (Multi-threading), nhưng gặp vấn đề về đồng bộ dữ liệu:

1. **Scan (Chụp màn hình) → ROI:**
   - Worker chạy ngầm trích xuất khung hình game ở tốc độ ~30-60 FPS (tùy cấu hình).
2. **Nhận diện (Vision Engine):**
   - Các class `TargetBarDetector`, `TargetNameReader` phân tích numpy frame (chạy trên thread nền).
3. **Target (Trạng thái Mục tiêu):**
   - Cấu trúc `TargetInfo` (name, level, hp, mp) được bắn qua `EventBus` (ví dụ `TargetHpUpdatedEvent`).
4. **Combat & Combo (Tấn công & Chuỗi kỹ năng):**
   - `HuntOrchestrator` (chạy trên thread Background) quản lý chiến đấu.
   - `CabalComboDetector` theo dõi vùng sáng (Sweet spot ~0.78 tỉ lệ ngang combo bar). Khi chạm mốc này, nó trigger hàm callback `do_press()`.
   - Hàm callback `do_press()` gửi lệnh giả lập phím Z (Auto Target) và phím kỹ năng.
5. **Thống kê (Analytics):**
   - Log số lần cast skill và tính tỉ lệ thành công (bắn event `SkillStatsUpdatedEvent`).

## 4. Các vấn đề kỹ thuật khác cần lưu ý

1. **Python GIL:** Khóa toàn cục của Python khiến đa luồng (threading) không đem lại hiệu năng tính toán song song thực sự. Xử lý ảnh (OpenCV) và Render UI (Tkinter) sẽ tranh chấp GIL nếu không cẩn thận.
2. **Threading Model:** UI chạy ở Main Thread, toàn bộ Hunt/Vision chạy ở Worker Threads. Bất kỳ hàm nào cập nhật giao diện không dùng `after` đều có rủi ro văng (crash) `_tkinter.TclError`.
3. **MagicMock trong code chính:** Sự hiện diện của Dummy/Mock objects trong logic setup hoặc UI Wrapper là một dạng nợ kỹ thuật trầm trọng.
4. **Auto-target:** Hệ thống cần chủ động mô phỏng phím 'Z' (khóa mục tiêu) ngay khi target chết thay vì chờ game tự chuyển (do game không tự chuyển mục tiêu). Phím này phải cấu hình được qua `hunt_cfg`.
