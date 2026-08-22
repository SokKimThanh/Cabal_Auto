# Hướng Dẫn Thiết Lập Hotkey Toggle & Bring-to-Front Cho Cửa Sổ

**Ngày cập nhật:** 24/10/2025
**Đối tượng:** Người dùng muốn đưa nhanh cửa sổ ứng dụng lên trên cùng khi bị che (Tối ưu cho ADHD - Giảm xao nhãng và thao tác thừa)

---

## 💡 Tổng Quan & Nguyên Tắc Tối Ưu Cho Người ADHD

Khi làm việc hoặc chơi game, việc ứng dụng bị che bởi các cửa sổ khác (như trình duyệt, Discord, File Explorer) khiến bạn phải bấm `Alt + Tab` nhiều lần hoặc rà chuột tìm trên Taskbar. Thao tác rườm rà này dễ làm ngắt quãng sự tập trung (gây xao nhãng cho người ADHD).

**Giải pháp Toggle Hotkey 1-Phím:**
- **Lần 1 (Ứng dụng chưa mở):** Tự động khởi chạy ứng dụng.
- **Lần 2 (Ứng dụng đang mở nhưng bị che/thu nhỏ):** Tự động đưa cửa sổ ứng dụng lên trên cùng (Bring to Front) và Focus ngay lập tức.
- **Lần 3 (Nếu đang focus ứng dụng):** Giữ nguyên hoặc thu nhỏ (tùy chỉnh).

---

## ⌨️ Danh Sách Hotkey An Toàn (Không Xung Đột Hệ Thống)

Dưới đây là các tổ hợp phím khuyên dùng, đảm bảo **không bị trùng** với hotkey mặc định của hệ điều hành (như `Win+L`, `Win+D`, `Alt+Tab`, `Cmd+Tab`, `Cmd+Space`):

| Hệ điều hành | Hotkey Khuyên Dùng | Ý Nghĩa / Dễ Nhớ | Tránh Xung Đột Với |
|---|---|---|---|
| **Windows** | `Ctrl + Alt + W` hoặc `Win + Shift + W` | W = Window | `Win + L` (Khóa màn hình), `Win + D` (Desktop), `Alt + Tab` |
| **macOS** | `Cmd + Option + W` hoặc `Control + Option + W` | W = Window | `Cmd + Tab`, `Cmd + Space` (Spotlight), `Cmd + Option + Esc` |
| **Linux** | `Ctrl + Alt + W` hoặc `Super + Shift + W` | W = Window | `Super` (App Launcher), `Alt + Tab`, `Ctrl + Alt + T` |

---

## 🛠️ Script Mẫu & Hướng Dẫn Cấu Hình Cho Từng Hệ Điều Hành

### 1. Windows (Sử dụng AutoHotkey v2 - Khuyên dùng)

AutoHotkey (AHK) là công cụ nhẹ, phản hồi tức thì và cực kỳ hiệu quả trên Windows.

#### Các bước thực hiện:
1. Tải và cài đặt **AutoHotkey v2** từ [autohotkey.com](https://www.autohotkey.com/).
2. Nhấp chuột phải vào Desktop/Thư mục bất kỳ -> chọn **New** -> **AutoHotkey Script** (đặt tên là `WindowToggle.ahk`).
3. Nhấp chuột phải vào file `.ahk` -> chọn **Edit Script** và dán đoạn mã bên dưới:

```autohotkey
#Requires AutoHotkey v2.0

; Tổ hợp phím: Ctrl + Alt + W
^!w::
{
    ; Tên cửa sổ hoặc một phần tiêu đề cửa sổ cần đưa lên trên cùng
    targetTitle := "Cabal Auto Hunt"  ; Thay bằng tiêu đề cửa sổ của bạn

    ; Đường dẫn tới file thực thi ứng dụng (để khởi chạy nếu chưa mở)
    targetPath := "pythonw app_gui.py"  ; Hoặc đường dẫn file .exe / .bat

    if WinExist(targetTitle)
    {
        if WinActive(targetTitle)
        {
            ; Nếu đang ở trên cùng -> Ẩn xuống (Toggle hide)
            WinMinimize targetTitle
        }
        else
        {
            ; Nếu đang bị che hoặc thu nhỏ -> Đưa lên trên cùng và focus
            WinRestore targetTitle
            WinActivate targetTitle
        }
    }
    else
    {
        ; Nếu chưa mở -> Chạy ứng dụng
        Run targetPath
    }
}
```

4. Lưu file và double-click vào `WindowToggle.ahk` để chạy.
5. *(Tùy chọn)* Đưa file `.ahk` vào thư mục Startup (`Win + R` -> gõ `shell:startup`) để script tự chạy khi bật máy.

---

### 2. macOS (Sử dụng Ứng dụng Phím Tắt / Shortcuts mặc định)

Trên macOS, bạn không cần cài thêm phần mềm ngoài mà có thể dùng sẵn ứng dụng **Shortcuts (Phím tắt)** hoặc **AppleScript**.

#### Các bước thực hiện:
1. Mở ứng dụng **Shortcuts (Phím tắt)** trên Mac.
2. Bấm **+** (Tạo shortcut mới), chọn **Add Action (Thêm tác vụ)** -> Tìm và chọn **Run AppleScript**.
3. Dán đoạn mã AppleScript sau:

```applescript
on run {input, parameters}
    set appName to "Cabal Auto Hunt" -- Hoặc tên ứng dụng / terminal của bạn

    tell application "System Events"
        set isRunning to (exists (processes where name contains appName))
    end tell

    if isRunning then
        tell application appName
            reopen
            activate
        end tell
    else
        -- Thay đổi đường dẫn đến lệnh chạy app nếu chưa mở
        do shell script "cd /path/to/app && python3 app_gui.py > /dev/null 2>&1 &"
    end if

    return input
end run
```

4. Ở góc phải màn hình chỉnh sửa Shortcut -> Chọn tab **Shortcut Details (Chi tiết phím tắt)** -> Tích chọn **Use as Quick Action** và gán phím tắt `Cmd + Option + W`.
5. Bấm thử `Cmd + Option + W` để trải nghiệm.

---

### 3. Linux (Sử dụng `wmctrl` + `xdotool` & Custom Shortcut)

Trên Linux (Ubuntu, Debian, Fedora, Arch...), bạn có thể dùng công cụ điều khiển cửa sổ `wmctrl` và `xdotool`.

#### Các bước thực hiện:
1. Cài đặt `wmctrl` và `xdotool` (nếu chưa có):
   ```bash
   sudo apt update && sudo apt install wmctrl xdotool -y
   ```

2. Tạo script bash `toggle_window.sh`:
   ```bash
   #!/bin/bash
   WINDOW_NAME="Cabal Auto Hunt"
   CMD="python3 /path/to/app_gui.py"

   # Kiểm tra xem cửa sổ có đang tồn tại không
   if wmctrl -l | grep -i "$WINDOW_NAME" > /dev/null; then
       # Lấy tên cửa sổ đang active
       ACTIVE_WIN=$(xdotool getactivewindow getwindowname 2>/dev/null)

       if [[ "$ACTIVE_WIN" == *"$WINDOW_NAME"* ]]; then
           # Nếu đang focus -> Thu nhỏ
           wmctrl -r "$WINDOW_NAME" -b toggle,hidden
       else
           # Nếu đang bị che -> Đưa lên trên cùng & focus
           wmctrl -a "$WINDOW_NAME"
       fi
   else
       # Chưa mở -> Chạy ứng dụng
       $CMD &
   fi
   ```

3. Cấp quyền thực thi cho script:
   ```bash
   chmod +x toggle_window.sh
   ```

4. Gán hotkey vào hệ thống:
   - Vào **Settings** -> **Keyboard** -> **Keyboard Shortcuts** -> kéo xuống chọn **Custom Shortcuts (+)**.
   - Name: `Toggle App Window`
   - Command: `/path/to/toggle_window.sh`
   - Shortcut: `Ctrl + Alt + W`

---

## 🎯 Tóm Tắt Quy Trình Sử Dụng (Quick Summary)

1. **Gán phím tắt**: Thiết lập phím tắt `Ctrl + Alt + W` (Windows/Linux) hoặc `Cmd + Option + W` (macOS).
2. **Bấm lần đầu**: Cửa sổ ứng dụng mở ra.
3. **Khi bị che**: Khi bạn mở trình duyệt hoặc app khác che mất ứng dụng, chỉ cần bấm lại `Ctrl + Alt + W` / `Cmd + Option + W` -> Cửa sổ ứng dụng sẽ nhảy ngay lên trên cùng màn hình mà không cần rà chuột tìm kiếm!
