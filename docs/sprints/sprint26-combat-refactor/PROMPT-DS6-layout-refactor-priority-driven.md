# Session Prompt DS6: Layout Refactor - Priority-Driven Restructuring

**Timebox:** 30-40 phút  
**Priority:** HIGH – Nền tảng cho DS1-5 có tác dụng  
**Dependencies:** UX5.2 hoàn thành, DS1-5 tokens + themes sẵn sàng  
**Reference:** `docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md`

---

## ⚠ Xác Nhận Trước Khi Bắt Đầu

1. **Mục Tiêu:** Reorder sidebar tabs và reorganize view phân chia theo ưu tiên workflow người dùng (từ Redesign document).
2. **Scope Giới Hạn:** Chỉ di chuyển, hide/show, reorder UI hierarchy — **KHÔNG** thay đổi callback, business logic hay persistence.
3. **Nguyên Tắc:** Workflow core (hunt → monster → start/stop) phải nổi bật; chức năng phụ (stats, help) nằm ở vị trí phụ.

---

## Objective

Restructure `app_gui.py` sidebar navigation và view hierarchy để phản ánh đúng thứ tự ưu tiên người dùng:

- **Tier 1 (Nổi bật nhất):** Hunt, Monster Rotation Manager
- **Tier 2 (Dễ truy cập):** Setup, Hotkey, Template Manager
- **Tier 3 (Phụ trợ):** Logs, Stats, Help, Library Manager

Hiện tại sidebar có thứ tự không tối ưu; session này sẽ reorder tabs sao cho workflow hunt được tập trung vào trung tâm UI.

---

## Target Files

- Modify: `app_gui.py` (sidebar tab order, view stack, layout priority)
- Modify: `ui/views/` view files (no business logic change, visual hierarchy only)
- Modify: test fixtures nếu cần
- Reference: `lib/ui_style.py`, `docs/UX_ANALYSIS_AND_INTERFACE_REDESIGN.md`

---

## Current State (From Redesign Analysis)

### Priority Classification (Section 4, UX_ANALYSIS_AND_INTERFACE_REDESIGN.md)

**Tier 1 — Ưu tiên cao nhất (nút sống):**
1. Chọn cửa sổ mục tiêu ✅ (Action bar)
2. Refresh danh sách cửa sổ ✅ (Action bar)
3. Start Hunt ✅ (Action bar)
4. Stop Hunt ✅ (Action bar)
5. Monster rotation / danh sách mục tiêu đang chạy ⚠️ (currently tab 2, should be tab 1)
6. Trạng thái hunt hiện thời ✅ (Hunt tab)
7. Quick actions: thêm, xóa, di chuyển monster ⚠️ (currently in Monster Manager, should inline in Hunt tab)

**Tier 2 — Ưu tiên cao:**
1. template / target area ✅ (Hunt tab)
2. hotkey toàn cục ⚠️ (currently tab 4, should be tier 2)
3. thiết lập nhanh cho hunt ✅ (Setup)
4. mode Beginner / Intermediate / Advanced ✅ (Hunt tab)
5. global apply ✅ (Action bar)

**Tier 3 — Ưu tiên trung bình:**
1. Monster Manager ⚠️ (currently tab 2, should be tier 3 or merged into Hunt)
2. Skill Manager ⚠️ (currently tab 3, should be tier 3)
3. Library Manager ⚠️ (visible, should be tier 3)
4. Timing Calculator ⚠️ (if exists)
5. Template management ⚠️ (if exists separately)

**Tier 4 — Ưu tiên thấp (phụ trợ):**
1. Stats tab ⚠️ (currently prominent, should move down)
2. Help tab ⚠️ (currently prominent, should move down)
3. log / debug / status ✅ (Logs tab)
4. cảnh báo kỹ thuật ⚠️ (should be toast, not modal)

---

## Implementation Details

### 1. Sidebar Tab Reorder

**Current Order (app_gui.py, self.notebook_tabs):**
```
1. Hunt
2. Monster Manager
3. Skill Manager
4. Hotkey
5. Template Manager
6. Logs
7. Stats
8. Help
```

**Target Order (after redesign):**
```
1. Hunt (Tier 1 — core workflow)
2. Setup (Tier 2 — quick config)
3. Hotkey (Tier 2 — keyboard support)
4. Logs (Tier 2 — live status)
--- [Separator or visual break] ---
5. Monster Manager (Tier 3 — advanced monster config)
6. Skill Manager (Tier 3 — advanced skill config)
7. Template Manager (Tier 3 — template library)
8. Stats (Tier 4 — telemetry, optional)
9. Help (Tier 4 — documentation, optional)
```

**Rationale:**
- Hunt is first, undisputed
- Setup moves up (quick workflow config, not advanced)
- Hotkey stays accessible (keyboard-first users)
- Logs moves to tier 2 (active monitoring during hunt)
- Advanced managers (Monster, Skill, Template) move down
- Stats/Help move to end (users rarely toggle during hunt)

### 2. Within-View Hierarchy Changes

#### Hunt Tab (`ui/tabs/hunt_tab.py`)
- ✅ Keep: Target Card, HP bar, Status, Skill Lanes, Mode Selector
- ⚠️ **Move Up (make prominent):** Quick Monster Add/Remove buttons
  - Currently: likely in Monster Manager tab
  - Target: Add inline quick-add in Hunt tab under Monster Rotation
- ⚠️ **Reduce:** Monster Manager "full editor" — move to Monster Manager tab only
- ✅ Keep: Template/target area on Hunt tab (power users need this)

#### Monster Manager Tab (`ui/views/monster_manager.py`)
- Role: Full CRUD for monster library
- Visibility: Secondary, not primary workflow
- Action: Reposition as **Tab 5** instead of Tab 2
- Affordance: Clear label "Advanced Monster Config" or icon

#### Skill Manager Tab (`ui/views/skill_manager.py`)
- Role: Configure skill slots, combos, timing
- Visibility: Secondary, not primary workflow
- Action: Reposition as **Tab 6** instead of Tab 3
- Affordance: Clear label "Skill Config" or icon

#### Hotkey Tab (`ui/views/hotkey_config.py`)
- Role: Bind global hotkeys
- Visibility: **Move to Tab 3** (important for keyboard-first users)
- Affordance: Icon + label unchanged

#### Setup Tab (`ui/views/setup_wizard.py`)
- Role: Quick hunt mode (Beginner/Intermediate/Advanced), skill lane, rotation
- Visibility: **Move to Tab 2** (quick workflow config)
- Affordance: Currently icon + label, keep as-is

#### Logs Tab (`ui/views/activity_logs_frame.py`)
- Role: Live hunt activity + warnings
- Visibility: **Move to Tab 4** (active monitoring)
- Affordance: Icon + label

#### Stats Tab (`ui/views/stats_frame.py`)
- Role: Telemetry, performance metrics
- Visibility: **Move to Tab 8** (low priority)
- Affordance: Icon + label, slightly grayed-out styling (optional)

#### Help Tab (`ui/views/help_frame.py`)
- Role: Documentation, troubleshooting
- Visibility: **Move to Tab 9** (lowest priority)
- Affordance: Icon + label, optional tooltip "(?) Help"

### 3. Within-Hunt-Tab Quick Actions

**Pseudo-code reorg (hunt_tab.py structure):**
```python
def _build_ui(self):
    # Tier 1: Active hunt state (unchanged)
    _build_target_card()      # Target info + HP + status
    _build_skill_lanes()      # Skill panel (unchanged)
    _build_mode_selector()    # Beginner/Int/Adv (unchanged)
    
    # Tier 1.5: Quick Monster Actions (NEW - promote from Monster Manager)
    _build_quick_monster_actions()  # [ + Add Monster ] [ X Remove ] buttons
    
    # Tier 2: Monster Rotation List (unchanged, but now with better affordance)
    _build_monster_rotation_list()  # Treeview of current rotation
    
    # Tier 3: Template / Target area (unchanged, still for power users)
    _build_template_target_area()   # Advanced section
```

---

## Implementation Rules

1. **No Business Logic Change:**
   - Callbacks remain unchanged
   - Persistence (config, monster DB, skill slots) unchanged
   - Database queries unchanged
   - Combat state machine unchanged

2. **Tab Reordering:**
   - Modify `self.notebook_tabs` list order in `app_gui.py`
   - Modify `self.notebook.add(frame, text=label)` order
   - Update test fixture order if tests check `notebook_tabs` indexing

3. **View Lifecycle Unchanged:**
   - View init, destroy, refresh logic unchanged
   - pack/grid managers unchanged
   - No new frames or widget restructuring beyond what's listed above

4. **Keyboard/Screen Reader:**
   - Tab order via keyboard Tab key should follow new notebook order
   - No new accessibility issues introduced

5. **Icon/Label Consistency:**
   - Use existing DS1/DS2 tokens for any new affordance styling
   - No new hard-coded colors

6. **Breakpoints:**
   - Sidebar width still respects min/max from DS3
   - No new overflow or clipping due to label length
   - DPI scaling unaffected

---

## Validation & Testing

### 1. Unit Tests

```powershell
py -m pytest tests/unit/test_app_gui_structure.py -v
```

- Notebook tab order matches expected order (new)
- Each tab frame exists and is accessible
- Tab switching doesn't break event propagation
- No callback functions are invoked during reorder

### 2. Integration Tests

```powershell
py -m pytest tests/integration/test_hunt_workflow.py -v
```

- Start hunt workflow still works (Hunt tab → Setup → Start → Stop)
- Monster quick-add works from Hunt tab (if implemented)
- Monster full editor still works from Monster Manager tab
- Switching between tabs doesn't lose state

### 3. Manual Validation

**Matrix (1366x768, 1920x1080, vi/en, DPI 100/150/200):**

| Tab | Visible | Label | Icon | Action | Workflow Impact |
|-----|---------|-------|------|--------|-----------------|
| Hunt | Yes | Hunt | 🎮 | Select target, manage rotation | Core, must work |
| Setup | Yes | Setup | ⚙️ | Configure mode, skill lane | Quick config |
| Hotkey | Yes | Hotkey | ⌨️ | Bind keys | Power user |
| Logs | Yes | Logs | 📜 | View activity | Monitoring |
| Monster Mgr | Yes | Monster | 🦾 | Full CRUD | Advanced |
| Skill Mgr | Yes | Skill | ⚔️ | Configure slots | Advanced |
| Template | Yes | Template | 🎯 | Manage templates | Advanced |
| Stats | Yes | Stats | 📊 | View metrics | Optional |
| Help | Yes | Help | ❓ | Documentation | Optional |

**Manual Steps:**
1. Open app
2. Verify sidebar order matches target
3. Click each tab (no errors)
4. Hunt tab → add monster → start hunt → stop hunt (check workflow)
5. Switch to Monster Manager → edit monster → back to Hunt (check state)
6. Check i18n label updates match new order
7. Resize window 1366→1920, check no overflow
8. Toggle DPI 100%→200%, check readability

### 4. Visual Regression

- Screenshot each tab in both `vi/en` at 1366x768 and 1920x1080
- Compare against baseline (if baseline exists)
- No new overlap, clipping or text truncation

---

## Gate Criteria

### ✅ PASSED if:
- Sidebar tab order matches target list exactly
- All tabs remain functional (no crash, callbacks work)
- Hunt workflow (add monster → start → stop) unchanged
- Keyboard Tab navigation follows new order
- No visual regression in any tab
- Unit + integration tests pass
- Manual validation passes all steps

### 🔴 REVERTED if:
- Any tab callback is broken or event propagation lost
- Monster state is lost when switching tabs
- Sidebar overflow or new clipping introduced
- Unit/integration tests fail
- Visual regression detected in migration-scoped views

---

## Timeline & Effort

| Phase | Time | Owner |
|-------|------|-------|
| Read Redesign + Finalize Target Order | 5 min | Session |
| Update app_gui.py tab order | 5 min | Session |
| Promote quick-add actions to Hunt tab (optional) | 10 min | Session |
| Update tests | 5 min | Session |
| Manual validation | 10 min | Session |
| **Total** | **35 min** | — |

---

## Related Documents

- [UX_ANALYSIS_AND_INTERFACE_REDESIGN.md](../UX_ANALYSIS_AND_INTERFACE_REDESIGN.md) — Priority classification
- [DS1-DS5 Prompts](./PROMPT-DS1-tkinter-safe-tokens.md) — Tokens + themes foundation
- [UX5.2 Prompt](./Prompt-UX5.2%20Dynamic%20Canvas%20HP%20Bar,%20Throttling%20&%20Window%20Recovery%20Logic.md) — Hunt tab enhancements

---

## Checklist for Session Completion

- [ ] Redesign priority classification understood
- [ ] Target tab order finalized
- [ ] app_gui.py `self.notebook_tabs` list reordered
- [ ] All tab frames attached in new order
- [ ] Tests updated for new order
- [ ] Quick-add actions promoted (if in scope)
- [ ] Manual validation passed (all matrix items)
- [ ] No regression in hunt workflow
- [ ] PASSED gate reported

---

**Date:** 2026-09-05  
**Status:** Ready for implementation  
**Next Phase:** After DS6, run full app test suite and visual acceptance (DS5-equivalent for layout)
