# UX Enhancement: Global Unsaved Badge Relocation

**Date**: October 19, 2025  
**Status**: ✅ Completed  
**Type**: UI/UX Improvement

---

## 🎯 Objective

Di chuyển badge "Chưa lưu" từ vị trí trong tab lên **top bar** cạnh nút lưu tổng, để:
- Phản ánh trạng thái **global** của cả 3 tab (Quái Vật, Kỹ Năng, Tính Toán)
- Tránh nhầm lẫn giữa trạng thái tab-specific và global
- Dễ dàng nhận biết khi có thay đổi chưa lưu

---

## 📋 Changes Summary

### 1. Badge Separation

**Before**: 1 badge dùng chung cho cả global và template editing
```python
self.unsaved_badge = None  # Used for both purposes - CONFLICT!
```

**After**: 2 badge riêng biệt
```python
self.unsaved_badge = None   # Global badge in top bar (all tabs)
self.template_badge = None  # Template-specific badge in monster tab
```

### 2. Global Badge in Top Bar

**Location**: Right of Save button in `top_bar`

**Code**:
```python
# Global unsaved badge (for all tabs) - right of Save button
self.unsaved_badge = tk.Label(
    top_bar, 
    text='', 
    bg=UI.COLOR_WARNING,     # Orange background
    fg='#FFFFFF',            # White text
    font=(UI.FONT_FAMILY, 9, 'bold'), 
    padx=8, 
    pady=4
)
self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
self.unsaved_badge.pack_forget()  # Initially hidden
```

**Visual Position**:
```
┌─────────────────────────────────────────────────┐
│ [Library Manager Title]  [CHƯA LƯU] [💾] [✖]  │ ← Top bar
├─────────────────────────────────────────────────┤
│ [Tab: Quái Vật] [Tab: Kỹ Năng] [Tab: Timing]   │
│                                                 │
│  ... Tab content ...                            │
└─────────────────────────────────────────────────┘
```

### 3. Template Badge Remains in Monster Tab

**Location**: Template form title area (monster tab only)

**Purpose**: Show template-specific editing state
- 🟧 "Đang chỉnh sửa" (Orange) - when unlocked
- 🟩 "Đã lưu" (Green, 3s) - after save

**Code**:
```python
# Template-specific badge for template editing
self.template_badge = tk.Label(
    form_title_frame,
    text='',
    bg=UI.COLOR_WARNING,
    fg='#FFFFFF',
    font=(UI.FONT_FAMILY, 9, 'bold')
)
self.template_badge.place_forget()  # Initially hidden
```

### 4. Updated Methods

#### _mark_unsaved() - Global Badge Control
```python
def _mark_unsaved(self, state: bool):
    """Show/hide global unsaved badge in top bar (tracks all 3 tabs)."""
    if hasattr(self, 'unsaved_badge') and self.unsaved_badge:
        if state:
            text = 'CHƯA LƯU' if self.lang == 'vi' else 'UNSAVED'
            self.unsaved_badge.config(text=text)
            # Show badge in top bar
            self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)
        else:
            self.unsaved_badge.config(text='')
            self.unsaved_badge.pack_forget()
```

#### Template Badge Methods
```python
def _show_editing_badge(self):
    """Orange badge: template editing in progress."""
    if self.template_badge:
        badge_text = 'Editing' if self.lang == 'en' else 'Đang chỉnh sửa'
        self.template_badge.config(text=f'  {badge_text}  ', bg='#FF9800')
        self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')

def _show_saved_badge(self):
    """Green badge: template saved successfully."""
    if self.template_badge:
        badge_text = 'Saved' if self.lang == 'en' else 'Đã lưu'
        self.template_badge.config(text=f'  {badge_text}  ', bg='#4CAF50')
        self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')
        # Hide after 3 seconds
        self.after(3000, lambda: self.template_badge.place_forget())

def _hide_template_badge(self):
    """Hide template badge when viewing locked template."""
    if self.template_badge:
        self.template_badge.place_forget()
```

#### _apply_all_changes() - Clear Badge After Save
```python
def _apply_all_changes(self):
    # ... save all data ...
    
    # Clear unsaved state after successful save
    self.changes_made = {
        'monsters_changed': False, 
        'skills_changed': False, 
        'timing_applied': False
    }
    self._mark_unsaved(False)  # ← Hide global badge
    
    # Show success message
    messagebox.showinfo(self._t('success_title'), self._t('changes_applied'))
```

---

## 🎨 Badge States & Behaviors

### Global Badge (Top Bar)

| Trigger | State | Badge | Position |
|---------|-------|-------|----------|
| Any tab changed | Has unsaved | 🟧 "CHƯA LƯU" | Top bar, right of 💾 |
| Click Save 💾 | All saved | ⚪ Hidden | - |
| Load window | No changes | ⚪ Hidden | - |

**Tracking Logic**:
```python
self.changes_made = {
    'monsters_changed': False,   # Tab 1: Quái Vật
    'skills_changed': False,     # Tab 2: Kỹ Năng
    'timing_applied': False      # Tab 3: Timing
}

# Show badge if ANY tab has changes
if any(self.changes_made.values()):
    self._mark_unsaved(True)
```

### Template Badge (Monster Tab)

| Trigger | State | Badge | Position |
|---------|-------|-------|----------|
| Select template | Locked | ⚪ Hidden | - |
| Click Edit ✏️ | Unlocked | 🟧 "Đang chỉnh sửa" | Template title, right |
| Edit fields | Unlocked | 🟧 "Đang chỉnh sửa" | Template title, right |
| Click Save 💾 | Locked | 🟩 "Đã lưu" (3s) | Template title, right |
| After 3s | Locked | ⚪ Hidden | - |

---

## 🔍 Before vs After Comparison

### Before (WRONG)

**Problem 1**: Badge position ambiguous
```
┌────────────────────────────────────┐
│ [Title] [💾] [✖]                   │
├────────────────────────────────────┤
│ [Tab: Quái] [CHƯA LƯU] ← ???      │  ← Badge in tab area
│                                    │     Is this for tab or global?
│  Template editing...               │
│  [Template] [CHƯA LƯU] ← ???      │  ← Another badge in form
└────────────────────────────────────┘     Which one to trust?
```

**Problem 2**: Badge conflict
- Global badge and template badge use same `self.unsaved_badge` widget
- Template methods overwrite global badge
- User sees wrong state

### After (CORRECT)

**Solution**: Clear separation
```
┌────────────────────────────────────┐
│ [Title] [CHƯA LƯU] [💾] [✖]       │  ← GLOBAL badge (all tabs)
├────────────────────────────────────┤
│ [Tab: Quái] [Tab: Skill] [Timing] │
│                                    │
│  [Template Title] [Đang chỉnh sửa]│  ← TEMPLATE badge (editing)
│  Template fields...                │
└────────────────────────────────────┘
```

**Benefits**:
- ✅ Global badge clearly visible near Save button
- ✅ Template badge stays in context (template form)
- ✅ No conflict - separate widgets
- ✅ User knows exactly what needs saving

---

## 🧪 Testing Scenarios

### Test 1: Global Badge - Monster Tab Changes
**Steps**:
1. Open Library Manager
2. Tab "Quái Vật" → Add/edit/delete monster
3. Check top bar

**Expected**:
- ✅ Global badge "CHƯA LƯU" appears in top bar (right of 💾)
- ✅ Badge visible from ANY tab (switch tabs to verify)
- ✅ Click 💾 → Badge disappears

### Test 2: Global Badge - Skill Tab Changes
**Steps**:
1. Tab "Kỹ Năng" → Add/edit/delete skill
2. Check top bar
3. Switch to other tabs

**Expected**:
- ✅ Global badge "CHƯA LƯU" appears in top bar
- ✅ Badge stays visible when switching tabs
- ✅ Click 💾 → Badge disappears

### Test 3: Global Badge - Timing Tab Changes
**Steps**:
1. Tab "Timing" → Apply timing recommendation
2. Check top bar

**Expected**:
- ✅ Global badge "CHƯA LƯU" appears in top bar
- ✅ Click 💾 → Badge disappears

### Test 4: Template Badge - Independent from Global
**Steps**:
1. Tab "Quái Vật" → Select template
2. Click ✏️ Edit → Edit template name
3. Observe BOTH badges

**Expected**:
- ✅ **Global badge** "CHƯA LƯU" in top bar (monsters changed)
- ✅ **Template badge** "Đang chỉnh sửa" (orange) in template form
- ✅ Two badges visible simultaneously, no conflict
- ✅ Click template 💾 → Template badge → "Đã lưu" (green, 3s)
- ✅ Global badge stays "CHƯA LƯU" (main form not saved yet)
- ✅ Click main 💾 → Global badge disappears

### Test 5: Multiple Tabs Changed
**Steps**:
1. Tab "Quái Vật" → Edit monster
2. Tab "Kỹ Năng" → Edit skill
3. Tab "Timing" → Apply timing
4. Switch between tabs

**Expected**:
- ✅ Global badge "CHƯA LƯU" visible in all tabs
- ✅ Badge position fixed in top bar
- ✅ Badge doesn't move when switching tabs
- ✅ Click 💾 → All changes saved → Badge disappears

### Test 6: Save and Badge Disappear
**Steps**:
1. Make changes in any tab
2. Global badge appears
3. Click 💾 Save button
4. Wait for success message

**Expected**:
- ✅ Success message shown
- ✅ Global badge disappears immediately
- ✅ Window closes (or stays open based on settings)

---

## 📁 Files Modified

**File**: `lib/ui/library_manager.py`

**Line Changes**:
- Line 476: Added `self.template_badge = None` (NEW)
- Lines 881-886: Created global badge in `top_bar` (NEW location)
- Line 1473: Changed `self.unsaved_badge` → `self.template_badge`
- Lines 548-557: Updated `_mark_unsaved()` - use `pack()` instead of `place()`
- Lines 1758-1796: Updated template badge methods to use `self.template_badge`
- Lines 3204-3206: Added badge clear in `_apply_all_changes()` (NEW)

**Total**: ~20 lines modified, ~6 lines added

---

## 🎓 Design Principles Applied

### 1. Separation of Concerns
**Problem**: One badge for multiple purposes
**Solution**: 
- Global badge → Global state (all tabs)
- Template badge → Template editing state (monster tab only)

### 2. Visual Hierarchy
**Problem**: Badge hidden in tab area, not visible
**Solution**: Badge in top bar, always visible, near related action (Save button)

### 3. Contextual Feedback
**Problem**: Badge far from action button
**Solution**: Badge right next to Save button - clear relationship

### 4. Consistency
**Principle**: Badge position stable across tab switches
**Implementation**: Badge in parent frame (`top_bar`), not in tab content

---

## ✅ Benefits

### User Experience
- 🎯 **Clear Global State**: Badge in top bar shows total unsaved changes
- 👀 **Always Visible**: Badge stays visible when switching tabs
- 🔗 **Near Action**: Badge right next to Save button - clear relationship
- 🧠 **Reduced Confusion**: No ambiguity - global badge for global state

### Technical
- 🏗️ **Better Architecture**: Separate widgets for separate purposes
- 🐛 **No Conflicts**: Template badge doesn't overwrite global badge
- 🔧 **Easier Maintenance**: Clear separation of concerns
- 📊 **Accurate Tracking**: Badge reflects changes from all 3 tabs

### Code Quality
- ✨ **Clean Code**: Each badge has single responsibility
- 📝 **Self-Documenting**: Method names clearly indicate badge type
- 🛡️ **Type Safe**: Separate attributes prevent accidental overwrites
- 🧪 **Testable**: Each badge can be tested independently

---

## 📚 Related Documentation

- **Previous**: `docs/sprints/sprint19/BUGFIX_TEMPLATE_BADGE_PREMATURE_DISPLAY.md` - Fixed template badge timing
- **Related**: `docs/UPDATE_TEMPLATE_INSTANT_SAVE.md` - Template instant save feature
- **Context**: `docs/sprints/sprint19/SPRINT19_SUMMARY.md` - Sprint overview

---

## 🔮 Future Enhancements

### Potential Improvements
1. **Badge Counter**: Show number of unsaved items
   ```
   [CHƯA LƯU (3)]  ← Shows 3 items changed
   ```

2. **Tab-Specific Indicators**: Small dots on tab labels
   ```
   [Quái Vật •] [Kỹ Năng •] [Timing]  ← • = has changes
   ```

3. **Hover Details**: Tooltip showing which tabs have changes
   ```
   Hover badge → "Changes: Quái Vật, Kỹ Năng"
   ```

4. **Color Coding**: Different colors for different change types
   ```
   🟡 Yellow: Draft/editing
   🟠 Orange: Unsaved changes
   🔴 Red: Conflicts/errors
   ```

---

**Status**: ✅ Production Ready  
**Impact**: High (UX clarity improvement)  
**Risk**: Low (non-breaking change)
