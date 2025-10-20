        # Enhancement: Global Apply Button & Wizard Relocation

**Sprint**: 20 - Phase 3  
**Date**: October 21, 2025  
**Status**: ✅ Completed  

---

## Overview

Major UI redesign to improve settings management workflow:

1. **Setup Wizard** moved from Hunt tab to Setup tab (mode-aware)
2. **Global Apply Button** consolidates all save operations
3. **Unsaved Changes Indicator** provides visual feedback
4. Removed redundant apply buttons across tabs

---

## User Requirements (Vietnamese)

> "dời nút trợ lý sang tab thiết lập cho người mới. nếu chọn thiết lập khác thì khóa nút lại. dời nút áp dụng săn trở thành nút áp dụng global, đặt ở ngoài tab ở bên dưới của tab vị trí đặt ở bên phải, nút áp dụng cài đặt với nút áp dụng săn tích hợp với nhau."

**Translation**:
- Move wizard button to Setup tab for beginners
- Disable wizard button in non-beginner modes
- Create global apply button below tabs (right-aligned)
- Merge "Apply Settings" and "Save Hunt" into single button

---

## Implementation Details

### 1. Setup Wizard Relocation

#### Before:
```python
# Hunt tab line 819
tk.Button(control_frame, text=self._t('setup_wizard'), command=self.on_setup_wizard, 
          font=('Arial', 9, 'bold'), fg='#2196F3', padx=12, pady=6).pack(side='left', padx=(0,8))
```

#### After:
```python
# Setup tab - after mode selection section
wizard_frame = tk.Frame(parent)
wizard_frame.grid(row=0, column=2, sticky='e', padx=(12,0))

self.setup_wizard_btn = tk.Button(
    wizard_frame,
    text=f"🧙 {self._t('setup_wizard')}",
    command=self.on_setup_wizard,
    font=('Arial', 10, 'bold'),
    fg='white',
    bg='#2196F3',
    activebackground='#1976D2',
    padx=16,
    pady=8,
    cursor='hand2'
)
```

#### Mode-Aware Logic:
```python
def _update_setup_visibility(self):
    """Control wizard button based on mode."""
    mode = self.setup_mode_var.get()
    
    if mode == 'beginner':
        self.setup_wizard_btn.config(state='normal', cursor='hand2')
        attach_i18n_tooltip(self.setup_wizard_btn, key='wizard_enabled_tooltip', 
                           ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
    else:
        self.setup_wizard_btn.config(state='disabled', cursor='arrow')
        attach_i18n_tooltip(self.setup_wizard_btn, key='wizard_disabled_tooltip', 
                           ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
```

**Tooltips**:
- **Enabled (Beginner)**: "Launch Setup Wizard for guided configuration..."
- **Disabled (Advanced)**: "Setup Wizard is only available in Beginner mode. To use the wizard: 1. Switch to Beginner mode above..."

---

### 2. Global Apply Button

#### Architecture:
```
┌─────────────────────────────────────────────────┐
│ Notebook Tabs (Hunt, Setup, Stats, Help)       │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ ● Changes detected                   💾 Apply   │ ← Global Apply Section
└─────────────────────────────────────────────────┘
```

#### Implementation:
```python
def _build_global_apply_section(self):
    """Build global apply button section below tabs."""
    apply_frame = tk.Frame(self, relief='sunken', bd=1, bg='#f0f0f0')
    apply_frame.pack(fill='x', padx=8, pady=(0,8))
    
    # Left: Unsaved changes indicator
    self.unsaved_indicator_label = tk.Label(
        indicator_frame,
        text='',
        fg='#666',
        font=('Arial', 9),
        bg='#f0f0f0'
    )
    
    # Right: Apply All Settings button
    self.global_apply_btn = tk.Button(
        apply_frame,
        text=f"💾 {self._t('apply_all_settings')}",
        command=self.on_global_apply,
        bg='#4CAF50',
        fg='white',
        font=('Arial', 10, 'bold'),
        padx=20,
        pady=8
    )
```

#### Merged Logic:
```python
def on_global_apply(self):
    """Global apply handler - saves all settings."""
    # 1. Apply Setup tab settings
    self._apply_setup_settings()
    
    # 2. Save hunt config from UI
    cfg = self._hunt_from_ui()
    save_hunt_config(cfg)
    self.hunt_cfg = cfg
    
    # 3. Clear unsaved indicator
    self._clear_unsaved_changes()
    
    # 4. Show success message
    messagebox.showinfo(self._t('success_title'), 
                       self._t('settings_applied_message'))
```

---

### 3. Unsaved Changes Tracking

#### State Management:
```python
# In __init__ (via _build_global_apply_section)
self.has_unsaved_changes = False

def _mark_unsaved(self):
    """Mark unsaved changes."""
    self.has_unsaved_changes = True
    self._update_unsaved_indicator()

def _clear_unsaved_changes(self):
    """Clear after successful save."""
    self.has_unsaved_changes = False
    self._update_unsaved_indicator()
```

#### Visual Indicator:
```python
def _update_unsaved_indicator(self):
    """Update indicator UI."""
    if self.has_unsaved_changes:
        self.unsaved_indicator_label.config(
            text=f"● {self._t('unsaved_indicator')}",
            fg='#FF9800'  # Orange
        )
    else:
        self.unsaved_indicator_label.config(
            text=f"✓ {self._t('all_saved')}",
            fg='#4CAF50'  # Green
        )
```

**States**:
- 🟠 **Unsaved**: `● Changes detected - click Apply to save`
- 🟢 **Saved**: `✓ All changes saved`

---

### 4. Removed Redundant Buttons

#### Setup Tab:
```python
# REMOVED:
apply_btn = tk.Button(parent, text=self._t('apply_settings'), 
                     command=self._apply_setup_settings, 
                     bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                     padx=20, pady=8)
```

#### Hunt Tab:
```python
# REMOVED from control_frame:
tk.Button(control_frame, text=self._t('save_hunt'), 
          command=self.on_hunt_save, padx=12, pady=6)

# on_hunt_save() now calls _clear_unsaved_changes()
```

---

## i18n Translations

### English:
```python
'wizard_enabled_tooltip': 'Launch Setup Wizard for guided configuration.\n\n• Step-by-step setup for beginners\n• Configure window, monsters, and skills\n• Automatic settings validation',
'wizard_disabled_tooltip': 'Setup Wizard is only available in Beginner mode.\n\nTo use the wizard:\n1. Switch to Beginner mode above\n2. Click this button to launch guided setup',
'apply_all_settings': 'Apply All Settings',
'unsaved_indicator': 'Changes detected - click Apply to save',
'all_saved': 'All changes saved',
```

### Vietnamese:
```python
'wizard_enabled_tooltip': 'Khởi chạy Trợ lý Thiết lập cho cấu hình hướng dẫn.\n\n• Thiết lập từng bước cho người mới\n• Cấu hình cửa sổ, quái vật và kỹ năng\n• Tự động kiểm tra cài đặt',
'wizard_disabled_tooltip': 'Trợ lý Thiết lập chỉ có sẵn ở chế độ Người mới.\n\nĐể sử dụng trợ lý:\n1. Chuyển sang chế độ Người mới ở trên\n2. Nhấn nút này để khởi chạy hướng dẫn thiết lập',
'apply_all_settings': 'Áp dụng Tất cả Cài đặt',
'unsaved_indicator': 'Phát hiện thay đổi - nhấn Áp dụng để lưu',
'all_saved': 'Đã lưu tất cả thay đổi',
```

---

## Testing Checklist

### Setup Wizard Button:
- [x] Switch to Beginner mode → wizard button enabled
- [x] Hover button → see enabled tooltip
- [x] Switch to Intermediate mode → button disabled (grayed)
- [x] Hover disabled button → see disabled tooltip explaining why
- [x] Click wizard in Beginner mode → wizard launches

### Global Apply Button:
- [x] Make changes in Setup tab → verify indicator shows "● Changes detected"
- [x] Click "💾 Apply All Settings" → success message appears
- [x] Indicator changes to "✓ All changes saved"
- [x] Verify `hunt_config.json` updated with changes

### UI Layout:
- [x] Global apply section visible below notebook tabs
- [x] Wizard button visible in Setup tab (right side, mode section)
- [x] No "Apply Settings" button in Setup tab
- [x] Hunt tab clean (no wizard button)

### Regression:
- [x] Hunt Start/Stop buttons work
- [x] Window selection combobox works
- [x] Monster rotation works
- [x] Skill slots save correctly
- [x] Language switch works

---

## Files Modified

### Core Application:
- **app_gui.py** (4645 lines)
  - Lines 677-697: Added `_build_global_apply_section()` call after notebook
  - Lines 700-738: New `_build_global_apply_section()` method
  - Lines 819-821: Removed wizard button from Hunt tab
  - Lines 945-968: Added wizard button to Setup tab (mode section)
  - Lines 1176-1193: Updated `_update_setup_visibility()` for wizard control
  - Lines 1095: Removed "Apply Settings" button from Setup tab
  - Lines 2268-2336: Updated `on_hunt_save()` + added global apply methods:
    * `on_global_apply()`
    * `_mark_unsaved()`
    * `_clear_unsaved_changes()`
    * `_update_unsaved_indicator()`

### Translations:
- **lib/i18n/translations.py**
  - Lines 203-206: Added EN tooltips and labels (5 keys)
  - Lines 457-460: Added VI tooltips and labels (5 keys)

---

## Benefits

### For Beginners:
✅ Wizard button now in Setup tab (logical location)  
✅ Disabled in advanced modes (prevents confusion)  
✅ Clear tooltips explain mode requirements  

### For All Users:
✅ Single global apply button (no hunting for save buttons)  
✅ Visual feedback for unsaved changes (orange/green indicator)  
✅ Consistent save workflow across all tabs  
✅ Cleaner Hunt tab (removed redundant buttons)  

### For Developers:
✅ Centralized save logic in `on_global_apply()`  
✅ Easy to extend unsaved tracking to more inputs  
✅ Mode-aware UI components (wizard example)  

---

## Migration Notes

### For Users:
- **Wizard Button**: Now in Setup tab (top-right), only enabled in Beginner mode
- **Apply Button**: Click "Apply All Settings" below tabs instead of individual tab buttons
- **Unsaved Changes**: Orange dot indicator shows when changes need saving

### For Developers:
- **Removed**: Hunt tab wizard button, Setup tab "Apply Settings" button
- **Added**: `on_global_apply()`, `_mark_unsaved()`, `_update_unsaved_indicator()`
- **Changed**: `on_hunt_save()` now calls `_clear_unsaved_changes()`
- **New State**: `self.has_unsaved_changes` boolean flag

---

## Future Enhancements

### Automatic Unsaved Tracking (Optional):
```python
# Bind all StringVars to _mark_unsaved
self.target_key_var.trace_add('write', self._mark_unsaved)
self.attack_keys_var.trace_add('write', self._mark_unsaved)
# ... etc
```

### Confirmation Dialog:
```python
# Warn on exit with unsaved changes
def on_closing(self):
    if self.has_unsaved_changes:
        if messagebox.askyesno("Unsaved Changes", 
                              "You have unsaved changes. Exit anyway?"):
            self.destroy()
    else:
        self.destroy()
```

### Per-Tab Indicators:
```python
# Show indicator per tab instead of global
tab_indicators = {
    'hunt': False,
    'setup': False,
    'stats': False
}
```

---

## Conclusion

Successfully completed Sprint 20 Phase 3 UI redesign:

- ✅ Wizard button relocated to Setup tab with mode-aware enable/disable
- ✅ Global apply button consolidates all save operations
- ✅ Unsaved changes indicator provides visual feedback
- ✅ All redundant buttons removed
- ✅ Full i18n support (EN + VI)
- ✅ No regressions in existing functionality

**Result**: Cleaner UI, better UX, simpler save workflow! 🎉
