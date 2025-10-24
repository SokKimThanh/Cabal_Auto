# Monster Editor Complete Implementation Plan

Branch: `feature/monster-editor-refactor`
Status: In Progress
Created: 2025-10-24

## Overview

Nâng cấp Quick Monster Editor thành Full Monster Editor với đầy đủ chức năng quản lý quái vật và template.

## Current State (Commit 890f7d2)

✅ **Completed:**
- Skeleton modules (monster_manager.py, worker.py, hotkey_manager.py)
- i18n translations (monster_editor_translations.py)
- Hotkey integration (Ctrl+Shift+M in app_gui.py)
- Basic Quick Editor UI (527 lines)
  - Top panel: Title + Save/Cancel buttons
  - Center panel: Name, Level, Threshold fields
  - Bottom panel: Capture/Test buttons + Progress
  - Queue-based worker integration
  - i18n support

❌ **Missing:**
- Left panel: Monster list
- Right panel: Tab organization
- CRUD operations (load/save monsters.json)
- Template management (browse/delete)
- Dirty state tracking
- Icons integration
- Full test coverage

## Implementation Batches

### Batch 1: Add Missing Translations
**Goal:** Thêm các i18n keys còn thiếu cho full UI

**Files:**
- `lib/i18n/monster_editor_translations.py`

**Keys to add:**
```python
# Status
'status_modified': 'Modified (not saved)',
'status_unsaved': 'Unsaved changes',
'status_saved': 'All saved',

# Tabs
'tab_info': 'Monster Info',
'tab_templates': 'Templates',

# Labels
'monster_list_title': 'Monsters',
'monster_priority_label': 'Priority:',
'monster_hp_label': 'HP:',
'monster_damage_label': 'Damage per hit:',
'monster_desc_label': 'Description:',
'template_list_title': 'Templates:',

# Buttons
'btn_save_all': 'Save All',
'btn_close': 'Close',
'btn_add_monster': 'Add Monster',
'btn_browse': 'Browse',
'btn_delete_template': 'Delete Template',

# Messages
'msg_test_result': 'Matches: {}, Confidence: {:.1%}',
```

**Commit:** `feat: add missing translations for full Monster Editor`

**Test:**
- Run app, verify i18n keys load without errors
- Switch language (EN/VI), check all new keys render correctly

---

### Batch 2: Add Icons Helper Integration
**Goal:** Import và setup IconHelper để hiển thị icons cho buttons

**Files:**
- `ui/quick_monster_editor.py`

**Changes:**
```python
# Add imports
try:
    from lib.ui.icon_helper import IconHelper
    icon_helper = IconHelper()
except ImportError:
    class MockIconHelper:
        def get_icon(self, name: str, fallback: str = '', size: int = 16) -> str:
            return fallback
    icon_helper = MockIconHelper()

try:
    from lib.ui.capture_helper import capture_region_and_save
    PIL_AVAILABLE = True
except ImportError:
    capture_region_and_save = None
    PIL_AVAILABLE = False
```

**Icons to use:**
- `add` (➕) - Add monster
- `delete` (🗑️) - Delete monster/template
- `save` (💾) - Save all
- `folder` (📁) - Browse file
- `capture` (📸) - Capture region
- `search` (🔍) - Test recognition

**Commit:** `feat: integrate IconHelper for Monster Editor buttons`

**Test:**
- Create `tests/unit/ui/test_monster_editor_icons.py`
- Test icon loading with/without IconHelper
- Verify fallback emojis work

---

### Batch 3: Add Data Layer (Load/Save monsters.json)
**Goal:** Implement CRUD operations với monsters.json

**Files:**
- `ui/quick_monster_editor.py`

**Add:**
```python
import json
import uuid
from pathlib import Path

# Constants
DATA_PATH = Path("lib/data/monsters.json")

class MonsterEditor:
    def _load_monsters(self) -> None:
        """Load monsters from JSON file."""
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.monsters = json.load(f)
                # Ensure all have ID
                for monster in self.monsters:
                    if 'id' not in monster:
                        monster['id'] = str(uuid.uuid4())
            else:
                self.monsters = []
        except Exception as e:
            print(f"[MonsterEditor] Error loading: {e}")
            self.monsters = []
    
    def _save_monsters(self) -> bool:
        """Save monsters to JSON file."""
        try:
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.monsters, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[MonsterEditor] Error saving: {e}")
            return False
```

**State variables:**
```python
self.monsters: List[Dict[str, Any]] = []
self.current_monster_id: Optional[str] = None
self.is_dirty = False  # Global unsaved changes
self.is_monster_dirty = False  # Current monster modified
```

**Commit:** `feat: implement load/save for monsters.json`

**Test:**
- Create `tests/unit/ui/test_monster_editor_data.py`
- Test load empty file
- Test load valid monsters
- Test save monsters
- Test UUID generation
- Test error handling

---

### Batch 4: Add Left Panel (Monster List)
**Goal:** Tạo left panel với monster listbox + Add/Delete buttons

**Files:**
- `ui/quick_monster_editor.py`

**UI Structure:**
```python
def _create_left_panel(self, parent: tk.Widget) -> None:
    """Create left panel with monster list."""
    left_frame = tk.Frame(parent, bg=UI.BG_DEFAULT, width=250)
    left_frame.pack(side='left', fill='y', padx=(10, 5), pady=10)
    left_frame.pack_propagate(False)
    
    # Title
    tk.Label(..., text='Monsters').pack(...)
    
    # Listbox with scrollbar
    self.monster_listbox = tk.Listbox(...)
    self.monster_listbox.bind('<<ListboxSelect>>', self._on_monster_select)
    
    # Buttons
    add_icon = icon_helper.get_icon('add', '➕')
    tk.Button(text=f"{add_icon} Add", command=self._on_add_monster)
    
    delete_icon = icon_helper.get_icon('delete', '🗑️')
    tk.Button(text=f"{delete_icon} Delete", command=self._on_delete_monster)
```

**Methods:**
```python
def _refresh_monster_list(self) -> None:
    """Refresh monster listbox."""
    
def _on_monster_select(self, event) -> None:
    """Handle monster selection (save current if dirty)."""
    
def _on_add_monster(self) -> None:
    """Add new monster with defaults."""
    
def _on_delete_monster(self) -> None:
    """Delete selected monster (with confirmation)."""
```

**Commit:** `feat: add left panel with monster list and CRUD buttons`

**Test:**
- Create `tests/unit/ui/test_monster_editor_list.py`
- Test add monster
- Test delete monster
- Test list refresh
- Test selection handling

---

### Batch 5: Add Right Panel Tabs Structure
**Goal:** Tạo tab organization với ttk.Notebook

**Files:**
- `ui/quick_monster_editor.py`

**UI Structure:**
```python
def _create_right_panel(self, parent: tk.Widget) -> None:
    """Create right panel with tabs."""
    right_frame = tk.Frame(parent, bg=UI.BG_DEFAULT)
    right_frame.pack(side='left', fill='both', expand=True)
    
    # Status indicator (modified)
    self.monster_status_label = tk.Label(...)
    
    # Tabs
    notebook = ttk.Notebook(right_frame)
    
    # Tab 1: Monster Info
    info_tab = tk.Frame(notebook, bg=UI.BG_DEFAULT)
    notebook.add(info_tab, text=i18n_t('tab_info'))
    self._create_info_tab(info_tab)
    
    # Tab 2: Templates
    template_tab = tk.Frame(notebook, bg=UI.BG_DEFAULT)
    notebook.add(template_tab, text=i18n_t('tab_templates'))
    self._create_template_tab(template_tab)
```

**Commit:** `feat: add tab structure for Monster Info and Templates`

**Test:**
- Visual test: tabs render correctly
- Test tab switching
- Test i18n tab labels

---

### Batch 6: Implement Monster Info Tab
**Goal:** Form đầy đủ: name, level, priority, hp, damage, description

**Files:**
- `ui/quick_monster_editor.py`

**Fields:**
```python
def _create_info_tab(self, parent: tk.Widget) -> None:
    container = tk.Frame(parent, bg=UI.BG_DEFAULT)
    container.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Name (Entry)
    self.name_entry = tk.Entry(...)
    self.name_entry.bind('<KeyRelease>', lambda e: self._mark_dirty())
    
    # Level (Spinbox 1-200)
    self.level_spinbox = tk.Spinbox(from_=1, to=200, ...)
    
    # Priority (Spinbox 1-100)
    self.priority_spinbox = tk.Spinbox(from_=1, to=100, ...)
    
    # HP (Spinbox 1-999999)
    self.hp_spinbox = tk.Spinbox(from_=1, to=999999, ...)
    
    # Damage per hit (Spinbox 1-99999)
    self.damage_spinbox = tk.Spinbox(from_=1, to=99999, ...)
    
    # Description (Text widget with scrollbar)
    self.desc_text = tk.Text(width=40, height=6, ...)
```

**Methods:**
```python
def _load_monster_to_form(self, monster: Dict) -> None:
    """Load monster data to form widgets."""
    
def _save_form_to_monster(self) -> None:
    """Save form data to current monster dict."""
    
def _mark_dirty(self) -> None:
    """Mark current monster as modified."""
```

**Commit:** `feat: implement Monster Info tab with full form fields`

**Test:**
- Test load data to form
- Test save form to data
- Test dirty state tracking
- Test validation (name not empty, level > 0)

---

### Batch 7: Implement Templates Tab
**Goal:** Template list + Capture/Browse/Delete/Test + Threshold slider

**Files:**
- `ui/quick_monster_editor.py`

**UI:**
```python
def _create_template_tab(self, parent: tk.Widget) -> None:
    # Template list (Listbox)
    self.template_listbox = tk.Listbox(...)
    
    # Buttons row
    capture_icon = icon_helper.get_icon('capture', '📸')
    tk.Button(text=f"{capture_icon} Capture", command=self._on_capture_template)
    
    browse_icon = icon_helper.get_icon('folder', '📁')
    tk.Button(text=f"{browse_icon} Browse", command=self._on_browse_template)
    
    delete_icon = icon_helper.get_icon('delete', '🗑️')
    tk.Button(text=f"{delete_icon} Delete", command=self._on_delete_template)
    
    test_icon = icon_helper.get_icon('search', '🔍')
    tk.Button(text=f"{test_icon} Test", command=self._on_test_template)
    
    # Threshold slider
    self.threshold_scale = tk.Scale(from_=0.0, to=1.0, resolution=0.01, ...)
    self.threshold_label = tk.Label(text="0.70", ...)
```

**Methods:**
```python
def _on_capture_template(self) -> None:
    """Use capture_helper to capture region."""
    
def _on_browse_template(self) -> None:
    """Open file dialog to browse template."""
    
def _on_delete_template(self) -> None:
    """Delete selected template from list."""
    
def _on_test_template(self) -> None:
    """Test template recognition (mock for now)."""
```

**Commit:** `feat: implement Templates tab with capture/browse/delete/test`

**Test:**
- Test capture integration
- Test browse file dialog
- Test delete template
- Test threshold slider

---

### Batch 8: Add Dirty State Tracking
**Goal:** Hiển thị status modified/unsaved, enable/disable Save button

**Files:**
- `ui/quick_monster_editor.py`

**UI Updates:**
```python
# Top panel status
self.status_label = tk.Label(...)  # Global status

# Right panel status
self.monster_status_label = tk.Label(...)  # Current monster status

# Save button
self.save_button = tk.Button(...)
self.save_button.config(state='disabled')  # Initially disabled
```

**Methods:**
```python
def _update_status(self) -> None:
    """Update all status labels and button states."""
    if self.is_monster_dirty:
        self.monster_status_label.config(
            text='● Modified (not saved)',
            fg=UI.COLOR_WARNING
        )
    
    if self.is_dirty:
        self.status_label.config(
            text='Unsaved changes',
            fg=UI.COLOR_WARNING
        )
        self.save_button.config(state='normal')
    else:
        self.status_label.config(
            text='All saved',
            fg=UI.COLOR_ACCENT
        )
        self.save_button.config(state='disabled')
```

**Commit:** `feat: add dirty state tracking with visual indicators`

**Test:**
- Test status updates on edit
- Test save button enable/disable
- Test status clear after save

---

### Batch 9: Implement Save All Functionality
**Goal:** Save all monsters + validation + callback

**Files:**
- `ui/quick_monster_editor.py`

**Methods:**
```python
def _on_save_all(self) -> None:
    """Save all changes to file."""
    # 1. Save current monster if dirty
    if self.is_monster_dirty and self.current_monster_id:
        self._save_form_to_monster()
    
    # 2. Validate all monsters
    for monster in self.monsters:
        if not monster.get('name', '').strip():
            messagebox.showerror('Error', 'All monsters must have a name')
            return
    
    # 3. Save to file
    if self._save_monsters():
        self.is_dirty = False
        self.is_monster_dirty = False
        self._update_status()
        messagebox.showinfo('Success', 'Saved successfully')
        
        # 4. Callback
        if self.on_save_callback:
            self.on_save_callback(None, self.monsters)
```

**Commit:** `feat: implement save all with validation and callback`

**Test:**
- Test save flow
- Test validation
- Test callback invocation

---

### Batch 10: Add Window Close Handling
**Goal:** Xử lý unsaved changes khi đóng window

**Files:**
- `ui/quick_monster_editor.py`

**Methods:**
```python
def _on_close(self) -> None:
    """Handle window close with unsaved changes check."""
    if self.is_dirty or self.is_monster_dirty:
        result = messagebox.askyesnocancel(
            'Unsaved Changes',
            'Save changes before closing?'
        )
        
        if result is None:  # Cancel
            return
        elif result:  # Yes - save
            self._on_save_all()
    
    self.destroy()

def _bind_events(self) -> None:
    """Bind event handlers."""
    self.protocol("WM_DELETE_WINDOW", self._on_close)
```

**Commit:** `feat: add unsaved changes prompt on window close`

**Test:**
- Test close with no changes
- Test close with unsaved changes (Yes/No/Cancel)

---

### Batch 11: Update Window Size and Layout
**Goal:** Tăng kích thước window, adjust layout cho full UI

**Files:**
- `ui/quick_monster_editor.py`

**Changes:**
```python
class MonsterEditor(tk.Toplevel):  # Rename from QuickMonsterEditor
    def __init__(self, ...):
        title = i18n_t('full_editor_title', ns='monster_editor', default='Monster Manager')
        self.title(title)
        self.geometry("900x650")  # Increase from 500x400
        self.minsize(800, 600)
        
        # Remove topmost for better UX
        # self.attributes('-topmost', True)
```

**Update docstring:**
```python
"""
Monster Editor - Complete monster management with tabs.

Full-featured editor with:
- Left: Monster list
- Right: Tabs (Info + Templates)
- Top: Status + Actions
- Bottom: Progress bar
"""
```

**Commit:** `refactor: increase window size and update to full editor layout`

---

### Batch 12: Integration Tests
**Goal:** Tạo integration tests cho full flow

**Files:**
- `tests/integration/test_monster_editor_full_flow.py`

**Test cases:**
```python
def test_create_monster_flow():
    """Test: Open editor → Add monster → Fill form → Save → Close"""
    
def test_edit_monster_flow():
    """Test: Open editor → Select monster → Edit → Save"""
    
def test_template_capture_flow():
    """Test: Select monster → Capture template → Save"""
    
def test_dirty_state_flow():
    """Test: Edit → Check dirty → Save → Check clean"""
    
def test_unsaved_changes_flow():
    """Test: Edit → Close → Prompt → Cancel/Save/Discard"""
```

**Commit:** `test: add integration tests for Monster Editor workflows`

---

### Batch 13: Documentation
**Goal:** Cập nhật docs với full features

**Files:**
- `docs/branches/MONSTER_EDITOR_COMPLETE_SUMMARY.md`
- `docs/branches/PR_MONSTER_EDITOR_COMPLETE.md`

**Content:**
- Full features list
- UI screenshots (ASCII art)
- Usage guide
- API reference
- Testing guide

**Commit:** `docs: add complete Monster Editor documentation`

---

## Quality Checklist

### Code Quality
- [ ] All functions have docstrings
- [ ] Type hints for all parameters
- [ ] No hardcoded strings (use i18n)
- [ ] Error handling with try/except
- [ ] No direct widget updates from threads
- [ ] Queue-based worker communication

### Testing
- [ ] Unit tests for data operations
- [ ] Unit tests for UI components
- [ ] Integration tests for workflows
- [ ] Manual testing checklist

### UI/UX
- [ ] Consistent spacing (negative space)
- [ ] Clear visual hierarchy
- [ ] Icons for all actions
- [ ] Status indicators
- [ ] Tooltips on buttons
- [ ] Keyboard shortcuts

### i18n
- [ ] All labels translated
- [ ] All buttons translated
- [ ] All messages translated
- [ ] Both EN and VI complete

## Estimated Timeline

- **Batch 1-3** (Setup): 1-2 commits, 30 min
- **Batch 4-7** (UI Implementation): 4 commits, 2-3 hours
- **Batch 8-10** (State & Save): 3 commits, 1-2 hours
- **Batch 11-13** (Polish & Docs): 3 commits, 1 hour

**Total:** ~10-13 commits, 4-6 hours

## Success Criteria

✅ Editor can:
1. Load monsters from monsters.json
2. Display monster list in left panel
3. Show monster details in Info tab
4. Manage templates in Templates tab
5. Capture new templates
6. Browse existing templates
7. Test template recognition
8. Track dirty state
9. Save all changes
10. Handle unsaved changes on close

✅ Code quality:
- All batches committed separately
- All tests passing
- No lint errors
- Full documentation
