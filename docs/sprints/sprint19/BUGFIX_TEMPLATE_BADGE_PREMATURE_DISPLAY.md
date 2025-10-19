# Bugfix: Template Badge Hiển Thị Sai Thời Điểm

**Date**: October 19, 2025  
**Status**: ✅ Fixed  
**Issue**: Badge "Chưa lưu" hiển thị ngay khi chọn template, dù chưa có chỉnh sửa

---

## 🐛 Vấn Đề

### Mô tả
Trong tab **Thư viện Quái Vật**, khi người dùng chọn template (hoặc hệ thống tự động chọn template đầu tiên), badge "CHƯA LƯU" / "UNSAVED" xuất hiện ngay lập tức, dù:

- ❌ Template đang ở trạng thái **locked** (readonly)
- ❌ Người dùng **chưa nhấn** nút ✏️ để mở khóa
- ❌ **Chưa có** bất kỳ thay đổi nào

### Ảnh hưởng
- 😕 **Gây nhầm lẫn**: Người dùng nghĩ họ đã thay đổi gì đó
- 😟 **Gây lo lắng**: Sợ mất dữ liệu khi chưa làm gì
- 🎨 **UI lộn xộn**: Badge xuất hiện không cần thiết
- ❌ **Sai logic**: Trạng thái không phản ánh hành vi thực tế

### Nguyên nhân

#### 1. Badge hiển thị sai thời điểm
**File**: `lib/ui/library_manager.py`  
**Method**: `_select_template_by_index()`

```python
def _select_template_by_index(self, idx: int):
    # ... load template data ...
    
    # Lock fields after selection
    self._lock_template_fields()
    
    # ❌ WRONG: Call _mark_unsaved() even when just viewing
    try:
        self._mark_unsaved(any(self.changes_made.values()))
    except Exception:
        pass
```

**Vấn đề**: 
- Template vừa được chọn → locked (readonly)
- Nhưng `_mark_unsaved()` vẫn được gọi → Badge "CHƯA LƯU" xuất hiện
- Không hợp lý vì chưa có editing nào

#### 2. Conflict giữa 2 badge systems
**Badge cũ** (Global unsaved):
```python
def _mark_unsaved(self, state: bool):
    # Display: "CHƯA LƯU" / "UNSAVED"
    # Position: relx=1.0, x=-12, rely=0.5, anchor='e'
    # Color: UI.COLOR_WARNING
```

**Badge mới** (Template editing):
```python
def _show_editing_badge(self):
    # Display: "Đang chỉnh sửa" / "Editing"
    # Position: relx=1.0, x=-15, y=12, anchor='e'
    # Color: #FF9800 (Orange)

def _show_saved_badge(self):
    # Display: "Đã lưu" / "Saved"
    # Position: relx=1.0, x=-15, y=12, anchor='e'
    # Color: #4CAF50 (Green)
```

**Conflict**: Cùng sử dụng `self.unsaved_badge` widget → Ghi đè lẫn nhau

#### 3. Template change callbacks gọi _mark_unsaved()
**Các trace callbacks**:
- `_on_template_name_change()`
- `_on_template_path_change()`
- `_on_template_threshold_change()`
- `_on_template_region_change()`

Tất cả đều gọi:
```python
self.changes_made['monsters_changed'] = True
self._mark_unsaved(True)  # ← Conflict with template badge
```

**Vấn đề**: Badge orange "Đang chỉnh sửa" bị ghi đè bởi badge "CHƯA LƯU"

---

## ✅ Giải Pháp

### 1. Ẩn badge khi chọn template (locked state)

**Before**:
```python
def _select_template_by_index(self, idx: int):
    # ... load data ...
    self._lock_template_fields()
    # Show "CHƯA LƯU" badge ← WRONG
    self._mark_unsaved(any(self.changes_made.values()))
```

**After**:
```python
def _select_template_by_index(self, idx: int):
    # ... load data ...
    self._lock_template_fields()
    # Hide badge when just viewing (locked state) ← CORRECT
    self._hide_template_badge()
```

### 2. Tạo method _hide_template_badge()

**NEW**:
```python
def _hide_template_badge(self):
    """Hide template badge (used when viewing locked template)."""
    try:
        if self.unsaved_badge:
            self.unsaved_badge.place_forget()
    except Exception:
        pass
```

**Purpose**: Ẩn badge khi template ở trạng thái locked (view-only)

### 3. Xóa _mark_unsaved() khỏi template callbacks

#### _on_template_name_change()
**Before**:
```python
self.changes_made['monsters_changed'] = True
try:
    self._mark_unsaved(True)  # ← Conflict
except Exception:
    pass
```

**After**:
```python
self.changes_made['monsters_changed'] = True
# Badge already shown by unlock action - no need to mark unsaved here
```

#### _on_template_path_change()
**Before**:
```python
self.changes_made['monsters_changed'] = True
try:
    self._mark_unsaved(True)  # ← Conflict
except Exception:
    pass
```

**After**:
```python
self.changes_made['monsters_changed'] = True
# Badge already shown by unlock action - no need to mark unsaved here
```

#### _on_template_threshold_change()
**Before**:
```python
self.changes_made['monsters_changed'] = True
try:
    self._mark_unsaved(True)  # ← Conflict
except Exception:
    pass
```

**After**:
```python
self.changes_made['monsters_changed'] = True
# Badge already shown by unlock action - no need to mark unsaved here
```

#### _on_template_region_change()
**Before**:
```python
self.changes_made['monsters_changed'] = True
try:
    self._mark_unsaved(True)  # ← Conflict
except Exception:
    pass
```

**After**:
```python
self.changes_made['monsters_changed'] = True
# Badge already shown by unlock action - no need to mark unsaved here
```

---

## 🎯 Logic Mới (Đúng)

### UX Flow - Template Badge States

```
┌─────────────────────────────────────┐
│ 1. Chọn Template                    │
│    State: 🔒 LOCKED (readonly)      │
│    Badge: ⚪ HIDDEN (no badge)      │
│    Button: ✏️ Edit                  │
└─────────────────────────────────────┘
            ↓ Click ✏️
┌─────────────────────────────────────┐
│ 2. Unlock Template                  │
│    State: 🔓 UNLOCKED (editable)    │
│    Badge: 🟧 "Đang chỉnh sửa"       │
│    Button: 💾 Save                  │
└─────────────────────────────────────┘
            ↓ Edit fields...
┌─────────────────────────────────────┐
│ 3. Editing                          │
│    State: 🔓 UNLOCKED (editable)    │
│    Badge: 🟧 "Đang chỉnh sửa"       │
│    Button: 💾 Save                  │
└─────────────────────────────────────┘
            ↓ Click 💾
┌─────────────────────────────────────┐
│ 4. Save & Lock                      │
│    State: 🔒 LOCKED (readonly)      │
│    Badge: 🟩 "Đã lưu" (3s)          │
│    Button: ✏️ Edit                  │
└─────────────────────────────────────┘
            ↓ After 3 seconds
┌─────────────────────────────────────┐
│ 5. Back to Locked View              │
│    State: 🔒 LOCKED (readonly)      │
│    Badge: ⚪ HIDDEN (auto-hide)     │
│    Button: ✏️ Edit                  │
└─────────────────────────────────────┘
```

### Badge Display Rules

| Trigger | State | Badge | Color | Duration |
|---------|-------|-------|-------|----------|
| **Select template** | Locked | ⚪ Hidden | - | Permanent |
| **Click Edit ✏️** | Unlocked | 🟧 "Đang chỉnh sửa" | Orange #FF9800 | Until save |
| **Field changes** | Unlocked | 🟧 "Đang chỉnh sửa" | Orange #FF9800 | Until save |
| **Click Save 💾** | Locked | 🟩 "Đã lưu" | Green #4CAF50 | 3 seconds |
| **After 3s** | Locked | ⚪ Hidden | - | Permanent |

---

## 📊 Impact

### Before Fix (Wrong)

**Scenario 1**: Chọn template
```
User: Chọn "Coc go 7"
System: Load data → Lock fields
Badge: 🔴 "CHƯA LƯU" (WRONG - chưa edit gì)
User: 😕 "Tôi có thay đổi gì không?"
```

**Scenario 2**: Unlock và edit
```
User: Click ✏️ → Edit name
Badge: 🟠 "Đang chỉnh sửa" (Correct)
Callback: _on_template_name_change()
Badge: 🔴 "CHƯA LƯU" (Conflict - ghi đè badge orange)
User: 😟 "Badge đổi màu tự nhiên?"
```

### After Fix (Correct)

**Scenario 1**: Chọn template
```
User: Chọn "Coc go 7"
System: Load data → Lock fields
Badge: ⚪ Hidden (CORRECT - just viewing)
User: 😊 "OK, đang xem template"
```

**Scenario 2**: Unlock và edit
```
User: Click ✏️
Badge: 🟧 "Đang chỉnh sửa" (Show immediately)
User: Edit name → Edit threshold
Badge: 🟧 "Đang chỉnh sửa" (Stable - không ghi đè)
User: 😊 "Badge ổn định, dễ hiểu"
```

**Scenario 3**: Save
```
User: Click 💾
System: Save → Lock fields
Badge: 🟩 "Đã lưu" (Green, 3s)
After 3s: Badge hidden automatically
User: 😊 "Clear feedback, không rối"
```

---

## 🧪 Testing

### Test Case 1: Badge Hidden on Template Selection
**Steps**:
1. Open Library Manager
2. Tab "Thư viện Quái Vật"
3. Select monster "Coc go~"
4. Observe template list auto-selects first template

**Expected**:
- ✅ Template fields are **readonly** (locked)
- ✅ Button shows **✏️ Edit**
- ✅ **NO badge** displayed
- ❌ **NOT** showing "Chưa lưu" or "UNSAVED"

### Test Case 2: Badge Shows on Unlock
**Steps**:
1. With template selected and locked
2. Click ✏️ Edit button

**Expected**:
- ✅ Template fields become **editable**
- ✅ Button changes to **💾 Save**
- ✅ Badge shows **🟧 "Đang chỉnh sửa"** (Orange)

### Test Case 3: Badge Remains During Editing
**Steps**:
1. With template unlocked
2. Edit name: "Coc go 7" → "Coc go 7 updated"
3. Edit threshold: "0.8" → "0.85"
4. Edit region: Change width value

**Expected**:
- ✅ Badge **remains stable**: 🟧 "Đang chỉnh sửa"
- ❌ **NOT** changing to "CHƯA LƯU"
- ❌ **NOT** flickering or disappearing

### Test Case 4: Badge Changes on Save
**Steps**:
1. With template unlocked and edited
2. Click 💾 Save button

**Expected**:
- ✅ Badge changes to **🟩 "Đã lưu"** (Green)
- ✅ Fields become **readonly** (locked)
- ✅ Button changes to **✏️ Edit**
- ✅ After **3 seconds**, badge **auto-hides**

### Test Case 5: Badge Hidden After Auto-Hide
**Steps**:
1. After saving template
2. Wait 3+ seconds
3. Observe badge area

**Expected**:
- ✅ Badge is **completely hidden**
- ✅ Template remains **locked**
- ✅ Button shows **✏️ Edit**

### Test Case 6: Multiple Template Switches
**Steps**:
1. Select template "Coc go 1" → Badge hidden ✅
2. Click ✏️ → Badge "Đang chỉnh sửa" 🟧
3. Click 💾 → Badge "Đã lưu" 🟩 (3s)
4. Select template "Coc go 2" → Badge hidden ✅
5. Click ✏️ → Badge "Đang chỉnh sửa" 🟧

**Expected**:
- ✅ Each selection → Badge hidden
- ✅ Each unlock → Badge "Đang chỉnh sửa"
- ✅ Each save → Badge "Đã lưu" → Hidden
- ✅ No badge conflicts or flickering

---

## 📝 File Changes

### Modified File
**File**: `lib/ui/library_manager.py`

**Changes**:
1. `_select_template_by_index()` (Line ~1610)
   - Replaced: `self._mark_unsaved(any(...))`
   - With: `self._hide_template_badge()`

2. NEW METHOD: `_hide_template_badge()` (Line ~1791)
   - Hide badge when template locked

3. `_on_template_name_change()` (Line ~1827)
   - Removed: `self._mark_unsaved(True)`
   - Added comment: "Badge already shown by unlock action"

4. `_on_template_path_change()` (Line ~1854)
   - Removed: `self._mark_unsaved(True)`
   - Added comment: "Badge already shown by unlock action"

5. `_on_template_threshold_change()` (Line ~1874)
   - Removed: `self._mark_unsaved(True)`
   - Added comment: "Badge already shown by unlock action"

6. `_on_template_region_change()` (Line ~180)
   - Removed: `self._mark_unsaved(True)`
   - Added comment: "Badge already shown by unlock action"

**Total**: 6 changes, ~10 lines modified

---

## 🎓 Lessons Learned

### 1. Badge System Separation
**Problem**: Dùng chung 1 widget cho 2 purposes khác nhau
- Global unsaved badge (`_mark_unsaved`)
- Template editing badge (`_show_editing_badge`)

**Solution**: 
- Tách biệt rõ ràng contexts:
  - Template editing → Use template badge (orange/green)
  - Global form → Use global badge (if needed)

### 2. State-Based UI
**Principle**: UI elements phải phản ánh state hiện tại
- Locked (view-only) → NO badge
- Unlocked (editing) → Orange badge
- Just saved → Green badge (temporary)

### 3. Avoid Premature Indication
**Problem**: Badge xuất hiện khi không cần thiết
**Solution**: Chỉ hiển thị khi có **action thực sự** từ user

### 4. Callback Consistency
**Problem**: Callbacks conflict với main badge system
**Solution**: 
- Kiểm tra state trước khi display badge
- Không gọi global badge từ specific context (template)

---

## ✅ Summary

**Fixed**:
✅ Badge không còn xuất hiện sai thời điểm khi chọn template  
✅ Badge ẩn hoàn toàn khi template locked  
✅ Badge "Đang chỉnh sửa" (orange) xuất hiện khi unlock  
✅ Badge ổn định, không bị ghi đè bởi callbacks  
✅ Badge "Đã lưu" (green) xuất hiện sau save, tự ẩn sau 3s  
✅ UX logic rõ ràng, dễ hiểu, phản ánh đúng hành vi  

**Benefits**:
- 🎨 UI gọn gàng, không rối
- 😊 Người dùng không bị nhầm lẫn
- 🎯 Trạng thái badge phản ánh đúng action
- 🔒 Locked = hidden badge (just viewing)
- 🔓 Unlocked = orange badge (editing)
- 💾 Saved = green badge (feedback) → auto-hide

**Status**: ✅ Production Ready
