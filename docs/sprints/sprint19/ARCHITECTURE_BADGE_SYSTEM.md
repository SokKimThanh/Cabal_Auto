# Badge System Architecture - Sprint 19

**Date**: October 19, 2025

---

## 🏗️ Badge System Overview

### Before Sprint 19 (WRONG)

```
┌─────────────────────────────────────────────────┐
│ [Title]                          [💾] [✖]      │ Top bar
├─────────────────────────────────────────────────┤
│ [Tab: Quái] [CHƯA LƯU] ← ???                   │ Tabs
│                                                 │
│  [Template Form] [CHƯA LƯU] ← ???              │ Form
│  Template fields...                             │
└─────────────────────────────────────────────────┘

❌ Problems:
1. Single badge widget (self.unsaved_badge)
2. Used for BOTH global and template purposes
3. Template methods overwrite global state
4. Badge position ambiguous (tab area)
5. Not visible when switching tabs
```

### After Sprint 19 Phase 1 (BETTER)

```
┌─────────────────────────────────────────────────┐
│ [Title]                          [💾] [✖]      │ Top bar
├─────────────────────────────────────────────────┤
│ [Tab: Quái] [Tab: Skill] [Tab: Timing]         │ Tabs
│                                                 │
│  [Template: Coc go 1]  [Đang chỉnh sửa]        │ Form
│  Template fields...                             │
└─────────────────────────────────────────────────┘

✅ Improvements:
1. Badge timing fixed (only shows when unlocked)
2. No premature "Chưa lưu" display
3. Template callbacks don't trigger badge
4. Badge stable during editing
```

### After Sprint 19 Phase 2 (BEST)

```
┌─────────────────────────────────────────────────┐
│ [Title]              [CHƯA LƯU] [💾] [✖]       │ Top bar (GLOBAL)
├─────────────────────────────────────────────────┤
│ [Tab: Quái] [Tab: Skill] [Tab: Timing]         │ Tabs
│                                                 │
│  [Template: Coc go 1]  [Đang chỉnh sửa]        │ Form (TEMPLATE)
│  Template fields...                             │
└─────────────────────────────────────────────────┘

✅✅ Final State:
1. TWO separate badge widgets
2. Global badge in top bar (all tabs)
3. Template badge in form (template editing)
4. Clear visual separation
5. No conflicts, independent control
```

---

## 📊 Badge Widget Hierarchy

### Widget Structure

```
LibraryManagerWindow (tk.Toplevel)
│
├─ main_frame (tk.Frame)
│  │
│  ├─ top_bar (tk.Frame) ← height=44, bg=#F5F5F5
│  │  │
│  │  ├─ Title Label (left)
│  │  │  └─ "Library Manager"
│  │  │
│  │  ├─ 🟧 GLOBAL BADGE (right) ← self.unsaved_badge
│  │  │  ├─ Text: "CHƯA LƯU" / "UNSAVED"
│  │  │  ├─ Pack: side='right', padx=(0,6)
│  │  │  └─ Initially: pack_forget()
│  │  │
│  │  ├─ Save Button 💾 (right)
│  │  │  └─ Command: _apply_all_changes()
│  │  │
│  │  └─ Close Button ✖ (right)
│  │
│  └─ notebook (ttk.Notebook)
│     │
│     ├─ Tab 1: monster_tab
│     │  └─ template_edit_panel
│     │     └─ template_form_frame
│     │        └─ form_title_frame
│     │           │
│     │           ├─ Title Label (left)
│     │           │
│     │           └─ 🟧/🟩 TEMPLATE BADGE ← self.template_badge
│     │              ├─ Text: "Đang chỉnh sửa" / "Đã lưu"
│     │              ├─ Place: relx=1.0, x=-15, y=12
│     │              └─ Initially: place_forget()
│     │
│     ├─ Tab 2: skill_tab
│     │
│     └─ Tab 3: timing_tab
```

---

## 🎯 Badge Responsibilities

### Global Badge (self.unsaved_badge)

**Widget**: `tk.Label` in `top_bar`
**Parent**: `top_bar` frame
**Layout**: `pack(side='right')` next to Save button

**Responsibilities**:
- Track changes across ALL 3 tabs
- Show when ANY tab has unsaved changes
- Hide when ALL changes are saved
- Visible from ANY tab (stays in top bar)

**States**:
```python
# Show
text = 'CHƯA LƯU' (VI) or 'UNSAVED' (EN)
bg = UI.COLOR_WARNING  # Orange
self.unsaved_badge.pack(side='right', padx=(0, 6), pady=6)

# Hide
self.unsaved_badge.pack_forget()
```

**Controlled by**:
```python
self._mark_unsaved(True)   # Show badge
self._mark_unsaved(False)  # Hide badge
```

**Triggered by**:
- Monster add/edit/delete
- Skill add/edit/delete
- Timing calculation apply
- ANY change in `self.changes_made` dict

### Template Badge (self.template_badge)

**Widget**: `tk.Label` in `form_title_frame`
**Parent**: Monster tab's template form
**Layout**: `place(relx=1.0, x=-15, y=12)` at right

**Responsibilities**:
- Show template editing state
- Independent from global badge
- Only visible in Monster tab
- Temporary feedback for template actions

**States**:
```python
# Editing (Orange)
text = 'Đang chỉnh sửa' (VI) or 'Editing' (EN)
bg = '#FF9800'  # Orange
self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')

# Saved (Green, 3 seconds)
text = 'Đã lưu' (VI) or 'Saved' (EN)
bg = '#4CAF50'  # Green
self.template_badge.place(relx=1.0, x=-15, y=12, anchor='e')
# Auto-hide after 3s

# Hidden
self.template_badge.place_forget()
```

**Controlled by**:
```python
self._show_editing_badge()   # Orange badge
self._show_saved_badge()     # Green badge (3s)
self._hide_template_badge()  # Hide badge
```

**Triggered by**:
- Template unlock (click ✏️)
- Template save (click 💾 in form)
- Template lock (after save)

---

## 🔄 Badge State Machine

### Global Badge State Machine

```
┌──────────────┐
│   HIDDEN     │ ← Initial state
│  (no badge)  │
└──────┬───────┘
       │
       │ User makes change in ANY tab
       │ (_mark_unsaved(True))
       ↓
┌──────────────┐
│   VISIBLE    │
│ "CHƯA LƯU"  │ ← Stays visible across tabs
└──────┬───────┘
       │
       │ User clicks 💾 Save in top bar
       │ (_mark_unsaved(False))
       ↓
┌──────────────┐
│   HIDDEN     │
│  (saved)     │
└──────────────┘
```

### Template Badge State Machine

```
┌──────────────┐
│   HIDDEN     │ ← Initial: Template selected (locked)
└──────┬───────┘
       │
       │ Click ✏️ Edit
       │ (_show_editing_badge())
       ↓
┌──────────────┐
│   EDITING    │
│"Đang chỉnh   │ ← Orange background
│   sửa"       │
└──────┬───────┘
       │
       │ Edit template fields
       │ (Badge stays visible)
       │
       │ Click 💾 Save in form
       │ (_show_saved_badge())
       ↓
┌──────────────┐
│    SAVED     │
│  "Đã lưu"    │ ← Green background
└──────┬───────┘
       │
       │ Wait 3 seconds
       │ (auto-hide timer)
       ↓
┌──────────────┐
│   HIDDEN     │ ← Back to locked view
└──────────────┘
```

---

## 📈 Badge Interaction Flow

### Scenario 1: Edit Monster → Save All

```
Step 1: Edit Monster
┌────────────────────────────────────┐
│ [Title]  [CHƯA LƯU] [💾] [✖]      │ ← Global badge appears
├────────────────────────────────────┤
│ [Quái Vật*] [Kỹ Năng] [Timing]    │
│  ... editing monster ...           │
└────────────────────────────────────┘
self.changes_made['monsters_changed'] = True
self._mark_unsaved(True)

Step 2: Switch to Skills Tab
┌────────────────────────────────────┐
│ [Title]  [CHƯA LƯU] [💾] [✖]      │ ← Badge still visible
├────────────────────────────────────┤
│ [Quái Vật] [Kỹ Năng*] [Timing]    │
│  ... viewing skills ...            │
└────────────────────────────────────┘
Badge follows user (in top bar)

Step 3: Click Save 💾
┌────────────────────────────────────┐
│ [Title]          [💾] [✖]          │ ← Badge disappears
├────────────────────────────────────┤
│ Success: Changes applied           │
└────────────────────────────────────┘
self._mark_unsaved(False)
```

### Scenario 2: Edit Template → Save Template → Save All

```
Step 1: Edit Template
┌────────────────────────────────────┐
│ [Title]  [CHƯA LƯU] [💾] [✖]      │ ← Global badge
├────────────────────────────────────┤
│ [Template] [Đang chỉnh sửa] [💾]  │ ← Template badge (orange)
│  ... editing template ...          │
└────────────────────────────────────┘
TWO badges visible:
- Global: Changes to monsters data
- Template: Currently editing this template

Step 2: Click Template Save 💾
┌────────────────────────────────────┐
│ [Title]  [CHƯA LƯU] [💾] [✖]      │ ← Global badge STAYS
├────────────────────────────────────┤
│ [Template]   [Đã lưu]   [💾]      │ ← Template badge (green, 3s)
│  ... template saved to memory ...  │
└────────────────────────────────────┘
Template saved to self.monsters (memory)
Global badge remains (not saved to disk)

Step 3: After 3 seconds
┌────────────────────────────────────┐
│ [Title]  [CHƯA LƯU] [💾] [✖]      │ ← Global badge STILL visible
├────────────────────────────────────┤
│ [Template]           [💾]          │ ← Template badge auto-hidden
│  ... template locked again ...     │
└────────────────────────────────────┘
Template badge disappears (auto-hide)
Global badge remains (need main save)

Step 4: Click Main Save 💾
┌────────────────────────────────────┐
│ [Title]          [💾] [✖]          │ ← Both badges gone
├────────────────────────────────────┤
│ Success: All changes saved to disk │
└────────────────────────────────────┘
All changes saved to monsters.json
```

---

## 🧩 Code Organization

### Badge-Related Methods

```python
# === GLOBAL BADGE METHODS ===

def _mark_unsaved(self, state: bool):
    """Show/hide global badge in top bar."""
    # Used by: Monster/Skill/Timing change handlers
    
def _update_save_button_tooltip(self, has_unsaved: bool):
    """Update Save button tooltip based on state."""
    # Called by: _mark_unsaved()

# === TEMPLATE BADGE METHODS ===

def _show_editing_badge(self):
    """Show orange 'Đang chỉnh sửa' badge."""
    # Used by: _unlock_template_fields()
    
def _show_saved_badge(self):
    """Show green 'Đã lưu' badge (auto-hide 3s)."""
    # Used by: _save_template_immediately()
    
def _hide_template_badge(self):
    """Hide template badge."""
    # Used by: _select_template_by_index()
```

### Change Tracking

```python
# State dictionary
self.changes_made = {
    'monsters_changed': False,  # Tab 1
    'skills_changed': False,    # Tab 2
    'timing_applied': False     # Tab 3
}

# Check if ANY tab has changes
has_unsaved = any(self.changes_made.values())
self._mark_unsaved(has_unsaved)
```

---

## ✅ Design Benefits

### 1. Separation of Concerns
- Global badge → Global state (all tabs)
- Template badge → Local state (template editing)
- Clear responsibilities, no overlap

### 2. Visual Hierarchy
- Global badge: Top bar (high visibility)
- Template badge: Form title (contextual)
- User knows scope at a glance

### 3. Consistent Behavior
- Global badge: Persistent until save
- Template badge: Temporary feedback
- Predictable, no surprises

### 4. Maintainability
- Separate widgets → No conflicts
- Clear method names → Self-documenting
- Independent control → Easy to modify

---

**Status**: ✅ Architecture Complete  
**Documentation**: Comprehensive  
**Ready for**: Production Deployment
