# Launchers

Thư mục này chứa các script để khởi chạy ứng dụng Cabal Auto Hunt.

## Files

### `run.bat`
Simple launcher với hardcoded venv path. Dùng cho quick launch khi bạn chắc chắn venv path.

**Usage:**
```cmd
cd E:\Cabal_Auto
scripts\launchers\run.bat
```

### `run_venv.bat` (Recommended)
Smart launcher tự động tìm Python từ nhiều nguồn.

**Usage:**
```cmd
# Use default .venv or venv
scripts\launchers\run_venv.bat

# Use custom venv
scripts\launchers\run_venv.bat myvenv
```

**Priority:**
1. Tham số truyền vào
2. `.venv\Scripts\python.exe`
3. `venv\Scripts\python.exe`
4. System Python on PATH

### `run_venv.ps1` (Most Powerful)
PowerShell launcher with advanced features.

**Usage:**
```powershell
# Basic usage
.\scripts\launchers\run_venv.ps1

# Custom venv
.\scripts\launchers\run_venv.ps1 -VenvPath myvenv

# Pass arguments to app_gui.py
.\scripts\launchers\run_venv.ps1 -Args "--debug --verbose"

# Both
.\scripts\launchers\run_venv.ps1 -VenvPath .venv -Args "--debug"
```

## Backward Compatibility

File `run.bat` ở root directory là wrapper gọi đến `scripts\launchers\run_venv.bat` để đảm bảo backward compatibility.

## Development

Khi develop, nên dùng:
```powershell
# PowerShell
.\scripts\launchers\run_venv.ps1

# Command Prompt
scripts\launchers\run_venv.bat
```

## See Also

- Main README: `../../README.md`
- Requirements: `../../requirements.txt`
