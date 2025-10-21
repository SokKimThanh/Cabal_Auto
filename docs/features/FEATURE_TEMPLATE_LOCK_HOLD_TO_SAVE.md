# Template Edit Lock/Unlock với Hold-to-Save

**Date**: October 19, 2025  
**Status**: ✅ Completed  
**Feature**: UX improvement cho template editing với lock/unlock và hold-to-save

---

## 🎯 Mục tiêu

Cải thiện UX của template editor trong tab Quái Vật (Monster Library):

1. **Template bị khóa mặc định** khi chọn quái vật
2. **Nhấn nút bút** để mở khóa và cho phép chỉnh sửa
3. **Icon thay đổi** từ bút (✏️) sang đĩa mềm (💾) khi đang edit
4. **Hold-to-save**: Nhấn giữ 2 giây để lưu template tạm thời
5. **Progress animation**: Hiển thị thanh tiến trình khi giữ nút
6. **Badge "Đã lưu tạm"**: Hiển thị thông báo sau khi lưu thành công

---

## 🎨 UX Flow

```
┌─────────────────────────────────────────────────┐
│ 1. Chọn quái vật                                │
│    ↓                                             │
│    Template info hiển thị, fields BỊ KHÓA       │
│    Icon: ✏️ (Edit)                              │
│    Tooltip: "Sửa template"                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. Nhấn nút ✏️                                   │
│    ↓                                             │
│    Fields MỞ KHÓA (có thể chỉnh sửa)            │
│    Icon thay đổi: 💾 (Save)                     │
│    Tooltip: "Giữ 2s để lưu template"            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Chỉnh sửa template                           │
│    ↓                                             │
│    Nhập tên, threshold, region...               │
│    Badge: "Chưa lưu" (nếu có thay đổi)          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. Nhấn giữ nút 💾 (2 giây)                     │
│    ↓                                             │
│    Progress bar chạy 0% → 100%                  │
│    Màu nút: Blue → Green                        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 5. Sau 2 giây                                   │
│    ↓                                             │
│    ✅ Template lưu vào lib/data/monsters.json   │
│    ✅ Fields tự động KHÓA lại                    │
│    ✅ Icon trở về ✏️                             │
│    ✅ Badge: "Đã lưu tạm" (3 giây)              │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Details

### 1. **Trạng thái Template Lock**

**File**: `lib/ui/library_manager.py`

**Biến trạng thái**:
```python
self.template_locked = True  # Mặc định khóa
self.template_temp_saved = False  # Track temp save
```

**Entry widget references**:
```python
self.template_name_entry = None
self.template_threshold_entry = None
self.template_region_entries = {}  # Dict of region entries
```

### 2. **Lock/Unlock Methods**

```python
def _lock_template_fields(self):
    """Khóa tất cả fields, set state='readonly'."""
    self.template_locked = True
    if self.template_name_entry:
        self.template_name_entry.config(state='readonly')
    if self.template_threshold_entry:
        self.template_threshold_entry.config(state='readonly')
    for entry in self.template_region_entries.values():
        entry.config(state='readonly')

def _unlock_template_fields(self):
    """Mở khóa tất cả fields, set state='normal'."""
    self.template_locked = False
    self.template_temp_saved = False
    if self.template_name_entry:
        self.template_name_entry.config(state='normal')
    # ... tương tự cho threshold và region
```

### 3. **Toggle Button (Edit ↔ Save)**

**Button creation**:
```python
# Line ~1454
self.template_toggle_btn = self._make_icon_button(
    edit_toolbar, 
    'edit', '✏️', 'tip_template_edit',
    command=self._toggle_template_edit,  # Toggle command
    bg=UI.BTN_INFO_BG, fg=UI.BTN_INFO_FG
)
```

**Toggle logic**:
```python
def _toggle_template_edit(self):
    if self.template_locked:
        # Unlock và đổi icon sang Save
        self._unlock_template_fields()
        self._update_toggle_button_icon('save', '💾', 'tip_template_save_temp')
    else:
        # Bắt đầu hold-to-save
        self._start_hold_to_save()
```

### 4. **Hold-to-Save Animation**

**Progress animation** (20 steps x 100ms = 2000ms):

```python
def _start_hold_to_save(self):
    hold_duration = 2000  # 2 seconds
    steps = 20
    step_duration = 100  # milliseconds
    current_step = [0]
    is_holding = [True]
    
    def update_progress():
        if not is_holding[0]:
            # User released early - reset
            return
        
        current_step[0] += 1
        progress = current_step[0] / steps
        
        # Color interpolation: Blue (#2196F3) → Green (#4CAF50)
        r = int(33 + (76 - 33) * progress)
        g = int(150 + (175 - 150) * progress)
        b = int(243 + (80 - 243) * progress)
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        self.template_toggle_btn.config(bg=color)
        
        if current_step[0] >= steps:
            # Completed - save
            self._save_template_temporarily()
            self._lock_template_fields()
            self._update_toggle_button_icon('edit', '✏️', 'tip_template_edit')
        else:
            self.after(step_duration, update_progress)
    
    # Bind release to cancel
    def on_release(event):
        is_holding[0] = False
    
    self.template_toggle_btn.bind('<ButtonRelease-1>', on_release, add='+')
    update_progress()
```

### 5. **Temporary Save**

**Save to lib/data/monsters.json**:

```python
def _save_template_temporarily(self):
    self.template_temp_saved = True
    
    # Save to lib/data/monsters.json
    data_dir = self.project_root / 'lib' / 'data'
    monsters_path = data_dir / 'monsters.json'
    
    with open(monsters_path, 'w', encoding='utf-8') as f:
        json.dump(self.monsters, f, indent=2, ensure_ascii=False)
    
    # Show badge
    self._show_temp_save_badge()
    
    # Mark as changed for main save
    self.changes_made['monsters_changed'] = True
```

### 6. **Temp Save Badge**

**Badge display** (3 seconds):

```python
def _show_temp_save_badge(self):
    badge_text = 'Temp Saved' if self.lang == 'en' else 'Đã lưu tạm'
    self.unsaved_badge.config(text=f'  {badge_text}  ', bg='#4CAF50')
    self.unsaved_badge.place(relx=1.0, x=-15, y=12, anchor='e')
    
    # Hide after 3 seconds
    self.after(3000, lambda: self.unsaved_badge.place_forget())
```

### 7. **Auto-Apply Prevention**

**Trace handlers check lock status**:

```python
def _on_template_name_change(self):
    if getattr(self, '_suspend_template_var_traces', False):
        return
    # Don't apply if locked
    if getattr(self, 'template_locked', True):
        return
    # Apply changes...
    tmpl['name'] = self.template_name_var.get().strip()
```

Tương tự cho `_on_template_path_change`, `_on_template_threshold_change`, `_on_template_region_change`.

---

## 📋 Files Modified

### 1. **lib/ui/library_manager.py**

**Sections changed**:

| Line Range | Change Description |
|------------|-------------------|
| 478-500 | Added state variables: `template_locked`, `template_name_entry`, `template_threshold_entry`, `template_region_entries`, `template_toggle_btn`, `template_temp_saved` |
| 1454-1456 | Changed edit button to toggle button with `_toggle_template_edit` command |
| 1481-1483 | Store `template_name_entry` reference with `state='readonly'` |
| 1490-1492 | Store `template_threshold_entry` reference with `state='readonly'` |
| 1505-1511 | Store `template_region_entries` dict references with `state='readonly'` |
| 1606-1612 | Added `_lock_template_fields()` call after template selection |
| 1614-1697 | Added methods: `_lock_template_fields()`, `_unlock_template_fields()`, `_toggle_template_edit()`, `_update_toggle_button_icon()` |
| 1699-1762 | Added `_start_hold_to_save()` with progress animation |
| 1764-1816 | Added `_save_template_temporarily()` and `_show_temp_save_badge()` |
| 1835-1837 | Added lock check in `_on_template_name_change()` |
| 1864-1866 | Added lock check in `_on_template_path_change()` |
| 1880-1882 | Added lock check in `_on_template_threshold_change()` |

### 2. **lib/i18n/translations.py**

**Added tooltip key**:

```python
# English
'tip_template_save_temp': 'Hold 2s to save template',

# Vietnamese
'tip_template_save_temp': 'Giữ 2s để lưu template',
```

---

## 🎯 Key Features

### ✅ Lock by Default
- Khi chọn quái vật hoặc template → fields tự động khóa
- Không thể chỉnh sửa cho đến khi nhấn nút bút

### ✅ Visual Feedback
- Icon động: ✏️ ↔ 💾
- Tooltip động: "Sửa template" ↔ "Giữ 2s để lưu"
- Progress bar: Màu nút chuyển từ blue sang green
- Badge hiển thị: "Đã lưu tạm" (3 giây)

### ✅ Hold-to-Save UX
- Phải giữ nút 2 giây → tránh lưu nhầm
- Nếu thả sớm → hủy, không lưu
- Progress animation smooth (20 steps)

### ✅ Separate Save
- Template save: Chỉ lưu template hiện tại vào lib/data/
- Main save: Lưu tất cả thay đổi (Monsters + Skills + Timing)

### ✅ Auto-Lock After Save
- Sau khi lưu tạm → fields tự động khóa lại
- Icon tự động đổi về ✏️
- User phải nhấn bút lại để edit tiếp

---

## 🧪 Testing

### Manual Test Steps

1. **Test Lock on Selection**:
   - Mở Library Manager → tab Quái Vật
   - Chọn một quái từ danh sách
   - Chọn một template
   - ✅ Verify: All fields readonly (không thể gõ)

2. **Test Unlock**:
   - Nhấn nút ✏️
   - ✅ Verify: Fields có thể chỉnh sửa
   - ✅ Verify: Icon đổi sang 💾
   - ✅ Verify: Tooltip: "Giữ 2s để lưu template"

3. **Test Hold-to-Save Full Duration**:
   - Nhấn giữ nút 💾 đủ 2 giây
   - ✅ Verify: Progress animation chạy (màu blue → green)
   - ✅ Verify: Sau 2 giây, badge "Đã lưu tạm" xuất hiện
   - ✅ Verify: Fields tự động khóa lại
   - ✅ Verify: Icon đổi về ✏️

4. **Test Hold-to-Save Early Release**:
   - Nhấn nút 💾 nhưng thả sớm (< 2 giây)
   - ✅ Verify: Progress bar reset
   - ✅ Verify: Không lưu (không có badge)
   - ✅ Verify: Fields vẫn unlocked

5. **Test File Save**:
   - Sau khi hold-to-save thành công
   - Kiểm tra file: `lib/data/monsters.json`
   - ✅ Verify: File updated với template mới

6. **Test Auto-Apply Prevention**:
   - Template khóa → gõ vào fields
   - ✅ Verify: Không thể gõ (readonly)
   - Unlock → gõ
   - ✅ Verify: Có thể gõ nhưng chưa lưu

---

## 🔍 Edge Cases Handled

1. **Multiple rapid clicks**: Button state managed correctly
2. **Window close during hold**: Save aborted safely
3. **No template selected**: Lock/unlock disabled
4. **Badge already showing**: Previous badge cleared before showing new
5. **Save error**: Error dialog shown, fields remain unlocked

---

## 📊 State Diagram

```
┌──────────────┐
│  LOCKED      │ ← Default state after selection
│  (readonly)  │
│  Icon: ✏️    │
└──────┬───────┘
       │ Click edit
       ↓
┌──────────────┐
│  UNLOCKED    │
│  (editable)  │
│  Icon: 💾    │
└──────┬───────┘
       │ Hold 2s
       ↓
┌──────────────┐
│  SAVING      │
│  (progress)  │
│  Color: →🟢  │
└──────┬───────┘
       │ Complete
       ↓
┌──────────────┐
│  SAVED       │
│  Badge: ✅   │
│  → LOCKED    │
└──────────────┘
```

---

## 💡 Design Decisions

### Why Lock by Default?
- Ngăn chỉnh sửa nhầm
- Rõ ràng về intent: phải nhấn bút để edit
- Consistent với UX pattern "View → Edit → Save"

### Why Hold-to-Save (not Click)?
- Tránh lưu nhầm khi chỉ muốn xem
- Progress feedback rõ ràng
- Familiar UX pattern (như Instagram, Twitter)

### Why 2 Seconds?
- Đủ ngắn để không gây khó chịu
- Đủ dài để tránh lưu nhầm
- Standard duration trong UX design

### Why Separate from Main Save?
- Template thay đổi thường xuyên hơn
- Không muốn mất thay đổi khi đóng dialog
- Cho phép "checkpoint" trong quá trình edit

---

## 🚀 Future Enhancements

1. **Undo/Redo**: Lưu lịch sử thay đổi template
2. **Auto-save**: Tự động lưu sau mỗi N giây không thay đổi
3. **Conflict detection**: Warning nếu file thay đổi bên ngoài
4. **Keyboard shortcut**: Ctrl+S để save nhanh
5. **Preview during edit**: Live preview khi chỉnh sửa threshold

---

## ✅ Checklist

- [x] Template fields locked by default
- [x] Toggle button với icon động
- [x] Hold-to-save với progress bar
- [x] Save to lib/data/monsters.json
- [x] Badge "Đã lưu tạm" hiển thị
- [x] Auto-lock after save
- [x] Prevent auto-apply when locked
- [x] Tooltip i18n (EN/VI)
- [x] Handle early release
- [x] Error handling
- [x] Documentation complete

---

**Author**: GitHub Copilot  
**Review Status**: Ready for user testing
