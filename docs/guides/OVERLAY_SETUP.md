# Overlay Feature Setup Guide

## 🎯 Overview

The overlay feature requires **PyWin32** library for Windows GDI rendering and true click-through support.

## ⚙️ Installation

### Option 1: Automatic Installation (Recommended)

Run the provided batch script:

```batch
install_dependencies.bat
```

This will:
- ✅ Detect your Python environment (venv or system)
- ✅ Check all required packages
- ✅ Auto-install missing dependencies

### Option 2: Manual Installation

If using **virtual environment** (recommended):

```powershell
# Activate venv
venv\Scripts\activate

# Install pywin32
pip install pywin32

# Verify installation
python -c "import win32gui; print('PyWin32 OK')"
```

If using **system Python**:

```powershell
# Install directly
pip install pywin32

# Verify
python -c "import win32gui; print('PyWin32 OK')"
```

### Option 3: Install All Dependencies

```powershell
pip install -r requirements.txt
```

## 🔍 Troubleshooting

### Error: "No module named 'win32gui'"

**Cause**: PyWin32 not installed in the Python environment being used.

**Solution**:

1. Check which Python is running:
   ```powershell
   where python
   ```

2. Check if you're in venv:
   ```powershell
   # Should show (venv) prefix in prompt
   # If not, activate it:
   venv\Scripts\activate
   ```

3. Install pywin32:
   ```powershell
   pip install pywin32
   ```

4. Restart the application

### Error: "DLL load failed"

**Cause**: PyWin32 post-install script didn't run.

**Solution**:

```powershell
# Run post-install script manually
python venv\Scripts\pywin32_postinstall.py -install
```

### Overlay Toggle Not Working

**Symptoms**: 
- Pressing Ctrl+Shift+O shows error dialog
- "Missing Dependency" message appears

**Solution**:
1. Run `install_dependencies.bat`
2. Check console output for errors
3. Restart application after installing

## 📋 Dependency Check

Run the dependency checker to verify all packages:

```powershell
python scripts/check_dependencies.py
```

Auto-install missing packages:

```powershell
python scripts/check_dependencies.py --install
```

## 🚀 Quick Start

1. **Install dependencies**:
   ```batch
   install_dependencies.bat
   ```

2. **Run application**:
   ```batch
   run.bat
   ```
   Or:
   ```powershell
   venv\Scripts\activate
   python app_gui.py
   ```

3. **Test overlay**:
   - Configure a game window in Hunt tab
   - Press `Ctrl+Shift+O` to toggle overlay
   - Overlay should appear with click-through enabled

## 📦 Required Packages

| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | ≥4.8.0 | Image processing |
| numpy | ≥1.24.0 | Array operations |
| pillow | ≥10.0.0 | Image handling |
| pyautogui | ≥0.9.50 | GUI automation |
| keyboard | ≥0.13.5 | Hotkey support |
| **pywin32** | **≥306** | **Overlay window (Win32 GDI)** |
| pytest | ≥8.0.0 | Testing |

## 🔗 References

- [PyWin32 Documentation](https://github.com/mhammond/pywin32)
- [Sprint 23 Phase 5 Documentation](docs/sprints/SPRINT23_VISION_ADVANCED_PHASE5.md)
- [Overlay Architecture](docs/architecture/OVERLAY_WINDOW_ARCHITECTURE.md)

## ❓ Support

If you encounter issues:

1. Check console output for detailed error messages
2. Run `python scripts/check_dependencies.py` to verify installation
3. Check Python version: `python --version` (requires Python 3.8+)
4. Ensure you're using the correct Python environment (venv)

## 📝 Notes

- PyWin32 is **Windows-only** - overlay feature not available on other platforms
- Must run as regular user (not elevated/admin) for click-through to work properly
- Virtual environment recommended to avoid conflicts with system packages
