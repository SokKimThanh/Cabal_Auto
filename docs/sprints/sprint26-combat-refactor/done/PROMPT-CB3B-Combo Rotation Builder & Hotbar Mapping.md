# Session Prompt CB3B: Redesign Skill Configuration & Dual-Lane Combo UI

**Status**: 🟡 PARTIAL (55-60% complete)  
**Completion Date**: 2026-09-05  
**Last Update**: Status review completed

Timebox: 25-30 minutes.

Objective:
Refactor Skill Configuration panel in `app_gui.py` and `ui/tabs/hunt_tab.py` into a dual-lane layout separating Attack/Combo Rotation from automated Buffs.

---

## 📋 CURRENT IMPLEMENTATION STATUS

### ✅ COMPLETED (55-60%)
- [x] Dual-Lane Layout (Combo Chain + Buff Lane with grid layout)
- [x] Combo Mode Controls (Enable Auto Combo checkbox + Combo Start Key combobox)
- [x] Skill Card UI (name dropdown, Cast time, Cooldown badges)
- [x] Config Schema for combo (`hunt_cfg["combo"] = {enabled, combo_start_key}`)
- [x] i18n Support (lane headers, labels)
- [x] DPI scaling for cards

### ❌ NOT YET IMPLEMENTED (40-45%)
- [ ] Hotkey Conflict Validation (no check for key collisions)
- [ ] buff_slots Config Separation (still merged with skill_slots)
- [ ] Auto-Refresh Interval per Buff (duration_sec field)
- [ ] Buff Runtime Scheduling (skill_runtime_service integration)
- [ ] Legacy Config Migration Precedence Rules (unclassified handling)
- [ ] Validation Test Suite (DPI, i18n, migration, hotkey conflict tests)

---

## 📍 DETAILED BREAKDOWN

### What's Actually Implemented

#### 1. Dual-Lane Layout ✅
**Location**: `ui/tabs/hunt_tab.py` lines 773-939

**What Works**:
- Combo Lane (Lane A): 4 horizontal skill cards
- Buff Lane (Lane B): 4 horizontal skill cards  
- Grid layout with proper column/row configuration
- Cards display: skill name dropdown + cast time badge + cooldown badge
- DPI scaling for responsive UI
- i18n labels ("Combo Chain", "Buff Lane")

**What's Missing**:
- Filtering by skill type: ALL skills shown in both lanes (not separated by type)
- Buff-specific features: NO duration_sec input, NO Auto-Refresh interval display
- Scroll container for >6 skills (currently fixed at 8 slots total)

#### 2. Combo Mode Controls ✅
**Location**: `ui/tabs/hunt_tab.py` lines 786-833

**What Works**:
- Checkbox: "Enable Auto Combo" (toggles enabled state in config)
- Combobox: "Combo Start Key" with values [Alt+1 through Alt+5]
- Config persistence: `hunt_cfg["combo"] = {"enabled": bool, "combo_start_key": str}`
- State management: Key selector disabled when combo disabled

**What's Missing**:
- Hotkey conflict validation (NO checks for collisions)
- Broader key options beyond Alt+1-5
- Global vs in-window hook mechanism NOT specified in code

#### 3. Config Schema ✅
**Location**: `lib/features/hunt/hunt_config.py`

**What Works**:
- Combo config structure exists: `hunt_cfg["combo"]["enabled"]` and `hunt_cfg["combo"]["combo_start_key"]`
- Config migration handles skill type field: `migrate_hunt_config()` in config_migrator.py

**What's Missing**:
- buff_slots array (should be separate from skill_slots)
- duration_sec field per buff
- Legacy migration precedence rules (catalog lookup for unclassified entries)
- Separate buff_slots list in config schema

#### 4. Skill Card Display ✅
**Location**: `ui/tabs/hunt_tab.py` lines 887-930

**What Works**:
- Skill name dropdown selector
- Cast time display: "⚡ X.Xs"
- Cooldown display: "⏳ X.Cs"
- Dynamic update on selection via `update_card_stats()`
- Tooltip support

**What's Missing**:
- Key binding display (should show which key is assigned to skill)
- Buff-specific fields: Auto-Refresh interval input
- No distinction between attack/buff card styles

### What Needs to Be Done

#### Missing Feature 1: Hotkey Conflict Validation ❌
**Priority**: HIGH  
**Scope**: Validate Combo Start Key doesn't conflict with skill keys  
**Implementation Needed**:
```python
def validate_hotkey_no_conflict(combo_key, skill_slots, existing_hotkeys):
    """
    Check if combo_key conflicts with:
    1. Any attack skill key
    2. Any buff skill key
    3. Any app-wide hotkey (pause, resume, emergency stop)
    """
    # Collect all assigned keys
    occupied_keys = set()
    for slot in skill_slots:
        if slot.get("key"):
            occupied_keys.add(slot["key"])
    
    # Check against app hotkeys (global_hotkeys in config)
    for hotkey in existing_hotkeys.values():
        occupied_keys.add(hotkey)
    
    if combo_key in occupied_keys:
        return False, f"Hotkey conflict: {combo_key} already used by skill"
    return True, None
```

**Files to Modify**:
- `ui/tabs/hunt_tab.py`: Add validation callback to combo_start_key_cmb
- Create: `lib/features/hotkey/hotkey_validator.py` (new service)

#### Missing Feature 2: buff_slots Config Separation ❌
**Priority**: HIGH  
**Scope**: Separate skill_slots and buff_slots in config  
**Implementation Needed**:
```python
# Current structure:
hunt_cfg["skill_slots"] = [
    {"name": "Sword Slash", "type": "attack", "key": "q"},
    {"name": "Mana Heal", "type": "buff", "key": "e"},
]

# Desired structure:
hunt_cfg["skill_slots"] = [
    {"name": "Sword Slash", "type": "attack", "key": "q"},
]
hunt_cfg["buff_slots"] = [
    {"name": "Mana Heal", "type": "buff", "key": "e", "duration_sec": 300},
]
```

**Files to Modify**:
- `lib/features/hunt/config_migrator.py`: Add `_migrate_buff_slots()` function
- `ui/tabs/hunt_tab.py`: Filter Lane A by type=="attack", Lane B by type=="buff"

#### Missing Feature 3: Auto-Refresh Interval (duration_sec) ❌
**Priority**: MEDIUM  
**Scope**: Add duration_sec field to buff slots, display in Lane B UI  
**Implementation Needed**:
- Add input field to buff lane cards: "Auto-Refresh: [300]s"
- Persist to config: `buff_slots[i]["duration_sec"]`
- Display current value from `hunt_cfg["buff_slots"]`

**Files to Modify**:
- `ui/tabs/hunt_tab.py`: Add spinbox/entry for duration_sec in Lane B cards
- `lib/features/hunt/hunt_config.py`: Ensure duration_sec saved/loaded

#### Missing Feature 4: Buff Runtime Scheduling ❌
**Priority**: LOW (verify scope first)  
**Scope**: Active buff refresh logic in skill_runtime_service  
**Status**: NEEDS CLARIFICATION
- Is buff refresh supposed to be automatic during hunt (active scheduling)?
- Or only config storage for future use (config-only)?

**If Active Scheduling Required**:
```python
# In skill_runtime_service.py:
class BuffScheduler:
    def schedule_buff_refresh(self, buff_name, duration_sec):
        """Automatically refresh buff every duration_sec"""
        # Timer-based re-casting of buff skill
```

**Files to Modify**:
- `lib/features/skills/skill_runtime_service.py`: Add buff refresh scheduling
- `lib/features/hunt/hunt_orchestrator.py`: Call buff scheduler during hunt loop

#### Missing Feature 5: Legacy Config Migration ❌
**Priority**: MEDIUM  
**Scope**: Handle unclassified skill entries with proper precedence  
**Implementation Needed** (in config_migrator.py):

```python
def _migrate_buff_slots(data):
    """
    Extract buff-type skills from legacy skill_slots into separate buff_slots
    
    Precedence:
    1. Use explicit "type" field if present
    2. If missing, lookup in skill catalog by name/id
    3. If still unresolved, default to attack lane + log warning
    """
    skill_slots = data.get("skill_slots", [])
    buff_slots = []
    remaining_attack_slots = []
    
    for slot in skill_slots:
        skill_type = slot.get("type")
        
        # Step 1: Has explicit type?
        if skill_type in ("buff", "attack"):
            if skill_type == "buff":
                slot.setdefault("duration_sec", 300)  # Default duration
                buff_slots.append(slot)
            else:
                remaining_attack_slots.append(slot)
        else:
            # Step 2: Lookup in skill catalog
            skill_name = slot.get("name", "")
            skill_db = load_skill_library()
            catalog_type = None
            
            for skill_entry in skill_db.values():
                if skill_entry.get("name") == skill_name:
                    catalog_type = skill_entry.get("type")
                    break
            
            if catalog_type == "buff":
                slot["type"] = "buff"
                slot.setdefault("duration_sec", 300)
                buff_slots.append(slot)
            elif catalog_type == "attack":
                slot["type"] = "attack"
                remaining_attack_slots.append(slot)
            else:
                # Step 3: Unresolved → default to attack + log
                logger.warning(f"Unclassified skill '{skill_name}' → defaulted to attack lane")
                slot.setdefault("type", "attack")
                remaining_attack_slots.append(slot)
    
    data["skill_slots"] = remaining_attack_slots
    data["buff_slots"] = buff_slots
```

**Files to Modify**:
- `lib/features/hunt/config_migrator.py`: Add _migrate_buff_slots() function

#### Missing Feature 6: Validation Tests ❌
**Priority**: MEDIUM  
**Tests Needed**:

```python
# Test 1: DPI validation (100%, 125%, 150%)
def test_dpi_scaling():
    """Verify skill cards don't overlap at different DPI levels"""
    for dpi in [100, 125, 150]:
        # Render UI at DPI
        # Assert no card bounding boxes intersect
        # Assert cards within lane container visible area

# Test 2: i18n round-trip
def test_i18n_round_trip():
    """Verify all lane headers/labels translate correctly"""
    for lang in ["vi", "en"]:
        # Switch language
        # Assert headers show translated text
        # Assert no hard-coded English strings visible

# Test 3: Legacy config migration
def test_legacy_config_migration():
    """Test precedence rules for unclassified entries"""
    legacy_cfg = {
        "skill_slots": [
            {"name": "Sword Slash", "type": "attack"},  # Has type
            {"name": "Mana Heal"},  # Missing type, in catalog
            {"name": "Unknown Skill"},  # Missing type, not in catalog
        ]
    }
    migrated = migrate_hunt_config(legacy_cfg)
    
    # Assert Sword Slash in skill_slots
    # Assert Mana Heal in buff_slots
    # Assert Unknown Skill in skill_slots (default)
    # Assert warning logged for Unknown Skill

# Test 4: Save/reload round-trip
def test_save_reload_round_trip():
    """Verify skill_slots/buff_slots don't cross-contaminate"""
    cfg = {
        "skill_slots": [{"name": "Attack1", "type": "attack"}],
        "buff_slots": [{"name": "Buff1", "type": "buff", "duration_sec": 300}],
    }
    save_hunt_config(cfg)
    reloaded = load_hunt_config()
    
    # Assert no buff in skill_slots
    # Assert no attack in buff_slots

# Test 5: Hotkey conflict detection
def test_hotkey_conflict():
    """Verify conflict validation blocks incompatible combos"""
    skill_slots = [
        {"name": "Skill1", "key": "q"},
        {"name": "Skill2", "key": "w"},
    ]
    
    # Should pass (no conflict)
    is_valid, msg = validate_hotkey("Alt+1", skill_slots)
    assert is_valid
    
    # Should fail (q already used)
    is_valid, msg = validate_hotkey("q", skill_slots)
    assert not is_valid
    assert "q" in msg
```

**Files to Create**:
- `tests/test_cb3b_dual_lane_layout.py` (40+ test cases)
- `tests/test_cb3b_hotkey_conflict.py`
- `tests/test_cb3b_buff_slots_migration.py`

---

Target Files:
- Modify: `ui/tabs/hunt_tab.py` (or `app_gui.py` skill section)
- Modify: `lib/features/skills/skill_runtime_service.py`
- Modify: `lib/features/hunt/hunt_config.py`
- Reference: `lib/ui_style.py`

## Implementation Details

1. Dual-Lane Layout Construction:
   - Lane A (Combo Chain): horizontal scroll/grid container displaying skill cards sequentially for Attack skills (`type == 'attack'`). Default visible width shows 4-6 cards before scrolling kicks in — this is a display-sizing target, not a hard cap; the lane must scroll to accommodate any number of configured attack skills without truncating or dropping entries.
   - Each Card displays: Skill Name dropdown, Key entry, compact labels for `Cast: X.Xs` and `CD: X.Xs` read from database.
   - Lane B (Buff Lane): 2-3 rows for Buff skills (`type == 'buff'`), with Key entry and Auto-Refresh interval (`duration_sec`).
   - Scope note: this session covers the UI panel and config schema (storing `duration_sec` per buff slot). Whether `skill_runtime_service.py` actively schedules buff refresh using this value, or only persists it for a future session to consume, must be confirmed before coding — if runtime scheduling is in scope, add it explicitly as its own implementation step with its own test; otherwise document this session as "config + UI only, runtime consumption is out of scope."
2. Combo Mode Controls:
   - Add Checkbutton `Enable Auto Combo` and Entry/Combobox for `Combo Start Key` (default: `Alt+3`).
   - Specify the hotkey capture mechanism explicitly: state whether this is a global OS-level hook (e.g. via a `keyboard`/`pynput`-style library, active even when the app is unfocused) or an in-window binding (only active while the app has focus). This materially changes both implementation and the conflict risk with other applications' shortcuts — pick one and note it in code comments.
   - Validate that `Combo Start Key` does not conflict with:
     - Any key currently assigned to an attack skill (Lane A),
     - Any key currently assigned to a buff skill (Lane B),
     - Any other existing global hotkey already registered by the app (e.g. pause/resume, emergency stop), if the app has any.
   - On conflict, block save and show which existing binding it collides with (not just a generic "conflict" message).
3. Config Separation & Migration:
   - Save clean lists to config: `hunt_cfg["skill_slots"]` (attacks only) and `hunt_cfg["buff_slots"]` (buffs only).
   - In `load_hunt_config()`, automatically sort legacy combined slots into their respective lanes using this precedence:
     1. If the legacy entry has a `type` field (`'attack'` or `'buff'`), use it directly.
     2. If `type` is missing, look up the skill by name/id in the skill database and use its catalog-defined type.
     3. If still unresolved (skill not found in catalog either), default it into Lane A (attack) and flag it in logs as "unclassified — defaulted to attack lane" so the user can manually correct it, rather than silently dropping the entry or raising an exception.

## Validation

- Launch GUI at Windows DPI 100%, 125%, 150%: confirm horizontal skill cards do not overlap or wrap destructively. Define pass/fail concretely: after render at each DPI level, assert no two card bounding boxes (via widget `winfo_x/y/width/height`) intersect, and no card's right edge exceeds the lane container's visible width in a way that clips content instead of triggering scroll.
- Switch language between `vi` and `en`: confirm all lane headers and badges translate correctly (pull strings from the existing locale/i18n source, not hard-coded literals in the widget code).
- (Added) Legacy config migration round-trip test: load a mock legacy config containing (a) entries with explicit `type`, (b) entries missing `type` but present in the skill catalog, and (c) an entry missing `type` and absent from the catalog → assert each lands in the correct lane per the precedence rules above, and the catalog-absent case is logged as unclassified rather than raising.
- (Added) Save → reload round-trip: after migrating and saving, reload `hunt_cfg` and assert `skill_slots` contains only attack-type entries and `buff_slots` contains only buff-type entries (no cross-contamination).
- (Added) Hotkey conflict test: attempt to set `Combo Start Key` to a key already bound to an existing attack skill → assert save is blocked and the specific conflicting binding is reported.

---

## 🎯 COMPLETION ROADMAP (Next Steps to Reach 100%)

**Estimated Time to Complete**: 45-60 minutes

### Phase 1: Hotkey Conflict Validation (10-12 min)
**Priority**: HIGH | **Risk**: MEDIUM

1. Create `lib/features/hotkey/hotkey_validator.py`:
   - Implement `validate_hotkey_no_conflict(combo_key, skill_slots, global_hotkeys)` function
   - Check against all occupied keys (attack skills + buff skills + app hotkeys)
   - Return (is_valid: bool, conflict_message: str)
   
2. Wire validation to UI (`ui/tabs/hunt_tab.py`):
   - Attach validator callback to `combo_start_key_cmb` combobox
   - On selection, validate key doesn't conflict
   - If conflict detected: show error toast/dialog, prevent save
   - If valid: update config immediately

3. Add unit test: `tests/test_cb3b_hotkey_conflict.py` (5-8 test cases)

### Phase 2: buff_slots Config Separation (15-18 min)
**Priority**: HIGH | **Risk**: HIGH (breaking change)

1. Modify `lib/features/hunt/config_migrator.py`:
   - Add `_migrate_buff_slots()` function with 3-level precedence
   - Call during `migrate_hunt_config()` to extract buffs from skill_slots
   - Implement skill catalog lookup (if type missing)
   - Default to "attack" + log warning (if unresolved)

2. Update `lib/features/hunt/hunt_config.py`:
   - Ensure `load_hunt_config()` calls migrator properly
   - Add test for round-trip save/reload (buff_slots preserved)

3. Modify UI (`ui/tabs/hunt_tab.py`):
   - Filter Lane A: only skills where `type == "attack"` from `skill_slots`
   - Filter Lane B: only skills where `type == "buff"` from `buff_slots`
   - Update `_refresh_skill_slots_options()` to handle both arrays

4. Add tests: `tests/test_cb3b_buff_slots_migration.py` (6-8 test cases)

### Phase 3: Auto-Refresh Interval per Buff (8-10 min)
**Priority**: MEDIUM | **Risk**: LOW

1. Modify UI (`ui/tabs/hunt_tab.py`):
   - For Lane B cards: add spinbox/entry widget "Auto-Refresh: [X]s"
   - Default value: 300 seconds
   - Bind to config update: `buff_slots[idx]["duration_sec"] = int(widget.get())`

2. Ensure config persistence:
   - `save_hunt_config()` preserves `duration_sec` field
   - `load_hunt_config()` loads and restores to spinbox values

3. Add simple round-trip test (part of Phase 2 tests)

### Phase 4: Buff Runtime Scheduling (Optional, 15-20 min)
**Priority**: LOW | **Status**: Needs clarification first

**Decision Point**: Does CB3B include active buff refresh during hunt loop?
- **Option A**: Config-only (this session only stores duration_sec, future session uses it)
  - Mark scope as "complete" after Phase 3
  - Note for next sprint: "buff refresh scheduling deferred to future sprint"
- **Option B**: Active scheduling (buff refresh happens automatically during hunt)
  - Add `BuffScheduler` class to `skill_runtime_service.py`
  - Implement timer-based buff re-casting in `hunt_orchestrator.py`
  - Add test: verify buff fired at correct intervals

**Recommendation**: Clarify this with PM/design before starting Phase 4.

### Phase 5: Validation Test Suite (10-12 min)
**Priority**: MEDIUM | **Risk**: LOW

Create comprehensive test file: `tests/test_cb3b_validation_suite.py`

1. **DPI Scaling Test** (3-4 cases)
   - Verify card layout at 100%, 125%, 150%
   - Assert no card overlap, no content clipping
   
2. **i18n Translation Test** (2-3 cases)
   - Switch to Vietnamese/English
   - Assert all lane headers, labels, badges show translated text
   - Assert no hard-coded English strings visible

3. **Legacy Config Migration Test** (3-4 cases)
   - Test precedence: explicit type > catalog lookup > default
   - Test unclassified entry logged + defaulted to attack
   
4. **Save/Reload Round-trip Test** (2-3 cases)
   - Assert skill_slots ≠ buff_slots (no cross-contamination)
   - Assert duration_sec persisted for buff slots

5. **Hotkey Conflict Test** (included in Phase 1)

---

## Session Boundary Gate

- Use UIStyle tokens (zero hard-coded hex colors).
- Ensure existing hotkeys and key-bindings remain functional.
- Confirm the hotkey capture mechanism (global hook vs in-window binding) is explicitly documented in code.
- Confirm buff-runtime scope (config-only vs active scheduling) was decided and documented before implementation, not left ambiguous.
- Report PASSED/REVERTED at minute 25.