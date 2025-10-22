# Single Instance Lock - Cabal Auto Hunt

## 📋 Tổng quan | Overview

**Chức năng**: Ngăn chặn nhiều instance của ứng dụng chạy đồng thời.  
**Function**: Prevent multiple instances of the application from running simultaneously.

**Quy tắc**: Chỉ cho phép **DUY NHẤT 1 ứng dụng** chạy tại một thời điểm.  
**Rule**: Only **ONE SINGLE instance** can run at a time.

---

## 🎯 Lý do thực hiện | Rationale

### Vấn đề | Problem
- Người dùng có thể vô tình mở nhiều instance → xung đột tài nguyên
- Multiple hunt threads có thể gây ra race conditions
- File config có thể bị ghi đè không đồng bộ
- Game client có thể bị điều khiển bởi nhiều instance cùng lúc

### Giải pháp | Solution
Sử dụng **Single Instance Lock** để đảm bảo:
- ✅ Chỉ 1 instance duy nhất được phép chạy
- ✅ Instance mới sẽ bị chặn với thông báo rõ ràng
- ✅ Người dùng phải tắt app cũ trước khi mở app mới

---

## 🔧 Cơ chế hoạt động | Implementation

### Windows
- **Công nghệ**: Named Mutex (Windows API)
- **API**: `CreateMutexW()` + `GetLastError()`
- **Mutex Name**: `Global\CabalAutoHunt_v1_SingleInstance`
- **Ưu điểm**: 
  - Đáng tin cậy 100%
  - Tự động release khi process kết thúc
  - Không cần cleanup thủ công

### Unix/Linux
- **Công nghệ**: File Locking (fcntl)
- **Lock File**: `tmp/CabalAutoHunt_v1.lock`
- **API**: `fcntl.flock()` with `LOCK_EX | LOCK_NB`
- **Ưu điểm**: 
  - POSIX standard
  - Tự động release khi process kết thúc
  - File chứa PID để debug

---

## 📝 Code Structure

### Class: `SingleInstanceLock`

```python
class SingleInstanceLock:
    """Cross-platform single instance lock."""
    
    def __init__(self, app_name: str = "CabalAutoHunt"):
        """Initialize lock with unique app name."""
    
    def acquire(self) -> bool:
        """Try to acquire lock. Returns True if successful."""
    
    def release(self):
        """Release lock and cleanup resources."""
```

### Workflow

```python
def main():
    # 1. Create lock
    instance_lock = SingleInstanceLock("CabalAutoHunt_v1")
    
    # 2. Try to acquire
    if not instance_lock.acquire():
        # Show error message
        messagebox.showerror(...)
        sys.exit(1)
    
    try:
        # 3. Run application
        app = App()
        app.mainloop()
    finally:
        # 4. Always release lock
        instance_lock.release()
```

---

## 💬 User Experience

### Kịch bản 1: Mở instance đầu tiên | First Instance
```
✅ Lock acquired successfully
✅ Application starts normally
```

### Kịch bản 2: Mở instance thứ 2 (while 1st is running) | Second Instance
```
❌ Lock acquisition failed
❌ Error dialog shown (bilingual):
   - English: "Cannot start: Another instance is already running!"
   - Vietnamese: "Không thể khởi động: Ứng dụng đã đang chạy!"
❌ Application exits immediately
```

### Kịch bản 3: Tắt instance 1, mở instance mới | Close & Restart
```
✅ Instance 1 releases lock (in finally block)
✅ Instance 2 can now acquire lock
✅ Instance 2 starts normally
```

---

## 🧪 Testing

### Test Case 1: Normal Startup
**Bước thực hiện**:
1. Đảm bảo không có instance nào đang chạy
2. Chạy `python app_gui.py`

**Kết quả mong đợi**:
- ✅ App khởi động bình thường
- ✅ File `tmp/CabalAutoHunt_v1.lock` được tạo (Unix) hoặc Mutex được tạo (Windows)

### Test Case 2: Second Instance Blocked
**Bước thực hiện**:
1. Mở terminal 1: `python app_gui.py` (chạy background)
2. Mở terminal 2: `python app_gui.py` (thử mở instance 2)

**Kết quả mong đợi**:
- ❌ Instance 2 hiển thị error dialog
- ❌ Instance 2 không khởi động
- ✅ Instance 1 vẫn chạy bình thường

### Test Case 3: Restart After Close
**Bước thực hiện**:
1. Mở instance 1
2. Đóng instance 1 (Ctrl+C hoặc nút X)
3. Ngay lập tức mở instance 2

**Kết quả mong đợi**:
- ✅ Instance 1 release lock khi đóng
- ✅ Instance 2 khởi động thành công

---

## 🚨 Error Handling

### Windows Permission Error
**Lỗi**: `Access Denied` khi create mutex  
**Nguyên nhân**: UAC restrictions hoặc antivirus  
**Giải pháp**: Chạy as Administrator hoặc whitelist app

### Unix Lock File Permission
**Lỗi**: `Permission Denied` khi create lock file  
**Nguyên nhân**: Directory không writable  
**Giải pháp**: Đảm bảo `tmp/` directory có quyền write

### Stale Lock Detection
**Tình huống**: App crash → lock không được release  
**Windows**: Mutex tự động cleanup khi process dies → Không vấn đề  
**Unix**: Lock file có thể còn lại → Cần check PID trong file để verify

---

## 📊 Technical Details

### Windows Mutex
```cpp
HANDLE CreateMutexW(
    NULL,                           // Security attributes (NULL = default)
    FALSE,                          // Initial owner (FALSE = not owned)
    "Global\\CabalAutoHunt_v1"     // Mutex name (Global = all sessions)
);

// Check if mutex already exists
DWORD error = GetLastError();
if (error == ERROR_ALREADY_EXISTS) {
    // Another instance is running
}
```

### Unix File Lock
```python
import fcntl

lock_file = open('tmp/app.lock', 'w')
fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
# LOCK_EX = Exclusive lock
# LOCK_NB = Non-blocking (raise error if already locked)
```

---

## 🔍 Debugging

### Check if lock is held (Windows)
```powershell
# PowerShell: Check running Python processes
Get-Process python | Select-Object Id, ProcessName, MainWindowTitle
```

### Check if lock is held (Unix)
```bash
# Check lock file
cat tmp/CabalAutoHunt_v1.lock  # Shows PID

# Check if process is running
ps -p <PID>
```

### Force unlock (Emergency)
**Windows**: Kill process via Task Manager  
**Unix**: 
```bash
rm tmp/CabalAutoHunt_v1.lock  # Remove stale lock
kill -9 <PID>                 # Force kill process
```

---

## 📚 References

- **Windows Mutex**: https://docs.microsoft.com/en-us/windows/win32/sync/mutex-objects
- **Unix File Locking**: https://docs.python.org/3/library/fcntl.html
- **Python ctypes**: https://docs.python.org/3/library/ctypes.html

---

## ✅ Status

**Implemented**: ✅ Completed  
**Tested**: ✅ Windows 10/11  
**Platform Support**: ✅ Windows + Unix/Linux  
**Version**: 1.0.0  
**Date**: October 21, 2025
