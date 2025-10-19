# Sprint 19 - Badge System Improvements

**Date**: October 19, 2025  
**Status**: ✅ Completed

---

## 🎯 Objectives

**Phase 1**: Fix template badge hiển thị sai thời điểm
- ❌ Badge "Chưa lưu" xuất hiện ngay khi chọn template (chưa edit)
- ✅ Badge chỉ hiển thị khi thực sự unlock và edit

**Phase 2**: Relocate global badge to top bar
- ❌ Badge trong tab area, gây nhầm lẫn giữa local và global state
- ✅ Badge trong top bar cạnh nút Save, phản ánh trạng thái toàn cục

---

## 📋 Changes

### Phase 1: Template Badge Timing Fix

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

### Phase 2: Global Badge Relocation

### 1. Badge Separation
**Before**: 1 badge cho cả global và template → conflict
**After**: 2 badge riêng biệt
```python
self.unsaved_badge = None   # Global badge in top bar (all tabs)
self.template_badge = None  # Template badge in monster tab
```

### 2. Global Badge in Top Bar
**Location**: Right of Save button in `top_bar`
```python
# Global unsaved badge (for all tabs)
self.unsaved_badge = tk.Label(top_bar, text='', 
    bg=UI.COLOR_WARNING, fg='#FFFFFF', 
    font=(UI.FONT_FAMILY, 9, 'bold'), padx=8, pady=4)
self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
self.unsaved_badge.pack_forget()  # Initially hidden
```

**Visual**:
```
┌────────────────────────────────────────────────┐
│ [Title]              [CHƯA LƯU] [💾] [✖]      │ ← Top bar
├────────────────────────────────────────────────┤
│ [Quái Vật] [Kỹ Năng] [Timing]                 │
└────────────────────────────────────────────────┘
```

### 3. Template Badge Methods Updated
All template badge methods now use `self.template_badge`:
- `_show_editing_badge()` → Orange "Đang chỉnh sửa"
- `_show_saved_badge()` → Green "Đã lưu" (3s)
- `_hide_template_badge()` → Hide when locked

### 4. Global Badge Tracking
```python
def _mark_unsaved(self, state: bool):
    """Show/hide global badge (tracks all 3 tabs)."""
    if state:
        self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
    else:
        self.unsaved_badge.pack_forget()
```

Tracks changes from:
- Tab 1: Quái Vật (monsters)
- Tab 2: Kỹ Năng (skills)  
- Tab 3: Timing (calculations)

---

## 📚 Documentation

**Phase 1**:
- **Bugfix Detail**: `docs/sprints/sprint19/BUGFIX_TEMPLATE_BADGE_PREMATURE_DISPLAY.md`
- **Test Script**: `tests/demo_template_badge_timing.py`

**Phase 2**:
- **UX Enhancement**: `docs/sprints/sprint19/UX_GLOBAL_BADGE_RELOCATION.md`
- **Test Script**: `tests/demo_global_badge_relocation.py`

**Related**:
- **Previous Feature**: `docs/UPDATE_TEMPLATE_INSTANT_SAVE.md`

---

## 🔍 Related Issues

**Previous Sprint**:
- Sprint 18 Phase 4: Template lock/unlock với instant save
- Implemented badge system (orange/green)

**This Sprint - Phase 1**:
- Fixed badge premature display
- Resolved badge conflict in template callbacks
- Improved template badge timing

**This Sprint - Phase 2**:
- Relocated global badge to top bar
- Separated global and template badge systems
- Improved UX clarity for multi-tab state tracking

---

## ✅ Final Results

### Phase 1
- ✅ Template badge chỉ hiển thị khi unlock
- ✅ Không còn conflict trong callbacks
- ✅ Logic rõ ràng: locked = hidden, unlocked = orange

### Phase 2
- ✅ Global badge trong top bar cạnh Save button
- ✅ Badge visible across all 3 tabs
- ✅ Clear separation: global vs template badge
- ✅ Better UX: badge near related action

---

**Status**: ✅ Production Ready  
**Total Lines Changed**: ~30 lines in `lib/ui/library_manager.py`  
**Impact**: High (Major UX clarity improvement)  
**Risk**: Low (Non-breaking changes)
