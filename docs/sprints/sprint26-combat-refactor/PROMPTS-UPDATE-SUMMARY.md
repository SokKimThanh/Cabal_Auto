# Summary: UX5.1 & CB4A Prompts Updated to Reflect 2-Phase Strategy

**Date:** 2026-09-05  
**Status:** ✅ Complete

---

## What Changed

### 📝 UX5.1 Prompt Updates

| Section | Change | Impact |
|---------|--------|--------|
| **Title & Timebox** | Added "PHASE 1 of 2-Phase" + increased timebox from 20-25 min to 40-50 min | Clarifies this is foundational work |
| **Relationship Section** | Replaced ambiguous "(a) vs (b)" with explicit Phase 1 → Phase 2 dependency chain | Clear prerequisites for CB4A |
| **Objective** | Updated to emphasize "shell nền tảng" and that Phase 2 reuses, not modifies | Clarifies UX5.1 is not modified by CB4A |
| **Target Files** | Renamed function to `get_target_monster_info()` (was `safe_get_monster_data()`) | Single unified function name |
| **Implementation 1.1** | Changed function name + added "SINGLE SOURCE OF TRUTH" label | No duplicate schema definitions |
| **Validation Section** | Added test for unified fallback with CB4A | Confirms no duplicate logic |
| **Session Boundary Gate** | Added explicit "PHASE 1 COMPLETION CRITERIA" + CB4A dependency gate | Clear pass/fail criteria |

**Key Additions:**
- 🔴 Red gate: "Only CB4A can proceed after UX5.1 PASSED"
- ✅ Explicit Phase 1 responsibilities  
- 📋 Clear pass criteria (8 tests, zero memory leaks, 100%-200% DPI)

---

### 📝 CB4A Prompt Updates

| Section | Change | Impact |
|---------|--------|--------|
| **Title & Timebox** | Added "PHASE 2 of 2-Phase" + increased timebox from 25-30 min to 40-50 min | Emphasizes it's enhancement, not standalone |
| **New Section: CRITICAL Gate** | Added "Only start after UX5.1 PASSED" with 4 prerequisites | Hard prerequisite enforcement |
| **Objective** | Changed from "build a dashboard" to "enhance existing panel" | Clear: enhancement, not redesign |
| **Target Files** | Updated to show "Modify" vs "Create" vs "Reuse" explicitly | Clear what's inherited vs new |
| **Implementation 1.1** | Added "✅ REUSE" section (don't redefine `get_target_monster_info()`) | Prevents duplicate definitions |
| **Implementation 3** | Changed from building panel to "EXTEND EXISTING" with new methods | Clear: add to UX5.1, don't rebuild |
| **Validation Section** | Added prerequisite check + noted UX5.1 tests should PASS first | Testing assumes UX5.1 works |
| **Session Boundary Gate** | Added PREREQUISITE CHECK before CB4A testing + regression clause | Tests include UX5.1 regression check |
| **New Summary Table** | Added at end: inheritance matrix + test suite merge plan | Crystal clear what's inherited |

**Key Additions:**
- 🚫 Explicit dependency gate (prerequisite check)
- 📊 Inheritance table showing what's inherited from UX5.1
- 🔄 Clear methods to ADD (update_status, update_hp_display, clear_target_card)
- 📋 Merged test suite: 8 (UX5.1) + 6 (CB4A) = 14 total

---

## Benefits of These Updates

### ✅ Clarity
- **Before:** Two overlapping prompts with unclear relationship  
- **After:** Clear "Phase 1 shell" → "Phase 2 enhancement" progression

### ✅ Risk Reduction  
- **Before:** Risk of duplicate implementations (two `get_target_monster_info()` versions)  
- **After:** Single unified function, explicitly called out

### ✅ Test Clarity
- **Before:** Unclear which tests belong where  
- **After:** 8 UX5.1 tests (foundation) + 6 CB4A tests (enhancement) = 14 total

### ✅ Dependency Management
- **Before:** CB4A could be started prematurely  
- **After:** Hard gate: "Do not start CB4A until UX5.1 PASSED"

### ✅ Maintenance
- **Before:** Prompts could drift apart  
- **After:** Shared functions/keys explicitly tracked in inheritance tables

---

## Implementation Sequence (Recommended)

### Sprint N (Phase 1: UX5.1)
**Timebox:** 40-50 min  
**Deliverables:**
1. `get_target_monster_info()` with 2-tầng fallback + `is_placeholder` flag
2. Target Card Panel UI (776x552px, PhotoImage, lifecycle management)
3. ~10 i18n keys in `target_card.*` namespace
4. 8 unit tests (schema, memory, DPI, lifecycle)
5. **Gate:** PASSED = zero memory leaks, 100%-200% DPI rendering, all tests passing

### Sprint N+1 (Phase 2: CB4A)
**Prerequisites:** UX5.1 Phase 1 PASSED  
**Timebox:** 40-50 min  
**Deliverables:**
1. `target_hp_reader.py` (HP% calculation wrapping CB1)
2. Status FSM in orchestrator (APPROACHING → ATTACKING → DEAD)
3. Race condition handler (cancel pending clear on rapid re-target)
4. 6 unit tests (HP transitions, race condition, rapid re-target)
5. **Gate:** PASSED = smooth HP%, correct state transitions, no race condition

**Merged Result:** 14 tests passing, full feature operational

---

## Files Modified

1. ✅ `docs/sprints/sprint26-combat-refactor/Prompt-UX5.1 Active Target Card Shell, Fallback Schema & Image Lifecycle.md` - Updated to Phase 1 spec
2. ✅ `docs/sprints/sprint26-combat-refactor/PROMPT-CB4A-Real-time Target Card & HP Visualizer Panel.md` - Updated to Phase 2 spec
3. ✅ `docs/sprints/sprint26-combat-refactor/REVIEW-UX5.1-vs-PROJECT-STATE.md` - Already created (85% readiness assessment)
4. ✅ `docs/sprints/sprint26-combat-refactor/REVIEW-CB4A-vs-PROJECT-STATE.md` - Already created (80% readiness assessment)

---

## Key Takeaways

| Aspect | Before | After |
|--------|--------|-------|
| **Relationship** | Unclear, possibly duplicative | Clear phase dependency: 1 → 2 |
| **get_target_monster_info()** | Defined twice (UX5.1 + CB4A) | Defined once, reused by both |
| **Target Card Panel** | Might be rebuilt by CB4A | Built in Phase 1, extended in Phase 2 |
| **i18n Keys** | Might be duplicated | Defined once in `target_card.*` namespace |
| **Start Gate for CB4A** | None | Hard gate: UX5.1 PASSED required |
| **Test Strategy** | 8 + 6 = 14 unclear allocation | Clear: 8 (UX5.1 foundation) + 6 (CB4A enhancement) |

---

## Next Steps

### If User Wants to Proceed:
1. **Review both updated prompts** (UX5.1 + CB4A) to confirm 2-phase approach
2. **Decide:** Implement Phase 1 (UX5.1) now, or defer?
3. **If yes to Phase 1:** Start UX5.1 implementation (40-50 min timebox)
4. **After Phase 1 PASSED:** Proceed to Phase 2 (CB4A) with prerequisite checks

### If User Wants Modifications:
- Adjust timebox (currently 40-50 min each phase)
- Change HP throttle interval (currently 150-200ms suggested)
- Add/remove test cases
- Modify inheritance allocation (what's shared vs independent)

---

**Status:** ✅ Prompts updated and aligned  
**Ready for:** User review + implementation decision
