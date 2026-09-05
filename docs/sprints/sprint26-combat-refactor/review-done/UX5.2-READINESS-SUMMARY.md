# Executive Summary: UX5.2 Readiness Report (2026-09-05)

**Overall Status:** 🔴 **CANNOT START UX5.2** (4 critical blockers)

---

## Quick Facts

| Aspect | Status | Details |
|--------|--------|---------|
| **UX5.1 Phase 1** | ✅ READY | Target Card shell complete, can commit |
| **CB4A Phase 2** | ⚠️ PARTIAL | Exists but has wrong specs + missing handlers |
| **UX5.2 Phase 3** | 🔴 BLOCKED | Cannot start until blockers fixed |
| **Blockers** | 4 critical | Details below |
| **Fix Time** | 30 min | Prerequisites before UX5.2 |
| **UX5.2 Time** | 25-30 min | After fixes done |

---

## The 4 Blockers (In Priority Order)

### 1. **HP Throttle Spec Wrong** (5 min fix)
```
Current:  throttle_ms = 150, min_diff = 1.0, OR logic
Needed:   throttle_ms = 100, min_delta = 0.5, AND logic
Impact:   UI will exceed 10 FPS, causes stutters
```

### 2. **No Canvas HP Bar** (5 min fix)
```
Current:  ttk.Progressbar only
Needed:   tk.Canvas with step-fill rendering
Impact:   Cannot implement any UX5.2 HP features
```

### 3. **No Death Handler** (5 min fix)
```
Current:  clear_target_card exists, but no HP=0% logic
Needed:   Gray bar + [Đã Tiêu Diệt] + race guard
Impact:   Quick kills break card display
```

### 4. **No Window Recovery Service** (10 min fix)
```
Current:  Only validation exists
Needed:   WindowRecoveryController with async retry + lock
Impact:   Cannot implement recovery button
```

---

## What to Do Now

### ✅ You Can Do Right Now
1. ✅ Commit UX5.1 phase 1 (it's ready)
2. ✅ Review the 2 new documents I created

### 🔴 You Must Do Before UX5.2
Complete these 5 prerequisite tasks (30 min total):

1. **Fix target_hp_reader.py** (5 min)
   - Change: `throttle_ms = 150` → `100`
   - Change: `min_diff = 1.0` → `0.5`
   - Fix logic: OR → AND

2. **Add 4 i18n keys** (2 min)
   - target_card.target_dead
   - target_card.recovery_btn
   - target_card.recovery_retry
   - target_card.recovery_failed

3. **Implement WindowRecoveryController** (10 min)
   - New class in `window_selection_service.py`
   - Async retry (500ms spacing, NO `time.sleep()`)
   - Retry lock (singleton)

4. **Replace Progressbar with Canvas** (5 min)
   - Remove: `ttk.Progressbar`
   - Add: `tk.Canvas` + pre-init 3 objects

5. **Update hp_display method** (3 min)
   - Handle death: gray bar + [Đã Tiêu Diệt]
   - Render bar with step-fill
   - Handle color by percent

6. **Run tests** (5 min)
   - Verify throttle: max 50 renders in 5s
   - Verify delta: <0.5% skips render
   - Verify death: gray bar displays

---

## Timeline

```
Now:              UX5.1 ready to commit ✅
↓ (5 min)        
Fix throttle      AND update logic
↓ (2 min)
Add i18n keys
↓ (10 min)
Window recovery   Service class
↓ (5 min)
Canvas replace    Progressbar → Canvas
↓ (3 min)
Update methods    Death handler + rendering
↓ (5 min)
Test all          Gate validation
↓ (25-30 min)
Then: Start UX5.2 Main implementation
```

**Total:** 55-60 minutes end-to-end (prerequisites + UX5.2)

---

## Key Files You Need to Edit

1. **lib/vision/target_hp_reader.py** (Lines 9-10, 12-28)
   - Fix throttle specs
   - Fix AND logic
   - Add death signal

2. **ui/tabs/hunt_tab.py** (Lines 324-325, update methods)
   - Replace Progressbar with Canvas
   - Update `update_hp_display()`
   - Add death handler + race guard

3. **lib/features/hunt/window_selection_service.py** (New class)
   - Add `WindowRecoveryController`
   - Async retry with lock

4. **lib/i18n/translations.py** (Add 4 keys)
   - target_card.target_dead
   - target_card.recovery_* (3 variants)

---

## Critical Requirements (Don't Violate)

From UX5.2 spec — non-negotiable:

1. **Throttle = 100ms HARD LIMIT**
   - NO exceptions, even if delta = 10%
   - AND logic: both time AND delta must be true

2. **Death Handling**
   - Canvas gray (#52525B)
   - Text: [Đã Tiêu Diệt]
   - Race guard: after_cancel when target changes

3. **Recovery Retry**
   - 3 steps, 500ms apart
   - NO time.sleep() on Main Thread
   - Use self.after() instead
   - Shared lock with UX1

4. **HP Reader**
   - Only wrap CB1 logic
   - Don't rewrite pixel detection
   - CB1 is single source of truth

---

## Documents I Created for You

1. **REVIEW-UX5.2-READINESS.md** (detailed analysis)
   - Full dependency chain
   - Component-by-component status
   - Implementation details with code examples

2. **UX5.2-PREREQUISITES-AND-ISSUES.md** (implementation guide)
   - Each prerequisite task spelled out
   - Code snippets for each fix
   - Validation checklist

Both in: `docs/sprints/sprint26-combat-refactor/`

---

## Recommendation

**Conservative Path (Safest):**
1. Commit UX5.1 now ✅
2. Do all 5 prerequisite tasks (30 min)
3. Test everything passes ✅
4. Then start UX5.2 implementation (25-30 min)
5. Done with high quality ✅

**Total Time:** 55-60 minutes, zero risk

---

## Next Steps

**Right Now:**
- [ ] Read REVIEW-UX5.2-READINESS.md (understand scope)
- [ ] Read UX5.2-PREREQUISITES-AND-ISSUES.md (implementation tasks)
- [ ] Commit UX5.1 if not already done

**Then:**
- [ ] Complete 5 prerequisite tasks (30 min)
- [ ] Run test suite
- [ ] Start UX5.2 session (25-30 min)

**Questions?**
- All details in the two new documents
- Code examples included for each fix
- Validation checklist provided

