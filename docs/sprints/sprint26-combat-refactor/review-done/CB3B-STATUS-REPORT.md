# CB3B Status Report: Combo Rotation Builder & Dual-Lane UI

**Date**: 2026-09-05  
**Assessed By**: Code Review  
**Current Completion**: **55-60%**

---

## 📊 Summary

The CB3B (Combo Rotation Builder) feature is partially implemented. The dual-lane UI layout and combo mode controls are working, but critical features like hotkey conflict validation and buff_slots config separation are missing.

### ✅ What's Working (55-60%)
- Dual-lane skill card layout (Combo Chain + Buff Lane)
- Combo mode controls (checkbox + key selector)
- Skill card display with stats
- Config schema for combo settings
- i18n translations

### ❌ What's Missing (40-45%)
- Hotkey conflict validation
- buff_slots vs skill_slots separation
- Auto-refresh interval per buff
- Buff runtime scheduling
- Comprehensive test suite

---

## 📍 Implementation Checklist

### ✅ COMPLETED
- [x] **Dual-Lane Layout** (lines 773-939 in hunt_tab.py)
  - Combo Lane: 4 skill cards in top row
  - Buff Lane: 4 skill cards in bottom row
  - Grid layout with proper column configuration
  - Card components: name dropdown, cast time badge, cooldown badge
  - DPI scaling support (100%, 125%, 150%)
  - i18n labels ("Combo Chain", "Buff Lane")

- [x] **Combo Mode Controls** (lines 786-833 in hunt_tab.py)
  - Checkbox: "Enable Auto Combo"
  - Combobox: "Combo Start Key" (values: Alt+1 through Alt+5)
  - State management: Key selector disabled when combo is off
  - Config persistence: hunt_cfg["combo"] = {enabled, combo_start_key}

- [x] **Skill Card Display** (lines 887-930 in hunt_tab.py)
  - Skill name dropdown selector
  - Cast time badge display (⚡ X.Xs)
  - Cooldown badge display (⏳ X.Cs)
  - Dynamic stat update on skill selection
  - Tooltip support

- [x] **Config Schema** (hunt_config.py + config_migrator.py)
  - Combo configuration structure exists
  - Config migrator handles skill type field
  - Save/load cycle working

### ❌ NOT COMPLETED

- [ ] **Hotkey Conflict Validation** (10-12 min to implement)
  - NO validation that combo_start_key doesn't conflict with attack/buff keys
  - NO error message on conflict
  - NO save blocking on detected conflict
  - **Files to create**: lib/features/hotkey/hotkey_validator.py
  - **Files to modify**: ui/tabs/hunt_tab.py (add validation callback)

- [ ] **buff_slots Config Separation** (15-18 min to implement)
  - Currently: ALL skills in single "skill_slots" array
  - Needed: Separate "skill_slots" (attacks) and "buff_slots" (buffs)
  - Need: Skill type filtering (attack vs buff)
  - **Files to modify**: 
    - lib/features/hunt/config_migrator.py (add _migrate_buff_slots function)
    - ui/tabs/hunt_tab.py (filter lanes by type)

- [ ] **Auto-Refresh Interval (duration_sec)** (8-10 min to implement)
  - NO duration_sec field per buff slot
  - NO UI input for auto-refresh interval
  - NO persistence to config
  - **Files to modify**: ui/tabs/hunt_tab.py (add spinbox for Lane B cards)

- [ ] **Buff Runtime Scheduling** (15-20 min, IF in scope)
  - NOT implemented in skill_runtime_service.py
  - Unclear if this session should implement active scheduling or just config storage
  - **Decision needed**: Config-only vs active scheduling during hunt loop
  - **If active**: Modify skill_runtime_service.py and hunt_orchestrator.py

- [ ] **Legacy Config Migration** (Part of buff_slots work)
  - Missing precedence rules for unclassified entries
  - NO catalog lookup for skills missing "type" field
  - NO logging for unclassified → defaulted decisions

- [ ] **Validation Test Suite** (10-12 min to implement)
  - DPI scaling tests (100%, 125%, 150%)
  - i18n round-trip tests (vi/en)
  - Legacy config migration tests
  - Save/reload round-trip tests
  - Hotkey conflict tests
  - **Files to create**: tests/test_cb3b_*.py (multiple test files)

---

## 📈 Implementation Path to 100%

### Quick Path (45-60 minutes for remaining work)

**Phase 1 - Hotkey Validation** (10-12 min)
```
Create: lib/features/hotkey/hotkey_validator.py
Modify: ui/tabs/hunt_tab.py
Create: tests/test_cb3b_hotkey_conflict.py
```

**Phase 2 - buff_slots Separation** (15-18 min) ⚠️ HIGH PRIORITY
```
Modify: lib/features/hunt/config_migrator.py (add _migrate_buff_slots)
Modify: lib/features/hunt/hunt_config.py (ensure persistence)
Modify: ui/tabs/hunt_tab.py (filter by type)
Create: tests/test_cb3b_buff_slots_migration.py
```

**Phase 3 - Auto-Refresh Interval** (8-10 min)
```
Modify: ui/tabs/hunt_tab.py (add duration_sec spinbox for Lane B)
Test: Verify round-trip save/load
```

**Phase 4 - Buff Scheduling** (OPTIONAL, 15-20 min)
```
Decision: Is active scheduling in scope?
If YES: Modify skill_runtime_service.py + hunt_orchestrator.py
If NO: Mark "config-only, scheduling deferred to next sprint"
```

**Phase 5 - Test Suite** (10-12 min)
```
Create: tests/test_cb3b_validation_suite.py
Include: DPI, i18n, migration, round-trip tests
```

---

## 📝 Code Locations

### Files Already Modified (Working)
- `ui/tabs/hunt_tab.py` (lines 773-939)
  - Dual-lane layout construction
  - Combo mode controls
  - Skill card rendering with stats
  
- `lib/features/hunt/config_migrator.py`
  - Config schema v3 with combo support
  - Skill type handling (attack/buff)
  
- `lib/features/hunt/hunt_config.py`
  - Config save/load with migration

### Files Needing Changes
1. **Create new**:
   - `lib/features/hotkey/hotkey_validator.py` - Hotkey validation logic
   - `tests/test_cb3b_hotkey_conflict.py` - Hotkey conflict tests
   - `tests/test_cb3b_buff_slots_migration.py` - buff_slots migration tests
   - `tests/test_cb3b_validation_suite.py` - DPI, i18n, round-trip tests

2. **Modify existing**:
   - `lib/features/hunt/config_migrator.py` - Add _migrate_buff_slots() function
   - `ui/tabs/hunt_tab.py` - Add hotkey validation, buff_slots filtering, duration_sec UI
   - `skill_runtime_service.py` - Buff scheduling (IF in scope)
   - `hunt_orchestrator.py` - Call buff scheduler (IF in scope)

---

## 🎯 Risk Assessment

| Feature | Priority | Risk | Est. Time |
|---------|----------|------|-----------|
| Hotkey Conflict Validation | HIGH | MEDIUM | 10-12 min |
| buff_slots Separation | HIGH | HIGH | 15-18 min |
| Auto-Refresh Interval | MEDIUM | LOW | 8-10 min |
| Buff Runtime Scheduling | LOW | MEDIUM | 15-20 min |
| Test Suite | MEDIUM | LOW | 10-12 min |

---

## 💡 Recommendations

1. **Immediate Priority**: Complete buff_slots separation (Phase 2)
   - This is a breaking change that affects data structure
   - Better to do early before other features depend on merged structure

2. **Critical Gate**: Clarify buff scheduling scope before Phase 4
   - Don't waste time if it's config-only vs active scheduling unclear
   - Ask PM/design: "Should buffs auto-refresh during hunt loop?"

3. **Test Early**: Add comprehensive tests as you go
   - DPI tests especially important for cross-platform compatibility
   - Migration tests critical since schema version changes

4. **Documentation**: Update PROMPT-CB3B.md with completion roadmap
   - ✅ DONE - Added detailed breakdown and phased implementation plan

---

## 🔄 Next Actions

### For Product/Design
- [ ] Clarify if buff auto-refresh is in scope (Phase 4 decision)
- [ ] Review hotkey conflict resolution UX (show which key conflicts)

### For Engineering
- [ ] Start Phase 1 (Hotkey Validation) - 10-12 min
- [ ] Start Phase 2 (buff_slots Separation) - 15-18 min  
- [ ] Add Phase 5 (Test Suite) in parallel if possible

### For QA
- [ ] Test DPI scaling at 100%, 125%, 150%
- [ ] Test i18n (Vietnamese/English)
- [ ] Verify hotkey conflict blocking works
- [ ] Verify buff_slots don't mix with skill_slots

---

## 📄 Updated Documentation

- ✅ [PROMPT-CB3B.md](PROMPT-CB3B-Combo%20Rotation%20Builder%20&%20Hotbar%20Mapping.md) 
  - Updated with current status checklist
  - Added detailed breakdown of what's implemented
  - Added completion roadmap with time estimates
  - Added test examples for each missing feature
  - Added prioritized implementation guide

---

**Status**: 🟡 PARTIAL - Ready for Phase 1-2 implementation  
**Recommendation**: Begin Phase 1 & 2 immediately; clarify Phase 4 scope first
