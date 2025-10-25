# Quick Fix: Tkinter Empty Window Bug

**Problem:** Extra empty "tk" window appears in taskbar

**Root Cause:** Creating `tk.StringVar()` without `master` parameter before `super().__init__()`

---

## ⚡ Quick Solution

### DON'T ❌
```python
class MyDialog(tk.Toplevel):
    def __init__(self, parent):
        # ❌ Creates auto-root window!
        self.my_var = tk.StringVar(value="test")
        super().__init__(parent)
```

### DO ✅
```python
class MyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        # ✅ Safe - self is valid master now
        self.my_var = tk.StringVar(master=self, value="test")
```

---

## 🔍 Diagnosis

Count taskbar windows:
- **Expected:** 1 window (your dialog)
- **Bug:** 2 windows (your dialog + "tk")

---

## ✅ Prevention Rules

1. **Always call `super().__init__(parent)` first** in Toplevel subclasses
2. **Always use `master=self`** for tk variables (StringVar, IntVar, BooleanVar)
3. **Never create tk variables before `super().__init__()`** (unless you know what you're doing)
4. **Test visually:** Check Windows taskbar for extra windows

---

## 📚 Full Documentation

See: [`docs/bugfixes/TKINTER_EMPTY_WINDOW_BUG_LESSONS_LEARNED.md`](bugfixes/TKINTER_EMPTY_WINDOW_BUG_LESSONS_LEARNED.md)

Includes:
- Detailed root cause analysis
- Complete debugging journey
- MRO chain fixes
- Prevention checklist
- Code examples

---

**Last Updated:** October 26, 2025
