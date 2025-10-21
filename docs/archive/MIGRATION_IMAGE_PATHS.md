# Image Path Consolidation Plan

**Date:** October 19, 2025  
**Issue:** Images scattered across multiple locations  
**Goal:** Consolidate all images under `assets/images/` at root level

## 📊 Current State

### Directory Structure
```
E:\Cabal_Auto\
├── assets\
│   └── images\
│       └── icons\         (30+ icon files - .ico and .png)
│
└── lib\
    └── assets\
        └── images\
            ├── monsters\  (9 monster template images)
            └── skills\    (4 skill images)
```

### Problems Identified

1. **Split locations**: Images in both `assets/images/` and `lib/assets/images/`
2. **Inconsistent paths**: 
   - `capture_helper.py` saves to `lib/assets/images/monsters/`
   - Config files reference `assets/images/monsters/`
3. **Confusing structure**: `lib/` should contain code, not assets

## 🎯 Target Structure

```
E:\Cabal_Auto\
└── assets\
    └── images\
        ├── icons\      (UI icons - .png and .ico)
        ├── monsters\   (Monster templates)
        └── skills\     (Skill icons)
```

## 📋 Migration Tasks

### Task 1: Create Target Directories
- [ ] Ensure `assets/images/monsters/` exists
- [ ] Ensure `assets/images/skills/` exists

### Task 2: Move Files
- [ ] Move 9 files from `lib/assets/images/monsters/` → `assets/images/monsters/`
- [ ] Move 4 files from `lib/assets/images/skills/` → `assets/images/skills/`

### Task 3: Update Code Paths

#### Files to Update:

1. **lib/ui/capture_helper.py** (Line 20)
   ```python
   # Before
   ASSETS_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / 'assets' / 'images' / 'monsters'
   
   # After  
   ASSETS_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'assets' / 'images' / 'monsters'
   # Or better: use project root detection
   ```

2. **lib/features/skills/migrator.py** (Line 27)
   ```python
   # Already correct - uses relative path 'assets/images/skills'
   # Just verify it resolves correctly from project root
   ```

3. **Icon helper** - Already correct
   - Uses `assets/images/icons` at root level

### Task 4: Clean Up
- [ ] Remove `lib/assets/` directory after migration
- [ ] Update documentation

## 🔍 Files Using Image Paths

### Direct Path Usage:
1. `lib/ui/capture_helper.py` - NEEDS UPDATE
2. `lib/features/skills/migrator.py` - CHECK
3. `lib/ui/icon_helper.py` - OK (uses root assets)
4. `app_gui.py` - Uses relative paths (should work)

### Reference in Docs (info only):
- `tests/opencv_test.py`
- `docs/PROJECT_SUMMARY.py`
- `lib/vision/template_matcher.py` (examples)

## ✅ Verification Steps

After migration:
1. Test capture_helper saves to correct location
2. Test icon_helper loads icons
3. Test skill images load correctly
4. Test monster templates load correctly
5. Verify no references to `lib/assets/`

## 🚨 Risk Assessment

**Low Risk:**
- All paths are configurable
- Data files use relative paths
- Can test without breaking existing functionality

**Mitigation:**
- Keep backup of `lib/assets/` until verified
- Test each component after update
