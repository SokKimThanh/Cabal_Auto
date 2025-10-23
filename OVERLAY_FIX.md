# Quick Fix: Overlay "No module named 'win32gui'" Error

## 🚨 Problem

When toggling overlay (Ctrl+Shift+O), you see:
```
ModuleNotFoundError: No module named 'win32gui'
```

## ✅ Solution (30 seconds)

### 1. Run Auto-Installer

Double-click this file in project root:
```
install_dependencies.bat
```

Wait for it to complete (~30 seconds).

### 2. Restart Application

Close and reopen `app_gui.py`.

### 3. Test Overlay

Press `Ctrl+Shift+O` - should work now!

---

## 🔧 Manual Fix (if auto-installer fails)

### Step 1: Open PowerShell in project folder

```powershell
cd E:\Cabal_Auto
```

### Step 2: Activate virtual environment

```powershell
venv\Scripts\activate
```

You should see `(venv)` prefix.

### Step 3: Install pywin32

```powershell
pip install pywin32
```

### Step 4: Verify

```powershell
python -c "import win32gui; print('OK')"
```

Should print `OK`.

### Step 5: Restart app

```batch
run.bat
```

---

## 📌 Important Notes

✅ **DO**: Use `run.bat` to start app (auto-activates venv)
❌ **DON'T**: Double-click `app_gui.py` directly (won't use venv)

✅ **DO**: Install in venv (`venv\Scripts\activate` first)
❌ **DON'T**: Install system-wide (may conflict)

---

## 🎯 Verification Checklist

- [ ] Ran `install_dependencies.bat` OR manual install
- [ ] Console shows "PyWin32 OK" or similar success message
- [ ] Closed and restarted application using `run.bat`
- [ ] Configured game window in Hunt tab
- [ ] Pressed `Ctrl+Shift+O` - overlay appears
- [ ] Can click through overlay to game window

---

## 🆘 Still Not Working?

1. Check Python version: `python --version` (need 3.8+)
2. Check venv active: prompt shows `(venv)`
3. Check installation: `pip list | findstr pywin32`
4. Run full check: `python scripts/check_dependencies.py`

**Common mistake**: Running app without activating venv first!

**Fix**: Always use `run.bat` instead of double-clicking `app_gui.py`.
