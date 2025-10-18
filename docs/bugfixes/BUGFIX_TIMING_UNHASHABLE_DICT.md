# Bug Fix: Timing Recommendation - Unhashable Dict Error

**Date:** October 18, 2025
**Sprint:** Sprint 18 Phase 4
**Severity:** Critical (blocks timing calculation feature)
**Status:** ✅ Fixed

---

## Problem Description

### User Report
```
Error: cannot use 'dict' as a dict key (unhashable type: 'dict')
```

Khi người dùng nhấn nút "Tính thời gian" (Calculate Timing), hệ thống hiển thị lỗi này và không thể tính toán thời gian khuyến nghị.

### Root Cause

Lỗi xảy ra do **mismatch giữa data structure** trong code và trong file cấu hình:

**Code assumption:**
```python
# Code giả định skill_slots là array of STRING
for skill_name in configured_skills:
    if skill_name in skill_dict:  # ❌ ERROR: skill_name is dict, not string!
```

**Actual data structure (hunt_config.json):**
```json
{
  "skill_slots": [
    {
      "name": "Dark Explosion",
      "key": "1",
      "type": "attack",
      "cooldown": 1.9,
      "cast_time": 1.7,
      "image": "assets/images/skills/..."
    }
  ]
}
```

`skill_slots` lưu **full skill objects** (dict), không phải chỉ tên skill (string).

---

## Impact

### Critical Issues
1. **Feature Blocker**: Không thể sử dụng tính năng "From Configured Skills" (tính từ kỹ năng đã cấu hình)
2. **Data Type Error**: TypeError khi dùng dict object làm dictionary key
3. **UX Breakdown**: Dialog timing recommendation không hiển thị được kết quả

### Affected Code Sections
- **Line 3716**: Initial skill filtering when dialog opens
- **Line 3845**: Skill filtering inside `update_recommendations()` function

---

## Solution Implementation

### Fix Strategy

Thay vì giả định `skill_slots` chứa strings, code bây giờ **kiểm tra type và extract data** từ dict objects:

```python
# ❌ OLD CODE (assumes strings)
for skill_name in configured_skills:
    if skill_name in skill_dict:
        skill_type = skill_dict[skill_name].get('type', 'attack').lower()
```

```python
# ✅ NEW CODE (handles dict objects)
for skill_slot in configured_skills:
    # Extract skill name from dict (skill_slots stores full skill objects)
    if isinstance(skill_slot, dict):
        skill_name = skill_slot.get('name', '')
        skill_type = skill_slot.get('type', 'attack').lower()
    else:
        # Fallback: if it's already a string
        skill_name = skill_slot
        # Look up type from library
        if skill_name in skill_dict:
            skill_type = skill_dict[skill_name].get('type', 'attack').lower()
        else:
            skill_type = 'attack'
    
    if skill_type == 'attack':
        attack_skill_names.append(skill_name)
    else:
        buff_skill_names.append(skill_name)
```

### Code Changes

**File:** `app_gui.py`

**Location 1: Line ~3708-3730** (Dialog initialization)
```python
# Calculate from CONFIGURED skills (from hunt_config skill_slots)
configured_skills = self.hunt_cfg.get('skill_slots', [])
skills_data = load_skill_library()
skill_dict = {s['name']: s for s in skills_data}

# Filter to get only ATTACK skills from configured skills
attack_skill_names = []
buff_skill_names = []
for skill_slot in configured_skills:
    # Extract skill name from dict (skill_slots stores full skill objects)
    if isinstance(skill_slot, dict):
        skill_name = skill_slot.get('name', '')
        skill_type = skill_slot.get('type', 'attack').lower()
    else:
        # Fallback: if it's already a string
        skill_name = skill_slot
        # Look up type from library
        if skill_name in skill_dict:
            skill_type = skill_dict[skill_name].get('type', 'attack').lower()
        else:
            skill_type = 'attack'
    
    if skill_type == 'attack':
        attack_skill_names.append(skill_name)
    else:
        buff_skill_names.append(skill_name)
```

**Location 2: Line ~3838-3860** (Inside `update_recommendations()`)
- Applied same fix to ensure consistency

---

## Testing & Validation

### Test Scenario
1. ✅ Open app with configured skills (3 attack + 1 buff)
2. ✅ Click "Tính thời gian" button
3. ✅ Dialog opens without errors
4. ✅ "From Configured Skills" option displays correct info:
   - "3 kỹ năng TẤN CÔNG: Dark Explosion, Bone Javelin, Skull Shooter"
   - "1 kỹ năng BUFF: Regeneration (không tính)"
5. ✅ Calculation works correctly with all options (from_skills, slow, normal, fast, custom)

### Verified Behaviors
- ✅ No TypeError when opening timing dialog
- ✅ Skills correctly separated into attack/buff categories
- ✅ Attack speed calculated from attack skills only (excludes buff)
- ✅ All preset options work correctly
- ✅ Custom speed input works

---

## Key Learnings

### Data Structure Awareness
**Lesson:** Always verify actual data structure in config files, not assumptions.

**Previous Bug:** Similar issue fixed in BUGFIX_TIMING_RECOMMENDATION_UX.md where we changed from `load_skill_library()` to `hunt_cfg.get('skill_slots')` but didn't account for the dict structure.

### Defensive Programming
The fix now includes:
1. **Type checking**: `isinstance(skill_slot, dict)`
2. **Fallback handling**: Support both dict and string formats
3. **Safe extraction**: `skill_slot.get('name', '')` with defaults

### Code Resilience
This pattern should be applied anywhere we access `skill_slots`:
```python
# Always extract name from skill_slot dict
for skill_slot in hunt_cfg.get('skill_slots', []):
    if isinstance(skill_slot, dict):
        skill_name = skill_slot.get('name', '')
        # Use skill_name...
```

---

## Related Issues

### Previous Related Bugs
1. **BUGFIX_TIMING_RECOMMENDATION_UX.md**: Changed skill source to configured skills
   - This introduced the dict vs string mismatch
2. **BUGFIX_SETUP_APPLY_SETTINGS.md**: Translation access fix
3. **BUGFIX_HUNT_START_OPENCV_LOGGER.md**: Logger parameter fixes

### Future Recommendations
1. Add type hints to clarify expected data structures
2. Consider creating a `Skill` dataclass for type safety
3. Add validation when loading hunt_config.json
4. Document data structure in hunt_config.json with comments

---

## Files Modified

### app_gui.py
- **Lines 3708-3730**: Fixed skill extraction in dialog initialization
- **Lines 3838-3860**: Fixed skill extraction in update_recommendations()
- **Total changes**: ~40 lines modified (2 locations)

### Debug Logging Added
```python
# Added error traceback logging
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    print(f"ERROR in on_monster_calculate_timing:\n{error_trace}")
    # ... display to user
```

---

## Deployment Notes

### No Breaking Changes
- Fix is backward compatible (supports both dict and string formats)
- No config file migration needed
- No user action required

### Verification Steps
1. Test with existing hunt_config.json (dict format) ✅
2. Test with empty skill_slots ✅
3. Test with mixed attack/buff skills ✅
4. Test all timing calculation presets ✅

---

## Conclusion

**Resolution:** Fixed TypeError by properly extracting skill names from dict objects in `skill_slots` array.

**Impact:** Timing recommendation feature now works correctly with configured skills.

**Status:** ✅ Bug resolved, feature fully functional.

---

**Next Steps:**
- Continue Sprint 18 Phase 4 Task #4 (Stats Tab)
- Monitor for similar dict/string mismatches in other code sections
- Consider adding type hints for better IDE support
