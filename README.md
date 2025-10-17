# Cabal Auto (Windows)

Auto thao tác đơn giản cho Cabal VTC Origin bằng Python: click chuột định kỳ và điều khiển bằng hotkey an toàn. Có thể mở rộng nhận diện hình ảnh (OpenCV) ở môi trường Python phù hợp.

## Cấu trúc

- `main.py`: ví dụ click đơn giản (chạy vô hạn, không có hotkey an toàn) – KHÔNG khuyến nghị dùng.
- `main_safe.py`: phiên bản an toàn, có hotkey bật/tắt/tạm dừng/thoát, đọc cấu hình từ `config.json`.
- `config.json`: cấu hình toạ độ click, chu kỳ, và hotkey.
- `requirements.txt`: danh sách thư viện.
- `assets/images/`: nơi để ảnh nếu dùng nhận diện (hiện trống).

## Yêu cầu

- Windows
- Python (khuyến nghị 3.10/3.11 nếu cần OpenCV). Môi trường hiện tại là 3.14 nên OpenCV có thể chưa có wheel tương thích.
- Virtual environment tại `venv/`.

## Cài đặt thư viện

Trong PowerShell (Windows), kích hoạt môi trường rồi cài:

```powershell
# Kích hoạt môi trường ảo
E:\Cabal_Auto\venv\Scripts\Activate.ps1

# Cài đặt thư viện
pip install -r requirements.txt
```

Lưu ý: Ở môi trường Python 3.14, `opencv-python` có thể chưa cài được. Nếu cần OpenCV, tạo venv với Python 3.10/3.11 và cài lại.

## Cấu hình

Sửa `config.json`:

```json
{
  "click": { "x": 500, "y": 400, "interval_sec": 2.0 },
  "hotkeys": { "toggle": "f8", "exit": "f9" },
  "safety": { "failsafe": true, "pause_key": "f7" }
}
```

- `x, y`: toạ độ màn hình để click.
- `interval_sec`: khoảng cách giữa các lần click.
- `toggle`: bật/tắt vòng lặp.
- `pause_key`: tạm dừng.
- `exit`: thoát chương trình.
- `failsafe`: di chuyển chuột lên góc trên-trái (0,0) để ngắt khẩn cấp.

## Chạy

Chạy phiên bản an toàn:

```powershell
E:\Cabal_Auto\venv\Scripts\python.exe main_safe.py
```

Hotkeys mặc định:
- F8: bật/tắt
- F7: tạm dừng/tiếp tục
- F9: thoát

## Chạy giao diện (GUI)

Chạy ứng dụng GUI để nhập X, Y, interval và điều khiển Start/Stop:

```powershell
E:\Cabal_Auto\venv\Scripts\python.exe app_gui.py
```

Tuỳ chọn (kích hoạt venv rồi chạy):

```powershell
E:\Cabal_Auto\venv\Scripts\Activate.ps1
python app_gui.py
```

Nếu PowerShell chặn script khi kích hoạt venv, dùng lệnh tạm thời cho phiên làm việc hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
E:\Cabal_Auto\venv\Scripts\Activate.ps1
python app_gui.py
```

Lưu ý:
- Tkinter đã khả dụng trong venv hiện tại. Không cần quyền admin để chạy GUI.
- Khi nhấn Start, app sẽ click tại (X, Y) mỗi “Interval (s)”. Đưa chuột lên góc trên-trái (0,0) để FAILSAFE.

````markdown
# Cabal Auto (Windows)

Tự động săn quái cho Cabal VTC Origin bằng Python. Hỗ trợ GUI tab Săn quái: chọn cửa sổ game theo PID/HWND, nhận diện mục tiêu bằng ảnh mẫu, tự chuyển mục tiêu và đánh theo phím cấu hình. Có thể mở rộng nhận diện (OpenCV) ở môi trường Python phù hợp.

## Cấu trúc

- `app_gui.py`: giao diện điều khiển tab Săn quái (đã bỏ tab Click).
- `hunt_config.json`: cấu hình săn (tiêu đề/PID cửa sổ, phím target/attack, ảnh mẫu, vùng tìm kiếm, thời gian, bring-to-front).
- `auto_hunt.py`: script săn không GUI (tuỳ chọn), dùng cùng `hunt_config.json`.
- `win_input.py`: gửi phím ở mức thấp (SendInput) cho các script cần.
- `skills.json`, `main_skills.py`: ví dụ auto combo theo cooldown (tuỳ chọn).
- `config.json`: cấu hình chung (GUI, failsafe...).
- `requirements.txt`, `assets/images/`.
- `main.py`, `main_safe.py`: các ví dụ click (demo), không cần dùng cho săn.

## Yêu cầu

- Windows
- Python (khuyến nghị 3.10/3.11 nếu cần OpenCV). Python 3.14 có thể chưa có wheel `opencv-python`.
- Virtual environment tại `venv/`.

## Cài đặt thư viện

Trong PowerShell (Windows), kích hoạt môi trường rồi cài:

```powershell
# Kích hoạt môi trường ảo
E:\Cabal_Auto\venv\Scripts\Activate.ps1

# Cài đặt thư viện
pip install -r requirements.txt
```

Lưu ý: Ở Python 3.14, `opencv-python` có thể chưa cài được. Nếu cần OpenCV, dùng Python 3.10/3.11.

## Chạy giao diện (GUI)

```powershell
E:\Cabal_Auto\venv\Scripts\python.exe app_gui.py
```

Tuỳ chọn (kích hoạt venv rồi chạy):

```powershell
E:\Cabal_Auto\venv\Scripts\Activate.ps1
python app_gui.py
```

Nếu PowerShell chặn script khi kích hoạt venv, dùng lệnh tạm thời cho phiên hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
E:\Cabal_Auto\venv\Scripts\Activate.ps1
python app_gui.py
```

Lưu ý:
- Tkinter đã khả dụng trong venv. Không cần quyền admin để chạy GUI (nhưng nên chạy cùng quyền với game để focus foreground tốt hơn).
- GUI sẽ tự thu nhỏ khi chạy săn nếu game đã được focus; nhấn F9 để dừng (nếu có thư viện `keyboard`), hoặc Alt+Tab về GUI rồi bấm Dừng/ESC.

## Hướng dẫn tab Săn quái (GUI)

1) Tìm & chọn cửa sổ game:
- Nhập từ khoá (ví dụ "cabal") và bấm “Tìm cửa sổ”.
- Chọn dòng có tiêu đề + [PID]. Bấm “Đưa lên trước” để kiểm tra focus.

2) Thiết lập phím & thời gian:
- `Phím chọn mục tiêu` (target_key): mặc định `TAB`.
- `Phím đánh` (attack_keys): ví dụ `1,2,3` (phải là phím skill thật sự trong game).
- `Giữ phím (ms)`, `Chu kỳ đổi mục tiêu (s)`, `Chu kỳ tìm (s)`, `Chu kỳ đánh (s)`.

3) Ảnh mẫu & vùng tìm:
- Chọn ảnh template là khung target/HP để bot biết “đang có mục tiêu”.
- Nên giới hạn vùng tìm (Region) quanh khu vực khung target để nhanh và chính xác hơn.

4) Chạy & dừng:
- Bấm “Lưu cấu hình săn” rồi “Chạy săn”. Nếu focus thành công, GUI sẽ thu nhỏ để phím đi vào game.
- Dừng bằng F9 (nếu có `keyboard`) hoặc Alt+Tab về GUI rồi bấm “Dừng săn”/ESC.

### Cơ chế (search -> attack)

- Trạng thái `search`: chỉ bấm `target_key` theo `target_cycle_delay` cho đến khi nhận diện thấy template (`search_interval`).
- Trạng thái `attack`: spam `attack_keys` cho đến khi mất template quá `lost_timeout_sec` (mặc định ~0.8s), rồi quay lại `search`.
- Nhờ vậy bot không đổi mục tiêu liên tục khi đang tấn công.

### Gợi ý focus/foreground

- Ưu tiên focus theo HWND/PID. Nếu vẫn không mang lên trước:
  - Chạy GUI cùng quyền với game (Run as Administrator nếu game chạy Admin).
  - Dùng Borderless/Windowed thay vì fullscreen exclusive.
  - Một số anti-cheat có thể hạn chế SetForegroundWindow.

## Quyền và lưu ý

- Thư viện `keyboard` bắt global hotkey có thể yêu cầu chạy PowerShell/VS Code với quyền Administrator.
- `pyautogui.FAILSAFE` bật: đưa chuột tới góc trên-trái để dừng khẩn cấp.

## Nhận diện hình ảnh (tùy chọn)

Nếu cần dùng OpenCV:
1. Cài Python 3.10 hoặc 3.11.
2. Tạo venv mới và cài đặt lại:
   ```powershell
   py -3.11 -m venv venv
   E:\Cabal_Auto\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Thêm ảnh vào `assets/images/` và dùng `cv2`/`PIL`.

## Troubleshooting

- Game không bật lên trước/không nhận phím:
  - Chọn đúng PID và thử “Đưa lên trước”.
  - Chạy GUI as Admin như game.
  - Thử Borderless/Windowed.
- Chỉ đổi mục tiêu mà không đánh:
  - Kiểm tra `attack_keys` đúng phím skill.
  - Chọn template ổn định (ít nhấp nháy) và điều chỉnh `search_interval`, `lost_timeout_sec`.
- OpenCV không có ở Python 3.14:
  - Tạo venv Python 3.10/3.11 và `pip install opencv-python` để dùng `confidence` cho nhận diện ổn định hơn.

````
