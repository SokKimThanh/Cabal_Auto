# BUGFIX: Skill Image Capture Path

**Date**: October 19, 2025  
**Status**: ✅ Fixed  
**Severity**: High - Skills saved to wrong directory  
**Component**: Library Manager - Skill Tab

---

## Problem Description

### Issue
When capturing skill images in Library Manager's Skill Tab, images were being saved to the **monsters** directory instead of the **skills** directory.

### Root Cause
`capture_helper.py` was hardcoded to save all captures to `assets/images/monsters/`, regardless of whether capturing a monster or skill image.

```python
# BEFORE - Always saved to monsters/
ASSETS_DIR = _project_root / 'assets' / 'images' / 'monsters'
# ...
path = ASSETS_DIR / filename  # No way to choose different directory
```

### Impact
- ❌ Skill images mixed with monster templates
- ❌ Incorrect directory structure
- ❌ Confusion when browsing image folders
- ❌ Skills.json referenced images in wrong location

---

## Investigation

### File Analysis

**`lib/ui/capture_helper.py`** (Line 20-26):
```python
# Original hardcoded path
ASSETS_DIR = _project_root / 'assets' / 'images' / 'monsters'
```

**`lib/ui/library_manager.py`** (Line 2795-2802):
```python
# Skill Tab capture call - no way to specify target directory
result = capture_region_and_save(
    self, 
    self.pil_available, 
    self.current_skill.get('name', ''), 
    self.lang, 
    pre_wait_hook=_pre_wait_bring
)  # Missing: capture_type parameter!
```

### Expected Behavior
- Monster images → `assets/images/monsters/`
- Skill images → `assets/images/skills/`

### Actual Behavior
- Monster images → `assets/images/monsters/` ✓
- Skill images → `assets/images/monsters/` ✗ (WRONG!)

---

## Solution

### 1. Updated `capture_helper.py` - Added Skills Directory Support

**File**: `lib/ui/capture_helper.py`

**Lines 20-31** - Added ASSETS_SKILLS_DIR:
```python
# Get project root by going up from lib/ui/capture_helper.py
_current_file = Path(__file__).resolve()  # lib/ui/capture_helper.py
_lib_dir = _current_file.parent.parent    # lib/
_project_root = _lib_dir.parent            # project root

# Default ASSETS_DIR for monsters (backward compatibility)
ASSETS_DIR = _project_root / 'assets' / 'images' / 'monsters'
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Skills directory
ASSETS_SKILLS_DIR = _project_root / 'assets' / 'images' / 'skills'
ASSETS_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
```

**Lines 107-124** - Added `capture_type` parameter:
```python
def capture_region_and_save(
    parent: Any, 
    pil_available: bool, 
    monster_name: str, 
    lang: str = 'vi', 
    pre_wait_hook: Optional[Callable[[], None]] = None,
    capture_type: str = 'monster'  # NEW: Determines save directory
) -> Optional[Tuple[str, Tuple[int,int,int,int]]]:
    """Implements the shared capture flow: wait 3s, screenshot, region select, crop and save.
    
    Args:
        parent: Parent widget
        pil_available: Whether PIL is available
        monster_name: Name for the image file (works for both monsters and skills)
        lang: Language ('vi' or 'en')
        pre_wait_hook: Optional callback before screenshot
        capture_type: 'monster' or 'skill' - determines save directory
    
    Returns (path, bbox) where bbox is (left, top, width, height), or None if cancelled/failed.
    """
```

**Lines 189-199** - Dynamic directory selection:
```python
# Determine save directory based on capture type
if capture_type == 'skill':
    save_dir = ASSETS_SKILLS_DIR
    default_name = 'skill'
else:  # default to 'monster'
    save_dir = ASSETS_DIR
    default_name = 'monster'

# Save under appropriate directory
slug = _slugify(monster_name or default_name)
ts = int(time.time())
filename = f"{slug}_capture_{ts}.png"
path = save_dir / filename
```

### 2. Updated Library Manager - Skill Tab Capture Call

**File**: `lib/ui/library_manager.py`

**Lines 2795-2802** - Added `capture_type='skill'`:
```python
result = capture_region_and_save(
    self, 
    self.pil_available, 
    self.current_skill.get('name', ''), 
    self.lang, 
    pre_wait_hook=_pre_wait_bring,
    capture_type='skill'  # ✅ NEW: Save to assets/images/skills/
)
```

**Lines 2804-2811** - Fixed result handling:
```python
if result:
    # result is (path, bbox) tuple
    image_path, bbox = result
    # Update current skill
    self.current_skill['image'] = image_path
    self.changes_made['skills_changed'] = True
    self._mark_unsaved(True)
    
    # Refresh preview
    self._show_skill_image_preview(self.current_skill)
```

**Previous bug**: Code tried `result.get('image_path')` - wrong! Result is a tuple, not dict.

### 3. Backward Compatibility

**Monster Tab remains unchanged** - default `capture_type='monster'`:
```python
# lib/ui/library_manager.py Line 1717
result = capture_region_and_save(
    parent, 
    self.pil_available, 
    self.current_monster.get('name',''), 
    self.lang, 
    pre_wait_hook=_pre_wait_bring
)  # No capture_type needed - defaults to 'monster'
```

---

## Testing

### Test Script: `test_skill_capture_path.py`

**Test Results**:
```
✓ Monster save dir: E:\Cabal_Auto\assets\images\monsters (Exists: True)
✓ Skill save dir:   E:\Cabal_Auto\assets\images\skills (Exists: True)
✓ Directories are different (correct!)
✓ Function parameters includes 'capture_type' (Default: 'monster')
✓ Skill Tab uses capture_type='skill'
✓ Skill Tab calls capture_region_and_save
```

### Manual Testing Checklist
- [x] Monster capture saves to `assets/images/monsters/`
- [x] Skill capture saves to `assets/images/skills/`
- [x] Both directories auto-created if missing
- [x] Image preview shows captured skill image
- [x] Skills.json updated with correct path
- [x] Backward compatibility maintained for monsters

---

## Code Changes Summary

### Files Modified
1. **`lib/ui/capture_helper.py`**
   - Added `ASSETS_SKILLS_DIR` constant
   - Added `capture_type` parameter to `capture_region_and_save()`
   - Dynamic directory selection logic
   - Enhanced docstring

2. **`lib/ui/library_manager.py`**
   - Skill Tab: Added `capture_type='skill'` to capture call
   - Fixed result handling (tuple unpacking vs dict access)

### Files Created
- `test_skill_capture_path.py` - Automated verification test
- `docs/bugfixes/BUGFIX_SKILL_CAPTURE_PATH.md` - This document

---

## Related Issues

### Additional Fix: Library Manager Monster Path
Also fixed in same session: `library_manager.py` line 434 had incorrect path resolution:
```python
# BEFORE (wrong - only goes to lib/)
self.project_root = Path(os.path.dirname(os.path.dirname(__file__)))

# AFTER (correct - goes to project root)
_current_file = Path(__file__).resolve()
_lib_ui_dir = _current_file.parent
_lib_dir = _lib_ui_dir.parent
self.project_root = _lib_dir.parent
```

---

## Prevention

### Code Review Checklist
- [ ] When adding new capture types, verify save directory
- [ ] Test both Monster and Skill capture paths
- [ ] Verify directory auto-creation works
- [ ] Check image paths in JSON data files

### Future Enhancements
Consider adding more capture types:
- `capture_type='icon'` → `assets/images/icons/`
- `capture_type='ui'` → `assets/images/ui/`
- Validate `capture_type` values

---

## Conclusion

✅ **Fix confirmed working:**
- Monsters save to: `E:\Cabal_Auto\assets\images\monsters/`
- Skills save to: `E:\Cabal_Auto\assets\images\skills/`
- Both paths verified and tested
- Backward compatibility maintained

**Before**: All captures → monsters folder (incorrect)  
**After**: Captures go to appropriate folders based on type (correct)

The Library Manager Skill Tab now correctly saves captured images to the skills directory, maintaining proper project organization.
