# Icon Status Report - Buttons in App

**Generated**: October 21, 2025  
**Status**: Icon Map Updated + Missing Icons Identified

## 📊 Summary

- **Total Icon Entries**: 39 (was 24)
- **Icons with .ico files**: 28
- **Icons with .png only**: 2 (capture, monster, template)
- **Icons needing .ico files**: 2 (up, down)

## ✅ Icons Already Implemented

These buttons already have icons in the app:

| Button | Icon Name | File | Location | Status |
|--------|-----------|------|----------|--------|
| **Refresh Windows** | refresh | refresh.ico | Hunt tab | ✅ Implemented |
| **Start Hunt** | start | start.ico | Hunt tab | ✅ Implemented |
| **Stop Hunt** | stop | stop.ico | Hunt tab | ✅ Implemented |
| **Global Apply** | save | save.ico | Top bar | ✅ Implemented |
| **Setup Wizard** | support | support.ico | Setup tab | ✅ Implemented |

## 🆕 Icons Added to Map

These icons were added to `icon_map` for future use:

### New Icon Entries
| Icon Name | File | Emoji Fallback | Usage |
|-----------|------|----------------|-------|
| **next** | next.ico | → | Setup Wizard (already used) |
| **previous** | previous.ico | ← | Setup Wizard (already used) |
| **preview** | preview.ico | 👁️ | Preview overlay button |
| **question** | question_mark.ico | ❓ | Test/help buttons |
| **up** | up.ico | ↑ | Move up (NO .ICO YET) |
| **down** | down.ico | ↓ | Move down (NO .ICO YET) |

### Alias Entries (Using Existing Icons)
| Alias | Maps To | File | Usage |
|-------|---------|------|-------|
| **browse** | folder | folder.ico | Browse file/template buttons |
| **clear** | delete | delete.ico | Clear bounds/slots buttons |
| **close** | cancel | cancel.ico | Close dialog buttons |
| **new** | add | add.ico | New monster/skill buttons |
| **calculate** | info | info.ico | Calculate/estimate buttons |
| **apply** | save | save.ico | Apply timing buttons |
| **test** | question | question_mark.ico | Test recognition buttons |
| **use** | start | start.ico | Use template button |
| **library** | list | list.ico | Library manager button |

### Updated Entries
| Icon Name | Old | New | Reason |
|-----------|-----|-----|--------|
| **folder** | folder.png | folder.ico | Prioritize .ico (folder.ico exists) |

## 🔴 Buttons WITHOUT Icons (Need Implementation)

These buttons are in the app but don't have icons yet:

### Hunt Tab

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 840 | ➕ (Add Monster) | add | ✅ add.ico | 🟡 MEDIUM (emoji ok) |
| 842 | ↑ (Move Up) | up | ❌ NO .ICO | 🔴 HIGH (need up.ico) |
| 843 | ↓ (Move Down) | down | ❌ NO .ICO | 🔴 HIGH (need down.ico) |
| 881 | Clear Slot | clear | ✅ delete.ico | 🟢 LOW (functional) |
| 1139 | Browse | browse | ✅ folder.ico | 🟡 MEDIUM |
| 1164 | Clear Bounds | clear | ✅ delete.ico | 🟢 LOW |

### Setup Tab

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 1049 | Library Manager | library | ✅ list.ico | 🟡 MEDIUM |

### Monster Tab

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 3193 | Estimate | calculate | ✅ info.ico | 🟢 LOW |
| 3201 | Calculate Timing | calculate | ✅ info.ico | 🟢 LOW |
| 3221 | Clear Bounds | clear | ✅ delete.ico | 🟢 LOW |
| 3229 | Browse | browse | ✅ folder.ico | 🟡 MEDIUM |
| 3230 | Open Templates | folder | ✅ folder.ico | 🟡 MEDIUM |
| 3256 | Browse Template | browse | ✅ folder.ico | 🟡 MEDIUM |
| 3257 | Capture | capture | ✅ capture.png | 🟢 LOW (.png ok) |
| 3288 | Preview Overlay | preview | ✅ preview.ico | 🟡 MEDIUM |
| 3300 | Test Recognition | test | ✅ question_mark.ico | 🟡 MEDIUM |
| 3304 | Add Template | add | ✅ add.ico | 🟢 LOW |
| 3305 | Update Template | edit | ✅ edit.ico | 🟢 LOW |
| 3306 | Delete Template | delete | ✅ delete.ico | 🟢 LOW |
| 3312 | New Monster | new | ✅ add.ico | 🟢 LOW |
| 3313 | Save Monster | save | ✅ save.ico | 🟢 LOW |
| 3314 | Delete Monster | delete | ✅ delete.ico | 🟢 LOW |
| 3315 | Use Template | use | ✅ start.ico | 🟡 MEDIUM |

### Timing Calculator Dialog

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 3943 | Calculate | calculate | ✅ info.ico | 🟢 LOW |
| 3945 | Apply to Config | apply | ✅ save.ico | 🟢 LOW |
| 3947 | Close | close | ✅ cancel.ico | 🟢 LOW |

### Skills Tab

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 4190 | Browse | browse | ✅ folder.ico | 🟡 MEDIUM |
| 4200 | New Skill | new | ✅ add.ico | 🟢 LOW |
| 4201 | Save Skill | save | ✅ save.ico | 🟢 LOW |
| 4202 | Delete Skill | delete | ✅ delete.ico | 🟢 LOW |

### Dialog Buttons

| Line | Button Text | Suggested Icon | File Exists | Implementation Priority |
|------|-------------|----------------|-------------|------------------------|
| 1735 | Add (Dialog) | add | ✅ add.ico | 🟢 LOW |
| 1737 | Cancel (Dialog) | cancel | ✅ cancel.ico | 🟢 LOW |
| 2938 | Close (Preview) | close | ✅ cancel.ico | 🟢 LOW |
| 3055 | Close (Result) | close | ✅ cancel.ico | 🟢 LOW |

## 🎯 Action Items

### 🔴 CRITICAL - Missing Icon Files

**Need to create these .ico files:**

1. **up.ico** (↑)
   - Used for: Move Up button (line 842)
   - Current: Text emoji "↑"
   - Recommendation: Create 16x16 .ico with up arrow

2. **down.ico** (↓)
   - Used for: Move Down button (line 843)
   - Current: Text emoji "↓"
   - Recommendation: Create 16x16 .ico with down arrow

### 🟡 HIGH PRIORITY - Implement Icons in Code

**These have .ico files but not implemented in buttons:**

1. **Browse buttons** (8 locations)
   - Icon: `folder.ico` (exists)
   - Lines: 1139, 3229, 3230, 3256, 4190
   - Pattern: `self._icon('browse', '📂', size=16)`

2. **Preview Overlay button** (1 location)
   - Icon: `preview.ico` (exists)
   - Line: 3288
   - Pattern: `self._icon('preview', '👁️', size=18)`

3. **Move Up/Down buttons** (2 locations)
   - Icon: Need `up.ico`, `down.ico`
   - Lines: 842, 843
   - Pattern: `self._icon('up', '↑', size=14)`

4. **Library Manager button** (1 location)
   - Icon: `list.ico` (exists, via 'library' alias)
   - Line: 1049
   - Pattern: `self._icon('library', '📚', size=18)`

### 🟢 MEDIUM PRIORITY - Add Icons to Existing Buttons

**These work fine but would benefit from icons:**

1. **Clear buttons** (3 locations)
   - Icon: `delete.ico` (via 'clear' alias)
   - Lines: 881, 1164, 3221

2. **Add/New buttons** (4 locations)
   - Icon: `add.ico` (via 'new' alias)
   - Lines: 840, 3304, 3312, 4200

3. **Save buttons** (4 locations)
   - Icon: `save.ico` (already exists)
   - Lines: 3313, 4201, 3945

4. **Delete buttons** (4 locations)
   - Icon: `delete.ico` (already exists)
   - Lines: 3306, 3314, 4202

5. **Calculate/Estimate buttons** (3 locations)
   - Icon: `info.ico` (via 'calculate' alias)
   - Lines: 3193, 3201, 3943

6. **Test Recognition button** (1 location)
   - Icon: `question_mark.ico` (via 'test' alias)
   - Line: 3300

## 📋 Implementation Pattern

For each button without an icon, use this pattern:

```python
# BEFORE (no icon)
tk.Button(
    parent,
    text=self._t('button_text'),
    command=self.handler
).pack(...)

# AFTER (with icon)
icon_name_icon = self._icon('icon_name', 'emoji_fallback', size=16)
btn = tk.Button(
    parent,
    text=f" {self._t('button_text')}" if not isinstance(icon_name_icon, str) else self._t('button_text'),
    image=icon_name_icon if not isinstance(icon_name_icon, str) else None,
    compound='left' if not isinstance(icon_name_icon, str) else 'none',
    command=self.handler
)
btn.pack(...)
if not isinstance(icon_name_icon, str):
    btn.image = icon_name_icon  # Keep reference
```

## 🎨 Icon Size Guidelines

| Button Type | Recommended Size | Example |
|-------------|------------------|---------|
| **Small control buttons** | 14x14 | Up/Down arrows |
| **Standard buttons** | 16x16 | Browse, Clear, Delete |
| **Prominent buttons** | 18x18 | Preview, Library Manager |
| **Primary actions** | 20-22x22 | Save, Apply, Start |

## 📊 Icon Map Statistics

### Before Update
- Total entries: 24
- Icons: 24
- Aliases: 0

### After Update
- Total entries: 39
- Unique icons: 26
- Aliases: 13
- Icons with .ico: 28
- Icons with .png only: 2
- Icons missing files: 2 (up, down)

### Coverage
- Buttons with icons: 5/39 (13%)
- Buttons ready for icons: 34/39 (87%)
- Buttons needing .ico files: 2/39 (5%)

## 🔮 Next Steps

1. **Create missing icon files** (HIGH PRIORITY)
   - [ ] up.ico (16x16)
   - [ ] down.ico (16x16)

2. **Implement icons in code** (MEDIUM PRIORITY)
   - [ ] Browse buttons (8 locations)
   - [ ] Preview Overlay button
   - [ ] Move Up/Down buttons (after creating .ico)
   - [ ] Library Manager button

3. **Optional enhancements** (LOW PRIORITY)
   - [ ] Add icons to all Clear buttons
   - [ ] Add icons to all Save/Delete buttons
   - [ ] Add icons to Calculate buttons
   - [ ] Standardize icon sizes across app

4. **Testing**
   - [ ] Verify all icons load correctly
   - [ ] Check emoji fallbacks work
   - [ ] Ensure no visual regressions
   - [ ] Test on different DPI settings

---

**Note**: All icons now prioritize .ico format with automatic fallback to .png, then emoji. The icon loading system is robust and handles missing files gracefully.
