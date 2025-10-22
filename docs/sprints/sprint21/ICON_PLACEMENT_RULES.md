# Icon Placement Rules - UI Design Guidelines

**Version**: 1.0  
**Date**: October 21, 2025  
**Sprint**: 21 Patch 15  

## 📐 Quy Tắc Tổng Quan

### 1. **Icon Position - Vị Trí Icon**

#### Action Buttons (Save, Delete, Add, Edit, Apply, Cancel, etc.)
- **Icon luôn ở bên TRÁI** (`compound='left'`)
- Lý do: Consistent với reading flow (trái→phải), icon làm visual anchor

```python
# ✅ ĐÚNG - Action button
button = tk.Button(
    text=" Save",
    image=save_icon,
    compound='left'  # Icon TRÁI
)
```

#### Navigation Buttons (Special Case)
- **Next/Forward**: Icon ở bên PHẢI (`compound='right'`) - directional cue
- **Back/Previous**: Icon ở bên TRÁI (`compound='left'`) - directional cue
- Lý do: Icon direction matches movement direction

```python
# ✅ ĐÚNG - Next button (icon phải)
next_btn = tk.Button(
    text="Next ",
    image=next_icon,  # → arrow
    compound='right'  # Icon PHẢI (đi về phía trước)
)

# ✅ ĐÚNG - Back button (icon trái)
back_btn = tk.Button(
    text=" Back",
    image=back_icon,  # ← arrow
    compound='left'  # Icon TRÁI (đi về phía sau)
)
```

### 2. **Multi-State Buttons - Buttons Nhiều Trạng Thái**

Buttons có thể thay đổi state (Next → Finish, Start → Stop, etc.):
- **Icon PHẢI đổi theo state**
- **Icon position PHẢI thay đổi theo ý nghĩa state**

```python
# ✅ ĐÚNG - Next/Finish button state management
if is_last_step:
    # FINISH state: Action button → icon TRÁI
    button.config(
        text=" Finish",
        image=save_icon,    # Check/Save icon
        compound='left'     # Icon TRÁI (action button)
    )
else:
    # NEXT state: Navigation button → icon PHẢI
    button.config(
        text="Next ",
        image=next_icon,    # Arrow icon
        compound='right'    # Icon PHẢI (navigation)
    )
```

### 3. **Text Rules - Quy Tắc Text**

#### No Emoji in Text When Icon Present
- ❌ **SAI**: `text=" Save"` khi có save icon
- ✅ **ĐÚNG**: `text=" Save"` (space for spacing only)
- ❌ **SAI**: `text="💾 Save"` khi có save.ico
- ✅ **ĐÚNG**: `text=" Save"` (no emoji, icon handles visual)

```python
# ❌ SAI - Emoji in text when icon exists
button = tk.Button(
    text="💾 Save",      # Redundant emoji
    image=save_icon,
    compound='left'
)

# ✅ ĐÚNG - Clean text, icon only
button = tk.Button(
    text=" Save",        # Space for padding only
    image=save_icon,
    compound='left'
)
```

#### Emoji Fallback
- Chỉ dùng emoji khi **KHÔNG CÓ icon** (icon load failed)
- Pattern: Check `isinstance(icon, str)` để detect fallback

```python
# ✅ ĐÚNG - Conditional emoji
icon = self._icon('save', '💾', size=16)
button = tk.Button(
    text=" Save" if not isinstance(icon, str) else "💾 Save",
    image=icon if not isinstance(icon, str) else None,
    compound='left' if not isinstance(icon, str) else 'none'
)
```

### 4. **Icon Format Priority - Ưu Tiên Định Dạng Icon**

```
.ico > .png > emoji
```

#### Lý do:
1. **.ico**: Vector-based, multiple resolutions, Windows native, sharp at any size
2. **.png**: Raster, fixed resolution, can blur when scaled
3. **emoji**: Unicode fallback, inconsistent rendering across systems

```python
# Icon helper tự động prioritize
icon_helper.get_icon('save', fallback='💾', size=16)
# Thử: save.ico → save.png → '💾'
```

### 5. **Icon Sizes - Kích Thước Icon**

| Button Type | Icon Size | Font Size | Use Case |
|-------------|-----------|-----------|----------|
| Small control | 14px | 9pt | Up/Down arrows |
| Standard button | 16px | 10pt | Most buttons |
| Prominent button | 18px | 10pt bold | Rotation Builder |
| Primary action | 20-22px | 11pt bold | Global Apply, Save |

## 📋 Implementation Checklist

### Creating a New Button

- [ ] Xác định button type: Action hay Navigation?
- [ ] Icon position: Left (action) hay Right (navigation)?
- [ ] Icon size phù hợp với font size?
- [ ] Text không có emoji khi có icon?
- [ ] Icon format: Có .ico file chưa?
- [ ] Multi-state: Cần thay đổi icon/position theo state?
- [ ] Negative space: padx/pady đủ không?
- [ ] Contrast ratio: ≥4.5:1 (WCAG AA)?

### Example: Creating Save Button

```python
# 1. Get icon using _icon() helper
save_icon = self._icon('save', '💾', size=18)

# 2. Create button with proper rules
btn = tk.Button(
    parent,
    text=" Save Settings" if not isinstance(save_icon, str) else "💾 Save Settings",
    image=save_icon if not isinstance(save_icon, str) else None,
    compound='left' if not isinstance(save_icon, str) else 'none',  # LEFT for action
    font=('Arial', 10, 'bold'),
    bg='#357A38',     # Green (CR 5.26:1)
    fg='white',
    padx=24,          # Negative space
    pady=10,
    cursor='hand2',
    command=self.on_save
)

# 3. Keep reference to prevent GC
if not isinstance(save_icon, str):
    btn.image = save_icon
```

## 🎨 Visual Examples

### Action Buttons Pattern
```
[💾] Save          ← Icon LEFT
[➕] Add Item      ← Icon LEFT
[🗑️] Delete        ← Icon LEFT
[✏️] Edit          ← Icon LEFT
[✖] Cancel        ← Icon LEFT
```

### Navigation Buttons Pattern
```
[←] Back          ← Icon LEFT (going backward)
Next [→]          ← Icon RIGHT (going forward)
```

### Multi-State Button Pattern
```
Step 1-4: Next [→]        ← Icon RIGHT (navigation)
Step 5:   [💾] Finish      ← Icon LEFT (action)
```

## 🔍 Code Patterns

### Using _icon() Helper
```python
def _icon(self, name: str, fallback: str, size: int = 16):
    """
    Centralized icon loading with caching.
    Priority: .ico → .png → emoji fallback
    """
    # Icon helper with cache
    # Returns PhotoImage or str (emoji)
```

### Action Button Template
```python
icon = self._icon('action_name', '🔰', size=16)
btn = tk.Button(
    text=" Action" if not isinstance(icon, str) else "🔰 Action",
    image=icon if not isinstance(icon, str) else None,
    compound='left' if not isinstance(icon, str) else 'none',
    padx=20, pady=8
)
if not isinstance(icon, str):
    btn.image = icon
```

### Navigation Button Template
```python
# Next (icon RIGHT)
next_icon = self._icon('next', '→', size=18)
btn_next = tk.Button(
    text="Next " if not isinstance(next_icon, str) else "Next",
    image=next_icon if not isinstance(next_icon, str) else None,
    compound='right' if not isinstance(next_icon, str) else 'none'
)

# Back (icon LEFT)
back_icon = self._icon('previous', '←', size=16)
btn_back = tk.Button(
    text=" Back" if not isinstance(back_icon, str) else "Back",
    image=back_icon if not isinstance(back_icon, str) else None,
    compound='left' if not isinstance(back_icon, str) else 'none'
)
```

### Multi-State Button Template
```python
def update_button_state(self, is_final):
    if is_final:
        # Action state (Finish, Stop, etc.)
        icon = self._icon('save', '✓', size=18)
        self.button.config(
            text=" Finish" if not isinstance(icon, str) else "Finish",
            image=icon if not isinstance(icon, str) else None,
            compound='left'  # Action → LEFT
        )
    else:
        # Navigation state (Next, Continue, etc.)
        icon = self._icon('next', '→', size=18)
        self.button.config(
            text="Next " if not isinstance(icon, str) else "Next",
            image=icon if not isinstance(icon, str) else None,
            compound='right'  # Navigation → RIGHT
        )
    
    if not isinstance(icon, str):
        self.button.image = icon
```

## 📊 Current Implementation Status

### Setup Wizard (ui/setup_wizard.py)
- ✅ Back button: Icon LEFT (previous.ico)
- ✅ Next button: Icon RIGHT → Finish: Icon LEFT (state-based)
- ✅ Cancel button: Icon LEFT (cancel.ico)
- ✅ Search button: Icon LEFT (search.ico)
- ✅ Clear button: Icon LEFT (delete.ico)
- ✅ Rotation Builder: Icon LEFT (skill.ico)

### Main App (app_gui.py)
- ✅ Global Apply: Icon LEFT (save.ico, 22px)
- ✅ All action buttons: Icon LEFT
- ✅ No compound='right' found (except Next in wizard)

## 🎯 Benefits of These Rules

1. **Consistency**: Predictable icon placement across entire app
2. **Cognitive Load**: Users learn pattern once, apply everywhere
3. **Accessibility**: Clear visual hierarchy, better for screen readers
4. **Maintainability**: Rules-based approach, easy to validate
5. **Performance**: Icon caching reduces redundant loads
6. **Flexibility**: Multi-state buttons handle context changes gracefully

## 🚨 Common Mistakes to Avoid

### ❌ DON'T: Mix icon positions arbitrarily
```python
# BAD - Inconsistent
btn1 = tk.Button(text="Save ", image=icon, compound='right')  # RIGHT?
btn2 = tk.Button(text=" Delete", image=icon, compound='left')  # LEFT?
```

### ✅ DO: Follow action/navigation rule
```python
# GOOD - Consistent
btn_save = tk.Button(text=" Save", image=save_icon, compound='left')    # Action → LEFT
btn_next = tk.Button(text="Next ", image=next_icon, compound='right')   # Navigation → RIGHT
```

### ❌ DON'T: Use emoji when icon loaded
```python
# BAD - Redundant emoji
btn = tk.Button(text="💾 Save", image=save_icon, compound='left')
```

### ✅ DO: Clean text, let icon do the work
```python
# GOOD - Clean text
btn = tk.Button(text=" Save", image=save_icon, compound='left')
```

### ❌ DON'T: Forget state changes
```python
# BAD - Static icon position
btn.config(text="Finish ", image=finish_icon, compound='right')  # Still RIGHT?
```

### ✅ DO: Update icon position with state
```python
# GOOD - State-aware
if is_final:
    btn.config(text=" Finish", image=save_icon, compound='left')  # Action → LEFT
else:
    btn.config(text="Next ", image=next_icon, compound='right')   # Nav → RIGHT
```

## 📚 Related Documentation

- [Icon Map Status Report](ICON_STATUS_REPORT.md) - Full icon coverage analysis
- [Button Styles Guide](../lib/ui/button_styles.py) - Color, contrast, negative space
- [Negative Space Guide](ENHANCEMENT_DIALOG_SAVE_ICONS.md) - Padding optimization

---

**Last Updated**: October 21, 2025  
**Maintained By**: Cabal Auto Hunt Development Team  
**Next Review**: Sprint 22
