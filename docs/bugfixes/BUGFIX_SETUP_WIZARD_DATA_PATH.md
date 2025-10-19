# Bugfix: Setup Wizard Data Path

**Date:** October 19, 2025  
**Issue:** Setup wizard không thể tìm thấy dữ liệu monsters và skills  
**Severity:** High - Blocking first-time setup  
**Status:** ✅ Fixed

## 🐛 Problem

Setup wizard (`ui/setup_wizard.py`) không thể load danh sách monsters và skills khi chạy các bước setup (Step 3 và Step 4).

### Root Cause

File `ui/setup_wizard.py` đang sử dụng đường dẫn sai:
```python
# Incorrect (looking for ui/data/)
monsters_path = os.path.join(os.path.dirname(__file__), 'data', 'monsters.json')
skills_path = os.path.join(os.path.dirname(__file__), 'data', 'skills.json')
```

Vấn đề:
- `__file__` = `E:\Cabal_Auto\ui\setup_wizard.py`
- `os.path.dirname(__file__)` = `E:\Cabal_Auto\ui`
- Path được tạo = `E:\Cabal_Auto\ui\data\monsters.json` ❌

Nhưng thực tế thư mục `data/` nằm ở:
- `E:\Cabal_Auto\data\monsters.json` ✅

## 🔧 Solution

Sửa đường dẫn để trỏ đúng về parent directory.

### File 1: `ui/setup_wizard.py`

#### Step 3 - Monster Selection (Line 572)

**Before:**
```python
monsters_path = os.path.join(os.path.dirname(__file__), 'data', 'monsters.json')
```

**After:**
```python
monsters_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'monsters.json')
```

### Step 4 - Skill Configuration (Line 660)

**Before:**
```python
skills_path = os.path.join(os.path.dirname(__file__), 'data', 'skills.json')
```

**After:**
```python
skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'skills.json')
```

### File 2: `ui/auto_hunt.py`

#### CONFIG_PATH (Line 12)

**Before:**
```python
CONFIG_PATH = Path(__file__).parent / 'data' / 'hunt_config.json'
```

**After:**
```python
CONFIG_PATH = Path(__file__).parent.parent / 'data' / 'hunt_config.json'
```

#### skills_path (Line 235)

**Before:**
```python
skills_path = Path(__file__).parent / 'data' / 'skills.json'
```

**After:**
```python
skills_path = Path(__file__).parent.parent / 'data' / 'skills.json'
```

## ✅ Verification

Test script confirms fix:
```python
ui_dir = Path('E:/Cabal_Auto/ui')

# Old path (incorrect)
old_path = ui_dir / 'data' / 'monsters.json'
print(old_path.exists())  # False ❌

# New path (correct)
new_path = ui_dir.parent / 'data' / 'monsters.json'
print(new_path.exists())  # True ✅
print(len(json.load(open(new_path))))  # 3 monsters
```

**Results:**
- ✅ `ui/setup_wizard.py` - Monsters path: `E:\Cabal_Auto\data\monsters.json` (3 items found)
- ✅ `ui/setup_wizard.py` - Skills path: `E:\Cabal_Auto\data\skills.json` (5 items found)
- ✅ `ui/auto_hunt.py` - Config path: `E:\Cabal_Auto\data\hunt_config.json` (exists)
- ✅ `ui/auto_hunt.py` - Skills path: `E:\Cabal_Auto\data\skills.json` (exists)
- ✅ Setup wizard now displays Step 3 and Step 4 correctly
- ✅ Auto hunt script can load configuration and skills

## 📝 Notes

### Why `app_gui.py` Works

File `app_gui.py` ở root level nên path của nó đúng từ đầu:
```python
# app_gui.py is at E:\Cabal_Auto\app_gui.py
CONFIG_PATH = Path(__file__).parent / 'data' / 'config.json'
# Results in: E:\Cabal_Auto\data\config.json ✅
```

### Directory Structure

```
E:\Cabal_Auto\
├── app_gui.py          ← Root level (paths OK)
├── data\               ← Data folder here!
│   ├── monsters.json
│   └── skills.json
└── ui\
    ├── app_gui.py
    └── setup_wizard.py ← Was looking in ui/data/ (wrong!)
```

## 🎯 Impact

- **Before:** Setup wizard showed "No monsters/skills found" errors
- **After:** Setup wizard loads and displays all monsters (3) and skills (5)
- **User Experience:** First-time setup now works as expected
- **Testing:** Manual testing confirmed wizard displays data correctly

## 🔍 Related Files

**Fixed:**
- ✅ `ui/setup_wizard.py` - Fixed data paths (2 locations)
- ✅ `ui/auto_hunt.py` - Fixed data paths (2 locations)

**Already Correct:**
- ✅ `app_gui.py` - Correct (root level)

**Data Files:**
- `data/config.json`
- `data/hunt_config.json`
- `data/monsters.json`
- `data/skills.json`

## 📌 Tags

`bugfix` `setup-wizard` `data-path` `file-not-found` `high-priority`
