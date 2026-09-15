# 🎮 Cabal Auto Hunt (Windows)

Hệ thống tự động hóa thông minh dành cho Cabal VTC Origin, được phát triển bằng Python với giao diện UI/UX trực quan. Dự án áp dụng các pattern kiến trúc phần mềm hiện đại nhằm đảm bảo hiệu năng cao, dễ bảo trì và khả năng mở rộng.

## ⭐ Chức năng chính

- 🎯 **Nhận diện hình ảnh thông minh (OpenCV):** Sử dụng Template Matching để tự động tìm và khóa mục tiêu (quái vật) với độ chính xác cao.
- 🛡️ **Hệ thống Auto-Casting & Auto-Buff:** Tự động thi triển kỹ năng chiến đấu theo chuỗi (rotation) và tự động làm mới buff trước khi hết hiệu ứng.
- 📚 **Quản lý Thư viện Tập trung:** Cho phép người dùng quản lý dữ liệu quái vật, kỹ năng và tính toán thời gian (timing) tối ưu ngay trên giao diện UI.
- ⌨️ **Global Hotkeys:** Điều khiển hệ thống (Start/Stop, mở UI) bằng phím tắt toàn cục ngay cả khi ứng dụng bị ẩn.
- 🪟 **Tự động nhận diện cửa sổ:** Tự động phát hiện và gắn kết vào cửa sổ game Cabal một cách an toàn.

## 🏗️ Cấu tạo & Mô hình hệ thống

Hệ thống được thiết kế theo hướng module hóa, phân tách rõ ràng giữa giao diện người dùng và logic xử lý nghiệp vụ:

- **1. Kiến trúc MVC & Event-Driven (EventBus):**
  - Giao diện (View) hoàn toàn tách biệt khỏi Logic nghiệp vụ (Controller/Service).
  - Các thành phần giao tiếp với nhau thông qua `EventBus` (ví dụ: phát sự kiện `MonsterRotationUpdatedEvent` khi có thay đổi), giúp loại bỏ sự phụ thuộc chéo (tight coupling) và dễ dàng quản lý luồng hoạt động.
- **2. Dependency Injection (DI):**
  - Sử dụng `AppContainer` để khởi tạo và quản lý toàn bộ các Service cốt lõi lúc khởi động.
  - Lớp `App` đóng vai trò là bootstrapper khởi động ứng dụng, không chứa logic nghiệp vụ (xóa bỏ mô hình God Class).
- **3. Quản lý trạng thái (State Management):**
  - `AppStateController` hoạt động như một kho lưu trữ dữ liệu trung tâm (Single Source of Truth) kết nối với UI.
  - Logic xử lý chi tiết được giao phó cho các Controllers chuyên biệt như `HuntConfigController`, `SkillPresetController`, và `MonsterRotationController`.
- **4. Xử lý Đa luồng (Multi-threading & Scheduling):**
  - Hệ thống `TaskScheduler` quản lý các tác vụ UI (Tkinter) và timers một cách mượt mà.
  - Vòng lặp săn quái (`HuntOrchestrator`) chạy trên luồng nền (background thread), tương tác qua callbacks và events để không làm đóng băng giao diện chính.
  - Các tương tác thao tác phím chuột vật lý được quản lý riêng bởi `SkillCasterService`.

## 🚀 Cài đặt & Sử dụng nhanh

**Yêu cầu hệ thống:** Windows 10/11, Python 3.10+ (cài sẵn OpenCV, Numpy, PyAutoGUI, Keyboard).

**1. Clone dự án & Cài đặt môi trường:**
```powershell
git clone https://github.com/SokKimThanh/Cabal_Auto.git
cd Cabal_Auto
py -3.10 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**2. Khởi động ứng dụng:**
- **Cách nhanh nhất:** Chạy file `run.bat` ở thư mục gốc.
- **Bằng PowerShell:** `.\scripts\launchers\run_venv.ps1`
- **Bằng Python:** `python app_gui.py`

*(Ở lần chạy đầu tiên, **Setup Wizard** sẽ tự động mở lên để hướng dẫn bạn thiết lập cơ bản)*

## 📚 Tài liệu chi tiết

Để giữ cho tài liệu README ngắn gọn, các tài liệu hướng dẫn sâu hơn, cấu trúc chi tiết, báo cáo sprint đã được chuyển vào thư mục `docs/`.

- 📖 **[Trang chủ Tài liệu (Docs Index)](docs/INDEX.md)** - Xem toàn bộ hướng dẫn, kiến trúc và thiết kế.
- 👋 **[Hướng dẫn cho Người mới](docs/guides/HUONG_DAN_NGUOI_MOI.md)** - Cẩm nang 5 bước thiết lập.
- 🧩 **[Cấu trúc thư mục (Project Structure)](PROJECT_STRUCTURE.md)** - Mô tả tổ chức mã nguồn.
