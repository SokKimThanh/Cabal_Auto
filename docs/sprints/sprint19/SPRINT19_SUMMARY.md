# Sprint 19 - Template Badge Timing Fix

**Date**: October 19, 2025  
**Status**: ✅ Completed

---

## 🎯 Objectives

Fix template badge hiển thị sai thời điểm:
- ❌ Badge "Chưa lưu" xuất hiện ngay khi chọn template (chưa edit)
- ✅ Badge chỉ hiển thị khi thực sự unlock và edit

---

## 📋 Changes

### 1. Hide Badge on Template Selection
**File**: `lib/ui/library_manager.py`
- Method: `_select_template_by_index()`
- Changed: `_mark_unsaved()` → `_hide_template_badge()`
- Effect: Badge ẩn khi template locked (view-only)

### 2. NEW Method: _hide_template_badge()
```python
def _hide_template_badge(self):
    """Hide template badge (used when viewing locked template)."""
    try:
        if self.unsaved_badge:
            self.unsaved_badge.place_forget()
    except Exception:
        pass
```

### 3. Remove _mark_unsaved() from Template Callbacks
Removed conflicting `_mark_unsaved(True)` calls from:
- `_on_template_name_change()`
- `_on_template_path_change()`
- `_on_template_threshold_change()`
- `_on_template_region_change()`

**Reason**: Badge "Đang chỉnh sửa" (orange) already shown by unlock action

---

## 🎨 Badge States (Fixed)

| Trigger | State | Badge | Color |
|---------|-------|-------|-------|
| Select template | 🔒 Locked | ⚪ Hidden | - |
| Click Edit ✏️ | 🔓 Unlocked | 🟧 "Đang chỉnh sửa" | Orange |
| Edit fields | 🔓 Unlocked | 🟧 "Đang chỉnh sửa" | Orange |
| Click Save 💾 | 🔒 Locked | 🟩 "Đã lưu" (3s) | Green |
| After 3s | 🔒 Locked | ⚪ Hidden | - |

---

## ✅ Results

**Before**:
- 😕 Badge "CHƯA LƯU" hiển thị ngay khi chọn template
- 😟 Gây nhầm lẫn, lo lắng cho user
- 🎨 UI rối, badge conflict

**After**:
- 😊 Badge chỉ hiển thị khi unlock để edit
- 🎯 Logic rõ ràng: Locked = hidden, Unlocked = orange
- 🎨 UI gọn gàng, không conflict

---

## 🧪 Testing

**Test Script**: `tests/demo_template_badge_timing.py`

**Manual Test**:
```bash
python app_gui.py
# → Quản Lý Thư Viện → Tab Quái Vật
# → Chọn template → Verify NO badge
# → Click ✏️ → Verify orange badge "Đang chỉnh sửa"
# → Edit → Verify badge stable
# → Click 💾 → Verify green badge "Đã lưu" → auto-hide
```

---

## 📚 Documentation

- **Bugfix Detail**: `docs/sprints/sprint19/BUGFIX_TEMPLATE_BADGE_PREMATURE_DISPLAY.md`
- **Test Script**: `tests/demo_template_badge_timing.py`
- **Previous Feature**: `docs/UPDATE_TEMPLATE_INSTANT_SAVE.md`

---

## 🔍 Related Issues

**Previous Sprint**:
- Sprint 18 Phase 4: Template lock/unlock với instant save
- Implemented badge system (orange/green)

**This Sprint**:
- Fixed badge premature display
- Resolved badge conflict between global and template badges
- Improved UX logic

---

**Status**: ✅ Production Ready  
**Lines Changed**: ~15 lines in `lib/ui/library_manager.py`  
**Impact**: High (UX clarity improvement)
